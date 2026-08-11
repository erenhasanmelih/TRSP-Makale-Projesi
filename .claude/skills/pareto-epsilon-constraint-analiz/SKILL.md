---
name: pareto-epsilon-constraint-analiz
description: CV ve EV modelleri (veya exact model ile heuristic) arasındaki çok amaçlı trade-off'u ε-Constraint yöntemiyle Pareto cephesine dönüştürür — bir amacı (örn. maliyet) birincil hedef, diğerini (örn. çözüm süresi/emisyon) parametrik üst sınır olarak ele alan tarama planı ve baskılanan (dominated) çözümleri eleyen tablo üretir. CV/EV veya exact/heuristic arasında Pareto karşılaştırması gerektiğinde kullan.
---

# Pareto ε-Constraint Analiz

`concepts/pareto_epsilon_constraint.md` ve `decisions/karar_pareto_epsilon_constraint_plani.md`'de planlanan çok amaçlı CV/EV karşılaştırmasını yürütmek için kullanılan analitik şablon. [[trsp-karsilastirma-analisti]] ajanı tarafından kullanılır.

## Ne Zaman Kullanılır

- CV vs EV arasında maliyet-vs-çözüm süresi veya maliyet-vs-operasyonel kısıt trade-off'u Pareto cephesi olarak çıkarılmak istendiğinde.
- Exact model ile hibrit sezgisel arasındaki çözüm kalitesi vs. çözüm süresi trade-off'u karşılaştırılırken.
- `raw/sonuclar/*.docx` sonuçlarından baskılanan (dominated) koşuları eleyip yalnızca Pareto-optimal noktaları raporlamak gerektiğinde.

## Girdi Formatı

```
Birincil amaç: örn. toplam rota maliyeti (minimize)
İkincil amaç (ε ile sınırlanacak): örn. çözüm süresi veya toplam gecikme
ε tarama aralığı: [min, max] + adım sayısı
Veri kaynağı: raw/sonuclar/*.docx dosyalarından çıkarılan (metrik, değer) çiftleri
```

## Çıktı Formatı

1. **ε tarama tablosu:** her ε değeri için birincil amacın optimal/elde edilen değeri.
2. **Baskılama (dominance) filtresi:** bir çözüm başka bir çözüme göre her iki amaçta da eşit veya kötüyse elenir — kalan noktalar Pareto-optimal küme.
3. **Pareto cephesi tablosu:** (çözüm ID, amaç1, amaç2, kaynak dosya) — grafik/tablo olarak `syntheses/` sayfasına gömülür.
4. **Yorum paragrafı:** cephenin şekli (dışbükey/içbükey), hangi bölgede CV'nin hangi bölgede EV'nin baskın olduğu.

## Adımlar

1. `docx-sonuc-cikarici` skill'iyle ilgili `raw/sonuclar/*.docx` dosyalarından ham metrik çiftlerini çıkar.
2. Birincil/ikincil amacı ve ε aralığını belirle; `concepts/pareto_epsilon_constraint.md`'deki mevcut metodoloji notlarıyla tutarlılığını kontrol et.
3. Baskılama filtresini uygula, Pareto-optimal noktaları belirle.
4. Tabloyu ve yorumu `syntheses/` altında atomik bir sayfa olarak dosyala (örn. `syntheses/cv_ev_pareto_analizi.md`), `decisions/karar_pareto_epsilon_constraint_plani.md`'ye geri link ver.

## Örnek

**Girdi:** "C10 ve R10 sonuçlarından CV/EV için maliyet-vs-çözüm süresi Pareto cephesini çıkar."

**Çıktı:** ε (çözüm süresi üst sınırı) taramasına göre elde edilen maliyet tablosu + Pareto-optimal alt küme + "EV, düşük ε (kısa süre) bölgesinde CV'ye göre X birim daha maliyetli, geniş ε'de fark kapanıyor" tarzı yorum.

## İlgili

- `concepts/pareto_epsilon_constraint.md`
- `decisions/karar_pareto_epsilon_constraint_plani.md`
- İlişkili skill: `docx-sonuc-cikarici`
