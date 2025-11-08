# 🕵️‍♂️ autopsy

**Otonom Hata Düzeltme Sistemi — Herkes Kullanabilir, Dağıtamaz.**

`autopsy`, hata raporları (Sentry, GitHub Issues, Loglar vs.) geldiğinde, bunları analiz eden, kod yaması üreten, test eden ve bir Pull Request açarak geliştiriciye sunan **açık kaynak, modüler ve AI destekli bir otomasyon sistemidir**.

> **"Hata geldi. Kod düzeltildi. PR açıldı. Sen uyuyorsun."**

---

## 🌟 Özellikler

- ✅ **Modüler mimari**: Her bileşen (giriş, analiz, yama, test, PR) bağımsız.
- ✅ **LLM entegrasyonu**: GPT, Claude, Ollama veya yerel modellerle çalışır.
- ✅ **Çoklu dil desteği**: Hata raporları ve PR'ler çok dilli olabilir.
- ✅ **Yerel çalışma**: Hiçbir bulut gerekmez — tamamen lokalde çalışır.
- ✅ **Güvenli**: Hiçbir değişiklik otomatik merge edilmez — her şey incelemeye sunulur.
- ✅ **Açık kaynak ama adaletli**: Herkes kullanabilir, ancak 5+ kişilik şirketler ticari olarak dağıtamaz.

---

## 🚫 Lisans (Kritik!)

Bu proje **[Fair Source License v1.0](LICENSE)** ile lisanslanmıştır:

> 🔹 **Herkes** kullanabilir (bireysel, akademik, küçük ekipler).  
> 🔹 **5+ kişilik şirketler**, bu kodu kendi ticari ürünlerinde **dağıtamaz**.  
> 🔹 Ticari kullanım için: [license@autopsy.dev](mailto:license@autopsy.dev)

---

## 🛠️ Kurulum (Simülasyon Modu)

```bash
# 1. Repo klonla
git clone https://github.com/yourusername/autopsy.git
cd autopsy

# 2. Gerekli kütüphaneleri kur
pip install -r requirements.txt

# 3. Yapılandırmayı düzenle
cp config/autopsy.yaml.example config/autopsy.yaml
nano config/autopsy.yaml  # LLM ve giriş kaynağını ayarla

# 4. Çalıştır
python autopsy.py
