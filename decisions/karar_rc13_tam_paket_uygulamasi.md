---
title: Karar (UYGULANDI) — Ö3+Ö4+Ö7a+Ö7b+Ö8 raw/'a İşlendi (RC15/RC20 Hızlandırma Paketi)
tags: [karar, uygulandi, rc13, rc15, rc20, min-veh, bwp, tight-big-m, sarj-mola-duzeltmesi, mip-formulasyon, cv, ev, gurobi]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-29
status: güncel
---

# Karar (UYGULANDI) — Ö3+Ö4+Ö7a+Ö7b+Ö8 Tam Paket

> **GÜNCELLEME (2026-08-31): Bu sayfadaki RC13/RC15 rakamları GEÇERSİZ
> KALDI.** [[karar_5_8_teknisyen_bug_fix]] `raw/`'a uygulandıktan sonra
> aynı örnekler yeniden koşuldu: RC13 EV **19938.07** (önceden 20666.99,
> **%3,5 daha iyi**, 12.87 s), RC15 EV **21851.58** (önceden 23912.82,
> **%8,6 daha iyi**, 32.15 s), RC13 CV incumbent **19938.07** ama 300 s'de
> henüz kanıtlanmadı (%8,7 gap; önceden 36.95 s'de kanıtlanmıştı). Sebep:
> bu sayfadaki koşumlar `skill_tech_map[skill][0]` hatasıyla (8
> teknisyenin yalnızca 5'i aktif) yapılmıştı — o hâlde bulunan "optimal"
> değerler eksik bir girdi kümesine göre doğruydu, gerçek (8 teknisyenli)
> problem için değildi. Aşağıdaki §1/§8 tabloları CLAUDE.md Hard Rule
> §7.4 gereği **silinmedi** (bug fix öncesi `raw/` durumunun doğru bir
> kaydı), ama artık makalede/raporda kullanılacak güncel sayılar değil.
>
> **Durum: UYGULANDI (2026-08-29).** [[karar_rc13_asgari_paket_uygulamasi]]'nın
> (Ö1+Ö2+Ö6) üstüne, [[sorun_rc13_darbogaz_kok_neden_analizi]] §6'da kenara
> ayrılmış **Ö3 (min_veh), Ö4 (bwp+arc_fix), Ö7a (tight_m), Ö7b (ölü kısıt
> temizliği)** ve Eren'in sorusu üzerine bulunan **Ö8 (EV mola/şarj
> çakışması düzeltmesi)** doğrudan `raw/CV_model_gurobi_exact.py` ve
> `raw/EV_v.1.1.py`'ye işlendi. **Ö5 (statik DFJ) Eren'in talimatıyla
> RAFA KALDIRILDI, uygulanmadı.**

## 1. Sonuç önce — RC13 saniyelere indi, RC15 de kanıtlanmış optimale ulaştı

| Örnek | Model | Önceki (Ö1+Ö2+Ö6) | Şimdi (+ Ö3+Ö4+Ö7a+Ö7b+Ö8) |
|---|---|---|---|
| RC13 | EV | 67.4 s, optimal | **5.96 s, optimal** (%0.00 gap, 20666.99) |
| RC13 | CV | 106.4 s, optimal | **36.95 s, optimal** (20666.99) |
| RC15 | EV | 180 s'de %8.05 gap (kanıtlanamadı) | **11.35 s, optimal** (23912.82) |
| RC20 | EV | 180 s'de 0 çözüm | 300 s'de **hâlâ 0 çözüm** (alt sınır 24099.9'a yükseliyor — bkz. §5) |
| RC20 | CV | — | 180 s'de 0 çözüm |
| C5/R5/RC5 | CV+EV | optimal (~0s) | değişmedi |
| R10/RC10 | CV+EV | <1s optimal | değişmedi (aynı objektif, aynı düğüm mertebesi) |

Tüm koşumlar `raw/solution_validator.validate_solution()` ile doğrulandı
(hepsi `valid=True`). Heterojen filo (Ö2) ve heterojen vardiya penceresi
(Ö3/Ö4'ün güvenlik kontrolü) elle simüle edilerek ayrıca test edildi —
ikisi de doğru şekilde eski/güvenli davranışa geri dönüyor (bkz. §6).

## 2. Ö3 — `min_veh` geçerli eşitsizliği (YALNIZCA EV)

```python
Σ_r Σ_kk u[r,kk] >= ceil(ogleden_sonra_yuku / (ls-ll))
```

`ogleden_sonra_yuku` = `ec_i+st_i > el` olan müşterilerin toplam `st_i`
toplamı (moladan önce bitiremeyen, transitivite ile `τ_i>=ll`'ye zorunlu
itilen müşteriler). `u[r,kk]` üzerine yazıldı (**`z_veh` üzerine değil** —
kritik, aksi hâlde EV-4c yüzünden etkisiz kalırdı, bkz. teşhis sayfası §6).

**CV'ye BİLEREK taşınmadı.** CV'nin molası (CV-13) opsiyonel olduğundan bir
CV kaynağı molayı hiç kullanmayarak bu zorlama zincirini önleyebilir —
argüman CV'de kurulamaz (ayrıntı: kodun içindeki not,
`CV_model_gurobi_exact.py` CV-4 bloğunun hemen altı).

**Güvenlik kontrolü:** yalnızca `es/ls/el/ll` TÜM ekipler için aynıysa
etkinleşir (`_bwp_active` bayrağı) — heterojen vardiya penceresinde
otomatik ve güvenli biçimde devre dışı kalır (§6'da test edildi).

## 3. Ö4 — Mola penceresi yayılımı (`bwp`, YALNIZCA EV) + `arc_fix` (HER İKİSİ)

**bwp** (`ec_i+st_i>el ⇒ ec_i:=ll`; `lc_i<ll ⇒ lc_i:=el-st_i`) — yalnızca
EV'de uygulandı, CV'YE TAŞINMADI (aynı gerekçe: CV'nin molası opsiyonel).

**arc_fix** (`ec_i+st_i+tt_ij > lc_j` olan yayları `At`'ten tamamen çıkar)
— **HER İKİ modelde** uygulandı; mola varsayımından bağımsız, tamamen
güvenli bir zaman-tutarlılığı budaması. EV'de `bwp`'nin dar pencerelerini,
CV'de ham pencereleri kullanır.

Etkisi: RC13 EV `NumVars` 5745→**5385**, `NumConstrs` 20044→**14453**
(arc_fix'in `At` küçültmesi + Ö7b'nin ölü kısıt temizliği birlikte).

## 4. Ö7a — Düğüm-bazlı sıkı Big-M (tight_m)

EV-6/EV-7/EV-17/EV-30 ve CV-8/CV-19/CV-31'deki **global** (gün-geneli sabit)
Big-M'ler, düğüm-bazlı `max(0, τ_ub(i)−τ_lb(j))` formülüyle değiştirildi
(`τ_ub/τ_lb` = ilgili düğümün kendi `[ec,lc]` penceresi — bkz.
[[tight_big_m]]).

**Ek bir gözlem (uygulama sırasında bulundu):** `w[i,j,kk] <= x[i,j,kk]`
(EV-8/CV-9) HER (i,j,kk) için geçerli olduğundan, `x=0` iken `w` de otomatik
`0`'dır — yani LHS'teki `w*(ll-el)` mola terimi Big-M'e **eklenmesi
gerekmez** (orijinal CV-31 yorumundaki gözlemle aynı, EV-6/7/17/30'a da
genelleştirildi). Şarj terimi (`g_e*(YE-ye)`) ise `x`'ten bağımsız olduğu
için Big-M'de KALMAK ZORUNDA — bu ayrım gözden kaçırılırsa
[[sorun_rc13_darbogaz_kok_neden_analizi]]'nde bahsi geçen
`sorun_ev17_big_m_gecersiz_kucuk` hatası tekrarlanabilirdi.

CV-19'da fazladan bir sadeleştirme: `g_c*(YC[i]-yc[i])` terimi CV-22
(`YC[i]==yc[i]`, TÜM `Cs` için, istisnasız) nedeniyle HER fizibıl çözümde
kanıtlanabilir biçimde `0`'dır (CV'de gerçek istasyon hiç yok), dolayısıyla
Big-M'den `g_c*G_k` terimi de düşürüldü.

## 5. Ö7b — Ölü kısıt temizliği

`ye[j]>=0.0` (EV18_lb/EV19_lb) ve `yc[j]>=0` (CV20_lb/CV21_lb) kaldırıldı —
`ye`/`yc` zaten `lb=0.0` ile tanımlı, bu satırlar hiçbir şey yapmıyordu.
RC13'te ~24480 gereksiz kısıttı; solve davranışını değiştirmez, yalnızca
model kurma/`.lp` yazma süresini kısaltır.

## 6. Ö8 — EV mola/şarj çakışması düzeltmesi (Eren'in sorusu üzerine)

**Sorun:** `Delta_s[s,kk]` (istasyon-kaynak bazlı "şarj süresi") hiçbir
kısıtta gerçek şarj miktarına (`YE-ye`) bağlanmamıştı — yalnızca
EV-6/10/15'i sıkılaştıran (asla gevşetmeyen) bir terimdi, optimizasyon onu
her zaman `0`'a çekiyordu (fiilen ölü, [[sorun_rc13_darbogaz_kok_neden_analizi]]
§7.2). Gerçek şarj-süresi mekanizması zaten EV-17'de vardı
(`g_e*(YE[i]-ye[i])`) ama EV-17'nin kendisinde mola terimi HİÇ yoktu.
Sonuç: bir kaynak istasyonda şarj olduktan HEMEN SONRA molaya girerse
(veya tersi), ne EV-6 (mola-farkında, şarj-farkında değil) ne EV-17
(şarj-farkında, mola-farkında değil) ikisini BİRLİKTE zorunlu kılıyordu —
teorik bir fizibilite gevşekliği.

**Düzeltme:**
- `Delta_s` KALDIRILDI (ve onunla birlikte `_rename` çağrısı).
- EV-6/EV-10/EV-15'te `Delta_s[s,kk]` yerine gerçek terim
  `g_e*(YE[s]-ye[s])` kullanıldı.
- EV-17'ye eksik olan `w[i,j,kk]*(ll[t_]-el[t_])` mola terimi eklendi
  (müşteri düğümlerinde zararsız: EV-27 nedeniyle şarj terimi zaten `0`,
  EV-7 zaten aynı mola terimini içeriyor — EV-17 orada fazladan ama geçerli
  bir kısıt olarak kalıyor).
- `alpha_s/rho_s/o_s/q_s` DOKUNULMADI — bunlar dürüst "gelecek çalışma"
  yer tutucuları (parçalı-doğrusal şarj eğrisi), Eren'in sorduğu
  "gariplik" bunlar değil.
- CV'nin `Delta_c`'sine DOKUNULMADI — CV'de gerçek istasyon hiç yok
  (`Fc=[0]` sabit), bu zaten ayrı ve önceden belgelenmiş bir konu
  ([[sorun_cv_kullanilmayan_istasyon_parametreleri]]).

**Şu anki pratik etkisi: SIFIR.** [[karar_rc13_asgari_paket_uygulamasi]]'nın
uyguladığı Ö6 (istasyon düşürme) mevcut 30 örneğin TAMAMINDA `S=[]`
üretiyor, yani EV-6/10/15/17'nin istasyon-ilgili kısımları zaten hiç
çalışmıyor. Düzeltme yalnızca istasyonlar bir gün geri gelirse (farklı/daha
uzak bir veri seti) devreye girecek — ileriye dönük bir doğruluk
düzeltmesidir, bugünkü hız sonuçlarına katkısı yoktur.

## 7. Ö5 (statik DFJ) — RAFA KALDIRILDI

Eren'in açık talimatıyla uygulanmadı. Gerekçe (teşhis sayfası §4.3):
diğer indirimlerle (Ö1/Ö2/Ö6) birlikteyken **net zararlı** ölçülmüştü
(2.7s→10.7s, RC13 EV ablasyonunda). Bu kararın kodda hiçbir karşılığı yok.

## 8. Doğrulama

`raw/` modülleri doğrudan import edilip test edildi (`raw/`'un `__main__`'ı
interaktif `input()` içerdiğinden çalıştırılmadı) —
`%TEMP%\...\scratchpad\test_helpers.py`, `raw/` dışında.

| Test | Sonuç |
|---|---|
| C5/R5/RC5 × {CV,EV} | Hepsi optimal, önceki değerlerle birebir aynı |
| R10/RC10 × {CV,EV} | Hepsi optimal (<1s), önceki değerlerle birebir aynı |
| RC13 × {CV,EV} | Optimal, 20666.99 (önceki turla birebir aynı objektif) |
| RC15 EV | Optimal, 23912.82 (yeni — önceden kanıtlanmamıştı) |
| RC20 × {CV,EV} | 0 çözüm (300s/180s) — bkz. §1 tablosu, sınır aşılamadı |
| Heterojen filo (Ö2 fallback, C5'te elle simüle) | Doğru çalışıyor, aynı optimal |
| Heterojen vardiya penceresi (Ö3/Ö4 fallback, RC13'te elle simüle) | `_bwp_active=False`'a düşüyor, optimal (20666.99) korunuyor |

Tüm koşumlarda `solution_validator.validate_solution()` → `valid=True`.

## 9. Sınırlamalar

- **RC20 hâlâ çözülemiyor** (300s'de 0 çözüm, EV+CV). Alt sınır düzenli
  yükseliyor (24099.9'a kadar) ama Gurobi'nin varsayılan sezgiselleri bu
  ölçekte İLK fizibıl çözümü bile bulamıyor. `NoRelHeurTime`/`MIPFocus=1`
  gibi parametre ayarları da tek başına yeterli olmadı (test edildi).
  Muhtemel sonraki adımlar: Ö5'in lazy-callback biçimi, warm-start
  (heuristic'ten ilk çözüm), veya yalnızca parametre taraması.

  > **ÇÜRÜTÜLDÜ (2026-08-31)** — bkz. §9.1 aşağıda.

### 9.1 ÇELİŞKİ (çözüldü) — yukarıdaki RC20 teşhisi YANLIŞTI

**İddia A (bu sayfa, 2026-08-29, yukarıdaki madde):** RC20 bir *arama gücü*
sorunudur; lazy-callback / warm-start / parametre taraması ile aşılabilir.

**İddia B ([[sorun_rc20_darbogaz_kok_neden_analizi]], 2026-08-31):** RC20
**hem EV hem CV için INFEASIBLE'dır**. Değiştirilmemiş `raw/` modeline tek
bir *geçerli* eşitsizlik (`Σ st_i·x[i,j,kk] ≤ 25200·z_veh[kk]`) eklendiğinde
Gurobi infeasibility'yi EV'de 2.5 s, CV'de 8.0 s'de **kanıtlıyor**; aynı
eşitsizlik RC13/RC15/R15/C15'te bilinen optimalleri (20 666.99 / 23 912.82)
**değiştirmiyor** → eşitsizlik geçerli, infeasibility modelin kendisine ait.
Kök neden: `skill_tech_map[skill][0]` (5/8 teknisyen) + EV-22/CV-27
(`Σz ≤ |V| = 3`) + EV-23/CV-28 → zorunlu `{2,2,1}` beceri bölünmesi; 15
bölünmenin 15'i de aktif kaynak başına 25 200 s'lik günlük hizmet
kapasitesini aşıyor (en iyisi **+791 s**).

**Karar: İddia A ÇÜRÜTÜLDÜ.** Gözlemi (0 çözüm) doğru, yorumu yanlıştı;
önerdiği üç yol da boşa yatırım olurdu. Bu bölüm CLAUDE.md Hard Rule §7.4
gereği **silinmedi**, her iki taraf da kaynağıyla korunuyor. Aynı düzeltme
`log.md`'nin 2026-08-29 girdisi için de geçerlidir.

- **n ≥ 20 olan TÜM örnekler** (C/R/RC × 20/40/60/80/100 = 15 örnek) aynı
  argümanla infeasible'dır; mevcut `raw/` konfigürasyonunda exact modelin
  çözebileceği en büyük boyut **n = 15**'tir
  ([[sorun_rc20_darbogaz_kok_neden_analizi]] §4.3).
- Ö8'in pratik etkisi mevcut veri setinde SIFIR (§6) — yalnızca istasyonlu
  senaryolar için doğruluk garantisi.
- Test scripti `raw/`'un `__main__`'ındaki `NoRelHeurTime=600`/`MIPFocus=2`
  parametrelerini KULLANMADI (sade `MIPGap=1e-4`/`Seed=1`); gerçek
  `__main__` koşumunda süre farklı çıkabilir.

## Sources

- `raw/CV_model_gurobi_exact.py` — arc_fix bloğu, CV-8/19/31 tight-M, CV20/21_lb kaldırma
- `raw/EV_v.1.1.py` — bwp+arc_fix+Ö3 hesaplama bloğu, EV-6/7/17/30 tight-M,
  Delta_s kaldırma + EV-6/10/15/17 gerçek şarj terimi, EV18/19_lb kaldırma
- Test: `%TEMP%\...\scratchpad\test_helpers.py` (raw/ dışında)

## Related

- [[sorun_rc20_darbogaz_kok_neden_analizi]] (**§1 ve §9'daki RC20 teşhisini ÇÜRÜTÜR**: RC20 "çözülemiyor" değil, EV+CV **infeasible**'dır — bkz. aşağıdaki ÇELİŞKİ)
- [[sorun_rc13_darbogaz_kok_neden_analizi]] (bu kararın uyguladığı Ö3/Ö4/Ö7 önerileri)
- [[karar_rc13_asgari_paket_uygulamasi]] (bu kararın üstüne inşa edildiği Ö1+Ö2+Ö6 temeli)
- [[tight_big_m]] (Ö7a'nın kavramsal temeli)
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]] (Ö8'in düzelttiği EV şarj mekanizması)
- [[celiski_ogle_molasi_zorunlulugu]] (Ö3/Ö4'ün CV'ye taşınamama gerekçesinin kök nedeni: CV-13 opsiyonel/EV-12 zorunlu ayrımı)
- [[sorun_cv_kullanilmayan_istasyon_parametreleri]] (Ö8'in CV'ye neden taşınmadığı)
- [[degisken_yakit_enerji_izleme]]
