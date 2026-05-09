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
        df_w['Critical'] = df_w['Critical'].astype(str).str.replace('%', '').replace('nan', '0').astype(float)
        
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
    return stats, res, weak_elements, strong_elements

# --- LOGIKA 1: REKOMENDASI SENJATA (BARU) ---
def recommend_weapons(monster_name, df_w, df_m):
    stats, res_dict, weak_elements, strong_elements = get_monster_stats(monster_name, df_m)
    recom_list = []
    
    for _, w in df_w.iterrows():
        att = w['Attack Max']
        crit = w['Critical']
        elemen = w['Elemen']
        nilai_el = w['Nilai Elemen']
        
        # 1. Damage Fisik (Attack + Ekspektasi Bonus Critical)
        base_score = att + (att * (crit / 100.0) * 0.5) 
        
        # 2. Kalkulasi Keuntungan/Kerugian Elemen
        el_score = 0
        if elemen != 'Raw' and pd.notna(elemen):
            mon_res = res_dict.get(elemen, 3) 
            
            # Jika elemen senjata cocok dengan kelemahan target = Bonus Besar
            if elemen in weak_elements:
                el_score += 50 + (nilai_el * 3)
            # Jika elemen senjata menabrak pertahanan terkuat target = Penalti / Resisted
            elif elemen in strong_elements:
                el_score -= 50
            else:
                # Elemen Netral: Dihitung berdasar nilai resistansi
                el_score += (3 - mon_res) * 5

        # 3. Utilitas Efek Status
        status_score = 0
        if pd.notna(w['Bonus Status Effect']) and str(w['Bonus Status Effect']).lower() not in ['none', 'nan', '']:
            status_score = 15 # Senjata status (Poison, Para, dll) selalu punya nilai taktis
            
        final_score = base_score + el_score + status_score
        
        recom_list.append({'Weapon': w, 'Score': final_score})
        
    sorted_recom = sorted(recom_list, key=lambda x: x['Score'], reverse=True)
    return sorted_recom[:6] # Ambil Top 6 agar tampilannya pas di grid

# --- LOGIKA 2: REKOMENDASI MONSTER UNTUK SENJATA (BARU) ---
def recommend_monsters_for_weapon(weapon_name, df_w, df_m):
    w_stats = df_w[df_w['Nama Senjata'] == weapon_name].iloc[0]
    elemen = w_stats['Elemen']
    
    recom_list = []
    
    for _, m in df_m.iterrows():
        score = 0
        def_penalty = m['Defence'] * 5 # Semakin tebal defence, semakin alot dilawan
        
        # Jika senjata punya elemen, incar monster yang tidak punya resistansi elemen itu
        if elemen != 'Raw' and pd.notna(elemen):
            res_val = m.get(f'Res_{elemen}', 3)
            # res_val 1 (sangat lemah) -> skor tinggi, res_val 5 (kebal) -> skor hancur
            el_advantage = (5 - res_val) * 30
            score = el_advantage - def_penalty
        else:
            # Jika senjatanya RAW, sistem cuma mencari target ber-defence ampas
            score = 100 - def_penalty
            
        recom_list.append({'Monster': m, 'Score': score})
        
    sorted_recom = sorted(recom_list, key=lambda x: x['Score'], reverse=True)
    return sorted_recom[:6], w_stats


# --- UI APLIKASI STREAMLIT ---
st.markdown("<h1 style='text-align: center;'>⚔️ Armory & Weapon Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Temukan senjata paling mematikan untuk membunuh target, atau cari target paling empuk untuk senjata Anda.</p>", unsafe_allow_html=True)
st.divider()

# Menggunakan Tabs untuk navigasi mode
tab1, tab2 = st.tabs(["🗡️ Cari Senjata Lawan Monster", "🎯 Cari Target Untuk Senjata"])

# --- TAB 1: SENJATA UNTUK MONSTER ---
with tab1:
    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        monster_list = sorted(df_monster['Monster'].tolist())
        selected_monster = st.selectbox("Pilih Monster Lawan:", options=monster_list, key="sel_mon")
        btn_find_w = st.button("Analisis Kelemahan", type="primary", use_container_width=True)
        
    with col_info:
        if selected_monster:
            _, _, weak_els, strong_els = get_monster_stats(selected_monster, df_monster)
            st.info(f"Kelemahan Terbesar **{selected_monster}**: {', '.join([f'{elemen_emojis.get(e, '')} {e}' for e in weak_els])}")
            st.warning(f"Sangat Kebal Terhadap: {', '.join([f'{elemen_emojis.get(e, '')} {e}' for e in strong_els])}")

    if btn_find_w:
        with st.spinner('Mencari persenjataan...'):
            recommendations = recommend_weapons(selected_monster, df_weapon, df_monster)
            st.markdown(f"### 🏆 Top 6 Senjata Terbaik Melawan {selected_monster}")
            
            # Tampilan Card Grid (2 Kolom)
            cols = st.columns(2)
            for i, item in enumerate(recommendations):
                w = item['Weapon']
                tipe_icon = tipe_senjata_emojis.get(w['Tipe Senjata'], w['Tipe Senjata'])
                el_icon = elemen_emojis.get(w['Elemen'], '')
                
                with cols[i % 2]: # Membagi ke kiri dan kanan bergantian
                    with st.container(border=True):
                        st.markdown(f"#### #{i+1} {w['Nama Senjata']}")
                        st.caption(f"{tipe_icon}")
                        
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
        btn_find_m = st.button("Cari Target Empuk", type="primary", use_container_width=True)
        
    with w_col_info:
        if selected_weapon:
            w_info = df_weapon[df_weapon['Nama Senjata'] == selected_weapon].iloc[0]
            el_str = f"{elemen_emojis.get(w_info['Elemen'], '')} {w_info['Elemen']}"
            st.success(f"**{w_info['Nama Senjata']}** adalah senjata bertipe **{w_info['Tipe Senjata']}** dengan daya hancur ber-elemen **{el_str}**.")

    if btn_find_m:
        with st.spinner('Memindai habitat monster...'):
            recommendations, w_stats = recommend_monsters_for_weapon(selected_weapon, df_weapon, df_monster)
            elemen_weap = w_stats['Elemen']
            
            st.markdown(f"### 🎯 Top 6 Monster Rentan Terhadap {selected_weapon}")
            if elemen_weap == 'Raw':
                st.caption("Karena senjata ini tipe Raw (Fisik murni), sistem merekomendasikan target dengan stat *Defence* keseluruhan paling lemah.")
            else:
                st.caption(f"Sistem mengincar target yang memiliki pertahanan sangat buruk terhadap elemen **{elemen_weap}**.")
            
            # Tampilan Card Grid (2 Kolom)
            cols2 = st.columns(2)
            for i, item in enumerate(recommendations):
                m = item['Monster']
                
                with cols2[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"#### #{i+1} {m['Monster']}")
                        
                        m1, m2 = st.columns(2)
                        m1.metric("Defence", m['Defence'], delta="-Rendah", delta_color="inverse")
                        
                        if elemen_weap != 'Raw':
                            res_val = m.get(f'Res_{elemen_weap}', 3)
                            # Render teks berdasarkan seberapa lemah
                            if res_val == 1:
                                desc = "Sangat Rentan"
                            elif res_val == 2:
                                desc = "Rentan"
                            else:
                                desc = "Normal"
                                
                            m2.metric(f"Resistansi {elemen_weap}", res_val, delta=desc, delta_color="inverse")
