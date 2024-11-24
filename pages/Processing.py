import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from streamlit_webrtc import webrtc_streamer

df = pd.read_csv('data_will_model.csv')

scaler = RobustScaler()
numerical_cols = ['song_popularity','song_duration_min', 'danceability',
                 'energy', 'loudness','speechiness','time_signature','audio_mode','tempo_category_numeric']
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

# Pisahkan fitur dan target
X = df.drop('song_popularity', axis=1)  # Fitur
y = df['song_popularity']  # Target

# Membagi data menjadi data latih dan data uji
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Membuat model Random Forest Regressor
model = RandomForestRegressor(n_estimators=100, random_state=42)

# Melatih model
model.fit(X_train, y_train)


# Streamlit app
st.title('Song Popularity Prediction App')

st.header('Input the song features to predict its popularity')

# Input widgets untuk user input
song_duration_min = st.number_input('Song Duration (minutes)', min_value=0.0, max_value=10.0, step=0.01)
danceability = st.number_input('Danceability', min_value=0.0, max_value=1.0, step=0.01)
energy = st.number_input('Energy', min_value=0.0, max_value=1.0, step=0.01)
loudness = st.slider('Loudness (dB)', min_value=-60.0, max_value=0.0, step=0.1)
audio_mode = st.selectbox('Audio Mode', [0, 1])  
speechiness = st.number_input('Speechiness', min_value=0.0, max_value=1.0, step=0.01)
key_selected = st.selectbox('Key', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]) 
time_selected = st.selectbox('Time Signature', [0, 1, 2, 3, 4, 5, 6]) 
tempo_selected = st.selectbox('Tempo', [0, 1, 2, 3, 4, 5]) 

# Menggabungkan semua input ke dalam satu list
input_data = [song_duration_min, danceability, energy, loudness, audio_mode, speechiness, key_selected, time_selected, tempo_selected]
             

# Tombol untuk melakukan prediksi
if st.button('Predict Popularity'):
    # Konversi input data ke numpy array dan reshaped untuk prediksi
    input_array = np.array(input_data).reshape(1, -1)
    
    # Standarisasi input
    input_array_scaled = scaler.transform(input_array)
    
    # Melakukan prediksi
    predicted_popularity = model.predict(input_array_scaled)[0]

    prediksi_positif = np.abs(predicted_popularity) * 100
    prediksi_positif_int = prediksi_positif.astype(int)
    st.write(f'Song Popularity: {prediksi_positif_int}')

