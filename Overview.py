import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

## data

df = pd.read_csv('song_data.csv')

df_proc = pd.read_csv('data_will_model.csv')



st.set_page_config(page_title="Homepage",layout="wide")
#side bar
#st.sidebar.header("Segmentasi Pelanggan Produk HNI")
#st.sidebar.image("1835901.jpg")

##layout

# Menggunakan HTML dan CSS untuk membuat header dan subheader rata tengah
st.markdown(
    """
    <h1 style='text-align: center;'>APLIKASI MEMPREDIKSI POPULARITAS LAGU DENGAN MENGGUNAKAN ALGORITMA RANDOM FOREST</h1>
    """, 
    unsafe_allow_html=True
)
st.write('''
        ''')
st.markdown('''Aplikasi adalah berupa alat untuk memprediksi popularitas sebuah lagu dengan menggunakan sebuah variasi algoritma regresi,dan Kali ini,akan menganalisa data popularitas lagu dimana memiliki ranking dari 0-100 dimana apabila 0 adalah mengindikasikan apabila lagu tersebut tidak populer

Berikut adalah data yang akan diolah ''')

st.write(df)
st.markdown('''Data diatas masih berupa RAW data,yang mana nantinya akan diolah melalui beberapa proses antara lain:  
1. Import relevant libraries
2. Set Up the current working directory & Import Dataset
3. Exploratory Data Analysis (EDA)
4. Count Categorical Value
5. Mengubah Nominal Variabel
6. Clean the Dataset
7. Visualizations
8. Scalling
9. Modelling
10. Evaluasi
        
Berikut adalah data yang telah diolah sebelum dilakukannya scalling hingga evaluasi: ''')

st.write(df_proc)
