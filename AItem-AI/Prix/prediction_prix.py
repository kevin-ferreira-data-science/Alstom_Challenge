import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import plotly.graph_objects as go

# Charger les données
df = pd.read_csv('prices.csv')

# Préparer les données pour l'entraînement
X = np.arange(len(df['Date'])).reshape(-1, 1)  # Utilisation de np.arange et redimensionnement
y = df['Prix']

# Diviser les données en ensemble d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Entraîner le modèle
model = LinearRegression()  
model.fit(X_train, y_train)

# Prédire les prix
y_pred = model.predict(X_test)

# Afficher les erreurs
print('Erreur absolue moyenne:', metrics.mean_absolute_error(y_test, y_pred)) 
print('Erreur quadratique moyenne:', metrics.mean_squared_error(y_test, y_pred)) 
print('Erreur quadratique moyenne racine:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))

# Créer un graphique avec plotly
fig = go.Figure()

# Ajouter les données réelles
fig.add_trace(go.Scatter(x=df['Date'], y=y_test, mode='markers', name='Données réelles'))

# Ajouter les prédictions
fig.add_trace(go.Scatter(x=df['Date'].iloc[X_test.flatten()], y=y_pred, mode='lines', name='Prédictions'))

# Afficher le graphique
fig.show()
