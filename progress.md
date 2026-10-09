# Geliştirme durumu

Bu dosya, depoda gerçekten bulunan işlevlerin ve kalan işlerin özetidir.

## Mevcut durum

- [x] YAML yapılandırma yükleme ve temel doğrulama.
- [x] Girdi adaptörü arayüzü, mock adaptör ve ortak olay normalizasyonu.
- [x] Son kararları ve geri bildirim durumunu listeleyen denetlenebilir geçmiş.
- [x] SQLite üzerinde kalıcı olay ve karar kaydı.
- [x] Hata tipi/mesajı imzasına göre benzer olayların eşleştirilmesi.
- [x] İnsan kabul/red geri bildirimini kaydetme ve sonraki kararlarda kullanma.
- [x] Test durumu ve gerekçe içeren deterministik karar politikası.
- [x] Başarısız veya çalıştırılmamış testleri ilerleme engeli olarak ele alma.
- [x] Patch ve PR için insan onayını zorunlu tutan simülasyon akışı.
- [x] Karar hafızası ve geri bildirim için birim testleri.
- [x] Kurulum ve mimari sınırlarının belgelenmesi.

## Bilerek henüz yapılmayanlar

- [ ] Gerçek Sentry, GitHub Issues veya webhook girdi adaptörleri.
- [ ] LLM sağlayıcı arayüzü ve gerçek hata analizi.
- [ ] LLM çıktısı için şema doğrulama ve güvenli patch üretimi.
- [ ] Patch diff inceleme, repo sınırı denetimi ve izole worktree uygulaması.
- [ ] Gerçek test runner, zaman aşımı ve kaynak sınırları.
- [ ] Açık insan-onayı adımı ve onay durumunun kalıcı takibi.
- [ ] Onay sonrası Git branch/commit ve GitHub Pull Request adaptörü.
- [ ] Hafıza dışa aktarma/silme, saklama süresi ve geri yükleme araçları.
- [ ] Hafıza temizleme ve saklama süresi yönetimi.
- [ ] CI, statik analiz, desteklenen Python sürümleri için otomatik doğrulama.

## Önerilen sonraki adımlar

1. Hafıza imzası, karar sınırları ve yapılandırma için daha fazla test ekle.
2. LLM arayüzünü salt analiz/aday üretimi için ekle; çıktıyı doğrula ve
   otomatik uygulama yapma.
3. Patch'i ayrı worktree'de denetle ve testleri kısıtlı ortamda çalıştır.
4. İnsan onayı ve audit kaydını tamamla.
5. Yalnızca onaydan sonra GitHub PR açma entegrasyonunu ekle.

## Güvenlik kabul ölçütleri

- Hiçbir dalda otomatik merge yok.
- İnsan onayı olmadan patch uygulanmıyor veya PR açılmıyor.
- Hata raporları ve geri bildirim notları yerel hassas veri sayılıyor.
- Dış girdiler, model çıktıları, komutlar ve dosya yolları doğrulanıyor.
- Test çalıştırma izolasyon ve zaman sınırları olmadan canlı kullanıma
  alınmıyor.
