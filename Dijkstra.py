import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import heapq
import base64
import os

st.set_page_config(page_title="Optimizador de Rutas - Dijkstra (Guatemala)", layout="wide")

# ---------------------------------------------------------
# 1. Función para codificar la imagen del mapa en Base64
# ---------------------------------------------------------
def obtener_imagen_base64(ruta_imagen):
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    return None

# ---------------------------------------------------------
# 2. Algoritmo de Dijkstra y Reconstrucción de Ruta
# ---------------------------------------------------------
def dijkstra(grafo, inicial):
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicial] = 0
    previo = {nodo: None for nodo in grafo}
    pq = [(0, inicial)]

    while pq:
        dist_actual, u = heapq.heappop(pq)

        if dist_actual > distancias[u]:
            continue

        for v, peso in grafo[u]:
            dist = dist_actual + peso
            if dist < distancias[v]:
                distancias[v] = dist
                previo[v] = u
                heapq.heappush(pq, (dist, v))

    return distancias, previo

def obtener_camino(previo, destino):
    camino = []
    actual = destino
    while actual is not None:
        camino.insert(0, actual)
        actual = previo[actual]
    return camino

# ---------------------------------------------------------
# 3. Coordenadas Geográficas para los 45 Vértices
# ---------------------------------------------------------
POSICIONES_GEOGRAFICAS = {
    # Región Metropolitana y Central
    "Guatemala": (0, 0), "Mixco": (-40, -20), "Villa_Nueva": (10, 40), 
    "Petapa": (25, 20), "San_Lucas": (-70, -10), "Amatitlan": (20, 60),
    "Villa_Canales": (35, 40), "Sanarate": (80, -40), "Guastatoya": (90, -70),
    
    # Occidente y Altiplano
    "Antigua_Guatemala": (-90, 20), "Chimaltenango": (-110, -10), "Tecpan": (-130, -30),
    "Patzun": (-120, 10), "Solola": (-170, 0), "Totonicapan": (-200, -40),
    "Quetzaltenango": (-230, -20), "Coatepeque": (-260, 40), "San_Marcos": (-270, -60),
    "Malacatan": (-290, -40), "Huehuetenango": (-220, -130), "Quiche_Cruz": (-150, -90),
    
    # Sur / Costa Sur
    "Escuintla": (0, 100), "Santa_Lucia": (-50, 90), "Tiquisate": (-90, 120),
    "Mazatenango": (-140, 100), "Retalhuleu": (-180, 110), "Cocales": (-100, 95),
    "Puerto_San_Jose": (15, 160), "Iztapa": (35, 170), "Palin": (10, 80),
    "Cuilapa": (60, 90), "Jutiapa": (110, 110), "Jalapa": (90, 10),
    
    # Oriente y Norte
    "Chiquimula": (150, -10), "Esquipulas": (170, 40), "Jocotan": (160, -20),
    "Zacapa": (130, -40), "Puerto_Barrios": (220, -110), "Livingston": (200, -130),
    "Coban": (20, -160), "San_Pedro_Carcha": (35, -170), "Salamá": (40, -100),
    "Flores_Peten": (0, -320), "Melchor": (70, -310), "Poptun": (40, -240)
}

# ---------------------------------------------------------
# Interfaz Gráfica con Streamlit
# ---------------------------------------------------------
st.title("🇬🇹 Optimizador de Red Vial de Guatemala - Dijkstra (45 Nodos)")
st.markdown("---")

st.sidebar.header("⚙️ Configuración de la Red")
st.sidebar.info(f"Vértices configurados en el sistema: **{len(POSICIONES_GEOGRAFICAS)}**")

# Definición de Conexiones Base (Aristas ponderadas en kilómetros o costo)
aristas_base = [
    ("Guatemala", "Mixco", 18), ("Guatemala", "Villa_Nueva", 22), ("Guatemala", "Petapa", 15),
    ("Guatemala", "San_Lucas", 28), ("Guatemala", "Sanarate", 52), ("San_Lucas", "Antigua_Guatemala", 25),
    ("Antigua_Guatemala", "Chimaltenango", 24), ("Chimaltenango", "Tecpan", 29), ("Chimaltenango", "Patzun", 22),
    ("Tecpan", "Solola", 55), ("Solola", "Totonicapan", 35), ("Totonicapan", "Quetzaltenango", 28),
    ("Quetzaltenango", "Coatepeque", 48), ("Quetzaltenango", "San_Marcos", 45), ("San_Marcos", "Malacatan", 32),
    ("Guatemala", "Escuintla", 58), ("Escuintla", "Santa_Lucia", 30), ("Santa_Lucia", "Cocales", 15),
    ("Cocales", "Mazatenango", 40), ("Mazatenango", "Retalhuleu", 20), ("Retalhuleu", "Coatepeque", 35),
    ("Escuintla", "Puerto_San_Jose", 45), ("Puerto_San_Jose", "Iztapa", 15), ("Escuintla", "Palin", 15),
    ("Palin", "Amatitlan", 12), ("Amatitlan", "Villa_Canales", 18), ("Guatemala", "Cuilapa", 60),
    ("Cuilapa", "Jutiapa", 55), ("Guatemala", "Jalapa", 90), ("Jalapa", "Chiquimula", 65),
    ("Chiquimula", "Esquipulas", 45), ("Chiquimula", "Jocotan", 20), ("Chiquimula", "Zacapa", 25),
    ("Zacapa", "Puerto_Barrios", 150), ("Puerto_Barrios", "Livingston", 25), ("Guatemala", "Salama", 95),
    ("Salama", "Coban", 75), ("Coban", "San_Pedro_Carcha", 8), ("Coban", "Flores_Peten", 210),
    ("Flores_Peten", "Melchor", 90), ("Flores_Peten", "Poptun", 100), ("Poptun", "Chiquimula", 180),
    ("Guastatoya", "Zacapa", 55), ("Guastatoya", "Sanarate", 15), ("Huehuetenango", "Quetzaltenango", 85),
    ("Quiche_Cruz", "Huehuetenango", 70), ("Quiche_Cruz", "Coban", 95)
]

