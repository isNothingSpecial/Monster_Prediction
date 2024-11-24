import streamlit as st
import pandas as pd

# Load data monster
monster_data = pd.read_csv("MHST_monsties.csv")
monster_description = pd.read_csv("MHST_monsties.csv")

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

# Path gambar monster dan statistik
monster_image_path = f"Monslist/{monster_name}.webp"
basic_stats_chart_path = f"Basic_Stat/{monster_name}.png"
attack_stats_chart_path = f"Att_Stat/{monster_name}.png"
resistance_stats_chart_path = f"Res_Stat/{monster_name}.png"

# Header
st.title(f"Monster: {monster_name}")

# Membuat layout grid
col1, col2 = st.columns(2)  # Kolom untuk grid 2 kolom

with col1:
    # Gambar Monster
    st.image(monster_image_path, caption=f"{monster_name}", use_column_width=True)
    # Statistik Dasar
    st.subheader("Statistik Dasar")
    st.image(basic_stats_chart_path, use_column_width=True)


with col2:
    # Deskripsi Monster
    st.subheader("Deskripsi")
    st.write(description)

# Grid untuk Attack dan Resistance
col3, col4 = st.columns(2)

with col3:
    # Statistik Attack Element
    st.subheader("Statistik Attack Element")
    st.image(attack_stats_chart_path, use_column_width=True)

with col4:
    # Statistik Resistance
    st.subheader("Statistik Resistance")
    st.image(resistance_stats_chart_path,use_column_width=True)
