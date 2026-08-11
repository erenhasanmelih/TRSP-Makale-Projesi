---
title: Sorun (Faz 2, Kalan İş) — ye/YE Eşitsizlik Kısmi Şarj Raporlama Hatası
tags: [sorun, faz2, ev, şarj-modeli, raporlama, kalan-iş]
source: src/EV_v_1_1_fixed.py
date: 2026-08-11
status: güncel
---

# Sorun (Faz 2, Kalan İş) — ye/YE Eşitsizlik Kısmi Şarj Raporlama Hatası

## Sorun

Faz 2'de A1 düzeltildi (bkz. [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]) — şarj artık gerçekten akışa yansıyor. Ama `ye[i,k]` (varıştaki enerji) ile `YE[i,k]` (ayrılıştaki enerji, dolum sonrası) arasındaki bağıntı hâlâ yalnızca **tek-yönlü `<=` eşitsizliklerle** kurulu (`c20_ub`, `c21_ub` — `src/EV_v_1_1_fixed.py:484-498`), **eşitlik yok**.

Bunun sonucu: Gurobi'nin çözücüsü, fizibiliteyi bozmadan `ye`'yi gerçek State-of-Charge'ın **altında** bir değer olarak seçebiliyor (eşitsizlik gevşek kaldığı sürece kısıt ihlal edilmiyor). Bu durumda `print_ev_solution` fonksiyonunun raporladığı şarj miktarı (`YE[i]-ye[i]`) gerçek ihtiyaçtan büyük görünüyor — **şişiyor**.

## Doğrulama

Test çalıştırmasında gerçek şarj ihtiyacı yaklaşık **250** birim iken, raporlanan değer **851** birim olarak çıktı.

## Neden önemli

- **Fizibiliteyi bozmuyor** — modelin optimal çözümü hâlâ geçerli, `obj` değeri etkilenmiyor.
- **Raporlama güvenilirliğini** doğrudan etkiliyor — makalede/analizde "EV modeli X birim enerji şarj etti" gibi bir sayı verilecekse, bu sayı şu an güvenilir değil.

## Kanıt

Bu bulgu, [[karar_partial_charging_denklemleri_entegrasyonu_plani]]'nın (Keskin & Çatay 2016 tam eşitlik denklemleri) **hâlâ tamamlanmadığının** somut kanıtıdır — o sayfa "KISMEN uygulandı" olarak güncellendi ve bu sorun oraya çapraz-referans verildi.

## Önerilen çözüm (henüz uygulanmadı)

`ye`/`YE` arasına Keskin & Çatay'ın tam doğrusal kısmi şarj formülasyonu (şarj hızı katsayısı × süre eşitliği, `YE[i,k] = ye[i,k] + g_e * charge_duration[i,k]`) eklenip mevcut `<=` eşitsizlikleri `==` eşitliğe dönüştürülmeli. Bu, [[karar_partial_charging_denklemleri_entegrasyonu_plani]]'nın kapsamına giriyor.

## Sources

- `src/EV_v_1_1_fixed.py:484-498` (c20_ub, c21_ub — tek yönlü eşitsizlikler)
- test çalıştırması (Faz 2 doğrulama notları, R5 problem seti)

## Related

- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
- [[karar_partial_charging_denklemleri_entegrasyonu_plani]]
- [[partial_recharging]]
- [[degisken_yakit_enerji_izleme]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
