import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("Planning - Diagramme de Gantt interactif")

# ------------------------
# Upload fichier
# ------------------------
fichier = st.file_uploader("📂 Charger le fichier PLANNING.xlsx", type=["xlsx"])

# Zoom interactif
zoom = st.slider("Zoom / taille du Gantt", 0.25, 2.0, 1.0, 0.05)  # on peut réduire à 0.25 pour tout voir

if fichier is not None:
    df = pd.read_excel(fichier, sheet_name="DATA")
    df = df.iloc[:, 0:4]
    df.columns = ["numero_tache", "designation_tache", "duree_theorique", "antecedents"]

    # --------------------------
    # Traiter les antécédents
    # --------------------------
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

    # --------------------------
    # Calcul début
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
    # Gantt inversé + zoom
    # --------------------------
    sns.set_style("whitegrid")
    
    # Hauteur automatique selon nb tâches et zoom, largeur fixe
    fig_height = max(4, len(df)*0.3) * zoom
    fig_width = 12  # largeur fixe pour tenir dans la page
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=100)

    df_plot = df[::-1]  # inverse l'ordre pour première tâche en haut

    ax.barh(
        y=df_plot["designation_tache"],
        width=df_plot["duree_theorique"],
        left=df_plot["debut"],
        height=0.6,
        color=sns.color_palette("tab20", n_colors=len(df_plot))
    )

    ax.set_xlabel("Temps")
    ax.set_ylabel("Tâches")
    ax.set_title("Diagramme de Gantt")
    plt.tight_layout()
    st.pyplot(fig)

    # --------------------------
    # Bouton pour "Zoom complet"
    # --------------------------
    if st.button("📌 Afficher tout (Zoom automatique)"):
        zoom_auto = 4 / max(1, len(df)*0.3)  # ajuste le zoom pour tout faire tenir dans 4 pouces de hauteur
        fig, ax = plt.subplots(figsize=(fig_width, 4), dpi=100)
        ax.barh(
            y=df_plot["designation_tache"],
            width=df_plot["duree_theorique"],
            left=df_plot["debut"],
            height=0.6,
            color=sns.color_palette("tab20", n_colors=len(df_plot))
        )
        ax.set_xlabel("Temps")
        ax.set_ylabel("Tâches")
        ax.set_title("Diagramme de Gantt - Vue complète")
        plt.tight_layout()
        st.pyplot(fig)

else:
    st.info("Veuillez uploader votre fichier Excel PLANNING.xlsx pour générer le Gantt.")
