import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# --- Konfigurasi Halaman Dasar ---
st.set_page_config(page_title="MHST Database", layout="wide", initial_sidebar_state="expanded")

# --- Helper Function: Pembuat Radar Chart ---
def create_radar_chart(categories, values, title, line_color):
    # Menyambungkan titik terakhir ke titik awal agar poligon tertutup
    categories = list(categories) + [list(categories)[0]]
    values = list(values) + [list(values)[0]]
    
    # Menentukan nilai maksimum untuk skala chart (minimal 5)
    max_val = max(5, max(values))
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=[c.replace('Att_', '').replace('Res_', '') for c in categories],
        fill='toself',
        name=title,
        line_color=line_color,
        marker=dict(size=8)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max_val])
        ),
        showlegend=False,
        title=dict(text=title, font=dict(size=16), x=0.5),
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )
    return fig

# --- Sidebar: Pilihan Series Game ---
st.sidebar.title("🐉 MHST Database")
series_choice = st.sidebar.selectbox(
    "Pilih Series Game:",
    ["Monster Hunter Stories 1", "Monster Hunter Stories 2", "Monster Hunter Stories 3"]
)

# --- Mapping File Berdasarkan Series ---
file_map = {
    "Monster Hunter Stories 1": "MHST_monsties.csv",
    "Monster Hunter Stories 2": "MHST2_monsties.csv", # Ganti dengan nama file csv MHST 2 nanti
    "Monster Hunter Stories 3": "MHST3_monsties.csv"  # Ganti dengan nama file csv MHST 3 nanti
}

file_name = file_map[series_choice]

# --- Load Data ---
try:
    df_monster = pd.read_csv(file_name)
except FileNotFoundError:
    st.sidebar.error(f"Dataset untuk {series_choice} ({file_name}) belum tersedia.")
    st.title(series_choice)
    st.info("Fitur untuk seri ini sedang dalam tahap pengembangan. Silakan pilih 'Monster Hunter Stories 1'.")
    st.stop()

# --- Fungsi Pendukung ---
tendency_map = {1: "Speed", 2: "Power", 3: "Technique"}

# --- Sidebar: Kontrol Pencarian dan Pilih Monster ---
st.sidebar.header(f"Pencarian Monster ({series_choice})")
search_query = st.sidebar.text_input("Cari Monster (Masukkan nama):")
filtered_data = df_monster[df_monster['Monster'].str.contains(search_query, case=False, na=False)] if search_query else df_monster

if filtered_data.empty:
    st.sidebar.warning("Monster tidak ditemukan.")
    st.stop()

monster_name = st.sidebar.selectbox("Pilih Monster:", options=filtered_data['Monster'].unique())

# --- Ambil Data Monster yang Dipilih ---
monster_data = df_monster[df_monster['Monster'] == monster_name].iloc[0]
tendency = tendency_map.get(monster_data.get('Tendency', 0), "Unknown")

# Kategori Stat
stats_basic = ["HP", "Attack", "Defence", "Speed"]
stats_attack = ["Att_Fire", "Att_Water", "Att_Thunder", "Att_Ice", "Att_Dragon"]
stats_resist = ["Res_Fire", "Res_Water", "Res_Thunder", "Res_Ice", "Res_Dragon"]

# Perhitungan Elemen Terkuat/Terlemah
strongest_attack_value = monster_data[stats_attack].max()
strongest_attack_elements = [el.replace('Att_', '') for el, val in monster_data[stats_attack].items() if val == strongest_attack_value]

highest_res_value = monster_data[stats_resist].max()
highest_res_elements = [el.replace('Res_', '') for el, val in monster_data[stats_resist].items() if val == highest_res_value]

weakest_res_value = monster_data[stats_resist].min()
weakest_res_elements = [el.replace('Res_', '') for el, val in monster_data[stats_resist].items() if val == weakest_res_value]

