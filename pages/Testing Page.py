import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# --- 1. KONFIGURASI HALAMAN & VARIABEL GLOBAL TERSAMA ---
st.set_page_config(page_title="MHST Recommendation System", layout="wide")

tendency_map = {1: 'Speed', 2: 'Power', 3: 'Technique'}
tendency_rev_map = {'Speed': 1, 'Power': 2, 'Technique': 3}
element_emojis = {'Fire': '🔥', 'Water': '💧', 'Thunder': '⚡', 'Ice': '❄️', 'Dragon': '🐉'}
tendency_emojis = {'Speed': '🏃 (Speed)', 'Power': '🥊 (Power)', 'Technique': '🧠 (Technique)', 'Unknown': '❓ (Unknown)'}

stats_basic = ['HP', 'Attack', 'Defence', 'Speed']
stats_attack = ['Att_Fire', 'Att_Water', 'Att_Thunder', 'Att_Ice', 'Att_Dragon']
stats_resist = ['Res_Fire', 'Res_Water', 'Res_Thunder', 'Res_Ice', 'Res_Dragon']

# --- 2. FUNGSI LOAD DATA & CHART (DIPAKAI BERSAMA) ---
@st.cache_data
def load_data(file_path):
    try:
        # Membaca CSV dengan deteksi koma/titik koma otomatis
        df = pd.read_csv(file_path, sep=None, engine='python')
        if 'No' in df.columns:
            df = df.drop(columns=['No'])
        return df
    except Exception:
        # Jika user sudah mengubahnya jadi excel, sistem akan mencoba memuat excel
        try:
            df = pd.read_excel(file_path.replace('.csv', '.xlsx'), engine='openpyxl')
            if 'No' in df.columns: df = df.drop(columns=['No'])
            return df
        except:
            return None

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
    fig.update_layout(title=dict(text=title, x=0.5, font=dict(size=14)), polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False, margin=dict(l=20, r=20, t=40, b=20), height=280)
    return fig

# =====================================================================
# --- 3. DUNIA MHST 1 (SIMPLE, TOP 3, NUMERIC TENDENCY) ---
# =====================================================================
def run_mhst1_app(df):
    st.markdown("<h1 style='text-align: center;'>⚔️ MHST 1: Classic Recommender</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Mencari Top 3 Monstie pendamping berdasarkan kelemahan elemen dan adu Tendency klasik.</p>", unsafe_allow_html=True)
    st.divider()

    def analyze_mhst1(monster_name):
        stats = df[df['Monster'] == monster_name].iloc[0]
        res_cols = {k.replace('Res_', ''): stats.get(k, 3) for k in stats_resist}
        min_res = min(res_cols.values())
        weak_elements = [el for el, val in res_cols.items() if val == min_res]

        att_cols = {k.replace('Att_', ''): stats.get(k, 3) for k in stats_attack}
        max_att = max(att_cols.values())
        strong_elements = [el for el, val in att_cols.items() if val == max_att]

        # MHST 1 menggunakan angka 1, 2, 3 di kolom 'Tendency'
        opp_tendency = tendency_map.get(stats.get('Tendency', 0), 'Unknown')
        if opp_tendency == 'Speed': counter_tend = 'Technique'
        elif opp_tendency == 'Technique': counter_tend = 'Power'
        elif opp_tendency == 'Power': counter_tend = 'Speed'
        else: counter_tend = 'Unknown'
        return stats, weak_elements, strong_elements, opp_tendency, counter_tend

    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        monster_list = sorted(df['Monster'].tolist())
        target = st.selectbox("Pilih Target Lawan:", options=monster_list, key="m1_sel")
        btn = st.button("Cari Top 3 Counter", use_container_width=True, type="primary")

    with col_info:
        if target:
            stats, weak_els, strong_els, opp_tend, _ = analyze_mhst1(target)
            o1, o2, o3 = st.columns(3)
            with o1: st.info(f"**Tendency:**\n{tendency_emojis.get(opp_tend, opp_tend)}")
            with o2: st.error(f"**Serangan Kuat:**\n{strong_els[0] if strong_els else 'Raw'}")
            with o3: st.success(f"**Kelemahan:**\n{', '.join(weak_els)}")

    if btn:
        stats, weak_els, strong_els, opp_tend, counter_tend = analyze_mhst1(target)
        candidates = df[df['Tendency'] == tendency_rev_map.get(counter_tend, 0)].copy()
        candidates = candidates[candidates['Monster'] != target]
        opp_strongest = strong_els[0] if strong_els else 'Fire'

        recom_list = []
        for w_el in weak_els:
            att_col, res_col = f'Att_{w_el}', f'Res_{opp_strongest}'
            if att_col in candidates.columns and res_col in candidates.columns:
                candidates['Score'] = (candidates[att_col] * 2) + candidates[res_col]
                for _, row in candidates.sort_values(by=['Score'], ascending=False).head(3).iterrows():
                    recom_list.append({'Monster': row['Monster'], 'Score': row['Score'], 'Stats': row, 'Atk': row[att_col], 'Def': row[res_col], 'AtkEl': w_el, 'DefEl': opp_strongest})
        
        final_recoms = pd.DataFrame(recom_list).drop_duplicates(subset=['Monster']).sort_values(by='Score', ascending=False).head(3).to_dict('records')
        
        if final_recoms:
            st.markdown(f"### 🏆 Top 3 Rekomendasi vs {target}")
            cols = st.columns(3)
            for i, r in enumerate(final_recoms):
                with cols[i]:
                    with st.container(border=True):
                        st.markdown(f"<h3 style='text-align:center;'>#{i+1} {r['Monster']}</h3>", unsafe_allow_html=True)
                        st.write(f"**Tipe:** {tendency_emojis.get(counter_tend)}")
                        m1, m2 = st.columns(2)
                        with m1: st.metric(f"Atk {r['AtkEl']}", r['Atk'])
                        with m2: st.metric(f"Def {r['DefEl']}", r['Def'])
                        with st.expander("📊 Head-to-Head (Dasar)"):
                            st.plotly_chart(create_h2h_radar_dynamic(target, stats, r['Monster'], r['Stats'], stats_basic, "Stat Dasar"), use_container_width=True)
        else:
            st.warning("Tidak ada Monstie yang cocok ditemukan.")

