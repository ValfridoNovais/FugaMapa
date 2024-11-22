import streamlit as st
from datetime import datetime, timedelta
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

# Tabela com velocidades médias (em km/h) para diferentes tipos de transporte
transport_speeds = {
    "a pé": 5,        # Velocidade média de caminhada
    "bicicleta": 15,  # Velocidade média de bicicleta
    "carro": 60,      # Velocidade média de um carro em área urbana
    "moto": 70,       # Velocidade média de uma moto
}

# Título da aplicação
st.title("Simulador de Mancha de Raio de Mobilidade")

# Sidebar para configurações
st.sidebar.header("Configurações do Simulador")

# Estado inicial para hora e minutos
if "hour" not in st.session_state:
    st.session_state.hour = 12
if "minute" not in st.session_state:
    st.session_state.minute = 0

# Ajuste de hora e minutos com sliders e botões
col1, col2 = st.sidebar.columns([1, 1])
with col1:
    if st.button("+ Hora"):
        st.session_state.hour = (st.session_state.hour + 1) % 24
    if st.button("+ Minuto"):
        st.session_state.minute = (st.session_state.minute + 1) % 60
with col2:
    if st.button("- Hora"):
        st.session_state.hour = (st.session_state.hour - 1) % 24
    if st.button("- Minuto"):
        st.session_state.minute = (st.session_state.minute - 1) % 60

# Sliders para ajustar hora e minutos
st.session_state.hour = st.sidebar.slider("Hora", 0, 23, st.session_state.hour)
st.session_state.minute = st.sidebar.slider("Minuto", 0, 59, st.session_state.minute)

# Calcula o horário do fato como objeto datetime
incident_time = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(
    hours=st.session_state.hour, minutes=st.session_state.minute
)

# Entrada do tipo de transporte na sidebar
st.sidebar.subheader("Selecione o Tipo de Transporte")
transport_mode = st.sidebar.selectbox("Transporte", list(transport_speeds.keys()))

# Coordenadas iniciais: Teófilo Otoni, Minas Gerais
initial_location = [-17.8575, -41.5057]  # Coordenadas de Teófilo Otoni

# Recuperar o ponto clicado do mapa e manter estado
if "last_clicked" not in st.session_state:
    st.session_state.last_clicked = None

# Criar o mapa inicial
m = folium.Map(location=initial_location, zoom_start=12)

# Adicionar alfinete se o ponto foi selecionado
if st.session_state.last_clicked is not None:
    latitude, longitude = st.session_state.last_clicked
    folium.Marker(
        location=(latitude, longitude),
        popup="Local Selecionado",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    # Calcular a mancha de raio se as condições forem atendidas
    current_time = datetime.now()
    elapsed_seconds = (current_time - incident_time).total_seconds()

    if elapsed_seconds >= 0:
        # Calcular a distância máxima percorrida
        speed_kmh = transport_speeds[transport_mode]
        elapsed_hours = elapsed_seconds / 3600  # Convertendo segundos para horas
        max_distance_km = speed_kmh * elapsed_hours

        # Adicionar círculo representando a mancha de mobilidade
        folium.Circle(
            location=(latitude, longitude),
            radius=max_distance_km * 1000,  # Raio em metros
            color="blue",
            fill=True,
            fill_opacity=0.5,
            popup=f"Raio de {max_distance_km:.2f} km",
        ).add_to(m)
    else:
        st.warning("O horário do fato não pode ser no futuro!")

# Adicionar funcionalidade de clique no mapa
click_marker = folium.LatLngPopup()
m.add_child(click_marker)

# Exibir o mapa interativo
output = st_folium(m, width=700, height=500)

# Capturar o clique do usuário e armazenar em `st.session_state`
if output and "last_clicked" in output and output["last_clicked"] is not None:
    st.session_state.last_clicked = (output["last_clicked"]["lat"], output["last_clicked"]["lng"])
