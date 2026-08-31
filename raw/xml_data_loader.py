import glob
import math
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Any


def _strip_hash_comments(line: str) -> str:
    cleaned = []
    in_quote = False
    quote_char = None
    for ch in line:
        if ch in ('"', "'"):
            if in_quote and ch == quote_char:
                in_quote = False
                quote_char = None
            elif not in_quote:
                in_quote = True
                quote_char = ch
            cleaned.append(ch)
        elif ch == '#' and not in_quote:
            break
        else:
            cleaned.append(ch)
    return ''.join(cleaned).rstrip()


def _safe_parse_xml(path: str) -> ET.ElementTree:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    cleaned = '\n'.join(_strip_hash_comments(line) for line in text.splitlines())
    return ET.ElementTree(ET.fromstring(cleaned))


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in meters between two points."""
    r = 6371000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _parse_location(location_element: ET.Element) -> Tuple[float, float]:
    lat = location_element.findtext('Latitude')
    lon = location_element.findtext('Longitude')
    return float(lat or 0.0), float(lon or 0.0)


def _find_problem_xmls(root_dir: str, subdirs: List[str]) -> List[str]:
    paths = []
    for subdir in subdirs:
        folder = os.path.join(root_dir, subdir)
        if not os.path.isdir(folder):
            continue
        paths.extend(sorted(glob.glob(os.path.join(folder, '*.xml'))))
    return paths


def load_problem_instances(root_dir: str, subdirs: List[str]) -> Dict[str, Dict[str, Any]]:
    instances: Dict[str, Dict[str, Any]] = {}
    problem_paths = _find_problem_xmls(root_dir, subdirs)

    for path in problem_paths:
        tree = _safe_parse_xml(path)
        root = tree.getroot()

        depot_node = None
        deliveries: List[Dict[str, Any]] = []
        for node in root.findall('.//Node'):
            node_type = node.get('Type', '').strip()
            node_id = node.get('No') or node.get('Name') or str(len(deliveries) + 1)
            node_id = str(node_id)
            location = node.find('Location')
            if location is None:
                continue
            lat, lon = _parse_location(location)

            if node_type.lower() == 'entrance':
                depot_node = {
                    'id': node_id,
                    'label': node.get('Name', node_id),
                    'type': node_type,
                    'lat': lat,
                    'lon': lon,
                    'service_time': 0.0,
                    'ready_time': 0.0,
                    'due_date': 100000.0,
                }
                continue

            if node_type.lower() == 'delivery':
                request = node.find('.//Request')
                ready = float(request.get('ReadyTime', '0') or 0.0) if request is not None else 0.0
                due = float(request.get('DueDate', '0') or 0.0) if request is not None else 100000.0
                service_time = float(request.get('ServiceTime', '0') or 0.0) if request is not None else 0.0
                deliveries.append({
                    'id': node_id,
                    'label': node.get('Name', node_id),
                    'type': node_type,
                    'lat': lat,
                    'lon': lon,
                    'service_time': service_time,
                    'ready_time': ready,
                    'due_date': due,
                })

        if depot_node is None:
            raise ValueError(f"No entrance/depot node found in problem XML: {path}")

        instance_name = os.path.relpath(path, root_dir)
        instances[instance_name] = {
            'path': path,
            'depot': depot_node,
            'deliveries': deliveries,
        }

    return instances


def parse_vehicle_file(vehicle_xml_path: str, expected_type: str = None) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
    tree = _safe_parse_xml(vehicle_xml_path)
    root = tree.getroot()
    vehicle_ids: List[str] = []
    vehicle_attrs: Dict[str, Dict[str, Any]] = {}

    seen_ids = {}
    for info in root.findall('.//Info4Vehicle'):
        vehicle_type = info.get('Type', '').strip()
        if expected_type and vehicle_type != expected_type:
            continue

        raw_id = info.get('ID') or f"{vehicle_type}_{len(vehicle_ids) + 1}"
        count = seen_ids.get(raw_id, 0) + 1
        seen_ids[raw_id] = count
        vehicle_id = raw_id if count == 1 else f"{raw_id}_{count}"
        vehicle_ids.append(vehicle_id)
        def _float(name: str, default: float = 0.0) -> float:
            value = info.get(name)
            try:
                return float(value) if value is not None else default
            except ValueError:
                return default

        vehicle_attrs[vehicle_id] = {
            'Type': vehicle_type,
            'MaxSpeed': _float('MaxSpeed', 40.0),
            'Range': _float('Range', 100000.0),
            'BatteryCapacity': _float('BatteryCapacity', 0.0),
            'SoC': _float('SoC', 0.0),
            'MaximumLoadCapacityKg': _float('MaximumLoadCapacityKg', 0.0),
            # DÜZELTME (A7, 2026-08-22): bu iki alan v1.1 yeniden yazımında
            # yanlışlıkla düşürülmüştü; XML'de mevcut oldukları hâlde
            # okunmadıkları için CV modelinin yakıt tüketim oranı sabit
            # 1.0'a düşüyordu (bkz. prepare_cv_data_from_instance).
            'BatteryRechargingRate': _float('BatteryRechargingRate', 0.0),
            'EnergyConsumptionRate': _float('EnergyConsumptionRate', 0.0),
        }

    if not vehicle_ids:
        raise ValueError(f"No vehicles found in XML file: {vehicle_xml_path}")
    return vehicle_ids, vehicle_attrs


def parse_charging_stations(station_xml_path: str) -> List[Dict[str, Any]]:
    tree = _safe_parse_xml(station_xml_path)
    root = tree.getroot()
    stations: List[Dict[str, Any]] = []

    for station in root.findall('.//ChargingStation'):
        name = station.get('Name') or station.get('Id') or f"station_{len(stations) + 1}"
        location = station.find('Location')
        if location is None:
            continue
        lat, lon = _parse_location(location)
        stations.append({'id': str(name), 'lat': lat, 'lon': lon})

    return stations


def _build_node_index(depot: Dict[str, Any], deliveries: List[Dict[str, Any]], stations: List[Dict[str, Any]] = None):
    nodes = [depot] + deliveries
    if stations:
        nodes.extend(stations)
    index = {node['id']: idx for idx, node in enumerate(nodes)}
    return nodes, index


def _build_arcs(node_ids: List[int], station_ids: List[int] = None) -> List[Tuple[int, int]]:
    arcs = []
    for i in node_ids:
        for j in node_ids:
            if i != j:
                arcs.append((i, j))
    if station_ids is not None:
        for station in station_ids:
            for i in node_ids:
                if i != station:
                    arcs.append((i, station))
                    arcs.append((station, i))
    return list(dict.fromkeys(arcs))


def _build_distances_and_travel_times(nodes: List[Dict[str, Any]], arcs: List[Tuple[int, int]], speed_kmh: float):
    speeds = max(speed_kmh, 1.0) / 3.6
    d = {}
    tt = {}
    for i, j in arcs:
        lat_i, lon_i = nodes[i]['lat'], nodes[i]['lon']
        lat_j, lon_j = nodes[j]['lat'], nodes[j]['lon']
        distance_m = haversine(lat_i, lon_i, lat_j, lon_j)
        travel_time = distance_m / speeds
        d[(i, j)] = distance_m
        tt[(i, j)] = travel_time
    return d, tt


# ---------------------------------------------------------------------------
# R_max TÜRETİMİ (2026-08-24)
#
# Depo klon düğümü tasarımı (decisions/karar_klon_dugum_coklu_sefer_zaman_
# indeksleme_plani.md) R_max sabit 3 ile çalışıyordu; bu, klon yaylarını,
# u[r,k] değişkenlerini ve CV-29/30/31 (EV-28/29/30) kısıtlarını 3 kat
# büyütüyor ve RC13 gibi örneklerde dal-sınır ağacını gereksiz genişletiyordu
# (aynı sayfanın §13.2.1'i). Aşağıdaki iki fonksiyon R_max'ı VERİDEN türetir.
#
# KRİTİK: türetilen değer, en iyi (optimal) çözümü KESMEYEN, kanıtlanabilir
# bir ÜST SINIR olmak zorundadır. Bu yüzden yalnızca iki geçerli argüman
# kullanılır (ikisi de en iyimser senaryoyu varsayar):
#
#   (1) BİRLEŞTİRME BASKINLIĞI (merge dominance) — asıl sonuç veren argüman.
#       Aynı kaynağın ardışık iki seferi (… → i → depo → j → …) tek sefere
#       birleştirilirse (… → i → j → …):
#         • Amaç fonksiyonu KÖTÜLEŞMEZ: üçgen eşitsizliği gereği
#           d(i,j) <= d(i,0) + d(0,j) (haversine metriktir).
#         • Zaman fizibilitesi KORUNUR: mevcut tau değerleri aynen geçerlidir,
#           çünkü tau_i + st_i + tt(i,0) <= tau[E_r] <= tau[O_{r+1}] <=
#           tau_j - tt(0,j) ve tt(i,j) <= tt(i,0) + tt(0,j).
#         • Mola KORUNUR: mola kaldırılan yaylardan birindeyse yeni (i,j)
#           yayına taşınır; CV-10 (tau_i + st_i <= el) ve CV-12 (tau_j >= ll)
#           yukarıdaki zincirden aynen türer. Mola SAYISI değişmez, yani
#           CV-13 (<= z) / EV-12 (== z_veh) bozulmaz.
#         • CV-3/EV-3 (yay tekilliği) BOZULMAZ: i ve j müşteri düğümleriyse,
#           CV-2 gereği onları ziyaret eden tek kaynak zaten k'dir, dolayısıyla
#           (i,j) yayını başka kaynak kullanamaz. (Bir seferin ilk/son düğümü
#           bir ŞARJ İSTASYONU ise o düğüm w.l.o.g. rotadan atılabilir: depodan
#           tam şarjla çıkıp hemen şarj olmak veya şarj olup hemen depoya
#           dönmek mesafeyi artırır, zamanı uzatır.)
#         • TEK engel ENERJİdir: birleşen rota depoda yeniden dolum yapmaz
#           (CV-23/24, EV-24/25 yalnızca depodan çıkışta tam dolum verir).
#       Dolayısıyla: bir vardiyaya sığabilen HER rotanın uzunluğu araç
#       menzilinden küçükse, enerji hiçbir zaman bağlamaz ve HER optimal
#       çözüm, kaynak başına TEK sefere indirgenebilir  ⇒  R_max = 1.
#
#   (2) ZAMAN BÜTÇESİ — (1) geçmezse kullanılan yedek argüman.
#       Her sefer en az bir müşteri içerir (müşterisiz sefer amaç fonksiyonunu
#       kesin olarak kötüleştirir) ve müşteri j'yi içeren bir seferin süresi
#       en az f_j = tt(0,j) + st_j + tt(j,0)'dır (kapalı tur uzunluğu >= gidiş
#       + dönüş). Seferler CV-29 zinciriyle ardışık olduğundan ve seferlerin
#       müşteri kümeleri ayrık olduğundan, R sefer için "en küçük R adet f_j"
#       toplamı vardiya bütçesine sığmak zorundadır.
# ---------------------------------------------------------------------------


def max_single_trip_distance(
    d: Dict[Tuple[int, int], float],
    st: Dict[int, float],
    customers: List[int],
    speed_ms: float,
    time_budget: float,
    arc_count_exact: bool = True,
) -> float:
    """Bir vardiyaya sığabilen HERHANGİ bir tek seferlik rotanın uzunluğu için
    geçerli (kanıtlanabilir) bir ÜST SINIR döndürür (metre).

    Ziyaret edilen müşteri sayısı k üzerinden iki bağımsız üst sınırın
    kesişimi alınır ve k üzerinde maksimum alınır:

      (a) ZAMAN sınırı — rota süresi = seyahat + hizmet <= time_budget
          olduğundan seyahat süresi <= time_budget - (en küçük k hizmet
          süresinin toplamı); mesafe = hız x seyahat süresi.
      (b) YAY SAYISI sınırı — k müşterili bir rota TAM OLARAK k+1 yay
          kullanır ve yaylar birbirinden farklıdır, dolayısıyla uzunluk
          <= en uzun (k+1) yayın toplamı. Bu sınır yalnızca rotada
          müşteri ve depo dışında düğüm yoksa geçerlidir; bu yüzden EV
          (şarj istasyonlu) tarafında arc_count_exact=False verilir ve
          yalnızca (a) kullanılır.
    """
    if not customers or speed_ms <= 0.0 or time_budget <= 0.0:
        return 0.0

    service_sorted = sorted(float(st.get(j, 0.0)) for j in customers)
    arcs_sorted: List[float] = []
    if arc_count_exact:
        allowed = set(customers) | {0}
        arcs_sorted = sorted(
            (val for (i, j), val in d.items() if i in allowed and j in allowed),
            reverse=True,
        )

    best = 0.0
    acc_service = 0.0
    for k in range(1, len(customers) + 1):
        acc_service += service_sorted[k - 1]
        travel_time = time_budget - acc_service
        if travel_time <= 0.0:
            break                       # k müşteri hizmet süresi bile sığmıyor
        bound = speed_ms * travel_time
        if arc_count_exact:
            bound = min(bound, sum(arcs_sorted[:k + 1]))
        best = max(best, bound)
    return best


def derive_r_max(
    d: Dict[Tuple[int, int], float],
    tt: Dict[Tuple[int, int], float],
    st: Dict[int, float],
    C: List[int],
    es: Dict[Any, float],
    ls: Dict[Any, float],
    el: Dict[Any, float],
    ll: Dict[Any, float],
    speed_kmh: float,
    range_m: float,
    break_is_mandatory: bool = False,
    cap: int = 3,
    arc_count_exact: bool = True,
) -> Tuple[int, Dict[Any, int], Dict[str, Any]]:
    """Kaynak başına günlük maksimum sefer sayısı (R_max) için VERİDEN
    türetilmiş, optimal çözümü kesmeyen bir üst sınır hesaplar.

    Dönüş: (global_r_max, ekip_bazlı_r_max, teşhis_bilgisi)

    `cap` matematiksel modelin kendi üst sınırıdır (CV-4/EV-4: günde en fazla
    3 sefer); türetilen değer bunu ASLA aşmaz. Alt sınır 1'dir (R_max=0
    anlamsızdır: "hiç çıkma" seçeneği zaten z[k]=0 ile temsil edilir).
    """
    speed_ms = max(float(speed_kmh), 1.0) / 3.6
    techs = list(es.keys())
    by_tech: Dict[Any, int] = {}
    reasons: Dict[Any, str] = {}
    diag: Dict[str, Any] = {}

    for t in techs:
        horizon = float(ls[t]) - float(es[t])
        break_len = (float(ll[t]) - float(el[t])) if break_is_mandatory else 0.0
        # Mola ZORUNLU ise vardiya bütçesinden düşülür (mola bir yay üzerinde
        # [el, ll] penceresini işgal eder, bkz. CV-10/CV-12). OPSİYONEL ise
        # düşülmez: en iyimser (en uzun) senaryo molasız olandır.
        budget = max(0.0, horizon - break_len)

        # (1) BİRLEŞTİRME BASKINLIĞI — enerji hiç bağlamıyor mu?
        max_dist = max_single_trip_distance(d, st, C, speed_ms, budget, arc_count_exact)
        if range_m > 0.0 and max_dist <= range_m:
            by_tech[t] = 1
            reasons[t] = (f"birlestirme-baskinligi: vardiyaya sigan en uzun rota "
                          f"{max_dist:.0f} m <= menzil {range_m:.0f} m")
            diag.setdefault('max_route_distance', max_dist)
            continue

        # (2) ZAMAN BÜTÇESİ — en küçük R adet tek-müşteri sefer alt sınırı.
        f_sorted = sorted(
            float(tt.get((0, j), 0.0)) + float(st.get(j, 0.0)) + float(tt.get((j, 0), 0.0))
            for j in C
        )
        fitted = 0
        acc = 0.0
        for val in f_sorted[:cap]:
            if val <= 0.0:
                fitted = cap
                break
            if acc + val <= budget:
                acc += val
                fitted += 1
            else:
                break
        by_tech[t] = max(1, min(cap, fitted, len(C) or 1))
        reasons[t] = (f"zaman-butcesi: butce {budget:.0f} s, en kucuk {cap} sefer "
                      f"alt siniri {f_sorted[:cap]}")
        diag.setdefault('max_route_distance', max_dist)

    r_max = max(by_tech.values()) if by_tech else cap
    diag.update({
        'cap': cap,
        'range_m': range_m,
        'speed_ms': speed_ms,
        'break_is_mandatory': break_is_mandatory,
        'arc_count_exact': arc_count_exact,
        'reasons': reasons,
        'r_max': r_max,
    })
    return r_max, by_tech, diag


def prepare_cv_data_from_instance(
    instance: Dict[str, Any],
    vehicle_ids: List[str],
    vehicle_attrs: Dict[str, Dict[str, Any]],
    technicians: List[str] = None,
    es_val: float = 0.0,
    ls_val: float = 32400.0,
    el_val: float = 14400.0,
    ll_val: float = 21600.0,
) -> Dict[str, Any]:
    if technicians is None:
        technicians = ['tech1']

    depot = instance['depot']
    deliveries = instance['deliveries']
    nodes, index = _build_node_index(depot, deliveries)
    node_ids = list(range(len(nodes)))
    arcs = _build_arcs(node_ids)
    speed = vehicle_attrs[vehicle_ids[0]]['MaxSpeed']
    d, tt = _build_distances_and_travel_times(nodes, arcs, speed)

    st = {idx: nodes[idx]['service_time'] for idx in node_ids}
    ec = {idx: nodes[idx]['ready_time'] for idx in node_ids}
    lc = {idx: nodes[idx]['due_date'] for idx in node_ids}
    C = [index[delivery['id']] for delivery in deliveries]
    N0 = node_ids
    N = N0[:]
    A = arcs
    Ti = {c: technicians[:] for c in C}
    G = {v: vehicle_attrs[v]['Range'] for v in vehicle_ids}

    # DÜZELTME (A7, 2026-08-22): h_c (mesafe başına yakıt tüketim oranı)
    # artık XML'deki EnergyConsumptionRate niteliğinden okunuyor.
    # Önceki hâli sabit 1.0 idi; G[v]=Range=6000 ile birleşince CV
    # rotalarını sefer başına fiilen ~6 km ile sınırlıyordu (gerçek değer
    # 0.055 ile menzil 6000/0.055 ≈ 109 km olur). EV tarafındaki
    # h_e = BatteryCapacity/Range deseniyle tutarlıdır
    # (FC_Info4Vehicle4CV.xml: EnergyConsumptionRate="0.055", Range="6000").
    # Bkz. decisions/karar_a7_cv_yakit_tuketim_orani_duzeltmesi.md.
    ref_v = vehicle_ids[0] if vehicle_ids else None
    h_c = float(vehicle_attrs.get(ref_v, {}).get('EnergyConsumptionRate', 0.0) or 0.0) if ref_v else 0.0
    if h_c <= 0.0:
        # XML'de oran tanımlı değilse eski davranışa geri düş.
        h_c = 1.0
    # NOT: heterojen filo (araç bazlı h_c) desteği bilinçli olarak
    # eklenmemiştir — CV_model_gurobi_exact.build_model tek bir skaler
    # h_c parametresi alır ve data sözlüğü ona **kwargs olarak geçirilir;
    # fazladan bir anahtar TypeError üretir. Filo şu an homojendir
    # (üç CV de EnergyConsumptionRate="0.055").
    # CV'de yol ortasında yakıt ikmali modellenmiyor (CV-22: YC[i]==yc[i]),
    # bu yüzden g_c'nin çözüme etkisi yoktur; imza uyumluluğu için taşınır.
    refuel_rate = float(vehicle_attrs.get(ref_v, {}).get('BatteryRechargingRate', 0.0) or 0.0) if ref_v else 0.0
    g_c = (1.0 / refuel_rate) if refuel_rate > 0.0 else 1.0

    es_map = {t: es_val for t in technicians}
    ls_map = {t: ls_val for t in technicians}
    el_map = {t: el_val for t in technicians}
    ll_map = {t: ll_val for t in technicians}

    # R_max TÜRETİMİ (2026-08-24). CV'de:
    #  * menzil = G[v] / h_c  (yakıt kapasitesi / mesafe başına tüketim),
    #    filo heterojen olabileceği için EN KÜÇÜK menzil alınır;
    #  * mola OPSİYONELDİR (CV-13: Σw <= z), bu yüzden vardiya bütçesinden
    #    düşülmez (en iyimser senaryo molasızdır);
    #  * CV düğüm kümesinde şarj/yakıt istasyonu düğümü YOKTUR
    #    (_build_node_index istasyonsuz çağrılır), dolayısıyla k müşterili
    #    bir rota tam olarak k+1 yay kullanır → arc_count_exact=True.
    cv_range = (min(G.values()) / h_c) if (G and h_c > 0.0) else 0.0
    r_max, r_max_by_tech, r_max_info = derive_r_max(
        d, tt, st, C, es_map, ls_map, el_map, ll_map,
        speed_kmh=speed, range_m=cv_range,
        break_is_mandatory=False, cap=3, arc_count_exact=True,
    )

    return {
        'N': N,
        'N0': N0,
        'C': C,
        'Vc': vehicle_ids,
        'V': vehicle_ids,
        'T': technicians,
        'Ti': Ti,
        'Fc': [0],
        'A': A,
        'd': d,
        'tt': tt,
        'st': st,
        'G': G,
        'ec': ec,
        'lc': lc,
        'es': es_map,
        'ls': ls_map,
        'el': el_map,
        'll': ll_map,
        'h_c': h_c,
        'g_c': g_c,
        'k': {idx: 1 for idx in C},
        'lc0': 10000.0,
        'node_labels': {idx: nodes[idx]['label'] for idx in node_ids},
        # bkz. derive_r_max: sabit 3 yerine veriden türetilmiş üst sınır.
        'R_max': r_max,
        'R_max_by_tech': r_max_by_tech,
        'R_max_info': r_max_info,
    }


def prepare_ev_data_from_instance(
    instance: Dict[str, Any],
    vehicle_ids: List[str],
    vehicle_attrs: Dict[str, Dict[str, Any]],
    charging_stations: List[Dict[str, Any]],
    technicians: List[str] = None,
    es_val: float = 0.0,
    ls_val: float = 32400.0,
    el_val: float = 14400.0,
    ll_val: float = 21600.0,
    charging_power_w: float = 22000.0,
) -> Dict[str, Any]:
    if technicians is None:
        technicians = ['tech1']

    depot = instance['depot']
    deliveries = instance['deliveries']
    speed = vehicle_attrs[vehicle_ids[0]]['MaxSpeed']

    # Ö6 (2026-08-28, sorun_rc13_darbogaz_kok_neden_analizi.md): İSTASYONSUZ
    # ÖN-TEST. Şarj istasyonu düğümleri, DFJ/altur-eleme kesitlerinin
    # göremediği bir "kaçış yolu" açarak LP gevşetmesini zayıflatıyor
    # (RC13'te |At| %40 büyüyor, kök LP 13203.7 -> 14885.8 düşüyor).
    # `derive_r_max`'ın zaten kanıtladığı "birleştirme baskınlığı" testiyle
    # AYNI argüman: vardiyaya sığan en uzun tek seferlik rota, istasyon HİÇ
    # kullanılmadan bile araç menzilinin altındaysa, enerji hiçbir zaman
    # bağlamaz ve istasyon düğümü hiçbir optimal çözümde gerekmez — bu
    # durumda istasyonlar modelden TAMAMEN çıkarılır (S=[]), CV ile aynı
    # istasyonsuz yapıya döner. Test, olası istasyon menzil ARTIŞINI
    # hesaba katmadığı için (istasyonsuz menzil <= gerçek menzil) muhafazakar
    # taraftadır — güvenli. Enerji GERÇEKTEN bağlıyorsa (test geçmezse)
    # istasyonlar normal şekilde eklenir; davranış veri-bağımlıdır, sabit bir
    # "istasyon hiç yok" kuralı DEĞİLDİR.
    _probe_nodes, _probe_index = _build_node_index(depot, deliveries)
    _probe_node_ids = list(range(len(_probe_nodes)))
    _probe_arcs = _build_arcs(_probe_node_ids)
    _probe_d, _probe_tt = _build_distances_and_travel_times(_probe_nodes, _probe_arcs, speed)
    _probe_st = {idx: _probe_nodes[idx]['service_time'] for idx in _probe_node_ids}
    _probe_C = [_probe_index[delivery['id']] for delivery in deliveries]
    _probe_es = {t: es_val for t in technicians}
    _probe_ls = {t: ls_val for t in technicians}
    _probe_el = {t: el_val for t in technicians}
    _probe_ll = {t: ll_val for t in technicians}
    _probe_Q = {v: vehicle_attrs[v]['BatteryCapacity'] or 50000.0 for v in vehicle_ids}
    _probe_ref = vehicle_attrs[vehicle_ids[0]]
    _probe_h_e = (_probe_ref['BatteryCapacity'] or 50000.0) / (_probe_ref['Range'] or 322000.0)
    _probe_range = (min(_probe_Q.values()) / _probe_h_e) if (_probe_Q and _probe_h_e > 0.0) else 0.0
    _, _, _probe_info = derive_r_max(
        _probe_d, _probe_tt, _probe_st, _probe_C, _probe_es, _probe_ls, _probe_el, _probe_ll,
        speed_kmh=speed, range_m=_probe_range,
        break_is_mandatory=True, cap=3, arc_count_exact=False,
    )
    stations_dropped = (
        _probe_range > 0.0
        and _probe_info.get('max_route_distance', float('inf')) <= _probe_range
    )
    stations_to_use = [] if stations_dropped else charging_stations

    nodes, index = _build_node_index(depot, deliveries, stations_to_use)
    node_ids = list(range(len(nodes)))
    station_ids = [index[s['id']] for s in stations_to_use if s['id'] in index]
    arcs = _build_arcs(node_ids, station_ids)
    d, tt = _build_distances_and_travel_times(nodes, arcs, speed)

    st = {idx: nodes[idx]['service_time'] if idx < len(deliveries) + 1 else 0.0 for idx in node_ids}
    ec = {idx: nodes[idx]['ready_time'] if idx < len(deliveries) + 1 else 0.0 for idx in node_ids}
    lc = {idx: nodes[idx]['due_date'] if idx < len(deliveries) + 1 else 100000.0 for idx in node_ids}
    C = [index[delivery['id']] for delivery in deliveries]
    N = node_ids
    Np = node_ids
    S = station_ids
    B = [0]
    Ti = {i: technicians[:] for i in node_ids}
    tt_0i = {i: tt[(0, i)] if (0, i) in tt else 0.0 for i in node_ids}
    tt_i0 = {i: tt[(i, 0)] if (i, 0) in tt else 0.0 for i in node_ids}
    tt_s0 = {s: tt[(s, 0)] if (s, 0) in tt else 0.0 for s in station_ids}
    # NOT: Q, EV'nin batarya kapasitesidir; önceki sürümde yanlışlıkla
    # 'MaximumLoadCapacityKg' (kargo yükü, veri setinde -1.0 = tanımsız)
    # alanından okunuyordu ve bu negatif değer modeli infeasible yapıyordu.
    # Doğrusu 'BatteryCapacity' alanıdır (bkz. FC_Info4Vehicle4EV.xml).
    Q = {v: vehicle_attrs[v]['BatteryCapacity'] or 50000.0 for v in vehicle_ids}

    # h_e (enerji tüketim oranı, Wh/m) ve g_e (şarj oranı, s/Wh) önceki
    # sürümde 0.0 (yer tutucu) idi; bu, enerji kısıtlarını fiilen devre
    # dışı bırakıyordu. Makale taslağının 3.2 Varsayımlar bölümünde
    # belirtilen Fiat E-Doblo Cargo teknik verilerinden (50 kWh batarya,
    # 322 km menzil) türetilmiştir: h_e = BatteryCapacity / Range.
    # ŞARJ GÜCÜ VARSAYIMI: makale taslağında bir şarj istasyonu gücü
    # belirtilmediğinden, ticari hafif ticari araçlar için tipik bir AC
    # hızlı şarj gücü olan 22 kW varsayılmıştır (charging_power_w
    # parametresiyle geçersiz kılınabilir); gerçek istasyon gücü
    # biliniyorsa bu değer güncellenmelidir.
    ref_vehicle = vehicle_attrs[vehicle_ids[0]]
    battery_capacity_wh = ref_vehicle['BatteryCapacity'] or 50000.0
    range_m = ref_vehicle['Range'] or 322000.0
    h_e = battery_capacity_wh / range_m
    g_e = 3600.0 / charging_power_w

    es_map = {t: es_val for t in technicians}
    ls_map = {t: ls_val for t in technicians}
    el_map = {t: el_val for t in technicians}
    ll_map = {t: ll_val for t in technicians}

    # R_max TÜRETİMİ (2026-08-24). EV'de CV'den üç farkla:
    #  * menzil = Q[v] / h_e (batarya / tüketim oranı) — istasyon ziyareti
    #    menzili yalnızca ARTIRIR, dolayısıyla "istasyonsuz menzil"i üst sınır
    #    testinde kullanmak GÜVENLİ (daha muhafazakâr) tarafta kalır;
    #  * mola ZORUNLUDUR (EV-12: Σw == z_veh), bu yüzden (ll-el) vardiya
    #    bütçesinden düşülür — bu, testin geçmesini sağlayan kritik terimdir
    #    (37.5 km/sa x 32400 s = 337.5 km > 322 km menzil iken,
    #     37.5 km/sa x 25200 s = 262.5 km <= 322 km);
    #  * düğüm kümesinde ŞARJ İSTASYONLARI vardır, dolayısıyla k müşterili bir
    #    rotanın yay sayısı k+1 OLMAYABİLİR → arc_count_exact=False (yalnızca
    #    zaman tabanlı mesafe sınırı kullanılır, yay sayımı devre dışı).
    ev_range = (min(Q.values()) / h_e) if (Q and h_e > 0.0) else 0.0
    r_max, r_max_by_tech, r_max_info = derive_r_max(
        d, tt, st, C, es_map, ls_map, el_map, ll_map,
        speed_kmh=speed, range_m=ev_range,
        break_is_mandatory=True, cap=3, arc_count_exact=False,
    )

    return {
        'N': N,
        'N_prime': Np,
        'C': C,
        'V': vehicle_ids,
        'T': technicians,
        'S': S,
        'B': B,
        'A': arcs,
        'T_i': Ti,
        'd': d,
        'tt': tt,
        'tt_0i': tt_0i,
        'tt_i0': tt_i0,
        'tt_s0': tt_s0,
        'st': st,
        'Q': Q,
        'ec': ec,
        'lc': lc,
        'lc_0': 10000.0,
        'es': es_map,
        'ls': ls_map,
        'el': el_map,
        'll': ll_map,
        # bkz. derive_r_max: sabit 3 yerine veriden türetilmiş üst sınır.
        'R_max': r_max,
        'R_max_by_tech': r_max_by_tech,
        'R_max_info': r_max_info,
        # Ö6: enerji hiç bağlamadığı için istasyonlar modelden çıkarıldı mı?
        'stations_dropped': stations_dropped,
        # NOT: şarj istasyonu düğümlerinde (parse_charging_stations'tan
        # gelen) 'label' anahtarı yok, sadece 'id' var; bu yüzden .get()
        # ile güvenli bir düşüş (fallback) sırası kullanılmıştır.
        'node_labels': {idx: nodes[idx].get('label', nodes[idx].get('id', str(idx))) for idx in node_ids},
        'h_e': h_e,
        'g_e': g_e,
        'a_max': 10000.0,
        'v_vb': {(v, b): 1.0 for v in vehicle_ids for b in B},
    }
