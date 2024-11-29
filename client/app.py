import streamlit as st
from services.auth_client import register, login

st.title("Tweety - Auth")

option = st.selectbox("Choose an option", ["Register", "Login"])

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if option == "Register":
    if st.button("Register"):
        response = register(username, password)
        if response is not None:
            st.write(response.message)
        else:
            st.error("Failed to connect to the authentication server.")
elif option == "Login":
    if st.button("Login"):
        response = login(username, password)
        if response is not None:
            st.write(response.message)
        else:
            st.error("Failed to connect to the authentication server.")