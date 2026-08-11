---
name: model-kod-celiski-denetleyici
description: Bir yönerge dokümanı (raw/Yönergelerimiz/*.docx) iddiasını ilgili Python kaynak kodu (CV_model_gurobi_exact.py, EV_v.1.1.py) satırlarıyla karşılaştırıp doğrulama durumunu (doğrulandı/çürütüldü/nüanslandı) belirler ve CLAUDE.md §7 formatında hazır bir "## ÇELİŞKİ" veya "## Doğrulama" markdown bloğu üretir. Yeni bir docx iddiası kodla karşılaştırılacağı veya mevcut bir çelişki/sorun sayfası güncel kodla yeniden doğrulanacağı zaman kullan.
---

# Model↔Kod Çelişki Denetleyici

Yönerge (docx) iddiası ile fiili kod davranışı arasındaki her sapmayı, CLAUDE.md'nin "kaynaksız iddia yasak" ve "çelişkiler işaretlenir, silinmez" kurallarına uygun şekilde belgeleyen süreç. [[trsp-exact-model-mimari]] ajanı tarafından kullanılır.

## Ne Zaman Kullanılır

- `raw/Yönergelerimiz/*.docx` içindeki bir kısıt/kural iddiası ilk kez kodla karşılaştırılırken.
- Kod değiştiği için daha önce doğrulanmış bir `decisions/celiski_*.md` veya `decisions/sorun_*.md` sayfasının güncel kodla hâlâ tutarlı olup olmadığı kontrol edilirken.
- `trsp-wiki-kutuphaneci`'nin LINT taramasında "stale claim" olarak işaretlediği bir sayfayı yeniden doğrularken.

## Girdi Formatı

```
İddia: "Öğle molası kullanımı zorunludur (=1)." (kaynak: raw/Yönergelerimiz/... .docx)
Karşılaştırılacak dosya(lar): raw/CV_model_gurobi_exact.py, raw/EV_v.1.1.py
Aranacak desen: mola kısıtı (örn. "mola_max1" adlı kısıt bloğu)
```

## Çıktı Formatı

Üç olası doğrulama durumundan biri, satır referanslı kanıtla:

| Durum | Anlamı | Markdown başlığı |
|---|---|---|
| **Doğrulandı** | İddia kodda birebir doğrulanır | `## Doğrulama` |
| **Çürütüldü** | İddia kodda bulunamaz/tam tersi doğru | `## ÇELİŞKİ` |
| **Nüanslandı** | Kısmen doğru, kısmen farklı (örn. sadece bir modelde var) | `## ÇELİŞKİ (nüans)` |

Çıktı şablonu:
```markdown
## ÇELİŞKİ

**Docx iddiası:** [iddia metni] — kaynak: `raw/Yönergelerimiz/dosya.docx`
**Kod gerçeği:** [gözlem] — kaynak: `raw/dosya.py` (satır N-M)
**Değerlendirme:** [doğrulandı/çürütüldü/nüanslandı — gerekçe]
**Durum:** çözülmedi | çözüldü (tarih + not)
```

## Adımlar

1. İddiayı `sources/` altındaki ilgili özet sayfasından veya doğrudan docx'ten al.
2. `Grep` ile kod tabanında ilgili kısıt/değişken adını ara (örn. kısıt isim deseni `addConstr(..., name="...")`).
3. Bulunan kod bloğunu satır numarasıyla oku, iddiayla birebir karşılaştır.
4. Durum belirle (doğrulandı/çürütüldü/nüanslandı) ve yukarıdaki şablonla markdown bloğu üret.
5. İlgili `decisions/celiski_*.md` veya `decisions/sorun_*.md` sayfasını güncelle (mevcutsa ekle, yoksa CLAUDE.md §5 formatında yeni sayfa oluştur) — **eski bulguyu asla silme**, "## ÇELİŞKİ (güncelleme)" olarak ekle.
6. `syntheses/model_kod_farkliliklari_genel_sentez.md`'nin özet tablosunu gerekiyorsa güncelle.

## Örnek

Bkz. `decisions/celiski_ogle_molasi_zorunlulugu.md` (Doğrulandı — CV:88-96, EV:177-183, kod `<=1` kullanıyor, docx `=1` iddia ediyor) ve `decisions/celiski_single_trip_vs_multitrip.md` (Çürütüldü — docx'ün tarif ettiği `c4_multitrip_{v}` kısıtı kodda bulunamadı).

## İlgili

- `syntheses/model_kod_farkliliklari_genel_sentez.md`
- CLAUDE.md §7 madde 2 ve 4 (kaynaksız iddia yasak, çelişkiler işaretlenir)
- İlişkili skill: `gurobi-big-m-formulator`
