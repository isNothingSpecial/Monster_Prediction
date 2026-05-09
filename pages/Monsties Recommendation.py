import streamlit as st
import pandas as pd
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="MHST Recommender", layout="wide")

# --- KAMUS EMOJI & TENDENCY ---
tendency_map = {1: 'Speed', 2: 'Power', 3: 'Technique'}
tendency_rev_map = {'Speed': 1, 'Power': 2, 'Technique': 3}

element_emojis = {
    'Fire': '🔥', 'Water': '💧', 'Thunder': '⚡', 'Ice': '❄️', 'Dragon': '🐉'
}
tendency_emojis = {
    'Speed': '🏃 (Speed)', 'Power': '🥊 (Power)', 'Technique': '🧠 (Technique)'
}

# --- SIDEBAR: PILIHAN SERIES GAME ---
st.sidebar.title("🐉 Pilihan Series")
series_choice = st.sidebar.selectbox(
    "Pilih Series Game:",
    ["Monster Hunter Stories 1", "Monster Hunter Stories 2", "Monster Hunter Stories 3"]
)

# Mapping nama series ke nama file CSV
file_map = {
    "Monster Hunter Stories 1": "MHST_monsties.csv",
    "Monster Hunter Stories 2": "MHST2_monsties.csv", # Sesuaikan jika nama file berbeda
    "Monster Hunter Stories 3": "MHST3_monsties.csv"  # Sesuaikan jika nama file berbeda
}

file_name = file_map[series_choice]

# --- LOAD DATA ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # Menghapus kolom 'No' jika ada
        if 'No' in df.columns:
            df = df.drop(columns=['No'])
        return df
    except FileNotFoundError:
        return None

df1 = load_data(file_name)

# --- FUNGSI ANALISIS LAWAN & REKOMENDASI ---
def analyze_opponent(monster_name, df):
    stats = df[df['Monster'] == monster_name].iloc[0]

    # 1. Cari Kelemahan Terbesar (Resistensi Terendah)
    res_cols = {'Fire': stats['Res_Fire'], 'Water': stats['Res_Water'], 
                'Thunder': stats['Res_Thunder'], 'Ice': stats['Res_Ice'], 'Dragon': stats['Res_Dragon']}
    min_res = min(res_cols.values())
    weak_elements = [el for el, val in res_cols.items() if val == min_res]

    # 2. Cari Serangan Terkuat Lawan (Untuk keperluan pertahanan Monstie kita)
    att_cols = {'Fire': stats['Att_Fire'], 'Water': stats['Att_Water'], 
                'Thunder': stats['Att_Thunder'], 'Ice': stats['Att_Ice'], 'Dragon': stats['Att_Dragon']}
    max_att = max(att_cols.values())
    strong_elements = [el for el, val in att_cols.items() if val == max_att]

    # 3. Tentukan Counter Tendency
    opp_tendency = tendency_map.get(stats['Tendency'], 'Unknown')
    if opp_tendency == 'Speed':
        counter_tendency = 'Technique'
    elif opp_tendency == 'Technique':
        counter_tendency = 'Power'
    else:
        counter_tendency = 'Speed'
        
    return stats, weak_elements, strong_elements, opp_tendency, counter_tendency

def recommend_monsties_v2(monster_name, df):
    stats, weak_elements, strong_elements, opp_tendency, counter_tendency = analyze_opponent(monster_name, df)
    
    # Filter Monstie berdasarkan Counter Tendency yang tepat
    candidates = df[df['Tendency'] == tendency_rev_map[counter_tendency]].copy()
    
    # Jangan rekomendasikan monster yang sama dengan lawan
    candidates = candidates[candidates['Monster'] != monster_name]
    
    opp_strongest_element = strong_elements[0] # Ambil salah satu serangan terkuat lawan
    
    recom_list = []
    
    for weak_el in weak_elements:
        att_col = f'Att_{weak_el}'
        res_col = f'Res_{opp_strongest_element}'
        
        if att_col in candidates.columns and res_col in candidates.columns:
            # Skor kombinasi (Serangan tinggi kelemahan lawan + Pertahanan tinggi dari serangan lawan)
            candidates['Score'] = (candidates[att_col] * 2) + candidates[res_col]
            
            top_candidates = candidates.sort_values(by=['Score', att_col], ascending=[False, False]).head(3)
            
            for _, row in top_candidates.iterrows():
                recom_list.append({
                    'Monster': row['Monster'],
                    'Attack Element': weak_el,
                    'Attack Value': row[att_col],
                    'Defense Element': opp_strongest_element,
                    'Defense Value': row[res_col],
                    'Tendency': counter_tendency,
                    'Score': row['Score']
                })
                
    unique_recoms = pd.DataFrame(recom_list).drop_duplicates(subset=['Monster'])
    if unique_recoms.empty:
        return None
        
    return unique_recoms.sort_values(by='Score', ascending=False).to_dict('records')


