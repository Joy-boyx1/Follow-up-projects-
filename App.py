import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

# ==============================
# LECTURE EXCEL
# ==============================
file_path = "PLANNING.xlsx"

df = pd.read_excel(file_path, sheet_name="DATA")

# Colonnes A,B,C,D
df = df.iloc[:, 0:4]

df.columns = [
    "numero_tache",          # Colonne A
    "designation_tache",     # Colonne B
    "duree_theorique",       # Colonne C
    "antecedents"            # Colonne D
]

# ==============================
# TRAITEMENT ANTECEDENTS
# ==============================
def parse_antecedents(val):
    if pd.isna(val) or str(val).strip() == "-":
        return []
    return [int(x) for x in str(val).split(",")]

df["liste_antecedents"] = df["antecedents"].apply(parse_antecedents)

# ==============================
# CALCUL DES DATES DE DEBUT
# ==============================
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
df["fin"] = df["debut"] + df["duree_theorique"]

# ==============================
# GANTT MATPLOTLIB
# 910 x 400 px
# ==============================
sns.set_style("whitegrid")

fig, ax = plt.subplots(figsize=(9.1, 4), dpi=100)

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
