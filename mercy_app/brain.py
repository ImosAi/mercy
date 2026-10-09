import hashlib
import json
import re
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

Feedback = Literal["accepted", "rejected"]
TestStatus = Literal["passed", "failed", "not_run"]


@dataclass(frozen=True)
class Incident:
    source: str
    error_type: str
    message: str
    stack_trace: str


@dataclass(frozen=True)
class Decision:
    run_id: str
    action: str
    confidence: float
    evidence_count: int
    acceptance_rate: float | None
    rationale: str
    test_status: TestStatus


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    error_type: str
    message: str
    action: str
    confidence: float
    test_status: TestStatus
    feedback: Feedback | None
    created_at: str


def _signature(incident: Incident) -> str:
    normalized_message = re.sub(r"\b\d+\b", "<n>", incident.message.lower())
    normalized_message = re.sub(r"\s+", " ", normalized_message).strip()
    fingerprint = json.dumps(
        [incident.error_type.lower().strip(), normalized_message],
        ensure_ascii=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()


class LayeredBrain:
    """Local, auditable memory: episodes -> feedback patterns -> guarded decisions."""

    def __init__(self, database: Path):
        if str(database) != ":memory:":
            database.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(str(database))
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                signature TEXT NOT NULL,
                source TEXT NOT NULL,
                error_type TEXT NOT NULL,
                message TEXT NOT NULL,
                stack_trace TEXT NOT NULL,
                test_status TEXT NOT NULL
                    CHECK (test_status IN ('passed', 'failed', 'not_run')),
                action TEXT NOT NULL,
                confidence REAL NOT NULL,
                evidence_count INTEGER NOT NULL,
                acceptance_rate REAL,
                rationale TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS runs_signature_idx ON runs(signature);
            CREATE TABLE IF NOT EXISTS feedback (
                run_id TEXT PRIMARY KEY REFERENCES runs(id),
                outcome TEXT NOT NULL CHECK (outcome IN ('accepted', 'rejected')),
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            """
        )

    def close(self) -> None:
        self._connection.close()

    def export_memory(self) -> dict[str, object]:
        rows = self._connection.execute(
            """
            SELECT runs.id, runs.signature, runs.source, runs.error_type,
                   runs.message, runs.stack_trace, runs.test_status,
                   runs.action, runs.confidence, runs.evidence_count,
                   runs.acceptance_rate, runs.rationale, runs.created_at,
                   feedback.outcome AS feedback_outcome,
                   feedback.note AS feedback_note,
                   feedback.created_at AS feedback_created_at
            FROM runs
            LEFT JOIN feedback ON feedback.run_id = runs.id
            ORDER BY runs.created_at ASC, runs.id ASC
            """
        ).fetchall()
        runs = []
        for row in rows:
            runs.append(
                {
                    "run_id": row["id"],
                    "signature": row["signature"],
                    "source": row["source"],
                    "error_type": row["error_type"],
                    "message": row["message"],
                    "stack_trace": row["stack_trace"],
                    "test_status": row["test_status"],
                    "action": row["action"],
                    "confidence": row["confidence"],
                    "evidence_count": row["evidence_count"],
                    "acceptance_rate": row["acceptance_rate"],
                    "rationale": row["rationale"],
                    "created_at": row["created_at"],
                    "feedback": {
                        "outcome": row["feedback_outcome"],
                        "note": row["feedback_note"],
                        "created_at": row["feedback_created_at"],
                    }
                    if row["feedback_outcome"] is not None
                    else None,
                }
            )
        return {
            "version": 1,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "runs": runs,
        }

    def clear_memory(self) -> None:
        self._connection.execute("DELETE FROM feedback")
        self._connection.execute("DELETE FROM runs")
        self._connection.commit()

    def recent_runs(self, limit: int = 10) -> list[RunSummary]:
        if not 1 <= limit <= 100:
            raise ValueError("Geçmiş limiti 1 ile 100 arasında olmalıdır.")
        rows = self._connection.execute(
            """
            SELECT runs.id, runs.error_type, runs.message, runs.action,
                   runs.confidence, runs.test_status, runs.created_at,
                   feedback.outcome
            FROM runs
            LEFT JOIN feedback ON feedback.run_id = runs.id
            ORDER BY runs.created_at DESC, runs.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            RunSummary(
                run_id=row["id"],
                error_type=row["error_type"],
                message=row["message"],
                action=row["action"],
                confidence=row["confidence"],
                test_status=row["test_status"],
                feedback=row["outcome"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def record_run(self, incident: Incident, test_status: TestStatus) -> Decision:
        signature = _signature(incident)
        rows = self._connection.execute(
            """
            SELECT feedback.outcome
            FROM runs
            JOIN feedback ON feedback.run_id = runs.id
            WHERE runs.signature = ?
            """,
            (signature,),
        ).fetchall()
        accepted = sum(row["outcome"] == "accepted" for row in rows)
        evidence_count = len(rows)
        acceptance_rate = accepted / evidence_count if evidence_count else None

        if test_status == "failed":
            action = "blocked_test_failure"
            rationale = "Test başarısız; aday patch ilerletilemez."
        elif test_status == "not_run":
            action = "tests_required"
            rationale = "Test sonucu yok; patch değerlendirilmeden önce test gerekli."
        elif evidence_count == 0:
            action = "candidate_needs_review"
            rationale = "Bu hata örüntüsü için geçmiş insan geri bildirimi yok."
        elif evidence_count >= 3 and acceptance_rate >= 0.75:
            action = "candidate_supported"
            rationale = (
                "Benzer geçmiş öneriler olumlu değerlendirildi; "
                "yine de insan onayı zorunlu."
            )
        elif evidence_count >= 3 and acceptance_rate <= 0.25:
            action = "revise_candidate"
            rationale = (
                "Benzer geçmiş öneriler çoğunlukla reddedildi; "
                "yaklaşım gözden geçirilmeli."
            )
        else:
            action = "candidate_needs_review"
            rationale = "Geçmiş örnek sayısı veya geri bildirim karışımı yetersiz."

        confidence = (
            round((evidence_count / (evidence_count + 3)) * abs(2 * acceptance_rate - 1), 3)
            if evidence_count
            else 0.0
        )
        run_id = str(uuid.uuid4())
        decision = Decision(
            run_id=run_id,
            action=action,
            confidence=confidence,
            evidence_count=evidence_count,
            acceptance_rate=acceptance_rate,
            rationale=rationale,
            test_status=test_status,
        )
        self._connection.execute(
            """
            INSERT INTO runs (
                id, signature, source, error_type, message, stack_trace,
                test_status, action, confidence, evidence_count,
                acceptance_rate, rationale, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                signature,
                incident.source,
                incident.error_type,
                incident.message,
                incident.stack_trace,
                test_status,
                action,
                confidence,
                evidence_count,
                acceptance_rate,
                rationale,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self._connection.commit()
        return decision

    def record_feedback(
        self, run_id: str, outcome: Feedback, note: str = ""
    ) -> None:
        if outcome not in {"accepted", "rejected"}:
            raise ValueError("Geri bildirim accepted veya rejected olmalıdır.")
        try:
            self._connection.execute(
                """
                INSERT INTO feedback (run_id, outcome, note, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (run_id, outcome, note, datetime.now(timezone.utc).isoformat()),
            )
            self._connection.commit()
        except sqlite3.IntegrityError as error:
            self._connection.rollback()
            exists = self._connection.execute(
                "SELECT 1 FROM runs WHERE id = ?", (run_id,)
            ).fetchone()
            if exists is None:
                raise ValueError(f"Çalıştırma bulunamadı: {run_id}") from error
            raise ValueError(
                f"{run_id} için geri bildirim zaten kaydedilmiş."
            ) from error
