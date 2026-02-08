import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("Planning - Diagramme de Gantt")

# ==============================
# UPLOAD FICHIER
# ==============================
fichier = st.file_uploader(
    "📂 Charger le fichier PLANNING.xlsx",
    type=["xlsx"]
)

# ==============================
# TRAITEMENT LORSQUE FICHIER UPLOAD
# ==============================
if fichier is not None:

    # Lecture de la feuille DATA
    df = pd.read_excel(fichier, sheet_name="DATA")
    df = df.iloc[:, 0:4]

    # Colonnes en français
    df.columns = [
        "numero_tache",
        "designation_tache",
        "duree_theorique",
        "antecedents"
    ]

    # --------------------------
    # Traitement antécédents
    # --------------------------
    def parse_antecedents(val):
        if pd.isna(val) or str(val).strip() == "-":
            return []
        return [int(x) for x in str(val).split(",")]

    df["liste_antecedents"] = df["antecedents"].apply(parse_antecedents)

    # --------------------------
    # Calcul dates de début
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
    # Diagramme de Gantt
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