# --- UI APLIKASI STREAMLIT ---
st.markdown(f"<h1 style='text-align: center;'>⚔️ {series_choice}: Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Sistem cerdas untuk menemukan Monstie pendamping terbaik berdasarkan analisa ofensif dan defensif.</p>", unsafe_allow_html=True)
st.divider()

# Pengecekan apakah data berhasil di-load
if df1 is None:
    st.error(f"Dataset untuk {series_choice} ({file_name}) belum tersedia di direktori.")
    st.info("Fitur untuk seri ini sedang dalam tahap pengembangan. Silakan pilih 'Monster Hunter Stories 1' di menu samping untuk mencoba.")
    st.stop() # Menghentikan eksekusi kode di bawahnya agar tidak error

# Layout Pemilihan Lawan
col_select, col_opp_info = st.columns([1, 2])

with col_select:
    st.subheader("🎯 Target Lawan")
    monster_list = sorted(df1['Monster'].tolist())
    selected_monster = st.selectbox("Pilih monster yang ingin Anda lawan:", options=monster_list)
    btn_analyze = st.button("Analisis & Cari Counter", use_container_width=True, type="primary")

with col_opp_info:
    if selected_monster:
        stats, weak_els, strong_els, opp_tendency, _ = analyze_opponent(selected_monster, df1)
        st.subheader("📊 Profil Target")
        
        o_col1, o_col2, o_col3 = st.columns(3)
        with o_col1:
            st.info(f"**Tendency:**\n{tendency_emojis.get(opp_tendency, opp_tendency)}")
        with o_col2:
            st.error(f"**Serangan Terkuat:**\n{element_emojis.get(strong_els[0], '')} {strong_els[0]}")
        with o_col3:
            st.success(f"**Kelemahan Terbesar:**\n{', '.join([f'{element_emojis.get(e, '')} {e}' for e in weak_els])}")

st.divider()

# Eksekusi Rekomendasi
if btn_analyze:
    with st.spinner('Mencari Monstie terbaik dari database...'):
        recommendations = recommend_monsties_v2(selected_monster, df1)
        
        if not recommendations:
            st.warning("Tidak ada Monstie yang cocok ditemukan untuk kriteria ini.")
        else:
            _, opp_weak, opp_strong, opp_tend, target_tendency = analyze_opponent(selected_monster, df1)
            
            st.markdown(f"### 🏆 Top Rekomendasi untuk Melawan {selected_monster}")
            st.caption(f"Sistem memfilter Monstie dengan Tendency **{target_tendency}**, memiliki elemen serangan **{', '.join(opp_weak)}**, dan mampu menahan serangan **{opp_strong[0]}** dari lawan.")
            
            # Menampilkan hasil dalam bentuk "Cards" menggunakan kolom
            cols = st.columns(len(recommendations))
            
            for i, recom in enumerate(recommendations):
                with cols[i]:
                    st.markdown(f"<h3 style='text-align:center;'>#{i+1} {recom['Monster']}</h3>", unsafe_allow_html=True)
                    
                    # Cek dan Tampilkan Gambar
                    image_path = f"Monslist/{recom['Monster']}.webp"
                    if os.path.exists(image_path):
                        st.image(image_path, use_container_width=True)
                    else:
                        st.info("🖼️ Gambar tidak tersedia", icon="ℹ️")
                    
                    # Kotak Informasi Metrik
                    st.write(f"**Tipe:** {tendency_emojis.get(recom['Tendency'], recom['Tendency'])}")
                    
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric(
                            label=f"Serangan {recom['Attack Element']}", 
                            value=recom['Attack Value'],
                            delta="Penetrasi", delta_color="normal"
                        )
                    with m2:
                        st.metric(
                            label=f"Pertahanan {recom['Defense Element']}", 
                            value=recom['Defense Value'],
                            delta="Daya Tahan", delta_color="normal"
                        )
                    
                    st.markdown("---")
