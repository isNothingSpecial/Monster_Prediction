import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="MHST Recommendation System", layout="wide")

# --- KAMUS EMOJI & TENDENCY ---
tendency_map = {1: 'Speed', 2: 'Power', 3: 'Technique'}
tendency_rev_map = {'Speed': 1, 'Power': 2, 'Technique': 3}

element_emojis = {
    'Fire': '🔥', 'Water': '💧', 'Thunder': '⚡', 'Ice': '❄️', 'Dragon': '🐉'
}
tendency_emojis = {
    'Speed': '🏃 (Speed)', 'Power': '🥊 (Power)', 'Technique': '🧠 (Technique)'
}

# Kategori Stat untuk iterasi grafik
stats_basic = ['HP', 'Attack', 'Defence', 'Speed']
stats_attack = ['Att_Fire', 'Att_Water', 'Att_Thunder', 'Att_Ice', 'Att_Dragon']
stats_resist = ['Res_Fire', 'Res_Water', 'Res_Thunder', 'Res_Ice', 'Res_Dragon']

# --- SIDEBAR: PILIHAN SERIES GAME ---
st.sidebar.title("🐉 Pilihan Series")
series_choice = st.sidebar.selectbox(
    "Pilih Series Game:",
    ["Monster Hunter Stories 1", "Monster Hunter Stories 2", "Monster Hunter Stories 3"]
)

file_map = {
    "Monster Hunter Stories 1": "MHST_monsties.csv",
    "Monster Hunter Stories 2": "MHST2_monsties.csv", 
    "Monster Hunter Stories 3": "MHST3_monsties.csv"  
}
file_name = file_map[series_choice]

# --- LOAD DATA ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'No' in df.columns:
            df = df.drop(columns=['No'])
        return df
    except FileNotFoundError:
        return None

df1 = load_data(file_name)

# --- FUNGSI RADAR CHART DINAMIS ---
def create_h2h_radar_dynamic(target_name, target_stats, recom_name, recom_stats, categories, title):
    # Membersihkan label kategori agar tampil rapi di chart (Menghilangkan Att_ dan Res_)
    display_cats = [c.replace('Att_', '').replace('Res_', '') for c in categories]
    cats_closed = display_cats + [display_cats[0]]
    
    val_target = [target_stats.get(c, 0) for c in categories]
    val_target_closed = val_target + [val_target[0]]
    
    val_recom = [recom_stats.get(c, 0) for c in categories]
    val_recom_closed = val_recom + [val_recom[0]]
    
    fig = go.Figure()
    
    # Trace 1: Target Lawan (Merah)
    fig.add_trace(go.Scatterpolar(
        r=val_target_closed, theta=cats_closed, fill='toself',
        name=f"{target_name}", line_color='#ff4b4b', opacity=0.6
    ))
    
    # Trace 2: Monstie Kita/Rekomendasi (Biru/Cyan)
    fig.add_trace(go.Scatterpolar(
        r=val_recom_closed, theta=cats_closed, fill='toself',
        name=f"{recom_name}", line_color='#00d4ff', opacity=0.8
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=14)),
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False, 
        margin=dict(l=20, r=20, t=40, b=20),
        height=280
    )
    return fig

# --- FUNGSI ANALISIS LAWAN & REKOMENDASI ---
def analyze_opponent(monster_name, df):
    stats = df[df['Monster'] == monster_name].iloc[0]

    res_cols = {k.replace('Res_', ''): stats[k] for k in stats_resist}
    min_res = min(res_cols.values())
    weak_elements = [el for el, val in res_cols.items() if val == min_res]

    att_cols = {k.replace('Att_', ''): stats[k] for k in stats_attack}
    max_att = max(att_cols.values())
    strong_elements = [el for el, val in att_cols.items() if val == max_att]

    opp_tendency = tendency_map.get(stats['Tendency'], 'Unknown')
    if opp_tendency == 'Speed': counter_tendency = 'Technique'
    elif opp_tendency == 'Technique': counter_tendency = 'Power'
    else: counter_tendency = 'Speed'
        
    return stats, weak_elements, strong_elements, opp_tendency, counter_tendency

