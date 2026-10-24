import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import heapq
import base64
import os

st.set_page_config(page_title="Optimizador de Rutas - Dijkstra (Guatemala Real)", layout="wide")

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
# 3. Coordenadas Geográficas Reales (Escala para Mapa de Guatemala)
# ---------------------------------------------------------
POSICIONES_GEOGRAFICAS = {
    # Región Central y Metropolitana
    "Guatemala": (0, 20), "Mixco": (-25, 15), "Villa_Nueva": (0, 45), 
    "Petapa": (15, 35), "San_Lucas": (-45, 20), "Amatitlan": (-5, 55),
    "Villa_Canales": (20, 45), "Sanarate": (45, -5), "Guastatoya": (40, -25),
    
    # Occidente y Altiplano
    "Antigua_Guatemala": (-55, 25), "Chimaltenango": (-75, 10), "Tecpan": (-90, -5),
    "Patzun": (-80, 20), "Solola": (-120, 15), "Totonicapan": (-140, -10),
    "Quetzaltenango": (-160, 10), "Coatepeque": (-190, 45), "San_Marcos": (-200, -15),
    "Malacatan": (-220, 0), "Huehuetenango": (-160, -70), "Quiche_Cruz": (-100, -50),
    
    # Sur / Costa Sur
    "Escuintla": (-10, 80), "Santa_Lucia": (-45, 75), "Tiquisate": (-85, 95),
    "Mazatenango": (-110, 80), "Retalhuleu": (-140, 85), "Cocales": (-75, 80),
    "Puerto_San_Jose": (-10, 125), "Iztapa": (15, 125), "Palin": (-5, 68),
    "Cuilapa": (25, 75), "Jutiapa": (60, 95), "Jalapa": (55, 30),
    
    # Oriente y Norte
    "Chiquimula": (95, 20), "Esquipulas": (110, 55), "Jocotan": (105, 5),
    "Zacapa": (85, -15), "Puerto_Barrios": (150, -95), "Livingston": (130, -105),
    "Coban": (10, -85), "San_Pedro_Carcha": (25, -95), "Salamá": (20, -45),
    "Flores_Peten": (10, -230), "Melchor": (75, -215), "Poptun": (55, -165)
}

# ---------------------------------------------------------
# Interfaz Gráfica con Streamlit
# ---------------------------------------------------------
st.title("🇬🇹 Optimizador de Red Vial de Guatemala - Dijkstra (45 Nodos Geográficos)")
st.markdown("---")

st.sidebar.header("⚙️ Configuración de la Red")
st.sidebar.info(f"Vértices geográficos configurados: **{len(POSICIONES_GEOGRAFICAS)}**")

# Conexiones con distancias reales aproximadas en kilómetros
aristas_base = [
    ("Guatemala", "Mixco", 18), ("Guatemala", "Villa_Nueva", 22), ("Guatemala", "Petapa", 15),
    ("Guatemala", "San_Lucas", 28), ("Guatemala", "Sanarate", 52), ("San_Lucas", "Antigua_Guatemala", 15),
    ("Antigua_Guatemala", "Chimaltenango", 24), ("Chimaltenango", "Tecpan", 29), ("Chimaltenango", "Patzun", 22),
    ("Tecpan", "Solola", 45), ("Solola", "Totonicapan", 35), ("Totonicapan", "Quetzaltenango", 28),
    ("Quetzaltenango", "Coatepeque", 48), ("Quetzaltenango", "San_Marcos", 45), ("San_Marcos", "Malacatan", 32),
    ("Guatemala", "Escuintla", 58), ("Escuintla", "Santa_Lucia", 30), ("Santa_Lucia", "Cocales", 15),
    ("Cocales", "Mazatenango", 40), ("Mazatenango", "Retalhuleu", 20), ("Retalhuleu", "Coatepeque", 35),
    ("Escuintla", "Puerto_San_Jose", 45), ("Puerto_San_Jose", "Iztapa", 15), ("Escuintla", "Palin", 15),
    ("Palin", "Amatitlan", 12), ("Amatitlan", "Villa_Canales", 18), ("Guatemala", "Cuilapa", 60),
    ("Cuilapa", "Jutiapa", 55), ("Guatemala", "Jalapa", 90), ("Jalapa", "Chiquimula", 65),
    ("Chiquimula", "Esquipulas", 45), ("Chiquimula", "Jocotan", 20), ("Chiquimula", "Zacapa", 25),
    ("Zacapa", "Puerto_Barrios", 150), ("Puerto_Barrios", "Livingston", 25), ("Guatemala", "Salamá", 95),
    ("Salamá", "Coban", 75), ("Coban", "San_Pedro_Carcha", 8), ("Coban", "Flores_Peten", 280),
    ("Flores_Peten", "Melchor", 90), ("Flores_Peten", "Poptun", 100), ("Poptun", "Chiquimula", 195),
    ("Guastatoya", "Zacapa", 55), ("Guastatoya", "Sanarate", 15), ("Huehuetenango", "Quetzaltenango", 85),
    ("Quiche_Cruz", "Huehuetenango", 70), ("Quiche_Cruz", "Coban", 95), ("Quiche_Cruz", "Tecpan", 65)
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
# Ejecución y Control de Estado de la Ruta
# ---------------------------------------------------------
camino_actual = []
costo_total = float('inf')

if calcular:
    distancias, previo = dijkstra(grafo, origen)
    costo_total = distancias[destino]

    if costo_total == float('inf'):
        st.error(f"❌ No existe una ruta alcanzable desde **{origen}** hasta **{destino}**.")
    else:
        camino_actual = obtener_camino(previo, destino)
        st.success(f"✅ ¡Ruta más corta calculada con éxito desde **{origen}** hasta **{destino}**!")
        st.metric(label="🛣️ Distancia / Costo Total Acumulado (Km)", value=f"{costo_total} km")
        st.write(f"**Secuencia exacta de la ruta:** `{' ➔ '.join(camino_actual)}`")

# ---------------------------------------------------------
# Creación de la Red Interactiva con Pyvis y Coordenadas Reales
# ---------------------------------------------------------
net = Network(height="650px", width="100%", bgcolor="#1e1e1e", font_color="white")

for nodo, (x, y) in POSICIONES_GEOGRAFICAS.items():
    if nodo in camino_actual:
        color = "#ff2e63"  # Rojo brillante para la ruta óptima
        size = 26
    elif nodo == origen:
        color = "#00adb5"  # Celeste para el origen
        size = 22
    elif nodo == destino:
        color = "#f39c12"  # Naranja para el destino
        size = 22
    else:
        color = "#a6a6a6"  # Gris neutral para los demás nodos
        size = 13

    # Fijamos las coordenadas x e y para que respeten la forma real del mapa
    net.add_node(nodo, label=nodo.replace("_", " "), x=x*4, y=y*4, color=color, size=size, physics=False)

for u, v, peso in aristas_base:
    es_camino = False
    if len(camino_actual) > 1:
        for i in range(len(camino_actual) - 1):
            if (u == camino_actual[i] and v == camino_actual[i+1]) or (v == camino_actual[i] and u == camino_actual[i+1]):
                es_camino = True
                break

    if es_camino:
        net.add_edge(u, v, color="#ff2e63", width=5, title=f"Distancia: {peso} km (Ruta Óptima)")
    else:
        net.add_edge(u, v, color="#444444", width=1, title=f"Distancia: {peso} km")

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

st.subheader("🗺️ Mapa Geográfico Interactivo de la Red Vial de Guatemala")
components.html(html_final, height=670, scrolling=False)
