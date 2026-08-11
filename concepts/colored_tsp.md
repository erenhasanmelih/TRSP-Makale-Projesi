---
title: Colored TSP (Renkli Gezgin Satıcı Problemi)
tags: [kavram, rotalama, uyumluluk, literatür]
source: raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Colored TSP (Renkli Gezgin Satıcı Problemi)

Gezgin Satıcı Problemi'nin (TSP), her düğüme (müşteriye) sadece belirli "renk"teki (yetkinlik/uyumluluk grubu) araçların/ajanların gidebildiği bir varyantı. Literatür kaynağı: *Multi-Depot General Colored Traveling Salesman Problem with Time Windows in Home Healthcare System* (VND + "Bölme/Splitting" prosedürü kullanıyor).

## TRSP projesindeki rolü

- **Problem tanımının temeli:** Acar & Altın (2025) çalışmasına atıfla, TRSP'nin "Zaman Pencereli Çok Depolu Genel Renkli Gezgin Satıcı Problemi (MD-GCTSP-TW)" olarak temellendirilmesi planlanıyor (bkz. [[karar_literatur_temelli_problem_tanimi_md_gctsp_tw]]).
- **Uyumluluk matrisi mantığı:** Home healthcare makalesindeki "her aracın her hastaya gidememesi" durumu "Renkler (Colors)" ve "Uyumluluk Matrisi (Compatibility Constraints)" ile modelleniyor — TRSP'deki "belirli teknisyenlerin belirli araçlara binmesi ve sadece kendi yetkinliklerine uygun işlere gitmesi" mantığıyla birebir örtüşüyor.
- **İndis düşürme (index reduction):** 4 boyutlu karar değişkeninin (çıkış, varış, araç, ekip) 3 boyuta (çıkış, varış, uyumlu araç-ekip kaynağı) indirgenmesi, Colored TSP mantığından ("araç ve ekip önceden eşleştirilecek") türetiliyor — bkz. [[index_reduction_3b]].

## Güncelleme (Faz 2, 2026-08-11)

"İndis düşürme" alt maddesindeki plan artık uygulandı — bkz. [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]] ve [[index_reduction_3b]] (Uygulama bölümü). Uygulanan çözüm, planın "araç ve ekip önceden eşleştirilecek" varsayımını birebir izlemedi; bunun yerine tüm (araç,ekip) çiftleri `K_pairs` olarak tutulup uyumsuzlar yetkinlik filtresiyle (`_crew_allowed`, A5) elendi — colored-TSP'nin "her düğüme sadece uyumlu renk gidebilir" mantığı bu filtreleme adımında somutlaştı.

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`
- `src/EV_v_1_1_fixed.py:113-145`
- `src/CV_model_gurobi_fixed.py:37-64`

## Related

- [[index_reduction_3b]]
- [[uyumluluk_matrisi]]
- [[vnd]]
- [[karar_literatur_temelli_problem_tanimi_md_gctsp_tw]]
- [[sources/2026-08-09-full_path]]
- [[sources/2026-08-09-ek_noktalar_ve_makaleleri]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