# Construcción del Grafo en memoria
grafo = {nodo: [] for nodo in POSICIONES_GEOGRAFICAS.keys()}
for u, v, peso in aristas_base:
    if u in grafo and v in grafo:
        grafo[u].append((v, peso))
        grafo[v].append((u, peso))  # Grafo no dirigido

# Selectores de Origen y Destino
nodos_lista = sorted(list(POSICIONES_GEOGRAFICAS.keys()))
col1, col2 = st.sidebar.columns(2)
origen = col1.selectbox("Origen", nodos_lista, index=nodos_lista.index("Guatemala") if "Guatemala" in nodos_lista else 0)
destino = col2.selectbox("Destino", nodos_lista, index=nodos_lista.index("Flores_Peten") if "Flores_Peten" in nodos_lista else 1)

calcular = st.sidebar.button("🚀 Calcular Ruta Óptima", type="primary")

# ---------------------------------------------------------
# Ejecución y Visualización
# ---------------------------------------------------------
if calcular:
    distancias, previo = dijkstra(grafo, origen)
    camino_optimo = obtener_camino(previo, destino)
    costo_total = distancias[destino]

    if costo_total == float('inf'):
        st.error(f"❌ No existe una ruta alcanzable desde **{origen}** hasta **{destino}**.")
    else:
        st.success(f"✅ ¡Ruta más corta calculada con éxito desde **{origen}** hasta **{destino}**!")
        st.metric(label="🛣️ Distancia / Costo Total Acumulado", value=f"{costo_total} km")
        st.write(f"**Secuencia exacta de la ruta:** `{' ➔ '.join(camino_optimo)}`")

# Creación de la Red Interactiva con Pyvis y Fondo del Mapa
net = Network(height="650px", width="100%", bgcolor="#1e1e1e", font_color="white")
net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=95)

# Determinar nodos que forman parte del camino óptimo si se calculó
camino_actual = obtener_camino(previo, destino) if 'previo' in locals() and costo_total != float('inf') else []

for nodo, (x, y) in POSICIONES_GEOGRAFICAS.items():
    if nodo in camino_actual:
        color = "#ff2e63"  # Rojo brillante para la ruta óptima
        size = 25
    elif nodo == origen:
        color = "#00adb5"  # Celeste para el origen
        size = 22
    elif nodo == destino:
        color = "#f39c12"  # Naranja para el destino
        size = 22
    else:
        color = "#a6a6a6"  # Gris neutral para el resto de los 45 nodos
        size = 14

    net.add_node(nodo, label=nodo.replace("_", " "), x=x*3, y=y*3, color=color, size=size, fixed=False)

for u, v, peso in aristas_base:
    if any((u in camino_actual and v in camino_actual and abs(camino_actual.index(u) - camino_actual.index(v)) == 1)):
        net.add_edge(u, v, color="#ff2e63", width=5, title=f"Peso: {peso} km (Ruta Óptima)")
    else:
        net.add_edge(u, v, color="#444444", width=1, title=f"Peso: {peso} km")

# Renderizar mapa de fondo con Base64
mapa_base64 = obtener_imagen_base64("mapa.png")
if mapa_base64:
    mapa_url = f"data:image/png;base64,{mapa_base64}"
    estilo_fondo = f"""
    <style>
        body {{
            background-image: url('{mapa_url}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            background-color: transparent !important;
            margin: 0;
        }}
    </style>
    """
else:
    estilo_fondo = ""

net.save_graph("dijkstra_mapa.html")

with open("dijkstra_mapa.html", "r", encoding="utf-8") as f:
    html_content = f.read()

html_final = html_content.replace("</head>", f"{estilo_fondo}</head>")

st.subheader("🗺️ Mapa Interactivo de la Red Vial (Guatemala - 45 Nodos)")
components.html(html_final, height=670, scrolling=False)
