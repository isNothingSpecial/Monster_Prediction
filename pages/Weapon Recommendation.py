import streamlit as st
import pandas as pd

# --- DEKLARASI DATASET CONTOH ---
df= pd.read_csv('MHST_monsties.csv')
df1 = df.drop(columns=['No'])
df2 = pd.read_csv('Weapon Monster Hunter Stories.csv')

# --- FUNGSI REKOMENDASI SENJATA ---

def find_weakness(monster_name, df1):
    opponent_stats = df1[df1['Monster'] == monster_name].iloc[0]

    resistance_values = {
        'Fire': opponent_stats['Res_Fire'],
        'Water': opponent_stats['Res_Water'],
        'Thunder': opponent_stats['Res_Thunder'],
        'Ice': opponent_stats['Res_Ice'],
        'Dragon': opponent_stats['Res_Dragon']
    }
    min_res_value = min(resistance_values.values())
    weak_elements = [el for el, val in resistance_values.items() if val == min_res_value]
    
    return weak_elements, opponent_stats

def recommend_weapons(monster_name, df2, df1):
    kelemahan_elemen, opponent_stats = find_weakness(monster_name, df1)
    
    # Gunakan DataFrame penuh tanpa filter rarity
    filtered_df2 = df2.copy()

    # Perbaikan: Konversi Tipe Data Numerik pada DataFrame yang sudah difilter
    for col in ['Attack Max', 'Critical', 'Nilai Elemen']:
        filtered_df2[col] = pd.to_numeric(filtered_df2[col], errors='coerce').fillna(0).astype(int)

    # Definisikan bobot untuk setiap kriteria
    BOBOT_SKILL_SPESIFIK = 100
    BOBOT_ELEMEN_KELEMAHAN = 50
    BOBOT_ATTACK = 1
    BOBOT_NILAI_ELEMEN = 5
    
    rekomendasi_senjata = []
    
    for index, weapon in filtered_df2.iterrows():
        skor = 0
        
        tipe_monster_str = opponent_stats['Type Monster'].replace(' ', '_').lower() + '_slayer'
        if pd.notna(weapon.get('Skill')) and tipe_monster_str in weapon['Skill'].lower():
            skor += BOBOT_SKILL_SPESIFIK

        if pd.notna(weapon.get('Elemen')) and weapon['Elemen'].capitalize() in kelemahan_elemen:
            skor += BOBOT_ELEMEN_KELEMAHAN
            skor += weapon.get('Nilai Elemen', 0) * BOBOT_NILAI_ELEMEN

        skor += weapon.get('Attack Max', 0) * BOBOT_ATTACK
        
        rekomendasi_senjata.append({'senjata': weapon.to_dict(), 'skor': skor})

    rekomendasi_senjata_sorted = sorted(rekomendasi_senjata, key=lambda x: x['skor'], reverse=True)
    return rekomendasi_senjata_sorted[:10]

# --- UI APLIKASI STREAMLIT ---
st.title("Sistem Rekomendasi Senjata MH Stories 1")

st.markdown("""
Aplikasi ini membantu Anda menemukan senjata terbaik untuk melawan monster target.
Pilih monster yang ingin Anda lawan.
""")

monster_list = df1['Monster'].tolist()
selected_monster = st.selectbox(
    "Pilih monster lawan:",
    options=monster_list
)

if st.button("Dapatkan Rekomendasi Senjata"):
    if selected_monster:
        with st.spinner('Menganalisis senjata...'):
            recommendations = recommend_weapons(selected_monster, df2, df1)

        st.subheader(f"Rekomendasi Senjata untuk Melawan {selected_monster}:")
        
        for i, item in enumerate(recommendations):
            weapon = item['senjata']
            skor = item['skor']

            # Cek evolusi
            is_evolution = pd.notna(weapon['Prasyarat Evolusi'])
            prasyarat_text = f"Evolusi dari: **{weapon['Prasyarat Evolusi']}**" if is_evolution else "Senjata dasar"

            with st.expander(f"{i+1}. {weapon['Nama Senjata']}"):
                st.write(f"**Tipe Senjata:** {weapon['Tipe Senjata']}")
                st.write(f"**Tingkat Kelangkaan (Rarity):** {weapon['Rarity']}")
                st.write(f"**Rekomendasi ini adalah:** {prasyarat_text}")
                st.write(f"**Skor:** {skor:.0f}")

                # Detail statistik untuk transparansi
                st.markdown("---")
                st.write(f"**Attack Max:** {weapon['Attack Max']}")
                st.write(f"**Elemen:** {weapon['Elemen']} (Nilai: {weapon['Nilai Elemen']})")
                st.write(f"**Critical:** {weapon['Critical']}%")
                st.write(f"**Skill:** {weapon['Skill']}")
