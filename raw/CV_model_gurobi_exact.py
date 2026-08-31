import os
import sys
import itertools
import gurobipy as gp
from gurobipy import GRB
import xml.etree.ElementTree as ET
from xml_data_loader import (
    load_problem_instances,
    parse_vehicle_file,
    prepare_cv_data_from_instance,
)

# ---------------------------------------------------------------------------
# Bu dosya, tez taslağının 3.4.1 (Konvansiyonel Araç Modeli) bölümündeki
# matematiksel modelin birebir Gurobi/Python karşılığıdır. Her kısıt bloğunun
# üzerindeki yorumda ilgili denklem numarası (CV-1 ... CV-25) belirtilmiştir.
# Karşılaştırma için bkz. "hasan taslak makale 1.docx", Bölüm 3.4.1.
#
# v1 (x_i,j,v,t, 4 boyutlu, ham Big-M=100000) sürümü referans için
# "CV_model_gurobi_exact - yedek (v1, x_ijvt).py" olarak saklanmıştır.
# ---------------------------------------------------------------------------


def build_model(
        N, N0, C, Vc, V, T, Ti, Fc, A,
        d, tt, st, G, ec, lc, es, ls, el, ll, h_c, g_c, k, lc0,
        a_max=None,
        node_labels=None,
        crew_members=None,
        R_max=3,
        R_max_by_tech=None,
        R_max_info=None
):
    m = gp.Model("CV_exact_model_v3_clone")

    # crew_members: her ekip kimliğinin (t) hangi HAM teknisyenlerden
    # oluştuğunu gösterir (örn. {"TECH_001_TECH_007": {"TECH_001",
    # "TECH_007"}}). Verilmezse her t kendi başına atomik bir teknisyen
    # kabul edilir (geriye dönük uyumluluk). Bu bilgi olmadan bir
    # teknisyenin AYNI ANDA hem tek başına hem bir ikilinin parçası olarak
    # kullanılmasını engellemek mümkün değildir (bkz. Kısıt CV-28).
    if crew_members is None:
        crew_members = {t: {t} for t in T}

    # a_max (maksimum dolum süresi) mevcut veri hazırlama katmanında
    # (xml_data_loader.prepare_cv_data_from_instance) henüz ayrı bir
    # parametre olarak sağlanmıyor; Fc gerçek bir istasyon içermediği
    # sürece (bkz. aşağıdaki not) bu değerin etkisi yoktur.
    if a_max is None:
        a_max = lc0

    # ------------------------------------------------------------------
    # Kaynak kümesi K = V x T  (3.4.1 Kümeler: "K ⊆ V×T ... K = V×T")
    # x_i,j,v,t (4 boyutlu) yerine x_i,j,k (3 boyutlu) kullanılmasını
    # sağlayan indis düşürme burada uygulanır (Acar & Altın, 2025).
    # k = (v, t) ikilisi tek bir "sefer kaynağı"nı temsil eder.
    #
    # Ö2 (2026-08-28, sorun_rc13_darbogaz_kok_neden_analizi.md): HOMOJEN
    # FİLODA ARAÇ İNDİSİNİ KALDIR. EV_v.1.1.py'deki aynı bloğun CV
    # karşılığı, birebir aynı gerekçe (bkz. o dosyadaki açıklama): filodaki
    # tüm araçlar aynı menzile (G) sahipse K=V×T yerine K=T kullanılır,
    # "en fazla |V| ekip aynı anda aktif" kısıtı (CV-27'nin agregatize
    # hâli) fiziksel araç sayısını korur. Heterojen filoda otomatik olarak
    # K=V×T'ye GERİ DÖNER.
    # ------------------------------------------------------------------
    aggregate_fleet = (G is not None and len(G) > 0
                        and len({round(float(_gv), 6) for _gv in G.values()}) <= 1)
    if aggregate_fleet:
        K = list(T)
    else:
        K = [(v, t) for v in V for t in T]

    def _t_of(kk):
        return kk[1] if isinstance(kk, tuple) else kk

    _G_const = next(iter(G.values())) if G else 0.0

    def _Gk(kk):
        return _G_const if aggregate_fleet else G[kk[0]]

    # kk_name: Gurobi kısıt/değişken isimlerinde k=(v,t) tuple'ının ham
    # Python string hali ("('EV_1', 'TECH_008')" gibi boşluk/tırnak/parantez
    # içeren) kullanılamaz — büyük modellerde bu, .lp dosyası yazarken
    # isim çakışmasına ve "Unable to write to file" hatasına yol açtığı
    # test sırasında tespit edildi. Temiz, alt-çizgili bir isim üretilir.
    # Aggregate modda kk zaten temiz bir string (crew id) olduğundan
    # doğrudan kullanılır.
    kk_name = {kk: (str(kk) if aggregate_fleet else f"{kk[0]}_{kk[1]}") for kk in K}

    def _clean_part(p):
        return kk_name[p] if isinstance(p, tuple) else str(p)

    def _rename(var_dict, prefix):
        # Gurobi'nin addVars() ile otomatik ürettiği isimler, kk gibi bir
        # tuple içeren indislerde ham Python tuple string'ini kullanır
        # ("x[0,1,('EV_1', 'TECH_008')]") ve bu, .lp dosyası yazarken
        # isim çakışmasına yol açar. Her değişkenin adı burada temiz,
        # alt-çizgili bir biçimle yeniden yazılır.
        for key, var in var_dict.items():
            parts = key if isinstance(key, tuple) else (key,)
            var.VarName = f"{prefix}[{','.join(_clean_part(p) for p in parts)}]"

    # Ti artık K üzerinde tanımlı: her müşteri için yetkinliği uygun
    # (araç, ekip) ikilileri (3.4.1 Kümeler: "Ti ⊆ K").
    # Ö2 UYUMU: aggregate modda kk = t (skaler) olduğundan Ti_K de aynı
    # şekilde skaler listesi olmalı — aksi hâlde Ö1'in yetkinlik filtresi
    # (kk in Ti_K[j]) hiçbir zaman eşleşmez ve TÜM x/w yanlışlıkla UB=0'a
    # sabitlenir.
    if aggregate_fleet:
        Ti_K = {j: list(Ti.get(j, [])) for j in C}
    else:
        Ti_K = {j: [(v, t) for v in V for t in Ti.get(j, [])] for j in C}

    # NOT: xml_data_loader.prepare_cv_data_from_instance şu an Fc'yi [0]
    # (depo) olarak döndürüyor; gerçek bir yakıt istasyonu ağı henüz veri
    # setine dahil edilmemiştir. Kısıt (CV-6),(CV-7),(CV-11),(CV-17) bu
    # yüzden s != 0 filtresiyle yazılmıştır: yapısal olarak modele hazır
    # tutulmuş, ancak mevcut veri setinde devre dışıdır (boş döngü).
    real_stations = [s for s in Fc if s != 0]

    # ------------------------------------------------------------------
    # DEPO KLON DÜĞÜMLERİ (2026-08-23) — sefer-indeksli zaman değişkeni.
    #
    # Sorun: tau[0,k] KAYNAK BAŞINA TEK bir skalerdi ve CV-8'in j=0 hâli
    # tarafından "depoya dönüş zamanı" olarak sabitleniyordu; bu yüzden
    # aynı kaynağın 2./3. seferi zaman olarak çakışabiliyordu (R10 ve
    # RC10'da solution_validator.py ile fiilen gözlendi: her iki sefer de
    # tau=0.0'da başlıyordu). Bkz. eski "CV-26 geri alındı" notu.
    #
    # Çözüm: fiziksel 0 düğümü, her sefer r için AYRI bir ÇIKIŞ klonu
    # (O[r], yalnızca ÇIKAN yay) ve AYRI bir DÖNÜŞ klonu (E[r], yalnızca
    # GİREN yay) ile değiştirilir. tau[O[r],k] ve tau[E[r],k] artık FARKLI
    # değişkenler olduğundan CV-29 (sefer sırası) ve CV-31 (depodan çıkış
    # zaman ilerlemesi) döngüsel çelişki üretmeden yazılabilir.
    #
    # Kasıtlı olarak YOK: O'ya giren yay, E'den çıkan yay, O[r]->E[r] yayı.
    # Böylece hiçbir altur bir depo klonunu içeremez (formülasyon sıkılaşır)
    # ve "boş sefer" bir yayla değil u[r,k]=0 ile temsil edilir.
    #
    # Ayrıntılı tasarım/gerekçe:
    # decisions/karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani.md
    # ------------------------------------------------------------------
    # R_max artık SABİT 3 DEĞİL: xml_data_loader.derive_r_max tarafından
    # veriden türetilir ve prepare_cv_data_from_instance sözlüğünde
    # data['R_max'] olarak gelir (build_model(**data) ile buraya taşınır).
    # Türetim, optimal çözümü kesmeyen KANITLANABİLİR bir üst sınırdır;
    # gerekçe için bkz. decisions/karar_r_max_dinamik_turetme.md.
    # Argüman verilmezse eski davranış (3) korunur.
    R_max = max(1, int(R_max))
    R = list(range(1, R_max + 1))
    Cs = [i for i in N0 if i != 0]              # müşteri (+ ileride istasyon)
    _base = max(N0) + 1
    O = {r: _base + (r - 1) for r in R}         # depo ÇIKIŞ klonları
    E = {r: _base + R_max + (r - 1) for r in R}  # depo DÖNÜŞ klonları
    clones = set(O.values()) | set(E.values())
    Nt = Cs + [O[r] for r in R] + [E[r] for r in R]

    A_set = set(A)
    At = [(i, j) for i in Cs for j in Cs if (i, j) in A_set]
    At += [(O[r], j) for r in R for j in Cs if (0, j) in A_set]
    At += [(i, E[r]) for r in R for i in Cs if (i, 0) in A_set]
    At_set = set(At)

    # Parametreler klonlara fiziksel depodan TAKMA AD (alias) ile taşınır.
    # Çağıranın data sözlüğü DEĞİŞTİRİLMEZ (yerel kopya alınır).
    d = dict(d)
    tt = dict(tt)
    st = dict(st)
    ec = dict(ec)
    lc = dict(lc)
    for r in R:
        o_r, e_r = O[r], E[r]
        st[o_r] = 0.0
        st[e_r] = 0.0
        ec[o_r] = ec.get(0, 0.0)
        ec[e_r] = ec.get(0, 0.0)
        lc[o_r] = lc.get(0, 0.0)
        lc[e_r] = lc.get(0, 0.0)
        for j in Cs:
            if (0, j) in A_set:
                d[o_r, j] = d[0, j]
                tt[o_r, j] = tt[0, j]
            if (j, 0) in A_set:
                d[j, e_r] = d[j, 0]
                tt[j, e_r] = tt[j, 0]
        # CV-15/CV-16 içindeki tt[0,i] / tt[i,0] terimleri klonlarda 0'dır
        # (klon zaten depodadır).
        tt[0, o_r] = 0.0
        tt[o_r, 0] = 0.0
        tt[0, e_r] = 0.0
        tt[e_r, 0] = 0.0

    # Ö4b (2026-08-29, sorun_rc13_darbogaz_kok_neden_analizi.md §6 Ö4) —
    # arc_fix: zaman penceresi tutarsız yayları At'ten (dolayısıyla
    # x/w/Ö1 UB=0 döngüsünün tamamından) tamamen çıkar. i'den en erken
    # ayrılış + seyahat süresi, j'nin en geç varış sınırını aşıyorsa bu yay
    # HİÇBİR fizibıl çözümde kullanılamaz — bu argüman mola varsayımından
    # BAĞIMSIZDIR (yalnızca CV-18'in ham [ec,lc] pencerelerini ve seyahat
    # tutarlılığını kullanır), dolayısıyla CV'de de EV'deki gibi GÜVENLİ.
    #
    # NOT — `bwp` (mola penceresi yayılımı, EV-only Ö4a) CV'ye BİLEREK
    # TAŞINMADI: CV'nin molası (CV-13) OPSİYONELDİR, bir CV kaynağı molayı
    # hiç kullanmayarak (Σw=0) EV'deki "ec_i+st_i>el ⇒ tau_i>=ll" zorlama
    # zincirini önleyebilir. Bu yayılımı CV'ye uygulamak fizibıl bir
    # "molasız" çözümü YANLIŞLIKLA kesebilirdi. arc_fix bu riski taşımaz
    # çünkü molayla hiç ilgilenmez.
    At = [
        (i, j) for (i, j) in At
        if ec.get(i, 0.0) + st.get(i, 0.0) + tt.get((i, j), 0.0) <= lc.get(j, float('inf')) + 1e-9
    ]
    At_set = set(At)

    # Karar Değişkenleri ---------------------------------------------------
    x = m.addVars([(i, j, kk) for (i, j) in At for kk in K], vtype=GRB.BINARY, name="x")
    tau = m.addVars([(i, kk) for i in Nt for kk in K], lb=0.0, vtype=GRB.CONTINUOUS, name="tau")
    YC = m.addVars(Nt, lb=0.0, vtype=GRB.CONTINUOUS, name="YC")
    yc = m.addVars(Nt, lb=0.0, vtype=GRB.CONTINUOUS, name="yc")
    w = m.addVars([(i, j, kk) for (i, j) in At for kk in K], vtype=GRB.BINARY, name="w")

    # Ö1 (2026-08-28, sorun_rc13_darbogaz_kok_neden_analizi.md): YETKİNLİK
    # FİLTRESİNİ x/w ÜZERİNDE UYGULA — EV_v.1.1.py'deki aynı bloğun CV
    # karşılığı, birebir aynı gerekçe (bkz. o dosyadaki açıklama).
    for (i, j) in At:
        for kk in K:
            if (i in C and kk not in Ti_K[i]) or (j in C and kk not in Ti_K[j]):
                x[i, j, kk].UB = 0.0
                w[i, j, kk].UB = 0.0

    # Delta_c: istasyon-kaynak bazlı yakıt dolum süresi (EV kodundaki
    # Delta[s,v] indekslemesiyle tutarlı; PDF'in Δc_v kısaltmasının
    # açık/doğru biçimidir).
    Delta_c = m.addVars([(s, kk) for s in Fc for kk in K], lb=0.0, vtype=GRB.CONTINUOUS, name="Delta_c")
    # alphac_kb, rhoc_kb, oc_k, qc_k (parçalı doğrusal dolum eğrisi):
    # 3.4.1'de gelecek çalışma bileşeni olarak işaretlendi; kısıtlara
    # henüz işlenmediğinden burada tanımlanmamıştır.

    # z_vt (CV-27): araç-ekip atama değişkeni. Doğrulama testinde (bkz.
    # solution_validator.py) bulunan gerçek bir hatayı düzeltir: aynı
    # fiziksel aracın (v) aynı gün içinde iki FARKLI ekiple (t1≠t2), hatta
    # çakışan saatlerde kullanılabildiği tespit edildi (RC7 örneğinde CV_3
    # aracı, saatleri çakışan iki farklı ekip tarafından "aynı anda"
    # kullanılmıştı). z[v,t]=1, aracın o gün YALNIZCA t ekibine tahsis
    # edildiğini ifade eder.
    z = m.addVars(K, vtype=GRB.BINARY, name="z")

    # u_{r,k} (YENİ, 2026-08-23): "kaynak k, r. seferi yapıyor". Depo klon
    # ailelerini (O[r] / E[r]) devreye alan/dışı bırakan gösterge değişken.
    u = m.addVars([(r, kk) for r in R for kk in K], vtype=GRB.BINARY, name="u")

    # KAYNAK-SPESİFİK R_max SIKILAŞTIRMASI (2026-08-24): klon kümesi (O/E)
    # global R_max ile boyutlandırılır, ancak bir EKİBİN (t) kendi vardiya
    # penceresi daha darsa o kaynağın fazla sefer klonları doğrudan
    # u[r,k] = 0 ile kapatılır (Gurobi presolve buna bağlı x/tau
    # değişkenlerini de eler). es/ls tüm ekipler için aynıysa bu blok hiçbir
    # şey yapmaz — heterojen vardiya penceresi eklendiğinde otomatik devreye
    # girer. Bkz. decisions/karar_r_max_dinamik_turetme.md §"kaynak-spesifik".
    if R_max_by_tech:
        for kk in K:
            t_ = _t_of(kk)
            limit = int(R_max_by_tech.get(t_, R_max))
            for r in R:
                if r > limit:
                    u[r, kk].UB = 0.0

    _rename(x, "x")
    _rename(tau, "tau")
    _rename(w, "w")
    _rename(Delta_c, "Delta_c")
    _rename(z, "z")
    _rename(u, "u")

    # Çıktı ve analiz için modele bağlama
    m._x = x
    m._tau = tau
    m._w = w
    m._A = At
    m._V = V
    m._T = T
    m._K = K
    # Klon altyapısı (print_cv_solution ve dış doğrulayıcılar için)
    m._O = O
    m._E = E
    m._R = R
    m._u = u
    m._z = z
    m._Nt = Nt
    m._clones = clones
    m._R_max = R_max
    m._R_max_info = R_max_info
    # Ö2: kk = (v,t) mi yoksa yalnızca t mi? print_cv_solution ve
    # solution_validator.py bu bayrağa göre dallanır.
    m._aggregate_fleet = aggregate_fleet

    # Amaç Fonksiyonu (CV-1): Toplam Mesafeyi Minimize Et
    m.setObjective(
        gp.quicksum(d[i, j] * x[i, j, kk] for (i, j) in At for kk in K),
        GRB.MINIMIZE
    )

    # Kısıt (CV-2): her müşteri, yalnızca yetkinliği uygun bir kaynak
    # (k ∈ Ti) tarafından tam olarak bir kez ziyaret edilir.
    for j in C:
        m.addConstr(
            gp.quicksum(x[i, j, kk] for i in Nt for kk in Ti_K[j] if (i, j) in At_set) == 1,
            name=f"CV2_atama_{j}"
        )

    # Kısıt (CV-3): her yay en fazla bir kaynak tarafından kullanılabilir.
    for i, j in At:
        m.addConstr(gp.quicksum(x[i, j, kk] for kk in K) <= 1, name=f"CV3_tekil_{i}_{j}")

    # Kısıt (CV-4a/b/c/d): ÇOKLU SEFER, KLONLU BİÇİM — k kaynağı günde en
    # fazla R_max (=3) sefer yapabilir. Eski tek kısıt
    #   Σ_j x[0,j,k] <= 3·z[k]
    # yerine, her sefer r için ayrı çıkış/dönüş dengesi yazılır:
    #   (CV-4a) Σ_j x[O_r,j,k] = u[r,k]      r. seferin depodan çıkışı
    #   (CV-4b) Σ_i x[i,E_r,k] = u[r,k]      r. seferin depoya dönüşü
    #   (CV-4c) u[r,k] <= z[k]               araç atanmamışsa sefer yok
    #   (CV-4d) u[r+1,k] <= u[r,k]           simetri kırma (boş indisler sonda)
    # Toplandığında eski CV-4 geri gelir: Σ_r Σ_j x[O_r,j,k] <= R_max·z[k].
    for kk in K:
        for r in R:
            m.addConstr(
                gp.quicksum(x[O[r], j, kk] for j in Cs if (O[r], j) in At_set) == u[r, kk],
                name=f"CV4a_cikis_{r}_{kk_name[kk]}"
            )
            m.addConstr(
                gp.quicksum(x[i, E[r], kk] for i in Cs if (i, E[r]) in At_set) == u[r, kk],
                name=f"CV4b_donus_{r}_{kk_name[kk]}"
            )
            m.addConstr(u[r, kk] <= z[kk], name=f"CV4c_z_bagi_{r}_{kk_name[kk]}")
        for r in R[:-1]:
            m.addConstr(u[r + 1, kk] <= u[r, kk], name=f"CV4d_sira_{r}_{kk_name[kk]}")

    # NOT — Ö3 (min_veh geçerli eşitsizliği, EV_v.1.1.py'de uygulandı)
    # BİLEREK BURAYA TAŞINMADI: argüman, EV-12'nin ZORUNLU molasının
    # (transitivite ile) bazı müşterileri öğleden sonraya "kilitlemesine"
    # dayanıyor. CV'nin molası (CV-13) OPSİYONEL olduğundan bir CV kaynağı
    # molayı hiç kullanmayarak bu kilitlenmeyi önleyebilir — aynı ec_i=el
    # olan bir müşteri CV'de öğleden sonraya zorlanmaz, yalnızca normal
    # CV-18 penceresi içinde herhangi bir zamanda ziyaret edilebilir.
    # Dolayısıyla min_veh'in "forced-afternoon müşteri kümesi" argümanı
    # CV'de KURULAMAZ; sahte/gevşek bir CV analoğu eklemek (örn. ls-ll
    # yerine ls-el kullanmak) ya geçersiz ya da neredeyse hep etkisiz
    # (min_trips=1) bir kısıt üretirdi. Bkz. EV_v.1.1.py'deki Ö3 notu.

    # Kısıt (CV-27): ARAÇ-EKİP TEKİLLİĞİ — her araç (v) günde en fazla bir
    # ekibe (t) atanabilir. CV-4 ile birlikte, bir aracın aynı gün içinde
    # iki farklı ekip tarafından (çakışsın ya da çakışmasın) kullanılmasını
    # engeller. Test aşamasında solution_validator.py ile tespit edilen
    # "araç çakışması" hatasının kalıcı çözümüdür.
    # Ö2 AGGREGATE MODU: k artık (v,t) değil yalnızca t olduğundan "hangi
    # FİZİKSEL aracın hangi ekibe gittiği" modelde temsil edilmiyor. Denk
    # (ve optimal-koruyucu, homojen filoda) ifade: aynı anda aktif ekip
    # sayısı fiziksel araç sayısını AŞAMAZ. Σ_t z[t] <= |V|.
    if aggregate_fleet:
        m.addConstr(
            gp.quicksum(z[t] for t in T) <= len(V),
            name="CV27_arac_kapasitesi_toplam"
        )
    else:
        for v in V:
            m.addConstr(
                gp.quicksum(z[v, t] for t in T) <= 1,
                name=f"CV27_arac_ekip_tekillik_{v}"
            )

    # Kısıt (CV-28): TEKNİSYEN TEKİLLİĞİ — kullanıcı tarafından bulunan
    # ek bir gerçek eksiklik: CV-27 yalnızca "her araç tek ekibe atanır"
    # diyordu, ama T kümesi hem bireysel teknisyenleri (örn. "TECH_001")
    # hem de bunların ikili kombinasyonlarını (örn.
    # "TECH_001_TECH_007") AYRI ekip kimlikleri olarak içerdiğinden,
    # hiçbir şey aynı HAM teknisyenin (TECH_001) aynı gün hem tek başına
    # bir araçta hem bir ikilinin parçası olarak BAŞKA bir araçta
    # kullanılmasını engellemiyordu — fiziksel olarak imkânsız bir durum.
    # Bu kısıt, her ham teknisyenin günde en fazla BİR aktif (araç,ekip)
    # atamasında yer alabilmesini garanti eder.
    all_raw_techs = set()
    for members in crew_members.values():
        all_raw_techs.update(members)
    for tech in all_raw_techs:
        if aggregate_fleet:
            terms = gp.quicksum(z[t] for t in T if tech in crew_members.get(t, {t}))
        else:
            terms = gp.quicksum(
                z[v, t] for v in V for t in T if tech in crew_members.get(t, {t})
            )
        m.addConstr(terms <= 1, name=f"CV28_teknisyen_tekillik_{tech}")

    # Kısıt (CV-5): akış dengesi — artık YALNIZCA ara düğümlerde (Cs).
    # Depo tarafındaki akış dengesi CV-4a/4b tarafından, hem de DAHA SIKI
    # biçimde sağlanır: eski "for i in N0" döngüsü yalnızca "toplam çıkış =
    # toplam dönüş" diyordu; CV-4a/b her r için ayrı ayrı
    # "çıkış_r = dönüş_r = u_r" diyor.
    for i in Cs:
        for kk in K:
            m.addConstr(
                gp.quicksum(x[i, j, kk] for j in Nt if (i, j) in At_set)
                - gp.quicksum(x[j, i, kk] for j in Nt if (j, i) in At_set) == 0,
                name=f"CV5_akis_{i}_{kk_name[kk]}"
            )

    # Kısıt (CV-6): istasyon-sonrası zaman ilerlemesi (sıkı Big-M).
    for s in real_stations:
        for j in Nt:
            if (s, j) not in At_set:
                continue
            for kk in K:
                t_ = _t_of(kk)
                bigM = a_max + ls[t_] + (ll[t_] - el[t_])
                m.addConstr(
                    tau[s, kk]
                    + w[s, j, kk] * (ll[t_] - el[t_])
                    + Delta_c[s, kk]
                    + tt[s, j] * x[s, j, kk]
                    - bigM * (1 - x[s, j, kk])
                    <= tau[j, kk],
                    name=f"CV6_istasyon_zaman_{s}_{j}_{kk_name[kk]}"
                )

    # Kısıt (CV-7): istasyonda dolumun mola başlamadan bitmesi.
    for c in real_stations:
        for kk in K:
            t_ = _t_of(kk)
            sum_w_cjk = gp.quicksum(w[c, j, kk] for j in Nt if (c, j) in At_set)
            sum_w_ijk_all = gp.quicksum(w[i, j, kk] for (i, j) in At)
            m.addConstr(
                tau[c, kk] + Delta_c[c, kk] <= el[t_] * sum_w_cjk + ls[t_] * (1 - sum_w_ijk_all),
                name=f"CV7_istasyon_mola_bitis_{c}_{kk_name[kk]}"
            )

    # Kısıt (CV-8): müşteri-arası zaman ilerlemesi (mola dahil, sıkı Big-M).
    # j artık depo DÖNÜŞ klonlarını (E[r]) da kapsar; böylece tau[E_r,k]
    # r. seferin depoya dönüş zamanını temsil eder.
    #
    # Ö7a (2026-08-29, sıkı Big-M): global (ls-es+(ll-el)) yerine düğüm-bazlı
    # tau_ub(i)-tau_lb(j) (bkz. concepts/tight_big_m.md, EV_v.1.1.py'deki
    # EV-7 notu). `(ll-el)` mola terimi Big-M'e eklenmedi — CV-9 (`w<=x`)
    # nedeniyle x=0 iken `w*(ll-el)` zaten kendiliğinden 0'dır.
    for i in C:
        for j in Nt:
            if (i, j) not in At_set:
                continue
            for kk in K:
                t_ = _t_of(kk)
                bigM = max(0.0, lc.get(i, 0.0) - ec.get(j, 0.0))
                m.addConstr(
                    tau[i, kk]
                    + w[i, j, kk] * (ll[t_] - el[t_])
                    + (tt[i, j] + st.get(i, 0.0)) * x[i, j, kk]
                    - bigM * (1 - x[i, j, kk])
                    <= tau[j, kk],
                    name=f"CV8_musteri_zaman_{i}_{j}_{kk_name[kk]}"
                )

    # Kısıt (CV-31) YENİ: DEPODAN ÇIKIŞ ZAMAN İLERLEMESİ — geri alınan
    # CV-26'nın DOĞRU hâli. Artık tau[O_r,k] ("r. seferin çıkışı") ile
    # tau[E_r,k] ("r. seferin dönüşü") FARKLI değişkenler olduğu için
    # tau[0,k] < tau[0,k] biçimindeki döngüsel çelişki oluşmaz.
    # Sıkı Big-M: x=0 iken CV-9 gereği w=0'dır, dolayısıyla (ll-el) terimi
    # kısıta girmez.
    #
    # Ö7a (2026-08-29): eski global `max(0, ls-es-tt[O_r,j])` yerine
    # düğüm-bazlı `tau_ub(O_r)-tau_lb(j)` (bkz. concepts/tight_big_m.md) —
    # aynı "w=0" gerekçesini korur, yalnızca üst/alt sınırları düğümlerin
    # KENDİ [ec,lc] pencerelerinden türetir (genel ls-es yerine).
    for r in R:
        for j in Cs:
            if (O[r], j) not in At_set:
                continue
            for kk in K:
                t_ = _t_of(kk)
                bigM = max(0.0, lc.get(O[r], 0.0) - ec.get(j, 0.0))
                m.addConstr(
                    tau[O[r], kk]
                    + w[O[r], j, kk] * (ll[t_] - el[t_])
                    + tt[O[r], j] * x[O[r], j, kk]
                    - bigM * (1 - x[O[r], j, kk])
                    <= tau[j, kk],
                    name=f"CV31_depo_cikis_zaman_{r}_{j}_{kk_name[kk]}"
                )

    # Kısıt (CV-29) YENİ: SEFER SIRASI — r. seferin depoya dönüşü, (r+1).
    # seferin depodan çıkışından sonra olamaz. Bu, R10/RC10'da
    # solution_validator.py tarafından tespit edilen "iki sefer de tau=0.0'da
    # başlıyor" ihlalinin doğrudan çözümüdür. Big-M = (ls - es) tam sınırdır
    # (u[r+1,k]=0 iken kısıt tamamen gevşer).
    for kk in K:
        t_ = _t_of(kk)
        for r in R[:-1]:
            m.addConstr(
                tau[E[r], kk] <= tau[O[r + 1], kk] + (ls[t_] - es[t_]) * (1 - u[r + 1, kk]),
                name=f"CV29_sefer_sirasi_{r}_{kk_name[kk]}"
            )

    # Kısıt (CV-30) YENİ: KULLANILMAYAN SEFER KLONLARININ ANKRAJI —
    # u[r,k]=0 iken (CV-15'in tau >= es alt sınırıyla birlikte) klon zaman
    # değişkenleri es'e sabitlenir. Dejenerasyon/simetri temizliğidir:
    # serbest yüzen tau değişkenleri dal-sınır ağacında eşdeğer düğüm
    # kopyaları üretir. CV-29'daki u-koruması bununla birlikte zorunludur.
    for kk in K:
        t_ = _t_of(kk)
        for r in R:
            m.addConstr(
                tau[O[r], kk] <= es[t_] + (ls[t_] - es[t_]) * u[r, kk],
                name=f"CV30o_bos_sefer_{r}_{kk_name[kk]}"
            )
            m.addConstr(
                tau[E[r], kk] <= es[t_] + (ls[t_] - es[t_]) * u[r, kk],
                name=f"CV30e_bos_sefer_{r}_{kk_name[kk]}"
            )

    # Kısıt (CV-9): mola onayı — indis düşürme sayesinde toplam olmadan.
    for i, j in At:
        for kk in K:
            m.addConstr(w[i, j, kk] <= x[i, j, kk], name=f"CV9_mola_onay_{i}_{j}_{kk_name[kk]}")

    # Kısıt (CV-10): mola sonrası alt sınır.
    for i in Nt:
        for kk in K:
            t_ = _t_of(kk)
            sum_w_ijk = gp.quicksum(w[i, j, kk] for j in Nt if (i, j) in At_set)
            m.addConstr(
                tau[i, kk] + st.get(i, 0.0) <= el[t_] * sum_w_ijk + ls[t_] * (1 - sum_w_ijk),
                name=f"CV10_mola_sonrasi_{i}_{kk_name[kk]}"
            )

    # Kısıt (CV-11): istasyon mola sonrası alt sınır (orijinal PDF'te de
    # CV-7 ile aynı biçimde tekrarlanan kısıt; kaynağın tutarlılığı için
    # aynen korunmuştur).
    for c in real_stations:
        for kk in K:
            t_ = _t_of(kk)
            sum_w_cjk = gp.quicksum(w[c, j, kk] for j in Nt if (c, j) in At_set)
            sum_w_ijk_all = gp.quicksum(w[i, j, kk] for (i, j) in At)
            m.addConstr(
                tau[c, kk] + Delta_c[c, kk] <= el[t_] * sum_w_cjk + ls[t_] * (1 - sum_w_ijk_all),
                name=f"CV11_istasyon_mola_sonrasi_{c}_{kk_name[kk]}"
            )

    # Kısıt (CV-12): mola öncesi üst sınır.
    for i in Nt:
        for kk in K:
            t_ = _t_of(kk)
            sum_w_jik = gp.quicksum(w[j, i, kk] for j in Nt if (j, i) in At_set)
            m.addConstr(
                tau[i, kk] >= ll[t_] * sum_w_jik + es[t_] * (1 - sum_w_jik),
                name=f"CV12_mola_oncesi_{i}_{kk_name[kk]}"
            )

    # Kısıt (CV-13): OPSİYONEL MOLA — GÜNDE KAYNAK BAŞINA EN FAZLA BİR
    # ÖĞLE MOLASI.
    #
    # DEĞİŞİKLİK (2026-08-23, klon tasarımıyla ZORUNLU): eski hâl
    #   Σ w[i,j,k] <= Σ_j x[0,j,k]   (= sefer sayısı)
    # idi, yani 2 sefer yapan kaynağa 2 mola veriyordu. Ama mola penceresi
    # günde TEK ve sabittir ([el_k, ll_k]; xml_data_loader.py:226-227) ve
    # CV-10/CV-12 iki molanın da AYNI pencereyi işgal etmesini dayatır.
    # Sefer sırası kısıtı (CV-29) yokken bu tutarsızlık gizli kalıyordu;
    # CV-29 eklendiğinde
    #   1. sefer molası => tau[E_1] >= ll ;  2. sefer molası => tau[O_2] <= el
    #   CV-29           => tau[E_1] <= tau[O_2]  =>  ll <= el  => ÇELİŞKİ
    # olur. Sayım tabanı bu yüzden "sefer sayısı"ndan "aktif kaynak"a
    # (z[k]) çevrilmiştir. Bkz. decisions/celiski_ogle_molasi_zorunlulugu.md
    for kk in K:
        sum_w_k = gp.quicksum(w[i, j, kk] for (i, j) in At)
        m.addConstr(
            sum_w_k <= z[kk],
            name=f"CV13_mola_max_{kk_name[kk]}"
        )

    # Kısıt (CV-14): MOLASIZ ERKEN DÖNÜŞ — molasını kullanmamış bir kaynak
    # depoya erken dönmek zorundadır. Big-M = (ls_k - ll_k), sıkı.
    # Depoya dönüş göstergesi artık klonlar üzerinden toplulaştırılır:
    # Σ_r x[i,E_r,k] (en fazla bir terim 1'dir).
    for kk in K:
        t_ = _t_of(kk)
        sum_w_k = gp.quicksum(w[i, j, kk] for (i, j) in At)
        bigM = ls[t_] - ll[t_]
        for i in C:
            ret_i = gp.quicksum(x[i, E[r], kk] for r in R if (i, E[r]) in At_set)
            if ret_i.size() == 0:
                continue
            m.addConstr(
                tau[i, kk] + st.get(i, 0.0) + tt.get((i, 0), 0.0)
                <= ll[t_] + bigM * (1 - ret_i + sum_w_k),
                name=f"CV14_erken_donus_{i}_{kk_name[kk]}"
            )

    # Kısıt (CV-15)-(CV-16): mesai saatleri (es_k, ls_k) sınırları.
    # Klon düğümlerde tt[0,i] = tt[i,0] = 0'dır (klon zaten depodadır).
    for i in Nt:
        for kk in K:
            t_ = _t_of(kk)
            tt_0i = 0.0 if i in clones else tt.get((0, i), 0.0)
            tt_i0 = 0.0 if i in clones else tt.get((i, 0), 0.0)
            m.addConstr(tau[i, kk] - tt_0i >= es[t_], name=f"CV15_es_{i}_{kk_name[kk]}")
            m.addConstr(
                tau[i, kk] + st.get(i, 0.0) + tt_i0 <= ls[t_],
                name=f"CV16_ls_{i}_{kk_name[kk]}"
            )

    # Kısıt (CV-17): istasyon mesai üst sınırı.
    for c in real_stations:
        for kk in K:
            t_ = _t_of(kk)
            m.addConstr(
                tau[c, kk] + Delta_c[c, kk] + tt.get((c, 0), 0.0) <= ls[t_],
                name=f"CV17_istasyon_ls_{c}_{kk_name[kk]}"
            )

    # Kısıt (CV-18): müşteri zaman penceresi.
    for i in C:
        for kk in K:
            m.addConstr(ec[i] <= tau[i, kk], name=f"CV18_lb_{i}_{kk_name[kk]}")
            m.addConstr(tau[i, kk] <= lc[i], name=f"CV18_ub_{i}_{kk_name[kk]}")

    # Kısıt (CV-19): yakıt seviyesiyle uyumlu zaman ilerlemesi.
    #
    # NOT (Big-M geçerliliği, 2026-08-22): x=0 iken kısıtın gevşemesi için
    # katsayının en az (ls_k - es_k) + g_c·G_k olması gerekir. __main__
    # data['lc0'] = 40000 atadığı için mevcut koşumlarda (lc0 + g_c·G_k)
    # zaten geçerlidir; ancak lc0, xml_data_loader'ın 10000'lik
    # varsayılanında bırakılırsa katsayı geçersiz ölçüde küçülür ve
    # fizibıl çözümler kesilir (EV modelinde fiilen bu olmuştu, bkz.
    # EV_v.1.1.py EV-17 notu). max(...) biçimi mevcut sayısal davranışı
    # DEĞİŞTİRMEZ (40000 > 32400), yalnızca kısıtı lc0'dan bağımsız
    # olarak güvenli hâle getirir.
    #
    # NOT (2026-08-23): depo yayı istisnası artık KLON yayları üzerinden
    # yazılır (i in clones or j in clones). Bu istisnanın korunması kritiktir;
    # kaldırılırsa sorun_ev_depo_yaylarinda_dongusel_infeasibility geri gelir.
    #
    # Ö7a (2026-08-29, sıkı Big-M): düğüm-bazlı tau_ub(i)-tau_lb(j)'ye
    # geçildi. `g_c*(YC[i]-yc[i])` terimi (ve dolayısıyla eski lc0/g_c*G_k
    # güvenlik payı) KALDIRILDI — CV-22 (`YC[i]==yc[i]`, TÜM Cs için,
    # istasyon istisnası YOK) bu farkı HER fizibıl çözümde kanıtlanabilir
    # biçimde sıfırlar (CV'de gerçek istasyon hiç yok, bkz.
    # sorun_cv_kullanilmayan_istasyon_parametreleri.md), dolayısıyla Big-M'in
    # onu kapsamasına gerek yoktur — LHS'teki terim yine de bırakıldı
    # (referans bütünlüğü/simetri için), yalnızca hep-sıfır olduğu
    # kanıtlanabilir olduğundan Big-M'den düşürüldü.
    for i, j in At:
        if i in clones or j in clones:
            continue
        for kk in K:
            t_ = _t_of(kk)
            bigM = max(0.0, lc.get(i, 0.0) - ec.get(j, 0.0))
            m.addConstr(
                tau[i, kk] + tt[i, j] * x[i, j, kk] + g_c * (YC[i] - yc[i])
                - bigM * (1 - x[i, j, kk]) <= tau[j, kk],
                name=f"CV19_yakit_zaman_{i}_{j}_{kk_name[kk]}"
            )

    # Kısıt (CV-20)-(CV-21): yakıt tüketimi (varış/ayrılış üzerinden).
    #
    # Ö7b (2026-08-29): CV20_lb/CV21_lb (`yc[j] >= 0`) KALDIRILDI — `yc`
    # zaten `lb=0.0` ile tanımlı (bkz. EV_v.1.1.py'deki aynı düzeltme,
    # EV18_lb/EV19_lb notu). Presolve bunları zaten atıyordu; solve
    # davranışını DEĞİŞTİRMEZ, yalnızca model kurma/`.lp` yazma süresini
    # kısaltır.
    for i, j in At:
        if i in clones or j in clones:
            continue
        for kk in K:
            m.addConstr(
                yc[j] <= yc[i] - (h_c * d[i, j]) * x[i, j, kk] + _Gk(kk) * (1 - x[i, j, kk]),
                name=f"CV20_ub_{i}_{j}_{kk_name[kk]}"
            )
            m.addConstr(
                yc[j] <= YC[i] - (h_c * d[i, j]) * x[i, j, kk] + _Gk(kk) * (1 - x[i, j, kk]),
                name=f"CV21_ub_{i}_{j}_{kk_name[kk]}"
            )

    # Kısıt (CV-22): ayrılış yakıt seviyesi, varış seviyesi ile kapasite
    # arasında olmalı; depoda ayrıca dolum yapılmaz (CV-23/24 depoyu
    # zaten tam dolu kabul eder).
    for i in Cs:
        m.addConstr(YC[i] == yc[i], name=f"CV22_no_refuel_{i}")
        for kk in K:
            m.addConstr(YC[i] <= _Gk(kk), name=f"CV22_ub_{i}_{kk_name[kk]}")

    # Kısıt (CV-23)-(CV-24): DEPODA TAM DOLUM — bir kaynak depodan
    # ayrılırken yakıt seviyesi tam kapasiteden ilk bacak tüketimi kadar
    # eksiltilerek belirlenir. Bu, çoklu seferin (CV-4) pratikte
    # kullandığı tek yakıt doldurma mekanizmasıdır.
    # Her sefer (r) için ayrı yazılır; en fazla biri aktiftir (x en fazla
    # bir r için 1'dir), dolayısıyla davranış birebir korunur ve her seferin
    # başındaki tam dolum ayrı bir yay üzerinden ifade edilir.
    for r in R:
        for j in Cs:
            if (O[r], j) not in At_set:
                continue
            for kk in K:
                Gk = _Gk(kk)
                m.addConstr(
                    yc[j] <= Gk - (h_c * d.get((0, j), 0.0)) * x[O[r], j, kk]
                    + Gk * (1 - x[O[r], j, kk]),
                    name=f"CV23_depo_dolum_ub_{r}_{j}_{kk_name[kk]}"
                )
                m.addConstr(
                    yc[j] >= Gk - (h_c * d.get((0, j), 0.0)) - Gk * (1 - x[O[r], j, kk]),
                    name=f"CV24_depo_dolum_lb_{r}_{j}_{kk_name[kk]}"
                )

    # Kısıt (CV-25): depoya dönüş bacağını tamamlayacak kadar yakıt garantisi.
    # Dönüş göstergesi klonlar üzerinden toplulaştırılır.
    for i in Cs:
        if (i, 0) not in A_set:
            continue
        for kk in K:
            ret_i = gp.quicksum(x[i, E[r], kk] for r in R if (i, E[r]) in At_set)
            m.addConstr(
                yc[i] >= (h_c * d.get((i, 0), 0.0)) * ret_i,
                name=f"CV25_donus_yakiti_{i}_{kk_name[kk]}"
            )

    # NOT (CV-26 TARİHÇESİ, 2026-08-23'te ÇÖZÜLDÜ): Depodan ilk çıkış için
    # tau[0,k]'yi bir alt sınır kaynağı olarak kullanan bir kısıt (CV-26)
    # daha önce denenmiş, IIS analiziyle şu çelişki tespit edilmişti:
    # tau[0,k], CV-8'in j=0 (depoya dönüş) hâli tarafından zaten "dönüş
    # zamanı" olarak kullanılıyordu; aynı değişkeni "çıkış zamanı" için de
    # kullanmak tau[0,k] < tau[0,k] biçiminde döngüsel bir infeasibility
    # üretiyordu. CV-26 bu yüzden geri alınmış, ancak bu geri alma
    # ZARARSIZ DEĞİLDİ: seferler arası sıralama kısıtı kalmadığı için aynı
    # kaynağın iki seferi zaman olarak ÇAKIŞABİLİYORDU (R10/RC10'da
    # solution_validator.py ile fiilen gözlendi).
    #
    # Bu sürümde sorun, notta önerilen kökten çözümle giderilmiştir: depo
    # düğümü sefer-indeksli ÇIKIŞ (O[r]) ve DÖNÜŞ (E[r]) klonlarına
    # ayrılmış, CV-31 (çıkış zaman ilerlemesi = CV-26'nın doğru hâli),
    # CV-29 (sefer sırası) ve CV-30 (boş sefer ankrajı) eklenmiştir.
    # Artık depodan çıkış saati tau[O_r,k], dönüş saati tau[E_r,k]'dir.

    return m


