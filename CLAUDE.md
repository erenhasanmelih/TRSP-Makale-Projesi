# CLAUDE.md — TRSP Bilgi Arşivi Şeması

Bu dosya bu wiki'nin anayasasıdır. Ajan (Claude Code) bu vault üzerinde çalışırken aşağıdaki kurallara uyar. Şema zamanla evrilir — bkz. [Evrim Notu](#evrim-notu).

Bu wiki, `.claude/skills/llm-wiki.md` içinde tanımlanan **llm-wiki** desenine dayanır ve TRSP projesine uyarlanmıştır.

## 1. Amaç

Bu vault, **TRSP (Teknisyen Rotalama ve Çizelgeleme Problemi)** üzerine yürütülen araştırma ve geliştirme çalışmasının kalıcı bilgi arşividir.

Kapsam:
- Telekomünikasyon sektöründe **EV (Electric Vehicle) ve CV (Combustion Vehicle) karma filolarıyla** teknisyen rotalama ve çizelgeleme.
- **Gurobi** ile kurulan tam (exact) **MIP (Mixed-Integer Programming)** modeli — kısıtlar, karar değişkenleri, amaç fonksiyonu, Big-M formülasyonları.
- **Q-Learning + VND (Variable Neighborhood Descent)** melez sezgisel (hybrid heuristic) algoritmasının geliştirilmesi.
- Bu ikisinin (exact model vs. heuristic) karşılaştırmalı performans analizi.

Bu wiki'nin cevap aramaya çalıştığı sorular: Model hangi kısıtları nasıl formüle ediyor ve neden? Kod, matematiksel modelden nerelerde ayrışıyor ve bu ayrışmalar bilinçli mi? Q-Learning + VND hangi tasarım kararlarıyla şekillendi? Hangi deney hangi sonucu verdi, hangi kaynaktan geliyor? Exact model ile heuristic arasındaki Pareto trade-off'ları (çözüm kalitesi vs. çözüm süresi) nedir?

## 2. Dil

- **Tüm wiki sayfaları Türkçe yazılır** (başlıklar, açıklamalar, analiz, senteze).
- Teknik terimler İngilizce kalabilir: `MIP`, `Big-M`, `Q-Learning`, `VND`, `partial recharging`, `colored TSP`, `time window`, `state-of-charge (SoC)` vb. Zorla Türkçeleştirme yapılmaz.
- Kod içi tanımlayıcılar (fonksiyon adı, değişken adı, dosya adı) olduğu gibi bırakılır, çevrilmez.

## 3. Klasör yapısı

```
.
├── CLAUDE.md          # bu dosya — şema
├── index.md           # içerik kataloğu, kategori bazında
├── log.md             # append-only zaman damgalı olay kaydı
├── raw/                # ham kaynaklar — ASLA DEĞİŞTİRİLMEZ
│   ├── Yönergelerimiz/  # Word (.docx) yönerge/notlar
│   ├── *.py             # Gurobi modeli, veri yükleyici, dönüştürücü script'leri
│   ├── *.xml             # problem set'leri, filo/istasyon/çalışan bilgisi
│   ├── *.lp               # Gurobi'nin ürettiği exact model dosyaları
│   ├── sonuclar/          # optimizasyon sonuç raporları (.docx)
│   └── problem_sets/, trsp_problem_sets/, ciktilar/  # veri/çıktı alt klasörleri
├── sources/            # her ham kaynak için BİR özet sayfası
├── entities/           # fonksiyonlar, kütüphaneler, değişkenler, parametreler
├── concepts/           # Colored TSP, Partial Recharging, Big-M Tightening, Q-Learning vb.
├── decisions/          # atomik mimari ve kod kararları
├── syntheses/          # üst düzey karşılaştırma ve Pareto analiz sayfaları
└── archive/            # eskimiş sayfalar — ASLA SİLİNMEZ, sadece buraya taşınır
```

