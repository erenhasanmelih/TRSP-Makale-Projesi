---
title: TOPSIS
tags: [entity, çok-kriterli-karar-verme, önceliklendirme]
source: raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: taslak
---

# TOPSIS

Çok Kriterli Karar Verme (ÇKKV / MCDM) yöntemi (Technique for Order Preference by Similarity to Ideal Solution). TRSP projesinde henüz koda entegre edilmemiş, planlama aşamasında iki rolde öneriliyor:

1. **Teknisyen performans/uzmanlık sıralaması:** Heterojen yetkinlik matrisleri, geçmiş arıza çözme performansı ve vardiya tercihleri TOPSIS ile değerlendirilerek optimal ve adil bir haftalık taslak oluşturulur.
2. **Düşük öncelikli iş emri sıralaması:** İptal skoru orta seviyede (şüpheli ama filtrelenmeyecek kadar düşük riskli) olan iş emirleri TOPSIS ile ağırlıklandırılarak "düşük öncelikli" olarak sıralanır ve rotanın sonuna eklenir.

"Makale adımlar ve düzenlemeler" belgesinde ayrıca hibrit algoritmanın Adım 1 (Veri Ön İşleme ve Kümeleme) katmanında CatBoost ile birlikte anılıyor.

## Sources

- `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[catboost]]
- [[iptal_olasiligi_tahmini]]
- [[karar_iptal_olasiligi_on_filtreleme_plani]]
- [[karar_hibrit_algoritma_mimari_sirasi]]
- [[sources/2026-08-09-dinamik_tahminleme_adimlari_ve_veri]]
