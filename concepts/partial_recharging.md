---
title: Partial Recharging / Partial Charging (Kısmi Şarj)
tags: [kavram, ev, enerji-modeli, matematiksel-model]
source: raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Partial Recharging / Partial Charging (Kısmi Şarj)

Elektrikli araçların (EV) bir şarj istasyonunda bataryayı tam doldurmak zorunda olmadığı, sadece bir sonraki müşteriye veya depoya yetecek kadar şarj olabildiği modelleme yaklaşımı. Literatür kaynağı: Keskin ve Çatay (2016)'nın doğrusal kısmi şarj denklemleri.

## Matematiksel modelde tanım

Model, şarj hızı katsayısı, maksimum şarj süresi ve dolum miktarının zaman ilerlemesine etkisini Kısıt (17) ve Kısıt (19) aracılığıyla hesaplıyor.

## Kod tarafındaki durum

Yönerge belgeleri "kodda dolum süresi hesabı yok" diyor, ama Stage 2 kod incelemesi (2026-08-09) bunu kısmen düzeltti: `EV_v.1.1.py`'de `c8_zaman_ilerleme` kısıtına eklenen `charge_time_i = g_e * (YE[i] - ye[i]) if i in S_set else 0.0` terimi (satır 165, 271), istasyonda geçirilen kısmi şarj süresini zaman ilerlemesine dahil ediyor — yani `YE[i]-ye[i]` (şarj edilen miktar, tam doldurmak zorunda değil) × `g_e` (şarj hızı katsayısı) ile hesaplanan bir süre modelleniyor. Bu, Keskin & Çatay (2016)'nın tam formülasyonuyla birebir aynı olmayabilir (doğrulanmadı) ama "hiç yok" iddiası artık geçerli değil — bkz. [[sorun_kismi_sarj_dinamikleri_kodda_yok]] (güncellendi).

## İlişkili eksiklik: Klon Düğüm

Partial charging'in tam çalışabilmesi için EV'lerin bir istasyona rota ortasında birden fazla kez uğrayabilmesi gerekir; bu da şarj istasyonları için "klonlanmış" (dummy) düğümler ve bunların giriş-çıkış akışlarının modele eklenmesini gerektirir (bkz. [[klon_dugum_node_replication]]).

## Uygulama (Faz 2, 2026-08-11) — kısmen ilerledi

Faz 2, kısmi şarjın **etkisiz kalmasına** neden olan bir hatayı düzeltti (A1): `c20` istasyon çıkış yaylarında da yazılıyordu ve `YE[s]>=ye[s]` olduğundan `c21`'i (gerçek şarj sonrası enerji) her zaman eziyordu — yani `charge_time_i` matematiksel olarak tanımlı olsa da gerçek şarj akışa hiç yansımıyordu. `src/EV_v_1_1_fixed.py:482-483` (`if i in S_set: continue`) düzeltmesiyle şarj artık gerçekten çalışıyor; R5'te öncesi 0 çözüm, sonrası 8 çözüm (obj=10118.32). Detay: [[karar_a1_ev_sarj_c20_c21_duzeltmesi]].

**Keskin & Çatay (2016)'nin tam eşitlik denklemleri hâlâ entegre edilmedi** — `ye`/`YE` arası hâlâ sadece tek-yönlü `<=` eşitsizlik, bu da raporlanan şarj miktarının şişmesine yol açabiliyor (bkz. [[sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi]]). Plan sayfası [[karar_partial_charging_denklemleri_entegrasyonu_plani]] artık "KISMEN uygulandı" olarak güncellendi.

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`
- `src/EV_v_1_1_fixed.py:472-531`

## Related

- [[klon_dugum_node_replication]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
- [[karar_partial_charging_denklemleri_entegrasyonu_plani]]
- [[sorun_ev_enerji_tuketim_modeli_basitlestirilmis]]
- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
- [[sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi]]