def recommend_monsties_v2(monster_name, df):
    stats, weak_elements, strong_elements, opp_tendency, counter_tendency = analyze_opponent(monster_name, df)
    
    candidates = df[df['Tendency'] == tendency_rev_map[counter_tendency]].copy()
    candidates = candidates[candidates['Monster'] != monster_name]
    opp_strongest_element = strong_elements[0] 
    recom_list = []
    
    for weak_el in weak_elements:
        att_col = f'Att_{weak_el}'
        res_col = f'Res_{opp_strongest_element}'
        
        if att_col in candidates.columns and res_col in candidates.columns:
            rarity_bonus = candidates.get('Rarity', 1) * 2 
            candidates['Score'] = (candidates[att_col] * 2) + candidates[res_col] + rarity_bonus
            top_candidates = candidates.sort_values(by=['Score', att_col], ascending=[False, False]).head(3)
            
            for _, row in top_candidates.iterrows():
                recom_list.append({
                    'Monster': row['Monster'],
                    'Attack Element': weak_el,
                    'Attack Value': row[att_col],
                    'Defense Element': opp_strongest_element,
                    'Defense Value': row[res_col],
                    'Tendency': counter_tendency,
                    'Score': row['Score'],
                    'Stats': row 
                })
                
    unique_recoms = pd.DataFrame(recom_list).drop_duplicates(subset=['Monster'])
    if unique_recoms.empty: return None
    
    # PERUBAHAN DISINI: Hanya kembalikan 3 teratas agar UI rapi
    return unique_recoms.sort_values(by='Score', ascending=False).head(3).to_dict('records')


# --- UI APLIKASI STREAMLIT ---
st.markdown(f"<h1 style='text-align: center;'>⚔️ {series_choice}: Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Temukan partner tempur terbaik atau lakukan simulasi komparasi stat di Battle Lab.</p>", unsafe_allow_html=True)
st.divider()

if df1 is None:
    st.error(f"Dataset untuk {series_choice} ({file_name}) belum tersedia di direktori.")
    st.info("Fitur untuk seri ini sedang dalam tahap pengembangan. Silakan pilih 'Monster Hunter Stories 1' di menu samping untuk mencoba.")
    st.stop() 

monster_list_all = sorted(df1['Monster'].tolist())

# --- DUA TAB UTAMA ---
tab1, tab2 = st.tabs(["🏆 Auto-Recommender", "🔬 Battle Lab (Head-to-Head)"])

# ==========================================
# TAB 1: AUTO RECOMMENDER
# ==========================================
with tab1:
    col_select, col_opp_info = st.columns([1, 2])

    with col_select:
        st.subheader("🎯 Target Lawan")
        selected_monster = st.selectbox("Pilih monster yang ingin Anda lawan:", options=monster_list_all)
        btn_analyze = st.button("Analisis & Cari Counter", use_container_width=True, type="primary")

    with col_opp_info:
        if selected_monster:
            stats, weak_els, strong_els, opp_tendency, _ = analyze_opponent(selected_monster, df1)
            st.subheader("📊 Profil Target")
            
            o_col1, o_col2, o_col3 = st.columns(3)
            with o_col1: st.info(f"**Tendency:**\n{tendency_emojis.get(opp_tendency, opp_tendency)}")
            with o_col2: st.error(f"**Serangan Terkuat:**\n{element_emojis.get(strong_els[0], '')} {strong_els[0]}")
            with o_col3: st.success(f"**Kelemahan Terbesar:**\n{', '.join([f'{element_emojis.get(e, '')} {e}' for e in weak_els])}")

    st.divider()

    if btn_analyze:
        with st.spinner('Mencari Monstie terbaik dari database...'):
            recommendations = recommend_monsties_v2(selected_monster, df1)
            
            if not recommendations:
                st.warning("Tidak ada Monstie yang cocok ditemukan untuk kriteria ini.")
            else:
                opp_stats, opp_weak, opp_strong, opp_tend, target_tendency = analyze_opponent(selected_monster, df1)
                
                st.markdown(f"### 🏆 Top 3 Rekomendasi untuk Melawan {selected_monster}")
                
                # PERUBAHAN DISINI: Mengunci jumlah kolom menjadi 3 agar lebar UI konsisten dan tidak tumpang tindih
                cols = st.columns(3)
                
                for i, recom in enumerate(recommendations):
                    with cols[i]:
                        with st.container(border=True):
                            st.markdown(f"<h3 style='text-align:center;'>#{i+1} {recom['Monster']}</h3>", unsafe_allow_html=True)
                            
                            image_path = f"Monslist/{recom['Monster']}.webp"
                            if os.path.exists(image_path):
                                st.image(image_path, use_container_width=True)
                            else:
                                st.info("🖼️ Gambar tidak tersedia", icon="ℹ️")
                            
                            st.write(f"**Tipe:** {tendency_emojis.get(recom['Tendency'], recom['Tendency'])}")
                            
                            m1, m2 = st.columns(2)
                            with m1: st.metric(label=f"Atk {recom['Attack Element']}", value=recom['Attack Value'])
                            with m2: st.metric(label=f"Def {recom['Defense Element']}", value=recom['Defense Value'])
                                
                            with st.expander("📊 Lihat Head-to-Head (Dasar)"):
                                fig_mini = create_h2h_radar_dynamic(
                                    selected_monster, opp_stats, 
                                    recom['Monster'], recom['Stats'], 
                                    stats_basic, "Stat Dasar"
                                )
                                st.plotly_chart(fig_mini, use_container_width=True)