def format_time(seconds: float) -> str:
    if seconds is None:
        return "--:--"
    seconds = max(0, round(seconds))
    shifted_seconds = seconds + 28800
    h = (shifted_seconds // 3600) % 24
    m = (shifted_seconds % 3600) // 60
    return f"{h:02d}:{m:02d}"


# DOSYAYA VE EKRANA YAZDIRAN GÜNCELLENMİŞ ÇIKTI FONKSİYONU
def print_cv_solution(data, model, out_name):
    # Çıktı dosyasını oluştur
    log_filename = f"Operasyon_Raporu_{out_name}.txt"

    with open(log_filename, "w", encoding="utf-8") as f:

        # Hem ekrana hem dosyaya yazdırmak için küçük bir yardımcı fonksiyon
        def log_print(text=""):
            # DÜZELTME (2026-08-22): Türkçe Windows konsolunda (cp1254) ya da
            # çıktı bir dosyaya/boruya yönlendirildiğinde, rapordaki emoji
            # karakterleri (📌, 👷, 🕒 ...) print() içinde
            # UnicodeEncodeError'a yol açıp ÇÖZÜM BULUNDUKTAN SONRA scripti
            # çökertiyordu; bu yüzden Operasyon_Raporu_*.txt dosyası da yarım
            # kalıyordu (R5 koşumunda birebir gözlendi). Dosya zaten utf-8
            # açıldığı için yalnızca konsol yazımı korunur.
            try:
                print(text)
            except UnicodeEncodeError:
                enc = getattr(sys.stdout, 'encoding', None) or 'ascii'
                print(text.encode(enc, errors='replace').decode(enc, errors='replace'))
            f.write(text + "\n")

        if model.SolCount == 0:
            log_print("Çözüm yok veya verilen süre içinde uygun bir rota bulunamadı.")
            return

        x = model._x
        tau = model._tau
        w_vars = model._w
        d = data['d']
        tt = data['tt']
        st = data['st']
        node_labels = data.get('node_labels', {})

        routes = {}
        for (i, j, kk), var in x.items():
            if var.X > 0.5:
                routes.setdefault(kk, []).append((i, j))

        log_print("\n" + "=" * 65)
        log_print(f"       GÜNLÜK OPERASYON DETAYLI ZAMAN ÇİZELGESİ - {out_name}")
        log_print("=" * 65)

        for kk, arcs in sorted(routes.items()):
            # Ö2 AGGREGATE MODU: bkz. EV_v.1.1.py'deki aynı dallanmanın notu.
            if isinstance(kk, tuple):
                v, t = kk
            else:
                v, t = "Arac?", kk
            ekip_isimleri = t.replace('_', ' & ')

            # DÜZELTME (2026-08-22): mola süresi rapor içinde sabit 3600 s
            # ("1 Saat") olarak varsayılıyordu; oysa modelde mola, zaman
            # ilerleme kısıtlarına (CV-8/CV-6) w_ijk*(ll_k - el_k) terimiyle
            # giriyor — yani mola süresi ekibin mola penceresi genişliği
            # kadardır (mevcut veriyle 21600-14400 = 7200 s = 2 saat).
            # Rapor bu yüzden dönüş saatlerini 1 saat ERKEN gösteriyordu.
            break_start = float(data['el'][t])
            break_end = float(data['ll'][t])
            break_dur = break_end - break_start
            break_h = break_dur / 3600.0
            break_label = f"{break_h:.0f} Saat" if abs(break_h - round(break_h)) < 1e-9 else f"{break_h:.2f} Saat"

            # ÇOKLU SEFER (CV-4a..d, <=R_max): DÜZELTME (2026-08-23) —
            # depo artık sefer-indeksli klonlarla temsil edildiğinden
            # (O[r] = çıkış klonu, E[r] = dönüş klonu), depodan çıkan yaylar
            # "i == 0" ile değil "i in O" ile bulunur ve r indisi zaten
            # KRONOLOJİK sırayı verir (CV-29). Eski depot_departures.sort()
            # (düğüm numarasına göre keyfi sıralama) gereksizleşmiştir.
            o_of_node = {node: r for r, node in getattr(model, '_O', {}).items()}
            e_of_node = {node: r for r, node in getattr(model, '_E', {}).items()}

            next_map = {}
            depot_departures = []   # (r, ilk_musteri)
            for i, j in arcs:
                if i in o_of_node:
                    depot_departures.append((o_of_node[i], j))
                else:
                    next_map[i] = j
            depot_departures.sort()

            trips = []       # [0, ..., 0] biçiminde düğüm listesi
            trip_rr = []     # (r_cikis, r_donus) klon indisleri
            for r_out, start in depot_departures:
                trip = [0, start]
                current = start
                r_in = None
                visited_in_trip = {start}
                while current in next_map:
                    nxt = next_map[current]
                    if nxt in e_of_node:
                        r_in = e_of_node[nxt]
                        trip.append(0)
                        break
                    if nxt in visited_in_trip:
                        break
                    trip.append(nxt)
                    visited_in_trip.add(nxt)
                    current = nxt
                trips.append(trip)
                trip_rr.append((r_out, r_in))

            keep = [idx for idx, route in enumerate(trips) if len(route) > 1]
            trips = [trips[idx] for idx in keep]
            trip_rr = [trip_rr[idx] for idx in keep]
            if not trips:
                continue

            toplam_mesafe_kk = sum(
                d.get((route[idx], route[idx + 1]), 0.0)
                for route in trips for idx in range(len(route) - 1)
            )

            log_print(f"📌 {v} ARACI OPERASYON RAPORU (Ekip: {ekip_isimleri}, {len(trips)} sefer)")
            log_print(f"  👷 Ekip           : {ekip_isimleri}")
            log_print(f"  📏 Toplam Mesafe (tüm seferler) : {toplam_mesafe_kk:.2f} metre")

            for trip_idx, (route, (r_out, r_in)) in enumerate(zip(trips, trip_rr), start=1):
                total_distance = sum(d.get((route[idx], route[idx + 1]), 0.0) for idx in range(len(route) - 1))
                log_print(f"  --- Sefer {trip_idx}/{len(trips)} (model sefer indisi r={r_out}) ---")
                log_print(f"  📏 Sefer Mesafesi : {total_distance:.2f} metre")
                log_print(f"  🕒 Kronolojik Zaman Çizelgesi ve Akışı:")

                # DÜZELTME (2026-08-23): depodan çıkış/dönüş saatleri artık
                # doğrudan klon zaman değişkenlerinden okunabilir
                # (tau[O_r,k] / tau[E_r,k]); eski "geriye türetme hack'i"
                # gerekmiyor. Yine de raporun FİZİKSEL olarak en sıkı
                # çizelgeyi göstermesi için görüntülenen çıkış saati,
                # klon değeriyle türetilmiş değerin en geç olanı alınır
                # (tau[O_r] serbestçe daha erken olabilir; araç depoda
                # bekliyor demektir). Model değerleri ayrıca teşhis satırı
                # olarak yazdırılır.
                first_customer = route[1]
                derived_departure = tau[first_customer, kk].X - tt.get((0, first_customer), 0.0)
                model_departure = tau[model._O[r_out], kk].X if hasattr(model, '_O') else None
                model_return = (tau[model._E[r_in], kk].X
                                if (hasattr(model, '_E') and r_in is not None) else None)
                depot_departure_val = derived_departure
                if model_departure is not None:
                    log_print(
                        f"     (model: τ[o_{r_out}] = {format_time(model_departure)}"
                        + (f" , τ[e_{r_in}] = {format_time(model_return)}" if model_return is not None else "")
                        + ")"
                    )

                # route içindeki 0'lar rapor amaçlıdır; w/x değişkenleri
                # depo yaylarında KLON-indekslidir (O[r_out] / E[r_in]),
                # bu yüzden mola göstergesi okunurken geri eşlenmelidir.
                def _break_on(pos, _route=route, _kk=kk, _r_out=r_out, _r_in=r_in):
                    a = _route[pos - 1]
                    b = _route[pos]
                    if pos == 1 and a == 0 and hasattr(model, '_O'):
                        a = model._O[_r_out]
                    if b == 0 and _r_in is not None and hasattr(model, '_E'):
                        b = model._E[_r_in]
                    var = w_vars.get((a, b, _kk))
                    return var is not None and var.X > 0.5

                for idx in range(len(route)):
                    curr_node = route[idx]
                    node_name = node_labels.get(curr_node, str(curr_node))

                    if idx == 0:
                        start_val = depot_departure_val
                        log_print(
                            f"     [ {format_time(start_val)} ] ➔ Depodan Çıkış yapıldı. Nokta: {curr_node} ({node_name})")
                    elif idx == len(route) - 1:
                        prev_node = route[idx - 1]
                        end_val = tau[prev_node, kk].X + st.get(prev_node, 0.0) + tt.get((prev_node, 0), 0.0)

                        if _break_on(idx):
                            # DÜZELTME (2026-08-22): mola aralığı artık modelin
                            # fiilen dayattığı pencere olarak yazılır. CV-10
                            # mola öncesi düğümde hizmetin el_k'den ÖNCE
                            # bitmesini, CV-12 mola sonrası düğüme ll_k'den
                            # SONRA varılmasını zorunlu kılar; yani mola
                            # [el_k, ll_k] penceresini işgal eder. Önceki hâl
                            # molayı "hizmet biter bitmez, 1 saat" olarak
                            # gösteriyordu — hem süre hem başlangıç yanlıştı.
                            log_print(
                                f"     ☕ [ {format_time(break_start)} - {format_time(break_end)} ] Yolda Öğle Molası ({break_label}) Kullanıldı.")
                            end_val = break_end + tt.get((prev_node, 0), 0.0)

                        leg_dist = d.get((prev_node, curr_node), 0.0)
                        log_print(f"     |                     └─── Son Müşteriden Yolculuk Mesafe: {leg_dist:.1f} m")
                        log_print(
                            f"     [ {format_time(end_val)} ] 🏁 Depoya Dönüş sağlandı. Nokta: {curr_node} ({node_name})")
                    else:
                        arr_val = tau[curr_node, kk].X
                        srv_val = st.get(curr_node, 0.0)
                        srv_min = int(srv_val // 60)
                        dep_val = arr_val + srv_val

                        prev_node = route[idx - 1]
                        leg_dist = d.get((prev_node, curr_node), 0.0)

                        if _break_on(idx):
                            log_print(
                                f"     ☕ [ {format_time(break_start)} - {format_time(break_end)} ] Yolda Öğle Molası ({break_label}) Kullanıldı.")

                        log_print(f"     |                     └─── Yolculuk Mesafe: {leg_dist:.1f} m")
                        log_print(f"     [ {format_time(arr_val)} ] ➔ Müşteriye Varış. Nokta: {curr_node} ({node_name})")
                        log_print(
                            f"               ↳ Hizmet Detayı : İş Süresi: {srv_min} dakika | Ayrılış Saati: {format_time(dep_val)}")

                start_time = depot_departure_val
                last_customer = route[-2]
                end_time = tau[last_customer, kk].X + st.get(last_customer, 0.0) + tt.get((last_customer, 0), 0.0)

                if _break_on(len(route) - 1):
                    end_time = break_end + tt.get((last_customer, 0), 0.0)

                total_duration = end_time - start_time
                duration_h = int(total_duration // 3600)
                duration_m = int((total_duration % 3600) // 60)
                log_print(f"  ⏳ Sefer Süresi: {duration_h} saat {duration_m} dakika")

            log_print("-" * 65)

    # DÜZELTME (2026-08-22): bu son satır `with` bloğunun DIŞINDA olduğu için
    # yukarıdaki log_print koruması onu kapsamıyordu ve cp1254 konsolda tek
    # başına UnicodeEncodeError üretiyordu (R5 koşumunda gözlendi).
    try:
        print(f"\n✅ Çıktı '{log_filename}' dosyasına başarıyla kaydedildi!")
    except UnicodeEncodeError:
        print(f"\n[OK] Cikti '{log_filename}' dosyasina basariyla kaydedildi!")


def select_instances(instances: dict) -> dict:
    base_names = sorted({os.path.splitext(os.path.basename(k))[0].strip() for k in instances})
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
        base = os.path.splitext(os.path.basename(key))[0].strip()
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

    employee_file = os.path.join(root, "Info4Employee.xml")
    skill_tech_map = {}
    all_technicians = []

    # NOT: os.path.exists() tek başına yeterli değildi — bu ortamdaki
    # Info4Employee.xml dosyası mevcut ama BOŞ (0 bayt), bu da
    # ET.parse()'ın "no element found" hatasıyla çökmesine yol açıyordu.
    # Kullanıcı doğrudan çalıştırırken bu hatayla karşılaştı; dosya boyutu
    # da kontrol edilerek düzeltildi.
    if os.path.exists(employee_file) and os.path.getsize(employee_file) > 0:
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
        out_name = os.path.splitext(os.path.basename(instance_name))[0].strip()
        print(f"\n== {out_name} için model kuruluyor ==")

        data = prepare_cv_data_from_instance(
            instance,
            vehicles,
            vehicle_attrs,
            technicians=all_technicians,
        )

        data['lc0'] = 40000.0

        # Türetilmiş R_max'ın hangi gerekçeyle seçildiğini koşum çıktısına yaz
        # (bkz. xml_data_loader.derive_r_max).
        _rmi = data.get('R_max_info') or {}
        _reason = next(iter((_rmi.get('reasons') or {}).values()), 'varsayilan')
        print(f"   R_max = {data.get('R_max')} ({_reason})")

        # NOT: instances sözlüğünün anahtarları (instance_name), root'a
        # GÖRELİ yollardır (örn. "trsp_problem_sets\C5.xml"). Önceki
        # sürümde bu, doğrudan ET.parse(instance_name) ile açılmaya
        # çalışılıyordu; bu yalnızca ÇALIŞMA DİZİNİ (cwd) script'in
        # klasörüyle aynıysa çalışır. VS Code'un "Run" düğmesi veya
        # farklı bir dizinden başlatma gibi durumlarda cwd farklı
        # olabildiğinden dosya bulunamıyor, delivery_skills boş kalıyor,
        # bu da T_list'in boşalıp modelin anlamsızca infeasible
        # çıkmasına yol açıyordu ("ROTA BULAMIYOR" şikayetinin asıl
        # sebebi buydu). os.path.join(root, ...) ile cwd'den bağımsız
        # hale getirildi.
        delivery_skills = []
        try:
            problem_tree = ET.parse(os.path.join(root, instance_name))
            for node in problem_tree.findall(".//Node"):
                req = node.find(".//Request")
                if req is not None:
                    skill = req.get("RequiredSkill")
                    if skill:
                        delivery_skills.append(skill)
        except Exception as e:
            print(f"Uyarı: {instance_name} okunurken hata oluştu. Hata: {e}")

        req_skills_unique = sorted(set(delivery_skills))
        active_techs = []
        tech_to_skill = {}

        for skill in req_skills_unique:
            if skill in skill_tech_map and skill_tech_map[skill]:
                # Bug fix (2026-08-31): önceki hâl skill_tech_map[skill][0] ile
                # her beceriden yalnızca İLK teknisyeni alıyor, aynı beceriye
                # sahip diğer teknisyenleri (örn. TECH_002/004/006) tamamen
                # atıyordu (bkz. sorun_rc20_darbogaz_kok_neden_analizi.md).
                # Doğrusu: bir beceriye sahip TÜM teknisyenler aktif olmalı.
                for tech in skill_tech_map[skill]:
                    active_techs.append(tech)
                    tech_to_skill[tech] = skill

        T_list = []
        crew_skills = {}
        # crew_members: her ekip kimliğinin hangi ham teknisyenlerden
        # oluştuğu (bkz. build_model içindeki CV-28 notu).
        crew_members = {}

        for tech in active_techs:
            T_list.append(tech)
            crew_skills[tech] = {tech_to_skill[tech]}
            crew_members[tech] = {tech}

        for t1, t2 in itertools.combinations(active_techs, 2):
            crew_name = f"{t1}_{t2}"
            T_list.append(crew_name)
            crew_skills[crew_name] = {tech_to_skill[t1], tech_to_skill[t2]}
            crew_members[crew_name] = {t1, t2}

        data['T'] = T_list
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

        lp_name = f"exact_model_{out_name}.lp"
        try:
            model.write(lp_name)
            print(f"Model kuruldu ve '{lp_name}' olarak yazildi.")
        except gp.GurobiError as e:
            print(f"Uyarı: LP dosyası yazılamadı ({e}); optimizasyona devam ediliyor.")

        model.setParam('TimeLimit', 10800)
        model.setParam('MIPFocus', 1)
        model.setParam('MIPGap', 0.05)
        # NOT: CV-27 (araç-ekip tekilliği) modeli daha DOĞRU hale getirdi,
        # ancak tüm müşteri-kaynak atamalarını birbirine bağlayan küresel
        # bir kısıt eklediği için Gurobi'nin İLK fizibil çözümü bulması
        # zorlaştı (test sırasında R10'da ~7 dakikaya çıktığı görüldü;
        # v1'de saniyeler sürüyordu — "ROTA BULAMIYOR" şikayetinin
        # sebebiydi, infeasibility değil). NoRelHeurTime, tam dallan-ve-
        # sınırla başlamadan önce bir süre yalnızca fizibil çözüm aramaya
        # odaklanarak bunu hızlandırır.
        model.setParam('NoRelHeurTime', 120)
        model.setParam('LogFile', f"gurobi_log_{out_name}.log")

        model.optimize()

        print(f"\n{out_name} için Çözüm durumu: {model.Status}")

        # Dosyaya yazdırma fonksiyonuna problem adını (out_name) da yolluyoruz
        print_cv_solution(data, model, out_name)
