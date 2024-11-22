import streamlit as st
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

# Tabela com velocidades médias (em km/h) para diferentes tipos de transporte
transport_speeds = {
    "a pé": 5,        # Velocidade média de caminhada
    "bicicleta": 15,  # Velocidade média de bicicleta
    "carro": 60,      # Velocidade média de um carro em área urbana
    "moto": 70,       # Velocidade média de uma moto
}

# Inicializando variáveis no session_state
if "zoom" not in st.session_state:
    st.session_state.zoom = 12
if "last_clicked" not in st.session_state:
    st.session_state.last_clicked = None
if "map_center" not in st.session_state:
    st.session_state.map_center = [-17.8575, -41.5057]
if "hour" not in st.session_state:
    st.session_state.hour = datetime.now().hour  # Hora atual
if "minute" not in st.session_state:
    st.session_state.minute = datetime.now().minute  # Minuto atual
if "radius_layer" not in st.session_state:
    st.session_state.radius_layer = None  # Camada inicial da mancha de raio

# Criar a interface
st.title("Simulador de Mancha de Raio de Mobilidade")

# Sidebar para configurações
st.sidebar.header("Configurações do Simulador")

# Ajuste de hora e minutos com selectbox
st.session_state.hour = st.sidebar.selectbox(
    "Hora do Fato", list(range(24)), index=st.session_state.hour
)
st.session_state.minute = st.sidebar.selectbox(
    "Minuto do Fato", list(range(60)), index=st.session_state.minute
)

# Escolha do transporte
transport_mode = st.sidebar.selectbox("Selecione o Tipo de Transporte", list(transport_speeds.keys()))

# Botão de atualização
if st.sidebar.button("Atualizar Mancha de Raio"):
    current_time = datetime.now()
    incident_time = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(
        hours=st.session_state.hour, minutes=st.session_state.minute
    )
    elapsed_seconds = (current_time - incident_time).total_seconds()

    if st.session_state.last_clicked and elapsed_seconds >= 0:
        latitude, longitude = st.session_state.last_clicked
        speed_kmh = transport_speeds[transport_mode]
        elapsed_hours = elapsed_seconds / 3600
        max_distance_km = speed_kmh * elapsed_hours

        # Atualizar a camada de raio no session_state
        st.session_state.radius_layer = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": max_distance_km * 1000,  # Convertendo para metros
            "popup": f"Raio de {max_distance_km:.2f} km"
        }

# Criar o mapa com o centro atual
m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.zoom)

# Adicionar funcionalidade de clique no mapa
click_marker = folium.LatLngPopup()
m.add_child(click_marker)

# Adicionar marcador do local clicado
if st.session_state.last_clicked:
    latitude, longitude = st.session_state.last_clicked
    folium.Marker(
        location=(latitude, longitude),
        popup="Local Selecionado",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

# Adicionar a mancha de raio ao mapa, se existir
if st.session_state.radius_layer:
    folium.Circle(
        location=(st.session_state.radius_layer["latitude"], st.session_state.radius_layer["longitude"]),
        radius=st.session_state.radius_layer["radius"],
        color="blue",
        fill=True,
        fill_opacity=0.5,
        popup=st.session_state.radius_layer["popup"]
    ).add_to(m)

# Mostrar o mapa no Streamlit
output = st_folium(m, width=700, height=500)

# Atualizar estado com base no clique do usuário
if output and "last_clicked" in output and output["last_clicked"] is not None:
    st.session_state.last_clicked = (output["last_clicked"]["lat"], output["last_clicked"]["lng"])
    st.session_state.map_center = [output["last_clicked"]["lat"], output["last_clicked"]["lng"]]

# Atualizar zoom se o usuário o modificar
if output and "zoom" in output:
    st.session_state.zoom = output["zoom"]
