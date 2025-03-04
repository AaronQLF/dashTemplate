import pandas as pd
from streamlit_dash import OutilMiseEnPage
# Example usage
# Example usage
df = pd.DataFrame({
    'region': ['North', 'North', 'South', 'South'],
    'country': ['USA', 'Canada', 'Brazil', 'Argentina'],
    'city': ['New York', 'Toronto', 'Sao Paulo', 'Buenos Aires'],
    'sales': [100, 200, 150, 250],
    'quantity': [10, 20, 15, 25]
})

app = OutilMiseEnPage()

app.powerbi_matrix(
    data=df,
    group_by=['region', 'country', 'city'],
    metrics={
        'sales': 'sum',
        'quantity': 'sum'
    }
)

app.run()