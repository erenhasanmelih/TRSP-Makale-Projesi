---
title: Karar (Planlı) — Şarj İstasyonları İçin Klon Düğüm Üretimi
tags: [karar, planlı, ev, şarj-istasyonu, matematiksel-model]
source: raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Karar (Planlı) — Şarj İstasyonları İçin Klon Düğüm Üretimi

## Karar

Matematiksel modelin şarj istasyonları için "klonlanmış" (dummy) düğümler üretmesi ve bunlara giriş-çıkış akışlarını tanımlaması gerekiyor — EV'ler rotanın ortasında bir şarj istasyonuna birden fazla kez uğrayabilmeli.

## Gerekçe

Kısmi şarj (partial recharging) esnekliğinin anlamlı olabilmesi için EV'nin aynı istasyona birden fazla kez dönebilmesi gerekiyor; mevcut modelde/kodda bu klonlama yapısı yok.

## Kardeş karar — DEPO klonlaması (2026-08-22)

Bu sayfa **şarj istasyonu** düğümlerinin klonlanmasıyla ilgilidir. Aynı
teknik, çoklu seferin zaman sırasını düzeltmek için **depo** düğümüne de
uygulanmalıdır: [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]].
İki tasarım birbiriyle çakışmaz (biri ara düğümleri, diğeri depo yaylarını
çoğullar) ve ortak bir klon altyapısıyla birlikte gerçekleştirilmelidir.

**GÜNCELLEME (2026-08-23):** depo klonlaması `raw/`'a **uygulandı**
(`raw/CV_model_gurobi_exact.py:88-152`, `raw/EV_v.1.1.py:98-156`) ve bu sayfanın
yeniden kullanabileceği bir kalıp bıraktı:

1. klon kimlikleri `max(N)+1`'den başlayan tamsayılar (`O`, `E` sözlükleri),
2. parametreler (`d`, `tt`, `st`, `ec`, `lc`, EV'de `tt_0i`/`tt_i0`) **yerel
   kopyaya** takma adla yazılır — çağıranın `data` sözlüğü değiştirilmez,
3. genişletilmiş yay kümesi `At`/`At_set` tüm `for (i,j) in A` döngülerinin
   yerini alır,
4. klon yayları enerji kısıtlarından `if i in clones or j in clones: continue`
   filtresiyle dışlanır.

**Önemli fark:** istasyon klonlaması depo klonlamasından daha zordur, çünkü
istasyon klonları hem giren hem çıkan yaya sahip olmalıdır (depoda `O`/`E`
ayrımı bu sorunu ortadan kaldırıyordu) ve `ye[s]`/`YE[s]`/`Delta_s[s,kk]`
değişkenlerinin de klon başına çoğullanması gerekir. Depo uygulamasında
istasyonlar `Cs` içinde bırakılmış, **klonlanmamıştır**.

## Sources

- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[klon_dugum_node_replication]]
- [[partial_recharging]]
- [[karar_partial_charging_denklemleri_entegrasyonu_plani]]
- [[sorun_sarj_yakit_istasyonlari_kodda_yok]]
- [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]]
