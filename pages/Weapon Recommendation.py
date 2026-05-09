import streamlit as st
import pandas as pd
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="MHST Armory", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df_m = pd.read_csv('MHST_monsties.csv')
        df_w = pd.read_csv('Weapon Monster Hunter Stories.csv')
        
        # Membersihkan kolom 'No' jika ada
        if 'No' in df_m.columns:
            df_m = df_m.drop(columns=['No'])
            
        # Pre-processing Data Senjata
        # Bersihkan simbol persentase (%) dari kolom Critical agar bisa dikalkulasi
        df_w['Critical'] = df_w['Critical'].astype(str).str.replace('%', '', regex=False).str.replace('nan', '0', regex=False).astype(float)
        
        # Konversi kolom ke numerik untuk perhitungan matematika
        for col in ['Attack Max', 'Attack Dasar', 'Nilai Elemen']:
            df_w[col] = pd.to_numeric(df_w[col], errors='coerce').fillna(0).astype(int)
            
        return df_m, df_w
    except FileNotFoundError:
        st.error("File CSV tidak ditemukan. Pastikan 'MHST_monsties.csv' dan 'Weapon Monster Hunter Stories.csv' ada di direktori yang sama.")
        st.stop()

df_monster, df_weapon = load_data()

# --- KAMUS EMOJI ---
elemen_emojis = {
    'Fire': '🔥', 'Water': '💧', 'Thunder': '⚡', 'Ice': '❄️', 'Dragon': '🐉', 'Raw': '⚔️'
}
tipe_senjata_emojis = {
    'Sword And Shield': '🗡️🛡️ SnS',
    'Great Sword': '🗡️ GS',
    'Hammer': '🔨 Hammer',
    'Hunting Horn': '📯 Horn'
}

# --- HELPER: ANALISIS LAWAN ---
def get_monster_stats(monster_name, df_m):
    stats = df_m[df_m['Monster'] == monster_name].iloc[0]
    res = {
        'Fire': stats['Res_Fire'], 'Water': stats['Res_Water'], 
        'Thunder': stats['Res_Thunder'], 'Ice': stats['Res_Ice'], 'Dragon': stats['Res_Dragon']
    }
    weakest_val = min(res.values())
    strongest_val = max(res.values())
    
    weak_elements = [k for k, v in res.items() if v == weakest_val]
    strong_elements = [k for k, v in res.items() if v == strongest_val]
    
    # Hitung Threat Level Monster
    threat_level = stats['HP'] + stats['Defence']
    
    return stats, res, weak_elements, strong_elements, threat_level

# --- LOGIKA 1: REKOMENDASI SENJATA UNTUK MONSTER (DIUPDATE: ANTI-SUICIDE/OVERKILL) ---
def recommend_weapons(monster_name, df_w, df_m):
    stats, res_dict, weak_elements, strong_elements, m_threat_level = get_monster_stats(monster_name, df_m)
    recom_list = []
    
    for _, w in df_w.iterrows():
        att = w['Attack Max']
        crit = w['Critical']
        elemen = w['Elemen']
        nilai_el = w['Nilai Elemen']
        
        # Hitung Weapon Power Level
        w_power_level = min((att / 120.0) * 10, 10.0)
        power_diff = w_power_level - m_threat_level
        
        # 1. Damage Fisik (Attack + Ekspektasi Bonus Critical)
        base_score = att + (att * (crit / 100.0) * 0.5) 
        
        # 2. Kalkulasi Keuntungan/Kerugian Elemen
        el_score = 0
        if elemen != 'Raw' and pd.notna(elemen):
            mon_res = res_dict.get(elemen, 3) 
            
            if elemen in weak_elements:
                el_score += 50 + (nilai_el * 3)
            elif elemen in strong_elements:
                el_score -= 50
            else:
                el_score += (3 - mon_res) * 5

        # 3. Utilitas Efek Status
        status_score = 0
        if pd.notna(w['Bonus Status Effect']) and str(w['Bonus Status Effect']).lower() not in ['none', 'nan', '']:
            status_score = 15 
            
        # 4. PENILAIAN LEVEL MATCHING (Mencegah bawa piso dapur untuk lawan naga)
        match_score = 0
        if power_diff < -4:
            # Senjata TERLALU LEMAH (Bunuh Diri) -> Diberi penalti besar agar tidak direkomendasikan
            match_score -= 100
            kat = "⚠️ Bunuh Diri (Undergeared)"
        elif power_diff > 4:
            # Senjata TERLALU KUAT (Overkill/Quick Finish) -> Penalti sedang, kecuali gak ada senjata lain
            match_score -= 50
            kat = "⚡ Overkill"
        elif power_diff < -1.5:
            kat = "🔥 Menantang"
        elif power_diff > 1.5:
            kat = "🍃 Mudah"
        else:
            match_score += 20 # Bonus jika pertarungannya sepadan
            kat = "⚖️ Sepadan (Balanced)"
            
        final_score = base_score + el_score + status_score + match_score
        
        # Hanya ambil jika skor tidak hancur lebur (mencegah rekomendasi bunuh diri)
        if final_score > 0:
            recom_list.append({
                'Weapon': w, 
                'Score': final_score,
                'Power': w_power_level,
                'Kategori': kat
            })
        
    sorted_recom = sorted(recom_list, key=lambda x: x['Score'], reverse=True)
    return sorted_recom[:6]

