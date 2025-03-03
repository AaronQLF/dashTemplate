import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np

# Création de données d'exemple
np.random.seed(42)
df = pd.DataFrame({
    'Catégorie': ['A', 'B', 'C', 'D', 'E'] * 10,
    'Valeur': np.random.randint(1, 100, 50),
    'Groupe': np.random.choice(['Groupe 1', 'Groupe 2', 'Groupe 3'], 50)
})

# Initialisation de l'application Dash
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

# Création d'un graphique avec Plotly Express
fig = px.bar(
    df.groupby('Catégorie')['Valeur'].mean().reset_index(),
    x='Catégorie',
    y='Valeur',
    title="Valeur moyenne par catégorie"
)

# Définition de la mise en page avec des composants dcc et html directement
app.layout = html.Div([
    # En-tête
    html.H1("Utilisation directe des composants dcc", className="mb-4"),
    html.P("Cet exemple montre comment utiliser directement les composants dcc sans passer par la classe OutilMiseEnPage."),
    html.Hr(),
    
    # Mise en page avec des colonnes Bootstrap
    dbc.Row([
        # Colonne des contrôles
        dbc.Col([
            html.H3("Contrôles"),
            
            # Dropdown (dcc.Dropdown)
            html.Label("Sélectionner un groupe"),
            dcc.Dropdown(
                id="group-dropdown",
                options=[{"label": groupe, "value": groupe} for groupe in df['Groupe'].unique()],
                value=df['Groupe'].unique()[0],
                className="mb-3"
            ),
            
            # Slider (dcc.Slider)
            html.Label("Valeur minimale"),
            dcc.Slider(
                id="min-value-slider",
                min=0,
                max=100,
                step=5,
                value=20,
                marks={i: str(i) for i in range(0, 101, 20)},
                className="mb-3"
            ),
            
            # Radio Items (dcc.RadioItems)
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
            
            # Checklist (dcc.Checklist)
            dcc.Checklist(
                id="show-trend",
                options=[{"label": "Afficher la ligne de tendance", "value": "show"}],
                value=["show"],
                className="mb-3"
            ),
            
            # Bouton (html.Button)
            html.Button(
                "Rafraîchir",
                id="refresh-button",
                className="btn btn-primary mb-3"
            )
        ], width=3),
        
        # Colonne de visualisation
        dbc.Col([
            html.H3("Visualisation"),
            
            # Carte pour le graphique
            dbc.Card([
                dbc.CardHeader("Graphique dynamique"),
                dbc.CardBody([
                    # Graphique Plotly (dcc.Graph)
                    dcc.Graph(id="main-chart")
                ])
            ], className="mb-4"),
            
            # Carte pour les données
            dbc.Card([
                dbc.CardHeader("Données filtrées"),
                dbc.CardBody([
                    # Tableau de données (dash_table.DataTable)
                    dash.dash_table.DataTable(
                        id="data-table",
                        page_size=5,
                        style_table={"overflowX": "auto"},
                        style_cell={
                            "textAlign": "left",
                            "padding": "8px"
                        },
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold"
                        }
                    )
                ])
            ])
        ], width=9)
    ])
], className="container py-4")

# Définition des callbacks
@callback(
    [Output("main-chart", "figure"),
     Output("data-table", "data"),
     Output("data-table", "columns")],
    [Input("group-dropdown", "value"),
     Input("min-value-slider", "value"),
     Input("chart-type", "value"),
     Input("show-trend", "value"),
     Input("refresh-button", "n_clicks")]
)
def update_output(selected_group, min_value, chart_type, show_trend, n_clicks):
    # Filtrage des données
    filtered_df = df[(df['Groupe'] == selected_group) & (df['Valeur'] >= min_value)]
    
    # Création du graphique en fonction du type sélectionné
    if chart_type == "bar":
        fig = px.bar(
            filtered_df,
            x='Catégorie',
            y='Valeur',
            color='Catégorie',
            title=f"Valeurs pour {selected_group} (min: {min_value})"
        )
    elif chart_type == "line":
        fig = px.line(
            filtered_df.groupby('Catégorie')['Valeur'].mean().reset_index(),
            x='Catégorie',
            y='Valeur',
            markers=True,
            title=f"Valeurs moyennes pour {selected_group} (min: {min_value})"
        )
    else:  # scatter
        fig = px.scatter(
            filtered_df,
            x='Catégorie',
            y='Valeur',
            color='Catégorie',
            size='Valeur',
            title=f"Valeurs pour {selected_group} (min: {min_value})"
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
    
    # Préparation des données pour le tableau
    table_data = filtered_df.to_dict('records')
    table_columns = [{"name": col, "id": col} for col in filtered_df.columns]
    
    return fig, table_data, table_columns

# Exécution de l'application
if __name__ == "__main__":
    app.run_server(debug=True, port=8090) 