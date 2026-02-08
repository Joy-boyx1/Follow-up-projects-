import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================
# CONFIG STREAMLIT
# ==============================
st.set_page_config(layout="wide")
st.title("Planning - Diagramme de Gantt")

# ==============================
# UPLOAD FICHIER EXCEL
# ==============================
fichier = st.file_uploader(
    "📂 Charger le fichier PLANNING.xlsx",
    type=["xlsx"]
)

# ==============================
# TRAITEMENT
# ==============================
if fichier is not None:

    # Lecture feuille DATA
    df = pd.read_excel(fichier, sheet_name="DATA")
    df = df.iloc[:, 0:4]  # Colonnes A,B,C,D

    # Colonnes en français
    df.columns = [
        "numero_tache",
        "designation_tache",
        "duree_theorique",
        "antecedents"
    ]

    # --------------------------
    # TRAITEMENT ANTECEDENTS (séparés par -)
    # --------------------------
    def parse_antecedents(val):
        """
        Retourne une liste d'entiers
        '-' seul → []
        plusieurs séparés par '-' → [int,...]
        """
        if pd.isna(val) or str(val).strip() == "-":
            return []
        antecedents = []
        for x in str(val).split("-"):
            x = x.strip()
            if x.isdigit():
                antecedents.append(int(x))
        return antecedents

    df["liste_antecedents"] = df["antecedents"].apply(parse_antecedents)

    # --------------------------
    # CALCUL DEBUT DES TACHES
    # --------------------------
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
    # DIAGRAMME DE GANTT
    # --------------------------
    sns.set_style("whitegrid")

    fig, ax = plt.subplots(figsize=(9.1, 4), dpi=100)  # 910x400 px

    for _, row in df.iterrows():
        ax.barh(
            row["designation_tache"],
            row["duree_theorique"],
            left=row["debut"]
        )

    ax.set_xlabel("Temps")
    ax.set_ylabel("Tâches")
    ax.set_title("Diagramme de Gantt")

    plt.tight_layout()
    st.pyplot(fig)

else:
    st.info("Veuillez uploader votre fichier Excel PLANNING.xlsx pour générer le Gantt.")