# --- Halaman Utama ---
st.markdown(f"<h1 style='text-align: center; color: #ff4b4b;'>{series_choice} Literatur</h1>", unsafe_allow_html=True)
st.divider()

# --- Menu Opsi (Menggunakan Tabs untuk Visual Lebih Modern) ---
# Menggunakan tabs menggantikan selectbox agar navigasinya lebih cepat dan secara visual lebih elegan
tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Monster Description", 
    "💎 Loot", 
    "⚔️ Armor & Weapon Obtained", 
    "🥚 Egg & Habitat"
])

# --- TAB 1: MONSTER DESCRIPTION ---
with tab1:
    st.header(f"Monster: {monster_name}")
    
    col_img, col_desc = st.columns([1, 2])
    with col_img:
        # Menampilkan gambar monster (jika ada)
        image_path = f"Monslist/{monster_name}.webp"
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            # Placeholder jika gambar kosong
            st.info(f"Gambar {monster_name} belum tersedia secara lokal di Monslist/")

    with col_desc:
        st.subheader("Ikhtisar Informasi")
        # Menggunakan st.metric untuk membuat ringkasan yang menarik secara visual
        met1, met2, met3 = st.columns(3)
        met1.metric(label="Tendency", value=tendency)
        met2.metric(label="Elemen Attack Terkuat", value=", ".join(strongest_attack_elements))
        met3.metric(label="Elemen Terlemah", value=", ".join(weakest_res_elements), delta="Kelemahan", delta_color="inverse")
        
        st.write(f"**Resistance Tertinggi**: {', '.join(highest_res_elements)} ({highest_res_value})")

    st.divider()
    st.subheader("Statistik Monster")

    # Membuat 3 Kolom untuk masing-masing klasifikasi chart
    col_stat1, col_stat2, col_stat3 = st.columns(3)

    # 1. Basic Stats
    with col_stat1:
        st.markdown("<h4 style='text-align:center;'>Stat Dasar</h4>", unsafe_allow_html=True)
        fig_basic = create_radar_chart(stats_basic, monster_data[stats_basic], "Basic Stats", "blue")
        st.plotly_chart(fig_basic, use_container_width=True)
        with st.expander("Lihat Angka Stat Dasar"):
            for stat in stats_basic:
                st.write(f"**{stat}:** {monster_data[stat]}")

    # 2. Attack Stats
    with col_stat2:
        st.markdown("<h4 style='text-align:center;'>Attack Element</h4>", unsafe_allow_html=True)
        fig_attack = create_radar_chart(stats_attack, monster_data[stats_attack], "Attack Element", "red")
        st.plotly_chart(fig_attack, use_container_width=True)
        with st.expander("Lihat Angka Attack Element"):
            for stat in stats_attack:
                st.write(f"**{stat.replace('Att_', '')}:** {monster_data[stat]}")

    # 3. Defence Stats
    with col_stat3:
        st.markdown("<h4 style='text-align:center;'>Defence Element</h4>", unsafe_allow_html=True)
        fig_resist = create_radar_chart(stats_resist, monster_data[stats_resist], "Defence Element", "green")
        st.plotly_chart(fig_resist, use_container_width=True)
        with st.expander("Lihat Angka Defence Element"):
            for stat in stats_resist:
                st.write(f"**{stat.replace('Res_', '')}:** {monster_data[stat]}")

# --- TAB 2: LOOT ---
with tab2:
    st.header(f"Loot dari {monster_name}")
    st.info("Informasi item loot atau material drop akan ditambahkan pada update selanjutnya.")

# --- TAB 3: ARMOR & WEAPON OBTAINED ---
with tab3:
    st.header(f"Armor & Weapon dari {monster_name}")
    st.info("Informasi panduan senjata dan armor akan ditambahkan pada update selanjutnya.")

# --- TAB 4: EGG & HABITAT ---
with tab4:
    st.header(f"Telur dan Habitat {monster_name}")
    st.info("Informasi pola telur, lokasi sarang, dan cara retret akan ditambahkan pada update selanjutnya.")
