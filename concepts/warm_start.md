---
title: Warm-Start (Sweep / Window-Wise Sweep / K-Means)
tags: [kavram, sezgisel, başlangıç-çözümü, kümeleme]
source: raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx; raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Warm-Start (Sweep / Window-Wise Sweep / K-Means)

Optimizasyon çözücüsüne (Gurobi) veya meta-sezgisel algoritmaya başlangıç noktası olarak hızlı, geçerli (feasible) bir çözüm sağlama tekniği. Dar zaman pencereli veya büyük ölçekli problemlerde çözücünün "körlemesine" aramasını engeller.

## TRSP projesindeki kullanım biçimleri

- **Window-Wise Sweep (Zaman Pencereli Süpürme):** dinamik tahminleme belgesinde, günlük atama öncesi hızlı rota oluşturma için önerilmiş.
- **Sweep veya K-Means:** Full Path.docx'te müşterilerin coğrafi olarak ve yetkinliklerine göre kümelenmesi için önerilmiş.
- **Sweep Algorithm (Adım 2):** "makale adımlar ve düzenlemeler" belgesinde, kümeleme sonrası hızlı ve geçerli başlangıç rotaları üretmek için — hem Gurobi'nin hem meta-sezgiselin körlemesine arama yapmasını engellemek amacıyla.

## Hibrit mimarideki konumu

Kümeleme (CatBoost/TOPSIS) → **Warm-Start (Sweep)** → Yerel Branch-and-Bound → VND (+ Q-Learning). Bkz. [[karar_hibrit_algoritma_mimari_sirasi]].

## Sources

- `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx`
- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[q_learning]]
- [[vnd]]
- [[karar_hibrit_algoritma_mimari_sirasi]]
