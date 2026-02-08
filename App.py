import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("Planning - Diagramme de Gantt")

# Upload fichier
fichier = st.file_uploader("📂 Charger le fichier PLANNING.xlsx", type=["xlsx"])

if fichier is not None:
    df = pd.read_excel(fichier, sheet_name="DATA")
    df = df.iloc[:, 0:4]
    df.columns = ["numero_tache", "designation_tache", "duree_theorique", "antecedents"]

    # Traitement antécédents séparés par -
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

    # Calcul début des tâches
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

    # --------------------------
    # GANTT inversé + espace entre les tâches
    # --------------------------
    sns.set_style("whitegrid")

    fig, ax = plt.subplots(figsize=(9.1, max(4, len(df)*0.3)), dpi=100)  # Ajuste hauteur selon nb tâches

    # Inverser l'ordre des tâches pour avoir la première en haut
    df_plot = df[::-1]

    # Barres horizontales
    ax.barh(
        y=df_plot["designation_tache"],
        width=df_plot["duree_theorique"],
        left=df_plot["debut"],
        height=0.6,  # hauteur barre + espace
        color=sns.color_palette("tab20", n_colors=len(df_plot))
    )

    ax.set_xlabel("Temps")
    ax.set_ylabel("Tâches")
    ax.set_title("Diagramme de Gantt")
    plt.tight_layout()
    st.pyplot(fig)

else:
    st.info("Veuillez uploader votre fichier Excel PLANNING.xlsx pour générer le Gantt.")
