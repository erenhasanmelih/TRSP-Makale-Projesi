---
title: Karar (Planlı) — Partial Charging Denklemlerinin Entegrasyonu
tags: [karar, planlı, ev, şarj-modeli]
source: raw/Yönergelerimiz/Full Path.docx
date: 2026-08-09
status: güncel
---

# Karar (Planlı) — Partial Charging Denklemlerinin Entegrasyonu

## Karar

Keskin ve Çatay (2016)'nın doğrusal kısmi şarj denklemleri, EV modeline (`EV_v.1.1.py`) düzgünce yedirilecek.

## Gerekçe

Mevcut EV kodu enerji seviyesini yalnızca tüketim katsayısı × mesafe ile azaltıyor, şarj süresi/hızı dinamiklerini hesaba katmıyor (bkz. [[sorun_kismi_sarj_dinamikleri_kodda_yok]]). Bu, EV modelini gerçekçi olmayan/eksik kılıyor.

## Kapsam / Faz

Full Path.docx'te Adım 1 (Matematiksel Modelin Yeniden İnşası) kapsamında listelenmiş; hangi fazda (Faz 1 kod revizyonu sadece CV modeli için tanımlanmış) uygulanacağı net değil — [[ÇELİŞKİ]] adayı olmasa da açık bir plan boşluğu.

## Uygulama (Faz 2, 2026-08-11) — KISMEN uygulandı

**Durum: KISMEN.** Faz 2, bu planın hedeflediği "şarj süresi/hızı dinamiklerinin hesaba katılmaması" sorununun **etkisiz kalan** bir alt-parçasını düzeltti (A1): `EV_v.1.1.py`'nin türetilen `src/EV_v_1_1_fixed.py` kopyasında, istasyon çıkış yaylarında da yazılan `c20` kısıtı, `YE[s]>=ye[s]` olduğundan `c21`'i (gerçek şarj sonrası enerji) her zaman eziyordu — yani şarj matematiksel olarak modellenmiş olsa da akışa hiç yansımıyordu. Düzeltme: `c20` döngüsünde `if i in S_set: continue` (`src/EV_v_1_1_fixed.py:482-483`). Doğrulama: R5'te öncesi 0 çözüm (TIME_LIMIT), sonrası 8 çözüm bulundu (obj=10118.32), istasyon SoC örneği 751.54→1000.00, `c20_ub` istasyon çıkışında artık 0 adet. Detay: [[karar_a1_ev_sarj_c20_c21_duzeltmesi]].

**Kalan iş — asıl plan hâlâ tamamlanmadı:** Keskin & Çatay (2016)'nın tam eşitlik denklemleri hâlâ entegre edilmedi. `ye[j,k]`/`YE[i,k]` arasındaki bağıntı hâlâ yalnızca tek-yönlü `<=` eşitsizliklerle kurulu (`c20_ub`, `c21_ub` — `src/EV_v_1_1_fixed.py:484-498`), eşitlik yok. Bu, A1 düzeltmesinden sonra yeni ve somut bir yan etki doğurdu: çözücü `ye`'yi gerçek SoC'nin altında seçebiliyor, bu da `print_ev_solution`'ın raporladığı şarj miktarının şişmesine yol açıyor (test: gerçek ihtiyaç ~250 iken 851 raporlandı). Fizibiliteyi bozmuyor ama raporlama güvenilirliğini etkiliyor — bkz. yeni sorun sayfası [[sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi]]. Bu planın "tamamlandı" sayılabilmesi için Keskin & Çatay'ın tam doğrusal kısmi şarj formülasyonunun (şarj hızı × süre eşitliği) `ye`/`YE` çiftine eklenmesi gerekiyor.

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `src/EV_v_1_1_fixed.py:472-531`

## Related

- [[partial_recharging]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
- [[karar_klon_dugum_sarj_istasyonu_plani]]
- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
- [[sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi]]
