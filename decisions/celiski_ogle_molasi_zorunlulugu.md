---
title: ÇELİŞKİ — Öğle Molası Zorunlu (Model) vs Opsiyonel (Kod)
tags: [çelişki, kısıt, mola, kritik]
source: raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx
date: 2026-08-09
status: güncel
---

# ÇELİŞKİ — Öğle Molası Zorunlu (Model) vs Opsiyonel (Kod)

## ÇELİŞKİ

**Matematiksel model tarafı:** Kısıt (12), göreve çıkan her teknisyen için mutlaka **tam olarak bir** öğle yemeği molası atanmasını `=1` eşitliğiyle zorunlu kılar.

**Kod tarafı:** `mola_max1_{t}` kısıtı `<=1` şeklinde modellenmiş — yani mola kullanmak **zorunlu değil**, en fazla bir kez kullanılabilecek bir opsiyon.

## Neden önemli

Bu fark, gün içi rotanın toplam süresini ve teknisyenlerin yasal mola hakkını doğrudan etkiler. Kodun opsiyonel davranışı, kısa rotalarda mola atlanarak daha hızlı çözüm bulunmasını kolaylaştırıyor olabilir (bir tür gevşetme/relaxation), ama bu iş hukuku açısından model varsayımıyla çelişiyor.

## İlişkili kod kararı

Kodun `mola_yoksa_erken_donus_{i}_{v}_{t}` kısıtı bu opsiyonelliği telafi etmeye çalışıyor: mola kullanılmadıysa depoya dönüşü daha erken saate zorluyor (bkz. [[karar_molasiz_erken_donus_kurali_kod]]). Model tarafında mola zaten zorunlu olduğundan böyle bir telafi kısıtına ihtiyaç yok.

## Stage 2 kod doğrulaması (2026-08-09)

Doğrulandı — kod, docx'ün tarifiyle tam örtüşüyor: `mola_max1_{t}` kısıtı hem CV (`CV_model_gurobi_exact.py:88-96`) hem EV (`EV_v.1.1.py:177-183`) dosyalarında `sum_w <= gp.quicksum(x[0,i,v,t] ...)` şeklinde, yani mola göstergesinin toplamı en fazla 1 (opsiyonel), zorunlu değil.

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- `raw/CV_model_gurobi_exact.py:88-96`
- `raw/EV_v.1.1.py:177-183`

## Related

- [[karar_molasiz_erken_donus_kurali_kod]]
- [[sorun_hardcoded_mola_parametreleri]]
- [[sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar]]
