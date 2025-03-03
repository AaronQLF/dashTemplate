import sys
import os
import time
import numpy as np
import pandas as pd
import plotly.express as px

# Ajoute le répertoire parent au chemin pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from LayoutManager import CDPQDCC
from performanceUtils import memoize, timed_cache, lru_cache, get_cache_stats

# Création de données d'exemple
np.random.seed(42)
df = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D', 'E'] * 10,
    'Value': np.random.randint(1, 100, 50),
    'Group': np.random.choice(['Groupe 1', 'Groupe 2', 'Groupe 3'], 50)
})

# Définition des fonctions mises en cache pour le traitement des données

@memoize
def filter_data(group, min_value):
    """Filtre les données en fonction du groupe et de la valeur minimale (avec mémoïsation de base)"""
    print(f"Filtrage des données pour le groupe {group} avec une valeur minimale de {min_value}...")
    time.sleep(0.5)  # Simulation du temps de traitement
    return df[(df['Group'] == group) & (df['Value'] >= min_value)]

@timed_cache(seconds=30)
def calculate_statistics(dataframe):
    """Calcule les statistiques pour un dataframe (avec cache basé sur le temps)"""
    print("Calcul des statistiques...")
    time.sleep(1)  # Simulation d'un calcul complexe
    return {
        'mean': dataframe['Value'].mean(),
        'median': dataframe['Value'].median(),
        'min': dataframe['Value'].min(),
        'max': dataframe['Value'].max(),
        'count': len(dataframe)
    }

@lru_cache(maxsize=5)
def create_chart(group, chart_type, use_color=True):
    """Crée un graphique basé sur les paramètres (avec cache LRU)"""
    print(f"Création d'un graphique {chart_type} pour {group}...")
    time.sleep(0.8)  # Simulation du temps de création du graphique
    
    filtered_df = df[df['Group'] == group]
    
    if chart_type == "Bar":
        if use_color:
            fig = px.bar(
                filtered_df, 
                x='Category', 
                y='Value', 
                color='Category',
                title=f"{group} - Valeurs par catégorie"
            )
        else:
            fig = px.bar(
                filtered_df, 
                x='Category', 
                y='Value',
                title=f"{group} - Valeurs par catégorie"
            )
    elif chart_type == "Line":
        fig = px.line(
            filtered_df.groupby('Category')['Value'].mean().reset_index(), 
            x='Category', 
            y='Value',
            markers=True,
            title=f"{group} - Valeurs par catégorie"
        )
    else:  # Scatter
        if use_color:
            fig = px.scatter(
                filtered_df, 
                x='Category', 
                y='Value', 
                color='Category',
                size='Value',
                title=f"{group} - Valeurs par catégorie"
            )
        else:
            fig = px.scatter(
                filtered_df, 
                x='Category', 
                y='Value',
                size='Value',
                title=f"{group} - Valeurs par catégorie"
            )
    
    return fig

# Création d'une application cdpqdcc
st = CDPQDCC("Exemple de mise en cache")

# Ajout d'un titre et d'une description
st.title("Optimisation des performances avec la mise en cache")
st.markdown("""
Cet exemple démontre comment utiliser les décorateurs de mise en cache pour améliorer les performances.
Remarquez comment les fonctions ne sont exécutées qu'une seule fois pour les mêmes entrées, et les appels suivants utilisent les résultats mis en cache.
""")

# Création d'une mise en page avec des contrôles et une visualisation
with st.columns([1, 2]) as cols:
    # Colonne des contrôles
    with cols[0]:
        st.header("Contrôles", level=3)
        
        # Ajout des contrôles de filtrage
        selected_group = st.selectbox(
            "Sélectionner un groupe",
            options=df['Group'].unique(),
            key="group_selector"
        )
        
        min_value = st.slider(
            "Valeur minimale",
            min_value=0,
            max_value=100,
            value=20,
            key="min_value_slider"
        )
        
        chart_type = st.radio(
            "Type de graphique",
            options=["Bar", "Line", "Scatter"],
            index=0,
            key="chart_type"
        )
        
        use_color = st.checkbox("Utiliser la couleur", value=True, key="use_color")
        
        # Ajout d'un bouton pour rafraîchir les données (contournant le cache)
        st.button("Rafraîchir les données", key="refresh_btn")
    
    # Colonne de visualisation
    with cols[1]:
        st.header("Visualisation", level=3)
        
        # Création d'une carte pour le graphique
        chart_container = st.card("Graphique dynamique")
        with chart_container:
            # Filtrage des données (utilisant la fonction mise en cache)
            filtered_data = filter_data(selected_group, min_value)
            
            # Création du graphique (utilisant la fonction mise en cache)
            fig = create_chart(selected_group, chart_type, len(use_color) > 0)
            
            # Affichage du graphique
            st.plotly_chart(fig, key="main_chart")
        
        # Création d'une carte pour les statistiques
        stats_container = st.card("Statistiques")
        with stats_container:
            # Calcul des statistiques (utilisant la fonction mise en cache)
            stats = calculate_statistics(filtered_data)
            
            # Affichage des statistiques en colonnes
            with st.columns(5) as stat_cols:
                with stat_cols[0]:
                    st.metric("Moyenne", f"{stats['mean']:.1f}")
                with stat_cols[1]:
                    st.metric("Médiane", f"{stats['median']:.1f}")
                with stat_cols[2]:
                    st.metric("Min", stats['min'])
                with stat_cols[3]:
                    st.metric("Max", stats['max'])
                with stat_cols[4]:
                    st.metric("Nombre", stats['count'])

# Ajout d'une section pour les statistiques de cache
st.divider()
st.header("Statistiques de cache", level=2)

# Affichage des statistiques de cache de manière formatée
stats = get_cache_stats()
st.markdown(f"""
### Résumé
- Nombre total de fonctions mises en cache: {stats['summary']['total_functions']}
- Nombre total de succès de cache: {stats['summary']['total_hits']}
- Nombre total d'échecs de cache: {stats['summary']['total_misses']}
""")

# Affichage des statistiques par fonction
st.markdown("### Statistiques par fonction")
for func_name, func_stats in stats['per_function'].items():
    hit_rate = func_stats['hits'] / (func_stats['hits'] + func_stats['misses']) * 100 if (func_stats['hits'] + func_stats['misses']) > 0 else 0
    st.markdown(f"""
**{func_name}**
- Succès: {func_stats['hits']}
- Échecs: {func_stats['misses']}
- Taux de succès: {hit_rate:.1f}%
""")

# Ajout d'un texte explicatif
st.divider()
st.markdown("""
### Comment fonctionne la mise en cache

1. **Mémoïsation (`@memoize`)**: Met en cache les résultats en fonction des arguments de la fonction. Idéal pour les fonctions pures.
2. **Cache temporisé (`@timed_cache`)**: Met en cache les résultats pendant une période spécifiée. Utile pour les données qui changent périodiquement.
3. **Cache LRU (`@lru_cache`)**: Limite la taille du cache en supprimant les éléments les moins récemment utilisés. Bon pour les environnements à mémoire limitée.
4. **Cache sur disque (`@disk_cache`)**: Stocke les résultats sur disque pour la persistance entre les exécutions du programme. Utile pour les calculs coûteux.
5. **Cache paramétré (`@parametrized_cache`)**: Permet d'activer/désactiver le cache en fonction d'un paramètre. Offre de la flexibilité.

Essayez de modifier les contrôles et remarquez comment certaines fonctions s'exécutent tandis que d'autres utilisent les résultats mis en cache !
""")

# Exécution de l'application
if __name__ == "__main__":
    st.run(debug=True, port=8090) 