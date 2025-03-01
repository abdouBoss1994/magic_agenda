import streamlit as st
import pandas as pd

# -- Configuration de la page --
st.set_page_config(page_title="Consultation du Plan d'Action", layout="wide")

@st.cache_data
def load_data(uploaded_file, file_type):
    """
    Charge les données à partir d'un fichier CSV ou XLSX, 
    puis convertit les colonnes de dates au format datetime si elles existent.
    """
    if file_type == "csv":
        # Adapter si votre séparateur n'est pas la virgule
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
    else:  # "xlsx"
        df = pd.read_excel(uploaded_file)
    
    # Exemple de colonnes à convertir en datetime (adapter à vos noms de colonnes)
    date_cols = [
        "Date de début", 
        "Date de fin",
        "Date_Debut_Execution_relle",
        "Date_Engagement",
        "Date_Paiement"
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
    
    return df

def main():
    st.title("Application de consultation du Plan d'Action")
    
    # -- Choix du type de fichier --
    file_type = st.selectbox(
        "Type de fichier à charger",
        ["csv", "xlsx"],
        help="Sélectionnez le type de fichier que vous souhaitez importer."
    )
    
    # -- Chargement du fichier --
    if file_type == "csv":
        uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"])
    else:
        uploaded_file = st.file_uploader("Choisir un fichier Excel (XLSX)", type=["xlsx"])
    
    if uploaded_file is not None:
        # Lecture du fichier
        df = load_data(uploaded_file, file_type)
        
        st.subheader("Aperçu des données brutes")
        st.dataframe(df.head(10))  # Affiche les 10 premières lignes
        
        # -- Filtres sur Domaines de dépense --
        if "Domaines de dépense" in df.columns:
            domaines_uniques = df["Domaines de dépense"].dropna().unique().tolist()
            domaines_selectionnes = st.multiselect(
                "Filtrer par Domaines de dépense",
                sorted(domaines_uniques)
            )
        else:
            domaines_selectionnes = []
        
        # -- Filtres sur Lignes budgétaires --
        if "Ligne budgétaire" in df.columns:
            lignes_uniques = df["Ligne budgétaire"].dropna().unique().tolist()
            lignes_selectionnees = st.multiselect(
                "Filtrer par Ligne budgétaire",
                sorted(lignes_uniques)
            )
        else:
            lignes_selectionnees = []
        
        # -- Filtre par plage de dates (exemple : Date de début) --
        if "Date de début" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Date de début"]):
            date_min = df["Date de début"].min()
            date_max = df["Date de début"].max()
            
            if pd.notnull(date_min) and pd.notnull(date_max):
                date_range = st.slider(
                    "Sélectionnez la plage de 'Date de début'",
                    min_value=date_min.to_pydatetime(),
                    max_value=date_max.to_pydatetime(),
                    value=(date_min.to_pydatetime(), date_max.to_pydatetime()),
                    format="DD/MM/YYYY"
                )
            else:
                date_range = (None, None)
        else:
            date_range = (None, None)
        
        # -- Application des filtres --
        df_filtered = df.copy()
        
        # Filtre sur Domaines de dépense
        if domaines_selectionnes:
            df_filtered = df_filtered[df_filtered["Domaines de dépense"].isin(domaines_selectionnes)]
        
        # Filtre sur Lignes budgétaires
        if lignes_selectionnees:
            df_filtered = df_filtered[df_filtered["Ligne budgétaire"].isin(lignes_selectionnees)]
        
        # Filtre sur la plage de dates (Date de début)
        if date_range[0] is not None and date_range[1] is not None:
            start_date, end_date = date_range
            df_filtered = df_filtered[
                (df_filtered["Date de début"] >= pd.to_datetime(start_date)) &
                (df_filtered["Date de début"] <= pd.to_datetime(end_date))
            ]
        
        st.subheader("Données filtrées")
        
        # -- Choix de la colonne de tri --
        sort_col = st.selectbox(
            "Choisissez la colonne pour trier les données",
            df_filtered.columns
        )
        
        # -- Ordre de tri (ascendant ou descendant) --
        sort_ascending = st.radio("Ordre de tri", ("Croissant", "Décroissant"))
        ascending = True if sort_ascending == "Croissant" else False
        
        # -- Application du tri --
        df_filtered = df_filtered.sort_values(by=sort_col, ascending=ascending)
        
        st.dataframe(df_filtered)
    else:
        st.info("Veuillez charger un fichier pour commencer.")

if __name__ == "__main__":
    main()
