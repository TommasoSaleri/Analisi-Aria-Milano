import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import streamlit as st
import folium
from streamlit_folium import st_folium
from data_processing import create_database
import os

# Controllo se esiste già il database elaborato; in caso contrario, richiamo la funzione per crearlo
if not os.path.exists("dati.json"):
    create_database()


@st.cache_data
def load_data():
    # carico i dati dal file json e preparo il dataframe
    try:
        # apro il file json in modalità lettura
        with open("dati.json", "r", encoding="utf8") as file:
            dati_json = json.load(file)

        #converto i dati in un dataframe pandas
        df = pd.DataFrame(dati_json)

        # converto la colonna data nel formato datetime gestibile dal sistema
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

        # rimuovo eventuali record con valori mancanti (null)
        df = df.dropna(subset=["valore"])
        return df
    except FileNotFoundError:
        st.error("❌ File 'dati.json' non trovato.")
        return pd.DataFrame()

# eseguo il caricamento dei dati
df = load_data()

# se il dataframe è vuoto, ri-eseguo la creazione del database e del dataframe
if df.empty:
    create_database()
    df = load_data()
    
    # se l'errore persiste, interrompo l'app
    if df.empty:
        st.stop()

# ---------------------------------------------------------
# 1. HEADER E SELEZIONE
# ---------------------------------------------------------

st.title("Analisi Qualità dell'Aria a Milano")

# estraggo la lista univoca degli inquinanti presenti nel dataset per il menu a scelta
inquinanti = sorted(df["inquinante"].unique())
inquinante_scelto = st.selectbox("🔍 Seleziona un inquinante da analizzare", inquinanti)

# ---------------------------------------------------------
# 2. SEZIONE DINAMICA: ESPLORA L'INQUINANTE
# ---------------------------------------------------------

# dizionario contenente le informazioni per ogni inquinante
descrizioni = {
    "C6H6": """
**COS'È:** Il benzene è un VOC (Composto Organico Volatile). Evapora facilmente e si disperde nell’aria. Molti VOC sono tossici e cancerogeni.

**CAUSE:** Traffico veicolare, Raffinerie e industrie chimiche, Processi industriali.

**EFFETTI SULL'UOMO:**
- *Breve termine:* Mal di testa, nausea, irritazioni.
- *Cronici:* Danni al midollo osseo e tumori del sangue.

**EFFETTI AMBIENTALI:** Contaminazione di acque (tossicità acquatica), suolo (ridotta fertilità) e aria (danni ai tessuti vegetali).

**GRUPPI A RISCHIO:** Bambini, anziani e lavoratori del settore chimico/petrolifero.
""",
    "CO_8h": """
**COS’È:** Concentrazione di monossido di carbonio misurata nell'arco di 8 ore. Gas incolore, inodore e insapore. È un inquinante primario altamente tossico che riduce il trasporto di ossigeno nel sangue.

**CAUSE:** Traffico veicolare, Riscaldamento domestico, Centrali termiche.

**EFFETTI SULL’UOMO:**
- *Breve termine:* Vertigini, nausea, confusione. Ad alte dosi può essere letale.
- *Cronici:* Problemi cardiovascolari per formazione di carbossiemoglobina.

**EFFETTI AMBIENTALI:** Contribuisce indirettamente alla formazione di ozono troposferico e smog urbano.

**GRUPPI A RISCHIO:** Persone con malattie cardiovascolari, anziani, bambini e donne in gravidanza.
""",
    "NO2": """
**COS’È:** Gas incolore con odore pungente. Inquinante sia primario che secondario, contribuisce a smog e piogge acide.

**CAUSE:** Traffico veicolare, Centrali termiche, Attività agricole.

**EFFETTI SULL’UOMO:**
- *Breve termine:* Irritazione vie respiratorie, tosse e difficoltà respiratoria.
- *Cronici:* Peggioramento asma e riduzione funzionalità polmonare.

**EFFETTI AMBIENTALI:** Formazione di smog fotochimico e piogge acide che danneggiano foreste e acque.

**GRUPPI A RISCHIO:** Bambini, anziani e soggetti asmatici.
""",
    "SO2": """
**COS’È:** Gas incolore, pungente e irritante. Prodotto principalmente dalla combustione di combustibili contenenti zolfo.

**CAUSE:** Combustione di carbone e petrolio, Raffinerie e produzione carta, Riscaldamento.

**EFFETTI SULL’UOMO:**
- *Breve termine:* Irritazione occhi e gola, tosse.
- *Cronici:* Bronchite cronica e aumento del rischio cardiovascolare.

**EFFETTI AMBIENTALI:** Principale responsabile delle piogge acide; riduce la biodiversità acquatica.

**GRUPPI A RISCHIO:** Bambini, anziani e persone con patologie respiratorie.
""",
    "O3": """
**COS’È:** Inquinante secondario al livello del suolo (smog), mentre in alta atmosfera protegge dai raggi UV. È un gas bluastro e pungente.

**CAUSE:** Reazioni chimiche tra NOx e VOC in presenza di forte luce solare (tipico in estate).

**EFFETTI SULL’UOMO:**
- *Breve termine:* Irritazione a gola e occhi, tosse.
- *Cronici:* Ridotta funzionalità polmonare e peggioramento patologie croniche.

**EFFETTI AMBIENTALI:** Riduce la crescita delle piante e danneggia i materiali (gomme, vernici).

**GRUPPI A RISCHIO:** Bambini e persone che svolgono attività fisica all'aperto.
""",
    "PM10": """
**COS’È:** Particelle solide/liquide con diametro ≤ 10μm. Penetrano nelle prime vie respiratorie.

**CAUSE:** Traffico, Riscaldamento a combustibili fossili, Processi industriali.

**EFFETTI SULL’UOMO:**
- *Breve termine:* Tosse e irritazione.
- *Cronici:* Bronchite cronica, malattie cardiovascolari e aumento della mortalità.

**EFFETTI AMBIENTALI:** Riduzione visibilità (smog) e alterazione chimica del suolo per deposizione.

**GRUPPI A RISCHIO:** Anziani, bambini e cardiopatici.
""",
    "PM25": """
**COS’È:** Particolato ultrafine (diametro ≤ 2,5μm). Estremamente pericoloso perché penetra fino agli alveoli polmonari e nel sangue.

**CAUSE:** Traffico, Riscaldamento, Centrali termiche e industria.

**EFFETTI SULL’UOMO:**
- *Breve termine:* Difficoltà respiratoria e affaticamento.
- *Cronici:* Infarti, mortalità precoce, asma grave.

**EFFETTI AMBIENTALI:** Smog denso, piogge acide e alterazione della fertilità del suolo.

**GRUPPI A RISCHIO:** Tutti i soggetti fragili e lavoratori esposti a traffico intenso.
"""
}

