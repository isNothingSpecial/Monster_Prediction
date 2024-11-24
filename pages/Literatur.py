import streamlit as st
import pandas as pd

# Load data monster
monster_data = pd.read_csv("MHST_monsties.csv")
monster_description = pd.read_csv("MHST_monsties.csv")
tendency_map = {1: "Speed", 2: "Power", 3: "Technique"}

# Sidebar untuk pencarian
st.sidebar.title("Pencarian Monster")
search_query = st.sidebar.text_input("Cari Monster (Masukkan nama):")
filtered_data = monster_data[monster_data['Monster'].str.contains(search_query, case=False)] if search_query else monster_data

monster_name = st.sidebar.selectbox(
    "Pilih Monster:",
    options=filtered_data['Monster'].unique()
)

# Filter data monster yang dipilih
monster = monster_data[monster_data['Monster'] == monster_name].iloc[0]
description = monster_description[monster_description['Monster'] == monster_name]['Monster'].values[0]
tendency = tendency_map[monster['Tendency']] 
stats_basic = ["HP", "Attack", "Defence", "Speed"]  # Kolom dasar
stats_attack = ["Att_Fire", "Att_Water", "Att_Thunder", "Att_Ice", "Att_Dragon"]  # Kolom attack element
stats_resist = ["Res_Fire", "Res_Water", "Res_Thunder", "Res_Ice", "Res_Dragon"]  # Kolom resistance element

# Path gambar monster dan statistik
monster_image_path = f"Monslist/{monster_name}.webp"
basic_stats_chart_path = f"Basic_Stat/{monster_name}.png"
attack_stats_chart_path = f"Att_Stat/{monster_name}.png"
resistance_stats_chart_path = f"Res_Stat/{monster_name}.png"

# Header
st.title(f"Monster: {monster_name}")

# Deskripsi dan Tendency
st.image(monster_image_path, caption=f"{monster_name}", use_column_width=True)
st.subheader("Deskripsi")
st.write(f"**{description}**")
st.write(f"**Tendency**: {tendency}")

# Membuat layout grid
st.subheader("Statistik Dasar")
col1, col2 = st.columns(1,1.5)  # Kolom untuk grid 2 kolom

with col1:
    # Statistik Dasar
    st.image(basic_stats_chart_path, use_column_width=True)

with col2:
    for stat in stats_basic:
        st.write(f"**{stat}:** {monster[stat]}")  # Menampilkan notasi stat dasar

# Grid untuk Attack
st.subheader("Statistik Attack Element")
col3, col4 = st.columns(1,1.5)

with col3:
    # Statistik Attack Element
    st.image(attack_stats_chart_path, use_column_width=True)

with col4:
    for stat in stats_attack:
        st.write(f"**{stat.replace('Att_', 'Attack ')}:** {monster[stat]}")  # Menampilkan notasi attack element

# Grid untuk Resistance
st.subheader("Statistik Resistance Element")
col5, col6 = st.columns(1,1.5)

with col3:
    # Statistik Attack Element
    st.image(resistance_stats_chart_path, use_column_width=True)

with col4:
    for stat in stats_attack:
        st.write(f"**{stat.replace('Res_', 'Resistance ')}:** {monster[stat]}")  # Menampilkan notasi attack element
