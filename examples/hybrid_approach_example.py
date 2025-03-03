import sys
import os
import numpy as np
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

# Ajoute le répertoire parent au chemin pour pouvoir importer le module streamlit_dash
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_dash import OutilMiseEnPage

# Création de données d'exemple
np.random.seed(42)
df = pd.DataFrame({
    'Catégorie': ['A', 'B', 'C', 'D', 'E'] * 10,
    'Valeur': np.random.randint(1, 100, 50),
    'Groupe': np.random.choice(['Groupe 1', 'Groupe 2', 'Groupe 3'], 50)
})

# Création d'une instance de OutilMiseEnPage
st = OutilMiseEnPage("Approche Hybride - OutilMiseEnPage + dcc")

# Ajout d'un titre et d'une description avec OutilMiseEnPage
st.title("Approche Hybride: OutilMiseEnPage + dcc")
st.markdown("""
Cette application démontre comment utiliser à la fois:
- La classe `OutilMiseEnPage` pour une syntaxe simple style Streamlit
- Les composants `dcc` directement pour un contrôle plus précis
""")

st.divider()

# Création d'une mise en page à deux colonnes avec OutilMiseEnPage
with st.columns([1, 1]) as cols:
    # Première colonne - Utilisation de OutilMiseEnPage
    with cols[0]:
        st.header("Partie OutilMiseEnPage", level=2)
        st.text("Cette section utilise l'API OutilMiseEnPage")
        
        # Ajout de contrôles avec OutilMiseEnPage
        selected_group = st.selectbox(
            "Sélectionner un groupe",
            options=df['Groupe'].unique(),
            key="group_selector"
        )
        
        min_value = st.slider(
            "Valeur minimale",
            min_value=0,
            max_value=100,
            value=20,
            key="min_value_slider"
        )
        
        # Création d'un graphique avec OutilMiseEnPage
        filtered_df = df[(df['Groupe'] == selected_group) & (df['Valeur'] >= min_value)]
        fig1 = px.bar(
            filtered_df,
            x='Catégorie',
            y='Valeur',
            color='Catégorie',
            title=f"Données pour {selected_group} (min: {min_value})"
        )
        st.plotly_chart(fig1)
    
    # Deuxième colonne - Utilisation directe des composants dcc
    with cols[1]:
        # Nous allons ajouter des composants dcc directement
        # Pour cela, nous devons accéder à l'objet app de OutilMiseEnPage
        # et ajouter nos composants à son layout
        
        # Création d'un conteneur pour les composants dcc
        dcc_container = html.Div([
            html.H2("Partie dcc native", className="mb-3"),
            html.P("Cette section utilise directement les composants dcc"),
            
            # Ajout de contrôles dcc
            html.Label("Type de graphique"),
            dcc.RadioItems(
                id="chart-type",
                options=[
                    {"label": "Barres", "value": "bar"},
                    {"label": "Ligne", "value": "line"},
                    {"label": "Points", "value": "scatter"}
                ],
                value="bar",
                className="mb-3"
            ),
            
            dcc.Checklist(
                id="show-trend",
                options=[{"label": "Afficher la ligne de tendance", "value": "show"}],
                value=["show"],
                className="mb-3"
            ),
            
            # Conteneur pour le graphique dcc
            html.Div([
                dcc.Graph(id="dcc-chart")
            ], className="border p-3 rounded")
        ], className="p-3")
        
        # Ajout du conteneur dcc à la colonne OutilMiseEnPage
        st._add_component(dcc_container)

# Ajout d'un callback pour le graphique dcc
# Nous devons accéder à l'objet app de OutilMiseEnPage pour définir le callback
@st.app.callback(
    Output("dcc-chart", "figure"),
    [Input("group_selector", "value"),
     Input("min_value_slider", "value"),
     Input("chart-type", "value"),
     Input("show-trend", "value")]
)
def update_dcc_chart(selected_group, min_value, chart_type, show_trend):
    # Filtrage des données
    filtered_df = df[(df['Groupe'] == selected_group) & (df['Valeur'] >= min_value)]
    
    # Création du graphique en fonction du type sélectionné
    if chart_type == "bar":
        fig = px.bar(
            filtered_df,
            x='Catégorie',
            y='Valeur',
            color='Catégorie',
            title=f"dcc: {selected_group} (min: {min_value})"
        )
    elif chart_type == "line":
        fig = px.line(
            filtered_df.groupby('Catégorie')['Valeur'].mean().reset_index(),
            x='Catégorie',
            y='Valeur',
            markers=True,
            title=f"dcc: Moyennes pour {selected_group}"
        )
    else:  # scatter
        fig = px.scatter(
            filtered_df,
            x='Catégorie',
            y='Valeur',
            color='Catégorie',
            size='Valeur',
            title=f"dcc: {selected_group} (min: {min_value})"
        )
    
    # Ajout d'une ligne de tendance si demandé
    if show_trend and "show" in show_trend:
        avg_by_cat = filtered_df.groupby('Catégorie')['Valeur'].mean().reset_index()
        fig.add_scatter(
            x=avg_by_cat['Catégorie'],
            y=avg_by_cat['Valeur'],
            mode='lines+markers',
            name='Moyenne',
            line=dict(color='black', width=2)
        )
    
    return fig

# Ajout d'une section finale avec OutilMiseEnPage
st.divider()
st.header("Communication entre les deux approches", level=2)
st.markdown("""
Comme vous pouvez le voir, les deux approches peuvent communiquer entre elles:
- Les contrôles de OutilMiseEnPage (groupe et valeur minimale) affectent le graphique dcc
- Les contrôles dcc (type de graphique et ligne de tendance) affectent uniquement le graphique dcc

Cette approche hybride vous permet de:
1. Utiliser la syntaxe simple de OutilMiseEnPage pour la structure générale
2. Intégrer des composants dcc natifs pour des fonctionnalités plus avancées
3. Faire communiquer les deux approches via les callbacks
""")

# Exécution de l'application
if __name__ == "__main__":
    st.run(debug=True, port=8090) 