import streamlit as st
from supabase import create_client, Client
import requests

# Load secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]
N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]

# Init Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

st.title("🔐 Supabase Login + n8n JWT Test")

# Input fields
email = st.text_input("Email")
password = st.text_input("Passwort", type="password")

if st.button("Login"):
    with st.spinner("Melde an..."):
        try:
            # Login request
            auth = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if auth is None or auth.user is None:
                st.error("Fehler beim Login.")
            else:
                access_token = auth.session.access_token
                st.success("Login erfolgreich!")
                st.code(access_token, language="text")

                st.subheader("JWT an n8n senden")

                # Send token to n8n
                headers = {"Authorization": f"Bearer {access_token}"}

                try:
                    response = requests.post(N8N_WEBHOOK_URL, headers=headers)

                    if response.status_code == 200:
                        st.success("Antwort von n8n erhalten:")
                        st.json(response.json())
                    else:
                        st.error(f"n8n Fehler: {response.status_code}")
                        st.text(response.text)

                except Exception as e:
                    st.error(f"Fehler bei Anfrage an n8n: {e}")

        except Exception as e:
            st.error(f"Login Fehler: {e}")