# mostro un riquadro espandibile con le informazioni relative all'inquinante selezionato
with st.expander(f"📖 Focus Inquinante: {inquinante_scelto}", expanded=True):
    info = descrizioni.get(inquinante_scelto, "Informazioni non disponibili per questo inquinante.")
    st.markdown(info)

# ---------------------------------------------------------
# 3. MAPPA DELLE STAZIONI
# ---------------------------------------------------------

st.subheader("📍 Localizzazione delle stazioni")

# estraggo le coordinate geografiche univoche per le stazioni che misurano l'inquinante scelto

# estraiamo solo le righe in cui la colonna "inquinante" corrisponde a quello scelto e la copiamo per evitare di modificare i dati
df_coord = df[df["inquinante"] == inquinante_scelto][["nome_stazione", "coordinate"]].copy()

# estraiamo da ogni cella della colonna "coordinate" latitudine e longitudine tramite la funzione lambada
df_coord["lon"] = df_coord["coordinate"].apply(lambda x: x[0])
df_coord["lat"] = df_coord["coordinate"].apply(lambda x: x[1])

# dataframe pulito con nome delle stazioni e coordinate estratte (no duplicati)
df_coord = df_coord[["nome_stazione", "lat", "lon"]].drop_duplicates()

def crea_mappa(data):
    # creazione mappa base centrata sulla media delle coordinate
    m = folium.Map(location=[data["lat"].mean(), data["lon"].mean()], zoom_start=11, tiles="cartodbpositron", dragging=False, zoom_control=True, scrollWheelZoom=False, doubleClickZoom=False)

    # aggiungo un marker per ogni stazione trovata
    for i in range(len(data)):
        riga_corrente = data.iloc[i]
        latitudine = riga_corrente["lat"]
        longitudine = riga_corrente["lon"]
        nome = riga_corrente["nome_stazione"]

        folium.Marker(
            location=[latitudine, longitudine],
            popup=nome,
            tooltip=nome,
            icon=folium.Icon(color="darkblue", icon="cloud", icon_color="white")
        ).add_to(m)
    return m

# visualizzo la mappa nell'interfaccia
st_folium(crea_mappa(df_coord), width=700, height=400, returned_objects=[])
st.divider()

# ---------------------------------------------------------
# 4. ANALISI TEMPORALE
# ---------------------------------------------------------

st.header(f"Andamento storico: {inquinante_scelto}")

