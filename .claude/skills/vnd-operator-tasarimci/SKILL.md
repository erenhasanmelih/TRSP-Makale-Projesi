---
name: vnd-operator-tasarimci
description: TRSP hibrit sezgiselinin VND (Variable Neighborhood Descent) aşaması için komşuluk operatörü (Swap, Insert, Reverse, Drop/Add) taslağı üretir; her operatörün karmaşıklığını, hangi kısıtları (zaman penceresi, SoC, uyumluluk matrisi) koruyarak çalıştığını ve k-drop/add sarsma (shaking) parametrelerini belgeler. Yeni bir VND operatörü tasarlanırken veya mevcut operatör setinin sırası/parametreleri değerlendirilirken kullan.
---

# VND Operatör Tasarımcı

Q-Learning + VND hibrit algoritmasının (bkz. `decisions/karar_hibrit_algoritma_mimari_sirasi.md`) yerel arama operatörlerini tasarlamak için kullanılan yapılandırılmış şablon. [[trsp-hibrit-sezgisel-muhendisi]] ajanı tarafından kullanılır.

## Ne Zaman Kullanılır

- 4 temel operatörden (Swap, Insert, Reverse, Drop/Add) biri ilk kez tasarlanırken/kodlanırken.
- Mevcut bir operatörün TRSP'ye özgü kısıtları (zaman penceresi, EV SoC, uyumluluk matrisi/colored TSP) ihlal edip etmediği denetlenirken.
- k-drop/add sarsma mekanizmasının şiddet parametresi (kaç düğüm çıkarılıp yeniden eklenecek) belirlenirken.

## Girdi Formatı

```
Operatör adı: Insert
Kapsam: tek rota içi | rotalar arası
Korunması gereken kısıtlar: zaman penceresi, EV SoC (partial recharging), teknisyen-araç uyumluluk matrisi, öğle molası kuralı
Mevcut çözüm temsili: rota listesi [depot, c1, c2, ..., depot] her araç için
```

## Çıktı Formatı

1. **Operatör tanımı:** ne yapar, hangi komşuluk yapısını tarar (örn. "her müşteriyi çıkar, tüm olası pozisyonlara yeniden ekle, en iyi geçerli pozisyonu seç").
2. **Karmaşıklık:** O(n²) / O(n³) gibi, n = rota uzunluğu.
3. **Feasibility kontrol listesi:** operatör sonrası hangi kısıtların yeniden kontrol edilmesi gerektiği (zaman penceresi ileri yayılım, SoC yeniden hesaplama, mola kuralı).
4. **Pseudocode / Python taslağı.**
5. **Q-Learning arayüzü notu:** bu operatörün Q-Learning'de hangi "eylem" olarak temsil edileceği (`q-learning-reward-tasarimci` skill'iyle uyumlu).

## Adımlar

1. Operatörün kapsamını (rota-içi mi rotalar-arası mı) ve hangi TRSP kısıtlarını etkileyebileceğini belirle (`concepts/uyumluluk_matrisi.md`, `concepts/partial_recharging.md`'yi kontrol et).
2. Pseudocode/Python taslağını yaz; her hamle sonrası feasibility yeniden kontrolünü açıkça belirt.
3. Karmaşıklık tahminini yap, büyük ölçek (50-100 müşteri) için pratik olup olmadığını değerlendir.
4. Operatörü `concepts/vnd.md` sayfasına ekle veya güncelle; kaynak olarak bu skill'in ürettiği tasarım kararını referans ver.
5. Eğer operatör literatürdeki bir alternatifle (VLSN, ALNS) karşılaştırılabilirse `concepts/literatur_alternatif_metasezgiseller.md`'ye çapraz-referans ekle.

## Örnek

**Girdi:** "Drop/Add operatörünü EV modeli için tasarla — bir müşteriyi rotadan çıkarıp SoC kısıtını ihlal etmeyen başka bir rotaya ekle."

**Çıktı:** Drop/Add pseudocode'u + her ekleme denemesinde SoC ileri yayılımının (partial recharging dinamikleriyle) yeniden hesaplanması gerektiğine dair feasibility notu + O(n·m) karmaşıklık tahmini (n=müşteri sayısı, m=araç sayısı).

## İlgili

- `decisions/karar_hibrit_algoritma_mimari_sirasi.md`
- `concepts/vnd.md`, `concepts/uyumluluk_matrisi.md`, `concepts/partial_recharging.md`
- İlişkili skill: `q-learning-reward-tasarimci`
