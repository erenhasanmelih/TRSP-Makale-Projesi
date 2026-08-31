---
title: Sorun — EV-17'nin Big-M Katsayısı (lc_0 + g_e·Q) Geçersiz Ölçüde Küçüktü, Fizibıl Çizelgeleri Kesiyordu
tags: [sorun, ev, cv, big-m, tight-big-m, v1.1, cozuldu]
source: raw/EV_v.1.1.py; raw/CV_model_gurobi_exact.py; raw/xml_data_loader.py
date: 2026-08-22
status: güncel
---

# Sorun — EV-17 Big-M Geçersizliği

## Bulgu

Matematiksel modelde EV-17 (ve CV-19) şöyle yazılıdır:

```
τ_ik + tt_ij·x_ijk + g_e·(YE_i − ye_i) − (lc_0 + g_e·Q_k)(1 − x_ijk) ≤ τ_jk
```

Big-M rolündeki `(lc_0 + g_e·Q_k)` katsayısının **geçerli** olması için, `x_ijk = 0`
iken kısıtın gerçekten gevşemesi gerekir; bunun için gereken alt sınır:

```
M ≥ max(τ_i) + g_e·Q_k − min(τ_j) = (ls_k − es_k) + g_e·Q_k
```

Mevcut veriyle: `ls − es = 32400 − 0 = 32400`, `g_e·Q = 0.163636 × 50000 = 8181.8`
→ **gereken M ≥ 40581.8**.

Kullanılan değer ise `lc_0 + g_e·Q`. Burada kritik asimetri şudur:

- **CV**: `raw/CV_model_gurobi_exact.py`'nin `__main__`'i `data['lc0'] = 40000.0`
  atıyor (satır 693) → `M = 46000 ≥ 38400` ⇒ **geçerli** (ama tesadüfen).
- **EV**: `raw/EV_v.1.1.py`'de böyle bir geçersiz kılma **yok**; `lc_0`,
  `xml_data_loader.prepare_ev_data_from_instance`'ın varsayılanı olan **10000**'de
  kalıyor → `M = 18181.8 < 40581.8` ⇒ **GEÇERSİZ**.

Geçersiz Big-M'in somut etkisi: `x_ijk = 0` olan (yani **seçilmemiş**) her `(i,j)`
çifti için bile kısıt `τ_i − τ_j ≤ 18181.8` biçimine dönüşüyor; yani aynı kaynağın
ziyaret ettiği herhangi iki düğüm arasında **sahte bir "5 saatten fazla ayrılamaz"
kuralı** doğuyor. Zorunlu öğle molası (EV-12) mola öncesi düğümü `≤ el = 14400`,
mola sonrası düğümü `≥ ll = 21600` yaptığından bir vardiya içindeki `τ` yayılımı bu
sınırı kolayca aşıyor ⇒ **fizibıl çizelgeler kesiliyordu.**

## Gurobi kanıtı

C5 örneğinde rota sabitlendi (`0→1→5→4→0` ve `0→2→3→0`) ve amaç
`min τ[1, kX]` (ilk müşteriye varış saati) olarak konuldu:

```
M_eski = 10000 + 0.163636*50000 = 18181.8
M_yeni = 32400 + 0.163636*50000 = 40581.8

[old_bigm ] status=2 (OPTIMAL) min tau[1,kX] = 3418.2 s
    tau[1]=3418.2  tau[5]=9630.4  tau[4]=21600.0  tau[0]=32400.0
[new_bigm ] status=2 (OPTIMAL) min tau[1,kX] =  133.7 s
    tau[1]=133.7   tau[5]=1822.7  tau[4]=26964.8  tau[0]=32400.0
```

Eski Big-M ile bulunan alt sınır **tam olarak** `21600 − 18181.8 = 3418.2` çıkıyor —
yani cebirsel tahminin birebir sayısal doğrulaması. Yeni Big-M ile ilk müşteriye varış
`133.7 s` (= `tt(0,1)`, EV-13'ün izin verdiği en erken saat) olabiliyor. Eski katsayı,
ilk müşteriye varışa **~57 dakikalık sahte bir gecikme** dayatıyordu.

## Düzeltme

Her iki modelde de Big-M `lc_0`'dan bağımsız, **ispatlanabilir geçerli** ve
mümkün olan en sıkı biçime çevrildi:

```python
bigM = max(lc0, ls[t_] - es[t_]) + g_e * Q[v_]      # EV_v.1.1.py:350
bigM = max(lc0, ls[t_] - es[t_]) + g_c * G[v_]      # CV_model_gurobi_exact.py:346
```

`max(...)` biçimi bilinçli seçildi: `lc_0`'ın zaten yeterince büyük olduğu durumlarda
(CV'de 40000 > 32400) **mevcut sayısal davranışı hiç değiştirmez**, yalnızca kısıtı
`lc_0` parametresinin keyfî ayarına karşı güvenli hâle getirir. CV tarafında bu
nedenle bir sonuç değişikliği beklenmez; EV tarafında ise geçerlilik ilk kez sağlanmış
olur.

## Etki kapsamı (dürüst sınır)

Küçük örneklerde (C5, RC5) **amaç değeri değişmedi** (C5: 8291.2 → 8291.2;
RC5: 7933.0 → 7933.0) — yani bu örneklerde geçersiz Big-M optimal *rotayı* kesmiyordu.
Kestiği şey **çizelge (τ) uzayıydı**: yukarıdaki testte ilk müşteriye varış saatinde
~57 dakikalık sahte bir alt sınır doğuyor. Daha uzun vardiya yayılımı gerektiren
(daha büyük / daha sıkı zaman pencereli) örneklerde bunun optimal rotayı da
kesebileceği, kısıtın geçersizliğinden doğrudan çıkar; bu yüzden düzeltme
"performans iyileştirmesi" değil **doğruluk düzeltmesi** olarak sınıflandırılmıştır.

## Not — diğer Big-M'ler kontrol edildi, geçerli

- EV-6 / CV-6: `a_max + ls_k + (ll_k − el_k)`; EV-15/CV-17 `τ_s + Δ_s ≤ ls` verdiğinden
  gereken alt sınır `ls − es`; geçerli.
- EV-7 / CV-8: `ls_k + (ll_k − el_k)`; geçerli.
- CV-14: `ls_k − ll_k`; üç durumun tamamında (x=0; x=1,Σw=0; x=1,Σw≥1) doğru davranıyor.
- EV-18/19, CV-20/21, CV-23/24: `Q_k` / `G_k`; `ye_j ≤ Q_k` kutu sınırı nedeniyle geçerli.

## Sources

- `raw/EV_v.1.1.py:336-358` (EV-17, düzeltilmiş Big-M + gerekçe yorumu)
- `raw/CV_model_gurobi_exact.py:329-351` (CV-19, aynı düzeltme)
- `raw/xml_data_loader.py:378` (`'lc_0': 10000.0` — EV varsayılanı)
- `raw/CV_model_gurobi_exact.py:693` (`data['lc0'] = 40000.0` — yalnızca CV'de var)

## Related

- [[karar_c2_tight_big_m_uygulamasi]]
- [[karar_tight_big_m_gecisi_plani]]
- [[sorun_ev_depo_yaylarinda_dongusel_infeasibility]]
- [[parametre_big_m_100000]]
