# Mimari

## Uygulanan mimari

```text
mercy.py (CLI)
  ├─ mercy_app.config
  │    └─ YAML okuma ve mevcut seçeneklerin doğrulanması
  ├─ mercy_app.inputs
  │    ├─ InputAdapter arayüzü
  │    ├─ MockInputAdapter
  │    └─ Olay normalizasyonu → Incident
  └─ mercy_app.brain
       ├─ Olay imzası
       ├─ SQLite olay/karar hafızası
       ├─ İnsan geri bildirimi hafızası
       ├─ Hassas stack trace içermeyen geçmiş özeti
       └─ Kanıta dayalı karar ve gerekçe
```

`mercy.py`, mevcut prototipte `MockInputAdapter` üzerinden örnek olayı alır.
`input.incident` ile olay yapılandırılabilir; eksik/boş hata tipi ve mesajı
reddedilir. Adaptörler ortak `Incident` veri modelini döndürür.
`LayeredBrain` olayın test durumunu ve geçmiş insan geri bildirimini inceleyip
bir karar üretir. Çalıştırma ve geri bildirim yerel SQLite dosyasına yazılır.

## Öğrenme katmanları

1. **Olay hafızası:** Olay, test durumu, karar, güven, gerekçe ve zaman damgası.
2. **Örüntü hafızası:** Aynı normalize edilmiş hata tipi/mesaj imzasına bağlı
   kabul/red geri bildirimleri.
3. **Karar katmanı:** Geçmiş kanıtın sayısını ve kabul oranını kullanır. Kanıt
   azsa temkinli kalır; test başarısızsa kararı bloke eder.
4. **İnsan denetimi:** Karar destek amaçlıdır. Otomatik patch, PR veya merge
   uygulaması yoktur.

Bu mekanizma model eğitimi değildir. Hafıza yerel, açıkça incelenebilir ve
silinince öğrenilmiş geçmişi kaybolur. Geri bildirim kalitesi doğrudan karar
kalitesini etkiler.

## Henüz uygulamada olmayan hedef bileşenler

```text
Sentry/GitHub/webhook adaptörleri (henüz yok)
  → olay normalizasyonu ve tekrar ayıklama
  → karar hafızası
  → LLM analiz/aday patch üretimi
  → patch doğrulama ve izole worktree
  → kısıtlı test runner
  → insan onayı
  → Git ve PR adaptörü
```

Yukarıdaki bileşenler hedef tasarımdır; mevcut sürümün özelliği olarak
değerlendirilmemelidir.

## Sorumluluk sınırları

- **CLI:** Komut satırı argümanları ve kullanıcıya sonuç gösterimi.
- **Config:** Yapılandırma dosyası ve desteklenen seçenekler için erken hata.
- **Brain:** Olay kaydı, benzer geçmiş bulma, geri bildirim ve karar politikası.
- **Girdi adaptörleri (planlı):** Kaynağa özgü kimlik doğrulama ve olayları
  ortak `Incident` biçimine dönüştürme.
- **Patch/test/PR bileşenleri (planlı):** Birbirinden ayrı modüller olmalı;
  test başarısı ve insan onayı geçitleri atlanamamalı.
