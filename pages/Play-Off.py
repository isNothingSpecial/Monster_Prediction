# File: pages/2_Update_Match.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Update Match", layout="wide")

def load_data():
    df = pd.read_csv("Match.csv", sep=";")
    replacements = {"Bigetron By Vitality": "Bigetron by Vitality"}
    df['Home Team'] = df['Home Team'].str.strip().replace(replacements)
    df['Away team'] = df['Away team'].str.strip().replace(replacements)
    return df

df_main = load_data()

st.markdown("<h1 style='text-align: center;'>🎛️ MATCH CONTROL CENTER</h1>", unsafe_allow_html=True)
st.info("Isi skor langsung pada kartu pertandingan di bawah ini, lalu klik 'Simpan Update'.")
st.markdown("---")

weeks = df_main['Week'].unique()

for week in weeks:
    st.markdown(f"### {week}")
    matches_in_week = df_main[df_main['Week'] == week]
    cols = st.columns(3)
    
    for i, (idx, match) in enumerate(matches_in_week.iterrows()):
        col_idx = i % 3
        with cols[col_idx]:
            with st.container(border=True):
                val_h = int(match['Score Home']) if pd.notnull(match['Score Home']) else None
                val_a = int(match['Score Away']) if pd.notnull(match['Score Away']) else None
                
                st.markdown(f"<div style='text-align: center; color: gray; font-size: 12px;'>Match {i+1}</div>", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1:
                    st.markdown(f"**{match['Home Team']}**")
                    score_h = st.number_input("Score", min_value=0, max_value=2, value=val_h, key=f"h_{idx}", label_visibility="collapsed")
                with c2:
                    st.markdown("<div style='text-align: center; font-weight: bold; margin-top: 10px;'>VS</div>", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"**{match['Away team']}**")
                    score_a = st.number_input("Score", min_value=0, max_value=2, value=val_a, key=f"a_{idx}", label_visibility="collapsed")
                
                if st.button("💾 Simpan Update", key=f"btn_{idx}", use_container_width=True):
                    df_main.at[idx, 'Score Home'] = score_h
                    df_main.at[idx, 'Score Away'] = score_a
                    df_main.to_csv("Match.csv", index=False, sep=";")
                    
                    st.success(f"Skor tersimpan!")
                    st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
