import streamlit as st
import pandas as pd

# --- DEKLARASI DATASET CONTOH ---
df= pd.read_csv('MHST_monsties.csv')
df_monster = df.drop(columns=['No'])
df_weapon = pd.read_csv('Weapon Monster Hunter Stories.csv')

def find_weakness(monster_name, df_monster):
    """
    Mengidentifikasi kelemahan elemen monster berdasarkan resistansi terendah dari DataFrame.
    """
    opponent_stats = df_monster[df_monster['Monster'] == monster_name]
    
    if opponent_stats.empty:
        return None, "Monster tidak ditemukan."

    opponent_stats = opponent_stats.iloc[0]

    resistance_values = {
        'Fire': opponent_stats['Res_Fire'],
        'Water': opponent_stats['Res_Water'],
        'Thunder': opponent_stats['Res_Thunder'],
        'Ice': opponent_stats['Res_Ice'],
        'Dragon': opponent_stats['Res_Dragon']
    }
    
    min_res_value = min(resistance_values.values())
    
    kelemahan_elemen = [
        element for element, value in resistance_values.items() if value == min_res_value
    ]
    
    return kelemahan_elemen, opponent_stats

def recommend_weapons(monster_name, df_weapon, df_monster):
    # Mengambil data monster yang dipilih
    kelemahan_elemen, opponent_stats = find_weakness(monster_name, df_monster)
    rekomendasi_senjata = []
    
    # Loop melalui setiap SENJATA
    for index, weapon in df_weapon.iterrows():
        skor = 0
        # Menambahkan skor berdasarkan KECOCOKAN SENJATA dengan kelemahan monster
        # ... (Logika scoring)
        rekomendasi_senjata.append({'senjata': weapon.to_dict(), 'skor': skor})
    
    return sorted(rekomendasi_senjata, key=lambda x: x['skor'], reverse=True)[:10]

# Fungsi baru (rekomendasi monster untuk senjata)
def recommend_monsters(weapon_name, df_weapon, df_monster):
    # Mengambil data senjata yang dipilih
    weapon_stats = df_weapon[df_weapon['Nama Senjata'] == weapon_name].iloc[0]
    rekomendasi_monster = []
    
    # Loop melalui setiap MONSTER
    for index, monster in df_monster.iterrows():
        skor = 0
        
        # Kriteria 1: Kecocokan Skill Senjata dengan Tipe Monster
        tipe_monster_str = monster['Type Monster'].replace(' ', '_').lower() + '_slayer'
        if pd.notna(weapon_stats.get('Skill')) and tipe_monster_str in weapon_stats['Skill'].lower():
            skor += 100 # Bobot bonus untuk slayer skill

        # Kriteria 2: Kecocokan Elemen Senjata dengan Kelemahan Monster
        weapon_element = weapon_stats.get('Elemen')
        if pd.notna(weapon_element):
            # Cek resistansi monster terhadap elemen senjata
            resistance_col = f"Res_{weapon_element.capitalize()}"
            if resistance_col in monster:
                # Semakin rendah resistansi monster, semakin tinggi skornya
                skor += (5 - monster[resistance_col]) * 20 

        # Kriteria 3: Statistik Attack Senjata
        # Skor monster dipengaruhi oleh seberapa kuat serangan senjata
        skor += weapon_stats.get('Attack Max', 0) * 1

        rekomendasi_monster.append({'monster': monster.to_dict(), 'skor': skor})
    
    return sorted(rekomendasi_monster, key=lambda x: x['skor'], reverse=True)[:10]

# --- UI APLIKASI STREAMLIT ---
st.title("Sistem Rekomendasi Senjata MH Stories 1")
st.markdown("""
Aplikasi ini membantu Anda menemukan senjata terbaik untuk melawan monster target.
Pilih monster yang ingin Anda lawan dari daftar di bawah ini.
""")

# Opsi pilihan mode
mode_selection = st.radio(
    "Pilih mode rekomendasi:",
    ('Rekomendasi Senjata untuk Monster', 'Rekomendasi Monster untuk Senjata')
)
    if st.button("Dapatkan Rekomendasi Senjata"):
        if selected_monster:
            with st.spinner('Menganalisis senjata...'):
                recommendations = recommend_weapons(selected_monster, df_weapon, df_monster)
            st.subheader(f"Rekomendasi Senjata untuk Melawan {selected_monster}:")
            if isinstance(recommendations, str):
                st.error(recommendations)
            else:
                for i, item in enumerate(recommendations):
                    weapon = item['senjata']
                    skor = item['skor']
                    with st.expander(f"{i+1}. {weapon['Nama Senjata']}"):
                        st.write(f"**Tipe Senjata:** {weapon['Tipe Senjata']}")
                        st.write(f"**Skor:** {skor:.0f}")
                        st.markdown("---")
                        st.write(f"**Attack Max:** {weapon['Attack Max']}")
                        st.write(f"**Elemen:** {weapon['Elemen']} (Nilai: {weapon['Nilai Elemen']})")
                        st.write(f"**Critical:** {weapon['Critical']}%") 
                        st.write(f"**Skill:** {weapon['Skill']}")

elif mode_selection == 'Rekomendasi Monster untuk Senjata':
    st.header("Rekomendasi Monster untuk Senjata Tertentu")
    weapon_list = df_weapon['Nama Senjata'].tolist()
    selected_weapon = st.selectbox(
        "Pilih senjata yang Anda miliki:",
        options=weapon_list
    )
    if st.button("Dapatkan Rekomendasi Monster"):
        if selected_weapon:
            with st.spinner('Menganalisis monster...'):
                recommendations = recommend_monsters(selected_weapon, df_weapon, df_monster)
            st.subheader(f"Rekomendasi Monster untuk Senjata {selected_weapon}:")
            if isinstance(recommendations, str):
                st.error(recommendations)
            else:
                for i, item in enumerate(recommendations):
                    monster = item['monster']
                    skor = item['skor']
                    with st.expander(f"{i+1}. {monster['Monster']}"):
                        st.write(f"**Tipe Monster:** {monster['Type Monster']}")
                        st.write(f"**Skor:** {skor:.0f}")
                        st.markdown("---")
                        st.write(f"**Tendency:** {monster['Tendency']}")
                        st.write(f"**Resistensi Elemen:**")
                        st.write(f"- Fire: {monster['Res_Fire']} | Water: {monster['Res_Water']}")
                        st.write(f"- Thunder: {monster['Res_Thunder']} | Ice: {monster['Res_Ice']}")
                        st.write(f"- Dragon: {monster['Res_Dragon']}")
