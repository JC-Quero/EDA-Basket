#Importamos las librerias
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('Estadisticas de Jugadores de NBA')

st.markdown("""
Esta aplicacion lo que hace es un "webscraping" de las estadisticas de los jugadores de la NBA donde seleccionamos uno (o mas) equipos, posiciones y un ano en particular y calcula un mapa de calor de como se relacionan 
* **Python libraries:** base64, pandas, streamlit
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

#SideBar
st.sidebar.header('Seleccione un Año')
selected_year = st.sidebar.selectbox('Año', list(reversed(range(1950,2024))))

# Web scraping
@st.cache_data
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header = 0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats
playerstats = load_data(selected_year)

# Sidebar - Elegimos Equipo
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Equipo', sorted_unique_team, sorted_unique_team)

# Sidebar - Posicion
unique_pos = ['C','PF','SF','PG','SG']
selected_pos = st.sidebar.multiselect('Posicion', unique_pos, unique_pos)

# Filtramos los datos
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.header('Estadisticas de los jugadores seleccionados')
st.write('Dimension de los datos: ' + str(df_selected_team.shape[0]) + ' Filas y ' + str(df_selected_team.shape[1]) + ' columnas.')
st.dataframe(df_selected_team)

#Descargamos los datos de las estadisticas de los jugadores
#(Ayuda) https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    st.write('Un heatmap de la matriz de correlación podría mostrar cómo las diferentes estadísticas (como puntos por partido, asistencias, rebotes) se relacionan entre sí. Las áreas con colores más oscuros (en un gradiente de color) indican correlaciones más fuertes.')
    df_selected_team.to_csv('output.csv',index=False)
    df = pd.read_csv('output.csv')

    df_numeric = df.apply(pd.to_numeric, errors='coerce').dropna(axis=1)


    corr = df_numeric.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(f)