# --- LOGIKA 2: REKOMENDASI MONSTER UNTUK SENJATA (ANTI-OVERKILL) ---
def recommend_monsters_for_weapon(weapon_name, df_w, df_m):
    w_stats = df_w[df_w['Nama Senjata'] == weapon_name].iloc[0]
    elemen = w_stats['Elemen']
    att_max = w_stats['Attack Max']
    
    # 1. Menentukan Weapon Tier / Power Level (Asumsi max attack di game ~120)
    w_power_level = min((att_max / 120.0) * 10, 10.0)
    
    recom_list = []
    
    for _, m in df_m.iterrows():
        # 2. Menentukan Monster Threat Level (Asumsi max HP 5 + max Def 5 = 10)
        m_threat_level = m['HP'] + m['Defence']
        
        # 3. Menghitung Selisih Kekuatan (Power Gap)
        power_diff = w_power_level - m_threat_level
        
        # 4. Kalkulasi Elemental Advantage
        el_advantage = 0
        if elemen != 'Raw' and pd.notna(elemen):
            res_val = m.get(f'Res_{elemen}', 3)
            el_advantage = (5 - res_val) * 25 
            
        # 5. Penilaian Kecocokan (Level Matching)
        match_score = 50 - (abs(power_diff) * 8)
        
        # 6. PENALTI OVERKILL / QUICK FINISH
        if power_diff > 4: 
            match_score -= 100 
            kategori_match = "⚡ Overkill (Quick Finish)"
        elif power_diff < -4:
            match_score -= 50
            kategori_match = "⚠️ Sangat Sulit (Undergeared)"
        elif power_diff > 1.5:
            kategori_match = "🍃 Mudah"
        elif power_diff < -1.5:
            kategori_match = "🔥 Menantang"
        else:
            kategori_match = "⚖️ Sempurna (Balanced)"
            
        # 7. Total Skor
        if elemen == 'Raw':
            score = match_score + ((5 - m['Defence']) * 10)
        else:
            score = el_advantage + match_score
            
        # Filter skor: Hindari memasukkan monster overkill ke rekomendasi teratas
        if score > 0:
            recom_list.append({
                'Monster': m, 
                'Score': score, 
                'Threat': m_threat_level,
                'Kategori': kategori_match,
                'PowerDiff': power_diff
            })
        
    sorted_recom = sorted(recom_list, key=lambda x: x['Score'], reverse=True)
    return sorted_recom[:6], w_stats, w_power_level


# --- UI APLIKASI STREAMLIT ---
st.markdown("<h1 style='text-align: center;'>⚔️ Armory & Weapon Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Temukan senjata paling mematikan untuk membunuh target, atau cari target paling worthy untuk diuji dengan senjata Anda.</p>", unsafe_allow_html=True)
st.divider()

# Menggunakan Tabs untuk navigasi mode
tab1, tab2 = st.tabs(["🗡️ Cari Senjata Lawan Monster", "🎯 Cari Target Untuk Senjata"])

