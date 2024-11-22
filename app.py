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

# Entrada do horário do fato na sidebar
st.sidebar.subheader("Selecione o Horário do Fato")
hour = st.sidebar.slider("Hora", 0, 23, 12)  # Slider para horas (0 a 23)
minute = st.sidebar.slider("Minuto", 0, 59, 0)  # Slider para minutos (0 a 59)

# Calcula o horário do fato como objeto datetime
incident_time = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(hours=hour, minutes=minute)

# Entrada do tipo de transporte na sidebar
st.sidebar.subheader("Selecione o Tipo de Transporte")
transport_mode = st.sidebar.selectbox("Transporte", list(transport_speeds.keys()))

# Instrução inicial
st.write("Clique no mapa abaixo para selecionar um ponto como o local do incidente.")

# Coordenadas iniciais: Teófilo Otoni, Minas Gerais
initial_location = [-17.8575, -41.5057]  # Coordenadas de Teófilo Otoni
m = folium.Map(location=initial_location, zoom_start=12)

# Adicionando LatLngPopup ao mapa para capturar cliques
click_marker = folium.LatLngPopup()
m.add_child(click_marker)

# Mostrando o mapa interativo
output = st_folium(m, width=700, height=500)

# Verificando se houve um clique no mapa
if output and "last_clicked" in output and output["last_clicked"] is not None:
    # Capturando as coordenadas do clique
    latitude, longitude = output["last_clicked"]["lat"], output["last_clicked"]["lng"]
    st.success(f"Coordenadas selecionadas: Latitude: {latitude}, Longitude: {longitude}")

    # Botão para calcular e gerar o mapa
    if st.sidebar.button("Gerar Mapa"):
        # Validação das entradas
        current_time = datetime.now()
        elapsed_seconds = (current_time - incident_time).total_seconds()

        if elapsed_seconds < 0:
            st.error("O horário do fato não pode ser no futuro!")
        else:
            # Calcula a distância percorrida em km
            speed_kmh = transport_speeds[transport_mode]
            elapsed_hours = elapsed_seconds / 3600  # Convertendo segundos para horas
            max_distance_km = speed_kmh * elapsed_hours

            # Gerando o mapa interativo com a mancha
            st.write(f"Distância máxima percorrida: {max_distance_km:.2f} km")

            # Ponto central
            center_point = (latitude, longitude)

            # Criando o mapa com Folium
            m = folium.Map(location=center_point, zoom_start=13)

            # Adicionando um círculo representando a mancha de mobilidade
            folium.Circle(
                location=center_point,
                radius=max_distance_km * 1000,  # Raio em metros
                color="blue",
                fill=True,
                fill_opacity=0.5,
                popup=f"Raio de {max_distance_km:.2f} km"
            ).add_to(m)

            # Renderizando o mapa atualizado no Streamlit
            st_folium(m, width=700, height=500)
else:
    st.warning("Por favor, clique em um ponto no mapa para selecionar o local.")
