import streamlit as st
from streamlit_webrtc import webrtc_streamer

# Menggunakan HTML dan CSS untuk membuat header dan subheader rata tengah
st.markdown(
    """
    <h1 style='text-align: center;'>KELOMPOK 2</h1>
    <h3 style='text-align: center;'>ENIGMA</h3>
    """, 
    unsafe_allow_html=True
)

# Membuat tiga kolom
col1, col2, col3 = st.columns(3)

# Menampilkan konten di setiap kolom
with col1:
    st.header("Bagus Rahma Aulia Chandra")
    st.write("Ketua Kelompok")

with col2:
    st.header("Athiya Fatihah Akbar")
    st.write("Anggota")

with col3:
    st.header("Debi Bayu Nanda")
    st.write("Anggpta")

st.image("ds.png", use_column_width=True)
