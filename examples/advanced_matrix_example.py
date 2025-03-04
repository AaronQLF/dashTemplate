import sys
import os
import pandas as pd
import numpy as np
import dash
from dash import Output, Input, State, html, dcc
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Ajoute le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit_dash import OutilMiseEnPage

def generate_sales_data():
    """Génère des données de ventes fictives pour l'exemple"""
    # Définit les régions et les produits
    regions = ['Nord', 'Sud', 'Est', 'Ouest', 'Centre']
    categories = ['Électronique', 'Vêtements', 'Alimentation', 'Maison', 'Loisirs']
    
    # Crée le DataFrame principal
    data = []
    for region in regions:
        total_ventes = random.randint(800000, 2000000)
        total_couts = random.randint(int(total_ventes * 0.5), int(total_ventes * 0.7))
        total_marge = total_ventes - total_couts
        rentabilite = (total_marge / total_ventes) * 100
        
        data.append({
            'Région': region,
            'Ventes': total_ventes,
            'Coûts': total_couts,
            'Marge': total_marge,
            'Rentabilité': f"{rentabilite:.1f}%",
            'Tendance': random.choice(['↑', '↓', '→']) 
        })
    
    # Crée les données détaillées par catégorie
    drill_data_level1 = {}
    drill_data_level2 = {}
    
    for i, region in enumerate(regions):
        # Données par catégorie pour chaque région
        categories_data = []
        for category in categories:
            cat_ventes = random.randint(100000, 400000)
            cat_couts = random.randint(int(cat_ventes * 0.5), int(cat_ventes * 0.7))
            cat_marge = cat_ventes - cat_couts
            cat_rentabilite = (cat_marge / cat_ventes) * 100
            
            categories_data.append({
                'Catégorie': category,
                'Ventes': cat_ventes,
                'Coûts': cat_couts,
                'Marge': cat_marge,
                'Rentabilité': f"{cat_rentabilite:.1f}%",
                'Tendance': random.choice(['↑', '↓', '→'])
            })
        
        drill_data_level1[i] = pd.DataFrame(categories_data)
        
        # Données par produit pour chaque catégorie
        for j, category in enumerate(categories):
            products = [f"{category} {p}" for p in ['Premium', 'Standard', 'Économique']]
            products_data = []
            
            for product in products:
                prod_ventes = random.randint(20000, 150000)
                prod_couts = random.randint(int(prod_ventes * 0.5), int(prod_ventes * 0.7))
                prod_marge = prod_ventes - prod_couts
                prod_rentabilite = (prod_marge / prod_ventes) * 100
                
                products_data.append({
                    'Produit': product,
                    'Ventes': prod_ventes,
                    'Coûts': prod_couts,
                    'Marge': prod_marge,
                    'Rentabilité': f"{prod_rentabilite:.1f}%",
                    'Stock': random.randint(50, 500)
                })
            
            # Clé composée pour le deuxième niveau de drill-through
            drill_data_level2[(i, j)] = pd.DataFrame(products_data)
    
    return pd.DataFrame(data), drill_data_level1, drill_data_level2

