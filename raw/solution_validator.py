# -*- coding: utf-8 -*-
"""
Çözüm sonrası tutarlılık doğrulayıcısı.

Bu modül, CV_model_gurobi_exact.py ve EV_model_gurobi_exact.py'nin
ürettiği çözümleri, modelin matematiksel kısıtlarının GARANTİ ETMEDİĞİ
ama operasyonel olarak zorunlu olan iki noktada denetler:

  1. Çoklu sefer (CV-4/EV-4) kullanan bir kaynağın (k) art arda seferleri
     kronolojik olarak sıralı mı (2. sefer, 1. sefer bitmeden başlamıyor mu)?
  2. Aynı fiziksel aracı (v) paylaşan farklı ekipler (k=(v,t1), k=(v,t2))
     aynı gün, çakışan saatlerde kullanılmış mı (bir araç aynı anda iki
     ekiple olamaz)?

Bu iki koşul, x_ijk ve w_ijk üzerinden tanımlı mevcut kısıtlarda (CV-1..26,
EV-1..21) DOĞRUDAN yer almaz; tau[0,k] tek bir değişken olduğu ve
seferler/araç paylaşımı arasında sıralama kısıtı bulunmadığı için, teorik
olarak ihlal edilebilirler. Bu modül, her çözümden sonra ÇALIŞTIRILARAK bu
ihlallerin fiilen olup olmadığını sayısal olarak doğrular.
"""
from collections import defaultdict


def _reconstruct_trips(arcs):
    """Bir kaynağın (k) yaylarını, print_cv_solution ile aynı mantıkla
    ayrı seferlere (trip'lere) ayırır. Her trip [0, ..., 0] biçiminde bir
    düğüm listesidir."""
    next_map = {}
    depot_departures = []
    for i, j in arcs:
        if i == 0:
            depot_departures.append(j)
        else:
            next_map[i] = j
    depot_departures.sort()

    trips = []
    for start in depot_departures:
        trip = [0, start]
        current = start
        visited_in_trip = {start}
        while current != 0 and current in next_map:
            nxt = next_map[current]
            trip.append(nxt)
            if nxt == 0 or nxt in visited_in_trip:
                break
            visited_in_trip.add(nxt)
            current = nxt
        trips.append(trip)
    return [t for t in trips if len(t) > 1]


def _trip_time_window(trip, tau, kk, st, tt):
    """Bir seferin [çıkış, dönüş] zaman aralığını hesaplar. Çıkış zamanı
    ilk müşterinin varışından geriye doğru türetilir (bkz.
    print_cv_solution'daki aynı mantık); dönüş zamanı son müşterinin
    varış + hizmet + dönüş seyahat süresidir."""
    first_customer = trip[1]
    last_customer = trip[-2]
    departure = tau[first_customer, kk].X - tt.get((0, first_customer), 0.0)
    arrival_back = (
        tau[last_customer, kk].X
        + st.get(last_customer, 0.0)
        + tt.get((last_customer, 0), 0.0)
    )
    return departure, arrival_back


