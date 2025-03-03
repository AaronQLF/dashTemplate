# Dash Template - Interface Style Streamlit

Ce projet fournit une API similaire à Streamlit pour créer des applications Dash avec une syntaxe simple et intuitive. Il permet de créer rapidement des tableaux de bord interactifs et des applications de visualisation de données.

## Fonctionnalités

- **API intuitive** : Créez des interfaces utilisateur avec une syntaxe inspirée de Streamlit
- **Mise en page flexible** : Utilisez des colonnes pour organiser votre contenu
- **Composants interactifs** : Boutons, curseurs, listes déroulantes, cases à cocher, etc.
- **Visualisations** : Intégration facile avec Plotly pour des graphiques interactifs
- **Utilitaires de mise en cache** : Améliorez les performances avec différentes stratégies de mise en cache

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Création d'une application simple

```python
from streamlit_dash import OutilMiseEnPage

# Création de l'application
st = OutilMiseEnPage("Mon Application")

# Ajout de contenu
st.title("Bienvenue dans mon application")
st.text("Voici un exemple simple d'utilisation de l'API.")

# Ajout de composants interactifs
name = st.text_input("Votre nom")
age = st.number_input("Votre âge", min_value=0, max_value=120)

if st.button("Soumettre"):
    st.text(f"Bonjour {name}, vous avez {age} ans.")

# Exécution de l'application
if __name__ == "__main__":
    st.run(debug=True)
```

### Utilisation des colonnes

```python
# Création de deux colonnes égales
with st.columns() as cols:
    # Première colonne
    with cols[0]:
        st.header("Colonne 1")
        st.text("Contenu de la première colonne")
    
    # Deuxième colonne
    with cols[1]:
        st.header("Colonne 2")
        st.text("Contenu de la deuxième colonne")

# Création de colonnes avec un ratio personnalisé (3:1)
with st.columns([3, 1]) as cols:
    # Colonne large (75%)
    with cols[0]:
        st.header("Colonne principale")
        st.text("Cette colonne occupe 75% de la largeur")
    
    # Colonne étroite (25%)
    with cols[1]:
        st.header("Barre latérale")
        st.text("Cette colonne occupe 25% de la largeur")
```

### Utilisation des utilitaires de mise en cache

```python
from performanceUtils import memoize, timed_cache, lru_cache

@memoize
def fonction_couteuse(param):
    # Cette fonction ne sera exécutée qu'une fois pour chaque valeur unique de param
    return resultat_couteux

@timed_cache(seconds=60)
def donnees_api(url):
    # Cette fonction mettra en cache les résultats pendant 60 secondes
    return recuperer_donnees(url)

@lru_cache(maxsize=100)
def calcul_frequent(x, y):
    # Cette fonction conservera les 100 résultats les plus récemment utilisés
    return calcul_complexe(x, y)
```

## Exemples

Le répertoire `examples/` contient plusieurs exemples d'utilisation :

- `streamlit_example.py` : Démontre l'utilisation des colonnes et des composants
- `caching_example.py` : Montre comment utiliser les utilitaires de mise en cache

Pour exécuter un exemple :

```bash
cd examples
python streamlit_example.py
```

## Structure du projet

- `streamlit_dash.py` : Implémentation principale de l'API style Streamlit
- `performanceUtils.py` : Utilitaires de mise en cache pour améliorer les performances
- `examples/` : Exemples d'utilisation
- `requirements.txt` : Dépendances du projet

## Dépendances

- dash
- dash-bootstrap-components
- pandas
- plotly
- numpy

## Licence

Ce projet est sous licence MIT.

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request. 