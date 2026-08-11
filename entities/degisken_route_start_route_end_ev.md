---
title: Karar Değişkenleri — route_start / route_end / ord (EV, Teknisyen Çakışma Önleme)
tags: [entity, karar-değişkeni, ev, teknisyen-çakışması, yeni-bulgu]
source: raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Karar Değişkenleri — route_start / route_end / ord (EV)

`EV_v.1.1.py:225-299` içinde, sadece `crew_members` verisi doluysa aktifleşen bir blokta tanımlı. Hiçbir yönerge belgesinde bahsi geçmeyen, kodun kendi başına geliştirdiği bir mekanizma (bkz. [[karar_ev_teknisyen_cakisma_onleme_mekanizmasi]]).

- `route_start[t]`, `route_end[t]` (satır 237-238): her ekibin (crew) o günkü rotasının başlangıç/bitiş zamanını tutan sürekli değişkenler; sırasıyla depo çıkış/dönüş arc'larına Big-M kısıtlarıyla bağlanıyor (245-280).
- `ord_{tech}_{c1}_{c2}` (satır 290): bir teknisyenin (`tech`) birden fazla ekipte (`c1`, `c2`) yer aldığı durumlarda, bu iki ekibin zaman içinde hangisinin önce geldiğini belirleyen ikili sıralama değişkeni.
- `noov_1`/`noov_2` kısıtları (292-299): `ord` değişkenine göre `route_start[c2] >= route_end[c1]` ya da tersini zorlayarak, aynı teknisyeni içeren iki ekibin **çakışan saatlerde aktif olmasını engelliyor**.

## Neden önemli

CV modelinde ve hiçbir yönerge belgesinde bu problem (bir teknisyenin aynı anda iki farklı ekipte görünmesi) ele alınmıyor — ama `itertools.combinations` ile dinamik ekip oluşturma (bkz. [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]) yapıldığında bu problem matematiksel olarak kaçınılmaz hale geliyor (aynı teknisyen birden fazla ekip kombinasyonunda yer alabiliyor). EV kodu bunu fark edip çözmüş, CV kodu (aynı ekip oluşturma mantığını kullanmasına rağmen) bu korumaya sahip değil — bu, CV modelinde potansiyel bir **eksik kısıt / olası hata kaynağı**.

## Sources

- `raw/EV_v.1.1.py:225-299`

## Related

- [[karar_ev_teknisyen_cakisma_onleme_mekanizmasi]]
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]
- [[parametre_big_m_100000]]
