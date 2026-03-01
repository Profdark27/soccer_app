import streamlit as st
import sqlite3
import pandas as pd
import os
import hashlib
from PIL import Image

# Configurazione Pagina
st.set_page_config(page_title="Soccer Manager PRO Web", page_icon="⚽", layout="wide")

# --- FUNZIONE SICUREZZA ---
def verifica_hash(password, salt, db_password):
    """Verifica se la password inserita corrisponde all'hash nel DB."""
    test_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return test_hash == db_password

def get_connection():
    return sqlite3.connect("societa_calcio.db", check_same_thread=False)

# --- SESSION STATE PER LOGIN ---
if 'autenticato' not in st.session_state:
    st.session_state['autenticato'] = False
    st.session_state['ruolo'] = None

# --- SIDEBAR NAVIGAZIONE ---
st.sidebar.title("⚽ Menu")
menu = ["🏠 Home", "📋 Rosa", "🔥 Marcatori", "📅 Calendario", "🏆 Risultati", "🔐 Area Riservata"]
scelta = st.sidebar.selectbox("Vai a:", menu)

conn = get_connection()

elif scelta == "🏠 Home":
    st.title("🏆 Soccer Manager Elite - Portale Web")
    st.write("Benvenuto nel sistema di gestione ufficiale.")
    # Nuovo link funzionante
    st.image("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=1000", use_container_width=True)

elif scelta == "📋 Rosa":
    st.header("👥 Rosa Giocatori")
    query = """
        SELECT g.nome, g.cognome, g.n_maglia, g.gol, s.nome as squadra, g.foto 
        FROM giocatori g JOIN squadre s ON g.squadra_id = s.id
    """
    df = pd.read_sql(query, conn)
    
    for _, row in df.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])
            with col1:
                if row['foto'] and os.path.exists(row['foto']):
                    st.image(row['foto'], width=120)
                else:
                    st.title("👤")
            with col2:
                st.subheader(f"{row['nome']} {row['cognome']} (#{row['n_maglia']})")
                st.write(f"**Squadra:** {row['squadra']} | **Gol segnati:** {row['gol']}")

elif scelta == "🔥 Marcatori":
    st.header("🎯 Classifica Marcatori")
    query = """
        SELECT g.nome || ' ' || g.cognome as Giocatore, s.nome as Squadra, g.gol as Gol 
        FROM giocatori g JOIN squadre s ON g.squadra_id = s.id 
        ORDER BY g.gol DESC
    """
    df_m = pd.read_sql(query, conn)
    st.table(df_m)

elif scelta == "📅 Calendario":
    st.header("📅 Prossime Partite")
    df_cal = pd.read_sql("SELECT data as Data, casa as Casa, fuori as Ospite FROM partite WHERE risultato IN ('', '-') ORDER BY id", conn)
    if not df_cal.empty:
        st.dataframe(df_cal, use_container_width=True)
    else:
        st.info("Nessuna partita in programma.")

elif scelta == "🏆 Risultati":
    st.header("✅ Risultati Gare")
    df_res = pd.read_sql("SELECT data as Data, casa as Casa, risultato as Risultato, fuori as Ospite FROM partite WHERE risultato NOT IN ('', '-') ORDER BY id DESC", conn)
    if not df_res.empty:
        st.dataframe(df_res, use_container_width=True)
    else:
        st.info("Nessun risultato registrato.")

elif scelta == "🔐 Area Riservata":
    st.header("Accesso Amministratore")
    
    if not st.session_state['autenticato']:
        with st.form("login_form"):
            user = st.text_input("Username")
            psw = st.text_input("Password", type="password")
            submit = st.form_submit_button("Accedi")
            
            if submit:
                cursor = conn.cursor()
                # Query sicura contro SQL Injection
                cursor.execute("SELECT password, salt, ruolo FROM utenti WHERE username = ?", (user,))
                res = cursor.fetchone()
                
                if res and verifica_hash(psw, res[1], res[0]):
                    st.session_state['autenticato'] = True
                    st.session_state['ruolo'] = res[2]
                    st.rerun()
                else:
                    st.error("Credenziali non valide")
    else:
        st.success(f"Loggato come {st.session_state['ruolo']}")
        if st.button("Logout"):
            st.session_state['autenticato'] = False
            st.rerun()
            
        st.info("💡 In questa versione Web la modifica dati è disabilitata per sicurezza. Usa l'app Desktop per aggiornare il database.")

st.sidebar.markdown("---")
st.sidebar.write("v5.0 Security Edition")