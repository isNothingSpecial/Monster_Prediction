import streamlit as st
import pandas as pd
import os

df= pd.read_csv('MHST_monsties.csv')
df1 = df.drop(columns=['No'])

# Fungsi rekomendasi (versi lengkap dari sebelumnya)
def recommend_monster_v3(opponent_stats, df1):
    rankings = []
    resistance_values = {
        'Fire': opponent_stats['Res_Fire'],
        'Water': opponent_stats['Res_Water'],
        'Thunder': opponent_stats['Res_Thunder'],
        'Ice': opponent_stats['Res_Ice'],
        'Dragon': opponent_stats['Res_Dragon']
    }
    lowest_resistance = min(resistance_values, key=resistance_values.get)
    for _, row in df1.iterrows():
        monster_stats = row.drop('Monster').to_dict()
        score = 0
        alasan = []
        if opponent_stats['Tendency'] == 2 and monster_stats['Tendency'] == 1:
            score += 10
            alasan.append("Speed counter Power (Tendency)")
        elif opponent_stats['Tendency'] == 3 and monster_stats['Tendency'] == 2:
            score += 10
            alasan.append("Power counter Technique (Tendency)")
        elif opponent_stats['Tendency'] == 1 and monster_stats['Tendency'] == 3:
            score += 10
            alasan.append("Technique counter Speed (Tendency)")
        else:
            score -= 5
            alasan.append("Tidak meng-counter tendency musuh")
        attack_values = {
            'Fire': monster_stats['Att_Fire'],
            'Water': monster_stats['Att_Water'],
            'Thunder': monster_stats['Att_Thunder'],
            'Ice': monster_stats['Att_Ice'],
            'Dragon': monster_stats['Att_Dragon']
        }
        highest_attack_value = attack_values[lowest_resistance]
        score += highest_attack_value
        alasan.append(f"Musuh memiliki resistance terendah terhadap {lowest_resistance},Attack Element ({lowest_resistance}) dari {row['Monster']} = {highest_attack_value}")
        rankings.append((row['Monster'], score, "; ".join(alasan)))
    rankings.sort(key=lambda x: x[1], reverse=True)
    return rankings[:5]

# UI
st.title("Rekomendasi Monster Terbaik")

# Input data lawan
st.sidebar.subheader("Input Statistik Monster Lawan")
opponent_stats = {
    "HP": st.sidebar.number_input("HP", value=5, min_value=0),
    "Attack": st.sidebar.number_input("Attack", value=5, min_value=0),
    "Defence": st.sidebar.number_input("Defence", value=5, min_value=0),
    "Speed": st.sidebar.number_input("Speed", value=5, min_value=0),
    "Att_Fire": st.sidebar.number_input("Attack Fire", value=5, min_value=0),
    "Att_Water": st.sidebar.number_input("Attack Water", value=5, min_value=0),
    "Att_Thunder": st.sidebar.number_input("Attack Thunder", value=5, min_value=0),
    "Att_Ice": st.sidebar.number_input("Attack Ice", value=5, min_value=0),
    "Att_Dragon": st.sidebar.number_input("Attack Dragon", value=5, min_value=0),
    "Res_Fire": st.sidebar.number_input("Resistance Fire", value=5, min_value=0),
    "Res_Water": st.sidebar.number_input("Resistance Water", value=5, min_value=0),
    "Res_Thunder": st.sidebar.number_input("Resistance Thunder", value=5, min_value=0),
    "Res_Ice": st.sidebar.number_input("Resistance Ice", value=5, min_value=0),
    "Res_Dragon": st.sidebar.number_input("Resistance Dragon", value=5, min_value=0),
    "Tendency": st.sidebar.selectbox("Tendency", [1, 2, 3], format_func=lambda x: {1: "Speed", 2: "Power", 3: "Technique"}[x])
}

# Proses Analisis
if st.button("Cari Rekomendasi Monster"):
    rekomendasi = recommend_monster_v3(opponent_stats, df1)
    st.subheader("Hasil Rekomendasi")
    for rank, (monster, score, alasan) in enumerate(rekomendasi, start=1):
        st.markdown(f"**{rank}. {monster}**")
        st.write(f"Score: {score}")
        alasan_lines = alasan.split("; ")
        formatted_alasan = "\n".join(alasan_lines)  # Memisahkan setiap alasan dengan newline
        st.markdown(f"**Alasan:**\n{formatted_alasan}")
