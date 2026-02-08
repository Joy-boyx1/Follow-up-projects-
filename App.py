import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("Planning - Diagrammes de Gantt & Avancement / Contrôle Qualité")

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
if "show_avancement" not in st.session_state:
    st.session_state.show_avancement = False
if "show_controle_qualite" not in st.session_state:
    st.session_state.show_controle_qualite = False

# ------------------------
# Affichage conditionnel
# ------------------------
if fichier is not None:
    df = pd.read_excel(fichier, sheet_name="DATA")
    
    # --------------------------
    # Boutons Gantt & Avancement
    # --------------------------
    if st.button("📊 Afficher / Masquer Gantt - Durée théorique"):
        st.session_state.show_gantt_theorique = not st.session_state.show_gantt_theorique
    if st.button("📊 Afficher / Masquer Gantt - Durée réel"):
        st.session_state.show_gantt_reel = not st.session_state.show_gantt_reel
    if st.button("📈 Afficher l'avancement"):
        st.session_state.show_avancement = not st.session_state.show_avancement
    if st.button("🛠️ Afficher Contrôle Qualité"):
        st.session_state.show_controle_qualite = not st.session_state.show_controle_qualite

    # --------------------------
    # Affichage Gantt Durée théorique
    # --------------------------
    if st.session_state.show_gantt_theorique:
        df_gantt = df.iloc[:, 0:5]
        df_gantt.columns = ["numero_tache", "designation_tache", "duree_theorique", "antecedents", "duree_reel"]

        # Traiter les antécédents
        def parse_antecedents(val):
            if pd.isna(val) or str(val).strip() == "-":
                return []
            return [int(x.strip()) for x in str(val).split("-") if x.strip().isdigit()]
        df_gantt["liste_antecedents"] = df_gantt["antecedents"].apply(parse_antecedents)

        # Calcul début
        debut_dict = {}
        for _, row in df_gantt.iterrows():
            tache = row["numero_tache"]
            preds = row["liste_antecedents"]
            debut_dict[tache] = 0 if len(preds) == 0 else max(debut_dict[p] + df_gantt.loc[df_gantt["numero_tache"] == p, "duree_theorique"].values[0] for p in preds)
        df_gantt["debut"] = df_gantt["numero_tache"].map(debut_dict)
        df_plot = df_gantt[::-1]

        fig1, ax1 = plt.subplots(figsize=(12, max(4, len(df_gantt)*0.3)))
        ax1.barh(y=df_plot["designation_tache"], width=df_plot["duree_theorique"], left=df_plot["debut"], height=0.6,
                 color=sns.color_palette("tab20", n_colors=len(df_plot)))
        ax1.set_xlabel("Temps")
        ax1.set_ylabel("Tâches")
        ax1.set_title("Durée théorique")
        plt.tight_layout()
        st.pyplot(fig1)

    # --------------------------
    # Affichage Gantt Durée réel
    # --------------------------
    if st.session_state.show_gantt_reel:
        df_gantt = df.iloc[:, 0:5]
        df_gantt.columns = ["numero_tache", "designation_tache", "duree_theorique", "antecedents", "duree_reel"]

        # Calcul début
        df_gantt["liste_antecedents"] = df_gantt["antecedents"].apply(lambda val: [] if pd.isna(val) or val=="-" else [int(x.strip()) for x in str(val).split("-") if x.strip().isdigit()])
        debut_dict = {}
        for _, row in df_gantt.iterrows():
            tache = row["numero_tache"]
            preds = row["liste_antecedents"]
            debut_dict[tache] = 0 if len(preds)==0 else max(debut_dict[p] + df_gantt.loc[df_gantt["numero_tache"]==p,"duree_theorique"].values[0] for p in preds)
        df_gantt["debut"] = df_gantt["numero_tache"].map(debut_dict)
        df_plot = df_gantt[::-1]

        fig2, ax2 = plt.subplots(figsize=(12, max(4, len(df_gantt)*0.3)))
        ax2.barh(y=df_plot["designation_tache"], width=df_plot["duree_reel"], left=df_plot["debut"], height=0.6,
                 color=sns.color_palette("tab20", n_colors=len(df_plot)))
        ax2.set_xlabel("Temps")
        ax2.set_ylabel("Tâches")
        ax2.set_title("Durée réel")
        plt.tight_layout()
        st.pyplot(fig2)

    # --------------------------
    # Affichage Avancement
    # --------------------------
    if st.session_state.show_avancement:
        df_av = df.iloc[:, 0:6]
        df_av.columns = ["numero_tache", "designation_tache", "duree_theorique", "antecedents", "duree_reel", "cause_retard"]
        df_av["avancement"] = df_av.apply(lambda x: (x["duree_theorique"]/x["duree_reel"])*100 if x["duree_reel"]>0 else 0, axis=1)
        df_av["Impact chemin critique"] = df_av.apply(lambda x: "Oui" if (x["duree_reel"] + 0)> df_av["duree_theorique"].sum() else "Non", axis=1)
        df_retard = df_av[df_av["avancement"]<100][["designation_tache","avancement","cause_retard","Impact chemin critique"]]
        df_retard = df_retard.rename(columns={"cause_retard":"Cause du retard"})
        if not df_retard.empty:
            st.subheader("Tâches en retard")
            st.dataframe(df_retard.reset_index(drop=True))
        else:
            st.success("Toutes les tâches sont à jour ou en avance !")

    # --------------------------
    # Affichage Contrôle Qualité
    # --------------------------
    if st.session_state.show_controle_qualite:
        # Colonnes B, H, I, J, K → index 1,7,8,9,10
        df_cq = df.iloc[:, [1,7,8,9,10]]
        df_cq.columns = ["Désignation de la tâche","Contrôle qualité","Statut du contrôle","Non-conformité détectée","Action corrective"]
        st.subheader("Contrôle Qualité")
        st.dataframe(df_cq.reset_index(drop=True))

else:
    st.info("Veuillez uploader votre fichier Excel PLANNING.xlsx pour générer les Gantt, l'avancement et le contrôle qualité.")
