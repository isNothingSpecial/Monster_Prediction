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

# Statistik Elemen
stats_attack = ["Att_Fire", "Att_Water", "Att_Thunder", "Att_Ice", "Att_Dragon"]
stats_resist = ["Res_Fire", "Res_Water", "Res_Thunder", "Res_Ice", "Res_Dragon"]

# Elemen Terkuat dan Resistance Tertinggi
strongest_attack_element = monster[stats_attack].idxmax()
highest_resistance_element = monster[stats_resist].idxmax()
strongest_attack_value = monster[strongest_attack_element]
highest_resistance_value = monster[highest_resistance_element]

# Path gambar monster dan statistik
monster_image_path = f"Monslist/{monster_name}.webp"
basic_stats_chart_path = f"Basic_Stat/{monster_name}.png"
attack_stats_chart_path = f"Att_Stat/{monster_name}.png"
resistance_stats_chart_path = f"Res_Stat/{monster_name}.png"

st.markdown(
    """
    <h1 style='text-align: center;'>LITERATUR</h1>
    """, 
    unsafe_allow_html=True
)

# Dropdown untuk literatur
literatur_options = ['Monster Description', 'Loot', 'Armor and Weapon Obtained', 'Egg and Habitat']
literatur = st.selectbox('Pilih Literatur yang ingin Anda ketahui', literatur_options)

# Tampilkan konten berdasarkan literatur
if literatur == 'Monster Description':
    st.title(f"Monster: {monster_name}")

    # Membuat layout grid
    col1, col2 = st.columns(2)
    with col1:
        # Gambar monster
        st.image(monster_image_path, caption=f"{monster_name}", use_column_width=True)
    with col2:
        # Deskripsi dan Tendency
        st.subheader("Deskripsi")
        st.write(f"**Nama**: {description}")
        st.write(f"**Tendency**: {tendency}")
        st.write(f"**Elemen Terkuat**: {strongest_attack_element.replace('Att_', '')} ({strongest_attack_value})")
        st.write(f"**Resistance Tertinggi**: {highest_resistance_element.replace('Res_', '')} ({highest_resistance_value})")

    # Statistik Dasar
    st.subheader("Statistik Dasar")
    col3, col4 = st.columns(2)
    with col3:
        st.image(basic_stats_chart_path, use_column_width=True)
    with col4:
        for stat in ["HP", "Attack", "Defence", "Speed"]:
            st.write(f"**{stat}:** {monster[stat]}")

    # Statistik Attack Element
    st.subheader("Statistik Attack Element")
    col5, col6 = st.columns(2)
    with col5:
        st.image(attack_stats_chart_path, use_column_width=True)
    with col6:
        for stat in stats_attack:
            st.write(f"**{stat.replace('Att_', 'Attack ')}:** {monster[stat]}")

    # Statistik Resistance Element
    st.subheader("Statistik Resistance Element")
    col7, col8 = st.columns(2)
    with col7:
        st.image(resistance_stats_chart_path, use_column_width=True)
    with col8:
        for stat in stats_resist:
            st.write(f"**{stat.replace('Res_', 'Resistance ')}:** {monster[stat]}")

elif literatur == 'Loot':
    st.title(f"Loot dari Monster: {monster_name}")
    st.write("Informasi loot akan ditambahkan di sini.")

elif literatur == 'Armor and Weapon Obtained':
    st.title(f"Armor dan Weapon dari Monster: {monster_name}")
    st.write("Informasi armor dan weapon akan ditambahkan di sini.")

elif literatur == 'Egg and Habitat':
    st.title(f"Egg dan Habitat dari Monster: {monster_name}")
    st.write("Informasi egg dan habitat akan ditambahkan di sini.")
