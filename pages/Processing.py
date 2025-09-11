import streamlit as st
import pandas as pd
import os

df= pd.read_csv('MHST_monsties.csv')
df1 = df.drop(columns=['No'])

# Tambahkan kolom 'Image_Path'
df1['Image_Path'] = df1['Monster'].apply(lambda x: f'Monslist/{x}.webp')

# --- FUNGSI REKOMENDASI (SAMA SEPERTI SEBELUMNYA) ---
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

    tendency_map = {1: 'Speed', 2: 'Power', 3: 'Technique'}
    opponent_tendency = tendency_map.get(opponent_stats['Tendency'])
    
    if opponent_tendency == 'Speed':
        counter_tendency = 'Technique'
    elif opponent_tendency == 'Technique':
        counter_tendency = 'Power'
    else:
        counter_tendency = 'Speed'
        
    return weak_elements, counter_tendency, opponent_stats

def recommend_monsties(monster_name, df1):
    try:
        weak_elements, counter_tendency, _ = find_weakness(monster_name, df1)
    except IndexError:
        return "Monster not found."

    tendency_map = {'Speed': 1, 'Power': 2, 'Technique': 3}
    
    counter_monsties = df1[df1['Tendency'] == tendency_map[counter_tendency]]
    
    recom_list = []
    
    for weak_el in weak_elements:
        attack_col = f'Att_{weak_el}'
        
        if attack_col in counter_monsties.columns:
            sorted_monsties = counter_monsties.sort_values(by=attack_col, ascending=False)
            
            for _, monstie in sorted_monsties.head(3).iterrows():
                recom_list.append({
                    'Monster': monstie['Monster'],
                    'Attack Element': weak_el,
                    'Attack Value': monstie[attack_col],
                    'Tendency': counter_tendency
                })
    
    unique_recoms = pd.DataFrame(recom_list).drop_duplicates(subset=['Monster']).to_dict('records')
    
    final_recoms = sorted(unique_recoms, key=lambda x: x['Attack Value'], reverse=True)
    
    if not final_recoms:
        return "No suitable monsties found."
    
    return final_recoms

# --- UI APLIKASI STREAMLIT ---
st.title("Monster Hunter Stories: Sistem Rekomendasi Monstie")

st.markdown("""
Aplikasi ini membantu Anda menemukan monster pendamping (Monstie) terbaik untuk melawan monster target.
Pilih monster yang ingin Anda lawan dari daftar di bawah ini.
""")

# Mendapatkan daftar nama monster dari DataFrame untuk dropdown
monster_list = df1['Monster'].tolist()

# Dropdown untuk memilih monster
selected_monster = st.selectbox(
    "Pilih monster lawan:",
    options=monster_list
)

# Tombol untuk menjalankan rekomendasi
if st.button("Dapatkan Rekomendasi"):
    if selected_monster:
        with st.spinner('Menganalisis kelemahan monster...'):
            recommendations = recommend_monsties(selected_monster, df1)
        
        st.subheader(f"Rekomendasi untuk Melawan {selected_monster}:")
        
        if isinstance(recommendations, str):
            st.error(recommendations)
        else:
            for i, recom in enumerate(recommendations):
                # Dapatkan path gambar dari DataFrame
                image_path = df1[df1['Monster'] == recom['Monster']]['Image_Path'].iloc[0]
            # Menggunakan expander untuk tampilan yang lebih rapi
            for i, recom in enumerate(recommendations):
                with st.expander(f"{i+1}. {recom['Monster']}"):
                    st.image(image_path, width=150)
                    st.write(f"**Tendensi yang direkomendasikan:** {recom['Tendency']}")
                    st.write(f"**Elemen serangan terbaik:** {recom['Attack Element']}")
                    st.write(f"**Nilai serangan:** {recom['Attack Value']}")
                    st.markdown("---")
                    st.write("Monster ini memiliki serangan yang kuat dan cocok secara strategi.")