# ==========================================
# TAB 2: BATTLE LAB (SIMULASI MANUAL)
# ==========================================
with tab2:
    st.subheader("🔬 Simulasi Head-to-Head Bebas")
    st.caption("Pilih dua monster apa saja untuk membandingkan statistik lengkap mereka.")
    
    col_m1, col_vs, col_m2 = st.columns([2, 1, 2])
    
    with col_m1:
        m1_select = st.selectbox("Lawan 1 (Merah):", options=monster_list_all, index=0, key="lab_m1")
        m1_stats = df1[df1['Monster'] == m1_select].iloc[0]
        
    with col_vs:
        st.markdown("<h1 style='text-align:center; padding-top:25px;'>VS</h1>", unsafe_allow_html=True)
        
    with col_m2:
        m2_select = st.selectbox("Lawan 2 (Biru):", options=monster_list_all, index=1 if len(monster_list_all)>1 else 0, key="lab_m2")
        m2_stats = df1[df1['Monster'] == m2_select].iloc[0]
        
    st.divider()
    
    # Legend Manual untuk menjelaskan warna
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><h5><span style='color: #ff4b4b;'>🔴 {m1_select}</span> &nbsp; VS &nbsp; <span style='color: #00d4ff;'>🔵 {m2_select}</span></h5></div>", unsafe_allow_html=True)

    # --- TAMPILAN 3 GRID RADAR CHART ---
    c_rad1, c_rad2, c_rad3 = st.columns(3)
    
    with c_rad1:
        fig_basic = create_h2h_radar_dynamic(m1_select, m1_stats, m2_select, m2_stats, stats_basic, "Stat Dasar")
        st.plotly_chart(fig_basic, use_container_width=True)
        
    with c_rad2:
        fig_att = create_h2h_radar_dynamic(m1_select, m1_stats, m2_select, m2_stats, stats_attack, "Attack Element")
        st.plotly_chart(fig_att, use_container_width=True)
        
    with c_rad3:
        fig_def = create_h2h_radar_dynamic(m1_select, m1_stats, m2_select, m2_stats, stats_resist, "Resistance Element")
        st.plotly_chart(fig_def, use_container_width=True)
    
    # --- TABEL DETAIL DALAM EXPANDER ---
    with st.expander("📄 Lihat Angka Detail Komparasi"):
        all_stats = ['Tendency'] + stats_basic + stats_attack + stats_resist
        
        m1_data = [tendency_map.get(m1_stats.get('Tendency', 0), '-')] + [m1_stats.get(s, 0) for s in stats_basic + stats_attack + stats_resist]
        m2_data = [tendency_map.get(m2_stats.get('Tendency', 0), '-')] + [m2_stats.get(s, 0) for s in stats_basic + stats_attack + stats_resist]
        
        clean_stats_names = ['Tendency'] + stats_basic + [s.replace('Att_', 'Attack ') for s in stats_attack] + [s.replace('Res_', 'Resistance ') for s in stats_resist]
        
        comp_data = {
            'Statistik': clean_stats_names,
            m1_select: m1_data,
            m2_select: m2_data
        }
        df_comp = pd.DataFrame(comp_data)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
