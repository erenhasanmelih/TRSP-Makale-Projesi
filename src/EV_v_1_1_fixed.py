import os
import itertools
import io
import sys
from contextlib import redirect_stdout
import gurobipy as gp
from gurobipy import GRB
import xml.etree.ElementTree as ET
from xml_data_loader_fixed import (
    load_problem_instances,
    parse_vehicle_file,
    parse_charging_stations,
    prepare_ev_data_from_instance,
)

# Kaynak: raw/EV_v.1.1.py - Faz 2 duzeltmeleri (A1, A7, A6, A4, A2+C1, A5, C2) uygulanmistir.

ENABLE_PAIR_CREWS = True
FEASIBILITY_FOCUSED_PARAMS = True
MAX_ROUTES_PER_VEHICLE = 1  # Gunluk en fazla 3 arac: mevcut 3 EV'nin her biri en fazla 1 rota alir.
MODEL_TIME_LIMIT_SECONDS = 60 * 60  # 1 saat / problem
TARGET_INSTANCE_SEQUENCE = [
    "R15",
    "RC15",
    "RC13",
]

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


def normalize_problem_code(name: str) -> str:
    return "".join(str(name).upper().split())


SRC_ROOT = os.path.dirname(os.path.abspath(__file__))


def resolve_data_root() -> str:
    """Veri (XML) kokunu bul. src/ altinda veri yoksa salt-okunur raw/ kullanilir."""
    if os.path.isdir(os.path.join(SRC_ROOT, "trsp_problem_sets")):
        return SRC_ROOT
    candidate = os.path.join(os.path.dirname(SRC_ROOT), "raw")
    if os.path.isdir(os.path.join(candidate, "trsp_problem_sets")):
        return candidate
    return SRC_ROOT