# =====================================================================
# --- 4. DUNIA MHST 2 (MULTIPHASE, HUNTING PARTY, STRING PARSER) ---
# =====================================================================
def run_mhst2_app(df):
    st.markdown("<h1 style='text-align: center;'>⚔️ MHST 2: Party Recommender</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Meracik tim lengkap (Vanguard, Backup, Specialist) untuk menghadapi setiap fase bos.</p>", unsafe_allow_html=True)
    st.divider()

    def parse_combat_pattern(row):
        parsed = {}
        pattern = row.get('Combat Pattern', 'Normal:Unknown')
        if pd.notna(pattern):
            for p in str(pattern).split('|'):
                if ':' in p:
                    k, v = p.split(':')
                    parsed[k.strip()] = v.strip()
        if not parsed: parsed['Normal'] = 'Unknown'
        return parsed

    df['Primary_Tendency'] = df.apply(lambda r: parse_combat_pattern(r).get('Normal', 'Unknown'), axis=1)

    def analyze_mhst2(monster_name):
        stats = df[df['Monster'] == monster_name].iloc[0]
        res_cols = {k.replace('Res_', ''): pd.to_numeric(stats.get(k), errors='coerce') for k in stats_resist if k in stats}
        res_cols = {k: v if pd.notna(v) else 3 for k, v in res_cols.items()}
        min_res = min(res_cols.values() or [3])
        weak_elements = [el for el, val in res_cols.items() if val == min_res] or ['Raw']

        att_cols = {k.replace('Att_', ''): pd.to_numeric(stats.get(k), errors='coerce') for k in stats_attack if k in stats}
        att_cols = {k: v if pd.notna(v) else 3 for k, v in att_cols.items()}
        max_att = max(att_cols.values() or [3])
        strong_elements = [el for el, val in att_cols.items() if val == max_att] or ['Raw']

        opp_tendencies = parse_combat_pattern(stats)
        return stats, weak_elements, strong_elements, opp_tendencies

    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        monster_list = sorted(df['Monster'].tolist())
        target = st.selectbox("Pilih Target Lawan:", options=monster_list, key="m2_sel")
        btn = st.button("Racik Hunting Party", use_container_width=True, type="primary")

    with col_info:
        if target:
            stats, weak_els, strong_els, opp_tendencies = analyze_mhst2(target)
            st.subheader("📊 Fase Pertarungan")
            t_cols = st.columns(max(len(opp_tendencies), 1))
            for idx, (phase, tend) in enumerate(opp_tendencies.items()):
                with t_cols[idx]:
                    emoji = tendency_emojis.get(tend, tend)
                    if phase == 'Normal': st.info(f"**{phase}:**\n{emoji}")
                    elif phase == 'Enraged': st.warning(f"**{phase}:**\n{emoji}")
                    else: st.error(f"**{phase}:**\n{emoji}")

    if btn:
        stats, weak_els, strong_els, opp_tendencies = analyze_mhst2(target)
        opp_strongest = strong_els[0]
        party_lineup = []
        used_monsters = set()

        for phase_name, opp_tend in opp_tendencies.items():
            counter_tend = 'Technique' if opp_tend == 'Speed' else 'Power' if opp_tend == 'Technique' else 'Speed' if opp_tend == 'Power' else 'Unknown'
            candidates = df[(df['Primary_Tendency'] == counter_tend) & (df['Monster'] != target) & (~df['Monster'].isin(used_monsters))].copy()
            
            best_cand, best_score, best_weak_el = None, -999, weak_els[0]
            for w_el in weak_els:
                att_col, res_col = f'Att_{w_el}', f'Res_{opp_strongest}'
                if att_col in candidates.columns and res_col in candidates.columns:
                    candidates['Score'] = (candidates[att_col] * 2) + candidates[res_col] + (candidates.get('Rarity', 1) * 2)
                    if not candidates.empty:
                        top = candidates.sort_values(by=['Score', att_col], ascending=[False, False]).iloc[0]
                        if top['Score'] > best_score:
                            best_score, best_cand, best_weak_el = top['Score'], top, w_el
                            
            if best_cand is not None:
                used_monsters.add(best_cand['Monster'])
                party_lineup.append({'Phase': phase_name, 'OppTend': opp_tend, 'CounterTend': counter_tend, 'Monster': best_cand['Monster'], 'Stats': best_cand, 'AtkEl': best_weak_el, 'Atk': best_cand.get(f'Att_{best_weak_el}', 0), 'DefEl': opp_strongest, 'Def': best_cand.get(f'Res_{opp_strongest}', 0)})

        if party_lineup:
            st.markdown(f"### 🛡️ Recommended Line-up vs {target}")
            cols = st.columns(max(len(party_lineup), 3))
            for i, r in enumerate(party_lineup):
                with cols[i]:
                    with st.container(border=True):
                        role = "🥇 Vanguard (Pembuka)" if i == 0 else "🔄 Backup (Swap 1)" if i == 1 else f"⚠️ Specialist (Swap {i})"
                        st.markdown(f"<div style='text-align:center; color:gray; font-size:12px;'>{role}</div>", unsafe_allow_html=True)
                        st.markdown(f"<h4 style='text-align:center;'>Fase: {r['Phase']}</h4>", unsafe_allow_html=True)
                        st.caption(f"<div style='text-align:center;'>Gunakan {tendency_emojis.get(r['CounterTend'])}</div>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='text-align:center; color:#00d4ff;'>{r['Monster']}</h3>", unsafe_allow_html=True)
                        m1, m2 = st.columns(2)
                        with m1: st.metric(f"Atk {r['AtkEl']}", r['Atk'])
                        with m2: st.metric(f"Def {r['DefEl']}", r['Def'])
                        with st.expander("📊 Head-to-Head (Dasar)"):
                            st.plotly_chart(create_h2h_radar_dynamic(target, stats, r['Monster'], r['Stats'], stats_basic, "Stat Dasar"), use_container_width=True)
        else:
            st.warning("Tidak dapat meracik Party. Database monster kurang lengkap.")

# =====================================================================
# --- 5. LOGIKA NAVIGASI UTAMA (SWITCHING) ---
# =====================================================================
st.sidebar.title("🐉 Pilihan Series")
series_choice = st.sidebar.selectbox("Pilih Series Game:", ["Monster Hunter Stories 1", "Monster Hunter Stories 2"])

file_map = {
    "Monster Hunter Stories 1": "MHST_monsties.csv",
    "Monster Hunter Stories 2": "MHST2_monsties.csv"
}

df_current = load_data(file_map[series_choice])

if df_current is None:
    st.error(f"Dataset untuk {series_choice} tidak ditemukan atau format rusak.")
    st.stop()

# Mengeksekusi blok kode yang berbeda berdasarkan pilihan di dropdown
if series_choice == "Monster Hunter Stories 1":
    run_mhst1_app(df_current)
elif series_choice == "Monster Hunter Stories 2":
    run_mhst2_app(df_current)
