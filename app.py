import streamlit as st
import requests

st.title("🔐 Supabase Login → JWT → n8n Call (ohne supabase-py)")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]
N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]

email = st.text_input("Email")
password = st.text_input("Passwort", type="password")


def supabase_login(email, password):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "password": password,
    }
    return requests.post(url, headers=headers, json=payload)


if st.button("Login"):
    if not email or not password:
        st.warning("Bitte Email und Passwort eingeben.")
        st.stop()

    with st.spinner("Authentifiziere über Supabase…"):
        response = supabase_login(email, password)

    if response.status_code != 200:
        st.error(f"❌ Login fehlgeschlagen: {response.text}")
        st.stop()

    data = response.json()
    jwt = data.get("access_token")

    st.success("Login erfolgreich!")
    st.code(jwt, language="text")

    st.subheader("📡 Sende JWT an n8n")

    headers = {"Authorization": f"Bearer {jwt}"}

    n8n_response = requests.post(N8N_WEBHOOK_URL, headers=headers)

    if n8n_response.status_code == 200:
        st.success("Antwort von n8n:")
        st.json(n8n_response.json())
    else:
        st.error(f"n8n Fehler: {n8n_response.status_code}")
        st.text(n8n_response.text)