# raggruppo i dati per anno calcolando il valore medio dell'inquinante
df_anno = df[df["inquinante"] == inquinante_scelto].groupby("anno")["valore"].mean().reset_index()

# grafico a linee per mostrare l'evoluzione negli anni

# cornice del grafico (spazio dedicato, fig1) e grafico (assi e etichette, ax1)
fig1, ax1 = plt.subplots(figsize=(10, 4))
sb.lineplot(data=df_anno, x="anno", y="valore", marker="o", color="#156D96", ax=ax1)

#aggiungo linee orizzontali al grafico
ax1.grid(axis='y', linestyle='-', alpha=0.7)

ax1.set_ylabel("µg/m³")
st.pyplot(fig1)

# Logica Trend
# 1. primo valore della serie (l'inizio del periodo)
valore_iniziale = df_anno["valore"].iloc[0]

# 2. ultimo valore della serie (la fine del periodo)
valore_finale = df_anno["valore"].iloc[-1]

# 3. calcolo variazione percentuale
variazione = ((valore_finale - valore_iniziale) / valore_iniziale) * 100

# 4. Confrontiamo i due valori
if valore_finale < valore_iniziale:
    trend = f"MIGLIORAMENTO ({variazione:.1f}%)"
    color = "green"
else:
    trend = f"PEGGIORAMENTO (+{variazione:.1f}%)"
    color = "red"

# stampo lo stato del trend con formattazione colorata
st.markdown(f"Stato: <span style='color:{color}'>**{trend}**</span> dal {df_anno['anno'].min()} al {df_anno['anno'].max()}", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 5. CLASSIFICA STAZIONI
# ---------------------------------------------------------

st.header("Classifica Criticità")

# calcolo la media storica per ogni singola stazione
df_staz = df[df["inquinante"] == inquinante_scelto].groupby("nome_stazione")["valore"].mean().reset_index()

# seleziono le 5 stazioni con i valori medi più alti
top5 = df_staz.sort_values(by="valore", ascending=False).head(5)

# organizzo la visualizzazione in due colonne
col1, col2 = st.columns([3, 2])

with col1:
    # grafico a barre orizzontali per la classifica
    fig2, ax2 = plt.subplots(figsize=(8, 6))

    # calcolo la larghezza delle barre in base agli elementi disposti
    if len(top5) >= 3:
        w = 0.7
    else:
        w = 0.3
    
    sb.barplot(
        data=top5, 
        x="valore", 
        y="nome_stazione", 
        palette="Blues_r", 
        ax=ax2,
        width=w
    )
    
    ax2.set_title("Stazioni con media più alta")
    ax2.set_xlabel("Valore medio (µg/m³)")
    ax2.set_ylabel("")

    # rimuovo bordi del grafico
    sb.despine(left=True, bottom=True)
    
    st.pyplot(fig2)

with col2:
    # tabella numerica dei dati medi
    st.write("### Dati medi")
    st.dataframe(top5.rename(columns={"nome_stazione": "Stazione", "valore": "Media (µg/m³)"}).style.format({"Media (µg/m³)": "{:.2f}"}), hide_index=True)

# ---------------------------------------------------------
# 6. DETTAGLIO ANNUALE
# ---------------------------------------------------------

st.header("📅 Dettaglio annuale")

# 1. Selezione dell'anno
# filtro gli anni disponibili per l'inquinante selezionato
anni_disponibili = sorted(df[df["inquinante"] == inquinante_scelto]["anno"].unique(), reverse=True)
anno_scelto = st.selectbox("Seleziona l'anno da analizzare", anni_disponibili)

# 2. Selezione della stazione
# filtro le stazioni che hanno registrato dati per quell'inquinante in quell'anno specifico
stazioni_disponibili = sorted(df[(df["inquinante"] == inquinante_scelto) & (df["anno"] == anno_scelto)]["nome_stazione"].unique())
stazione_scelta = st.selectbox("Seleziona stazione per il dettaglio", stazioni_disponibili)

# 3. estraggo i dati giornalieri per la combinazione scelta
df_focus = df[
    (df["anno"] == anno_scelto) & 
    (df["nome_stazione"] == stazione_scelta) & 
    (df["inquinante"] == inquinante_scelto)
].sort_values("data")

# 4. Visualizzazione del grafico
if not df_focus.empty:
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    sb.lineplot(data=df_focus, x="data", y="valore", color="#156D96", ax=ax3)
    ax3.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax3.set_title(f"Andamento giornaliero {inquinante_scelto} - {stazione_scelta} ({anno_scelto})")
    ax3.set_ylabel("µg/m³")
    st.pyplot(fig3)
else:
    st.warning(f"Dati non disponibili per la stazione {stazione_scelta} nell'anno {anno_scelto}.")