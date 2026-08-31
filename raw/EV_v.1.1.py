import math
import os
import sys
import gurobipy as gp
from gurobipy import GRB
from xml_data_loader import (
    load_problem_instances,
    parse_vehicle_file,
    parse_charging_stations,
    prepare_ev_data_from_instance,
)

# ---------------------------------------------------------------------------
# Bu dosya, tez taslağının 3.4.2 (Elektrikli Araç Modeli) bölümündeki
# matematiksel modelin birebir Gurobi/Python karşılığıdır. Her kısıt bloğunun
# üzerindeki yorumda ilgili denklem numarası (EV-1 ... EV-20) belirtilmiştir.
# Karşılaştırma için bkz. "hasan taslak makale 1.docx", Bölüm 3.4.2.
#
# v1 (x_i,j,v,t, 4 boyutlu, tek seferli) sürümü referans için
# "EV_model_gurobi_exact - yedek (v1, x_ijvt).py" olarak saklanmıştır.
#
# NOT (ÇOKLU SEFER TUTARSIZLIĞI): 3.4.2'de belirtildiği gibi, EV-4 kısıtı
# (<=3 depo çıkışı) bu sürümde ilk kez eklenmektedir; v1'in tek seferli
# yapısıyla üretilmiş olan Çizelge 4.1 sonuçları bu kod ile yeniden
# üretilene kadar güncel değildir. Sonuçların bu sürümle yeniden
# koşturulması gerekmektedir.
# ---------------------------------------------------------------------------


