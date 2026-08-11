import xml.etree.ElementTree as ET
import random
import os
import glob

# 1. PARAMETRELER VE KURALLAR
SERVICE_TIMES = {
    'P1': (3600, 7200), 'P2': (3600, 7200), 'P3': (3600, 7200),
    'P4': (1800, 3600), 'P5': (900, 2700)
}

# Sabit Zaman Pencereleri (08:00 = 0. saniye referans alınarak)
PREDEFINED_WINDOWS = [
    (0, 14400),      # Seçenek 1: 08:00 - 12:00
    (14400, 36000),  # Seçenek 2: 12:00 - 18:00
    (0, 36000)       # Seçenek 3: 08:00 - 18:00 (Tüm Gün)
]

SKILLS = {'P1': 's1', 'P2': 's2', 'P3': 's3', 'P4': 's4', 'P5': 's5'}
HORIZON = 36000 

# 2. ÜRETİM FONKSİYONU
def generate_task_data(task_type):
    st_i = random.randint(*SERVICE_TIMES[task_type])
    ec_i, lc_i = random.choice(PREDEFINED_WINDOWS)
    return st_i, ec_i, lc_i

# 3. ORANTISAL DAĞILIM FONKSİYONU 
def get_task_distribution(num_nodes):
    dist = []
    dist.extend(['P5'] * int(round(num_nodes * 0.35)))
    dist.extend(['P1'] * int(round(num_nodes * 0.20)))
    dist.extend(['P4'] * int(round(num_nodes * 0.20)))
    dist.extend(['P2'] * int(round(num_nodes * 0.15)))
    dist.extend(['P3'] * int(round(num_nodes * 0.10)))
    
    while len(dist) < num_nodes: dist.append('P5')
    while len(dist) > num_nodes: dist.pop()
    
    random.shuffle(dist) 
    return dist

# 4. XML DOSYALARINI GÜNCELLEME İŞLEMİ
def process_all_xmls(input_folder, output_folder):
    abs_input = os.path.abspath(input_folder)
    abs_output = os.path.abspath(output_folder)
    
    if not os.path.exists(abs_output):
        os.makedirs(abs_output)
        
    xml_files = glob.glob(os.path.join(abs_input, "*.xml"))
    
    # HAFIZA SÖZLÜĞÜ (Aynı N değeri için aynı profilleri tutar)
    PROFILE_CACHE = {}
    
    for file_path in xml_files:
        filename = os.path.basename(file_path)
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        delivery_nodes = root.findall('.//Node[@Type="Delivery"]')
        num_nodes = len(delivery_nodes)
        
        if num_nodes == 0:
            continue
            
        # EĞER BU MÜŞTERİ SAYISINI (Örn: 5) İLK KEZ GÖRÜYORSAK ÜRET VE HAFIZAYA YAZ
        if num_nodes not in PROFILE_CACHE:
            task_list = get_task_distribution(num_nodes)
            profiles = []
            for t_type in task_list:
                st_i, ec_i, lc_i = generate_task_data(t_type)
                profiles.append((t_type, st_i, ec_i, lc_i))
            
            PROFILE_CACHE[num_nodes] = profiles
            
        # HAFIZADAKİ SABİT PROFİLİ ÇEK
        current_profiles = PROFILE_CACHE[num_nodes]
        
        for idx, node in enumerate(delivery_nodes):
            # Rastgele üretmek yerine hafızadaki profili kullanıyoruz
            task_type, st_i, ec_i, lc_i = current_profiles[idx]
            
            request = node.find('.//Request')
            if request is not None:
                request.set('ProductId', task_type)
                request.set('ProductName', f"{task_type}_Gorevi")
                request.set('ReadyTime', str(ec_i))
                request.set('DueDate', str(lc_i))
                request.set('ServiceTime', str(st_i))
                request.set('RequiredSkill', SKILLS[task_type]) 
                
        out_path = os.path.join(abs_output, filename)
        tree.write(out_path, encoding='utf-8', xml_declaration=True)
        print(f"Basarili: {filename} dönüştürüldü ({num_nodes} müşteri - Hafızadan kopyalandı).")

if __name__ == "__main__":
    # Tekrar aynı sonuçları almak istersen diye sabitleyici (Opsiyonel)
    random.seed(42) 
    process_all_xmls('problem_sets', 'trsp_problem_sets')