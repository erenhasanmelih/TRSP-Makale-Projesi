import os
import itertools
import io
import sys
from contextlib import redirect_stdout
import gurobipy as gp
from gurobipy import GRB
import xml.etree.ElementTree as ET
from xml_data_loader import (
    load_problem_instances,
    parse_vehicle_file,
    parse_charging_stations,
    prepare_ev_data_from_instance,
)

ENABLE_PAIR_CREWS = True
FEASIBILITY_FOCUSED_PARAMS = True
NOREL_HEUR_TIME_CAP = 20
MAX_ROUTES_PER_VEHICLE = None  # None: unbounded by this rule, int: explicit cap
TEST_BATTERY_SCALE = 0.005  # Test icin kapasiteyi dusurmek isterseniz < 1.0 kullanin.

try:
    from docx import Document
except ImportError:
    Document = None

class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()


def write_output_docx(docx_path: str, text: str):
    if Document is None:
        raise RuntimeError(
            "python-docx kurulu degil. Lutfen once `pip install python-docx` calistirin."
        )
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(docx_path)

def build_model(data):
    m = gp.Model("EV_v1_1_exact_model")

    # Sets (EV naming aligned with EV_model_gurobi_exact.py)
    N = data["N"]
    Np = data["N_prime"]
    C = data["C"]
    S = data.get("S", [])
    V = data["V"]
    T = data["T"]
    Ti = data["T_i"] if "T_i" in data else data["Ti"]
    A = data["A"]
    crew_members = data.get("crew_members", {})

    # Parameters
    d = data["d"]
    tt = data["tt"]
    st = data["st"]
    Q = data["Q"]
    ec = data["ec"]
    lc = data["lc"]
    es = data["es"]
    ls = data["ls"]
    el = data["el"]
    ll = data["ll"]
    h_e = data["h_e"]
    g_e = data["g_e"]
    lc0 = data["lc_0"] if "lc_0" in data else data.get("lc0", 100000.0)
    energy_big_m = max(float(q) for q in Q.values()) if Q else 100000.0

    # Decision variables
    x = m.addVars(A, V, T, vtype=GRB.BINARY, name="x")
    tau = m.addVars(Np, T, lb=0.0, vtype=GRB.CONTINUOUS, name="tau")
    L = m.addVars(Np, T, lb=0.0, vtype=GRB.CONTINUOUS, name="L")
    YE = m.addVars(Np, V, T, lb=0.0, vtype=GRB.CONTINUOUS, name="YE")
    ye = m.addVars(Np, V, T, lb=0.0, vtype=GRB.CONTINUOUS, name="ye")
    w = m.addVars(A, T, vtype=GRB.BINARY, name="w")
    y_route = m.addVars(T, vtype=GRB.BINARY, name="y_route")
    S_set = set(S)

    # Save for output
    m._x = x
    m._tau = tau
    m._w = w
    m._A = A
    m._V = V
    m._T = T
    m._YE = YE
    m._ye = ye
    m._S = S_set
    m._Q = Q
    m._h_e = h_e
    m._g_e = g_e

    # Objective
    m.setObjective(
        gp.quicksum(d[i, j] * x[i, j, v, t] for (i, j) in A for v in V for t in T),
        GRB.MINIMIZE,
    )

    # Same mathematical constraints, EV notation only
    for j in C:
        m.addConstr(
            gp.quicksum(x[i, j, v, t] for i in Np for v in V for t in Ti[j] if (i, j) in A) == 1,
            name=f"c2_{j}",
        )

    for i, j in A:
        m.addConstr(gp.quicksum(x[i, j, v, t] for v in V for t in T) <= 1, name=f"c3_{i}_{j}")

    if MAX_ROUTES_PER_VEHICLE is not None:
        for v in V:
            m.addConstr(
                gp.quicksum(x[0, j, v, t] for j in Np for t in T if (0, j) in A) <= MAX_ROUTES_PER_VEHICLE,
                name=f"c4_{v}",
            )

    for t in T:
        depart_t = gp.quicksum(x[0, j, v, t] for j in Np for v in V if (0, j) in A)
        m.addConstr(depart_t <= 1, name=f"c5_{t}")
        m.addConstr(y_route[t] == depart_t, name=f"c5_link_{t}")

    for i in Np:
        for v in V:
            for t in T:
                m.addConstr(
                    gp.quicksum(x[i, j, v, t] for j in Np if (i, j) in A)
                    - gp.quicksum(x[j, i, v, t] for j in Np if (j, i) in A)
                    == 0,
                    name=f"c6_{i}_{v}_{t}",
                )

    break_duration = 3600
    break_min = 13800
    break_max = 15000

    for i, j in A:
        if j == 0:
            continue
        for v in V:
            for t in T:
                charge_time_i = g_e * (YE[i, v, t] - ye[i, v, t]) if i in S_set else 0.0
                m.addConstr(
                    tau[i, t]
                    + st.get(i, 0.0)
                    + w[i, j, t] * break_duration
                    + charge_time_i
                    + tt[i, j] * x[i, j, v, t]
                    - 100000.0 * (1 - x[i, j, v, t])
                    <= tau[j, t],
                    name=f"c8_zaman_ilerleme_{i}_{j}_{v}_{t}",
                )

    for t in T:
        sum_w = gp.quicksum(w[i, j, t] for (i, j) in A)

        m.addConstr(
            sum_w <= gp.quicksum(x[0, i, v, t] for i in Np for v in V if (0, i) in A),
            name=f"mola_max1_{t}",
        )

        for i in Np:
            if i == 0:
                continue
            for v in V:
                if (i, 0) in A:
                    m.addConstr(
                        tau[i, t] + st.get(i, 0.0) + tt.get((i, 0), 0.0)
                        <= break_max + 100000.0 * (1 - x[i, 0, v, t] + sum_w),
                        name=f"mola_yoksa_erken_donus_{i}_{v}_{t}",
                    )

    for i, j in A:
        for t in T:
            m.addConstr(
                w[i, j, t] <= gp.quicksum(x[i, j, v, t] for v in V),
                name=f"mola_yol_ustu_onayi_{i}_{j}_{t}",
            )

            m.addConstr(
                tau[i, t] + st.get(i, 0.0) >= break_min - 100000.0 * (1 - w[i, j, t]),
                name=f"mola_baslama_alt_sinir_{i}_{j}_{t}",
            )
            m.addConstr(
                tau[i, t] + st.get(i, 0.0) <= break_max + 100000.0 * (1 - w[i, j, t]),
                name=f"mola_baslama_ust_sinir_{i}_{j}_{t}",
            )

    for i in C:
        for t in T:
            if (0, i) in tt:
                m.addConstr(tau[i, t] - tt[0, i] >= es[t], name=f"c16_{i}_{t}")

    for i in C:
        for t in T:
            if (i, 0) in A and (i, 0) in tt:
                m.addConstr(
                    tau[i, t] + st.get(i, 0.0) + tt.get((i, 0), 0.0) + w[i, 0, t] * break_duration <= ls[t],
                    name=f"c17_{i}_{t}",
                )

    # Technician overlap prevention:
    # A technician may appear in multiple crews, but those crews cannot run simultaneously.
    if crew_members:
        horizon_end = 0.0
        if ls:
            horizon_end = max(float(vv) for vv in ls.values())
        if lc:
            horizon_end = max(horizon_end, max(float(vv) for vv in lc.values()))
        if horizon_end <= 0.0:
            horizon_end = 100000.0
        nonoverlap_M = horizon_end + break_duration

        route_start = m.addVars(T, lb=0.0, ub=horizon_end, vtype=GRB.CONTINUOUS, name="route_start")
        route_end = m.addVars(T, lb=0.0, ub=horizon_end + break_duration, vtype=GRB.CONTINUOUS, name="route_end")

        for t in T:
            m.addConstr(route_start[t] <= horizon_end * y_route[t], name=f"route_start_gate_{t}")
            m.addConstr(route_end[t] <= (horizon_end + break_duration) * y_route[t], name=f"route_end_gate_{t}")
            m.addConstr(route_end[t] >= route_start[t], name=f"route_seq_{t}")

            # Link route_start to chosen departure arc.
            for j in Np:
                if j == 0:
                    continue
                if (0, j) not in tt:
                    continue
                for v in V:
                    if (0, j) in A:
                        expr_dep = tau[j, t] - tt[0, j]
                        m.addConstr(
                            route_start[t] >= expr_dep - nonoverlap_M * (1 - x[0, j, v, t]),
                            name=f"route_start_lb_{t}_{v}_{j}",
                        )
                        m.addConstr(
                            route_start[t] <= expr_dep + nonoverlap_M * (1 - x[0, j, v, t]),
                            name=f"route_start_ub_{t}_{v}_{j}",
                        )

            # Link route_end to chosen return arc.
            for i in Np:
                if i == 0:
                    continue
                if (i, 0) not in tt:
                    continue
                for v in V:
                    if (i, 0) in A:
                        extra_charge = g_e * (YE[i, v, t] - ye[i, v, t]) if i in S_set else 0.0
                        expr_ret = tau[i, t] + st.get(i, 0.0) + tt[i, 0] + break_duration * w[i, 0, t] + extra_charge
                        m.addConstr(
                            route_end[t] >= expr_ret - nonoverlap_M * (1 - x[i, 0, v, t]),
                            name=f"route_end_lb_{t}_{v}_{i}",
                        )
                        m.addConstr(
                            route_end[t] <= expr_ret + nonoverlap_M * (1 - x[i, 0, v, t]),
                            name=f"route_end_ub_{t}_{v}_{i}",
                        )

        tech_to_crews = {}
        for crew, members in crew_members.items():
            for tech in members:
                tech_to_crews.setdefault(tech, []).append(crew)

        for tech, crews in tech_to_crews.items():
            valid_crews = [c for c in crews if c in T]
            for c1, c2 in itertools.combinations(valid_crews, 2):
                order = m.addVar(vtype=GRB.BINARY, name=f"ord_{tech}_{c1}_{c2}")
                inactive_relax = nonoverlap_M * (2 - y_route[c1] - y_route[c2])
                m.addConstr(
                    route_start[c2] >= route_end[c1] - nonoverlap_M * (1 - order) - inactive_relax,
                    name=f"noov_1_{tech}_{c1}_{c2}",
                )
                m.addConstr(
                    route_start[c1] >= route_end[c2] - nonoverlap_M * order - inactive_relax,
                    name=f"noov_2_{tech}_{c1}_{c2}",
                )

    for i in C:
        for t in T:
            m.addConstr(ec[i] <= tau[i, t], name=f"c18_lb_{i}_{t}")
            m.addConstr(tau[i, t] <= lc[i], name=f"c18_ub_{i}_{t}")

    return m

    # Energy tracking (same math as fuel block)
    for i, j in A:
        if i == 0 or j == 0:
            continue
        for v in V:
            for t in T:
                m.addConstr(ye[j, v, t] >= 0, name=f"c20_lb_{i}_{j}_{v}_{t}")
                m.addConstr(
                    ye[j, v, t] <= ye[i, v, t] - (h_e * d[i, j]) * x[i, j, v, t] + energy_big_m * (1 - x[i, j, v, t]),
                    name=f"c20_ub_{i}_{j}_{v}_{t}",
                )

    for i, j in A:
        if i == 0 or j == 0:
            continue
        for v in V:
            for t in T:
                m.addConstr(ye[j, v, t] >= 0, name=f"c21_lb_{i}_{j}_{v}_{t}")
                m.addConstr(
                    ye[j, v, t] <= YE[i, v, t] - (h_e * d[i, j]) * x[i, j, v, t] + energy_big_m * (1 - x[i, j, v, t]),
                    name=f"c21_ub_{i}_{j}_{v}_{t}",
                )

    for i in Np:
        if i == 0:
            continue
        for v in V:
            for t in T:
                if i in S_set:
                    # At charging stations, departure energy can be higher than arrival energy.
                    m.addConstr(YE[i, v, t] >= ye[i, v, t], name=f"c22_station_recharge_lb_{i}_{v}_{t}")
                else:
                    m.addConstr(YE[i, v, t] == ye[i, v, t], name=f"c22_no_recharge_{i}_{v}_{t}")
                m.addConstr(YE[i, v, t] <= Q[v], name=f"c22_ub_{i}_{v}_{t}")

    if S_set:
        max_q = max(float(Q[v]) for v in V) if V else 0.0
        for s in S_set:
            for v in V:
                for t in T:
                    outflow_s_vt = gp.quicksum(
                        x[s, j, v, t]
                        for j in Np
                        if (s, j) in A
                    )
                    m.addConstr(
                        YE[s, v, t] - ye[s, v, t] <= max_q * outflow_s_vt,
                        name=f"c22_station_recharge_bigM_{s}_{v}_{t}",
                    )

    for i in Np:
        if i == 0:
            continue
        for v in V:
            for t in T:
                if (i, 0) in A:
                    m.addConstr(
                        ye[i, v, t] >= (h_e * d.get((i, 0), 0.0)) * x[i, 0, v, t],
                        name=f"c_return_energy_{i}_{v}_{t}",
                    )

    for j in Np:
        if j == 0:
            continue
        for v in V:
            for t in T:
                if (0, j) in A:
                    m.addConstr(
                        ye[j, v, t] <= Q[v] - (h_e * d.get((0, j), 0.0)) * x[0, j, v, t] + 100000.0 * (1 - x[0, j, v, t]),
                        name=f"c_full_depot_ub_{j}_{v}_{t}",
                    )
                    m.addConstr(
                        ye[j, v, t] >= Q[v] - (h_e * d.get((0, j), 0.0)) - 100000.0 * (1 - x[0, j, v, t]),
                        name=f"c_full_depot_lb_{j}_{v}_{t}",
                    )

    return m


