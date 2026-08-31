---
title: Sorun — Emoji İçeren Operasyon Raporu cp1254 Konsolda UnicodeEncodeError ile Çöküyordu (Rapor Dosyası Yarım Kalıyor)
tags: [sorun, raporlama, cokme, cv, ev, windows, cozuldu]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-22
status: güncel
---

# Sorun — `log_print` Unicode Çökmesi

## Bulgu

`print_cv_solution` / `print_ev_solution` içindeki `log_print()` yardımcısı, metni
hem `print()` ile konsola hem de `f.write()` ile dosyaya yazıyor. Rapor satırları
emoji içeriyor (`📌`, `🔋`, `👷`, `📏`, `🕒`, `☕`, `🏁`, `⏳`, `✅`). Türkçe Windows'un
varsayılan konsol kod sayfası **cp1254** olduğunda (veya çıktı bir dosyaya/boruya
yönlendirildiğinde) `print()` şu hatayla çöküyor:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4cc'
  in position 0: character maps to <undefined>
```

Kritik nokta: bu çökme **Gurobi optimizasyonu bittikten SONRA** gerçekleşiyor. Yani
saatler süren bir koşum tamamlanıyor, optimal bulunuyor, ama `Operasyon_Raporu_*.txt`
dosyası ilk emoji satırında yarıda kesiliyor ve süreç `Traceback` ile ölüyor.

## Gerçek koşum kanıtı

`echo "R5" | python raw/CV_model_gurobi_exact.py` (2026-08-22):

```
Optimal solution found (tolerance 5.00e-02)
Best objective 1.011610062378e+04, best bound 1.011610062378e+04, gap 0.0000%
R5 için Çözüm durumu: 2
=================================================================
       GÜNLÜK OPERASYON DETAYLI ZAMAN ÇİZELGESİ - R5
=================================================================
Traceback (most recent call last):
  ...  line 526, in print_cv_solution
    log_print(f"\U0001f4cc {v} ARACI OPERASYON RAPORU ...")
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4cc'
```

Üretilen `Operasyon_Raporu_R5.txt` yalnızca 3 satır (başlık) içeriyordu.

## Düzeltme

`log_print` içindeki konsol yazımı korumaya alındı; dosya zaten `encoding="utf-8"`
ile açıldığı için raporun kendisi tam ve doğru kalır:

```python
try:
    print(text)
except UnicodeEncodeError:
    enc = getattr(sys.stdout, 'encoding', None) or 'ascii'
    print(text.encode(enc, errors='replace').decode(enc, errors='replace'))
f.write(text + "\n")
```

Her iki dosyaya `import sys` eklendi (`raw/CV_model_gurobi_exact.py:2`,
`raw/EV_v.1.1.py:2`).

## Not

Bu hata v1.1'e özgü bir regresyon **değildir** — v1 kodunda da aynı emojiler vardı
(`git show HEAD:raw/CV_model_gurobi_exact.py` satır 269 vb.). Ancak "Değişiklik
Raporu - v1.1.docx"nin §2.2'de anlattığı Türkçe-karakter/`m.write()` sorununun
kardeşi olduğu ve tam olarak aynı ortam sınıfında (Türkçe Windows) tetiklendiği için
burada birlikte belgelenmiştir.

## Sources

- `raw/CV_model_gurobi_exact.py:450-466` (düzeltilmiş `log_print`)
- `raw/EV_v.1.1.py:490-500` (aynı düzeltme)
- `raw/CV_model_gurobi_exact.py:1-3`, `raw/EV_v.1.1.py:1-4` (`import sys`)

## Related

- [[cozum_raporlama_fonksiyonlari]]
- [[sorun_rapor_mola_suresi_3600_vs_ll_el]]
