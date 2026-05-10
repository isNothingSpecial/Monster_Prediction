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

# --- SIDEBAR: PILIHAN SERIES GAME ---
st.sidebar.title("🐉 Pilihan Series")
series_choice = st.sidebar.selectbox(
    "Pilih Series Game:",
    ["Monster Hunter Stories 1", "Monster Hunter Stories 2", "Monster Hunter Stories 3"]
)

# Mapping nama series ke nama file CSV
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

# --- FUNGSI RADAR CHART HEAD-TO-HEAD ---
def create_h2h_radar(target_name, target_stats, recom_name, recom_stats):
    categories = ['HP', 'Attack', 'Defence', 'Speed']
    cats_closed = categories + [categories[0]]
    
    val_target = [target_stats.get(c, 0) for c in categories]
    val_target_closed = val_target + [val_target[0]]
    
    val_recom = [recom_stats.get(c, 0) for c in categories]
    val_recom_closed = val_recom + [val_recom[0]]
    
    fig = go.Figure()
    
    # Trace 1: Target Lawan (Merah)
    fig.add_trace(go.Scatterpolar(
        r=val_target_closed, theta=cats_closed, fill='toself',
        name=f"Lawan: {target_name}", line_color='#ff4b4b', opacity=0.6
    ))
    
    # Trace 2: Monstie Rekomendasi/Kita (Biru/Cyan)
    fig.add_trace(go.Scatterpolar(
        r=val_recom_closed, theta=cats_closed, fill='toself',
        name=f"Kita: {recom_name}", line_color='#00d4ff', opacity=0.8
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=20, b=20),
        height=300
    )
    return fig

# --- FUNGSI ANALISIS LAWAN & REKOMENDASI ---
def analyze_opponent(monster_name, df):
    stats = df[df['Monster'] == monster_name].iloc[0]

    res_cols = {'Fire': stats['Res_Fire'], 'Water': stats['Res_Water'], 
                'Thunder': stats['Res_Thunder'], 'Ice': stats['Res_Ice'], 'Dragon': stats['Res_Dragon']}
    min_res = min(res_cols.values())
    weak_elements = [el for el, val in res_cols.items() if val == min_res]

    att_cols = {'Fire': stats['Att_Fire'], 'Water': stats['Att_Water'], 
                'Thunder': stats['Att_Thunder'], 'Ice': stats['Att_Ice'], 'Dragon': stats['Att_Dragon']}
    max_att = max(att_cols.values())
    strong_elements = [el for el, val in att_cols.items() if val == max_att]

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
    
    candidates = df[df['Tendency'] == tendency_rev_map[counter_tendency]].copy()
    candidates = candidates[candidates['Monster'] != monster_name]
    
    opp_strongest_element = strong_elements[0] 
    recom_list = []
    
    for weak_el in weak_elements:
        att_col = f'Att_{weak_el}'
        res_col = f'Res_{opp_strongest_element}'
        
        if att_col in candidates.columns and res_col in candidates.columns:
            # Tambahan Rarity jika ada di dataset
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
                    'Stats': row # Simpan full stat untuk parsing ke Radar Chart
                })
                
    unique_recoms = pd.DataFrame(recom_list).drop_duplicates(subset=['Monster'])
    if unique_recoms.empty:
        return None
        
    return unique_recoms.sort_values(by='Score', ascending=False).to_dict('records')


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
            with o_col1:
                st.info(f"**Tendency:**\n{tendency_emojis.get(opp_tendency, opp_tendency)}")
            with o_col2:
                st.error(f"**Serangan Terkuat:**\n{element_emojis.get(strong_els[0], '')} {strong_els[0]}")
            with o_col3:
                st.success(f"**Kelemahan Terbesar:**\n{', '.join([f'{element_emojis.get(e, '')} {e}' for e in weak_els])}")

    st.divider()

    if btn_analyze:
        with st.spinner('Mencari Monstie terbaik dari database...'):
            recommendations = recommend_monsties_v2(selected_monster, df1)
            
            if not recommendations:
                st.warning("Tidak ada Monstie yang cocok ditemukan untuk kriteria ini.")
            else:
                opp_stats, opp_weak, opp_strong, opp_tend, target_tendency = analyze_opponent(selected_monster, df1)
                
                st.markdown(f"### 🏆 Top Rekomendasi untuk Melawan {selected_monster}")
                st.caption(f"Sistem memfilter Monstie dengan Tendency **{target_tendency}**, memiliki elemen serangan **{', '.join(opp_weak)}**, dan mampu menahan serangan **{opp_strong[0]}** dari lawan.")
                
                # Menggunakan layout kolom dinamis
                cols = st.columns(len(recommendations))
                
                for i, recom in enumerate(recommendations):
                    with cols[i]:
                        with st.container(border=True):
                            st.markdown(f"<h3 style='text-align:center;'>#{i+1} {recom['Monster']}</h3>", unsafe_allow_html=True)
                            
                            # Gambar
                            image_path = f"Monslist/{recom['Monster']}.webp"
                            if os.path.exists(image_path):
                                st.image(image_path, use_container_width=True)
                            else:
                                st.info("🖼️ Gambar tidak tersedia", icon="ℹ️")
                            
                            # Metrik
                            st.write(f"**Tipe:** {tendency_emojis.get(recom['Tendency'], recom['Tendency'])}")
                            
                            m1, m2 = st.columns(2)
                            with m1:
                                st.metric(label=f"Atk {recom['Attack Element']}", value=recom['Attack Value'])
                            with m2:
                                st.metric(label=f"Def {recom['Defense Element']}", value=recom['Defense Value'])
                                
                            # Fitur Head-to-Head dalam Expander
                            with st.expander("📊 Lihat Head-to-Head Stats"):
                                fig_mini = create_h2h_radar(
                                    target_name=selected_monster, 
                                    target_stats=opp_stats, 
                                    recom_name=recom['Monster'], 
                                    recom_stats=recom['Stats']
                                )
                                st.plotly_chart(fig_mini, use_container_width=True)


# ==========================================
# TAB 2: BATTLE LAB (SIMULASI MANUAL)
# ==========================================
with tab2:
    st.subheader("🔬 Simulasi Head-to-Head Bebas")
    st.caption("Pilih dua monster apa saja untuk membandingkan statistik dasar mereka secara visual.")
    
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
    
    # Render Chart Besar
    fig_lab = create_h2h_radar(m1_select, m1_stats, m2_select, m2_stats)
    st.plotly_chart(fig_lab, use_container_width=True)
    
    # Tabel Komparasi Detail
    st.markdown("#### Detail Komparasi")
    comp_data = {
        'Statistik': ['HP', 'Attack', 'Defence', 'Speed', 'Tendency'],
        m1_select: [m1_stats.get('HP', 0), m1_stats.get('Attack', 0), m1_stats.get('Defence', 0), m1_stats.get('Speed', 0), tendency_map.get(m1_stats.get('Tendency', 0), '-')],
        m2_select: [m2_stats.get('HP', 0), m2_stats.get('Attack', 0), m2_stats.get('Defence', 0), m2_stats.get('Speed', 0), tendency_map.get(m2_stats.get('Tendency', 0), '-')]
    }
    df_comp = pd.DataFrame(comp_data)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)
