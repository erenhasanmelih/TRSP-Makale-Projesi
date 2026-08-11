import glob
import math
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Any

# Kaynak: raw/xml_data_loader.py - Faz 2 duzeltmesi (A7) uygulanmistir; ayrica
# A2 (heterojen filo) icin arac bazli tuketim orani sozlukleri (h_c_v / h_e_v) eklenmistir.


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

    # --- A7 duzeltmesi: CV yakit tuketim orani artik XML'den okunuyor ---
    # Onceki hali: 'h_c': 1.0 sabiti (bkz. raw/xml_data_loader.py satir 266).
    # Sabit 1.0, G[v]=Range (6000 m) ile birlestiginde CV rotalarini fiilen ~6 km ile
    # sinirliyordu. EV tarafindaki desen (satir 322-325) ile ayni sekilde
    # EnergyConsumptionRate attribute'undan okunur (FC_Info4Vehicle4CV.xml: 0.055).
    ref_v = vehicle_ids[0] if vehicle_ids else None
    h_c = float(vehicle_attrs.get(ref_v, {}).get('EnergyConsumptionRate', 0.0)) if ref_v else 0.0
    if h_c <= 0.0:
        # XML'de oran tanimli degilse eski davranisa geri dus (geriye donuk uyumluluk).
        h_c = 1.0
    # Heterojen filo destegi icin arac bazli tuketim orani (A2 refaktoru kullanir).
    h_c_v = {}
    for v in vehicle_ids:
        rate = float(vehicle_attrs.get(v, {}).get('EnergyConsumptionRate', 0.0) or 0.0)
        h_c_v[v] = rate if rate > 0.0 else h_c
    # CV'de yakit ikmali modellenmiyor; g_c yalnizca imza uyumlulugu icin tasiniyor.
    refuel_rate = float(vehicle_attrs.get(ref_v, {}).get('BatteryRechargingRate', 0.0)) if ref_v else 0.0
    g_c = (1.0 / refuel_rate) if refuel_rate > 0.0 else 1.0

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
        'es': {t: es_val for t in technicians},
        'ls': {t: ls_val for t in technicians},
        'el': {t: el_val for t in technicians},
        'll': {t: ll_val for t in technicians},
        'h_c': h_c,
        'h_c_v': h_c_v,
        'g_c': g_c,
        'k': {idx: 1 for idx in C},
        'lc0': 10000.0,
        'node_labels': {idx: nodes[idx]['label'] for idx in node_ids},
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
) -> Dict[str, Any]:
    if technicians is None:
        technicians = ['tech1']

    depot = instance['depot']
    deliveries = instance['deliveries']
    nodes, index = _build_node_index(depot, deliveries, charging_stations)
    node_ids = list(range(len(nodes)))
    station_ids = [index[s['id']] for s in charging_stations if s['id'] in index]
    arcs = _build_arcs(node_ids, station_ids)
    speed = vehicle_attrs[vehicle_ids[0]]['MaxSpeed']
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
    # EV model energy capacity Q must represent battery energy/capacity, not payload.
    Q = {}
    for v in vehicle_ids:
        attrs = vehicle_attrs[v]
        qv = float(attrs.get('BatteryCapacity', 0.0) or 0.0)
        if qv <= 0.0:
            qv = float(attrs.get('SoC', 0.0) or 0.0)
        if qv <= 0.0:
            qv = float(attrs.get('Range', 0.0) or 0.0)
        if qv <= 0.0:
            qv = 1000.0
        Q[v] = qv

    ref_v = vehicle_ids[0] if vehicle_ids else None
    h_e = float(vehicle_attrs.get(ref_v, {}).get('EnergyConsumptionRate', 0.0)) if ref_v else 0.0
    recharge_rate = float(vehicle_attrs.get(ref_v, {}).get('BatteryRechargingRate', 0.0)) if ref_v else 0.0
    g_e = (1.0 / recharge_rate) if recharge_rate > 0.0 else 0.0
    # Heterojen filo destegi icin arac bazli tuketim orani (A2 refaktoru kullanir).
    h_e_v = {}
    for v in vehicle_ids:
        rate = float(vehicle_attrs.get(v, {}).get('EnergyConsumptionRate', 0.0) or 0.0)
        h_e_v[v] = rate if rate > 0.0 else h_e

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
        'es': {t: es_val for t in technicians},
        'ls': {t: ls_val for t in technicians},
        'el': {t: el_val for t in technicians},
        'll': {t: ll_val for t in technicians},
        'h_e': h_e,
        'h_e_v': h_e_v,
        'g_e': g_e,
        'a_max': 10000.0,
        'v_vb': {(v, b): 1.0 for v in vehicle_ids for b in B},
    }
