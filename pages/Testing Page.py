import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="MHST Recommendation System", layout="wide")

# --- KAMUS EMOJI & TENDENCY ---
tendency_map = {1: 'Speed', 2: 'Power', 3: 'Technique'}
tendency_emojis = {
    'Speed': '🏃 (Speed)', 'Power': '🥊 (Power)', 'Technique': '🧠 (Technique)', 'Unknown': '❓ (Unknown)'
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

# --- PERUBAHAN KE FORMAT EXCEL (.xlsx) ---
file_map = {
    "Monster Hunter Stories 1": "MHST_monsties.xlsx",
    "Monster Hunter Stories 2": "MHST2_monsties.xlsx", 
    "Monster Hunter Stories 3": "MHST3_monsties.xlsx"  
}
file_name = file_map[series_choice]

# --- LOAD DATA ---
@st.cache_data
def load_data(file_path):
    try:
        # Menggunakan read_excel() alih-alih read_csv()
        df = pd.read_excel(file_path, engine='openpyxl')
        if 'No' in df.columns:
            df = df.drop(columns=['No'])
        return df
    except ImportError:
        st.error("Library 'openpyxl' belum terinstall. Silakan buka terminal dan ketik: pip install openpyxl")
        st.stop()
    except Exception as e:
        return None

df1 = load_data(file_name)

# --- HELPER: PARSER FASE ---
def parse_combat_pattern(row):
    """Memecah string Combat Pattern menjadi dictionary fase."""
    parsed = {}
    pattern_string = row.get('Combat Pattern', 'Normal:Unknown') 
    
    if pd.notna(pattern_string):
        phases = str(pattern_string).split('|')
        for p in phases:
            if ':' in p:
                k, v = p.split(':')
                parsed[k.strip()] = v.strip()
    
    if not parsed:
        parsed['Normal'] = 'Unknown'
    return parsed

def get_primary_tendency(row):
    """Mengambil tendensi Normal sebagai identitas utama monstie tersebut."""
    return parse_combat_pattern(row).get('Normal', 'Unknown')

if df1 is not None:
    df1['Primary_Tendency'] = df1.apply(get_primary_tendency, axis=1)

# --- FUNGSI RADAR CHART DINAMIS ---
def create_h2h_radar_dynamic(target_name, target_stats, recom_name, recom_stats, categories, title):
    display_cats = [c.replace('Att_', '').replace('Res_', '') for c in categories]
    cats_closed = display_cats + [display_cats[0]]
    
    val_target = [target_stats.get(c, 0) for c in categories]
    val_target_closed = val_target + [val_target[0]]
    
    val_recom = [recom_stats.get(c, 0) for c in categories]
    val_recom_closed = val_recom + [val_recom[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=val_target_closed, theta=cats_closed, fill='toself', name=f"{target_name}", line_color='#ff4b4b', opacity=0.6))
    fig.add_trace(go.Scatterpolar(r=val_recom_closed, theta=cats_closed, fill='toself', name=f"{recom_name}", line_color='#00d4ff', opacity=0.8))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=14)),
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False, 
        margin=dict(l=20, r=20, t=40, b=20),
        height=280
    )
    return fig

# --- FUNGSI ANALISIS LAWAN & RACIK PARTY ---
def analyze_opponent_multiphase(monster_name, df):
    stats = df[df['Monster'] == monster_name].iloc[0]

    def safe_num(val, default=3):
        try:
            num = float(val)
            return default if pd.isna(num) else num
        except (ValueError, TypeError):
            return default

    res_cols = {k.replace('Res_', ''): safe_num(stats.get(k)) for k in stats_resist if k in stats}
    if not res_cols: res_cols = {'Fire':3, 'Water':3, 'Thunder':3, 'Ice':3, 'Dragon':3} 
    min_res = min(res_cols.values())
    weak_elements = [el for el, val in res_cols.items() if val == min_res]

    att_cols = {k.replace('Att_', ''): safe_num(stats.get(k)) for k in stats_attack if k in stats}
    if not att_cols: att_cols = {'Fire':3, 'Water':3, 'Thunder':3, 'Ice':3, 'Dragon':3} 
    max_att = max(att_cols.values())
    strong_elements = [el for el, val in att_cols.items() if val == max_att]

    if not strong_elements: strong_elements = ['Raw']
    if not weak_elements: weak_elements = ['Raw']

    opp_tendencies = parse_combat_pattern(stats)
        
    return stats, weak_elements, strong_elements, opp_tendencies