# --- TAB 1: SENJATA UNTUK MONSTER ---
with tab1:
    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        monster_list = sorted(df_monster['Monster'].tolist())
        selected_monster = st.selectbox("Pilih Monster Lawan:", options=monster_list, key="sel_mon")
        btn_find_w = st.button("Analisis & Cari Senjata", type="primary", use_container_width=True)
        
    with col_info:
        if selected_monster:
            _, _, weak_els, strong_els, threat_lvl = get_monster_stats(selected_monster, df_monster)
            st.info(f"Kelemahan Terbesar **{selected_monster}**: {', '.join([f'{elemen_emojis.get(e, '')} {e}' for e in weak_els])}")
            st.warning(f"Sangat Kebal Terhadap: {', '.join([f'{elemen_emojis.get(e, '')} {e}' for e in strong_els])}")
            st.error(f"💀 **Threat Level Monster: {threat_lvl}/10**")

    if btn_find_w:
        with st.spinner('Memindai persenjataan yang sesuai dengan ancaman...'):
            recommendations = recommend_weapons(selected_monster, df_weapon, df_monster)
            
            if not recommendations:
                st.warning("Tidak ada senjata di *database* yang direkomendasikan untuk melawan monster ini (Level ancaman terlalu tinggi/rendah).")
            else:
                st.markdown(f"### 🏆 Top 6 Senjata Direkomendasikan Melawan {selected_monster}")
                st.caption("Sistem memfilter senjata berdasarkan kecocokan Elemen dan memastikan Senjata memiliki kekuatan (*Power Level*) yang cukup untuk melawan ancaman monster.")
                
                # Tampilan Card Grid (2 Kolom)
                cols = st.columns(2)
                for i, item in enumerate(recommendations):
                    w = item['Weapon']
                    kat = item['Kategori']
                    pow_lvl = item['Power']
                    
                    tipe_icon = tipe_senjata_emojis.get(w['Tipe Senjata'], w['Tipe Senjata'])
                    el_icon = elemen_emojis.get(w['Elemen'], '')
                    
                    with cols[i % 2]:
                        with st.container(border=True):
                            st.markdown(f"#### #{i+1} {w['Nama Senjata']}")
                            st.caption(f"{tipe_icon} | Power: {pow_lvl:.1f}/10")
                            
                            # Pewarnaan Kategori Kesesuaian
                            if "Sepadan" in kat or "Sempurna" in kat:
                                st.success(f"Kesesuaian: **{kat}**")
                            elif "Mudah" in kat or "Menantang" in kat:
                                st.info(f"Kesesuaian: **{kat}**")
                            else:
                                st.warning(f"Kesesuaian: **{kat}**")
                            
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Attack Max", w['Attack Max'])
                            m2.metric("Elemen", f"{el_icon} {w['Elemen']}", delta=w['Nilai Elemen'] if w['Elemen']!='Raw' else None)
                            m3.metric("Critical", f"{w['Critical']}%")
                            
                            if pd.notna(w['Bonus Status Effect']) and str(w['Bonus Status Effect']).lower() not in ['none', 'nan', '']:
                                st.write(f"🧪 **Status Effect:** {w['Bonus Status Effect']} ({w.get('Nilai Status', '')})")
                            if pd.notna(w['Skill']):
                                st.write(f"✨ **Skill:** {w['Skill']}")


# --- TAB 2: MONSTER UNTUK SENJATA ---
with tab2:
    w_col_sel, w_col_info = st.columns([1, 2])
    with w_col_sel:
        weapon_list = sorted(df_weapon['Nama Senjata'].tolist())
        selected_weapon = st.selectbox("Pilih Senjata di Inventory Anda:", options=weapon_list, key="sel_weap")
        btn_find_m = st.button("Cari Target Terbaik", type="primary", use_container_width=True)
        
    with w_col_info:
        if selected_weapon:
            w_info = df_weapon[df_weapon['Nama Senjata'] == selected_weapon].iloc[0]
            el_str = f"{elemen_emojis.get(w_info['Elemen'], '')} {w_info['Elemen']}"
            w_power = min((w_info['Attack Max'] / 120.0) * 10, 10.0)
            
            st.success(f"**{w_info['Nama Senjata']}** ({w_info['Tipe Senjata']}) - Elemen: **{el_str}**")
            st.info(f"⚔️ **Weapon Power Tier: {w_power:.1f} / 10.0** (Berdasarkan Attack Max {w_info['Attack Max']})")

    if btn_find_m:
        with st.spinner('Menganalisis kecocokan Threat Level...'):
            recommendations, w_stats, w_power_level = recommend_monsters_for_weapon(selected_weapon, df_weapon, df_monster)
            elemen_weap = w_stats['Elemen']
            
            if not recommendations:
                st.warning("Tidak ada target monster yang direkomendasikan untuk senjata ini di database.")
            else:
                st.markdown(f"### 🎯 Top 6 Target Paling Layak (Worthy) untuk {selected_weapon}")
                st.caption("Sistem kini menghindari target 'Overkill' yang bisa diselesaikan dengan *Quick Finish*, dan mencari target *High-Value* dengan kelemahan elemen yang tepat.")
                
                # Tampilan Card Grid (2 Kolom)
                cols2 = st.columns(2)
                for i, item in enumerate(recommendations):
                    m = item['Monster']
                    kat = item['Kategori']
                    threat = item['Threat']
                    
                    with cols2[i % 2]:
                        with st.container(border=True):
                            st.markdown(f"#### #{i+1} {m['Monster']}")
                            
                            # Labeling Kategori Kesulitan
                            if "Sempurna" in kat:
                                st.success(f"Tingkat Kesulitan: **{kat}**")
                            elif "Mudah" in kat:
                                st.info(f"Tingkat Kesulitan: **{kat}**")
                            elif "Menantang" in kat:
                                st.warning(f"Tingkat Kesulitan: **{kat}**")
                            else:
                                st.error(f"Tingkat Kesulitan: **{kat}**")
                                
                            m1, m2 = st.columns(2)
                            m1.metric("Threat Level", f"{threat}/10", help="Gabungan Base HP + Defence Monster")
                            
                            if elemen_weap != 'Raw':
                                res_val = m.get(f'Res_{elemen_weap}', 3)
                                if res_val == 1: desc = "Sangat Rentan"
                                elif res_val == 2: desc = "Rentan"
                                else: desc = "Biasa"
                                
                                m2.metric(f"Res. {elemen_weap}", res_val, delta=desc, delta_color="inverse")
                            else:
                                m2.metric("Defence Fisik", m['Defence'])
