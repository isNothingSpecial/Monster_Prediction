import streamlit as st
import pandas as pd
import os

# --- Load Data ---
try:
    df_monster = pd.read_csv("MHST_monsties.csv")
    df_monster_description = pd.read_csv("MHST_monsties.csv")
except FileNotFoundError:
    st.error("File CSV tidak ditemukan. Pastikan 'MHST_monsties.csv' ada di direktori yang sama.")
    st.stop()

# --- Fungsi Pendukung ---
tendency_map = {1: "Speed", 2: "Power", 3: "Technique"}

# --- Sidebar dan Kontrol Pencarian ---
st.sidebar.header("Pencarian Monster")
search_query = st.sidebar.text_input("Cari Monster (Masukkan nama):")
filtered_data = df_monster[df_monster['Monster'].str.contains(search_query, case=False, na=False)] if search_query else df_monster

if filtered_data.empty:
    st.sidebar.warning("Monster tidak ditemukan.")
    st.stop()

monster_name = st.sidebar.selectbox(
    "Pilih Monster:",
    options=filtered_data['Monster'].unique()
)

# --- Ambil data monster yang dipilih ---
monster_data = df_monster[df_monster['Monster'] == monster_name].iloc[0]
monster_desc = df_monster_description[df_monster_description['Monster'] == monster_name]['Monster'].values[0]
tendency = tendency_map.get(monster_data['Tendency'], "Tidak diketahui")

# --- Stat Elemen dan Resistensi Terkuat ---
stats_attack = ["Att_Fire", "Att_Water", "Att_Thunder", "Att_Ice", "Att_Dragon"]
stats_resist = ["Res_Fire", "Res_Water", "Res_Thunder", "Res_Ice", "Res_Dragon"]

strongest_attack_element = monster_data[stats_attack].idxmax().replace('Att_', '')
highest_resistance_element = monster_data[stats_resist].idxmax().replace('Res_', '')
strongest_attack_value = monster_data[f"Att_{strongest_attack_element}"]
highest_resistance_value = monster_data[f"Res_{highest_resistance_element}"]

# --- ELEMEN TERLEMAH ---
weakest_resistance_element = monster_data[stats_resist].idxmin().replace('Res_', '')
weakest_resistance_value = monster_data[f"Res_{weakest_resistance_element}"]
# --- Halaman Utama ---
st.markdown(
    """
    <h1 style='text-align: center;'>LITERATUR</h1>
    """,
    unsafe_allow_html=True
)
st.divider()

# --- Dropdown untuk Literatur ---
literatur_options = ['Monster Description', 'Loot', 'Armor and Weapon Obtained', 'Egg and Habitat']
literatur = st.selectbox('Pilih Literatur yang ingin Anda ketahui', literatur_options)
st.divider()

# --- Tampilkan Konten Berdasarkan Dropdown ---
if literatur == 'Monster Description':
    st.header(f"Monster: {monster_name}")

    col1, col2 = st.columns([1, 2])
    with col1:
        # Pengecekan gambar untuk menghindari error
        image_path = f"Monslist/{monster_name}.webp"
        if os.path.exists(image_path):
            st.image(image_path, caption=f"{monster_name}", use_container_width=True)
        else:
            st.warning("Gambar monster tidak ditemukan.")

    with col2:
        st.subheader("Deskripsi")
        st.write(f"**Nama**: {monster_desc}")
        st.write(f"**Tendency**: {tendency}")
        st.write(f"**Elemen Terkuat**: {strongest_attack_element} ({strongest_attack_value})")
        st.write(f"**Resistance Tertinggi**: {highest_resistance_element} ({highest_resistance_value})")
        st.write(f"**Resistance Terendah**: {weakest_resistance_element} ({weakest_resistance_value})")

    st.subheader("Statistik Dasar")
    col3, col4 = st.columns(2)
    with col3:
        chart_path = f"Basic_Stat/{monster_name}.png"
        if os.path.exists(chart_path):
            st.image(chart_path, use_container_width=True)
        else:
            st.warning("Grafik Statistik Dasar tidak ditemukan.")

    with col4:
        for stat in ["HP", "Attack", "Defence", "Speed"]:
            st.write(f"**{stat}:** {monster_data[stat]}")

    st.subheader("Statistik Attack Element")
    col5, col6 = st.columns(2)
    with col5:
        chart_path = f"Att_Stat/{monster_name}.png"
        if os.path.exists(chart_path):
            st.image(chart_path, use_container_width=True)
        else:
            st.warning("Grafik Statistik Attack tidak ditemukan.")

    with col6:
        for stat in stats_attack:
            st.write(f"**{stat.replace('Att_', 'Attack ')}:** {monster_data[stat]}")

    st.subheader("Statistik Resistance Element")
    col7, col8 = st.columns(2)
    with col7:
        chart_path = f"Res_Stat/{monster_name}.png"
        if os.path.exists(chart_path):
            st.image(chart_path, use_container_width=True)
        else:
            st.warning("Grafik Statistik Resistance tidak ditemukan.")

    with col8:
        for stat in stats_resist:
            st.write(f"**{stat.replace('Res_', 'Resistance ')}:** {monster_data[stat]}")

elif literatur == 'Loot':
    st.header(f"Loot dari Monster: {monster_name}")
    st.info("Informasi loot akan ditambahkan di sini.")

elif literatur == 'Armor and Weapon Obtained':
    st.header(f"Armor dan Weapon dari Monster: {monster_name}")
    st.info("Informasi armor dan weapon akan ditambahkan di sini.")

elif literatur == 'Egg and Habitat':
    st.header(f"Egg dan Habitat dari Monster: {monster_name}")
    st.info("Informasi egg dan habitat akan ditambahkan di sini.")
