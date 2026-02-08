import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("Planning - Diagrammes de Gantt Toggle")

# ------------------------
# Upload fichier
# ------------------------
fichier = st.file_uploader("📂 Charger le fichier PLANNING.xlsx", type=["xlsx"])

# ------------------------
# Initialiser l'état des boutons
# ------------------------
if "show_gantt_theorique" not in st.session_state:
    st.session_state.show_gantt_theorique = False

if "show_gantt_reel" not in st.session_state:
    st.session_state.show_gantt_reel = False

# ------------------------
# Affichage conditionnel
# ------------------------
if fichier is not None:
    df = pd.read_excel(fichier, sheet_name="DATA")
    df = df.iloc[:, 0:5]
    df.columns = ["numero_tache", "designation_tache", "duree_theorique", "antecedents", "duree_reel"]

    # Traiter les antécédents
    def parse_antecedents(val):
        if pd.isna(val) or str(val).strip() == "-":
            return []
        antecedents = []
        for x in str(val).split("-"):
            x = x.strip()
            if x.isdigit():
                antecedents.append(int(x))
        return antecedents

    df["liste_antecedents"] = df["antecedents"].apply(parse_antecedents)

    # Calcul début
    debut_dict = {}
    for _, row in df.iterrows():
        tache = row["numero_tache"]
        preds = row["liste_antecedents"]
        if len(preds) == 0:
            debut_dict[tache] = 0
        else:
            debut_dict[tache] = max(
                debut_dict[p] + df.loc[df["numero_tache"] == p, "duree_theorique"].values[0]
                for p in preds
            )

    df["debut"] = df["numero_tache"].map(debut_dict)
    df_plot = df[::-1]  # inverse l'ordre pour première tâche en haut

    sns.set_style("whitegrid")
    fig_width = 12
    fig_height = max(4, len(df)*0.3)

    # --------------------------
    # Bouton Gantt Durée théorique
    # --------------------------
    if st.button("📊 Afficher / Masquer Gantt - Durée théorique"):
        st.session_state.show_gantt_theorique = not st.session_state.show_gantt_theorique

    if st.session_state.show_gantt_theorique:
        st.subheader("Diagramme de Gantt - Durée théorique")
        fig1, ax1 = plt.subplots(figsize=(fig_width, fig_height), dpi=100)
        ax1.barh(
            y=df_plot["designation_tache"],
            width=df_plot["duree_theorique"],
            left=df_plot["debut"],
            height=0.6,
            color=sns.color_palette("tab20", n_colors=len(df_plot))
        )
        ax1.set_xlabel("Temps")
        ax1.set_ylabel("Tâches")
        ax1.set_title("Durée théorique")
        plt.tight_layout()
        st.pyplot(fig1)

    # --------------------------
    # Bouton Gantt Durée réel
    # --------------------------
    if st.button("📊 Afficher / Masquer Gantt - Durée réel"):
        st.session_state.show_gantt_reel = not st.session_state.show_gantt_reel

    if st.session_state.show_gantt_reel:
        st.subheader("Diagramme de Gantt - Durée réel")
        fig2, ax2 = plt.subplots(figsize=(fig_width, fig_height), dpi=100)
        ax2.barh(
            y=df_plot["designation_tache"],
            width=df_plot["duree_reel"],
            left=df_plot["debut"],
            height=0.6,
            color=sns.color_palette("tab20", n_colors=len(df_plot))
        )
        ax2.set_xlabel("Temps")
        ax2.set_ylabel("Tâches")
        ax2.set_title("Durée réel")
        plt.tight_layout()
        st.pyplot(fig2)

else:
    st.info("Veuillez uploader votre fichier Excel PLANNING.xlsx pour générer les Gantt.")
