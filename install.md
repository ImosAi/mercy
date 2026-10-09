# Kurulum

Mercy'nin mevcut sürümü yerel bir simülasyon ve karar hafızası prototipidir.
Sentry/GitHub bağlantısı, LLM çağrısı, gerçek test çalıştırma, patch uygulama
ve PR açma henüz desteklenmez.

## Gereksinimler

- Python 3.10 veya üzeri
- `pip`
- SQLite desteği (Python standart kütüphanesindeki `sqlite3`)

## Linux ve macOS

Depo kök dizininde:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp config/mercy.yaml.example config/mercy.yaml
python mercy.py
```

İlk çalıştırma yapılandırmaya göre `data/mercy.sqlite3` yerel hafıza veritabanını
oluşturur. Yerel yapılandırma ve veritabanı Git'e eklenmemelidir; `.gitignore`
tarafından hariç tutulurlar.

## Windows (PowerShell)

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item config/mercy.yaml.example config/mercy.yaml
python mercy.py
```

PowerShell sanal ortam etkinleştirme politikasını engellerse, kurumunuzun
güvenlik politikasına uygun olarak Python ortamını etkinleştirin veya sanal
ortamın `python.exe` dosyasını doğrudan çalıştırın.

## Yapılandırma

`config/mercy.yaml.example` dosyasını `config/mercy.yaml` olarak kopyalayın.
Örnek ayarlar:

```yaml
input:
  source: mock

memory:
  database: ../data/mercy.sqlite3

simulation:
  test_status: not_run
```

Veritabanı yolu göreliyse yapılandırma dosyasının konumuna göre çözülür.
`simulation.test_status` yalnızca karar politikasını denemek içindir; `passed`
veya `failed` seçmek herhangi bir test komutu çalıştırmaz.

Farklı yapılandırma dosyası seçmek için:

```bash
python mercy.py --config /tam/yol/mercy.yaml
```

## İnsan geri bildirimi

Her çalıştırma çıktısındaki kimliği kullanarak kararın incelendiğini kaydedin:

```bash
python mercy.py --feedback <RUN_ID> --outcome accepted
python mercy.py --feedback <RUN_ID> --outcome rejected --note "Kısa gerekçe"
```

Geri bildirim her çalıştırma için bir kez kaydedilir ve yalnızca yerel
veritabanında, benzer hata imzalarının sonraki kararlarında kullanılır.

Kararların ve geri bildirim durumlarının kısa geçmişini görmek için:

```bash
python mercy.py --history
python mercy.py --history --limit 25
```

Geçmiş görünümü yığın izini göstermez. SQLite dosyasının kendisi tam hata
raporlarını içerebilir; erişimini koruyun.

## Testler

```bash
python -m unittest discover -s tests -v
```

## Sorun giderme

- `No module named yaml`: sanal ortamın etkin olduğundan emin olun ve
  `python -m pip install -r requirements.txt` komutunu çalıştırın.
- Yapılandırma bulunamıyor: `config/mercy.yaml` dosyasının oluşturulduğunu
  doğrulayın veya `--config` ile dosya yolunu belirtin.
- Kaynak desteklenmiyor: bu sürümde yalnızca `input.source: mock` geçerlidir.
- Eski kararlar görünmüyor: yapılandırmada aynı SQLite veritabanı yolunun
  kullanıldığını doğrulayın.
