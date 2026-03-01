import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image

# Configurazione Pagina
st.set_page_config(page_title="Soccer Manager Elite", page_icon="⚽", layout="wide")

# Connessione DB
def get_connection():
    conn = sqlite3.connect("societa_calcio.db", check_same_thread=False)
    return conn

# --- INTERFACCIA WEB ---
st.title("🏆 Soccer Manager Elite")
st.markdown("---")

menu = ["🏠 Home", "📋 Rosa Completa", "🔥 Marcatori", "📅 Calendario", "🏆 Risultati"]
scelta = st.sidebar.selectbox("Navigazione", menu)

conn = get_connection()
c = conn.cursor()

if scelta == "🏠 Home":
    st.subheader("Benvenuto nel Portale della Società")
    st.info("Seleziona una voce dal menu a sinistra per vedere i dettagli della stagione.")
    st.image("https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&q=80&w=1000", use_column_width=True)

elif scelta == "📋 Rosa Completa":
    st.header("👥 Rosa Giocatori")
    query = """
        SELECT g.nome, g.cognome, g.n_maglia, g.gol, s.nome as squadra, s.lega, g.foto 
        FROM giocatori g JOIN squadre s ON g.squadra_id = s.id
    """
    df = pd.read_sql(query, conn)
    
    for index, row in df.iterrows():
        col1, col2 = st.columns([1, 4])
        with col1:
            # Se la foto esiste nel cloud la mostra, altrimenti icona standard
            if row['foto'] and os.path.exists(row['foto']):
                st.image(row['foto'], width=100)
            else:
                st.write("👤")
        with col2:
            st.subheader(f"{row['nome']} {row['cognome']} (#{row['n_maglia']})")
            st.write(f"**Squadra:** {row['squadra']} | **Lega:** {row['lega']} | **Gol:** {row['gol']}")
        st.divider()

elif scelta == "🔥 Marcatori":
    st.header("🎯 Top Scorers")
    query = """
        SELECT g.nome || ' ' || g.cognome as Giocatore, s.nome as Squadra, g.gol as Gol 
        FROM giocatori g JOIN squadre s ON g.squadra_id = s.id 
        ORDER BY g.gol DESC
    """
    df_marcatori = pd.read_sql(query, conn)
    st.table(df_marcatori)

elif scelta == "📅 Calendario":
    st.header("📅 Prossime Partite")
    df_cal = pd.read_sql("SELECT data, casa, fuori FROM partite WHERE risultato = '' OR risultato = '-'", conn)
    if not df_cal.empty:
        st.dataframe(df_cal, use_container_width=True)
    else:
        st.write("Nessuna partita in programma.")

elif scelta == "🏆 Risultati":
    st.header("✅ Risultati Recenti")
    df_res = pd.read_sql("SELECT data, casa, risultato, fuori FROM partite WHERE risultato != '' AND risultato != '-'", conn)
    st.dataframe(df_res, use_container_width=True)