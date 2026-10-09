# Mercy

Mercy, hata düzeltme iş akışı için yerel ve denetlenebilir bir karar mekanizması
temeli sunar. Mevcut sürüm **simülasyondur**: gerçek hata kaynağına bağlanmaz,
LLM çağırmaz, patch üretmez/uygulamaz, test komutu çalıştırmaz ve PR açmaz.

## Katmanlı beyin

```text
Girdi
  ↓
Olay hafızası (SQLite: olay, test sonucu, karar)
  ↓
Örüntü hafızası (aynı hata imzası için insan geri bildirimleri)
  ↓
Karar katmanı (kanıt sayısı, kabul oranı, güven, gerekçe)
  ↓
İnsan incelemesi (zorunlu; otomatik patch/PR yok)
  ↓
Geri bildirim → sonraki kararlar
```

Bu, modelin ağırlıklarını eğitmez. Her değerlendirmeyi ve insanın kabul/red
geri bildirimini yerel SQLite veritabanına yazar. Tekrarlanan benzer örneklerde
geçmiş sonuçları kullanır; az veri varsa düşük güven bildirir. Başarısız test
kararı her zaman bloke eder. Beynin hafızası `data/mercy.sqlite3` dosyasında
tutulur; hassas raporlar içerebileceğinden bu dosyayı güvenli saklayın.

## Kurulum ve çalıştırma

Detaylı platform adımları için [install.md](./install.md) belgesine bakın.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config/mercy.yaml.example config/mercy.yaml
python mercy.py
```

Örnek olayı `config/mercy.yaml` içindeki `input.incident` alanından
düzenleyebilirsiniz. Olay en az `error_type` ve `message` içermelidir;
`stack_trace` isteğe bağlıdır.

İlk çalıştırmada yapılandırılmış örnek olay ve karar kaydedilir. Simülasyonda test sonucu
`not_run` olduğu için aday ilerletilmez. Karar politikasını örneklemek için
`config/mercy.yaml` içindeki simülasyon test sonucunu `passed` veya `failed`
yapabilirsiniz; bu değer **gerçek test çalıştırıldığı anlamına gelmez**.

İnceleme sonrası her çalıştırmaya bir kez geri bildirim verin:

```bash
python mercy.py --feedback <RUN_ID> --outcome accepted
python mercy.py --feedback <RUN_ID> --outcome rejected --note "Gerekçe"
```

Karar hafızasının son kayıtlarını (yığın izlerini içermeyen kısa özetleri)
görüntülemek için:

```bash
python mercy.py --history
python mercy.py --history --limit 25
```

Yapılandırmayı başka konumdan vermek için `--config PATH` kullanılır. Veritabanı
yolu göreliyse yapılandırma dosyasının bulunduğu dizine göre çözülür.

## Testler

```bash
python -m unittest discover -s tests -v
```

## Sonraki mimari aşamalar

1. Gerçek hata girdileri için adapter arayüzü ve olay normalizasyonu.
2. LLM sağlayıcısı, yapılandırılmış çıktı ve patch doğrulama.
3. İzole worktree ve zaman sınırlı test runner.
4. İnsan onayı sonrası branch/PR adapter'ı.

Her aşama kendi arayüzüyle eklenmeli; gerçek kaynaklar ve kod değişiklikleri
devreye alınmadan önce onay ve izolasyon sınırları korunmalıdır.

Güncel tamamlanan işler ve eksikler [progress.md](./progress.md), bileşen
sınırları [architecture.md](./architecture.md), katkı adımları
[CONTRIBUTING.md](./CONTRIBUTING.md) içindedir. `.claudeignore` araç bağlamı
için hassas/üretilmiş dosya yollarını listeler; gerçek sürüm kontrolü
hariç tutma kuralları `.gitignore` içindedir.

## Lisans

Bu proje [Fair Source License v1.0](LICENSE) ile lisanslanmıştır. Ticari lisans
konuları için [license@mercy.dev](mailto:license@mercy.dev) ile iletişime geçin.
