---
title: Literatürdeki Alternatif Meta-Sezgiseller (VLSN, ALNS, MTZ, Filtered Beam Search, HSA)
tags: [kavram, literatür, meta-sezgisel, karşılaştırma]
source: raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Literatürdeki Alternatif Meta-Sezgiseller

"EK NOKTALAR VE MAKALELERİ.docx" belgesinde TRSP'nin farklı alt problemleri için literatürden örnek gösterilen, ancak projenin nihai mimarisinde (Q-Learning + VND) **doğrudan kullanılmayan** alternatif yöntemlerin toplu referans sayfası. Atıf/karşılaştırma amaçlı tutuluyor.

- **VLSN (Very Large-Scale Neighborhood Search):** Açgözlü (Greedy) yapıcı sezgisellerle birlikte, çok kapsamlı komşuluk aramasıyla envanter-rotalama problemlerini entegre çözmek için kullanılıyor (*An Integrated Inventory-Routing System...*).
- **ALNS (Adaptive Large Neighborhood Search):** Kullanıcının kendi taslak metninde, Sweep ile birlikte melez (hybrid) bir mimaride TRSP'yi çözmek için önerilmiş — nihai mimaride VND + Q-Learning tercih edildiği için ALNS şu an literatür referansı statüsünde kalıyor.
- **MTZ (Miller-Tucker-Zemlin) alt-tur önleme kısıtları:** "makale adımlar ve düzenlemeler.docx"'te, gevşek Big-M ile birlikte anılan alt-tur (sub-tour) önleme zafiyetinin kaynağı olarak geçiyor; `tau` (zaman) değişkeni üzerinden kurulan kısıtlara işaret ediyor.
- **Filtered Beam Search:** Esnek üretim sistemlerinde makine/araçların (AGV) planlama ufku boyunca eşzamanlı çizelgelenmesi için kullanılan yarı-kesin arama ağacı sezgiseli.
- **Hyper Simulated Annealing (HSA):** [[q_learning]] ile yönlendirilen bir hiper-sezgisel; stokastik montaj hattı sıralaması problemlerinde kullanılıyor.

## Neden ayrı bir sayfa

Bu yöntemler projenin gerçek algoritma mimarisinin (bkz. [[karar_hibrit_algoritma_mimari_sirasi]]) parçası değil, literatür haritalaması / atıf gerekçelendirmesi amacıyla toplanmış örnekler. [[vnd]] ve [[q_learning]] sayfalarından farklı olarak burada aktif geliştirme kararı yok.

## Sources

- `raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[q_learning]]
- [[vnd]]
- [[tight_big_m]]
- [[karar_literatur_temelli_problem_tanimi_md_gctsp_tw]]
