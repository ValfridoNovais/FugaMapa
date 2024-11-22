import streamlit as st
from datetime import datetime, timedelta
import pytz  # Para ajuste de fuso horário
import folium
from streamlit_folium import st_folium

# Configurar o fuso horário da região
LOCAL_TZ = pytz.timezone("America/Sao_Paulo")  # Substitua pelo fuso horário correto, se necessário

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
    st.session_state.hour = datetime.now(LOCAL_TZ).hour  # Hora atual no fuso horário local
if "minute" not in st.session_state:
    st.session_state.minute = datetime.now(LOCAL_TZ).minute  # Minuto atual no fuso horário local
if "radius_layer" not in st.session_state:
    st.session_state.radius_layer = None  # Camada inicial da mancha de raio
if "is_processing_click" not in st.session_state:
    st.session_state.is_processing_click = False  # Estado do indicador de carregamento

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
    # Capturar o horário atual e o horário do fato no mesmo fuso horário
    current_time = datetime.now(LOCAL_TZ)  # Horário atual no fuso local
    incident_time = datetime.now(LOCAL_TZ).replace(hour=st.session_state.hour, minute=st.session_state.minute, second=0, microsecond=0)

    # Calcular o tempo decorrido em segundos
    elapsed_seconds = (current_time - incident_time).total_seconds()

    # Verificar se há um ponto clicado e o tempo decorrido é válido
    if st.session_state.last_clicked:
        if elapsed_seconds >= 0:
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
        else:
            st.error("O horário do fato está no futuro! Por favor, escolha um horário válido.")
    else:
        st.error("Por favor, selecione um ponto no mapa antes de atualizar.")

# Exibir indicador de processamento, se necessário
if st.session_state.is_processing_click:
    st.info("Capturando ponto no mapa... Aguarde!")

# Criar o mapa com o centro atual
m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.zoom)

# Adicionar marcador do local clicado, se houver
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

# Registrar clique no mapa
output = st_folium(m, width=700, height=500)

if output and "last_clicked" in output and output["last_clicked"] is not None:
    st.session_state.is_processing_click = True  # Ativar indicador de carregamento
    latitude, longitude = output["last_clicked"]["lat"], output["last_clicked"]["lng"]
    st.session_state.last_clicked = (latitude, longitude)
    st.session_state.map_center = [latitude, longitude]
    st.session_state.is_processing_click = False  # Desativar após capturar o ponto

# Atualizar zoom se o usuário o modificar
if output and "zoom" in output:
    st.session_state.zoom = output["zoom"]