def main():
    """
    Exemple avancé d'utilisation de la matrice éditable avec fonctionnalité de drill-through
    """
    # Crée l'application
    app = OutilMiseEnPage(title="Tableau de Bord des Ventes - Matrice Éditable Avancée")
    
    # Ajoute un titre
    app.title("Tableau de Bord des Ventes")
    
    # Ajoute une description
    app.markdown("""
    Ce tableau de bord démontre une utilisation avancée du composant `editable_matrix` avec:
    
    - Plusieurs niveaux de drill-through (Région → Catégorie → Produit)
    - Mise à jour en temps réel des calculs
    - Visualisations intégrées
    - Édition des données avec validation
    """)
    
    # Génère les données
    main_data, drill_data_level1, drill_data_level2 = generate_sales_data()
    
    # Crée un conteneur pour stocker les données
    app._add_component(dcc.Store(id='store-main-data', data=main_data.to_dict('records')))
    app._add_component(dcc.Store(id='store-drill-level1', data={str(k): v.to_dict('records') for k, v in drill_data_level1.items()}))
    app._add_component(dcc.Store(id='store-drill-level2', data={f"{k[0]}-{k[1]}": v.to_dict('records') for k, v in drill_data_level2.items()}))
    
    # Crée un layout à deux colonnes
    with app.columns([2, 1]):
        # Première colonne - Matrice principale
        with app[0]:
            app.header("Performance par Région")
            
            # Ajoute la matrice éditable avec drill-through
            matrix_id = app.editable_matrix(
                data=main_data,
                drill_data=drill_data_level1,
                editable_columns=['Ventes', 'Coûts'],
                key='matrix-main'
            )
            
            app.markdown("""
            **Instructions:**
            - Cliquez sur le **+** pour voir les détails par catégorie
            - Les colonnes **Ventes** et **Coûts** sont éditables
            - Les modifications sont automatiquement répercutées sur les calculs
            """)
            
            # Ajoute un espace pour les détails de niveau 2
            app._add_component(html.Div(id='detail-level2-container'))
        
        # Deuxième colonne - Graphiques et KPIs
        with app[1]:
            app.header("Visualisations")
            
            # Ajoute des métriques
            with app.card(title="KPIs Globaux"):
                total_ventes = main_data['Ventes'].sum()
                total_marge = main_data['Marge'].sum()
                rentabilite_moy = (total_marge / total_ventes) * 100
                
                app.metric("Ventes Totales", f"{total_ventes:,.0f} €")
                app.metric("Marge Totale", f"{total_marge:,.0f} €")
                app.metric("Rentabilité Moyenne", f"{rentabilite_moy:.1f}%")
            
            # Ajoute un graphique
            with app.card(title="Répartition des Ventes"):
                fig = px.pie(main_data, values='Ventes', names='Région', hole=0.4)
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                app.plotly_chart(fig)
            
            # Ajoute un autre graphique
            with app.card(title="Marge par Région"):
                fig = px.bar(main_data, x='Région', y='Marge', color='Région')
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                app.plotly_chart(fig)
    
    # Ajoute les callbacks
    
    # Callback pour mettre à jour les marges et rentabilités
    @app.app.callback(
        Output('matrix-main', 'data'),
        Input('matrix-main', 'data_timestamp'),
        State('matrix-main', 'data'),
        prevent_initial_call=True
    )
    def update_main_matrix(timestamp, data):
        if not timestamp or not data:
            return dash.no_update
        
        # Parcourt les lignes et met à jour les marges et rentabilités
        for row in data:
            if 'Ventes' in row and 'Coûts' in row:
                try:
                    ventes = float(row['Ventes'])
                    couts = float(row['Coûts'])
                    
                    # Calcule la marge
                    marge = ventes - couts
                    row['Marge'] = marge
                    
                    # Calcule la rentabilité
                    if ventes > 0:
                        rentabilite = (marge / ventes) * 100
                        row['Rentabilité'] = f"{rentabilite:.1f}%"
                        
                        # Met à jour la tendance en fonction de la rentabilité
                        if rentabilite > 40:
                            row['Tendance'] = '↑'
                        elif rentabilite < 30:
                            row['Tendance'] = '↓'
                        else:
                            row['Tendance'] = '→'
                    else:
                        row['Rentabilité'] = "0.0%"
                        row['Tendance'] = '↓'
                except (ValueError, TypeError):
                    # Ignore les erreurs de conversion
                    pass
        
        return data
    
    # Callback pour afficher les détails de niveau 2
    @app.app.callback(
        Output('detail-level2-container', 'children'),
        [Input('matrix-main-detail-container', 'children')],
        [State('store-drill-level2', 'data')]
    )
    def display_level2_details(level1_details, level2_data):
        if not level1_details:
            return []
        
        # Crée un composant pour afficher les détails de niveau 2
        return html.Div([
            html.H5("Détails par Produit", style={"marginTop": "20px"}),
            html.P("Cliquez sur une catégorie ci-dessus pour voir les produits associés.", 
                   style={"fontStyle": "italic", "color": "#666"})
        ])
    
    # Lance l'application
    app.run(debug=True, port=8052)

if __name__ == "__main__":
    main() 