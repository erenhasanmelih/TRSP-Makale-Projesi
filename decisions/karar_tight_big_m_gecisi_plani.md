---
title: Karar (Planlı) — Sıkı Big-M'e Geçiş
tags: [karar, planlı, matematiksel-model, big-m]
source: raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Karar (Planlı) — Sıkı Big-M'e Geçiş

## Karar

Koddaki sabit `100000.0` Big-M değerleri, Cordeau vd. (2002)'ye atıfla, müşterilerin zaman pencereleri arasındaki farka göre hesaplanan dinamik değerlere dönüştürülecek. Ek olarak "makale adımlar ve düzenlemeler.docx"'e göre Big-M, her teknisyenin o günkü maksimum mesai bitiş süresiyle sınırlandırılacak; MTZ alt-tur önleme kısıtlarıyla birlikte ele alınacak.

## Gerekçe

Gevşek (çok büyük) Big-M, Branch-and-Bound ağacının etkin budama yapmasını engelliyor — bu modelin 10-13/10-15 düğümde tıkanmasının ana nedenlerinden biri olarak teşhis edilmiş.

## Kapsam / Faz

Faz 1 (Kod Revizyonu) kapsamında, sadece `CV_model_gurobi_exact.py` için planlanmış.

## Uygulama (Faz 2, 2026-08-11)

**Bu plan uygulandı — kapsam CV'ye ek olarak EV'yi de içerecek şekilde genişledi** (plan metni sadece `CV_model_gurobi_exact.py`'yi hedefliyordu, ama aynı sabit `100000.0` deseni `EV_v.1.1.py`'de de vardı ve orada da düzeltildi). `src/CV_model_gurobi_fixed.py` ve `src/EV_v_1_1_fixed.py`'de 4 kısıt grubunda (`c8` zaman ilerlemesi, mola başlama alt/üst sınırı, molasız erken dönüş, `c_full_depot_lb/ub`, `c20/c21`) sabit `100000.0` yerine zaman penceresi farkından türetilen M değerleri kondu.

Planın önerdiği iki bileşenden **Cordeau vd. (2002) tarzı zaman penceresi farkına dayalı türetme** uygulandı; **MTZ alt-tur önleme kısıtlarıyla birlikte ele alma** kısmı bu refaktörün kapsamına girmedi (kod zaten `tau[i,t]` zaman-ilerleme değişkenleriyle alt-tur önlüyor, ayrı bir MTZ kısıtı eklenmedi — bkz. lint-report-2026-08-09.md K1 bulgusu, hâlâ çözülmemiş).

**Sapma notu:** kullanıcının önerdiği `M_ij = max(0, lc[i]+st[i]+break+tt[i,j]-ec[j])` formülündeki `-ec[j]` terimi kullanılmadı — gerekçe ve doğrulama sayıları için bkz. [[karar_c2_tight_big_m_uygulamasi]] (bu, planın atomik uygulama kaydıdır).

Doğrulama: modelde `|katsayı| >= 99999` olan terim sayısı 0 (öncesinde çoktu). R5 problem setinde Gurobi 13 ile OPTIMAL çözüm alındı (EV: obj=10116.10, CV: obj=10116.10).

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`
- `src/CV_model_gurobi_fixed.py`
- `src/EV_v_1_1_fixed.py`

## Related

- [[tight_big_m]]
- [[gurobi_mip_cozucusu]]
- [[karar_4b_to_3b_index_reduction_plani]]
- [[karar_3_fazli_uygulama_yol_haritasi]]
- [[karar_c2_tight_big_m_uygulamasi]]
- [[karar_a4_zaman_penceresi_bigm_kosullandirma]]
- [[sources/2026-08-09-full_path]]
