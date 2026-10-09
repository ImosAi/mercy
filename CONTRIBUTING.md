# Katkı rehberi

Mercy henüz simülasyon/prototip aşamasındadır. Değişikliklerde mevcut kapsamı
gerçek entegrasyon gibi göstermeyin ve otomatik patch/PR davranışını insan
onayı olmadan devreye almayın.

## Geliştirme ortamı

Kurulum adımları için [install.md](./install.md) belgesine bakın.

## Değişiklik öncesi

- Karar veya hafıza davranışını etkileyen değişiklikler için regresyon testi
  ekleyin.
- Dış girdi, model çıktısı, dosya yolu veya komut çalıştırma ekliyorsanız
  doğrulama ve güvenlik sınırlarını belgeleyin.
- Kullanıcıya görünen özellik ve yapılandırma değişikliklerini README ve ilgili
  belgeye yansıtın.
- Yapılandırmaya gizli anahtar eklemeyin; yerel veritabanı ve yapılandırma
  dosyalarını sürüm kontrolüne almayın.

## Doğrulama

```bash
python -m unittest discover -s tests -v
git diff --check
```

## Güvenlik ilkeleri

- Otomatik merge yapılmamalıdır.
- İnsan onayı olmadan patch uygulanmamalı veya PR açılmamalıdır.
- Test komutları canlı hedef depoda çalıştırılmadan önce izolasyon, izin ve
  zaman aşımı kontrolleri bulunmalıdır.
- Hata raporları, yığın izleri ve geri bildirim notları hassas veri içerebilir;
  loglara ve commit'lere eklemeyin.

