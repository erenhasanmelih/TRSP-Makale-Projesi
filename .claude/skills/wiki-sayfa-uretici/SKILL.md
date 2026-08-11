---
name: wiki-sayfa-uretici
description: CLAUDE.md §4 (naming convention) ve §5 (sayfa formatı) kurallarına tam uyumlu, doğru frontmatter (title/tags/source/date/status) ve doğru klasöre (sources/entities/concepts/decisions/syntheses) yerleştirilmiş yeni bir wiki sayfası taslağı üretir. Herhangi bir yeni bulgu, karar veya sentez wiki'ye atomik sayfa olarak dosyalanacağı zaman kullan.
---

# Wiki Sayfa Üretici

Yeni bir wiki sayfasının şema hatası (yanlış dosya adı formatı, eksik frontmatter alanı, yanlış klasör) yapmadan oluşturulmasını sağlayan şablon üretici. [[trsp-wiki-kutuphaneci]] ajanı tarafından kullanılır, ancak diğer 4 uzman ajan da yeni bulgularını dosyalarken bu şablonu referans alır.

## Ne Zaman Kullanılır

- Herhangi bir ajan yeni bir bulguyu (kaynak özeti, varlık, kavram, karar, sentez) ilk kez wiki'ye yazarken.
- Mevcut bir sayfa `status: eskimiş` olarak işaretlenip `archive/`'a taşınırken (dosya adı ve frontmatter korunarak).

## Girdi Formatı

```
Sayfa tipi: source | entity | concept | decision | synthesis
Başlık: [Türkçe başlık]
Kaynak(lar): raw/dosya_adi.py (satır X-Y) | raw/Yönergelerimiz/dosya.docx
Tarih: YYYY-MM-DD
İlgili sayfalar: [[sayfa1]], [[sayfa2]], ...
```

## Çıktı Formatı — dosya adı ve klasör kuralı

| Tip | Klasör | Dosya adı deseni |
|---|---|---|
| source | `sources/` | `YYYY-MM-DD-slug.md` |
| entity | `entities/` | `slug.md` |
| concept | `concepts/` | `slug.md` |
| decision | `decisions/` | `karar_slug.md` \| `sorun_slug.md` \| `celiski_slug.md` |
| synthesis | `syntheses/` | `slug.md` |

Türkçe karakterler (ç,ğ,ı,ö,ş,ü) dosya adında ASCII'ye çevrilir (c,g,i,o,s,u); içerik/başlıklar normal Türkçe kalır.

## Çıktı Formatı — frontmatter + gövde şablonu

```markdown
---
title: [Sayfa Başlığı]
tags: [etiket1, etiket2]
source: raw/dosya_adi
date: YYYY-MM-DD
status: taslak
---

# [Sayfa Başlığı]

[İçerik — her iddia kaynak referanslı]

## Sources

- `raw/dosya_adi.py` (satır X-Y)
- [[ilgili_kaynak_sayfasi]]

## Related

- [[ilgili_concept]]
- [[ilgili_entity]]
- [[ilgili_decision]]
```

## Adımlar

1. Sayfa tipini belirle, yukarıdaki tabloya göre klasörü ve dosya adı desenini seç.
2. Türkçe karakterleri ASCII'ye çevirerek dosya adını üret, `Glob` ile aynı adın mevcut olup olmadığını kontrol et (çakışma varsa `wiki-sayfa-uretici` yeni bir slug önerir, mevcut sayfanın üzerine yazılmaz).
3. Frontmatter'ı doldur — `status` başlangıçta `taslak`, içerik netleştikçe `güncel`'e çevrilir.
4. Gövdeyi yaz, her önemli cümleye kaynak referansı ekle (dosya adı + satır aralığı veya `[[wiki sayfası]]`).
5. `Sources` ve `Related` bölümlerini doldur — `Related`'daki her bağlantı için hedef sayfanın kendisine de geri-link eklenip eklenmeyeceğini (`obsidian-link-checker` ile) değerlendir.
6. `index.md`'nin ilgili tablosuna yeni satırı ekle.

## Örnek

**Girdi:** "EV modelinde bulunan yeni bir Gurobi tuning parametresi için entity sayfası aç."

**Çıktı:** `entities/parametre_ev_gurobi_tuning_yeni.md` — frontmatter (`title: [Parametre Adı]`, `tags: [entity, gurobi, ev]`, `source: raw/EV_v.1.1.py`, `date: 2026-08-09`, `status: taslak`) + gövde + Sources/Related bölümleri + `index.md`'ye eklenen satır.

## İlgili

- CLAUDE.md §4, §5
- İlişkili skill: `obsidian-link-checker`
