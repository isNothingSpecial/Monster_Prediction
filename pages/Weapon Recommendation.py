import streamlit as st
import pandas as pd
import os

# --- DEKLARASI DATASET LENGKAP ---
try:
    df_monster = pd.read_csv('MHST_monsties.csv')
    df_weapon = pd.read_csv('Weapon Monster Hunter Stories.csv')
    # Membersihkan kolom 'No' jika ada
    if 'No' in df_monster.columns:
        df_monster = df_monster.drop(columns=['No'])
except FileNotFoundError:
    st.error("File CSV tidak ditemukan. Pastikan 'MHST_monsties.csv' dan 'Weapon Monster Hunter Stories.csv' ada di direktori yang sama.")
    st.stop()


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
    """
    Merekomendasikan senjata terbaik untuk melawan monster tertentu.
    """
    kelemahan_elemen, opponent_stats = find_weakness(monster_name, df_monster)
    if opponent_stats is None:
        return "Monster tidak ditemukan."
    
    # Konversi kolom ke numerik
    for col in ['Attack Max', 'Critical', 'Nilai Elemen']:
        df_weapon[col] = pd.to_numeric(df_weapon[col], errors='coerce').fillna(0).astype(int)

    BOBOT_SKILL_SPESIFIK = 100
    BOBOT_ELEMEN_KELEMAHAN = 50
    BOBOT_ATTACK = 1
    BOBOT_NILAI_ELEMEN = 5
    BOBOT_CRITICAL = 3

    rekomendasi_senjata = []
    
    for _, weapon in df_weapon.iterrows():
        skor = 0
        
        tipe_monster_str = opponent_stats['Type Monster'].replace(' ', '_').lower() + '_slayer'
        if pd.notna(weapon.get('Skill')) and tipe_monster_str in weapon['Skill'].lower():
            skor += BOBOT_SKILL_SPESIFIK

        if pd.notna(weapon.get('Elemen')) and weapon['Elemen'].capitalize() in kelemahan_elemen:
            skor += BOBOT_ELEMEN_KELEMAHAN
            skor += weapon.get('Nilai Elemen', 0) * BOBOT_NILAI_ELEMEN
            
        skor += weapon.get('Attack Max', 0) * BOBOT_ATTACK
        skor += weapon.get('Critical', 0) * BOBOT_CRITICAL

        rekomendasi_senjata.append({'senjata': weapon.to_dict(), 'skor': skor})

    rekomendasi_senjata_sorted = sorted(rekomendasi_senjata, key=lambda x: x['skor'], reverse=True)
    return rekomendasi_senjata_sorted[:10]

def recommend_monsters(weapon_name, df_weapon, df_monster):
    """
    Merekomendasikan monster yang paling rentan terhadap senjata tertentu.
    """
    weapon_stats = df_weapon[df_weapon['Nama Senjata'] == weapon_name]
    if weapon_stats.empty:
        return "Senjata tidak ditemukan."
    weapon_stats = weapon_stats.iloc[0]
    
    rekomendasi_monster = []
    BOBOT_SKILL_SPESIFIK = 100
    BOBOT_ELEMEN_KELEMAHAN = 20
    BOBOT_ATTACK_MAX = 1
    BOBOT_NILAI_ELEMEN = 5
    BOBOT_CRITICAL = 3
    
    for _, monster in df_monster.iterrows():
        skor = 0
        
        weapon_skill = weapon_stats.get('Skill', '').lower()
        tipe_monster_str = monster['Type Monster'].replace(' ', '_').lower()
        if tipe_monster_str in weapon_skill:
            skor += BOBOT_SKILL_SPESIFIK
        
        weapon_element = weapon_stats.get('Elemen')
        if pd.notna(weapon_element):
            res_col = f"Res_{weapon_element.capitalize()}"
            if res_col in monster:
                skor += (5 - monster[res_col]) * BOBOT_ELEMEN_KELEMAHAN
                skor += weapon_stats.get('Nilai Elemen', 0) * BOBOT_NILAI_ELEMEN
        
        skor += weapon_stats.get('Attack Max', 0) * BOBOT_ATTACK_MAX
        skor += weapon_stats.get('Critical', 0) * BOBOT_CRITICAL
        
        rekomendasi_monster.append({'monster': monster.to_dict(), 'skor': skor})

    rekomendasi_monster_sorted = sorted(rekomendasi_monster, key=lambda x: x['skor'], reverse=True)
    return rekomendasi_monster_sorted[:10]


# --- UI APLIKASI STREAMLIT ---
st.title("Sistem Rekomendasi Senjata & Monster")
st.markdown("---")

mode_selection = st.radio(
    "Pilih mode rekomendasi:",
    ('Rekomendasi Senjata untuk Monster', 'Rekomendasi Monster untuk Senjata')
)

if mode_selection == 'Rekomendasi Senjata untuk Monster':
    st.header("Rekomendasi Senjata untuk Mengalahkan Monster Tertentu")
    monster_list = df_monster['Monster'].tolist()
    selected_monster = st.selectbox(
        "Pilih monster lawan:",
        options=monster_list
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
