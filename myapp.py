# Importación de librerías necesarias para la aplicación
import streamlit as st  # Framework para crear aplicaciones web interactivas
import pandas as pd  # Manipulación de datos
import base64  # Codificación de archivos
import matplotlib.pyplot as plt  # Creación de gráficos
import seaborn as sns  # Visualización estadística
import numpy as np  # Operaciones numéricas

# Título de la aplicación
st.title('Estadisticas de Jugadores de NBA')

# Descripción markdown de la aplicación
st.markdown("""
Esta aplicacion lo que hace es un "webscraping" de las estadisticas de los jugadores de la NBA donde seleccionamos uno (o mas) equipos, posiciones y un ano en particular y calcula un mapa de calor de como se relacionan 
* **Python libraries:** base64, pandas, streamlit
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

# Configuración de la barra lateral para selección de año
st.sidebar.header('Seleccione un Año')
selected_year = st.sidebar.selectbox('Año', list(reversed(range(1950,2024))))

# Función para cargar datos con caché de Streamlit para mejorar rendimiento
@st.cache_data
def load_data(year):
    # Construye la URL para scraping de estadísticas de la NBA
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    
    # Lee las tablas HTML de la página web
    html = pd.read_html(url, header = 0)
    df = html[0]
    
    # Limpia los datos
    raw = df.drop(df[df.Age == 'Age'].index)  # Elimina filas de encabezado repetidas
    raw = raw.fillna(0)  # Rellena valores nulos con 0
    playerstats = raw.drop(['Rk'], axis=1)  # Elimina columna de ranking
    return playerstats

# Carga los datos para el año seleccionado
playerstats = load_data(selected_year)

# Prepara la selección de equipos en la barra lateral
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Equipo', sorted_unique_team, sorted_unique_team)

# Prepara la selección de posiciones en la barra lateral
unique_pos = ['C','PF','SF','PG','SG']
selected_pos = st.sidebar.multiselect('Posicion', unique_pos, unique_pos)

# Filtra los datos según los equipos y posiciones seleccionados
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

# Muestra información sobre los datos filtrados
st.header('Estadisticas de los jugadores seleccionados')
st.write('Dimension de los datos: ' + str(df_selected_team.shape[0]) + ' Filas y ' + str(df_selected_team.shape[1]) + ' columnas.')
st.dataframe(df_selected_team)

# Función para crear enlace de descarga de archivo CSV
def filedownload(df):
    csv = df.to_csv(index=False)  # Convierte el DataFrame a CSV
    b64 = base64.b64encode(csv.encode()).decode()  # Codifica en base64
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

# Agrega un botón de descarga de CSV
st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Sección de mapa de calor de correlaciones
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    
    # Descripción del mapa de calor
    st.write('Un heatmap de la matriz de correlación podría mostrar cómo las diferentes estadísticas (como puntos por partido, asistencias, rebotes) se relacionan entre sí. Las áreas con colores más oscuros (en un gradiente de color) indican correlaciones más fuertes.')
    
    # Guarda los datos seleccionados en un CSV temporal
    df_selected_team.to_csv('output.csv',index=False)
    
    # Lee el CSV y convierte a numérico
    df = pd.read_csv('output.csv')
    df_numeric = df.apply(pd.to_numeric, errors='coerce').dropna(axis=1)
    
    # Calcula la matriz de correlación
    corr = df_numeric.corr()
    
    # Crea una máscara para mostrar solo la mitad inferior de la matriz
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    
    # Configura y muestra el mapa de calor
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(f)
