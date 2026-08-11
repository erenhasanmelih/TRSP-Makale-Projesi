---
title: Pareto Analizi / ε-Constraint Yöntemi
tags: [kavram, çok-amaçlı-optimizasyon, pareto, ev-cv-kıyaslama]
source: raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Pareto Analizi / ε-Constraint Yöntemi

Çok amaçlı (bi-objective) optimizasyon problemlerinde, amaçlardan birini minimize ederken diğerini bir kısıt (ε) olarak modele ekleyerek Pareto Cephesi (Pareto Frontier) üreten çözüm yöntemi.

## TRSP projesindeki planlanan kullanımı

- **Amaç:** Operasyonel Maliyetler (mesafe, yakıt/şarj, maaş) ile Müşteri Bekleme Süresi veya Karbon Emisyonu'nun aynı anda optimize edilmesi.
- **Yöntem:** Acar vd. (2025)'e atıfla, maliyet minimize edilirken karbon emisyonunun bir "kısıt" (ε) olarak modele eklenmesi.
- **Beklenen çıktı:** CV vs EV filoları için yönetimsel çıkarımlar (Managerial Insights) — "Bütçe kısıtlıysa CV, sıfır emisyon hedefleniyorsa ve zaman penceresi esnekse EV tercih edilmelidir."
- **Ayrıca:** hedef fonksiyonuna sadece mesafe değil, teknisyenler arası iş yükü dengelemesi de eklendiğinde, çatışan bu amaçların ε-kısıt yöntemiyle çözülmesi planlanıyor (Acar et al., 2025).

## Durum

Henüz kodda uygulanmamış; Full Path.docx Adım 4 kapsamında planlanıyor (bkz. [[karar_pareto_epsilon_constraint_plani]]).

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[karar_pareto_epsilon_constraint_plani]]
- [[karar_literatur_temelli_problem_tanimi_md_gctsp_tw]]