def validate_solution(model, data, x_key_is_triple=True):
    """model._x, model._tau, model._K üzerinden çözümü denetler.

    Döndürür: (ok: bool, findings: list[str])
    ok=True  -> hiçbir ihlal bulunamadı (iki koşul da sağlanıyor)
    ok=False -> findings listesinde insan-okunur ihlal açıklamaları var
    """
    x = model._x
    tau = model._tau
    K = model._K
    st = data.get('st', {})
    tt = data.get('tt', {})
    # Ö2 (2026-08-28): homojen filoda kk = t (skaler, fiziksel araç kimliği
    # YOK) olabilir (bkz. CV_model_gurobi_exact.py/EV_v.1.1.py
    # aggregate_fleet). K boşsa bile isinstance kontrolü güvenlidir.
    aggregate_fleet = getattr(model, '_aggregate_fleet', False) or (
        len(K) > 0 and not isinstance(K[0], tuple)
    )

    findings = []

    # Her k için kullanılan yayları topla
    arcs_by_k = defaultdict(list)
    for key, var in x.items():
        i, j, kk = key
        if var.X > 0.5:
            arcs_by_k[kk].append((i, j))

    # Her k için seferleri (trip) ve zaman aralıklarını hesapla
    windows_by_k = {}
    for kk, arcs in arcs_by_k.items():
        trips = _reconstruct_trips(arcs)
        windows = []
        for trip in trips:
            try:
                dep, ret = _trip_time_window(trip, tau, kk, st, tt)
            except KeyError:
                continue
            windows.append((dep, ret, trip))
        windows_by_k[kk] = windows

    # --- Kontrol 1: aynı k'nin seferleri kronolojik sıralı mı? ---
    for kk, windows in windows_by_k.items():
        windows_sorted = sorted(windows, key=lambda w: w[0])
        for idx in range(len(windows_sorted) - 1):
            dep1, ret1, trip1 = windows_sorted[idx]
            dep2, ret2, trip2 = windows_sorted[idx + 1]
            if dep2 < ret1 - 1e-6:
                findings.append(
                    f"SEFER SIRASI İHLALİ: kaynak {kk} için sefer "
                    f"{trip1} [{dep1:.1f}-{ret1:.1f}] ile sefer "
                    f"{trip2} [{dep2:.1f}-{ret2:.1f}] zaman olarak çakışıyor "
                    f"(2. sefer, 1. sefer bitmeden başlıyor)."
                )

    # --- Kontrol 2: aynı aracı (v) paylaşan farklı ekipler çakışıyor mu? ---
    #
    # Ö2 AGGREGATE MODU (2026-08-28): kk = t olduğunda modelde HANGİ
    # fiziksel aracın kullanıldığı hiç temsil edilmiyor (bkz.
    # CV_model_gurobi_exact.py/EV_v.1.1.py aggregate_fleet notu) — bu bilgi
    # olmadan "v = kk" gruplaması ANLAMSIZ olur (her ekibi kendi
    # "sahte aracı"na koyar ve hiçbir çakışma asla tespit edilemez, YANLIŞ
    # bir güven verir). Bunun yerine modelin CV27/EV22'nin agregatize
    # hâlinde garanti ettiği tek şey kontrol edilir: aynı anda aktif ekip
    # sayısı fiziksel araç sayısını (|V|) aşmıyor mu?
    if aggregate_fleet:
        vehicle_count = len(getattr(model, '_V', []) or [])
        active_at_once = 0
        events = []
        for kk, windows in windows_by_k.items():
            for dep, ret, trip in windows:
                events.append((dep, 1))
                events.append((ret, -1))
        for _, delta in sorted(events, key=lambda e: (e[0], -e[1])):
            active_at_once += delta
            if vehicle_count and active_at_once > vehicle_count:
                findings.append(
                    f"ARAÇ KAPASİTESİ İHLALİ: aynı anda {active_at_once} ekip "
                    f"aktif ama filoda yalnızca {vehicle_count} araç var "
                    f"(aggregate mod — Σz <= |V| kısıtı ihlal edilmiş görünüyor, "
                    f"bu normalde OLAMAZ; model/veri tutarsızlığını araştırın)."
                )
                break
    else:
        windows_by_v = defaultdict(list)
        for kk, windows in windows_by_k.items():
            v = kk[0] if x_key_is_triple else kk
            for dep, ret, trip in windows:
                windows_by_v[v].append((dep, ret, kk, trip))

        for v, windows in windows_by_v.items():
            windows_sorted = sorted(windows, key=lambda w: w[0])
            for idx in range(len(windows_sorted) - 1):
                dep1, ret1, k1, trip1 = windows_sorted[idx]
                dep2, ret2, k2, trip2 = windows_sorted[idx + 1]
                if k1 == k2:
                    continue  # aynı kaynağın kendi seferleri Kontrol 1'de ele alındı
                if dep2 < ret1 - 1e-6:
                    findings.append(
                        f"ARAÇ ÇAKIŞMASI: araç {v}, {k1} (sefer {trip1}, "
                        f"[{dep1:.1f}-{ret1:.1f}]) ve {k2} (sefer {trip2}, "
                        f"[{dep2:.1f}-{ret2:.1f}]) tarafından çakışan saatlerde "
                        f"kullanılmış."
                    )

    ok = len(findings) == 0
    return ok, findings


def summarize_trips(model, data):
    """Teşhis amaçlı: kaç kaynağın kaç seferi olduğunu özetler."""
    x = model._x
    arcs_by_k = defaultdict(list)
    for (i, j, kk), var in x.items():
        if var.X > 0.5:
            arcs_by_k[kk].append((i, j))
    multi_trip = {}
    for kk, arcs in arcs_by_k.items():
        trips = _reconstruct_trips(arcs)
        if len(trips) > 1:
            multi_trip[kk] = len(trips)
    return multi_trip
