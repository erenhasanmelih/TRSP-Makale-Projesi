---
title: Klon Düğüm / Node Replication (Şarj İstasyonu Çoğullama)
tags: [kavram, ev, matematiksel-model, şarj-istasyonu]
source: raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Klon Düğüm / Node Replication (Şarj İstasyonu Çoğullama)

EV'lerin bir rotanın ortasında aynı şarj istasyonuna birden fazla kez uğrayabilmesini modelleyebilmek için, her fiziksel istasyon düğümünün matematiksel modelde birden fazla "klonlanmış" (dummy) düğüm olarak temsil edilmesi tekniği. Her klon için ayrı giriş-çıkış akış kısıtları tanımlanır.

## TRSP projesindeki durum

`makale adımlar ve düzenlemeler.docx` belgesinde, mevcut EV modelinin bu yapıyı içermediği ve bunun EV modelini makale standardına göre eksik kıldığı belirtiliyor. [[partial_recharging]] ile doğrudan ilişkili: kısmi şarjın anlamlı olabilmesi için aracın aynı istasyona tekrar uğrayabilmesi gerekir.

## İkinci uygulama alanı — DEPO düğümü (2026-08-22)

Aynı teknik, `raw/`'da bulunan ikinci bir yapısal soruna da uygulanabilir:
çoklu sefer (CV-4/EV-4) yapan bir kaynağın depo zaman değişkeni `tau[0,kk]`
tek bir skaler olduğu için seferler zaman olarak çakışabiliyor
([[sorun_coklu_sefer_zaman_sirasi_ihlali]]). Çözüm, depoyu **sefer indisli
çıkış (`o_r`) ve dönüş (`e_r`) klonlarıyla** çoğullamaktır — bkz.
[[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]].

**DURUM (2026-08-23): depo klonlaması UYGULANDI.** Teknik artık `raw/`'da
canlıdır — `raw/CV_model_gurobi_exact.py:88-149` ve `raw/EV_v.1.1.py:98-159`
klon kümelerini (`O`, `E`), genişletilmiş yay kümesini (`At`) ve parametre
takma adlarını (`d`, `tt`, `st`, `ec`, `lc`, EV'de ayrıca `tt_0i`/`tt_i0`)
kuruyor. **Şarj istasyonu klonlaması hâlâ uygulanmadı**
([[karar_klon_dugum_sarj_istasyonu_plani]]), ancak depo uygulaması ona
doğrudan yeniden kullanılabilir bir kalıp bırakıyor: klon kimliği
`max(N)+1`'den başlayan tamsayılar, parametreler yerel kopyaya takma adla
yazılıyor (çağıranın `data` sözlüğü değiştirilmiyor), ve klon yayları
enerji kısıtlarından `if i in clones or j in clones: continue` filtresiyle
dışlanıyor.

Ortak yapı: her iki durumda da bir fiziksel düğümün **birden fazla kez
ziyaret edilmesi** gerekiyor, ama düğüm-indeksli zaman/enerji değişkenleri
(`tau[i,kk]`, `ye[i]`) yalnızca tek bir ziyareti temsil edebiliyor. Klonlama,
her ziyarete kendi değişken kopyasını verir. İkisi ortak bir klon
altyapısıyla (`clone_of[i]` haritası + parametre takma adları) birlikte
gerçekleştirilmelidir.

## Sources

- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`
- `raw/CV_model_gurobi_exact.py:411-427` (depo klonlamasının gerekçesi, kodun kendi notu)

## Related

- [[sorun_rc13_darbogaz_kok_neden_analizi]] (istasyon düğümleri RC13'te DFJ kesitlerinin göremediği bir "kaçış yolu" açıyor — Ö6)
- [[partial_recharging]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
- [[karar_klon_dugum_sarj_istasyonu_plani]]
- [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]]
- [[sorun_coklu_sefer_zaman_sirasi_ihlali]]
