# Composant Matrice Éditable avec Drill-Through

Ce composant permet de créer une matrice (tableau) éditable avec fonctionnalité de drill-through similaire à PowerBI, où les utilisateurs peuvent cliquer sur un bouton "+" à côté d'une ligne pour afficher des détails supplémentaires.

## Fonctionnalités

- **Édition des cellules** : Permet aux utilisateurs de modifier les valeurs dans les colonnes spécifiées
- **Drill-through** : Affiche des données détaillées pour chaque ligne lorsque l'utilisateur clique sur le bouton "+"
- **Expansion/réduction** : Les détails peuvent être affichés ou masqués en cliquant sur les boutons "+" et "-"
- **Mise à jour en temps réel** : Les calculs peuvent être mis à jour automatiquement lorsque les données sont modifiées

## Utilisation de base

```python
from streamlit_dash import OutilMiseEnPage
import pandas as pd

# Crée l'application
app = OutilMiseEnPage(title="Exemple de Matrice Éditable")

# Données principales
data = pd.DataFrame({
    'Région': ['Nord', 'Sud', 'Est', 'Ouest'],
    'Ventes': [1250000, 1500000, 980000, 1750000],
    'Coûts': [750000, 850000, 600000, 950000],
    'Marge': [500000, 650000, 380000, 800000]
})

# Données détaillées pour chaque région
drill_data = {
    0: pd.DataFrame({  # Détails pour la région Nord
        'Produit': ['Produit A', 'Produit B', 'Produit C'],
        'Ventes': [450000, 350000, 250000],
        'Coûts': [270000, 210000, 150000]
    }),
    1: pd.DataFrame({  # Détails pour la région Sud
        'Produit': ['Produit A', 'Produit B', 'Produit C'],
        'Ventes': [400000, 350000, 300000],
        'Coûts': [220000, 200000, 170000]
    })
    # ... autres régions
}

# Ajoute la matrice éditable
matrix_id = app.editable_matrix(
    data=data,
    drill_data=drill_data,
    editable_columns=['Ventes', 'Coûts']
)

# Lance l'application
app.run(debug=True, port=8050)
```

## Paramètres

- **data** (DataFrame): Un DataFrame pandas contenant les données principales à afficher
- **drill_data** (dict, optional): Un dictionnaire où les clés sont les indices des lignes et les valeurs sont des DataFrames contenant les données détaillées pour chaque ligne
- **key** (str, optional): Une clé unique pour la matrice (générée automatiquement si non spécifiée)
- **editable_columns** (list, optional): Liste des noms de colonnes qui peuvent être modifiées par l'utilisateur

## Mise à jour des calculs

Pour mettre à jour automatiquement les calculs lorsque les données sont modifiées, vous pouvez ajouter un callback:

```python
@app.app.callback(
    Output(matrix_id, "data"),
    Input(matrix_id, "data_timestamp"),
    State(matrix_id, "data")
)
def update_calculations(timestamp, data):
    if not timestamp or not data:
        return dash.no_update
    
    # Parcourt les lignes et met à jour les calculs
    for row in data:
        if 'Ventes' in row and 'Coûts' in row:
            try:
                ventes = float(row['Ventes'])
                couts = float(row['Coûts'])
                
                # Calcule la marge
                row['Marge'] = ventes - couts
            except (ValueError, TypeError):
                pass
    
    return data
```

## Exemples

Deux exemples sont fournis pour démontrer l'utilisation du composant:

1. **editable_matrix_example.py**: Exemple de base montrant comment utiliser le composant
2. **advanced_matrix_example.py**: Exemple avancé avec plusieurs niveaux de drill-through, mise à jour en temps réel et visualisations

Pour exécuter les exemples:

```bash
python examples/editable_matrix_example.py
python examples/advanced_matrix_example.py
```

## Personnalisation

Le composant peut être personnalisé en modifiant les styles CSS ou en ajoutant des fonctionnalités supplémentaires via des callbacks Dash. Consultez la documentation de Dash pour plus d'informations sur la personnalisation des composants.

## Gestion des Callbacks Multiples

Si vous avez plusieurs callbacks qui mettent à jour la même sortie (par exemple, la propriété `data` de la matrice), vous pouvez rencontrer l'erreur suivante:

```
In the callback for output(s):
  matrix-id.data
Output 0 (matrix-id.data) is already in use.
```

Il existe deux façons de résoudre ce problème:

### 1. Utiliser `allow_duplicate=True`

Vous pouvez autoriser les sorties dupliquées en ajoutant `allow_duplicate=True` au paramètre `Output`. **Important**: Lorsque vous utilisez `allow_duplicate=True`, vous devez obligatoirement ajouter `prevent_initial_call=True` au callback, sinon Dash générera une erreur:

```
dash.exceptions.DuplicateCallback: allow_duplicate requires prevent_initial_call to be True. 
The order of the call is not guaranteed to be the same on every page load.
```

Voici comment implémenter correctement un callback avec `allow_duplicate=True`:

```python
@app.app.callback(
    Output(matrix_id, "data", allow_duplicate=True),
    Input(...),
    State(...),
    prevent_initial_call=True  # OBLIGATOIRE avec allow_duplicate=True
)
```

Cette approche est utilisée dans l'implémentation interne du composant `editable_matrix`.

### 2. Combiner les callbacks en un seul

Une approche plus propre consiste à combiner tous les callbacks qui mettent à jour la même sortie en un seul callback, en utilisant `dash.callback_context` pour déterminer quel input a déclenché le callback:

```python
@app.app.callback(
    Output(matrix_id, "data"),
    [
        Input(matrix_id, "data_timestamp"),  # Déclencheur pour l'édition des cellules
        Input("button-1", "n_clicks"),       # Déclencheur pour le bouton 1
        Input("button-2", "n_clicks")        # Déclencheur pour le bouton 2
    ],
    [
        State(matrix_id, "data"),            # État actuel des données
        State("other-input", "value")        # Autres états nécessaires
    ],
    prevent_initial_call=True
)
def update_data(timestamp, btn1_clicks, btn2_clicks, current_data, other_value):
    # Détermine quel input a déclenché le callback
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Logique différente selon le déclencheur
    if trigger_id == matrix_id:
        # Logique pour l'édition des cellules
        pass
    elif trigger_id == "button-1":
        # Logique pour le bouton 1
        pass
    elif trigger_id == "button-2":
        # Logique pour le bouton 2
        pass
    
    return updated_data
```

Consultez l'exemple `multi_callback_matrix_example.py` pour une démonstration complète de cette approche. 