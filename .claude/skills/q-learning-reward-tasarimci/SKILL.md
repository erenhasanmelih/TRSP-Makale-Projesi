---
name: q-learning-reward-tasarimci
description: TRSP hibrit sezgiselindeki Q-Learning bileşeni için durum (state), eylem (action) ve ödül (reward) şemasını tasarlar; Q-tablosu güncelleme formülünü ve epsilon-greedy keşif takvimini somutlaştırır. VND operatör seçimini öğrenen Q-Learning ajanının durum/eylem/ödül tanımı ilk kez yapılırken veya mevcut şema üzerinde tasarım kararı gerekçelendirilirken kullan.
---

# Q-Learning Reward Tasarımcı

VND operatör seçimini öğrenen Q-Learning bileşeninin (Yıldız vd., 2025 referansı — bkz. `decisions/karar_hibrit_algoritma_mimari_sirasi.md`) durum-eylem-ödül tasarımını yapılandıran şablon. [[trsp-hibrit-sezgisel-muhendisi]] ajanı tarafından kullanılır.

## Ne Zaman Kullanılır

- Q-Learning ajanının durum uzayı (hangi çözüm özellikleri state'i tanımlayacak) ilk kez tasarlanırken.
- Eylem uzayı (`vnd-operator-tasarimci` ile tasarlanan operatör seti) Q-Learning eylemleriyle eşlenirken.
- Ödül fonksiyonu (çözüm kalitesi iyileşmesi mi, feasibility mi, ikisinin ağırlıklı toplamı mı) tasarlanırken.
- Epsilon-greedy keşif/exploit dengesinin takvimi (sabit mi, azalan mı) belirlenirken.

## Girdi Formatı

```
Eylem adayları: [Swap, Insert, Reverse, Drop/Add] (vnd-operator-tasarimci çıktısı)
Optimizasyon hedefi: toplam rota maliyeti (mesafe + zaman) minimizasyonu
Kısıt ihlali maliyeti: feasibility kaybı nasıl cezalandırılacak?
```

## Çıktı Formatı

1. **Durum (state) tanımı:** çözümün hangi özet istatistikleri (örn. toplam maliyet, ihlal sayısı, son k iyileşme trendi) state olarak kodlanacak — ayrık/sürekli, bucket'lama stratejisi.
2. **Eylem (action) uzayı:** operatör listesi + varsa parametreleri (örn. k-drop şiddeti).
3. **Ödül (reward) fonksiyonu:** matematiksel ifade, örn. `r = (maliyet_önce - maliyet_sonra) / maliyet_önce - ceza * ihlal_sayısı`.
4. **Q-tablosu güncelleme formülü:** `Q(s,a) ← Q(s,a) + α[r + γ·max_a' Q(s',a') − Q(s,a)]` — α (öğrenme oranı), γ (indirim faktörü) için önerilen başlangıç değerleri.
5. **Keşif takvimi:** epsilon başlangıç/bitiş değeri ve azalma stratejisi (lineer/üstel).
6. **Gerekçe notu:** her tasarım kararının neden seçildiği (alternatiflere kısa değinme).

## Adımlar

1. `concepts/q_learning.md` ve `decisions/karar_hibrit_algoritma_mimari_sirasi.md`'yi oku — mevcut bir tasarım kararı var mı kontrol et.
2. Eylem uzayını `vnd-operator-tasarimci` çıktısındaki operatör setiyle hizala.
3. Durum ve ödül tanımlarını somut formüllerle yaz; her seçimi 1-2 cümlelik gerekçeyle destekle.
4. α, γ, epsilon için literatür-temelli (Yıldız vd., 2025 veya benzer TRSP/VRP-RL çalışmaları) başlangıç değerleri öner.
5. Sonucu `decisions/karar_*.md` (yeni bir atomik karar sayfası, örn. `karar_q_learning_durum_eylem_odul_semasi.md`) olarak dosyala, `concepts/q_learning.md`'ye çapraz-referans ekle.

## Örnek

**Girdi:** "50-100 müşterilik problemde Q-Learning için state'i nasıl tanımlarız?"

**Çıktı:** State = `(iyileşme_trendi_bucket ∈ {azalan, sabit, artan}, ihlal_var_mı ∈ {0,1}, kalan_iterasyon_bucket ∈ {erken, orta, geç})` — 3 boyutlu ayrık state uzayı (toplam 3×2×3=18 durum), her biri için gerekçe (küçük state uzayı → hızlı yakınsama, büyük ölçekte pratik).

## İlgili

- `decisions/karar_hibrit_algoritma_mimari_sirasi.md`
- `concepts/q_learning.md`
- İlişkili skill: `vnd-operator-tasarimci`
