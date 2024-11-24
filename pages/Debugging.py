import streamlit as st
from PIL import Image
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

# Load gambar monster dan statistik
basic_stats_chart = Image.open(f"Basic_Stat/Stat_{monster_name}.png")

basic_stats_chart = Image.open(f"./path/to/Basic_Stat/Stat_{monster_name}.png")
print(f"Path to file: Basic_Stat/Stat_{monster_name}.png")
