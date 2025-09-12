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

    # Menggunakan .iloc[0] untuk mengakses baris tunggal sebagai Series
    opponent_stats = opponent_stats.iloc[0]

    resistance_values = {
        'Fire': opponent_stats['Res_Fire'],
        'Water': opponent_stats['Res_Water'],
        'Thunder': opponent_stats['Res_Thunder'],
        'Ice': opponent_stats['Res_Ice'],
        'Dragon': opponent_stats['Res_Dragon']
    }
    
    # Menemukan nilai resistansi terendah
    min_res_value = min(resistance_values.values())
    
    # Mengidentifikasi elemen-elemen dengan resistansi terendah
    kelemahan_elemen = [
        element for element, value in resistance_values.items() if value == min_res_value
    ]
    
    return kelemahan_elemen, opponent_stats

def recommend_weapons(monster_name, df_weapon, df_monster):
    """
    Merekomendasikan senjata terbaik untuk melawan monster tertentu dari DataFrame.
    """
    # Menggunakan fungsi helper untuk menemukan kelemahan dan data monster
    kelemahan_elemen, opponent_stats = find_weakness(monster_name, df_monster)
    
    if opponent_stats is None:
        return "Monster tidak ditemukan."

    # Definisikan bobot untuk setiap kriteria
    BOBOT_SKILL_SPESIFIK = 100
    BOBOT_ELEMEN_KELEMAHAN = 50
    BOBOT_ATTACK = 1
    BOBOT_NILAI_ELEMEN = 5

    rekomendasi_senjata = []
    
    # Iterasi melalui setiap baris DataFrame senjata
    for index, weapon in df_weapon.iterrows():
        skor = 0
        
        # Kriteria 1: Skill Spesifik
        tipe_monster_str = opponent_stats['Type Monster'].replace(' ', '_').lower() + '_slayer'
        if pd.notna(weapon.get('Skill')) and tipe_monster_str in weapon['Skill'].lower():
            skor += BOBOT_SKILL_SPESIFIK

        # Kriteria 2: Elemen Kelemahan
        if pd.notna(weapon.get('Elemen')) and weapon['Elemen'].capitalize() in kelemahan_elemen:
            skor += BOBOT_ELEMEN_KELEMAHAN
            skor += weapon.get('Nilai Elemen', 0) * BOBOT_NILAI_ELEMEN

        # Kriteria 3: Statistik Dasar
        skor += weapon.get('Attack Max', 0) * BOBOT_ATTACK

        rekomendasi_senjata.append({'senjata': weapon.to_dict(), 'skor': skor})

    # Urutkan senjata berdasarkan skor
    rekomendasi_senjata_sorted = sorted(rekomendasi_senjata, key=lambda x: x['skor'], reverse=True)
    return rekomendasi_senjata_sorted[:10]

# --- UI APLIKASI STREAMLIT ---
st.title("Sistem Rekomendasi Senjata MH Stories 1")

st.markdown("""
Aplikasi ini membantu Anda menemukan senjata terbaik untuk melawan monster target.
Pilih monster yang ingin Anda lawan dari daftar di bawah ini.
""")

monster_list = df1['Monster'].tolist()
selected_monster = st.selectbox(
    "Pilih monster lawan:",
    options=monster_list
)

if st.button("Dapatkan Rekomendasi Senjata"):
    if selected_monster:
        with st.spinner('Menganalisis senjata...'):
            # Memanggil fungsi dengan nama variabel yang benar
            recommendations = recommend_weapons(selected_monster, df2, df1)

        st.subheader(f"Rekomendasi Senjata untuk Melawan {selected_monster}:")
        for i, item in enumerate(recommendations):
            weapon = item['senjata']
            skor = item['skor']
            
        with st.expander(f"{i+1}. {weapon['Nama Senjata']}"):
             st.write(f"**Tipe Senjata:** {weapon['Tipe Senjata']}")
             st.write(f"**Skor:** {skor:.0f}")

             # Detail statistik untuk transparansi
        st.markdown("---")
        st.write(f"**Attack Max:** {weapon['Attack Max']}")
        st.write(f"**Elemen:** {weapon['Elemen']} (Nilai: {weapon['Nilai Elemen']})")
        st.write(f"**Critical:** {weapon['Critical']}%")
        st.write(f"**Skill:** {weapon['Skill']}")