def build_model(data):
    model = gp.Model("EV_exact_model_v2")

    # Sets (ham veri)
    N = data["N"]
    Np = data["N_prime"]
    C = data["C"]
    V = data["V"]
    T = data["T"]
    S = data["S"]                      # Fe: fiziksel şarj istasyonları
    B = data["B"]                      # kırılma noktaları (gelecek çalışma)
    A = data["A"]
    Ti = data["T_i"]
    # crew_members: her ekip kimliğinin hangi ham teknisyenlerden
    # oluştuğu (bkz. CV_model_gurobi_exact.py'deki CV-28 notu — aynı
    # gerekçeyle EV-23 için kullanılır). Verilmezse her t atomik kabul
    # edilir.
    crew_members = data.get("crew_members") or {t: {t} for t in T}

    # Parameters
    d = data["d"]
    tt = data["tt"]
    tt0i = data["tt_0i"]
    tti0 = data["tt_i0"]
    tts0 = data["tt_s0"]
    st = data["st"]
    Q = data["Q"]
    ec = data["ec"]
    lc = data["lc"]
    lc0 = data["lc_0"]
    es = data["es"]
    ls = data["ls"]
    el = data["el"]
    ll = data["ll"]
    h_e = data["h_e"]
    g_e = data["g_e"]
    a_max = data["a_max"]

    # ------------------------------------------------------------------
    # Kaynak kümesi K = V x T  (3.4.2 Kümeler: "K ⊆ V×T ... K = V×T")
    # x_i,j,v,t (4 boyutlu) yerine x_i,j,k (3 boyutlu) — indis düşürme
    # (Acar & Altın, 2025), CV modeliyle aynı mantık.
    #
    # Ö2 (2026-08-28, sorun_rc13_darbogaz_kok_neden_analizi.md): HOMOJEN
    # FİLODA ARAÇ İNDİSİNİ KALDIR. Filodaki tüm araçlar birebir aynıysa
    # (aynı batarya kapasitesi Q — mevcut mimaride hız zaten TEK bir
    # referans araçtan okunup tüm filoya uygulanıyor, bkz.
    # xml_data_loader.prepare_ev_data_from_instance) hangi FİZİKSEL aracın
    # hangi ekibe gittiği amaç fonksiyonunu hiç etkilemez — |V| adet
    # birbirinin YERİNE GEÇEBİLEN aracın tüm permütasyonları aynı maliyeti
    # verir (saf simetri). K = V×T yerine K = T kullanılır; "en fazla |V|
    # ekip aynı anda aktif olabilir" kısıtı (aşağıda EV-22'nin agregatize
    # hâli) fiziksel araç sayısını korur. Filo heterojenleşirse (Q
    # farklılaşırsa) otomatik olarak K=V×T'ye GERİ DÖNER — bu bir "her
    # zaman aggregate" kuralı değildir, veri-bağımlıdır.
    #
    # Entegrasyon maliyeti: k artık (v,t) yerine yalnızca t olabileceği
    # için, `kk`'nin HANGİ fiziksel aracı temsil ettiği modelde ARTIK
    # İZLENMEZ (aggregate modda aktif ekip sayısı <= |V| garanti edilir,
    # ama HANGİ aracın hangi ekibe gittiği bir POST-PROCESSING/raporlama
    # kararıdır — homojen filoda bu atama hiçbir zaman infeasible
    # üretemez). Bkz. _t_of/_Qk yardımcıları (kk'nin tuple mı skaler mi
    # olduğunu her çağrı noktasında ayrıştırır) ve print_ev_solution /
    # solution_validator.py'deki aggregate-mod dallanmaları.
    aggregate_fleet = (Q is not None and len(Q) > 0
                        and len({round(float(_qv), 6) for _qv in Q.values()}) <= 1)
    if aggregate_fleet:
        K = list(T)
    else:
        K = [(v, t) for v in V for t in T]

    def _t_of(kk):
        return kk[1] if isinstance(kk, tuple) else kk

    _Q_const = next(iter(Q.values())) if Q else 0.0

    def _Qk(kk):
        return _Q_const if aggregate_fleet else Q[kk[0]]

    # kk_name: Gurobi kısıt/değişken isimlerinde k=(v,t) tuple'ının ham
    # Python string hali kullanılamaz — .lp dosyası yazarken isim
    # çakışmasına ve "Unable to write to file" hatasına yol açtığı test
    # sırasında tespit edildi (bkz. CV_model_gurobi_exact.py'deki aynı not).
    # Aggregate modda kk zaten temiz bir string (crew id) olduğundan doğrudan
    # kullanılır.
    kk_name = {kk: (str(kk) if aggregate_fleet else f"{kk[0]}_{kk[1]}") for kk in K}

    def _clean_part(p):
        return kk_name[p] if isinstance(p, tuple) else str(p)

    def _rename(var_dict, prefix):
        # bkz. CV_model_gurobi_exact.py'deki aynı yardımcı fonksiyonun notu.
        for key, var in var_dict.items():
            parts = key if isinstance(key, tuple) else (key,)
            var.VarName = f"{prefix}[{','.join(_clean_part(p) for p in parts)}]"

    # Ti_K: her düğüm için yetkinliği uygun kaynaklar. NOT (DÜZELTME):
    # v1 kodunda Kısıt (1) yanlışlıkla Ti[i] (kaynak düğüm) üzerinden
    # filtreleniyordu; doğrusu -CV kodunda olduğu gibi- hedef düğüm j'nin
    # gereksinimidir (bkz. EV-2: "k ∈ Ti", Ti hedef düğüme göre
    # değerlendirilir). Mevcut veri hazırlama katmanında (prepare_ev_data
    # _from_instance) Ti tüm düğümler için aynı (yetkinlik filtresiz)
    # teknisyen listesini döndürdüğünden bu düzeltme sonucu değiştirmez,
    # ancak gerçek bir yetkinlik filtresi eklendiğinde doğru davranacaktır.
    # Ö2 UYUMU: aggregate modda kk = t (skaler) olduğundan Ti_K de aynı
    # şekilde skaler listesi olmalı — aksi hâlde Ö1'in yetkinlik filtresi
    # (kk in Ti_K[j]) hiçbir zaman eşleşmez ve TÜM x/w yanlışlıkla UB=0'a
    # sabitlenir.
    if aggregate_fleet:
        Ti_K = {j: list(Ti.get(j, [])) for j in Np}
    else:
        Ti_K = {j: [(v, t) for v in V for t in Ti.get(j, [])] for j in Np}

    # ------------------------------------------------------------------
    # DEPO KLON DÜĞÜMLERİ (2026-08-23) — sefer-indeksli zaman değişkeni.
    # CV_model_gurobi_exact.py'deki aynı tasarımın EV karşılığıdır
    # (CV-29/30/31 <-> EV-28/29/30). Gerekçe: tau[0,k] kaynak başına TEK bir
    # skalerdi ve EV-7'nin j=0 hâli tarafından "depoya dönüş zamanı" olarak
    # sabitleniyordu; bu yüzden aynı kaynağın 2./3. seferi zaman olarak
    # ÇAKIŞABİLİYORDU. Bkz. eski "EV-21 geri alındı" notu ve
    # decisions/karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani.md
    #
    # Cs = müşteri + ŞARJ İSTASYONU düğümleri; istasyonlar KLONLANMAZ
    # (o ayrı bir konudur: karar_klon_dugum_sarj_istasyonu_plani.md),
    # yalnızca depo klonlanır. EV'nin şarj mantığı düğüm-içi (Delta_s,
    # YE-ye), klonlama ise düğüm-arası (depo yayı ayrıştırması) çalıştığı
    # için ikisi çakışmaz.
    # ------------------------------------------------------------------
    # R_max artık SABİT 3 DEĞİL: xml_data_loader.derive_r_max tarafından
    # veriden türetilir ve prepare_ev_data_from_instance sözlüğünde
    # data['R_max'] olarak gelir. Türetim, optimal çözümü kesmeyen
    # KANITLANABİLİR bir üst sınırdır (EV'de belirleyici argüman: zorunlu
    # mola nedeniyle bir vardiyada kat edilebilecek en uzun mesafe
    # 37.5 km/sa x 25200 s = 262.5 km, batarya menzili 322 km'nin altındadır;
    # yani enerji hiç bağlamaz ve ardışık seferler üçgen eşitsizliğiyle tek
    # sefere birleştirilebilir). Bkz. decisions/karar_r_max_dinamik_turetme.md.
    R_max = max(1, int(data.get("R_max", 3)))
    R_max_by_tech = data.get("R_max_by_tech") or {}
    R = list(range(1, R_max + 1))
    Cs = [i for i in Np if i != 0]
    _base = max(Np) + 1
    O = {r: _base + (r - 1) for r in R}          # depo ÇIKIŞ klonları
    E = {r: _base + R_max + (r - 1) for r in R}  # depo DÖNÜŞ klonları
    clones = set(O.values()) | set(E.values())
    Nt = Cs + [O[r] for r in R] + [E[r] for r in R]

    A_set = set(A)
    At = [(i, j) for i in Cs for j in Cs if (i, j) in A_set]
    At += [(O[r], j) for r in R for j in Cs if (0, j) in A_set]
    At += [(i, E[r]) for r in R for i in Cs if (i, 0) in A_set]
    At_set = set(At)

    # Parametre takma adları — çağıranın data sözlüğü DEĞİŞTİRİLMEZ.
    d = dict(d)
    tt = dict(tt)
    st = dict(st)
    ec = dict(ec)
    lc = dict(lc)
    tt0i = dict(tt0i)
    tti0 = dict(tti0)
    for r in R:
        o_r, e_r = O[r], E[r]
        st[o_r] = 0.0
        st[e_r] = 0.0
        ec[o_r] = ec.get(0, 0.0)
        ec[e_r] = ec.get(0, 0.0)
        lc[o_r] = lc.get(0, 0.0)
        lc[e_r] = lc.get(0, 0.0)
        # klon zaten depodadır: EV-13/EV-14'teki tt_0i / tt_i0 terimleri 0
        tt0i[o_r] = 0.0
        tt0i[e_r] = 0.0
        tti0[o_r] = 0.0
        tti0[e_r] = 0.0
        for j in Cs:
            if (0, j) in A_set:
                d[o_r, j] = d[0, j]
                tt[o_r, j] = tt[0, j]
            if (j, 0) in A_set:
                d[j, e_r] = d[j, 0]
                tt[j, e_r] = tt[j, 0]

    # ------------------------------------------------------------------
    # Ö4 (2026-08-29, sorun_rc13_darbogaz_kok_neden_analizi.md §6 Ö4):
    # MOLA PENCERESİ YAYILIMI (bwp) — YALNIZCA EV. EV-12 her aktif kaynağa
    # TAM OLARAK BİR öğle molası dayattığından ve bu mola rotanın kronolojik
    # sırasını ikiye böldüğünden (EV-9/EV-11 + EV-7/EV-28 zinciri), bir
    # müşterinin ham [ec,lc] penceresi bu sabit molayla ÇAKIŞIYORSA gerçek
    # fizibıl pencere daha dardır: moladan ÖNCE bitiremiyorsa (ec_i+st_i>el)
    # τ_i MUTLAKA moladan sonraya (>=ll) düşer; moladan SONRA başlayamıyorsa
    # (lc_i<ll) τ_i MUTLAKA moladan önce (<=el-st_i) kalır. Bu daralma her
    # FİZİBIL çözümde zaten DOĞRUDUR (transitivite ile), yalnızca LP
    # gevşetmesinde görünmüyordu — parametreye açıkça yazmak hem EV-16'yı
    # hem (senkronize biçimde) tight_m'i (Ö7a) sıkılaştırıyor.
    #
    # CV'YE TAŞINMADI: CV'nin molası (CV-13) OPSİYONELDİR — bir CV kaynağı
    # molayı hiç kullanmayarak (Σw=0) bu transitivite zincirini tamamen
    # önleyebilir, dolayısıyla ec_i=el olan bir CV müşterisi ll'ye
    # zorlanmaz. Bu yayılımı CV'ye UYGULAMAK GÜVENSİZ olurdu (fizibıl bir
    # "molasız" CV çözümünü kesebilirdi).
    #
    # Yalnızca es/ls/el/ll TÜM ekipler için aynıysa (mevcut veride hep
    # öyle) uygulanır — heterojen vardiya penceresinde güvenli biçimde
    # devre dışı kalır (aksi hâlde hangi ekibin el/ll'sinin kullanılacağı
    # belirsizleşir ve yanlış ekip için tightening geçersiz olabilir).
    _el_vals = set(round(v, 6) for v in el.values())
    _ll_vals = set(round(v, 6) for v in ll.values())
    _bwp_active = len(_el_vals) == 1 and len(_ll_vals) == 1
    if _bwp_active:
        _el_u = next(iter(el.values()))
        _ll_u = next(iter(ll.values()))
        for i in C:
            if ec.get(i, 0.0) + st.get(i, 0.0) > _el_u:
                ec[i] = _ll_u
            if lc.get(i, 0.0) < _ll_u:
                lc[i] = _el_u - st.get(i, 0.0)

    # Ö4b — arc_fix: zaman penceresi tutarsız yayları At'ten (dolayısıyla
    # x/w/Ö1 UB=0 döngüsünün tamamından) tamamen çıkar. i'den en erken
    # ayrılış + seyahat süresi, j'nin en geç varış sınırını aşıyorsa bu yay
    # HİÇBİR fizibıl çözümde kullanılamaz — mola varsayımından bağımsız,
    # HER İKİ modelde güvenli (EV'de bwp SONRASI, dolayısıyla daha sıkı
    # ec/lc ile hesaplanır; bwp uygulanmadıysa ham pencerelerle).
    At = [
        (i, j) for (i, j) in At
        if ec.get(i, 0.0) + st.get(i, 0.0) + tt.get((i, j), 0.0) <= lc.get(j, float('inf')) + 1e-9
    ]
    At_set = set(At)

    # Ö3 (2026-08-29, §6 Ö3): min_veh GEÇERLİ EŞİTSİZLİĞİ — sırt-çantası alt
    # sınırı. Yukarıdaki bwp ile "moladan önce bitiremeyen" (zorunlu
    # öğleden-sonraya kayan) müşteriler belirlenir; bu müşterilerin toplam
    # hizmet süresi TEK bir aktif sefer-diliminin öğleden-sonra kapasitesini
    # (ls-ll) aşıyorsa en az o kadar sefer-dilimi (u[r,k]=1) ZORUNLUDUR.
    # Kısıt, u'nun tanımlandığı yerden SONRA (EV-4 bloğunun ardından)
    # yazılır; burada yalnızca gereken minimum SAYI hesaplanır.
    # KRİTİK: kesit z_veh üzerine DEĞİL, u üzerine yazılmalı — EV-4c yalnızca
    # u<=z_veh der, z_veh=1 hiçbir depo yayını ZORLAMAZ (ölçüldü, §6 Ö3).
    # YALNIZCA EV: aynı CV-uygunsuzluğu gerekçesiyle (bwp notu) CV'ye
    # taşınmadı.
    _min_trips_needed = 0
    if _bwp_active:
        _ls_vals = set(round(v, 6) for v in ls.values())
        if len(_ls_vals) == 1:
            _ls_u = next(iter(ls.values()))
            _afternoon_capacity = _ls_u - _ll_u
            _afternoon_customers = [i for i in C if ec.get(i, 0.0) + st.get(i, 0.0) > _el_u]
            _afternoon_load = sum(st.get(i, 0.0) for i in _afternoon_customers)
            if _afternoon_capacity > 0.0 and _afternoon_load > 0.0:
                _min_trips_needed = math.ceil(_afternoon_load / _afternoon_capacity)

    # Decision variables --------------------------------------------------
    x = model.addVars([(i, j, kk) for (i, j) in At for kk in K], vtype=GRB.BINARY, name="x")
    tau = model.addVars([(i, kk) for i in Nt for kk in K], lb=0.0, name="tau")
    YE = model.addVars(Nt, lb=0.0, name="YE")
    ye = model.addVars(Nt, lb=0.0, name="ye")
    w = model.addVars([(i, j, kk) for (i, j) in At for kk in K], vtype=GRB.BINARY, name="w")

    # Ö1 (2026-08-28, sorun_rc13_darbogaz_kok_neden_analizi.md): YETKİNLİK
    # FİLTRESİNİ x/w ÜZERİNDE UYGULA. EV-2 zaten Ti_K[j] ile hangi
    # kaynakların j'yi ziyaret EDEBİLECEĞİNİ kısıtlıyor, ama x[i,j,kk] her
    # kk için TANIMLI kalıyordu — yetkisiz kk'lar LP'de serbestçe kesirli
    # değer alabiliyordu (saf boyut/simetri kaybı; kök LP sınırını
    # değiştirmez ama düğüm başına iş yükünü büyütür — ölçüm: RC13'te
    # NumVars %-70). Bir kaynak kk, müşteri düğümü i veya j Ti_K[i]/Ti_K[j]
    # içinde değilse o düğümü ASLA TEK BAŞINA ziyaret edemez (EV-2 tekillik
    # garantisi), dolayısıyla bu sabitleme optimal çözümü KESMEZ (baskınlık:
    # yetkisiz kk üzerinden geçmek hem mesafe hem hizmet süresi bedeli öder,
    # üçgen eşitsizliğiyle atlamak asla daha pahalı olamaz). UB=0 (değişken
    # domain'inden çıkarmak yerine) seçildi: ~15 kısıt bloğunun
    # x[i,j,kk]/w[i,j,kk] erişimini bozmadan Gurobi presolve'un bunları
    # BİRİNCİ ADIMDA (sabit değişken elemesi) kaldırmasını sağlar — pratik
    # B&B etkisi domain daraltmayla aynıdır, yalnızca ham (presolve öncesi)
    # NumVars metriği aynı kalır.
    for (i, j) in At:
        for kk in K:
            if (i in C and kk not in Ti_K[i]) or (j in C and kk not in Ti_K[j]):
                x[i, j, kk].UB = 0.0
                w[i, j, kk].UB = 0.0

    # Ö8 (2026-08-29, sorun_rc13_darbogaz_kok_neden_analizi.md §7.2 +
    # Eren'in sorusu): Delta_s KALDIRILDI. Bu değişken "istasyon-kaynak
    # bazlı şarj süresi" olarak tanıtılmıştı ama hiçbir kısıtta gerçek şarj
    # miktarına (YE-ye) BAĞLANMAMIŞTI — yalnızca EV-6/EV-10/EV-15'te
    # kısıtları SIKILAŞTIRAN (asla gevşetmeyen) bir terim olarak geçiyordu,
    # bu yüzden optimizasyon onu her zaman 0'a çekiyordu (fiilen ölü).
    # Gerçek şarj-süresi mekanizması zaten VAR ve ÇALIŞIYOR — EV-17'nin
    # g_e*(YE[i]-ye[i]) terimi — ama yalnızca EV-17'de, EV-6/10/15'te değil.
    # Aşağıda Delta_s'in yerine bu GERÇEK terim geçirildi (aynı büyüklüğü
    # ifade ediyor: istasyonda alınan şarjın zaman maliyeti), böylece
    # istasyondan-çıkış zaman ilerlemesi artık mola VE şarj süresini
    # BİRLİKTE doğru sayıyor (bkz. EV-6/EV-10/EV-15 ve EV-17 altındaki
    # notlar). NOT: EV-6'nın Big-M'i Ö7a ile düğüm-bazlı sıkı forma
    # geçirildiği için eski global `a_max` güvenlik payı artık orada
    # kullanılmıyor (`data['a_max']` hâlâ okunuyor ama fiilen atıl).

    # alpha_s, rho_s, o_s, q_s (parçalı doğrusal şarj eğrisi kırılma
    # noktası ağırlıkları/istasyon SoC'leri): kullanıcı tercihiyle 3.4.2'de
    # GELECEK ÇALIŞMA bileşeni olarak korundu. Burada da aynı şekilde
    # tanımlanmış ancak hiçbir kısıtla ilişkilendirilmemiştir; bu nedenle
    # şu an için modelin çözümünü etkilemezler (bkz. 3.4.2 kısıtlar notu).
    alpha_s = model.addVars([(s, kk, b) for s in S for kk in K for b in B], lb=0.0, name="alpha_s")
    rho_s = model.addVars([(s, kk, b) for s in S for kk in K for b in B], lb=0.0, name="rho_s")
    o_s = model.addVars([(s, kk) for s in S for kk in K], lb=0.0, name="o_s")
    q_s = model.addVars([(s, kk) for s in S for kk in K], lb=0.0, name="q_s")
    # z_ijt / z'_ijt (mola öncesi/sonrası ayrımı): 3.4'te modelden
    # tamamen çıkarıldı (redundant, bkz. Bölüm 3.4 giriş notu) — bu
    # sürümde artık tanımlanmıyor.

    # z_veh (EV-22): araç-ekip atama değişkeni. CV modelinde
    # solution_validator.py ile tespit edilen "aynı aracın iki farklı
    # ekiple çakışan saatlerde kullanılması" hatasının EV modelindeki
    # karşılığını önler (bkz. CV_model_gurobi_exact.py'deki CV-27 notu).
    z_veh = model.addVars(K, vtype=GRB.BINARY, name="z_veh")

    # u_{r,k} (YENİ, 2026-08-23): "kaynak k, r. seferi yapıyor"
    # (CV modelindeki u ile birebir aynı rol).
    u = model.addVars([(r, kk) for r in R for kk in K], vtype=GRB.BINARY, name="u")

    # KAYNAK-SPESİFİK R_max SIKILAŞTIRMASI (2026-08-24): CV modelindeki aynı
    # blokla birebir simetriktir. Klon kümesi global R_max ile boyutlandırılır;
    # daha dar vardiya penceresine sahip bir ekibin fazla sefer klonları
    # u[r,k] = 0 ile kapatılır. es/ls homojen olduğu sürece etkisizdir.
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
    _rename(alpha_s, "alpha_s")
    _rename(rho_s, "rho_s")
    _rename(o_s, "o_s")
    _rename(q_s, "q_s")
    _rename(z_veh, "z_veh")
    _rename(u, "u")

    model._x = x
    model._tau = tau
    model._w = w
    model._A = At
    model._V = V
    model._T = T
    model._K = K
    # Klon altyapısı (print_ev_solution ve dış doğrulayıcılar için)
    model._O = O
    model._E = E
    model._R = R
    model._u = u
    model._z = z_veh
    model._Nt = Nt
    model._clones = clones
    model._R_max = R_max
    model._R_max_info = data.get("R_max_info")
    # Ö2: kk = (v,t) mi yoksa yalnızca t mi? print_ev_solution ve
    # solution_validator.py bu bayrağa göre dallanır.
    model._aggregate_fleet = aggregate_fleet

    # Amaç Fonksiyonu (EV-1)
    model.setObjective(
        gp.quicksum(d[i, j] * x[i, j, kk] for (i, j) in At for kk in K),
        GRB.MINIMIZE
    )

    # Kısıt (EV-2): atama / yetkinlik uyumluluğu.
    for j in C:
        model.addConstr(
            gp.quicksum(x[i, j, kk] for i in Nt for kk in Ti_K[j] if (i, j) in At_set) == 1,
            name=f"EV2_atama_{j}"
        )

    # Kısıt (EV-3): tekil kullanım.
    for (i, j) in At:
        model.addConstr(
            gp.quicksum(x[i, j, kk] for kk in K) <= 1,
            name=f"EV3_tekil_{i}_{j}"
        )

    # Kısıt (EV-4a/b/c/d): ÇOKLU SEFER, KLONLU BİÇİM (2026-08-23).
    # CV-4a..d'nin birebir EV karşılığı:
    #   (EV-4a) Σ_j x[O_r,j,k] = u[r,k]     (EV-4b) Σ_i x[i,E_r,k] = u[r,k]
    #   (EV-4c) u[r,k] <= z_veh[k]          (EV-4d) u[r+1,k] <= u[r,k]
    # Toplandığında eski EV-4 (Σ_j x[0,j,k] <= 3·z_veh[k]) geri gelir.
    for kk in K:
        for r in R:
            model.addConstr(
                gp.quicksum(x[O[r], j, kk] for j in Cs if (O[r], j) in At_set) == u[r, kk],
                name=f"EV4a_cikis_{r}_{kk_name[kk]}"
            )
            model.addConstr(
                gp.quicksum(x[i, E[r], kk] for i in Cs if (i, E[r]) in At_set) == u[r, kk],
                name=f"EV4b_donus_{r}_{kk_name[kk]}"
            )
            model.addConstr(u[r, kk] <= z_veh[kk], name=f"EV4c_z_bagi_{r}_{kk_name[kk]}")
        for r in R[:-1]:
            model.addConstr(u[r + 1, kk] <= u[r, kk], name=f"EV4d_sira_{r}_{kk_name[kk]}")

    # Ö3 (2026-08-29, §6 Ö3): min_veh GEÇERLİ EŞİTSİZLİĞİ. `_min_trips_needed`
    # yukarıda (bwp bloğunda) hesaplandı. `u` üzerine yazılır (bkz. o
    # bloktaki KRİTİK not — z_veh üzerine yazılırsa etkisizdir).
    if _min_trips_needed > 0:
        model.addConstr(
            gp.quicksum(u[r, kk] for r in R for kk in K) >= _min_trips_needed,
            name="EV_Ö3_min_veh_ogleden_sonra"
        )

    # Kısıt (EV-22): ARAÇ-EKİP TEKİLLİĞİ — her araç (v) günde en fazla bir
    # ekibe atanabilir (bkz. CV-27, aynı gerekçe).
    #
    # Ö2 AGGREGATE MODU: k artık (v,t) değil yalnızca t olduğundan "hangi
    # FİZİKSEL aracın hangi ekibe gittiği" modelde temsil edilmiyor.
    # Denk (ve optimal-koruyucu, homojen filoda) ifade: aynı anda aktif
    # ekip sayısı fiziksel araç sayısını AŞAMAZ. Σ_t z_veh[t] <= |V|.
    if aggregate_fleet:
        model.addConstr(
            gp.quicksum(z_veh[t] for t in T) <= len(V),
            name="EV22_arac_kapasitesi_toplam"
        )
    else:
        for v in V:
            model.addConstr(
                gp.quicksum(z_veh[v, t] for t in T) <= 1,
                name=f"EV22_arac_ekip_tekillik_{v}"
            )

    # Kısıt (EV-23): TEKNİSYEN TEKİLLİĞİ — CV-28 ile aynı gerekçe: bir ham
    # teknisyenin aynı gün hem tek başına hem bir ikilinin parçası olarak
    # farklı araçlarda kullanılmasını engeller. Araç indisinden bağımsızdır
    # (yalnızca ekip üyeliğine bakar), bu yüzden aggregate modda da
    # DEĞİŞMEDEN geçerlidir — sadece z_veh[v,t] yerine z_veh[t] toplanır.
    all_raw_techs = set()
    for members in crew_members.values():
        all_raw_techs.update(members)
    for tech in all_raw_techs:
        if aggregate_fleet:
            terms = gp.quicksum(z_veh[t] for t in T if tech in crew_members.get(t, {t}))
        else:
            terms = gp.quicksum(
                z_veh[v, t] for v in V for t in T if tech in crew_members.get(t, {t})
            )
        model.addConstr(terms <= 1, name=f"EV23_teknisyen_tekillik_{tech}")

    # Kısıt (EV-5): akış dengesi — artık YALNIZCA ara düğümlerde (Cs).
    # Depo tarafı EV-4a/4b ile, hem de daha sıkı biçimde (her r için ayrı)
    # sağlanır.
    for i in Cs:
        for kk in K:
            model.addConstr(
                gp.quicksum(x[i, j, kk] for j in Nt if (i, j) in At_set)
                - gp.quicksum(x[j, i, kk] for j in Nt if (j, i) in At_set)
                == 0,
                name=f"EV5_akis_{i}_{kk_name[kk]}"
            )

    # Kısıt (EV-6): istasyon-sonrası zaman ilerlemesi (sıkı Big-M).
    #
    # Ö8 (2026-08-29): Delta_s[s,kk] yerine EV-17'nin GERÇEK şarj-süresi
    # terimi (g_e*(YE[s]-ye[s])) kullanılıyor — bkz. Delta_s tanımının
    # kaldırıldığı yerdeki not.
    #
    # Ö7a (2026-08-29, sıkı Big-M): global (ls+a_max+(ll-el)) sabiti yerine
    # düğüm-bazlı tau_ub(s)-tau_lb(j) + şarj üst sınırı kullanılıyor (bkz.
    # concepts/tight_big_m.md). NOT: `w*(ll-el)` mola terimi Big-M'e EKLENMEDİ
    # — EV-8 (`w<=x`) her (i,j,kk) için geçerli olduğundan x=0 iken w de
    # otomatik 0'dır, yani bu terim Big-M'in "gevşetmesi" gereken durumda
    # zaten kendiliğinden sıfırlanır (CV-31'in orijinal yorumundaki aynı
    # gözlem). Şarj terimi (g_e*(YE-ye)) İSE x'e bağlı DEĞİLDİR (istasyonda
    # şarj, hangi sonraki düğüme gidileceğinden bağımsız gerçekleşir) —
    # bu yüzden Big-M'in KAPSAMASI ZORUNLU kalan tek ek terim budur; aksi
    # hâlde EV-17'de bir kez yaşanan "Big-M geçersiz küçük" hatası
    # (sorun_ev17_big_m_gecersiz_kucuk.md) burada da tekrarlanırdı.
    for s in S:
        for j in Nt:
            if (s, j) not in At_set:
                continue
            for kk in K:
                t_ = _t_of(kk)
                bigM = max(0.0, lc.get(s, 0.0) - ec.get(j, 0.0)) + g_e * _Qk(kk)
                model.addConstr(
                    tau[s, kk]
                    + w[s, j, kk] * (ll[t_] - el[t_])
                    + g_e * (YE[s] - ye[s])
                    + tt[s, j] * x[s, j, kk]
                    - bigM * (1 - x[s, j, kk])
                    <= tau[j, kk],
                    name=f"EV6_istasyon_zaman_{s}_{j}_{kk_name[kk]}"
                )

    # Kısıt (EV-7): müşteri-arası zaman ilerlemesi (mola dahil, sıkı Big-M).
    # j artık depo DÖNÜŞ klonlarını (E[r]) da kapsar.
    #
    # Ö7a (2026-08-29): global (ls-es+(ll-el)) yerine düğüm-bazlı
    # tau_ub(i)-tau_lb(j). NOT: `(ll-el)` mola terimi Big-M'e EKLENMEDİ —
    # EV-8 (`w<=x`) nedeniyle x=0 iken `w*(ll-el)` zaten kendiliğinden 0'dır
    # (bkz. EV-6'daki aynı gözlem). `bwp` (Ö4) uygulandıysa lc[i]/ec[j] zaten
    # daha dar olduğundan bu iki iyileştirme birbirini güçlendirir (bkz.
    # sorun_rc13_darbogaz_kok_neden_analizi.md Ö7 notu: "tek başına LP'yi
    # değiştirmiyor, ama bwp ile birlikte anlamlı").
    for i in C:
        for j in Nt:
            if (i, j) not in At_set:
                continue
            for kk in K:
                t_ = _t_of(kk)
                bigM = max(0.0, lc.get(i, 0.0) - ec.get(j, 0.0))
                model.addConstr(
                    tau[i, kk]
                    + w[i, j, kk] * (ll[t_] - el[t_])
                    + (tt[i, j] + st.get(i, 0.0)) * x[i, j, kk]
                    - bigM * (1 - x[i, j, kk])
                    <= tau[j, kk],
                    name=f"EV7_musteri_zaman_{i}_{j}_{kk_name[kk]}"
                )

    # Kısıt (EV-30) YENİ: DEPODAN ÇIKIŞ ZAMAN İLERLEMESİ — geri alınan
    # EV-21'in DOĞRU hâli (CV-31'in EV karşılığı). tau[O_r,k] ile
    # tau[E_r,k] artık farklı değişkenler olduğu için döngüsel çelişki yok.
    #
    # Ö7a (2026-08-29, sıkı Big-M): eski global `max(0, ls-es-tt[O_r,j])`
    # yerine düğüm-bazlı `tau_ub(O_r)-tau_lb(j)` (bkz. concepts/tight_big_m.md).
    # `(ll-el)` mola terimi Big-M'e eklenmedi — EV-8 (`w<=x`) nedeniyle x=0
    # iken `w*(ll-el)` zaten kendiliğinden 0'dır (orijinal yorumdaki
    # "CV-9 gereği w=0" gözlemiyle aynı, bkz. EV-6/EV-7'deki notlar).
    for r in R:
        for j in Cs:
            if (O[r], j) not in At_set:
                continue
            for kk in K:
                t_ = _t_of(kk)
                bigM = max(0.0, lc.get(O[r], 0.0) - ec.get(j, 0.0))
                model.addConstr(
                    tau[O[r], kk]
                    + w[O[r], j, kk] * (ll[t_] - el[t_])
                    + tt[O[r], j] * x[O[r], j, kk]
                    - bigM * (1 - x[O[r], j, kk])
                    <= tau[j, kk],
                    name=f"EV30_depo_cikis_zaman_{r}_{j}_{kk_name[kk]}"
                )

    # Kısıt (EV-28) YENİ: SEFER SIRASI (CV-29'un EV karşılığı).
    for kk in K:
        t_ = _t_of(kk)
        for r in R[:-1]:
            model.addConstr(
                tau[E[r], kk] <= tau[O[r + 1], kk] + (ls[t_] - es[t_]) * (1 - u[r + 1, kk]),
                name=f"EV28_sefer_sirasi_{r}_{kk_name[kk]}"
            )

    # Kısıt (EV-29) YENİ: KULLANILMAYAN SEFER KLONLARININ ANKRAJI
    # (CV-30'un EV karşılığı; dejenerasyon/simetri temizliği).
    for kk in K:
        t_ = _t_of(kk)
        for r in R:
            model.addConstr(
                tau[O[r], kk] <= es[t_] + (ls[t_] - es[t_]) * u[r, kk],
                name=f"EV29o_bos_sefer_{r}_{kk_name[kk]}"
            )
            model.addConstr(
                tau[E[r], kk] <= es[t_] + (ls[t_] - es[t_]) * u[r, kk],
                name=f"EV29e_bos_sefer_{r}_{kk_name[kk]}"
            )

    # Kısıt (EV-8): mola onayı.
    for (i, j) in At:
        for kk in K:
            model.addConstr(w[i, j, kk] <= x[i, j, kk], name=f"EV8_mola_onay_{i}_{j}_{kk_name[kk]}")

    # Kısıt (EV-9): mola sonrası alt sınır.
    for i in Nt:
        for kk in K:
            t_ = _t_of(kk)
            sum_w_ijk = gp.quicksum(w[i, j, kk] for j in Nt if (i, j) in At_set)
            model.addConstr(
                tau[i, kk] + st.get(i, 0.0) <= el[t_] * sum_w_ijk + ls[t_] * (1 - sum_w_ijk),
                name=f"EV9_mola_sonrasi_{i}_{kk_name[kk]}"
            )

    # Kısıt (EV-10): istasyon mola sonrası alt sınır.
    for s in S:
        for kk in K:
            t_ = _t_of(kk)
            sum_w_sjk = gp.quicksum(w[s, j, kk] for j in Nt if (s, j) in At_set)
            model.addConstr(
                tau[s, kk] + g_e * (YE[s] - ye[s]) <= el[t_] * sum_w_sjk + ls[t_] * (1 - sum_w_sjk),
                name=f"EV10_istasyon_mola_sonrasi_{s}_{kk_name[kk]}"
            )

    # Kısıt (EV-11): mola öncesi üst sınır.
    for i in Nt:
        for kk in K:
            t_ = _t_of(kk)
            sum_w_jik = gp.quicksum(w[j, i, kk] for j in Nt if (j, i) in At_set)
            model.addConstr(
                tau[i, kk] >= ll[t_] * sum_w_jik + es[t_] * (1 - sum_w_jik),
                name=f"EV11_mola_oncesi_{i}_{kk_name[kk]}"
            )

    # Kısıt (EV-12): ZORUNLU MOLA — GÜNDE AKTİF KAYNAK BAŞINA TAM OLARAK
    # BİR öğle molası.
    #
    # DEĞİŞİKLİK (2026-08-23, klon tasarımıyla ZORUNLU): eski hâl
    #   Σ w[i,j,k] == Σ_j x[0,j,k]   (= sefer sayısı)
    # idi, yani 2 sefer yapan kaynağa 2 mola ZORUNLU kılıyordu. Mola
    # penceresi günde tek ve sabit olduğundan ([el_k, ll_k]) ve EV-9/EV-11
    # iki molanın da aynı pencereyi işgal etmesini dayattığından, sefer
    # sırası kısıtı (EV-28) eklendiğinde bu
    #   1. sefer molası => tau[E_1] >= ll ; 2. sefer molası => tau[O_2] <= el
    #   EV-28           => tau[E_1] <= tau[O_2]   =>  ll <= el   => ÇELİŞKİ
    # üretir. Eşitlik olduğu gibi bırakılsaydı model infeasible OLMAZ, ama
    # Gurobi sessizce u[2,k]=0 seçer ve EV fiilen TEK SEFERLİ modele geri
    # dönerdi — yani düzeltme ölçülemez hâle gelirdi. Sayım tabanı bu yüzden
    # "sefer sayısı"ndan "aktif kaynak"a (z_veh[k]) çevrilmiştir. CV/EV
    # ayrımı (CV opsiyonel "<=", EV zorunlu "==") KORUNUR.
    # Bkz. decisions/celiski_ogle_molasi_zorunlulugu.md
    for kk in K:
        model.addConstr(
            gp.quicksum(w[i, j, kk] for (i, j) in At) == z_veh[kk],
            name=f"EV12_mola_zorunlu_{kk_name[kk]}"
        )

    # Kısıt (EV-13)-(EV-14): mesai saatleri sınırları.
    # Klon düğümlerde tt_0i = tt_i0 = 0'dır (klon zaten depodadır).
    for i in Nt:
        for kk in K:
            t_ = _t_of(kk)
            model.addConstr(tau[i, kk] - tt0i[i] >= es[t_], name=f"EV13_es_{i}_{kk_name[kk]}")
            model.addConstr(
                tau[i, kk] + st.get(i, 0.0) + tti0[i] <= ls[t_],
                name=f"EV14_ls_{i}_{kk_name[kk]}"
            )

    # Kısıt (EV-15): istasyon mesai üst sınırı.
    for s in S:
        for kk in K:
            t_ = _t_of(kk)
            model.addConstr(
                tau[s, kk] + g_e * (YE[s] - ye[s]) + tts0[s] <= ls[t_],
                name=f"EV15_istasyon_ls_{s}_{kk_name[kk]}"
            )

    # Kısıt (EV-16): zaman penceresi.
    for i in Nt:
        for kk in K:
            model.addConstr(tau[i, kk] >= ec[i], name=f"EV16_lb_{i}_{kk_name[kk]}")
            model.addConstr(tau[i, kk] <= lc[i], name=f"EV16_ub_{i}_{kk_name[kk]}")

    # Kısıt (EV-17): batarya seviyesiyle uyumlu zaman ilerlemesi
    # (Keskin & Çatay, 2016 — doğrusal kısmi şarj).
    #
    # DÜZELTME (2026-08-22, trsp-exact-model-mimari): depo yayları (i==0
    # veya j==0) bu kısıttan HARİÇ tutulur — CV modelindeki muadili
    # (CV-19, bkz. CV_model_gurobi_exact.py:330-345) zaten böyle
    # yazılmıştır. Önceki hâlde i==0 dahil ediliyordu ve tau[0,k]
    # "depoya DÖNÜŞ zamanı" olarak kullanıldığından (bkz. aşağıdaki
    # "EV-21 geri alındı" notu) EV-7'nin j=0 hâliyle birlikte
    # tau[0,k] + (pozitif tur süresi) <= tau[0,k] biçiminde DÖNGÜSEL bir
    # çelişki üretiyordu. Bu, EV-21'in geri alınma gerekçesinin EV-17
    # üzerinden arka kapıdan geri sızmış hâliydi.
    #
    # NOT (2026-08-23): depo yayı istisnası artık KLON yayları üzerinden
    # yazılır (i in clones or j in clones). Bu filtrenin genişletilmesi
    # ZORUNLUDUR: atlanırsa ye[o_r]/ye[e_r] yer tutucuları üzerinden sahte
    # kısıt üretilir ve sorun_ev_depo_yaylarinda_dongusel_infeasibility
    # geri gelir.
    for (i, j) in At:
        if i in clones or j in clones:
            continue
        for kk in K:
            t_ = _t_of(kk)
            # Ö8 (2026-08-29): EKSİK MOLA TERİMİ EKLENDİ (`w*(ll-el)`).
            # EV-17 önceden şarj süresini (g_e*(YE-ye)) doğru hesaplıyordu
            # ama mola süresini hiç içermiyordu — bir kaynak bir istasyonda
            # şarj olduktan HEMEN SONRA molaya girerse (ve tersi), ne EV-6
            # (mola-farkında ama önceden Delta_s ile şarj-farkında DEĞİLDİ)
            # ne de EV-17 (şarj-farkında ama mola-farkında DEĞİLDİ) ikisini
            # BİRLİKTE zorunlu kılıyordu — teorik bir fizibilite gevşekliği
            # (Eren'in sorusu üzerine bulundu). Müşteri düğümlerinde bu
            # terim zararsızdır: EV-27 nedeniyle YE[i]==ye[i] (şarj terimi
            # zaten 0) ve EV-7 zaten aynı mola terimini içerdiğinden EV-17
            # orada fazladan/örtüşen ama YİNE GEÇERLİ bir kısıt olarak kalır.
            #
            # Ö7a (2026-08-29, sıkı Big-M): düğüm-bazlı tau_ub(i)-tau_lb(j)
            # formülüne geçildi; eski `max(lc0, ls-es)+g_e*Qk` biçimi artık
            # gereksiz (lc0 güvenlik payı, sıkı formülün kendisi zaten
            # ec/lc'den doğru türetildiği için gerekmiyor). `(ll-el)` mola
            # terimi Big-M'e EKLENMEDİ — EV-8 (`w<=x`) nedeniyle x=0 iken
            # `w*(ll-el)` zaten kendiliğinden 0'dır (bkz. EV-6/EV-7/EV-30
            # notları). Şarj terimi (g_e*(YE-ye)) İSE x'ten bağımsız olduğu
            # için (istasyonda şarj miktarı hangi sonraki düğüme
            # gidileceğine bağlı değildir) Big-M'de KALMAK ZORUNDADIR — aksi
            # hâlde sorun_ev17_big_m_gecersiz_kucuk.md'nin aynısı burada
            # yeniden yaşanırdı.
            bigM = max(0.0, lc.get(i, 0.0) - ec.get(j, 0.0)) + g_e * _Qk(kk)
            model.addConstr(
                tau[i, kk]
                + w[i, j, kk] * (ll[t_] - el[t_])
                + tt[i, j] * x[i, j, kk]
                + g_e * (YE[i] - ye[i])
                - bigM * (1 - x[i, j, kk])
                <= tau[j, kk],
                name=f"EV17_batarya_zaman_{i}_{j}_{kk_name[kk]}"
            )

    # Kısıt (EV-18)-(EV-19): batarya tüketimi (varış/ayrılış üzerinden).
    #
    # DÜZELTME 1 (2026-08-22): depo yayları (i==0 veya j==0) HARİÇ.
    # Önceki hâlde bu kısıtlar depo yaylarını da kapsıyordu; ye[0] tek bir
    # değişken olduğu için 0 -> ... -> 0 kapalı turu boyunca zincir
    # ye[0] <= ye[0] - h_e * (tur mesafesi) biçimine indirgeniyor ve MODELİ
    # HER ROTA İÇİN INFEASIBLE yapıyordu (Gurobi IIS ile doğrulandı: C5,
    # 0-1-5-4-0 turu için IIS tam olarak dört adet EV18_ub kısıtından
    # oluşuyor). CV modelinin muadili (CV-20/CV-21,
    # CV_model_gurobi_exact.py:353-367) bu istisnayı zaten içeriyordu;
    # depo bacakları orada CV-23/CV-24/CV-25 ile ayrıca ele alınıyor.
    # Aynı yapı burada EV-24/EV-25/EV-26 olarak eklenmiştir.
    #
    # DÜZELTME 2 (A1, 2026-08-22): EV-18 (varış enerjisi ye[i] üzerinden
    # yazılan zincir) artık İSTASYON düğümlerinden çıkan yaylarda
    # yazılmaz. Aksi hâlde EV-20 gereği YE[s] >= ye[s] olduğundan EV-18
    # her zaman EV-19'dan sıkı kalır ve istasyonda alınan şarj miktarı
    # bir sonraki bacağın enerji bütçesine HİÇ yansımaz (şarj etmek
    # tamamen etkisiz kalır). Bkz. decisions/karar_a1_ev_sarj_c20_c21_
    # duzeltmesi.md ve src/EV_v_1_1_fixed.py:472-483.
    #
    # NOT (2026-08-23): istasyon istisnası (i not in S_set) klonlamadan
    # ETKİLENMEZ — istasyonlar Cs içinde kalır, klonlanmaz.
    #
    # Ö7b (2026-08-29): EV18_lb/EV19_lb (`ye[j] >= 0.0`) KALDIRILDI —
    # `ye` zaten `lb=0.0` ile tanımlı (bkz. değişken tanımı), bu satırlar
    # hiçbir şey yapmıyordu ve RC13'te 24480 gereksiz kısıt (toplamın
    # %26'sı) üretiyordu. Presolve bunları zaten atıyordu; kaldırılması
    # yalnızca model kurma/`.lp` yazma süresini kısaltır, çözüm davranışını
    # DEĞİŞTİRMEZ.
    S_set = set(S)
    for (i, j) in At:
        if i in clones or j in clones:
            continue
        for kk in K:
            Qk = _Qk(kk)
            if i not in S_set:
                model.addConstr(
                    ye[j] <= ye[i] - (h_e * d[i, j]) * x[i, j, kk] + Qk * (1 - x[i, j, kk]),
                    name=f"EV18_ub_{i}_{j}_{kk_name[kk]}"
                )
            model.addConstr(
                ye[j] <= YE[i] - (h_e * d[i, j]) * x[i, j, kk] + Qk * (1 - x[i, j, kk]),
                name=f"EV19_ub_{i}_{j}_{kk_name[kk]}"
            )

    # Kısıt (EV-20): ayrılış batarya seviyesi sınırları.
    for i in Nt:
        for kk in K:
            model.addConstr(ye[i] <= YE[i], name=f"EV20_lb_{i}_{kk_name[kk]}")
            model.addConstr(YE[i] <= _Qk(kk), name=f"EV20_ub_{i}_{kk_name[kk]}")

    # Kısıt (EV-24)-(EV-25): DEPODA TAM ŞARJ (yeni, 2026-08-22).
    # CV modelindeki CV-23/CV-24'ün (CV_model_gurobi_exact.py:379-397)
    # birebir EV karşılığı. EV-18/EV-19'dan depo yayları çıkarıldığı için
    # enerji zincirinin bir BAŞLANGIÇ ANKRAJINA ihtiyacı vardır: aksi
    # hâlde ye[j] yalnızca [0, Q] kutu sınırıyla sınırlı kalır ve enerji
    # kısıtları fiilen devre dışı kalırdı. Depodan ayrılan araç tam dolu
    # kabul edilir (matematiksel modelde CV-23/CV-24 ile aynı gerekçe);
    # bu aynı zamanda çoklu seferin (EV-4) kullandığı tek şarj
    # mekanizmasının resmi ifadesidir.
    # Her sefer (r) için ayrı yazılır: mesafe d[0,j] aynı kalır (klon takma
    # adı) ve en fazla biri aktiftir (x en fazla bir r için 1). Böylece her
    # seferin başındaki TAM ŞARJ ayrı bir yay üzerinden ifade edilir —
    # çoklu seferin kullandığı tek şarj mekanizması güçlenir.
    for r in R:
        for j in Cs:
            if (O[r], j) not in At_set:
                continue
            for kk in K:
                Qk = _Qk(kk)
                model.addConstr(
                    ye[j] <= Qk - (h_e * d.get((0, j), 0.0)) * x[O[r], j, kk]
                    + Qk * (1 - x[O[r], j, kk]),
                    name=f"EV24_depo_sarj_ub_{r}_{j}_{kk_name[kk]}"
                )
                model.addConstr(
                    ye[j] >= Qk - (h_e * d.get((0, j), 0.0)) - Qk * (1 - x[O[r], j, kk]),
                    name=f"EV25_depo_sarj_lb_{r}_{j}_{kk_name[kk]}"
                )

    # Kısıt (EV-26): DEPOYA DÖNÜŞ ENERJİSİ (yeni, 2026-08-22).
    # CV-25'in (CV_model_gurobi_exact.py:399-409) EV karşılığı. EV-18/19
    # depo yaylarını kapsamadığından, dönüş bacağının enerji açısından
    # hiç denetlenmemesi riski doğar; bu kısıt onu kapatır. İstasyon
    # düğümleri de dahil edildiğinden AYRILIŞ enerjisi (YE) kullanılır;
    # müşteri düğümlerinde EV-27 gereği YE[i] == ye[i] olduğu için bu,
    # CV-25 ile birebir aynı davranışı verir.
    # Dönüş göstergesi klonlar üzerinden toplulaştırılır: Σ_r x[i,E_r,k]
    # (en fazla bir terim 1'dir).
    for i in Cs:
        if (i, 0) not in A_set:
            continue
        for kk in K:
            ret_i = gp.quicksum(x[i, E[r], kk] for r in R if (i, E[r]) in At_set)
            model.addConstr(
                YE[i] >= (h_e * d.get((i, 0), 0.0)) * ret_i,
                name=f"EV26_donus_enerjisi_{i}_{kk_name[kk]}"
            )

    # Kısıt (EV-27): MÜŞTERİ DÜĞÜMÜNDE ŞARJ YOK (yeni, 2026-08-22).
    # CV-22'nin (CV_model_gurobi_exact.py:369-377, "YC[i] == yc[i]")
    # EV karşılığı. EV-20 yalnızca ye[i] <= YE[i] <= Q dediğinden, önceki
    # hâlde model bir MÜŞTERİ düğümünde de "şarj olabiliyordu" (fiziksel
    # olarak imkânsız; Keskin & Çatay (2016) formülasyonunda da
    # Y_i = y_i yalnızca istasyon olmayan düğümler için serbest bırakılır).
    # Bu kısıt olmadan A1 düzeltmesinin etkisi de ölçülemez hâle gelirdi.
    for i in C:
        model.addConstr(YE[i] == ye[i], name=f"EV27_musteride_sarj_yok_{i}")

    # NOT (EV-21 TARİHÇESİ, 2026-08-23'te ÇÖZÜLDÜ): CV modelinde aynı
    # fikirle denenen kısıt (CV-26/EV-21), tau[0,k]'nin CV-8/EV-7'nin j=0
    # hâli tarafından zaten "dönüş zamanı" olarak kullanılmasıyla çelişip
    # döngüsel infeasibility yarattığı için geri alınmıştı. Geri alma
    # ZARARSIZ DEĞİLDİ: aynı kaynağın seferleri zaman olarak çakışabiliyordu.
    # Bu sürümde depo klonlanarak (O[r]/E[r]) sorun kökten çözülmüş, EV-30
    # (çıkış zaman ilerlemesi = EV-21'in doğru hâli), EV-28 (sefer sırası)
    # ve EV-29 (boş sefer ankrajı) eklenmiştir.

    # Gelecek çalışma bileşenleri modelde tanımlı tutulur (bkz. yukarıdaki
    # not) ancak herhangi bir kısıtta kullanılmadıkları için Gurobi
    # tarafında "kullanılmayan değişken" uyarısını bilinçli olarak kabul
    # ediyoruz; bu satır yalnızca referans bütünlüğü içindir.
    _ = (N, alpha_s, rho_s, o_s, q_s)

    return model


