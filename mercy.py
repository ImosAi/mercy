import argparse
from pathlib import Path

from mercy_app.brain import LayeredBrain
from mercy_app.config import load_config
from mercy_app.inputs import create_input_adapter

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config" / "mercy.yaml"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mercy öğrenen karar mekanizması")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--feedback", metavar="RUN_ID")
    parser.add_argument("--outcome", choices=("accepted", "rejected"))
    parser.add_argument("--note", default="")
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--test-status", choices=("passed", "failed", "not_run"))
    parser.add_argument(
        "--export-memory",
        type=Path,
        help="Evrensel hafızayı JSON olarak dışa aktarır.",
    )
    parser.add_argument(
        "--clear-memory",
        action="store_true",
        help="Tüm hafızayı temizler; geri alınamaz.",
    )
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    if bool(args.feedback) != bool(args.outcome):
        parser.error("--feedback ve --outcome birlikte kullanılmalıdır.")
    if args.export_memory and args.clear_memory:
        parser.error("--export-memory ve --clear-memory birlikte kullanılamaz.")

    config = load_config(args.config)
    database = Path(config["memory"]["database"])
    if not database.is_absolute() and str(database) != ":memory:":
        database = args.config.resolve().parent / database

    brain = LayeredBrain(database)
    try:
        if args.feedback:
            brain.record_feedback(args.feedback, args.outcome, args.note)
            print(f"Geri bildirim kaydedildi: {args.feedback} → {args.outcome}")
            return 0

        if args.clear_memory:
            brain.clear_memory()
            print("Hafıza temizlendi.")
            return 0

        if args.export_memory:
            args.export_memory.parent.mkdir(parents=True, exist_ok=True)
            payload = brain.export_memory()
            with args.export_memory.open("w", encoding="utf-8") as handle:
                import json

                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            print(f"Hafıza dışa aktarıldı: {args.export_memory}")
            return 0

        if args.history:
            try:
                runs = brain.recent_runs(args.limit)
            except ValueError as error:
                parser.error(str(error))
            if not runs:
                print("Henüz kaydedilmiş çalıştırma yok.")
                return 0
            for run in runs:
                feedback = run.feedback or "bekliyor"
                print(
                    f"{run.run_id} | {run.error_type}: {run.message} | "
                    f"karar={run.action} | güven={run.confidence:.0%} | "
                    f"test={run.test_status} | geri bildirim={feedback} | "
                    f"{run.created_at}"
                )
            return 0

        test_status = args.test_status or config["simulation"].get(
            "test_status", "not_run"
        )
        incident = create_input_adapter(config["input"]).fetch()
        decision = brain.record_run(incident, test_status)
        print("🤍 mercy — öğrenen karar mekanizması (simülasyon)")
        print(f"Çalıştırma: {decision.run_id}")
        print(f"Karar: {decision.action}")
        print(f"Güven: {decision.confidence:.0%}")
        print(f"Geçmiş geri bildirim: {decision.evidence_count}")
        if decision.acceptance_rate is not None:
            print(f"Benzer önerilerin kabul oranı: {decision.acceptance_rate:.0%}")
        print(f"Test durumu: {decision.test_status}")
        print(f"Gerekçe: {decision.rationale}")
        print("Patch/PR uygulanmadı; insan onayı zorunludur.")
        print(
            "İnceleme sonrası geri bildirim: "
            f"python mercy.py --feedback {decision.run_id} --outcome accepted|rejected"
        )
        return 0
    finally:
        brain.close()


if __name__ == "__main__":
    raise SystemExit(main())
