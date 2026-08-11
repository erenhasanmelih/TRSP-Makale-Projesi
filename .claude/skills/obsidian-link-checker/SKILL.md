---
name: obsidian-link-checker
description: TRSP wiki'sindeki tüm markdown sayfalarını tarayıp Obsidian-stili [[wikilink]] bütünlüğünü denetler — kırık linkler (hedefi olmayan [[sayfa]]), orphan sayfalar (hiçbir yerden link almayan), ve tek-yönlü çapraz-referanslar (A→B var ama B→A yok) tespit eder. Bir LINT taraması sırasında veya birden fazla sayfa güncellendikten sonra bağlantı bütünlüğü doğrulanırken kullan.
---

# Obsidian Link Checker

CLAUDE.md §6 (LINT operasyonu) ve §7 madde 5'te (çift-yönlü bağlantı düşüncesi) tanımlanan denetimi mekanik olarak yürüten grep-tabanlı yöntem. [[trsp-wiki-kutuphaneci]] ajanı tarafından kullanılır.

## Ne Zaman Kullanılır

- Periyodik LINT taraması sırasında (`lint-report-YYYY-MM-DD.md` üretimi).
- Bir INGEST/QUERY operasyonu birden fazla sayfayı güncelledikten sonra, yeni eklenen çapraz-referansların hedeflerinin gerçekten var olduğunu doğrularken.
- Kullanıcı "şu sayfaya kim link veriyor" gibi bir soru sorduğunda.

## Girdi Formatı

```
Kapsam: tüm wiki | belirli bir klasör (örn. sadece decisions/) | belirli bir sayfa listesi
```

## Çıktı Formatı

Üç kategoride bulgu listesi:

1. **Kırık linkler:** `[[hedef_sayfa]]` biçimindeki referans, ancak `hedef_sayfa.md` dosyası hiçbir klasörde (`sources/`, `entities/`, `concepts/`, `decisions/`, `syntheses/`, `archive/`) bulunamıyor.
2. **Orphan sayfalar:** dosya var ama hiçbir başka sayfada `[[bu_sayfa]]` şeklinde referans edilmiyor (ve `index.md`'de de listelenmiyor).
3. **Tek-yönlü xref:** `A.md` içinde `[[B]]` var ama `B.md` içinde `[[A]]` yok — CLAUDE.md §7 madde 5 ihlali adayı (her zaman hata değildir, ama gözden geçirilmeli).

Her bulgu satırı: `[kategori] dosya_adı.md → detay`.

## Adımlar

1. Tüm `.md` dosyalarını (`sources/`, `entities/`, `concepts/`, `decisions/`, `syntheses/`, `archive/`) tara, her birinde geçen `[[...]]` desenlerini çıkar.
2. Her `[[hedef]]` için `hedef.md` dosyasının var olup olmadığını `Glob` ile kontrol et → yoksa "kırık link" olarak işaretle.
3. Tüm sayfa adlarının bir kümesini çıkar, hangilerinin hiç referans almadığını belirle → "orphan" olarak işaretle (index.md'deki tablo satırlarını da referans say).
4. Her `A→B` linki için `B→A` var mı kontrol et → yoksa "tek-yönlü xref" olarak işaretle (bilgi amaçlı, otomatik düzeltme yapma).
5. Sonuçları önem sırasına göre (kırık link > orphan > tek-yönlü) raporla; `trsp-wiki-kutuphaneci` bunu `lint-report-YYYY-MM-DD.md`'ye işler.

## Örnek

**Girdi:** "Tüm decisions/ klasörünü tara."

**Çıktı:**
```
[kırık link] karar_x.md → [[konsept_y]] hedefi bulunamadı
[orphan] sources/2026-08-09-full_path.md → hiçbir sayfadan referans almıyor
[tek-yönlü xref] karar_hibrit_algoritma_mimari_sirasi.md → [[q_learning]] var, q_learning.md → [[karar_hibrit_algoritma_mimari_sirasi]] yok
```

## İlgili

- CLAUDE.md §6 (LINT), §7 madde 5
- `lint-report-2026-08-09.md` (önceki taramanın raporu — format referansı)
- İlişkili skill: `wiki-sayfa-uretici`
