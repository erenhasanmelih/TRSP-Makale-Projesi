import os
import itertools
import gurobipy as gp
from gurobipy import GRB
import xml.etree.ElementTree as ET
from xml_data_loader_fixed import (
    load_problem_instances,
    parse_vehicle_file,
    prepare_cv_data_from_instance,
)

# Kaynak: raw/CV_model_gurobi_exact.py - Faz 2 duzeltmeleri (A7, A6, A4, A2+C1, A5, C2)
# uygulanmistir. (A1 yalnizca EV'ye ozgudur: CV modelinde sarj istasyonu dugumu yoktur.)


def build_model(
        N, N0, C, Vc, V, T, Ti, Fc, A,
        d, tt, st, G, ec, lc, es, ls, el, ll, h_c, g_c, k, lc0,
        node_labels=None, crew_members=None, h_c_v=None
):
    # Yukleyiciden gelen 'k' talep sozlugudur; asagida k, (arac, ekip) birlesik
    # indisi olarak kullanildigi icin once yeniden adlandirilir.
    k_demand = k
    del k

    m = gp.Model("exact_model")

    crew_members = crew_members or {}
    h_c_v = h_c_v or {}
    C_set = set(C)

    # ------------------------------------------------------------------
    # C1 (4B -> 3B indis indirgeme) + A5 (yetkinlik hard-constraint)
    # ------------------------------------------------------------------
    # K: gecerli (arac, ekip) eslesmelerinin birlesik indeksi.
    # x artik x[i, j, k] seklinde 3 indislidir (eski hali: x[i, j, v, t]).
    K_pairs = [(v, t) for v in V for t in T]
    KK = list(range(len(K_pairs)))
    k_veh = {kk: K_pairs[kk][0] for kk in KK}
    k_crew = {kk: K_pairs[kk][1] for kk in KK}
    K_of_crew = {t: [] for t in T}
    K_of_veh = {v: [] for v in V}
    for kk in KK:
        K_of_crew[k_crew[kk]].append(kk)
        K_of_veh[k_veh[kk]].append(kk)

    # Heterojen filo: her k'nin gercek araci uzerinden depo/tuketim parametreleri.
    G_of_k = {kk: float(G[k_veh[kk]]) for kk in KK}
    hc_of_k = {kk: float(h_c_v.get(k_veh[kk], h_c)) for kk in KK}

    Ti_set = {i: set(vals) for i, vals in Ti.items()}

    def _crew_allowed(node, t):
        # A5: musteri dugumlerinde sadece yetkin ekipler; depo serbest.
        if node in C_set:
            return t in Ti_set.get(node, set())
        return True

    # A5: uyumsuz (musteri, ekip) kombinasyonlari icin x degiskeni HIC uretilmez.
    XK = [
        (i, j, kk)
        for (i, j) in A
        for kk in KK
        if _crew_allowed(i, k_crew[kk]) and _crew_allowed(j, k_crew[kk])
    ]
    XK_set = set(XK)
    arc_ks = {}
    out_nodes = {}
    in_nodes = {}
    for (i, j, kk) in XK:
        arc_ks.setdefault((i, j), []).append(kk)
        out_nodes.setdefault((i, kk), []).append(j)
        in_nodes.setdefault((j, kk), []).append(i)

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
    for i in N0:
        if i in C_set and i in lc:
            tau_ub[i] = min(float(lc[i]), horizon_end)
        else:
            # Depo: yukleyicideki lc = 100000 yapay degeri yerine vardiya ufku.
            tau_ub[i] = horizon_end

    # --- ZAMAN VE MOLA İLERLEMESİ ---
    # Modelin 0. Saniyesi sabah 08:00'dir.
    break_duration = 3600  # Tam 1 Saat
    break_min = 13800  # 11:50 (+10/-10 dk tolerans alt sınırı)
    break_max = 15000  # 12:10 (+10/-10 dk tolerans üst sınırı)

    # Karar Değişkenleri (Gereksiz z ve z0 silindi, model hafifletildi)
    x = m.addVars(XK, vtype=GRB.BINARY, name="x")
    tau = m.addVars(N0, T, lb=0.0, vtype=GRB.CONTINUOUS, name="tau")
    L = m.addVars(N0, T, lb=0.0, vtype=GRB.CONTINUOUS, name="L")
    # A2: yakit degiskenleri artik (dugum, (arac,ekip)) indisli.
    YC = m.addVars(N0, KK, lb=0.0, vtype=GRB.CONTINUOUS, name="YC")
    yc = m.addVars(N0, KK, lb=0.0, vtype=GRB.CONTINUOUS, name="yc")
    w = m.addVars(A, T, vtype=GRB.BINARY, name="w")
    y_route = m.addVars(T, vtype=GRB.BINARY, name="y_route")
    alpha = m.addVars(Fc, Vc, lb=0.0, vtype=GRB.CONTINUOUS, name="alpha")

    # Degisken kutu sinirlari (tight Big-M turetimlerinin dayanagi)
    for i in N0:
        for t in T:
            tau[i, t].UB = tau_ub[i]
    for i in N0:
        for kk in KK:
            YC[i, kk].UB = G_of_k[kk]
            yc[i, kk].UB = G_of_k[kk]

    def visit_expr(i, t):
        """Ekip t'nin i dugumune girip girmedigini gosteren 0/1 ifadesi (A4)."""
        return gp.quicksum(
            x[p, i, kk] for kk in K_of_crew[t] for p in in_nodes.get((i, kk), ())
        )

    # Çıktı için karar değişkenlerini kaydetme
    m._x = x
    m._tau = tau
    m._w = w
    m._A = A
    m._V = V
    m._T = T
    m._YC = YC
    m._yc = yc
    m._G = G
    m._h_c = h_c
    m._K_pairs = K_pairs
    m._KK = KK

    # Amaç Fonksiyonu: Toplam Mesafeyi Minimize Et
    m.setObjective(
        gp.quicksum(d[i, j] * x[i, j, kk] for (i, j, kk) in XK),
        GRB.MINIMIZE
    )

    # c2: HER MÜŞTERİYE SADECE YETKİNLİĞİ OLAN EKiP GİREBİLİR
    # (A5 sayesinde uyumsuz ekiplerin degiskeni zaten uretilmemistir.)
    for j in C:
        m.addConstr(
            gp.quicksum(x[i, j, kk] for kk in KK for i in in_nodes.get((j, kk), ())) == 1,
            name=f"c2_{j}"
        )

    for i, j in A:
        ks = arc_ks.get((i, j), ())
        if not ks:
            continue
        m.addConstr(gp.quicksum(x[i, j, kk] for kk in ks) <= 1, name=f"c3_{i}_{j}")

    for v in V:
        m.addConstr(
            gp.quicksum(
                x[0, j, kk] for kk in K_of_veh[v] for j in out_nodes.get((0, kk), ())
            ) <= 1,
            name=f"c4_{v}"
        )

    for t in T:
        depart_t = gp.quicksum(
            x[0, j, kk] for kk in K_of_crew[t] for j in out_nodes.get((0, kk), ())
        )
        m.addConstr(depart_t <= 1, name=f"c5_{t}")
        m.addConstr(y_route[t] == depart_t, name=f"c5_link_{t}")

    for i in N0:
        for kk in KK:
            m.addConstr(
                gp.quicksum(x[i, j, kk] for j in out_nodes.get((i, kk), ()))
                - gp.quicksum(x[j, i, kk] for j in in_nodes.get((i, kk), ())) == 0,
                name=f"c6_{i}_{kk}"
            )

    # C2 (tight Big-M) #1: c8 zaman ilerleme kisiti.
    # x = 0 iken bagsiz kalmasi icin gereken en kucuk M:
    #   M8 = tau_ub[i] + st[i] + break_duration - tau_lb[j], tau_lb[j] = 0.
    for (i, j, kk) in XK:
        if j == 0:
            continue
        t = k_crew[kk]
        st_i = st.get(i, 0.0)
        big_m_8 = max(0.0, tau_ub[i] + st_i + break_duration)
        m.addConstr(
            tau[i, t]
            + st_i
            + w[i, j, t] * break_duration  # Eğer mola bu aralıkta verilirse 1 saat zaman ekle
            + tt[i, j] * x[i, j, kk]
            - big_m_8 * (1 - x[i, j, kk])
            <= tau[j, t],
            name=f"c8_zaman_ilerleme_{i}_{j}_{kk}"
        )

    # --- ESNEK MOLA KURALLARI YEPYENİ BLOK ---
    for t in T:
        sum_w = gp.quicksum(w[i, j, t] for (i, j) in A)

        # 1. En fazla 1 mola verilebilir
        m.addConstr(
            sum_w <= gp.quicksum(
                x[0, i, kk] for kk in K_of_crew[t] for i in out_nodes.get((0, kk), ())
            ),
            name=f"mola_max1_{t}"
        )

        # 2. Eğer Mola VERİLMEDİYSE, mesai (depoya dönüş) en geç 12:10'da bitmek zorundadır.
        for i in N0:
            if i == 0:
                continue
            for kk in K_of_crew[t]:
                if (i, 0, kk) in XK_set:
                    st_i = st.get(i, 0.0)
                    tt_i0 = tt.get((i, 0), 0.0)
                    # C2 (tight Big-M) #4
                    big_m_erken = max(0.0, tau_ub[i] + st_i + tt_i0 - break_max)
                    m.addConstr(
                        tau[i, t] + st_i + tt_i0
                        <= break_max + big_m_erken * (1 - x[i, 0, kk] + sum_w),
                        name=f"mola_yoksa_erken_donus_{i}_{kk}"
                    )

    for i, j in A:
        for t in T:
            # Mola sadece iki nokta arasında geçiş varsa verilebilir
            ks_t = [kk for kk in arc_ks.get((i, j), ()) if k_crew[kk] == t]
            m.addConstr(
                w[i, j, t] <= gp.quicksum(x[i, j, kk] for kk in ks_t),
                name=f"mola_yol_ustu_onayi_{i}_{j}_{t}"
            )

            # 3. Mola VERİLDİYSE, molanın başlama saati tolerans aralığında (11:50 - 12:10) olmak zorundadır.
            st_i = st.get(i, 0.0)
            # C2 (tight Big-M) #2
            big_m_mola_alt = max(0.0, break_min - st_i)
            big_m_mola_ust = max(0.0, tau_ub[i] + st_i - break_max)
            m.addConstr(
                tau[i, t] + st_i >= break_min - big_m_mola_alt * (1 - w[i, j, t]),
                name=f"mola_baslama_alt_sinir_{i}_{j}_{t}"
            )
            m.addConstr(
                tau[i, t] + st_i <= break_max + big_m_mola_ust * (1 - w[i, j, t]),
                name=f"mola_baslama_ust_sinir_{i}_{j}_{t}"
            )

    # --- ZAMAN PENCERESİ VE MESAİ LİMİTLERİ (A4) ---
    # (i) Ekip t musteri i icin yetkin degilse kisit HIC yazilmaz.
    # (ii) Yetkin ama ziyaret etmiyorsa Big-M ile gevsetilir.
    for i in C:
        for t in T:
            if t not in Ti_set.get(i, set()):
                continue
            if (0, i) in tt:
                big_m_16 = max(0.0, float(es[t]) + float(tt[0, i]))
                m.addConstr(
                    tau[i, t] - tt[0, i] >= es[t] - big_m_16 * (1 - visit_expr(i, t)),
                    name=f"c16_{i}_{t}"
                )

    for i in C:
        for t in T:
            if t not in Ti_set.get(i, set()):
                continue
            if (i, 0) in A and (i, 0) in tt:
                st_i = st.get(i, 0.0)
                tt_i0 = tt.get((i, 0), 0.0)
                big_m_17 = max(0.0, tau_ub[i] + st_i + tt_i0 + break_duration - float(ls[t]))
                m.addConstr(
                    tau[i, t] + st_i + tt_i0 + w[i, 0, t] * break_duration
                    <= ls[t] + big_m_17 * (1 - visit_expr(i, t)),
                    name=f"c17_{i}_{t}"
                )

    for i in C:
        for t in T:
            if t not in Ti_set.get(i, set()):
                continue
            big_m_18 = max(0.0, float(ec[i]))
            m.addConstr(
                ec[i] <= tau[i, t] + big_m_18 * (1 - visit_expr(i, t)),
                name=f"c18_lb_{i}_{t}"
            )
            # c18_ub tau'nun kutu ust siniri ile ayni; kosulsuz kalmasi guvenli.
            m.addConstr(tau[i, t] <= lc[i], name=f"c18_ub_{i}_{t}")

    # ------------------------------------------------------------------
    # A6: TEKNISYEN CAKISMA ONLEME (non-overlap) - EV_v.1.1.py satir 225-299'dan
    # portlanmistir. Ayni teknisyen birden fazla ekipte (tekil + ikili kombinasyon)
    # yer alabilir; ancak bu ekiplerin rotalari zaman icinde cakisamaz.
    # ------------------------------------------------------------------
    if crew_members:
        nonoverlap_M = horizon_end + break_duration

        route_start = m.addVars(T, lb=0.0, ub=horizon_end, vtype=GRB.CONTINUOUS, name="route_start")
        route_end = m.addVars(
            T, lb=0.0, ub=horizon_end + break_duration, vtype=GRB.CONTINUOUS, name="route_end"
        )

        for t in T:
            m.addConstr(route_start[t] <= horizon_end * y_route[t], name=f"route_start_gate_{t}")
            m.addConstr(
                route_end[t] <= (horizon_end + break_duration) * y_route[t],
                name=f"route_end_gate_{t}"
            )
            m.addConstr(route_end[t] >= route_start[t], name=f"route_seq_{t}")

            # route_start'i secilen cikis yayina bagla.
            for j in N0:
                if j == 0:
                    continue
                if (0, j) not in tt:
                    continue
                for kk in K_of_crew[t]:
                    if (0, j, kk) in XK_set:
                        expr_dep = tau[j, t] - tt[0, j]
                        m.addConstr(
                            route_start[t] >= expr_dep - nonoverlap_M * (1 - x[0, j, kk]),
                            name=f"route_start_lb_{t}_{kk}_{j}"
                        )
                        m.addConstr(
                            route_start[t] <= expr_dep + nonoverlap_M * (1 - x[0, j, kk]),
                            name=f"route_start_ub_{t}_{kk}_{j}"
                        )

            # route_end'i secilen donus yayina bagla.
            for i in N0:
                if i == 0:
                    continue
                if (i, 0) not in tt:
                    continue
                for kk in K_of_crew[t]:
                    if (i, 0, kk) in XK_set:
                        expr_ret = (
                            tau[i, t] + st.get(i, 0.0) + tt[i, 0]
                            + break_duration * w[i, 0, t]
                        )
                        m.addConstr(
                            route_end[t] >= expr_ret - nonoverlap_M * (1 - x[i, 0, kk]),
                            name=f"route_end_lb_{t}_{kk}_{i}"
                        )
                        m.addConstr(
                            route_end[t] <= expr_ret + nonoverlap_M * (1 - x[i, 0, kk]),
                            name=f"route_end_ub_{t}_{kk}_{i}"
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
                    name=f"noov_1_{tech}_{c1}_{c2}"
                )
                m.addConstr(
                    route_start[c1] >= route_end[c2] - nonoverlap_M * order - inactive_relax,
                    name=f"noov_2_{tech}_{c1}_{c2}"
                )

    # --- YAKIT TAKİBİ (A2: (dugum, k) indisli) ---
    for (i, j, kk) in XK:
        if i == 0 or j == 0:
            continue
        m.addConstr(yc[j, kk] >= 0, name=f"c20_lb_{i}_{j}_{kk}")
        m.addConstr(
            yc[j, kk] <= yc[i, kk] - (hc_of_k[kk] * d[i, j]) * x[i, j, kk]
            + G_of_k[kk] * (1 - x[i, j, kk]),
            name=f"c20_ub_{i}_{j}_{kk}"
        )

    for (i, j, kk) in XK:
        if i == 0 or j == 0:
            continue
        m.addConstr(yc[j, kk] >= 0, name=f"c21_lb_{i}_{j}_{kk}")
        m.addConstr(
            yc[j, kk] <= YC[i, kk] - (hc_of_k[kk] * d[i, j]) * x[i, j, kk]
            + G_of_k[kk] * (1 - x[i, j, kk]),
            name=f"c21_ub_{i}_{j}_{kk}"
        )

    for i in N0:
        if i == 0:
            continue
        for kk in KK:
            m.addConstr(YC[i, kk] == yc[i, kk], name=f"c22_no_refuel_{i}_{kk}")
            m.addConstr(YC[i, kk] <= G_of_k[kk], name=f"c22_ub_{i}_{kk}")

    for i in N0:
        if i == 0:
            continue
        for kk in KK:
            if (i, 0, kk) in XK_set:
                m.addConstr(
                    yc[i, kk] >= (hc_of_k[kk] * d.get((i, 0), 0.0)) * x[i, 0, kk],
                    name=f"c_return_fuel_{i}_{kk}"
                )

    # C2 (tight Big-M) #3: depodan tam dolu cikis.
    for j in N0:
        if j == 0:
            continue
        for kk in KK:
            if (0, j, kk) in XK_set:
                depart_use = hc_of_k[kk] * d.get((0, j), 0.0)
                big_m_full = max(0.0, G_of_k[kk] - depart_use)
                m.addConstr(
                    yc[j, kk] <= G_of_k[kk] - depart_use * x[0, j, kk],
                    name=f"c_full_depot_ub_{j}_{kk}"
                )
                m.addConstr(
                    yc[j, kk] >= G_of_k[kk] - depart_use - big_m_full * (1 - x[0, j, kk]),
                    name=f"c_full_depot_lb_{j}_{kk}"
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


def print_cv_solution(data, model):
    if model.SolCount == 0:
        print("Çözüm yok veya uygun değil.")
        return

    x = model._x
    tau = model._tau
    w_vars = model._w
    d = data['d']
    tt = data['tt']
    st = data['st']
    node_labels = data.get('node_labels', {})

    # A2+C1: x artik x[i, j, k] indisli; k -> (arac, ekip) esleme uzerinden cozulur.
    K_pairs = getattr(model, "_K_pairs", [])
    routes = {}
    for (i, j, kk), var in x.items():
        if var.X > 0.5:
            v, t = K_pairs[kk]
            routes.setdefault((v, t, kk), []).append((i, j))

    print("\n" + "=" * 65)
    print("               GÜNLÜK OPERASYON DETAYLI ZAMAN ÇİZELGESİ")
    print("=" * 65)

    for (v, t, kk), arcs in sorted(routes.items()):
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
        ekip_isimleri = t.replace('_', ' & ')

        print(f"📌 {v} ARACI OPERASYON RAPORU")
        print(f"  👷 Ekip           : {ekip_isimleri}")
        print(f"  📏 Toplam Mesafe  : {total_distance:.2f} metre")
        print(f"  🕒 Kronolojik Zaman Çizelgesi ve Akışı:")

        for idx in range(len(route)):
            curr_node = route[idx]
            node_name = node_labels.get(curr_node, str(curr_node))

            if idx == 0:
                start_val = tau[0, t].X if (0, t) in tau else 0.0
                print(f"     [ {format_time(start_val)} ] ➔ Depodan Çıkış yapıldı. Nokta: {curr_node} ({node_name})")
            elif idx == len(route) - 1:
                prev_node = route[idx - 1]
                end_val = tau[prev_node, t].X + st.get(prev_node, 0.0) + tt.get((prev_node, 0), 0.0)

                # EĞER DÖNÜŞ YOLUNDA MOLA VERİLDİYSE
                if w_vars[prev_node, curr_node, t].X > 0.5:
                    mola_bas = tau[prev_node, t].X + st.get(prev_node, 0.0)
                    mola_bit = mola_bas + 3600
                    print(
                        f"     ☕ [ {format_time(mola_bas)} - {format_time(mola_bit)} ] Yolda Öğle Molası (1 Saat) Kullanıldı.")
                    end_val += 3600  # Molayı bitiş saatine ekle

                leg_dist = d.get((prev_node, curr_node), 0.0)
                print(f"     |                     └─── Son Müşteriden Yolculuk Mesafe: {leg_dist:.1f} m")
                print(f"     [ {format_time(end_val)} ] 🏁 Depoya Dönüş sağlandı. Nokta: {curr_node} ({node_name})")
            else:
                arr_val = tau[curr_node, t].X
                srv_val = st.get(curr_node, 0.0)
                srv_min = int(srv_val // 60)
                dep_val = arr_val + srv_val

                prev_node = route[idx - 1]
                leg_dist = d.get((prev_node, curr_node), 0.0)

                # EĞER MÜŞTERİYE GELMEDEN ÖNCE MOLA VERİLDİYSE
                if w_vars[prev_node, curr_node, t].X > 0.5:
                    if prev_node == 0:
                        mola_bas = tau[0, t].X if (0, t) in tau else 0.0
                    else:
                        mola_bas = tau[prev_node, t].X + st.get(prev_node, 0.0)
                    mola_bit = mola_bas + 3600
                    print(
                        f"     ☕ [ {format_time(mola_bas)} - {format_time(mola_bit)} ] Yolda Öğle Molası (1 Saat) Kullanıldı.")

                print(f"     |                     └─── Yolculuk Mesafe: {leg_dist:.1f} m")
                print(f"     [ {format_time(arr_val)} ] ➔ Müşteriye Varış. Nokta: {curr_node} ({node_name})")
                print(
                    f"               ↳ Hizmet Detayı : İş Süresi: {srv_min} dakika | Ayrılış Saati: {format_time(dep_val)}")

        start_time = tau[0, t].X if (0, t) in tau else 0.0
        last_customer = route[-2]
        end_time = tau[last_customer, t].X + st.get(last_customer, 0.0) + tt.get((last_customer, 0), 0.0)

        if w_vars[last_customer, route[-1], t].X > 0.5:
            end_time += 3600  # Dönüşte mola verildiyse toplam süreye ekle

        total_duration = end_time - start_time
        duration_h = int(total_duration // 3600)
        duration_m = int((total_duration % 3600) // 60)
        print(f"  ⏳ Rota Toplam Süresi: {duration_h} saat {duration_m} dakika")
        print("-" * 65)


SRC_ROOT = os.path.dirname(os.path.abspath(__file__))


def resolve_data_root() -> str:
    """Veri (XML) kokunu bul. src/ altinda veri yoksa salt-okunur raw/ kullanilir."""
    if os.path.isdir(os.path.join(SRC_ROOT, "trsp_problem_sets")):
        return SRC_ROOT
    candidate = os.path.join(os.path.dirname(SRC_ROOT), "raw")
    if os.path.isdir(os.path.join(candidate, "trsp_problem_sets")):
        return candidate
    return SRC_ROOT


def select_instances(instances: dict) -> dict:
    base_names = sorted({os.path.splitext(os.path.basename(k))[0] for k in instances})
    print("Mevcut problemler:")
    print(", ".join(base_names))
    selected = input(
        "Çalıştırmak istediğiniz problem adlarını girin (virgülle ayırın, örn. C5,R5,RC5). Enter = tümü: "
    ).strip()
    if not selected:
        return instances

    keys = []
    chosen = {item.strip() for item in selected.split(',') if item.strip()}
    for key in sorted(instances):
        base = os.path.splitext(os.path.basename(key))[0]
        if base in chosen:
            keys.append(key)

    if not keys:
        raise ValueError(f"Seçilen problem kodlarına uygun dosya bulunamadı: {selected}")
    return {key: instances[key] for key in keys}


if __name__ == "__main__":
    # Veri raw/ altindan OKUNUR; tum ciktilar src/ altina yazilir (raw/ salt-okunur).
    root = resolve_data_root()
    outputs_dir = os.path.join(SRC_ROOT, "sonuclar")
    os.makedirs(outputs_dir, exist_ok=True)
    problem_dirs = ["trsp_problem_sets"]
    instances = load_problem_instances(root, problem_dirs)

    if not instances:
        raise ValueError("trsp_problem_sets klasöründe XML problem dosyası bulunamadı.")

    instances = select_instances(instances)
    vehicle_file = os.path.join(root, "FC_Info4Vehicle4CV.xml")
    vehicles, vehicle_attrs = parse_vehicle_file(vehicle_file, expected_type="CV")

    # 1. INFO4EMPLOYEE'DEN YETKİNLİK VE TEKNİSYEN LİSTESİNİ OKU
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
            "s5": ["TECH_008"]
        }

    for instance_name, instance in instances.items():
        print(f"\n== {instance_name} için model kuruluyor ==")

        data = prepare_cv_data_from_instance(
            instance,
            vehicles,
            vehicle_attrs,
            technicians=all_technicians,
        )

        data['lc0'] = 100000.0

        # 2. XML'DEN MÜŞTERİLERİN İSTEDİĞİ YETKİNLİKLERİ ÇIKAR
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
            print(f"Uyarı: {instance_name} okunurken hata oluştu. Hata: {e}")

        # 3. ARAÇ PAYLAŞIM MANTIĞI: TEKNİSYENLERİ 1'Lİ VE 2'Lİ EKİPLER HALİNDE KOMBİNE ET
        req_skills_unique = list(set(delivery_skills))
        active_techs = []
        tech_to_skill = {}

        for skill in req_skills_unique:
            if skill in skill_tech_map and skill_tech_map[skill]:
                tech = skill_tech_map[skill][0]
                active_techs.append(tech)
                tech_to_skill[tech] = skill

        T_list = []
        crew_skills = {}
        crew_members = {}

        for tech in active_techs:
            T_list.append(tech)
            crew_skills[tech] = {tech_to_skill[tech]}
            crew_members[tech] = [tech]

        for t1, t2 in itertools.combinations(active_techs, 2):
            crew_name = f"{t1}_{t2}"
            T_list.append(crew_name)
            crew_skills[crew_name] = {tech_to_skill[t1], tech_to_skill[t2]}
            crew_members[crew_name] = [t1, t2]

        data['T'] = T_list
        # A6: hangi teknisyenin hangi ekiplerde yer aldigi bilgisi non-overlap
        # bloguna girdi olur (EV_v.1.1.py satir 693/700 desenine paralel).
        data['crew_members'] = crew_members

        base_es = data['es'][all_technicians[0]] if all_technicians else 0.0
        base_ls = data['ls'][all_technicians[0]] if all_technicians else 32400.0
        base_el = data['el'][all_technicians[0]] if all_technicians else 14400.0
        base_ll = data['ll'][all_technicians[0]] if all_technicians else 21600.0

        data['es'] = {crew: base_es for crew in T_list}
        data['ls'] = {crew: base_ls for crew in T_list}
        data['el'] = {crew: base_el for crew in T_list}
        data['ll'] = {crew: base_ll for crew in T_list}

        C = sorted(data['C'])
        for idx, c_idx in enumerate(C):
            if idx < len(delivery_skills):
                req_skill = delivery_skills[idx]
                allowed_crews = []
                for crew in T_list:
                    if req_skill in crew_skills[crew]:
                        allowed_crews.append(crew)
                data['Ti'][c_idx] = allowed_crews
            else:
                data['Ti'][c_idx] = T_list[:]

        model = build_model(**data)
        model.update()

        out_name = os.path.splitext(os.path.basename(instance_name))[0]
        lp_name = os.path.join(outputs_dir, f"exact_model_{out_name}.lp")
        model.write(lp_name)
        print(f"Model kuruldu ve '{lp_name}' olarak yazildi.")

        # ZAMAN SINIRI: Model maksimum 15 dakika çalışsın
        model.Params.TimeLimit = 900

        model.optimize()
        print(f"Çözüm durumu: {model.Status}")
        print_cv_solution(data, model)