def recommend_hunting_party(monster_name, df):
    stats, weak_elements, strong_elements, opp_tendencies = analyze_opponent_multiphase(monster_name, df)
    opp_strongest_element = strong_elements[0] if strong_elements else 'Fire'
    
    party_lineup = []
    used_monsters = set()
    
    for phase_name, opp_tend in opp_tendencies.items():
        if opp_tend == 'Speed': counter_tend = 'Technique'
        elif opp_tend == 'Technique': counter_tend = 'Power'
        elif opp_tend == 'Power': counter_tend = 'Speed'
        else: counter_tend = 'Unknown'
        
        candidates = df[df['Primary_Tendency'] == counter_tend].copy()
        candidates = candidates[candidates['Monster'] != monster_name]
        candidates = candidates[~candidates['Monster'].isin(used_monsters)] 
        
        best_cand = None
        best_score = -999
        best_weak_el = weak_elements[0] if weak_elements else 'Raw'
        
        for weak_el in weak_elements:
            att_col = f'Att_{weak_el}'
            res_col = f'Res_{opp_strongest_element}'
            
            if att_col in candidates.columns and res_col in candidates.columns:
                rarity_bonus = candidates.get('Rarity', 1) * 2 
                candidates['Score'] = (candidates[att_col] * 2) + candidates[res_col] + rarity_bonus
                
                if not candidates.empty:
                    top = candidates.sort_values(by=['Score', att_col], ascending=[False, False]).iloc[0]
                    if top['Score'] > best_score:
                        best_score = top['Score']
                        best_cand = top
                        best_weak_el = weak_el
                        
        if best_cand is not None:
            used_monsters.add(best_cand['Monster'])
            party_lineup.append({
                'Phase': phase_name,
                'Opponent_Tendency': opp_tend,
                'Counter_Tendency': counter_tend,
                'Monster': best_cand['Monster'],
                'Attack Element': best_weak_el,
                'Attack Value': best_cand.get(f'Att_{best_weak_el}', 0),
                'Defense Element': opp_strongest_element,
                'Defense Value': best_cand.get(f'Res_{opp_strongest_element}', 0),
                'Tendency': counter_tend, 
                'Stats': best_cand 
            })
            
    return party_lineup

# --- UI APLIKASI STREAMLIT ---
st.markdown(f"<h1 style='text-align: center;'>⚔️ {series_choice}: Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Temukan Hunting Party terbaik atau lakukan simulasi komparasi stat di Battle Lab.</p>", unsafe_allow_html=True)
st.divider()

if df1 is None:
    st.error(f"Dataset untuk {series_choice} ({file_name}) belum tersedia di direktori atau format tidak didukung.")
    st.info("Pastikan Anda sudah menyimpan file sebagai Excel (.xlsx) dan menginstall library openpyxl.")
    st.stop() 

monster_list_all = sorted(df1['Monster'].tolist())

# --- DUA TAB UTAMA ---
tab1, tab2 = st.tabs(["🏆 Party Recommender", "🔬 Battle Lab (Head-to-Head)"])

