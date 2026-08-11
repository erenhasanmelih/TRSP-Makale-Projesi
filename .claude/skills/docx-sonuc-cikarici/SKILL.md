---
name: docx-sonuc-cikarici
description: raw/sonuclar/ altındaki Gurobi optimizasyon sonuç raporlarını (.docx — C5/C7/C10/C13, R5/R7/R10/R13, RC5/RC7/RC10/RC13, Optimizasyon_Sonuclari_Birlesimi) okuyup çözüm süresi, amaç fonksiyonu değeri, MIP gap, düğüm sayısı ve feasibility durumu gibi sayısal metrikleri yapılandırılmış bir tabloya çıkarır. Bir veya birden fazla sonuç raporundan sayısal karşılaştırma yapılması gereken her durumda kullan.
---

# Docx Sonuç Çıkarıcı

`raw/sonuclar/*.docx` dosyalarındaki serbest-metin optimizasyon raporlarını, karşılaştırma ve Pareto analizine hazır satır-sütun formatına dönüştüren çıkarım şablonu. [[trsp-karsilastirma-analisti]] ajanı tarafından kullanılır.

## Ne Zaman Kullanılır

- Birden fazla `.docx` sonuç raporu tek bir karşılaştırma tablosunda birleştirilmek istendiğinde.
- `pareto-epsilon-constraint-analiz` skill'inin girdi verisi hazırlanırken.
- `trsp-wiki-kutuphaneci`'nin LINT taramasında "raw/sonuclar/'dan çıkarılabilecek ama henüz syntheses/'a işlenmemiş performans karşılaştırması" bulgusuna yanıt verilirken.

## Girdi Formatı

```
Dosya(lar): raw/sonuclar/C10.docx, raw/sonuclar/R10.docx, ...
Çıkarılacak metrikler: çözüm süresi (sn), amaç fonksiyonu değeri, MIP gap (%), Branch&Bound düğüm sayısı, feasibility/infeasibility durumu, kullanılan Gurobi tuning parametreleri (varsa)
```

## Çıktı Formatı

Standart karşılaştırma tablosu (her satır bir problem seti/koşu):

| Problem Seti | Model (CV/EV) | Çözüm Süresi (sn) | Amaç Değeri | MIP Gap (%) | Düğüm Sayısı | Durum | Kaynak |
|---|---|---|---|---|---|---|---|
| C10 | CV | ... | ... | ... | ... | optimal/feasible/infeasible | `raw/sonuclar/C10.docx` |

## Adımlar

1. `.docx` dosyasını oku (python-docx ile metin çıkarımı gerekebilir — Bash aracıyla `python -c "from docx import Document; ..."` çalıştırılabilir).
2. Rapor içindeki sayısal değerleri (Gurobi log çıktısı formatına benzer ifadeler: "Optimal solution found", "MIPGap", "Explored N nodes" vb.) düzenli ifadelerle (regex) veya dikkatli okuma ile ayıkla.
3. Her dosya için bir satır oluştur, kaynak dosya adını mutlaka koru (kaynaksız iddia yasak kuralı gereği).
4. Eksik/belirsiz bir değer varsa hücreyi boş bırak, asla tahmin ederek doldurma — bunun yerine "docx'te belirtilmemiş" notu düş.
5. Tabloyu ilgili `syntheses/` sayfasına veya `pareto-epsilon-constraint-analiz` skill'inin girdisine aktar.

## Örnek

**Girdi:** "C5, C7, C10, C13 dosyalarındaki çözüm sürelerini tek tabloda topla."

**Çıktı:** 4 satırlık tablo (her problem setinin çözüm süresi + amaç değeri + durum) — "müşteri sayısı arttıkça çözüm süresinin nasıl büyüdüğü" gözlemiyle birlikte.

## İlgili

- `entities/gurobi_mip_cozucusu.md`
- İlişkili skill: `pareto-epsilon-constraint-analiz`

**Not:** `raw/sonuclar/` ikincil kaynaktır (CLAUDE.md §6) — bu skill yalnızca kullanıcı/ajan açıkça belirli dosyaları hedeflediğinde çalıştırılır, toplu otomatik tarama yapılmaz.
