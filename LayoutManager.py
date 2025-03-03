import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import uuid
from typing import List, Dict, Any, Optional, Union, Callable
import plotly.graph_objects as go

class layoutManager:
    """
    Une API similaire à Streamlit pour les applications Dash
    Cette classe permet de créer des interfaces Dash avec une syntaxe inspirée de Streamlit
    """
    
    def __init__(self, title="CDPQDCC App", theme=dbc.themes.BOOTSTRAP):
        """
        Initialise l'application CDPQDCC
        
        Args:
            title (str): Le titre de l'application
            theme: Le thème Bootstrap à utiliser
        """
        self.app = dash.Dash(__name__, external_stylesheets=[theme], suppress_callback_exceptions=True)
        self.app.title = title
        self._components = []  # Liste des composants principaux
        self._callbacks = []   # Liste des callbacks
        self._current_container = self._components  # Conteneur actuel pour l'ajout de composants
        self._container_stack = []  # Pile des conteneurs pour gérer les contextes imbriqués
        self._dummy_div = html.Div(id="dummy-div", style={"display": "none"})  # Div invisible pour les callbacks
        
        # Ajout de CSS personnalisé
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    body {
                        background-color: #f8f9fa;
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    }
                    
                    .st-container {
                        margin-bottom: 1rem;
                        width: 100%;
                    }
                    
                    .st-column {
                        padding: 0.5rem;
                        box-sizing: border-box;
                    }
                    
                    .st-expander {
                        border: 1px solid #e0e0e0;
                        border-radius: 0.3rem;
                        margin-bottom: 1rem;
                        overflow: hidden;
                    }
                    
                    .st-expander-header {
                        background-color: #f8f9fa;
                        padding: 0.75rem 1rem;
                        cursor: pointer;
                        font-weight: 600;
                        border-bottom: 1px solid #e0e0e0;
                    }
                    
                    .st-expander-content {
                        padding: 1rem;
                    }
                    
                    .st-card {
                        border: 1px solid #e0e0e0;
                        border-radius: 0.3rem;
                        margin-bottom: 1rem;
                        overflow: hidden;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    }
                    
                    .st-card-header {
                        background-color: #f8f9fa;
                        padding: 0.75rem 1rem;
                        font-weight: 600;
                        border-bottom: 1px solid #e0e0e0;
                    }
                    
                    .st-card-content {
                        padding: 1rem;
                    }
                    
                    /* Contrôles de formulaire */
                    .form-control, .dash-dropdown {
                        margin-bottom: 0.75rem;
                    }
                    
                    .form-label {
                        font-weight: 600;
                        margin-bottom: 0.25rem;
                        display: block;
                    }
                    
                    /* Slider */
                    .rc-slider {
                        margin: 1rem 0;
                    }
                    
                    /* Bouton */
                    .st-button {
                        margin-bottom: 0.75rem;
                    }
                    
                    /* Séparateur */
                    .st-divider {
                        margin: 1.5rem 0;
                        border-top: 1px solid #e0e0e0;
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
    
    def _add_component(self, component):
        """
        Ajoute un composant au conteneur actuel
        
        Args:
            component: Le composant à ajouter
        """
        self._current_container.append(component)
        return component
    
    def title(self, text):
        """
        Affiche un titre
        
        Args:
            text (str): Le texte du titre
        """
        return self._add_component(html.H1(text, className="st-title"))
    
    def header(self, text, level=2):
        """
        Affiche un en-tête
        
        Args:
            text (str): Le texte de l'en-tête
            level (int): Le niveau de l'en-tête (1-6)
        """
        if level < 1 or level > 6:
            level = 2
        return self._add_component(getattr(html, f"H{level}")(text, className=f"st-h{level}"))
    
    def text(self, text):
        """
        Affiche du texte
        
        Args:
            text (str): Le texte à afficher
        """
        return self._add_component(html.P(text, className="st-text"))
    
    def markdown(self, text):
        """
        Affiche du texte au format markdown
        
        Args:
            text (str): Le texte markdown à afficher
        """
        return self._add_component(dcc.Markdown(text, className="st-markdown"))
    
    def divider(self):
        """Affiche un séparateur horizontal"""
        return self._add_component(html.Hr(className="st-divider"))
    
    def columns(self, spec=None):
        """
        Crée une rangée avec des colonnes
        
        Args:
            spec (list, optional): Liste des largeurs relatives. Si None, crée des colonnes égales.
                Exemple: [3, 1] crée deux colonnes avec un ratio de largeur 3:1.
        
        Returns:
            ColumnManager: Un gestionnaire de contexte pour les colonnes
        """
        if spec is None:
            # Par défaut, 2 colonnes égales
            spec = [1, 1]
        
        # Calcule le total pour convertir en pourcentages
        total = sum(spec)
        
        # Crée une rangée pour les colonnes
        row_id = f"row-{str(uuid.uuid4())[:8]}"
        row = html.Div([], id=row_id, className="st-container", style={"display": "flex"})
        
        # Ajoute la rangée au conteneur actuel
        self._add_component(row)
        
        # Crée les colonnes
        columns = []
        for i, width in enumerate(spec):
            # Calcule le pourcentage de largeur
            width_pct = (width / total) * 100
            
            # Crée une colonne
            col_id = f"col-{i}-{str(uuid.uuid4())[:8]}"
            col = html.Div(
                [],
                id=col_id,
                className="st-column",
                style={"width": f"{width_pct}%"}
            )
            
            # Ajoute la colonne à la rangée
            row.children.append(col)
            
            # Ajoute la colonne à la liste
            columns.append(col)
        
        # Crée un gestionnaire de contexte pour les colonnes
        class ColumnManager:
            def __init__(self, parent, columns):
                self.parent = parent
                self.columns = columns
                self.original_container = parent._current_container
                self.original_stack = parent._container_stack.copy()
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Restaure le conteneur d'origine
                self.parent._current_container = self.original_container
                self.parent._container_stack = self.original_stack
            
            def __getitem__(self, index):
                # Crée un gestionnaire de contexte pour la colonne
                class ColumnContext:
                    def __init__(self, parent, column):
                        self.parent = parent
                        self.column = column
                        self.original_container = parent._current_container
                        self.original_stack = parent._container_stack.copy()
                    
                    def __enter__(self):
                        # Définit le conteneur actuel sur cette colonne
                        self.parent._container_stack.append(self.parent._current_container)
                        self.parent._current_container = self.column.children
                        return self
                    
                    def __exit__(self, exc_type, exc_val, exc_tb):
                        # Restaure le conteneur d'origine
                        self.parent._current_container = self.parent._container_stack.pop()
                
                return ColumnContext(self.parent, self.columns[index])
        
        return ColumnManager(self, columns)
    
    def beta_columns(self, n=2):
        """
        Crée n colonnes égales (compatibilité Streamlit)
        
        Args:
            n (int): Nombre de colonnes égales
        
        Returns:
            ColumnManager: Un gestionnaire de contexte pour les colonnes
        """
        return self.columns([1] * n)
    
    def button(self, label, key=None, on_click=None):
        """
        Affiche un bouton
        
        Args:
            label (str): L'étiquette du bouton
            key (str, optional): Une clé unique pour le bouton
            on_click (callable, optional): Fonction de rappel lorsque le bouton est cliqué
        """
        if key is None:
            key = f"button-{str(uuid.uuid4())[:8]}"
        
        button = html.Button(
            label,
            id=key,
            className="btn btn-primary st-button"
        )
        
        self._add_component(button)
        
        # Ajoute un callback si fourni
        if on_click:
            self._callbacks.append((
                Output(self._dummy_div.id, "children"),
                Input(key, "n_clicks"),
                on_click
            ))
        
        return button
    
    def text_input(self, label, value="", key=None, placeholder=None):
        """
        Affiche un champ de saisie de texte
        
        Args:
            label (str): L'étiquette du champ
            value (str, optional): La valeur par défaut
            key (str, optional): Une clé unique pour le champ
            placeholder (str, optional): Texte d'exemple
        """
        if key is None:
            key = f"text-input-{str(uuid.uuid4())[:8]}"
        
        container = html.Div(className="mb-3")
        
        container.children = [html.Label(label, htmlFor=key, className="form-label")]
        
        input_component = dcc.Input(
            id=key,
            type="text",
            value=value,
            placeholder=placeholder,
            className="form-control"
        )
        
        container.children.append(input_component)
        
        self._add_component(container)
        
        return input_component
    
    def number_input(self, label, min_value=None, max_value=None, value=0, step=1, key=None):
        """
        Affiche un champ de saisie numérique
        
        Args:
            label (str): L'étiquette du champ
            min_value (float, optional): Valeur minimale
            max_value (float, optional): Valeur maximale
            value (float, optional): Valeur par défaut
            step (float, optional): Pas
            key (str, optional): Une clé unique pour le champ
        """
        if key is None:
            key = f"number-input-{str(uuid.uuid4())[:8]}"
        
        container = html.Div(className="mb-3")
        
        # Ajoute l'étiquette
        container.children = [html.Label(label, htmlFor=key, className="form-label")]
        
        # Ajoute le champ
        input_component = dcc.Input(
            id=key,
            type="number",
            value=value,
            min=min_value,
            max=max_value,
            step=step,
            className="form-control"
        )
        
        container.children.append(input_component)
        
        self._add_component(container)
        
        return input_component
    
    def slider(self, label, min_value=0, max_value=100, value=50, step=1, key=None):
        """
        Affiche un curseur
        
        Args:
            label (str): L'étiquette du curseur
            min_value (float): Valeur minimale
            max_value (float): Valeur maximale
            value (float): Valeur par défaut
            step (float): Pas
            key (str, optional): Une clé unique pour le curseur
        """
        if key is None:
            key = f"slider-{str(uuid.uuid4())[:8]}"
        
        container = html.Div(className="mb-3")
        
        # Ajoute l'étiquette
        container.children = [html.Label(label, htmlFor=key, className="form-label")]
        
        # Ajoute le curseur
        slider_component = dcc.Slider(
            id=key,
            min=min_value,
            max=max_value,
            value=value,
            step=step,
            className="st-slider"
        )
        
        container.children.append(slider_component)
        
        self._add_component(container)
        
        return slider_component
    
    def selectbox(self, label, options, index=0, key=None):
        """
        Affiche une liste déroulante
        
        Args:
            label (str): L'étiquette de la liste
            options (list): Liste des options
            index (int, optional): Index de l'option sélectionnée par défaut
            key (str, optional): Une clé unique pour la liste
        """
        if key is None:
            key = f"selectbox-{str(uuid.uuid4())[:8]}"
        
        container = html.Div(className="mb-3")
        
        # Ajoute l'étiquette
        container.children = [html.Label(label, htmlFor=key, className="form-label")]
        
        # Formate les options pour dcc.Dropdown
        dropdown_options = []
        for i, option in enumerate(options):
            if isinstance(option, dict) and "label" in option and "value" in option:
                dropdown_options.append(option)
            else:
                dropdown_options.append({"label": str(option), "value": option})
        
        # Définit la valeur par défaut
        default_value = dropdown_options[index]["value"] if dropdown_options and 0 <= index < len(dropdown_options) else None
        
        # Ajoute la liste déroulante
        dropdown_component = dcc.Dropdown(
            id=key,
            options=dropdown_options,
            value=default_value,
            className="st-selectbox"
        )
        
        container.children.append(dropdown_component)
        
        self._add_component(container)
        
        return dropdown_component
    
    def multiselect(self, label, options, default=None, key=None):
        """
        Affiche une liste déroulante à sélection multiple
        
        Args:
            label (str): L'étiquette de la liste
            options (list): Liste des options
            default (list, optional): Liste des options sélectionnées par défaut
            key (str, optional): Une clé unique pour la liste
        """
        if key is None:
            key = f"multiselect-{str(uuid.uuid4())[:8]}"
        
        container = html.Div(className="mb-3")
        
        # Ajoute l'étiquette
        container.children = [html.Label(label, htmlFor=key, className="form-label")]
        
        # Formate les options pour dcc.Dropdown
        dropdown_options = []
        for option in options:
            if isinstance(option, dict) and "label" in option and "value" in option:
                dropdown_options.append(option)
            else:
                dropdown_options.append({"label": str(option), "value": option})
        
        # Ajoute la liste déroulante
        dropdown_component = dcc.Dropdown(
            id=key,
            options=dropdown_options,
            value=default,
            multi=True,
            className="st-multiselect"
        )
        
        container.children.append(dropdown_component)
        
        self._add_component(container)
        
        return dropdown_component
    
    def checkbox(self, label, value=False, key=None):
        """
        Affiche une case à cocher
        
        Args:
            label (str): L'étiquette de la case
            value (bool, optional): Valeur par défaut
            key (str, optional): Une clé unique pour la case
        """
        if key is None:
            key = f"checkbox-{str(uuid.uuid4())[:8]}"
        
        # Crée une liste de cases à cocher avec une seule option
        checklist = dcc.Checklist(
            id=key,
            options=[{"label": label, "value": "checked"}],
            value=["checked"] if value else [],
            className="st-checkbox"
        )
        
        self._add_component(checklist)
        
        return checklist
    
    def radio(self, label, options, index=0, key=None):
        """
        Affiche des boutons radio
        
        Args:
            label (str): L'étiquette du groupe
            options (list): Liste des options
            index (int, optional): Index de l'option sélectionnée par défaut
            key (str, optional): Une clé unique pour le groupe
        """
        if key is None:
            key = f"radio-{str(uuid.uuid4())[:8]}"
        
        container = html.Div(className="mb-3")
        
        # Ajoute l'étiquette
        container.children = [html.Label(label, className="form-label")]
        
        # Formate les options pour dcc.RadioItems
        radio_options = []
        for i, option in enumerate(options):
            if isinstance(option, dict) and "label" in option and "value" in option:
                radio_options.append(option)
            else:
                radio_options.append({"label": str(option), "value": option})
        
        # Définit la valeur par défaut
        default_value = radio_options[index]["value"] if radio_options and 0 <= index < len(radio_options) else None
        
        # Ajoute les boutons radio
        radio_component = dcc.RadioItems(
            id=key,
            options=radio_options,
            value=default_value,
            className="st-radio"
        )
        
        container.children.append(radio_component)
        
        self._add_component(container)
        
        return radio_component
    
    def expander(self, label, expanded=False):
        """
        Crée une section extensible
        
        Args:
            label (str): L'étiquette de la section
            expanded (bool, optional): Si la section est étendue par défaut
        
        Returns:
            ExpanderContext: Un gestionnaire de contexte pour la section
        """
        # Crée les composants de la section
        expander_id = f"expander-{str(uuid.uuid4())[:8]}"
        content_id = f"expander-content-{str(uuid.uuid4())[:8]}"
        
        # Crée l'en-tête
        header = html.Div(
            label,
            id=expander_id,
            className="st-expander-header",
            n_clicks=0
        )
        
        # Crée le contenu
        content = html.Div(
            [],
            id=content_id,
            className="st-expander-content",
            style={"display": "block" if expanded else "none"}
        )
        
        # Crée le conteneur de la section
        expander = html.Div(
            [header, content],
            className="st-expander"
        )
        
        # Ajoute la section au conteneur actuel
        self._add_component(expander)
        
        # Ajoute un callback pour basculer la section
        self._callbacks.append((
            Output(content_id, "style"),
            Input(expander_id, "n_clicks"),
            lambda n_clicks: {"display": "block" if n_clicks % 2 == 1 else "none"} if n_clicks else {"display": "block" if expanded else "none"}
        ))
        
        # Crée un gestionnaire de contexte pour la section
        class ExpanderContext:
            def __init__(self, parent, content):
                self.parent = parent
                self.content = content
                self.original_container = parent._current_container
                self.original_stack = parent._container_stack.copy()
            
            def __enter__(self):
                # Définit le conteneur actuel sur le contenu de la section
                self.parent._container_stack.append(self.parent._current_container)
                self.parent._current_container = self.content.children
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Restaure le conteneur d'origine
                self.parent._current_container = self.parent._container_stack.pop()
        
        return ExpanderContext(self, content)
    
    def card(self, title=None):
        """
        Crée une carte
        
        Args:
            title (str, optional): Le titre de la carte
        
        Returns:
            CardContext: Un gestionnaire de contexte pour la carte
        """
        # Crée les composants de la carte
        card_id = f"card-{str(uuid.uuid4())[:8]}"
        content_id = f"card-content-{str(uuid.uuid4())[:8]}"
        
        # Crée les enfants de la carte
        card_children = []
        
        # Ajoute l'en-tête si le titre est fourni
        if title:
            header = html.Div(
                title,
                className="st-card-header"
            )
            card_children.append(header)
        
        # Crée le contenu
        content = html.Div(
            [],
            id=content_id,
            className="st-card-content"
        )
        card_children.append(content)
        
        # Crée le conteneur de la carte
        card = html.Div(
            card_children,
            id=card_id,
            className="st-card"
        )
        
        # Ajoute la carte au conteneur actuel
        self._add_component(card)
        
        # Crée un gestionnaire de contexte pour la carte
        class CardContext:
            def __init__(self, parent, content):
                self.parent = parent
                self.content = content
                self.original_container = parent._current_container
                self.original_stack = parent._container_stack.copy()
            
            def __enter__(self):
                # Définit le conteneur actuel sur le contenu de la carte
                self.parent._container_stack.append(self.parent._current_container)
                self.parent._current_container = self.content.children
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Restaure le conteneur d'origine
                self.parent._current_container = self.parent._container_stack.pop()
        
        return CardContext(self, content)
    
    def plotly_chart(self, figure, use_container_width=True, key=None):
        """
        Affiche un graphique Plotly
        
        Args:
            figure: Un graphique Plotly
            use_container_width (bool, optional): Si le graphique doit utiliser la largeur du conteneur
            key (str, optional): Une clé unique pour le graphique
        """
        if key is None:
            key = f"chart-{str(uuid.uuid4())[:8]}"
        
        # Crée le composant graphique
        graph = dcc.Graph(
            id=key,
            figure=figure,
            config={"responsive": use_container_width},
            className="st-chart",
            style={"width": "100%" if use_container_width else "auto"}
        )
        
        self._add_component(graph)
        
        return graph
    
    def dataframe(self, data, key=None):
        """
        Affiche un dataframe
        
        Args:
            data: Un DataFrame pandas
            key (str, optional): Une clé unique pour le dataframe
        """
        if key is None:
            key = f"dataframe-{str(uuid.uuid4())[:8]}"
        
        # Crée le composant tableau
        table = dash.dash_table.DataTable(
            id=key,
            data=data.to_dict('records'),
            columns=[{"name": col, "id": col} for col in data.columns],
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "padding": "8px",
                "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
            },
            style_header={
                "backgroundColor": "#f8f9fa",
                "fontWeight": "bold",
                "borderBottom": "1px solid #e0e0e0"
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#f8f9fa"
                }
            ],
            page_size=10
        )
        
        self._add_component(table)
        
        return table
    
    def metric(self, label, value, delta=None, key=None):
        """
        Affiche une métrique
        
        Args:
            label (str): L'étiquette de la métrique
            value: La valeur de la métrique
            delta: La variation de la métrique
            key (str, optional): Une clé unique pour la métrique
        """
        if key is None:
            key = f"metric-{str(uuid.uuid4())[:8]}"
        
        # Crée le conteneur de la métrique
        container = html.Div(
            className="st-metric",
            style={
                "border": "1px solid #e0e0e0",
                "borderRadius": "0.3rem",
                "padding": "1rem",
                "marginBottom": "1rem",
                "backgroundColor": "#ffffff"
            }
        )
        
        # Ajoute l'étiquette
        container.children = [
            html.Div(
                label,
                style={
                    "fontSize": "0.875rem",
                    "color": "#6c757d",
                    "marginBottom": "0.5rem"
                }
            )
        ]
        
        # Ajoute la valeur
        container.children.append(
            html.Div(
                str(value),
                style={
                    "fontSize": "1.5rem",
                    "fontWeight": "600"
                }
            )
        )
        
        # Ajoute la variation si fournie
        if delta is not None:
            delta_color = "green" if delta > 0 else "red" if delta < 0 else "gray"
            delta_symbol = "▲" if delta > 0 else "▼" if delta < 0 else ""
            
            container.children.append(
                html.Div(
                    f"{delta_symbol} {delta}",
                    style={
                        "fontSize": "0.875rem",
                        "color": delta_color,
                        "marginTop": "0.25rem"
                    }
                )
            )
        
        self._add_component(container)
        
        return container
    
    def run(self, debug=True, port=8050, **kwargs):
        """
        Exécute l'application Dash
        
        Args:
            debug (bool, optional): Si l'application doit être exécutée en mode debug
            port (int, optional): Le port sur lequel exécuter l'application
            **kwargs: Arguments supplémentaires à passer à app.run_server
        """
        # Configure la mise en page
        main_container_style = {
            "max-width": "1200px",
            "margin": "0 auto",
            "padding": "20px"
        }
        
        self.app.layout = html.Div(
            [self._dummy_div, html.Div(self._components, style={"padding": "15px"})],
            style=main_container_style
        )
        
        # Enregistre tous les callbacks
        for outputs, inputs, function in self._callbacks:
            self.app.callback(outputs, inputs)(function)
        
        # Exécute l'application
        self.app.run_server(debug=debug, port=port, **kwargs) 