import sys
import os
import numpy as np
import pandas as pd
import plotly.express as px

# Ajoute le répertoire parent au chemin pour pouvoir importer le module streamlit_dash
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_dash import OutilMiseEnPage 

# Création de données d'exemple
np.random.seed(42)
df = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D', 'E'] * 10,
    'Value': np.random.randint(1, 100, 50),
    'Group': np.random.choice(['Groupe 1', 'Groupe 2', 'Groupe 3'], 50)
})

# Création d'une application Streamlit Dash
st = OutilMiseEnPage("Tableau de bord style Streamlit")

# Ajout d'un titre et d'une description
st.title("Tableau de bord style Streamlit")
st.text("Cet exemple démontre comment créer des mises en page similaires à Streamlit dans Dash.")

# Exemple 1: Deux colonnes égales
st.header("Exemple 1: Deux colonnes égales", level=2)
st.text("col1, col2 = st.beta_columns(2)")

# Création de deux colonnes égales
with st.columns() as cols:
    # Première colonne
    with cols[0]:
        st.header("Colonne 1", level=3)
        st.text("Ceci est la première colonne avec une largeur égale.")
        st.button("Bouton Colonne 1")
    
    # Deuxième colonne
    with cols[1]:
        st.header("Colonne 2", level=3)
        st.text("Ceci est la deuxième colonne avec une largeur égale.")
        st.button("Bouton Colonne 2")

# Exemple 2: Trois colonnes égales
st.header("Exemple 2: Trois colonnes égales", level=2)
st.text("col1, col2, col3 = st.beta_columns(3)")

# Création de trois colonnes égales
with st.columns([1, 1, 1]) as cols:
    # Première colonne
    with cols[0]:
        st.header("Colonne 1", level=3)
        st.text("Largeur: 1/3")
        st.selectbox(
            "Liste déroulante Col 1",
            options=[f'Option {i}' for i in range(1, 4)]
        )
    
    # Deuxième colonne
    with cols[1]:
        st.header("Colonne 2", level=3)
        st.text("Largeur: 1/3")
        st.slider("Curseur Col 2", min_value=0, max_value=100, value=50)
    
    # Troisième colonne
    with cols[2]:
        st.header("Colonne 3", level=3)
        st.text("Largeur: 1/3")
        st.checkbox("Case à cocher Col 3")

# Exemple 3: Colonnes avec ratio personnalisé
st.header("Exemple 3: Ratio de largeur personnalisé", level=2)
st.text("col1, col2 = st.beta_columns([3, 1])")

# Création de colonnes avec un ratio 3:1
with st.columns([3, 1]) as cols:
    # Première colonne (plus large)
    with cols[0]:
        st.header("Colonne 1 (75%)", level=3)
        st.text("Cette colonne occupe 75% de la largeur disponible.")
        
        # Création d'un graphique dans la colonne plus large
        fig = px.bar(
            df.groupby('Category')['Value'].mean().reset_index(),
            x='Category',
            y='Value',
            title="Valeur moyenne par catégorie"
        )
        st.plotly_chart(fig)
    
    # Deuxième colonne (plus étroite)
    with cols[1]:
        st.header("Colonne 2 (25%)", level=3)
        st.text("Cette colonne occupe 25% de la largeur disponible.")
        st.text("Parfait pour les contrôles ou les visualisations plus petites.")
        
        # Ajout de quelques contrôles
        st.radio(
            "Sélectionner une option",
            options=[f'Option {i}' for i in range(1, 4)]
        )

# Exemple 4: Tableau de bord interactif
st.header("Exemple 4: Tableau de bord interactif", level=2)
st.text("Un tableau de bord interactif simple avec des contrôles et des visualisations")

# Création d'une mise en page à deux colonnes pour le tableau de bord
with st.columns([1, 3]) as cols:
    # Colonne des contrôles
    with cols[0]:
        st.header("Contrôles", level=3)
        
        # Ajout de contrôles
        category = st.selectbox(
            "Sélectionner une catégorie",
            options=df['Category'].unique()
        )
        
        group = st.radio(
            "Sélectionner un groupe",
            options=df['Group'].unique()
        )
        
        show_trend = st.checkbox("Afficher la ligne de tendance", value=True)
        
        # Ajout d'une métrique
        avg_value = df[df['Category'] == category]['Value'].mean()
        st.metric("Valeur moyenne", f"{avg_value:.1f}", delta=avg_value - 50)
    
    # Colonne de visualisation
    with cols[1]:
        st.header("Visualisation", level=3)
        
        # Création d'onglets à l'aide d'un expandeur
        with st.card("Visualisation des données"):
            # Filtrage des données en fonction des sélections
            filtered_df = df[(df['Category'] == category) & (df['Group'] == group)]
            
            # Création d'un graphique à barres
            fig1 = px.bar(
                filtered_df,
                x='Category',
                y='Value',
                color='Group',
                title=f"Valeurs pour {category} dans {group}"
            )
            
            # Ajout d'une ligne de tendance si show_trend est coché
            if show_trend and len(show_trend) > 0:
                avg_by_cat = filtered_df.groupby('Category')['Value'].mean().reset_index()
                fig1.add_scatter(
                    x=avg_by_cat['Category'],
                    y=avg_by_cat['Value'],
                    mode='lines+markers',
                    name='Moyenne',
                    line=dict(color='black', width=2)
                )
            
            st.plotly_chart(fig1)
            
            # Affichage du tableau de données
            st.dataframe(filtered_df)

# Pied de page
st.divider()
st.text("Ce système de mise en page fournit une expérience similaire à Streamlit dans les applications Dash.")

# Exécution de l'application
if __name__ == "__main__":
    st.run(debug=True, port=8090) 