def format_time(seconds: float) -> str:
    if seconds is None:
        return "--:--"
    seconds = max(0, round(seconds))
    shifted_seconds = seconds + 28800
    h = (shifted_seconds // 3600) % 24
    m = (shifted_seconds % 3600) // 60
    return f"{h:02d}:{m:02d}"


def print_ev_solution(data, model, out_name):
    """CV_model_gurobi_exact.print_cv_solution ile aynı mantıkla, EV
    modeli için rota/saat çizelgesi raporu üretir. Önceki sürümde EV için
    böyle bir raporlama fonksiyonu yoktu (yalnızca amaç değeri/durum
    yazdırılıyordu); bu fonksiyon o eksikliği giderir."""
    log_filename = f"Operasyon_Raporu_EV_{out_name}.txt"

    with open(log_filename, "w", encoding="utf-8") as f:

        def log_print(text=""):
            # DÜZELTME (2026-08-22): bkz. CV_model_gurobi_exact.py'deki aynı
            # not — emoji içeren satırlar cp1254 konsolda UnicodeEncodeError
            # ile scripti çökertiyordu.
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
        log_print(f"       GÜNLÜK OPERASYON DETAYLI ZAMAN ÇİZELGESİ (EV) - {out_name}")
        log_print("=" * 65)

        for kk, arcs in sorted(routes.items()):
            # Ö2 AGGREGATE MODU: kk = t (skaler crew id), fiziksel araç
            # kimliği modelde YOK — yalnızca "en fazla |V| ekip aynı anda
            # aktif" garantisi var (EV22_arac_kapasitesi_toplam). Rapor
            # amacıyla araç adı yerine "Araç?" yer tutucusu yazılır; hangi
            # fiziksel aracın kullanılacağı homojen filoda hiçbir zaman
            # infeasibility üretmeyen bir post-processing atamasıdır.
            if isinstance(kk, tuple):
                v, t = kk
            else:
                v, t = "Arac?", kk
            ekip_isimleri = t.replace('_', ' & ')

            # DÜZELTME (2026-08-22): mola süresi sabit 3600 s varsayılıyordu;
            # modelde mola, EV-6/EV-7'ye w_ijk*(ll_k - el_k) terimiyle
            # giriyor (mevcut veriyle 7200 s). Bkz. CV tarafındaki aynı not.
            # Mola aralığı, modelin fiilen dayattığı pencere olarak yazılır
            # (EV-9: mola öncesi hizmet el_k'den önce biter, EV-11: mola
            # sonrası varış ll_k'den sonradır) — bkz. CV'deki aynı düzeltme.
            break_start = float(data['el'][t])
            break_end = float(data['ll'][t])
            break_dur = break_end - break_start
            break_h = break_dur / 3600.0
            break_label = f"{break_h:.0f} Saat" if abs(break_h - round(break_h)) < 1e-9 else f"{break_h:.2f} Saat"

            # bkz. CV_model_gurobi_exact.print_cv_solution'daki aynı
            # çoklu-sefer ayrıştırma mantığı. DÜZELTME (2026-08-23): depo
            # artık sefer-indeksli klonlarla temsil ediliyor (O[r]/E[r]),
            # bu yüzden depo çıkışları "i == 0" ile değil "i in O" ile
            # bulunur; r indisi kronolojik sırayı verir (EV-28).
            o_of_node = {node: r for r, node in getattr(model, '_O', {}).items()}
            e_of_node = {node: r for r, node in getattr(model, '_E', {}).items()}

            next_map = {}
            depot_departures = []   # (r, ilk_dugum)
            for i, j in arcs:
                if i in o_of_node:
                    depot_departures.append((o_of_node[i], j))
                else:
                    next_map[i] = j
            depot_departures.sort()

            trips = []
            trip_rr = []
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

            log_print(f"🔋 {v} ARACI OPERASYON RAPORU (Ekip: {ekip_isimleri}, {len(trips)} sefer)")
            log_print(f"  👷 Ekip           : {ekip_isimleri}")
            log_print(f"  📏 Toplam Mesafe (tüm seferler) : {toplam_mesafe_kk:.2f} metre")

            for trip_idx, (route, (r_out, r_in)) in enumerate(zip(trips, trip_rr), start=1):
                total_distance = sum(d.get((route[idx], route[idx + 1]), 0.0) for idx in range(len(route) - 1))
                log_print(f"  --- Sefer {trip_idx}/{len(trips)} (model sefer indisi r={r_out}) ---")
                log_print(f"  📏 Sefer Mesafesi : {total_distance:.2f} metre")
                log_print(f"  🕒 Kronolojik Zaman Çizelgesi ve Akışı:")

                # bkz. CV tarafındaki aynı not: klon zaman değişkenleri
                # (τ[o_r] / τ[e_r]) teşhis satırı olarak yazdırılır; rapor
                # çizelgesi fiziksel olarak en sıkı türetilmiş değeri kullanır.
                first_customer = route[1]
                depot_departure_val = tau[first_customer, kk].X - tt.get((0, first_customer), 0.0)
                if hasattr(model, '_O'):
                    _mo = tau[model._O[r_out], kk].X
                    _me = tau[model._E[r_in], kk].X if r_in is not None else None
                    log_print(
                        f"     (model: τ[o_{r_out}] = {format_time(_mo)}"
                        + (f" , τ[e_{r_in}] = {format_time(_me)}" if _me is not None else "")
                        + ")"
                    )

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
                        log_print(
                            f"     [ {format_time(depot_departure_val)} ] ➔ Depodan Çıkış yapıldı. Nokta: {curr_node} ({node_name})")
                    elif idx == len(route) - 1:
                        prev_node = route[idx - 1]
                        end_val = tau[prev_node, kk].X + st.get(prev_node, 0.0) + tt.get((prev_node, 0), 0.0)

                        if _break_on(idx):
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

                last_customer = route[-2]
                end_time = tau[last_customer, kk].X + st.get(last_customer, 0.0) + tt.get((last_customer, 0), 0.0)
                if _break_on(len(route) - 1):
                    end_time = break_end + tt.get((last_customer, 0), 0.0)
                total_duration = end_time - depot_departure_val
                duration_h = int(total_duration // 3600)
                duration_m = int((total_duration % 3600) // 60)
                log_print(f"  ⏳ Sefer Süresi: {duration_h} saat {duration_m} dakika")

            log_print("-" * 65)

    # DÜZELTME (2026-08-22): bkz. CV_model_gurobi_exact.py'deki aynı not —
    # bu satır `with` bloğunun dışında olduğu için log_print koruması
    # kapsamıyordu.
    try:
        print(f"\n✅ Çıktı '{log_filename}' dosyasına başarıyla kaydedildi!")
    except UnicodeEncodeError:
        print(f"\n[OK] Cikti '{log_filename}' dosyasina basariyla kaydedildi!")


if __name__ == "__main__":
    import itertools
    import xml.etree.ElementTree as ET

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

    root = os.path.dirname(__file__)
    # NOT: yalnızca trsp_problem_sets kullanılıyor. "problem_sets" klasöründeki
    # örneklerde RequiredSkill verisi bulunmuyor; bu, yetkinlik bazlı ekip
    # ataması boş kalıp modelin anında infeasible olmasına yol açıyordu
    # (smoke test sırasında tespit edildi). CV ile aynı, yetkinlik etiketli
    # örnekler kullanılarak iki filo adil biçimde karşılaştırılabilir hale
    # getirildi.
    problem_dirs = ["trsp_problem_sets"]
    instances = load_problem_instances(root, problem_dirs)
    instances = select_instances(instances)
    vehicle_file = os.path.join(root, "FC_Info4Vehicle4EV.xml")
    vehicles, vehicle_attrs = parse_vehicle_file(vehicle_file, expected_type="EV")
    station_file = os.path.join(root, "Kalabak_Info4ChargingStations.xml")
    stations = parse_charging_stations(station_file)

    # NOT: Önceki sürümde tek bir yer tutucu teknisyen (["tech1"]) kullanılıyordu.
    # CV_model_gurobi_exact.py ile tutarlı ve karşılaştırılabilir sonuçlar
    # üretebilmek için burada da CV'deki yetkinlik bazlı ekip kurulum mantığı
    # uygulanmıştır (bkz. CV_model_gurobi_exact.py __main__).
    employee_file = os.path.join(root, "Info4Employee.xml")
    skill_tech_map = {}
    all_technicians = []
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
            "s5": ["TECH_008"],
        }

    for instance_name, instance in instances.items():
        out_name = os.path.splitext(os.path.basename(instance_name))[0]
        print(f"\n== {out_name} için EV modeli kuruluyor ==")

        data = prepare_ev_data_from_instance(
            instance,
            vehicles,
            vehicle_attrs,
            stations,
            technicians=all_technicians,
        )

        # Türetilmiş R_max'ın hangi gerekçeyle seçildiğini koşum çıktısına yaz
        # (bkz. xml_data_loader.derive_r_max).
        _rmi = data.get('R_max_info') or {}
        _reason = next(iter((_rmi.get('reasons') or {}).values()), 'varsayilan')
        print(f"   R_max = {data.get('R_max')} ({_reason})")
        # Ö6 (2026-08-28): istasyonlar enerji hiç bağlamadığı için düşürüldü mü?
        if data.get('stations_dropped'):
            print(f"   Sarj istasyonlari DUSURULDU (enerji hic baglamiyor, S=[])")

        # NOT: instance_name, root'a GÖRELİ bir yoldur; cwd script'in
        # klasörüyle aynı değilse (örn. VS Code'un Run düğmesi) doğrudan
        # ET.parse(instance_name) dosyayı bulamaz (bkz.
        # CV_model_gurobi_exact.py'deki aynı düzeltme notu).
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

        base_es = data['es'][all_technicians[0]]
        base_ls = data['ls'][all_technicians[0]]
        base_el = data['el'][all_technicians[0]]
        base_ll = data['ll'][all_technicians[0]]
        data['es'] = {crew: base_es for crew in T_list}
        data['ls'] = {crew: base_ls for crew in T_list}
        data['el'] = {crew: base_el for crew in T_list}
        data['ll'] = {crew: base_ll for crew in T_list}

        C = sorted(data['C'])
        for idx, c_idx in enumerate(C):
            if idx < len(delivery_skills):
                req_skill = delivery_skills[idx]
                allowed_crews = [crew for crew in T_list if req_skill in crew_skills[crew]]
                data['T_i'][c_idx] = allowed_crews
            else:
                data['T_i'][c_idx] = T_list[:]

        m = build_model(data)
        # NOT: Gurobi'nin m.write() fonksiyonu, mutlak yol Türkçe karakter
        # içerdiğinde ("Masaüstü" gibi) "Unable to write to file" hatasıyla
        # çöküyor (test sırasında tespit edildi; ASCII yolda veya göreli
        # yolda sorun yok). Bu yüzden göreli dosya adı kullanılır (CV
        # kodundaki mevcut çalışma dizini yaklaşımıyla aynı) ve olası
        # başka bir ortamda da çökmeyi önlemek için try/except eklenmiştir.
        lp_path = f"ev_model_{out_name}.lp"
        m.update()
        try:
            m.write(lp_path)
            print(f"EV model kuruldu ve '{lp_path}' olarak yazildi.")
        except gp.GurobiError as e:
            print(f"Uyarı: LP dosyası yazılamadı ({e}); optimizasyona devam ediliyor.")
        m.setParam('TimeLimit', 10800)
        m.setParam('MIPGap', 0.005)
        m.setParam('MIPFocus', 2)
        m.setParam('Heuristics', 0.15)
        m.setParam('NoRelHeurTime', 600)
        m.setParam('LogFile', f"gurobi_log_ev_{out_name}.log")
        m.optimize()
        print(f"Status for {instance_name}: {m.Status}")
        if m.SolCount > 0:
            print(f"Objective: {m.ObjVal:.4f}")