Klasör anlamları:
- **sources/**: "Bu kaynakta ne yazıyor?" sorusunun cevabı. Ham dosyanın 1:1 özeti + çıkarımlar.
- **entities/**: Somut, adlandırılabilir yapı taşları — bir Python fonksiyonu (`add_partial_recharge_constraint`), bir kütüphane (`gurobipy`), bir model değişkeni (`x[i,j,k]`), bir parametre (`BIG_M`, `battery_capacity`).
- **concepts/**: Soyut fikirler ve teknikler — Colored TSP, Partial Recharging, Big-M Tightening, Q-Learning, VND, time window relaxation vb.
- **decisions/**: "Neden böyle yaptık?" sorusunun atomik cevabı — her karar tek bir sayfa, tek bir fikir. Örn: "Neden SoC değişkeni sürekli değil kesikli tutuldu."
- **syntheses/**: Birden fazla kaynağı/kararı/kavramı bir araya getiren üst düzey sayfalar — exact model vs. heuristic karşılaştırması, Pareto analizi, deney serisi özetleri.
- **archive/**: Geçersiz kalmış ama silinmeyen sayfalar. Tarih ve geçersiz kalma nedeni korunur.

## 4. Naming convention

- Tüm wiki sayfa dosya adları **snake_case**: `partial_recharging.md`, `big_m_tightening.md`, `ev_v1_1_model_yapisi.md`.
- `sources/` sayfaları: `YYYY-MM-DD-slug.md` formatında (kaynağın işlendiği tarih + kısa açıklayıcı slug). Örn: `sources/2026-08-09-ev_v1_1_gurobi_model.md`.
- Türkçe karakterler (ç, ğ, ı, ö, ş, ü) dosya adlarında **ASCII karşılıklarına çevrilir** (c, g, i, o, s, u) — çapraz platform uyumluluğu için. Sayfa içeriği ve başlıkları normal Türkçe kalır.
- Varlık (entity) adları kanonikleştirilir: bir Python fonksiyonu/değişkeni birden fazla dosyada geçiyorsa hepsi aynı `entities/` sayfasına link verir, kod içindeki tam ad frontmatter'da `title` olarak saklanır.

## 5. Sayfa formatı

Her wiki sayfası (sources/entities/concepts/decisions/syntheses) şu formatta:

```markdown
---
title: Sayfa Başlığı
tags: [etiket1, etiket2]
source: raw/dosya_adi.py
date: YYYY-MM-DD
status: taslak | güncel | eskimiş
---

# Sayfa Başlığı

İçerik. Her önemli iddia kaynağını belirtir (dosya adı, satır aralığı, veya bölüm).

## Sources

- `raw/dosya_adi.py` (satır 40-85)
- [[ilgili_kaynak_sayfasi]]

## Related

- [[ilgili_concept]]
- [[ilgili_entity]]
- [[ilgili_decision]]
```

- `[[sayfa_adi]]` sözdizimi Obsidian-stili çapraz-referans için kullanılır (uzantısız).
- `status: eskimiş` olan sayfalar `archive/`'a taşınmadan önce geçici olarak bu şekilde işaretlenebilir; ama kalıcı geçersizlik durumunda mutlaka `archive/`'a taşınır (bkz. Hard Rules).

## 6. Üç operasyon workflow'u (TRSP'ye uyarlanmış)

### INGEST — kaynak emme

Tetikleyici: kullanıcı `raw/` içine yeni bir dosya koyar ve "şunu ingest et" der (veya belirli bir dosya/klasör adı verir).

**Özel durum — bu proje için INGEST kapsamı**: `raw/` içindeki yalnızca iki tip kaynak birincil ingest hedefidir:
1. **Word (.docx) yönergeleri** — özellikle `raw/Yönergelerimiz/` altındaki yönerge/not dosyaları (proje talimatları, matematiksel model ↔ kod farklılıkları, makale adımları, dinamik tahminleme notları vb.).
2. **Python (.py) dosyaları** — Gurobi modelleri (`EV_v.1.1.py`, `CV_model_gurobi_exact.py`), veri yükleyici/dönüştürücü script'leri (`xml_data_loader.py`, `dataset_converter.py`) ve geçici/test script'leri (`_tmp_*.py`).

`raw/sonuclar/` altındaki sonuç `.docx` dosyaları ve `raw/*.xml`, `raw/*.lp` veri/çıktı dosyaları wiki'nin ikincil kaynaklarıdır — kullanıcı özellikle isterse ingest edilir, varsayılan ingest taramasına dahil edilmez (çok büyük ve büyük ölçüde ham veri, `.lp` dosyaları onlarca MB).

Her kaynak için adımlar:
1. Kaynağın içeriğini tara (`.docx` için metni çıkar, `.py` için kodu oku — fonksiyon/sınıf yapısı, önemli değişkenler, kısıt/amaç fonksiyonu tanımları).
2. Ana konuyu ve anahtar çıkarımları belirle.
3. `sources/YYYY-MM-DD-slug.md` olarak özet sayfası yaz (format: bkz. §5).
4. `index.md`'nin ilgili bölümünü güncelle (yeni kaynak satırı ekle).
5. Kaynakta bahsedilen `entities/`, `concepts/`, `decisions/` sayfalarını çapraz-güncelle:
   - Yeni bir fonksiyon/değişken/parametre görüldüyse → `entities/` sayfası oluştur veya güncelle.
   - Yeni bir teknik/kavram görüldüyse (örn. yeni bir kısıt tipi, yeni bir sezgisel bileşen) → `concepts/` sayfası oluştur veya güncelle.
   - Kaynak bir tasarım/kod kararını açıklıyorsa → `decisions/` altında atomik bir karar sayfası oluştur.
6. Mevcut sayfalarla çelişki varsa **"## ÇELİŞKİ"** başlığı altında işaretle, hiçbir şeyi silme (bkz. Hard Rules §8).
7. `log.md`'ye zaman damgalı giriş ekle: `## [YYYY-MM-DD] ingest | Kaynak adı → N sayfa dokunuldu`.

Tek bir `.py` dosyası (örn. `EV_v.1.1.py`, ~800+ satır) onlarca `entities/` ve birkaç `decisions/` sayfasına dokunabilir — bu normaldir.

### QUERY — sorgu

1. Önce `index.md` okunur.
2. İlgili `sources/`, `entities/`, `concepts/`, `decisions/`, `syntheses/` sayfaları bulunur ve okunur.
3. Cevap sentezlenir (metin, tablo, karşılaştırma — soruya uygun ne ise).
4. Her iddia kaynak sayfasına veya doğrudan `raw/` dosyasına referans verir.
5. **Değerli bir cevap** (yeni bir karşılaştırma, keşfedilen bir bağlantı, bir Pareto analizi) `syntheses/` veya ilgili kategoriye **atomik yeni sayfa** olarak dosyalanır — sohbette kaybolmaz.
6. Anlamlı sorgular `log.md`'ye eklenir: `## [YYYY-MM-DD] query | "Soru" → filed: syntheses/xxx.md`.

### LINT — sağlık kontrolü

Periyodik olarak (kullanıcı talebiyle) çalıştırılır. Kontrol edilenler:
- Sayfalar arası **çelişkiler** (özellikle model ↔ kod farklılıkları — bu proje için kritik bir tema).
- Yeni kaynaklarla geçersiz kalmış **stale claim**'ler.
- Hiçbir yerden link almayan **orphan** sayfalar.
- Wiki'de adı geçen ama kendi sayfası olmayan `entities/`/`concepts/` (örn. kodda kullanılan ama belgelenmemiş bir parametre).
- Eksik veya tek yönlü çapraz-referanslar.
- Sonuç dosyalarından (`raw/sonuclar/`) çıkarılabilecek ama henüz `syntheses/`'a işlenmemiş performans karşılaştırmaları.

Lint sonunda önerilen yeni ingest'ler ve yeni sorular raporlanır. Sonuç `log.md`'ye eklenir: `## [YYYY-MM-DD] lint | N çelişki, N orphan`.

## 7. Hard rules

1. **`raw/` asla değiştirilmez.** Ajan sadece okur; yazmaz, taşımaz, yeniden adlandırmaz, silmez. Kullanıcı ekler.
2. **Kaynaksız iddia yasak.** Wiki'deki her önemli cümle bir `raw/` dosyasına veya başka bir wiki sayfasına referans verir.
3. **Sayfa silme yok.** Eskimiş/hatalı sayfa önce `archive/`'a taşınır (git mv mantığıyla, tarih korunur), sonra `index.md` güncellenir. Doğrudan silme yasak.
4. **Çelişkiler işaretlenir, silinmez.** İki kaynak/sayfa çelişiyorsa ilgili sayfada **"## ÇELİŞKİ"** başlığı açılır, her iki taraf da kaynağıyla birlikte yazılır. Çelişki çözülene kadar bu başlık kalır; çözüldüğünde "çözüldü" notu eklenir ama başlık ve geçmiş silinmez.
5. **Çift-yönlü bağlantı düşüncesi.** Bir sayfa güncellenirken ona link veren diğer sayfalar da gözden geçirilir.
6. **Her operasyon log'lanır.** Ingest, anlamlı query'ler ve lint pass'leri `log.md`'ye zaman damgalı eklenir.
7. **Şema birlikte evrilir.** Bir kural işlemiyorsa bu dosya güncellenir; sonraki oturumlarda yeni kural geçerli olur (bkz. §8).
8. **Filed-back her şey atomiktir.** Bir sorgu cevabı wiki'ye dosyalanırken tek bir "oturum özeti" değil, her biri tek bir fikri taşıyan ayrık sayfalar olarak yazılır.

## 8. Evrim Notu

Bu şema sabit değildir. Kullanıcı ile ajan zaman içinde birlikte geliştirir:
- Bir kural pratikte işe yaramıyorsa, önce kullanıcıyla tartışılır, sonra bu dosyada güncellenir.
- Şema değiştiğinde önceki sayfalar **geriye dönük zorla düzeltilmez** — yeni ingest/query işlemlerinde yeni kural uygulanır. Eski sayfalar tutarsız kalırsa bir sonraki LINT pass'inde yakalanıp güncellenir.
- Önemli şema değişiklikleri `log.md`'ye `## [YYYY-MM-DD] schema | Değişiklik özeti` olarak not düşülür.
