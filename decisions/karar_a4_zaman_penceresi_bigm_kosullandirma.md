---
title: Karar (Faz 2, A4) — Zaman Penceresi Big-M Koşullandırması (Hibrit Yaklaşım)
tags: [karar, faz2, big-m, zaman-penceresi, a4, infeasibility]
source: src/EV_v_1_1_fixed.py; src/CV_model_gurobi_fixed.py
date: 2026-08-11
status: güncel
---

# Karar (Faz 2, A4) — Zaman Penceresi Big-M Koşullandırması (Hibrit Yaklaşım)

## Sorun

`raw/`'daki `c16`/`c17`/`c18` (zaman penceresi/yetkinlik kısıtları) hiçbir Big-M gevşetmesi olmadan **koşulsuz** yazılıyordu. Bu, boş bir `(i,t)` çifti — yani bir düğümü ziyaret etme zaman penceresi `t` ekibi için hiç uygun olmasa da veya `t` o düğüme hiç yetkin değilse — kısıtın yine de modele eklenmesine ve tüm modeli **infeasible** kılabilecek gereksiz bir kısıtlamaya yol açıyordu.

## Karar — hibrit yaklaşım

Üç parçalı bir çözüm uygulandı:

1. **`t not in Ti[i]`** (ekip `t` düğüm `i`'ye zaman penceresi açısından hiç uygun değilse) → kısıt **hiç yazılmıyor** (üretim aşamasında atlanıyor, Gurobi'ye hiç eklenmiyor).
2. **Yetkin ama ziyaret etmeyen ekipler** (kısıt yazılıyor ama `x=0` olduğunda etkisiz olmalı) → Big-M gevşetmesi eklendi:
   - `M16 = es[t] + tt[0,i]` (erken başlama zamanı + depo-i seyahat süresi)
   - `M17 = tau_ub[i] + st[i] + tt[i,0] + 3600 - ls[t]` (üst zaman sınırı + servis + dönüş + 1 saat tampon - ekibin geç bitiş zamanı)
   - `M18 = ec[i]` (düğümün en erken tamamlanma zamanı)
3. **`c18_ub`** (kutu üst sınırı) **koşulsuz bırakıldı** — gerekçe: bu kısıtın üst sınırı zaten `lc[i]` (düğümün geç tamamlanma zamanı) olduğundan, tek başına bir infeasibility kaynağı üretemez; kutu kısıtları (değişkenin kendi UB/LB'si) `x`'in 0/1 değerinden bağımsız olarak her zaman geçerlidir ve bir arc seçilmediğinde otomatik olarak gevşemez ama zaten aktif bir infeasibility riski taşımaz (M gerektirmez).

## Konum

- `src/EV_v_1_1_fixed.py:343-380,455-468`
- `src/CV_model_gurobi_fixed.py:252-290`

## Doğrulama

40 kısıttan 29'unda türetilen M=0 çıkıyor — bu **beklenen ve doğru** bir sonuç: M=0 çıkan kısıtlar, zaten geometrik/zamansal olarak gevşetmeye ihtiyaç duymayan (örn. zaten sıkı) durumları temsil ediyor; kalan 11'i gerçek gevşetme gerektiren durumlar.

## İlişki

Bu karar [[karar_c2_tight_big_m_uygulamasi]] (C2, sabit `100000.0`'ın türetilmiş M'lerle değiştirilmesi) ile aynı genel "tight Big-M" temasının parçası ama ayrı bir sorun kodudur (A4) — çünkü buradaki asıl motivasyon sadece performans değil, **infeasibility riskini gidermek**.

## Güncelleme (2026-08-22)

`raw/EV_v.1.1.py`/`raw/CV_model_gurobi_exact.py` (bu sayfanın "orijinal koşulsuz c16/c17/c18" olarak gösterdiği dosyalar) 2026-08-22'de değişti. Yeni kodda CV15/16/18 ve EV13/14/16 (zaman penceresi/mesai) kısıtları hâlâ, kaynağın (`kk`) o düğüme yetkinlik açısından uygun olup olmadığından bağımsız olarak, **tüm `(i,kk)` çiftleri için koşulsuz** yazılıyor (A4'ün çözmeye çalıştığı desenle aynı yapı) — ama mevcut veri setinde tüm ekiplere aynı `es`/`ls`/`el`/`ll` atandığından (`data['es'] = {crew: base_es for crew in T_list}` gibi), bu pratikte bir infeasibility riski yaratmıyor gibi görünüyor. Doğrulanmadı, kapsamlı bir statik okuma değil — sadece bir gözlem. Bkz. [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]], [[sources/2026-08-22-ev_v1_1_rewrite]].

## Sources

- `src/EV_v_1_1_fixed.py:343-380,455-468`
- `src/CV_model_gurobi_fixed.py:252-290`
- `raw/EV_v.1.1.py` (orijinal koşulsuz c16/c17/c18 — eski, 2026-08-09 hâli)
- `raw/CV_model_gurobi_exact.py` (orijinal koşulsuz c16/c17/c18 — eski, 2026-08-09 hâli)

## Related

- [[karar_c2_tight_big_m_uygulamasi]]
- [[karar_tight_big_m_gecisi_plani]]
- [[tight_big_m]]
- [[parametre_big_m_100000]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
