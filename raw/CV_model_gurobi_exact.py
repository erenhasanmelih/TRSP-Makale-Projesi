import os
import itertools
import gurobipy as gp
from gurobipy import GRB
import xml.etree.ElementTree as ET
from xml_data_loader import (
    load_problem_instances,
    parse_vehicle_file,
    prepare_cv_data_from_instance,
)


def build_model(
        N, N0, C, Vc, V, T, Ti, Fc, A,
        d, tt, st, G, ec, lc, es, ls, el, ll, h_c, g_c, k, lc0,
        node_labels=None
):
    m = gp.Model("exact_model")

    # Karar Değişkenleri (Gereksiz z ve z0 silindi, model hafifletildi)
    x = m.addVars(A, V, T, vtype=GRB.BINARY, name="x")
    tau = m.addVars(N0, T, lb=0.0, vtype=GRB.CONTINUOUS, name="tau")
    L = m.addVars(N0, T, lb=0.0, vtype=GRB.CONTINUOUS, name="L")
    YC = m.addVars(N0, lb=0.0, vtype=GRB.CONTINUOUS, name="YC")
    yc = m.addVars(N0, lb=0.0, vtype=GRB.CONTINUOUS, name="yc")
    w = m.addVars(A, T, vtype=GRB.BINARY, name="w")
    alpha = m.addVars(Fc, Vc, lb=0.0, vtype=GRB.CONTINUOUS, name="alpha")

    # Çıktı için karar değişkenlerini kaydetme
    m._x = x
    m._tau = tau
    m._w = w
    m._A = A
    m._V = V
    m._T = T

    # Amaç Fonksiyonu: Toplam Mesafeyi Minimize Et
    m.setObjective(
        gp.quicksum(d[i, j] * x[i, j, v, t] for (i, j) in A for v in V for t in T),
        GRB.MINIMIZE
    )

    # c2: HER MÜŞTERİYE SADECE YETKİNLİĞİ OLAN EKiP GİREBİLİR
    for j in C:
        m.addConstr(
            gp.quicksum(x[i, j, v, t] for i in N0 for v in V for t in Ti[j] if (i, j) in A) == 1,
            name=f"c2_{j}"
        )

    for i, j in A:
        m.addConstr(gp.quicksum(x[i, j, v, t] for v in V for t in T) <= 1, name=f"c3_{i}_{j}")

    for v in V:
        m.addConstr(gp.quicksum(x[0, j, v, t] for j in N0 for t in T if (0, j) in A) <= 1, name=f"c4_{v}")

    for t in T:
        m.addConstr(gp.quicksum(x[0, j, v, t] for j in N0 for v in V if (0, j) in A) <= 1, name=f"c5_{t}")

    for i in N0:
        for v in V:
            for t in T:
                m.addConstr(
                    gp.quicksum(x[i, j, v, t] for j in N0 if (i, j) in A)
                    - gp.quicksum(x[j, i, v, t] for j in N0 if (j, i) in A) == 0,
                    name=f"c6_{i}_{v}_{t}"
                )

    # --- ZAMAN VE MOLA İLERLEMESİ ---
    # Modelin 0. Saniyesi sabah 08:00'dir.
    break_duration = 3600  # Tam 1 Saat
    break_min = 13800  # 11:50 (+10/-10 dk tolerans alt sınırı)
    break_max = 15000  # 12:10 (+10/-10 dk tolerans üst sınırı)

    for i, j in A:
        if j == 0: continue
        for v in V:
            for t in T:
                m.addConstr(
                    tau[i, t]
                    + st.get(i, 0.0)
                    + w[i, j, t] * break_duration  # Eğer mola bu aralıkta verilirse 1 saat zaman ekle
                    + tt[i, j] * x[i, j, v, t]
                    - 100000.0 * (1 - x[i, j, v, t])
                    <= tau[j, t],
                    name=f"c8_zaman_ilerleme_{i}_{j}_{v}_{t}"
                )

    # --- ESNEK MOLA KURALLARI YEPYENİ BLOK ---
    for t in T:
        sum_w = gp.quicksum(w[i, j, t] for (i, j) in A)

        # 1. En fazla 1 mola verilebilir
        m.addConstr(
            sum_w <= gp.quicksum(x[0, i, v, t] for i in N0 for v in V if (0, i) in A),
            name=f"mola_max1_{t}"
        )

        # 2. Eğer Mola VERİLMEDİYSE, mesai (depoya dönüş) en geç 12:10'da bitmek zorundadır.
        for i in N0:
            if i == 0: continue
            for v in V:
                if (i, 0) in A:
                    m.addConstr(
                        tau[i, t] + st.get(i, 0.0) + tt.get((i, 0), 0.0)
                        <= break_max + 100000.0 * (1 - x[i, 0, v, t] + sum_w),
                        name=f"mola_yoksa_erken_donus_{i}_{v}_{t}"
                    )

    for i, j in A:
        for t in T:
            # Mola sadece iki nokta arasında geçiş varsa verilebilir
            m.addConstr(
                w[i, j, t] <= gp.quicksum(x[i, j, v, t] for v in V),
                name=f"mola_yol_ustu_onayi_{i}_{j}_{t}"
            )

            # 3. Mola VERİLDİYSE, molanın başlama saati tolerans aralığında (11:50 - 12:10) olmak zorundadır.
            m.addConstr(
                tau[i, t] + st.get(i, 0.0) >= break_min - 100000.0 * (1 - w[i, j, t]),
                name=f"mola_baslama_alt_sinir_{i}_{j}_{t}"
            )
            m.addConstr(
                tau[i, t] + st.get(i, 0.0) <= break_max + 100000.0 * (1 - w[i, j, t]),
                name=f"mola_baslama_ust_sinir_{i}_{j}_{t}"
            )

    # --- ZAMAN PENCERESİ VE MESAİ LİMİTLERİ ---
    for i in C:
        for t in T:
            if (0, i) in tt:
                m.addConstr(tau[i, t] - tt[0, i] >= es[t], name=f"c16_{i}_{t}")

    for i in C:
        for t in T:
            if (i, 0) in A and (i, 0) in tt:
                m.addConstr(
                    tau[i, t] + st.get(i, 0.0) + tt.get((i, 0), 0.0) + w[i, 0, t] * break_duration <= ls[t],
                    name=f"c17_{i}_{t}"
                )

    for i in C:
        for t in T:
            m.addConstr(ec[i] <= tau[i, t], name=f"c18_lb_{i}_{t}")
            m.addConstr(tau[i, t] <= lc[i], name=f"c18_ub_{i}_{t}")

    # --- YAKIT TAKİBİ ---
    for i, j in A:
        if i == 0 or j == 0: continue
        for v in Vc:
            for t in T:
                m.addConstr(yc[j] >= 0, name=f"c20_lb_{i}_{j}_{v}_{t}")
                m.addConstr(
                    yc[j] <= yc[i] - (h_c * d[i, j]) * x[i, j, v, t] + G[v] * (1 - x[i, j, v, t]),
                    name=f"c20_ub_{i}_{j}_{v}_{t}"
                )

    for i, j in A:
        if i == 0 or j == 0: continue
        for v in Vc:
            for t in T:
                m.addConstr(yc[j] >= 0, name=f"c21_lb_{i}_{j}_{v}_{t}")
                m.addConstr(
                    yc[j] <= YC[i] - (h_c * d[i, j]) * x[i, j, v, t] + G[v] * (1 - x[i, j, v, t]),
                    name=f"c21_ub_{i}_{j}_{v}_{t}"
                )

    for i in N0:
        if i == 0: continue
        m.addConstr(YC[i] == yc[i], name=f"c22_no_refuel_{i}")
        for v in Vc:
            m.addConstr(YC[i] <= G[v], name=f"c22_ub_{i}_{v}")

    for i in N0:
        if i == 0: continue
        for v in Vc:
            for t in T:
                if (i, 0) in A:
                    m.addConstr(
                        yc[i] >= (h_c * d.get((i, 0), 0.0)) * x[i, 0, v, t],
                        name=f"c_return_fuel_{i}_{v}_{t}"
                    )

    for j in N0:
        if j == 0: continue
        for v in Vc:
            for t in T:
                if (0, j) in A:
                    m.addConstr(
                        yc[j] <= G[v] - (h_c * d.get((0, j), 0.0)) * x[0, j, v, t] + 100000.0 * (1 - x[0, j, v, t]),
                        name=f"c_full_depot_ub_{j}_{v}_{t}"
                    )
                    m.addConstr(
                        yc[j] >= G[v] - (h_c * d.get((0, j), 0.0)) - 100000.0 * (1 - x[0, j, v, t]),
                        name=f"c_full_depot_lb_{j}_{v}_{t}"
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

    routes = {}
    for (i, j, v, t), var in x.items():
        if var.X > 0.5:
            routes.setdefault((v, t), []).append((i, j))

    print("\n" + "=" * 65)
    print("               GÜNLÜK OPERASYON DETAYLI ZAMAN ÇİZELGESİ")
    print("=" * 65)

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
    root = os.path.dirname(__file__)
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

        for tech in active_techs:
            T_list.append(tech)
            crew_skills[tech] = {tech_to_skill[tech]}

        for t1, t2 in itertools.combinations(active_techs, 2):
            crew_name = f"{t1}_{t2}"
            T_list.append(crew_name)
            crew_skills[crew_name] = {tech_to_skill[t1], tech_to_skill[t2]}

        data['T'] = T_list

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
        lp_name = f"exact_model_{out_name}.lp"
        model.write(lp_name)
        print(f"Model kuruldu ve '{lp_name}' olarak yazildi.")

        # ZAMAN SINIRI: Model maksimum 15 dakika çalışsın
        model.Params.TimeLimit = 900

        model.optimize()
        print(f"Çözüm durumu: {model.Status}")
        print_cv_solution(data, model)