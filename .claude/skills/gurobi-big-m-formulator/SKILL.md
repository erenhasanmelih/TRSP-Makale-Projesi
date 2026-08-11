---
name: gurobi-big-m-formulator
description: TRSP exact MIP modelinde (CV_model_gurobi_exact.py, EV_v.1.1.py) yeni bir kısıt için Big-M / tight Big-M formülasyonu üretir ve mevcut bir Big-M sabitinin (örn. sabit 100000.0) gereğinden gevşek olup olmadığını denetler. Yeni bir doğrusal olmayan/koşullu kısıtı gurobipy addConstr koduna dönüştürürken veya mevcut Big-M sabitlerini sıkılaştırırken (tight Big-M'e geçiş) kullan.
---

# Gurobi Big-M Formulator

TRSP exact modelinde koşullu kısıtları ("eğer x[i,j,v,t]=1 ise Y kısıtı geçerli olsun") doğrusal MIP kısıtına çeviren ve Big-M sabitinin sıkılığını (tightness) denetleyen bir yardımcı yetenek. [[trsp-exact-model-mimari]] ajanı tarafından kullanılır.

## Ne Zaman Kullanılır

- Yeni bir koşullu/doğrusal-olmayan davranışı (örn. yeni bir şarj/mola kuralı) gurobipy kısıtına dönüştürmek gerektiğinde.
- Mevcut sabit Big-M kullanımını (`parametre_big_m_100000` — bkz. `entities/parametre_big_m_100000.md`) tight Big-M'e geçirme planının (`decisions/karar_tight_big_m_gecisi_plani.md`) bir adımını uygularken.
- Bir kısıtın gereğinden büyük M kullanıp çözücü performansını (relaxation gap) kötüleştirip kötüleştirmediğini denetlerken.

## Girdi Formatı

```
Kısıt tanımı (doğal dil): "Eğer x[i,j,v,t]=1 ise, aracın j düğümüne varış zamanı (arr_j) i düğümünden ayrılış zamanından (dep_i) + seyahat süresinden (t_ij) küçük olamaz."
İlgili karar değişkenleri: x[i,j,v,t] (ikili), arr_j (sürekli), dep_i (sürekli)
Parametre aralıkları: t_ij ∈ [0, T_max], arr/dep ∈ [0, HORIZON]
```

## Çıktı Formatı

1. **Matematiksel formülasyon (LaTeX):**
   `arr_j >= dep_i + t_ij - M*(1 - x[i,j,v,t])`
2. **Tight M hesabı:** `M = HORIZON - t_ij_min` gibi değişkene özgü bir üst sınır (sabit 100000.0 yerine).
3. **gurobipy kod bloğu:**
   ```python
   M_ij = HORIZON - min_travel_time[i][j]
   model.addConstr(
       arr[j] >= dep[i] + t[i, j] - M_ij * (1 - x[i, j, v, t]),
       name=f"time_prop_{i}_{j}_{v}_{t}",
   )
   ```
4. **Sıkılık raporu:** kullanılan M'in her arc/kısıt için mümkün olan en küçük değere ne kadar yakın olduğu (`M_kullanilan / M_teorik_min` oranı).

## Adımlar

1. Kısıtın "eğer-o zaman" mantığını belirle, hangi ikili değişkenin (`x[i,j,v,t]` gibi) tetikleyici olduğunu tespit et.
2. Kısıtın aktif olmadığı durumda (tetikleyici=0) eşitsizliğin otomatik sağlanması için gereken minimum M'i, ilgili değişkenlerin bilinen alt/üst sınırlarından (`HORIZON`, `T_max`, mesafe matrisi vb.) türet — asla sabit `100000.0` kullanma.
3. LaTeX formülasyonunu ve gurobipy kodunu üret.
4. Mevcut kodda aynı kalıptaki başka bir kısıt varsa (`entities/parametre_big_m_100000.md`'deki kullanım noktaları), M değerinin tutarlı türetildiğini doğrula.
5. Sonucu `decisions/karar_tight_big_m_gecisi_plani.md` sayfasına ilerleme notu olarak ekle (CLAUDE.md §5 formatında, kaynak satır referanslı).

## Örnek

**Girdi:** EV modelinde şarj istasyonunda kalan enerjinin (`ye[i]`) bir sonraki düğüme yetip yetmediğini kontrol eden kısıt, şu an `100000.0` ile gevşetilmiş (bkz. `raw/EV_v.1.1.py`).

**Çıktı:** `M_enerji = BATTERY_CAPACITY` (araç bataryasının fiziksel üst sınırı, `100000.0`'dan çok daha küçük) kullanan yeni kısıt kodu + eski/yeni M oranı raporu (`100000 / BATTERY_CAPACITY ≈ Nx` sıkılaştırma faktörü).

## İlgili

- `decisions/karar_tight_big_m_gecisi_plani.md`
- `concepts/tight_big_m.md`
- `entities/parametre_big_m_100000.md`
- İlişkili skill: `model-kod-celiski-denetleyici`