# ==========================================
# TAB 1: AUTO RECOMMENDER / PARTY LINEUP
# ==========================================
with tab1:
    col_select, col_opp_info = st.columns([1, 2])

    with col_select:
        st.subheader("🎯 Target Lawan")
        selected_monster = st.selectbox("Pilih monster yang ingin Anda lawan:", options=monster_list_all)
        btn_analyze = st.button("Racik Hunting Party", use_container_width=True, type="primary")

    with col_opp_info:
        if selected_monster:
            stats, weak_els, strong_els, opp_tendencies = analyze_opponent_multiphase(selected_monster, df1)
            st.subheader("📊 Profil Target & Fase Pertarungan")
            
            strong_el_display = strong_els[0] if len(strong_els) > 0 else "Unknown"
            
            o_col1, o_col2 = st.columns(2)
            with o_col1: st.error(f"**Serangan Terkuat:**\n{element_emojis.get(strong_el_display, '')} {strong_el_display}")
            with o_col2: st.success(f"**Kelemahan Terbesar:**\n{', '.join([f'{element_emojis.get(e, '')} {e}' for e in weak_els])}")
            
            st.markdown("##### ⚔️ Pola Serangan (Combat Pattern)")
            t_cols = st.columns(max(len(opp_tendencies), 1))
            for idx, (phase, tend) in enumerate(opp_tendencies.items()):
                with t_cols[idx]:
                    emoji = tendency_emojis.get(tend, tend)
                    if phase == 'Normal': st.info(f"**{phase}:**\n{emoji}")
                    elif phase == 'Enraged': st.warning(f"**{phase}:**\n{emoji}")
                    else: st.error(f"**{phase}:**\n{emoji}")

    st.divider()

    if btn_analyze:
        with st.spinner('Meracik Hunting Party terbaik...'):
            party_lineup = recommend_hunting_party(selected_monster, df1)
            
            if not party_lineup:
                st.warning("Tidak dapat meracik Party. Database monster kurang lengkap.")
            else:
                opp_stats, opp_weak, opp_strong, opp_tendencies = analyze_opponent_multiphase(selected_monster, df1)
                
                st.markdown(f"### 🛡️ Recommended Line-up untuk Menaklukkan {selected_monster}")
                st.caption("Sistem menyusun tim berdasarkan masing-masing fase wujud target. Siapkan Monstie ini di dalam party Anda dan lakukan Swap di saat yang tepat!")
                
                num_cols = max(len(party_lineup), 3)
                cols = st.columns(num_cols)
                
                for i, recom in enumerate(party_lineup):
                    with cols[i]:
                        with st.container(border=True):
                            if i == 0: role = "🥇 Vanguard (Pembuka)"
                            elif i == 1: role = "🔄 Backup (Swap 1)"
                            else: role = f"⚠️ Specialist (Swap {i})"
                            
                            st.markdown(f"<div style='text-align:center; color:gray; font-size:12px;'>{role}</div>", unsafe_allow_html=True)
                            st.markdown(f"<h4 style='text-align:center;'>Fase: {recom['Phase']}</h4>", unsafe_allow_html=True)
                            st.caption(f"<div style='text-align:center;'>Counter <b>{recom['Opponent_Tendency']}</b> → Gunakan {tendency_emojis.get(recom['Counter_Tendency'], recom['Counter_Tendency'])}</div>", unsafe_allow_html=True)
                            
                            st.markdown(f"<h3 style='text-align:center; color:#00d4ff;'>{recom['Monster']}</h3>", unsafe_allow_html=True)
                            
                            image_path = f"Monslist/{recom['Monster']}.webp"
                            if os.path.exists(image_path):
                                st.image(image_path, use_container_width=True)
                            else:
                                st.info("🖼️ Gambar tidak tersedia", icon="ℹ️")
                            
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
        m1_tend = df1[df1['Monster'] == m1_select].iloc[0]['Primary_Tendency']
        
    with col_vs:
        st.markdown("<h1 style='text-align:center; padding-top:25px;'>VS</h1>", unsafe_allow_html=True)
        
    with col_m2:
        m2_select = st.selectbox("Lawan 2 (Biru):", options=monster_list_all, index=1 if len(monster_list_all)>1 else 0, key="lab_m2")
        m2_stats = df1[df1['Monster'] == m2_select].iloc[0]
        m2_tend = df1[df1['Monster'] == m2_select].iloc[0]['Primary_Tendency']
        
    st.divider()
    
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><h5><span style='color: #ff4b4b;'>🔴 {m1_select}</span> &nbsp; VS &nbsp; <span style='color: #00d4ff;'>🔵 {m2_select}</span></h5></div>", unsafe_allow_html=True)

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
    
    with st.expander("📄 Lihat Angka Detail Komparasi"):
        m1_data = [tendency_map.get(m1_tend, m1_tend)] + [m1_stats.get(s, 0) for s in stats_basic + stats_attack + stats_resist]
        m2_data = [tendency_map.get(m2_tend, m2_tend)] + [m2_stats.get(s, 0) for s in stats_basic + stats_attack + stats_resist]
        
        clean_stats_names = ['Primary Tendency'] + stats_basic + [s.replace('Att_', 'Attack ') for s in stats_attack] + [s.replace('Res_', 'Resistance ') for s in stats_resist]
        
        comp_data = {
            'Statistik': clean_stats_names,
            m1_select: m1_data,
            m2_select: m2_data
        }
        df_comp = pd.DataFrame(comp_data)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
