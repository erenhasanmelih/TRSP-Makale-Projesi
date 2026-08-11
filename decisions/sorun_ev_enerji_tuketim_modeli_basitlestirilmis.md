---
title: Sorun — EV Enerji Tüketim Modeli Aşırı Basitleştirilmiş
tags: [sorun, ev, enerji-modeli, doğrusal-olmama]
source: raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Sorun — EV Enerji Tüketim Modeli Aşırı Basitleştirilmiş

## Sorun

Kodda `yc`/`YC` (CV) ve `ye`/`YE` (EV) ile yakıt/enerji kapasitesi izleniyor, ancak elektrikli araçlarda enerji tüketimi gerçekte sadece mesafeye değil, **taşınan yüke ve hıza da bağlı doğrusal olmayan** bir yapıdadır. Mevcut kod bu tüketimi `h_e * mesafe` şeklinde tamamen doğrusal ve sadece mesafeye bağlı modelliyor.

Bu, "makale adımlar ve düzenlemeler.docx" belgesinde EV modelinin (o belgeye göre) mevcut haliyle "çalışamaz durumda" olarak nitelendirilmesinin gerekçelerinden biri; [[sorun_kismi_sarj_dinamikleri_kodda_yok]] ve [[klon_dugum_node_replication]] ile birlikte üç ana EV eksikliğinden biri.

## Açık konu / Stage 2 doğrulaması (2026-08-09)

"EV kodu çalışamaz durumda" ifadesi mevcut `EV_v.1.1.py` için abartılı görünüyor: dosya çalışır bir Gurobi modeli kuruyor, istasyon kısıtları (`S_set`) ve kısmi şarj süresi mekanizması (`charge_time_i`, bkz. [[sorun_kismi_sarj_dinamikleri_kodda_yok]]) mevcut. Ancak enerji tüketiminin (`h_e * mesafe`) hâlâ tamamen doğrusal ve yüke/hıza duyarsız olduğu doğrulandı (`EV_v.1.1.py:314,325,362`) — bu spesifik eksiklik gerçek. Muhtemelen docx'teki "çalışamaz durumda" ifadesi, dosyanın v1.1 öncesi bir sürümünü ya da genel bir uyarıyı yansıtıyor; abartılı ama temelsiz değil.

## Uygulama (Faz 2, 2026-08-11) — kısmen ilgili, EV değil CV tarafında

Bu sayfanın ana iddiası (EV enerji tüketiminin yüke/hıza duyarsız, sadece mesafeye doğrusal bağlı `h_e * mesafe` olması) **Faz 2'de değişmedi** — EV tarafında hâlâ aynı doğrusal model geçerli (`src/EV_v_1_1_fixed.py`, `he_of_k[k] * d[i,j]` terimi, bkz. [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]). Faz 2'nin dokunduğu şey EV'nin `h_e` katsayısının kendisi değil, **CV'nin paralel eksikliği** oldu: `CV_model_gurobi_exact.py`'de `h_c=1.0` sabitti, `EnergyConsumptionRate` hiç XML'den okunmuyordu (A7) — bu da CV menzilini gerçekçi olmayan biçimde büyütüyordu (6000/1.0=6000m). `src/xml_data_loader_fixed.py:249-269,289` düzeltmesiyle CV artık `EnergyConsumptionRate="0.055"`'i XML'den okuyor (menzil 6000/0.055=109091m, EV'nin 322580m'siyle artık aynı mertebede). Ayrıca hem CV hem EV için araç-bazlı `h_c_v`/`h_e_v` sözlükleri eklendi (heterojen filo desteği). Detay: [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]].

Yani bu sayfadaki "EV modeli basitleştirilmiş" iddiası hâlâ geçerli ve **çözülmedi**; ilgili ama farklı bir sorun (CV'nin eksik/sabit tüketim oranı) Faz 2'de giderildi.

## Sources

- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`
- `raw/EV_v.1.1.py:306-327,362` (doğrusal tüketim, h_e * mesafe)
- `src/xml_data_loader_fixed.py:249-269,289` (CV h_c XML'den okuma — A7, EV'nin doğrusal modeliyle ilgisiz ama paralel eksiklik)

## Related

- [[partial_recharging]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
- [[klon_dugum_node_replication]]
- [[sources/2026-08-09-makale_adimlar_ve_duzenlemeler]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
