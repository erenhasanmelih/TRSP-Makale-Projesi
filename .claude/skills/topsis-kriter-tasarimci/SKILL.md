---
name: topsis-kriter-tasarimci
description: TRSP haftalık çizelgeleme aşamasında TOPSIS ile teknisyen sıralaması veya iş emri önceliklendirmesi için karar kriterleri matrisini (kriterler, ağırlıklar, fayda/maliyet yönü) tasarlar ve normalize edilmiş TOPSIS skor hesabı şablonu üretir. Yeni bir çok-kriterli sıralama ihtiyacı (teknisyen sıralama, iş önceliklendirme) ortaya çıktığında kullan.
---

# TOPSIS Kriter Tasarımcı

Haftalık çizelgeleme aşamasının (bkz. `decisions/karar_3_asamali_rolling_horizon_sistem_mimarisi.md`, adım 1) TOPSIS bileşeni için kriter matrisini yapılandırılmış şekilde tasarlayan şablon. [[trsp-tahmin-veri-muhendisi]] ajanı tarafından kullanılır.

## Ne Zaman Kullanılır

- Teknisyen sıralaması (kimin hangi işe öncelikli atanacağı) için kriter seti ilk kez tanımlanırken.
- İş emri önceliklendirmesi (hangi iş emrinin haftalık havuzdan günlük plana daha önce girmesi gerektiği) için TOPSIS uygulanırken.
- Mevcut kriter ağırlıklarının duyarlılık analizi (`trsp-karsilastirma-analisti` ile birlikte) gerektiğinde.

## Girdi Formatı

```
Alternatifler: teknisyen listesi | iş emri listesi
Aday kriterler: örn. yetkinlik-uyumu, mesafe, iş yükü dengesi, iptal olasılığı skoru (CatBoost çıktısı), zaman penceresi aciliyeti
Kriter yönü: her biri için fayda (max) mi maliyet (min) mi
```

## Çıktı Formatı

1. **Kriter matrisi tablosu:** kriter adı | yön (fayda/maliyet) | önerilen ağırlık | veri kaynağı (hangi entity/kod alanından geliyor).
2. **Normalize edilmiş karar matrisi formülü:** `r_ij = x_ij / sqrt(Σx_ij²)`.
3. **Ağırlıklı normalize matris ve ideal/negatif-ideal çözüm tanımı.**
4. **Yakınlık katsayısı (closeness coefficient) formülü:** `C_i = d_i^- / (d_i^+ + d_i^-)`.
5. **Python/pandas taslağı** (skor hesaplama fonksiyonu).

## Adımlar

1. `entities/topsis.md` ve `decisions/karar_3_asamali_rolling_horizon_sistem_mimarisi.md`'yi oku — mevcut bir kriter seti tanımlı mı kontrol et.
2. Aday kriterleri projenin veri kaynaklarıyla (CatBoost tahmin skoru, uyumluluk matrisi, coğrafi mesafe) eşleştir; her kriter için kaynağı belirt.
3. Fayda/maliyet yönünü ve ilk ağırlık önerisini gerekçelendir (eşit ağırlık başlangıç noktası olabilir, sonra duyarlılık analiziyle ayarlanır).
4. Skor hesaplama formülünü ve Python taslağını üret.
5. Sonucu `entities/topsis.md` sayfasına "kriter matrisi" alt bölümü olarak ekle veya yeni bir `decisions/karar_topsis_kriter_matrisi.md` sayfası aç.

## Örnek

**Girdi:** "Teknisyen sıralaması için TOPSIS kriterlerini tasarla."

**Çıktı:** Kriter tablosu — {yetkinlik-uyumu (fayda, w=0.35, kaynak: `concepts/uyumluluk_matrisi.md`), mevcut iş yükü (maliyet, w=0.25), müşteriye mesafe (maliyet, w=0.20), geçmiş iptal oranı (maliyet, w=0.20)} + normalize/ağırlıklandırma formülleri + `pandas` skor fonksiyonu taslağı.

## İlgili

- `entities/topsis.md`, `entities/catboost.md`
- `decisions/karar_3_asamali_rolling_horizon_sistem_mimarisi.md`
- İlişkili skill: `solomon-sentetik-veri-uretici`
