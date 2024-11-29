import streamlit as st
from services import register, login

st.title("Red Social - Autenticación")

option = st.selectbox("Elige una opción", ["Sign Up", "Sign In"])

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if option == "Sign Up":
    if st.button("Sign Up"):
        response = register(username, password)
        st.write(response.message)
elif option == "Sign In":
    if st.button("Sign In"):
        response = login(username, password)
        st.write(response.message)