def set_model_param_safe(model: gp.Model, name: str, value):
    try:
        model.setParam(name, value)
    except gp.GurobiError as exc:
        print(f"Uyari: Parametre ayarlanamadi ({name}={value}). Detay: {exc}")

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
    h_e_v = data.get("h_e_v", {}) or {}
    g_e = data["g_e"]
    lc0 = data["lc_0"] if "lc_0" in data else data.get("lc0", 100000.0)

    C_set = set(C)
    S_set = set(S)

    # ------------------------------------------------------------------
    # C1 (4B -> 3B indis indirgeme) + A5 (yetkinlik hard-constraint)
    # ------------------------------------------------------------------
    # K: gecerli (arac, ekip) eslesmelerinin birlesik indeksi.
    # x artik x[i, j, k] seklinde 3 indislidir (eski hali: x[i, j, v, t]).
    K_pairs = [(v, t) for v in V for t in T]
    KK = list(range(len(K_pairs)))
    k_veh = {k: K_pairs[k][0] for k in KK}
    k_crew = {k: K_pairs[k][1] for k in KK}
    K_of_crew = {t: [] for t in T}
    K_of_veh = {v: [] for v in V}
    for k in KK:
        K_of_crew[k_crew[k]].append(k)
        K_of_veh[k_veh[k]].append(k)

    # Heterojen filo: her k'nin gercek araci uzerinden kapasite/tuketim.
    Q_of_k = {k: float(Q[k_veh[k]]) for k in KK}
    he_of_k = {k: float(h_e_v.get(k_veh[k], h_e)) for k in KK}

    Ti_set = {i: set(vals) for i, vals in Ti.items()}

    def _crew_allowed(node, t):
        # A5: musteri dugumlerinde sadece yetkin ekipler; depo/istasyon serbest.
        if node in C_set:
            return t in Ti_set.get(node, set())
        return True

    # A5: uyumsuz (musteri, ekip) kombinasyonlari icin x degiskeni HIC uretilmez.
    XK = [
        (i, j, k)
        for (i, j) in A
        for k in KK
        if _crew_allowed(i, k_crew[k]) and _crew_allowed(j, k_crew[k])
    ]
    XK_set = set(XK)
    arc_ks = {}
    out_nodes = {}
    in_nodes = {}
    for (i, j, k) in XK:
        arc_ks.setdefault((i, j), []).append(k)
        out_nodes.setdefault((i, k), []).append(j)
        in_nodes.setdefault((j, k), []).append(i)

    # ------------------------------------------------------------------
    # C2 (tight Big-M) altyapisi: zaman ufku ve dugum bazli tau ust sinirlari
    # ------------------------------------------------------------------
    horizon_end = max([float(vv) for vv in ls.values()]) if ls else 32400.0
    cust_lc = [float(lc[i]) for i in C if i in lc]
    if cust_lc:
        horizon_end = max(horizon_end, max(cust_lc))
    if horizon_end <= 0.0:
        horizon_end = 100000.0

    tau_ub = {}
    for i in Np:
        if i in C_set and i in lc:
            tau_ub[i] = min(float(lc[i]), horizon_end)
        else:
            # Depo / sarj istasyonlari: vardiya ufku ile sinirli
            # (yukleyicideki lc = 100000 yapay degeri Big-M'i sismesin diye kullanilmaz).
            tau_ub[i] = horizon_end

    break_duration = 3600
    break_min = 13800
    break_max = 15000

    max_q = max(Q_of_k.values()) if Q_of_k else 0.0
    charge_time_ub = g_e * max_q if S_set else 0.0

    # Decision variables
    x = m.addVars(XK, vtype=GRB.BINARY, name="x")
    tau = m.addVars(Np, T, lb=0.0, vtype=GRB.CONTINUOUS, name="tau")
    L = m.addVars(Np, T, lb=0.0, vtype=GRB.CONTINUOUS, name="L")
    # A2: enerji degiskenleri artik (dugum, (arac,ekip)) indisli.
    YE = m.addVars(Np, KK, lb=0.0, vtype=GRB.CONTINUOUS, name="YE")
    ye = m.addVars(Np, KK, lb=0.0, vtype=GRB.CONTINUOUS, name="ye")
    w = m.addVars(A, T, vtype=GRB.BINARY, name="w")
    y_route = m.addVars(T, vtype=GRB.BINARY, name="y_route")

    # Degisken sinirlari (tight Big-M turetimlerinin dayandigi kutu sinirlari)
    for i in Np:
        for t in T:
            tau[i, t].UB = tau_ub[i]
    for i in Np:
        for k in KK:
            YE[i, k].UB = Q_of_k[k]
            ye[i, k].UB = Q_of_k[k]

    def visit_expr(i, t):
        """Ekip t'nin i dugumune girip girmedigini gosteren 0/1 ifadesi (A4)."""
        return gp.quicksum(
            x[p, i, k] for k in K_of_crew[t] for p in in_nodes.get((i, k), ())
        )

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
    m._K_pairs = K_pairs
    m._KK = KK
    m._k_veh = k_veh
    m._k_crew = k_crew

    # Objective
    m.setObjective(
        gp.quicksum(d[i, j] * x[i, j, k] for (i, j, k) in XK),
        GRB.MINIMIZE,
    )

    # Same mathematical constraints, EV notation only
    for j in C:
        m.addConstr(
            gp.quicksum(x[i, j, k] for k in KK for i in in_nodes.get((j, k), ())) == 1,
            name=f"c2_{j}",
        )

    for i, j in A:
        ks = arc_ks.get((i, j), ())
        if not ks:
            continue
        m.addConstr(gp.quicksum(x[i, j, k] for k in ks) <= 1, name=f"c3_{i}_{j}")

    if MAX_ROUTES_PER_VEHICLE is not None:
        for v in V:
            m.addConstr(
                gp.quicksum(
                    x[0, j, k] for k in K_of_veh[v] for j in out_nodes.get((0, k), ())
                )
                <= MAX_ROUTES_PER_VEHICLE,
                name=f"c4_{v}",
            )

    for t in T:
        depart_t = gp.quicksum(
            x[0, j, k] for k in K_of_crew[t] for j in out_nodes.get((0, k), ())
        )
        m.addConstr(depart_t <= 1, name=f"c5_{t}")
        m.addConstr(y_route[t] == depart_t, name=f"c5_link_{t}")

    for i in Np:
        for k in KK:
            m.addConstr(
                gp.quicksum(x[i, j, k] for j in out_nodes.get((i, k), ()))
                - gp.quicksum(x[j, i, k] for j in in_nodes.get((i, k), ()))
                == 0,
                name=f"c6_{i}_{k}",
            )

    # C2 (tight Big-M) #1: c8 zaman ilerleme kisiti.
    # x[i,j,k] = 0 iken kisitin bagsiz kalmasi icin gerekli en kucuk M:
    #   M8 = tau_ub[i] + st[i] + break_duration + (istasyonsa max sarj suresi) - tau_lb[j]
    # tau_lb[j] = 0 alinir; cunku A4 sonrasi c18_lb yalnizca ziyaret edilen
    # dugumlerde baglayicidir.
    for (i, j, k) in XK:
        if j == 0:
            continue
        t = k_crew[k]
        st_i = st.get(i, 0.0)
        charge_time_i = g_e * (YE[i, k] - ye[i, k]) if i in S_set else 0.0
        big_m_8 = max(
            0.0,
            tau_ub[i] + st_i + break_duration + (charge_time_ub if i in S_set else 0.0),
        )
        m.addConstr(
            tau[i, t]
            + st_i
            + w[i, j, t] * break_duration
            + charge_time_i
            + tt[i, j] * x[i, j, k]
            - big_m_8 * (1 - x[i, j, k])
            <= tau[j, t],
            name=f"c8_zaman_ilerleme_{i}_{j}_{k}",
        )

    for t in T:
        sum_w = gp.quicksum(w[i, j, t] for (i, j) in A)

        m.addConstr(
            sum_w
            <= gp.quicksum(
                x[0, i, k] for k in K_of_crew[t] for i in out_nodes.get((0, k), ())
            ),
            name=f"mola_max1_{t}",
        )

        for i in Np:
            if i == 0:
                continue
            for k in K_of_crew[t]:
                if (i, 0, k) in XK_set:
                    st_i = st.get(i, 0.0)
                    tt_i0 = tt.get((i, 0), 0.0)
                    # C2 (tight Big-M) #4: mola_yoksa_erken_donus
                    big_m_erken = max(0.0, tau_ub[i] + st_i + tt_i0 - break_max)
                    m.addConstr(
                        tau[i, t] + st_i + tt_i0
                        <= break_max + big_m_erken * (1 - x[i, 0, k] + sum_w),
                        name=f"mola_yoksa_erken_donus_{i}_{k}",
                    )

    for i, j in A:
        for t in T:
            ks_t = [k for k in arc_ks.get((i, j), ()) if k_crew[k] == t]
            m.addConstr(
                w[i, j, t] <= gp.quicksum(x[i, j, k] for k in ks_t),
                name=f"mola_yol_ustu_onayi_{i}_{j}_{t}",
            )

            st_i = st.get(i, 0.0)
            # C2 (tight Big-M) #2: mola baslama pencereleri
            big_m_mola_alt = max(0.0, break_min - st_i)
            big_m_mola_ust = max(0.0, tau_ub[i] + st_i - break_max)
            m.addConstr(
                tau[i, t] + st_i >= break_min - big_m_mola_alt * (1 - w[i, j, t]),
                name=f"mola_baslama_alt_sinir_{i}_{j}_{t}",
            )
            m.addConstr(
                tau[i, t] + st_i <= break_max + big_m_mola_ust * (1 - w[i, j, t]),
                name=f"mola_baslama_ust_sinir_{i}_{j}_{t}",
            )

    # ------------------------------------------------------------------
    # A4: zaman penceresi kisitlari artik x ile kosullaniyor.
    # (i) Ekip t musteri i icin yetkin degilse kisit HIC yazilmaz (A5 ile tutarli).
    # (ii) Yetkin ama o rotada ziyaret etmiyorsa Big-M ile gevsetilir.
    # ------------------------------------------------------------------
    for i in C:
        for t in T:
            if t not in Ti_set.get(i, set()):
                continue
            if (0, i) in tt:
                big_m_16 = max(0.0, float(es[t]) + float(tt[0, i]))
                m.addConstr(
                    tau[i, t] - tt[0, i]
                    >= es[t] - big_m_16 * (1 - visit_expr(i, t)),
                    name=f"c16_{i}_{t}",
                )

    for i in C:
        for t in T:
            if t not in Ti_set.get(i, set()):
                continue
            if (i, 0) in A and (i, 0) in tt:
                st_i = st.get(i, 0.0)
                tt_i0 = tt.get((i, 0), 0.0)
                big_m_17 = max(
                    0.0, tau_ub[i] + st_i + tt_i0 + break_duration - float(ls[t])
                )
                m.addConstr(
                    tau[i, t] + st_i + tt_i0 + w[i, 0, t] * break_duration
                    <= ls[t] + big_m_17 * (1 - visit_expr(i, t)),
                    name=f"c17_{i}_{t}",
                )

    # Technician overlap prevention:
    # A technician may appear in multiple crews, but those crews cannot run simultaneously.
    if crew_members:
        nonoverlap_M = horizon_end + break_duration + charge_time_ub

        route_start = m.addVars(T, lb=0.0, ub=horizon_end, vtype=GRB.CONTINUOUS, name="route_start")
        route_end = m.addVars(
            T,
            lb=0.0,
            ub=horizon_end + break_duration + charge_time_ub,
            vtype=GRB.CONTINUOUS,
            name="route_end",
        )

        for t in T:
            m.addConstr(route_start[t] <= horizon_end * y_route[t], name=f"route_start_gate_{t}")
            m.addConstr(
                route_end[t]
                <= (horizon_end + break_duration + charge_time_ub) * y_route[t],
                name=f"route_end_gate_{t}",
            )
            m.addConstr(route_end[t] >= route_start[t], name=f"route_seq_{t}")

            # Link route_start to chosen departure arc.
            for j in Np:
                if j == 0:
                    continue
                if (0, j) not in tt:
                    continue
                for k in K_of_crew[t]:
                    if (0, j, k) in XK_set:
                        expr_dep = tau[j, t] - tt[0, j]
                        m.addConstr(
                            route_start[t] >= expr_dep - nonoverlap_M * (1 - x[0, j, k]),
                            name=f"route_start_lb_{t}_{k}_{j}",
                        )
                        m.addConstr(
                            route_start[t] <= expr_dep + nonoverlap_M * (1 - x[0, j, k]),
                            name=f"route_start_ub_{t}_{k}_{j}",
                        )

            # Link route_end to chosen return arc.
            for i in Np:
                if i == 0:
                    continue
                if (i, 0) not in tt:
                    continue
                for k in K_of_crew[t]:
                    if (i, 0, k) in XK_set:
                        extra_charge = g_e * (YE[i, k] - ye[i, k]) if i in S_set else 0.0
                        expr_ret = tau[i, t] + st.get(i, 0.0) + tt[i, 0] + break_duration * w[i, 0, t] + extra_charge
                        m.addConstr(
                            route_end[t] >= expr_ret - nonoverlap_M * (1 - x[i, 0, k]),
                            name=f"route_end_lb_{t}_{k}_{i}",
                        )
                        m.addConstr(
                            route_end[t] <= expr_ret + nonoverlap_M * (1 - x[i, 0, k]),
                            name=f"route_end_ub_{t}_{k}_{i}",
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

    # A4: c18 zaman penceresi de ziyaret kosuluna baglandi.
    # c18_lb (hazir olma zamani) ziyaret edilmeyen (i, t) ciftlerinde gevsetilir;
    # c18_ub ise tau degiskeninin kutu ust siniri olarak zaten garanti altindadir,
    # bu yuzden kosulsuz birakilmasi infeasibility yaratmaz.
    for i in C:
        for t in T:
            if t not in Ti_set.get(i, set()):
                continue
            big_m_18 = max(0.0, float(ec[i]))
            m.addConstr(
                ec[i] <= tau[i, t] + big_m_18 * (1 - visit_expr(i, t)),
                name=f"c18_lb_{i}_{t}",
            )
            m.addConstr(tau[i, t] <= lc[i], name=f"c18_ub_{i}_{t}")

    # ------------------------------------------------------------------
    # Enerji takibi (A1 + A2)
    # A1: c20 (varis enerjisi ye[i] uzerinden yazilan zincir) artik SADECE
    #     istasyon OLMAYAN dugumlerden cikan yaylarda yazilir. Aksi halde
    #     YE[s] >= ye[s] oldugundan c20 her zaman c21'den siki kalir, alinan
    #     sarj miktari enerji akisina hic yansimaz (sarj etkisiz kalirdi).
    # A2: ye/YE artik (dugum, k) indisli; her (arac, ekip) kendi enerjisini takip
    #     eder, istasyon dugumleri farkli rotalar arasinda paylasilmaz.
    # ------------------------------------------------------------------
    for (i, j, k) in XK:
        if i == 0 or j == 0:
            continue
        if i in S_set:
            continue  # A1: istasyon cikis yaylarinda c20 devre disi
        m.addConstr(ye[j, k] >= 0, name=f"c20_lb_{i}_{j}_{k}")
        m.addConstr(
            ye[j, k]
            <= ye[i, k] - (he_of_k[k] * d[i, j]) * x[i, j, k] + Q_of_k[k] * (1 - x[i, j, k]),
            name=f"c20_ub_{i}_{j}_{k}",
        )

    for (i, j, k) in XK:
        if i == 0 or j == 0:
            continue
        m.addConstr(ye[j, k] >= 0, name=f"c21_lb_{i}_{j}_{k}")
        m.addConstr(
            ye[j, k]
            <= YE[i, k] - (he_of_k[k] * d[i, j]) * x[i, j, k] + Q_of_k[k] * (1 - x[i, j, k]),
            name=f"c21_ub_{i}_{j}_{k}",
        )

    for i in Np:
        if i == 0:
            continue
        for k in KK:
            if i in S_set:
                # At charging stations, departure energy can be higher than arrival energy.
                m.addConstr(YE[i, k] >= ye[i, k], name=f"c22_station_recharge_lb_{i}_{k}")
            else:
                m.addConstr(YE[i, k] == ye[i, k], name=f"c22_no_recharge_{i}_{k}")
            m.addConstr(YE[i, k] <= Q_of_k[k], name=f"c22_ub_{i}_{k}")

    if S_set:
        for s in S_set:
            for k in KK:
                outflow_s = gp.quicksum(x[s, j, k] for j in out_nodes.get((s, k), ()))
                m.addConstr(
                    YE[s, k] - ye[s, k] <= Q_of_k[k] * outflow_s,
                    name=f"c22_station_recharge_bigM_{s}_{k}",
                )

    # Depoya donus enerjisi: istasyonda alinan sarj da hesaba katilir (A1),
    # istasyon disi dugumlerde YE == ye oldugu icin ifade degismez.
    for i in Np:
        if i == 0:
            continue
        for k in KK:
            if (i, 0, k) in XK_set:
                m.addConstr(
                    YE[i, k] >= (he_of_k[k] * d.get((i, 0), 0.0)) * x[i, 0, k],
                    name=f"c_return_energy_{i}_{k}",
                )

    # C2 (tight Big-M) #3: depodan tam dolu cikis.
    # ye[j,k] kutusunun ust siniri zaten Q_of_k[k] oldugundan ub tarafinda M = 0,
    # lb tarafinda M = Q_of_k[k] - h_e * d[0,j] yeterlidir (eski hali 100000.0).
    for j in Np:
        if j == 0:
            continue
        for k in KK:
            if (0, j, k) in XK_set:
                depart_use = he_of_k[k] * d.get((0, j), 0.0)
                big_m_full = max(0.0, Q_of_k[k] - depart_use)
                m.addConstr(
                    ye[j, k] <= Q_of_k[k] - depart_use * x[0, j, k],
                    name=f"c_full_depot_ub_{j}_{k}",
                )
                m.addConstr(
                    ye[j, k] >= Q_of_k[k] - depart_use - big_m_full * (1 - x[0, j, k]),
                    name=f"c_full_depot_lb_{j}_{k}",
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

    K_pairs = getattr(model, "_K_pairs", [])

    def charge_amount(node, k):
        key = (node, k)
        if node in S_set and YE is not None and ye is not None and key in YE and key in ye:
            return max(0.0, float(YE[key].X - ye[key].X))
        return 0.0

    # A2+C1: x artik x[i, j, k] indisli; k -> (arac, ekip) esleme uzerinden cozulur.
    routes = {}
    for (i, j, k), var in x.items():
        if var.X > 0.5:
            v, t = K_pairs[k]
            routes.setdefault((v, t, k), []).append((i, j))

    print("\n" + "=" * 98)
    print("EV GUNLUK OPERASYON OZETI")
    print("=" * 98)

    for (v, t, k), arcs in sorted(routes.items()):
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
        print("-" * 112)
        print(f"{'Giris':<7} {'Cikis':<7} {'Adim':<15} {'Nokta':<20} {'Varis SoC':>12} {'Cikis SoC':>12} {'Sarj':>10} {'Not':<20}")
        print("-" * 112)

        sim_soc = float(Q_map.get(v, 0.0))
        start_val = tau[0, t].X if (0, t) in tau else 0.0
        print(
            f"{format_time(start_val):<7} {format_time(start_val):<7} {'Depo cikis':<15} "
            f"{f'0 ({node_labels.get(0, 0)})':<20} {sim_soc:>12.2f} {sim_soc:>12.2f} {0.0:>10.2f} {'Baslangic':<20}"
        )

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
                    end_val += g_e * charge_amount(prev_node, k)
                if w_vars[prev_node, curr_node, t].X > 0.5:
                    end_val += 3600
                print(
                    f"{format_time(end_val):<7} {format_time(end_val):<7} {'Depo donus':<15} {f'{curr_node} ({node_name})':<20} "
                    f"{soc_arr:>12.2f} {soc_arr:>12.2f} {0.0:>10.2f} {'Rota sonu':<20}"
                )
            else:
                arr_val = tau[curr_node, t].X
                if curr_node in S_set:
                    q_in = soc_arr
                    q_add = charge_amount(curr_node, k)
                    q_out = min(float(Q_map.get(v, 0.0)), q_in + q_add)
                    charge_time = g_e * q_add
                    dep_val = arr_val + charge_time
                    print(
                        f"{format_time(arr_val):<7} {format_time(dep_val):<7} {'Sarj':<15} {f'{curr_node} ({node_name})':<20} "
                        f"{q_in:>12.2f} {q_out:>12.2f} {q_add:>10.2f} "
                        f"{('Ayrilis '+format_time(dep_val)):<20}"
                    )
                    sim_soc = q_out
                elif curr_node in C_set:
                    srv_val = st.get(curr_node, 0.0)
                    dep_val = arr_val + srv_val
                    print(
                        f"{format_time(arr_val):<7} {format_time(dep_val):<7} {'Musteri':<15} {f'{curr_node} ({node_name})':<20} "
                        f"{soc_arr:>12.2f} {soc_arr:>12.2f} {0.0:>10.2f} "
                        f"{('Servis '+str(int(srv_val // 60))+' dk'):<20}"
                    )
                    sim_soc = soc_arr
                else:
                    print(
                        f"{format_time(arr_val):<7} {format_time(arr_val):<7} {'Dugum':<15} {f'{curr_node} ({node_name})':<20} "
                        f"{soc_arr:>12.2f} {soc_arr:>12.2f} {0.0:>10.2f} {'':<20}"
                    )
                    sim_soc = soc_arr

        print("-" * 112)


def select_instances(instances: dict, ordered_codes: list = None) -> dict:
    code_to_key = {}
    for key in sorted(instances):
        base = os.path.splitext(os.path.basename(key))[0]
        code_to_key[normalize_problem_code(base)] = key

    available_codes = sorted(code_to_key.keys())
    print("Mevcut problemler:")
    print(", ".join(available_codes))

    if ordered_codes:
        selected_keys = []
        missing_codes = []
        for code in ordered_codes:
            norm_code = normalize_problem_code(code)
            key = code_to_key.get(norm_code)
            if key is None:
                missing_codes.append(norm_code)
            else:
                selected_keys.append(key)

        if missing_codes:
            print(f"Uyari: Asagidaki problemler bulunamadi ve atlandi: {', '.join(missing_codes)}")
        if not selected_keys:
            raise ValueError("Istenen problem sirasindan hicbiri bulunamadi.")

        selected_codes = [
            normalize_problem_code(os.path.splitext(os.path.basename(k))[0]) for k in selected_keys
        ]
        print("Calisma sirasi:")
        print(", ".join(selected_codes))
        return {key: instances[key] for key in selected_keys}

    try:
        selected = input(
            "Calistirmak istediginiz problem adlarini girin (virgulle ayirin, ornegin C5,R5,RC5). Enter = tumu: "
        ).strip()
    except EOFError:
        selected = ""

    if not selected:
        return instances

    keys = []
    chosen = {normalize_problem_code(item) for item in selected.split(",") if item.strip()}
    for code in chosen:
        key = code_to_key.get(code)
        if key is not None:
            keys.append(key)

    if not keys:
        raise ValueError(f"Secilen problem kodlarina uygun dosya bulunamadi: {selected}")
    return {key: instances[key] for key in keys}


if __name__ == "__main__":
    # Veri raw/ altindan OKUNUR; tum ciktilar src/ altina yazilir (raw/ salt-okunur).
    root = resolve_data_root()
    problem_dirs = ["trsp_problem_sets"]
    instances = load_problem_instances(root, problem_dirs)

    if not instances:
        raise ValueError("trsp_problem_sets klasorunde XML problem dosyasi bulunamadi.")

    instances = select_instances(instances, ordered_codes=TARGET_INSTANCE_SEQUENCE)

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

    outputs_dir = os.path.join(SRC_ROOT, "sonuclar")
    os.makedirs(outputs_dir, exist_ok=True)
    print(f"Sonuclar klasoru: {outputs_dir}")

    for instance_name, instance in instances.items():
        log_buffer = io.StringIO()
        tee = Tee(sys.stdout, log_buffer)
        out_name = normalize_problem_code(os.path.splitext(os.path.basename(instance_name))[0])
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

                lp_name = os.path.join(outputs_dir, f"EV_v1_1_exact_model_{out_name}.lp")
                model.write(lp_name)
                print(f"Model kuruldu ve '{lp_name}' olarak yazildi.")

                model.Params.TimeLimit = MODEL_TIME_LIMIT_SECONDS
                if FEASIBILITY_FOCUSED_PARAMS:
                    set_model_param_safe(model, "MIPFocus", 2)
                    set_model_param_safe(model, "Heuristics", 0.15)
                    set_model_param_safe(model, "NoRelHeurTime", 600)
                    set_model_param_safe(model, "NoRelHeurSolutions", 5)
                    set_model_param_safe(model, "RINS", 25)
                    set_model_param_safe(model, "SubMIPNodes", 500)
                    set_model_param_safe(model, "Presolve", 2)
                    set_model_param_safe(model, "Symmetry", 2)
                    set_model_param_safe(model, "MIPSepCuts", 2)
                    set_model_param_safe(model, "Cuts", 2)
                    set_model_param_safe(model, "IntegralityFocus", 1)
                    set_model_param_safe(model, "NumericFocus", 1)
                    set_model_param_safe(model, "MIPGap", 0.005)
                model.optimize()
                print(f"Cozum durumu: {model.Status}")

                if model.Status == GRB.INFEASIBLE:
                    print("Model INFEASIBLE. IIS hesaplaniyor...")
                    model.computeIIS()
                    iis_name = os.path.join(outputs_dir, f"EV_v1_1_exact_model_{out_name}.ilp")
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