def format_time(seconds: float) -> str:
    if seconds is None:
        return "--:--"
    seconds = max(0, round(seconds))
    shifted_seconds = seconds + 28800
    h = (shifted_seconds // 3600) % 24
    m = (shifted_seconds % 3600) // 60
    return f"{h:02d}:{m:02d}"


def print_ev_solution(data, model):
    if model.SolCount == 0:
        print("Cozum yok veya uygun degil.")
        return

    x = model._x
    tau = model._tau
    w_vars = model._w
    YE = getattr(model, "_YE", None)
    ye = getattr(model, "_ye", None)
    S_set = set(getattr(model, "_S", data.get("S", [])))
    C_set = set(data.get("C", []))
    Q_map = getattr(model, "_Q", data.get("Q", {}))
    h_e = float(getattr(model, "_h_e", data.get("h_e", 0.0)))
    g_e = float(getattr(model, "_g_e", data.get("g_e", 0.0)))
    d = data["d"]
    tt = data["tt"]
    st = data["st"]
    node_labels = data.get("node_labels", {})

    def charge_amount(node, veh, crew):
        key = (node, veh, crew)
        if node in S_set and YE is not None and ye is not None and key in YE and key in ye:
            return max(0.0, float(YE[key].X - ye[key].X))
        return 0.0

    routes = {}
    for (i, j, v, t), var in x.items():
        if var.X > 0.5:
            routes.setdefault((v, t), []).append((i, j))

    print("\n" + "=" * 98)
    print("EV GUNLUK OPERASYON OZETI")
    print("=" * 98)

    for (v, t), arcs in sorted(routes.items()):
        next_map = {i: j for i, j in arcs}
        route = [0]
        current = 0
        visited = set()
        while current in next_map and current not in visited:
            visited.add(current)
            current = next_map[current]
            route.append(current)

        if len(route) <= 1:
            continue

        total_distance = sum(d.get((route[idx], route[idx + 1]), 0.0) for idx in range(len(route) - 1))
        if "__" in t:
            ekip_isimleri = " + ".join(t.split("__"))
        else:
            ekip_isimleri = t

        print(f"[EV] {v} | Ekip: {ekip_isimleri}")
        print(
            f"Mesafe: {total_distance:.1f} m | Kapasite: {float(Q_map.get(v, 0.0)):.2f} | "
            f"Tuketim katsayisi (h_e): {h_e:.6f} | Sarj-zaman katsayisi (g_e): {g_e:.6f}"
        )
        print("-" * 98)
        print(f"{'Saat':<7} {'Adim':<15} {'Nokta':<20} {'Varis SoC':>12} {'Cikis SoC':>12} {'Sarj':>10} {'Not':<20}")
        print("-" * 98)

        sim_soc = float(Q_map.get(v, 0.0))
        start_val = tau[0, t].X if (0, t) in tau else 0.0
        print(f"{format_time(start_val):<7} {'Depo cikis':<15} {f'0 ({node_labels.get(0, 0)})':<20} {sim_soc:>12.2f} {sim_soc:>12.2f} {0.0:>10.2f} {'Baslangic':<20}")

        for idx in range(len(route)):
            curr_node = route[idx]
            node_name = node_labels.get(curr_node, str(curr_node))
            if idx == 0:
                continue
            prev_node = route[idx - 1]
            leg_dist = d.get((prev_node, curr_node), 0.0)
            soc_arr = max(0.0, sim_soc - h_e * leg_dist)

            if idx == len(route) - 1:
                prev_node = route[idx - 1]
                end_val = tau[prev_node, t].X + st.get(prev_node, 0.0) + tt.get((prev_node, 0), 0.0)
                if prev_node in S_set:
                    end_val += g_e * charge_amount(prev_node, v, t)
                if w_vars[prev_node, curr_node, t].X > 0.5:
                    end_val += 3600
                print(
                    f"{format_time(end_val):<7} {'Depo donus':<15} {f'{curr_node} ({node_name})':<20} "
                    f"{soc_arr:>12.2f} {soc_arr:>12.2f} {0.0:>10.2f} {'Rota sonu':<20}"
                )
            else:
                arr_val = tau[curr_node, t].X
                if curr_node in S_set:
                    q_in = soc_arr
                    q_add = charge_amount(curr_node, v, t)
                    q_out = min(float(Q_map.get(v, 0.0)), q_in + q_add)
                    charge_time = g_e * q_add
                    dep_val = arr_val + charge_time
                    print(
                        f"{format_time(arr_val):<7} {'Sarj':<15} {f'{curr_node} ({node_name})':<20} "
                        f"{q_in:>12.2f} {q_out:>12.2f} {q_add:>10.2f} "
                        f"{('Ayrilis '+format_time(dep_val)):<20}"
                    )
                    sim_soc = q_out
                elif curr_node in C_set:
                    srv_val = st.get(curr_node, 0.0)
                    dep_val = arr_val + srv_val
                    print(
                        f"{format_time(arr_val):<7} {'Musteri':<15} {f'{curr_node} ({node_name})':<20} "
                        f"{soc_arr:>12.2f} {soc_arr:>12.2f} {0.0:>10.2f} "
                        f"{('Servis '+str(int(srv_val // 60))+' dk'):<20}"
                    )
                    sim_soc = soc_arr
                else:
                    print(
                        f"{format_time(arr_val):<7} {'Dugum':<15} {f'{curr_node} ({node_name})':<20} "
                        f"{soc_arr:>12.2f} {soc_arr:>12.2f} {0.0:>10.2f} {'':<20}"
                    )
                    sim_soc = soc_arr

        print("-" * 98)


def select_instances(instances: dict) -> dict:
    base_names = sorted({os.path.splitext(os.path.basename(k))[0] for k in instances})
    print("Mevcut problemler:")
    print(", ".join(base_names))
    try:
        selected = input(
            "Calistirmak istediginiz problem adlarini girin (virgulle ayirin, ornegin C5,R5,RC5). Enter = tumu: "
        ).strip()
    except EOFError:
        # Non-interactive runs (or IDE terminals without stdin) default to all instances.
        selected = ""
    if not selected:
        return instances

    keys = []
    chosen = {item.strip() for item in selected.split(",") if item.strip()}
    for key in sorted(instances):
        base = os.path.splitext(os.path.basename(key))[0]
        if base in chosen:
            keys.append(key)

    if not keys:
        raise ValueError(f"Secilen problem kodlarina uygun dosya bulunamadi: {selected}")
    return {key: instances[key] for key in keys}


if __name__ == "__main__":
    root = os.path.dirname(__file__)
    problem_dirs = ["trsp_problem_sets"]
    instances = load_problem_instances(root, problem_dirs)

    if not instances:
        raise ValueError("trsp_problem_sets klasorunde XML problem dosyasi bulunamadi.")

    instances = select_instances(instances)

    vehicle_file = os.path.join(root, "FC_Info4Vehicle4EV.xml")
    vehicles, vehicle_attrs = parse_vehicle_file(vehicle_file, expected_type="EV")

    station_file = os.path.join(root, "Kalabak_Info4ChargingStations.xml")
    stations = parse_charging_stations(station_file)

    employee_file = os.path.join(root, "Info4Employee.xml")
    skill_tech_map = {}
    all_technicians = []

    if os.path.exists(employee_file):
        emp_tree = ET.parse(employee_file)
        for team in emp_tree.findall(".//Team"):
            skill = team.get("SkillSet")
            if skill:
                members = [m.get("ID") for m in team.find("Members").findall("Technician")]
                skill_tech_map[skill] = members
                all_technicians.extend(members)

    if not all_technicians:
        all_technicians = [f"TECH_{i:03d}" for i in range(1, 9)]
        skill_tech_map = {
            "s1": ["TECH_001", "TECH_002"],
            "s2": ["TECH_003", "TECH_004"],
            "s3": ["TECH_005", "TECH_006"],
            "s4": ["TECH_007"],
            "s5": ["TECH_008"],
        }

    outputs_dir = os.path.join(root, "sonuclar")
    os.makedirs(outputs_dir, exist_ok=True)
    print(f"Sonuclar klasoru: {outputs_dir}")

    for instance_name, instance in instances.items():
        log_buffer = io.StringIO()
        tee = Tee(sys.stdout, log_buffer)
        out_name = os.path.splitext(os.path.basename(instance_name))[0]
        docx_path = os.path.join(outputs_dir, f"{out_name}.docx")

        with redirect_stdout(tee):
            try:
                print(f"\n== {instance_name} icin EV modeli kuruluyor ==")

                data = prepare_ev_data_from_instance(
                    instance,
                    vehicles,
                    vehicle_attrs,
                    stations,
                    technicians=all_technicians,
                )

                if "Q" in data:
                    fixed_q = {}
                    for v in data["V"]:
                        qv = float(data["Q"].get(v, 0.0))
                        if qv <= 0.0:
                            attrs = vehicle_attrs.get(v, {})
                            qv = float(
                                attrs.get("BatteryCapacity")
                                or attrs.get("SoC")
                                or attrs.get("Range")
                                or 1000.0
                            )
                        fixed_q[v] = qv
                    data["Q"] = fixed_q
                    if TEST_BATTERY_SCALE < 1.0:
                        data["Q"] = {v: max(1.0, q * TEST_BATTERY_SCALE) for v, q in data["Q"].items()}
                        print(f"TEST: Batarya kapasitesi {TEST_BATTERY_SCALE:.3f} katsayisi ile dusuruldu.")

                if "lc_0" not in data:
                    data["lc_0"] = 100000.0

                if data.get("h_e", 0.0) <= 0.0 and data.get("V"):
                    ref_v = data["V"][0]
                    data["h_e"] = float(vehicle_attrs.get(ref_v, {}).get("EnergyConsumptionRate", 0.0))
                if data.get("g_e", 0.0) <= 0.0 and data.get("V"):
                    ref_v = data["V"][0]
                    recharge_rate = float(vehicle_attrs.get(ref_v, {}).get("BatteryRechargingRate", 0.0))
                    if recharge_rate > 0.0:
                        data["g_e"] = 1.0 / recharge_rate

                delivery_skills = []
                try:
                    problem_tree = ET.parse(instance_name)
                    for node in problem_tree.findall(".//Node"):
                        req = node.find(".//Request")
                        if req is not None:
                            skill = req.get("RequiredSkill")
                            if skill:
                                delivery_skills.append(skill)
                except Exception as e:
                    print(f"Uyari: {instance_name} okunurken hata olustu. Hata: {e}")

                req_skills_unique = list(set(delivery_skills))

                tech_skill_sets = {}
                for skill, members in skill_tech_map.items():
                    for tech in members:
                        tech_skill_sets.setdefault(tech, set()).add(skill)

                active_techs = set()
                for skill in req_skills_unique:
                    for tech in skill_tech_map.get(skill, []):
                        active_techs.add(tech)
                if not active_techs:
                    active_techs = set(all_technicians)
                active_techs = sorted(active_techs)

                T_list = []
                crew_skills = {}
                crew_members = {}

                for tech in active_techs:
                    crew_name = tech
                    T_list.append(crew_name)
                    crew_skills[crew_name] = set(tech_skill_sets.get(tech, set()))
                    crew_members[crew_name] = [tech]

                if ENABLE_PAIR_CREWS:
                    for t1, t2 in itertools.combinations(active_techs, 2):
                        crew_name = f"{t1}__{t2}"
                        T_list.append(crew_name)
                        crew_skills[crew_name] = set(tech_skill_sets.get(t1, set())).union(tech_skill_sets.get(t2, set()))
                        crew_members[crew_name] = [t1, t2]

                data["T"] = T_list
                data["crew_members"] = crew_members

                base_es = data["es"][all_technicians[0]] if all_technicians else 0.0
                base_ls = data["ls"][all_technicians[0]] if all_technicians else 32400.0
                base_el = data["el"][all_technicians[0]] if all_technicians else 14400.0
                base_ll = data["ll"][all_technicians[0]] if all_technicians else 21600.0

                data["es"] = {crew: base_es for crew in T_list}
                data["ls"] = {crew: base_ls for crew in T_list}
                data["el"] = {crew: base_el for crew in T_list}
                data["ll"] = {crew: base_ll for crew in T_list}

                C_sorted = sorted(data["C"])
                t_key = "T_i" if "T_i" in data else "Ti"
                for idx, c_idx in enumerate(C_sorted):
                    if idx < len(delivery_skills):
                        req_skill = delivery_skills[idx]
                        allowed_crews = []
                        for crew in T_list:
                            if req_skill in crew_skills[crew]:
                                allowed_crews.append(crew)
                        data[t_key][c_idx] = allowed_crews
                    else:
                        data[t_key][c_idx] = T_list[:]

                    if not data[t_key][c_idx]:
                        data[t_key][c_idx] = T_list[:]

                    if not data[t_key][c_idx]:
                        data[t_key][c_idx] = T_list[:]

                model = build_model(data)
                model.update()

                lp_name = f"EV_v1_1_exact_model_{out_name}.lp"
                model.write(lp_name)
                print(f"Model kuruldu ve '{lp_name}' olarak yazildi.")

                model.Params.TimeLimit = 120
                if FEASIBILITY_FOCUSED_PARAMS:
                    model.Params.MIPFocus = 1
                    model.Params.Heuristics = 0.35
                    model.Params.NoRelHeurTime = min(NOREL_HEUR_TIME_CAP, max(0, int(model.Params.TimeLimit * 0.15)))
                    model.Params.Presolve = 2
                    model.Params.Symmetry = 2
                model.optimize()
                print(f"Cozum durumu: {model.Status}")

                if model.Status == GRB.INFEASIBLE:
                    print("Model INFEASIBLE. IIS hesaplaniyor...")
                    model.computeIIS()
                    iis_name = f"EV_v1_1_exact_model_{out_name}.ilp"
                    model.write(iis_name)
                    print(f"IIS '{iis_name}' dosyasina yazildi.")
                elif model.Status == GRB.TIME_LIMIT:
                    if model.SolCount > 0:
                        print("TimeLimit: uygulanabilir cozum bulundu, optimalite kanitlanamadi.")
                    else:
                        print("TimeLimit: hic uygulanabilir cozum bulunamadi (INFEASIBLE ile ayni degil).")

                print_ev_solution(data, model)
            except Exception as exc:
                print(f"HATA: {instance_name} icin calisma sirasinda hata olustu: {exc}")

        try:
            write_output_docx(docx_path, log_buffer.getvalue())
            print(f"Docx kaydedildi: {docx_path}")
        except Exception as exc:
            print(f"Docx kaydetme hatasi ({out_name}): {exc}")


