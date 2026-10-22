import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import heapq

INF = float("inf")

# --- LÓGICA DEL ALGORITMO DIJKSTRA ---
def dijkstra(grafo, inicial):
    distancia = {v: INF for v in grafo}
    visitado = {v: False for v in grafo}
    previo = {v: None for v in grafo}
    
    distancia[inicial] = 0
    Q = [(0, inicial)]

    while Q:
        distancia_actual, actual = heapq.heappop(Q)
        if visitado[actual]:
            continue
        visitado[actual] = True

        for adyacente, peso in grafo[actual]:
            if not visitado[adyacente]:
                if distancia[actual] + peso < distancia[adyacente]:
                    distancia[adyacente] = distancia[actual] + peso
                    previo[adyacente] = actual
                    heapq.heappush(Q, (distancia[adyacente], adyacente))

    return distancia, previo

def obtener_camino(previo, destino):
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        actual = previo.get(actual)
    camino.reverse()
    return camino

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Rutas de Guatemala - Dijkstra", layout="wide")
st.title("🇬🇹 Red Vial de Guatemala - Algoritmo de Dijkstra")

st.sidebar.header("Configuración del Grafo")

# Diccionario con Posiciones X, Y aproximadas en el mapa geográfico de Guatemala
# (Coordenadas fijadas para que se mantengan ordenadas sobre la imagen de fondo)
POSICIONES_GEOGRAFICAS = {
    "Peten": (0, -280),
    "Flores": (20, -320),
    "Sayaxche": (-30, -220),
    "Alta_Verapaz": (10, -100),
    "Coban": (-20, -110),
    "Baja_Verapaz": (-10, -40),
    "Izabal": (180, -100),
    "Puerto_Barrios": (220, -110),
    "Zacapa": (130, -30),
    "Chiquimula": (140, 20),
    "El_Progreso": (60, -30),
    "Jalapa": (80, 40),
    "Jutiapa": (110, 110),
    "Santa_Rosa": (40, 120),
    "Escuintla": (-30, 120),
    "Puerto_Quetzal": (-30, 160),
    "Guatemala": (20, 30),
    "Mixco": (0, 30),
    "Villa_Nueva": (15, 50),
    "Sacatepequez": (-15, 40),
    "Chimaltenango": (-40, 20),
    "Solola": (-90, 20),
    "Quiche": (-60, -60),
    "Huehuetenango": (-140, -80),
    "San_Marcos": (-180, -20),
    "Quetzaltenango": (-130, 10),
    "Totonicapan": (-110, -10),
    "Retalhuleu": (-150, 60),
    "Suchitepequez": (-100, 70),
    "Coatepeque": (-170, 40),
    "Mazatenango": (-90, 80)
}

# Entrada predeterminada de los 31 Nodos
default_vertices = ", ".join(POSICIONES_GEOGRAFICAS.keys())

# Aristas ordenadas con distancias reales/aproximadas
default_edges = """
Peten Flores 1
Peten Sayaxche 2
Peten Alta_Verapaz 4
Peten Izabal 7
Flores Sayaxche 2
Alta_Verapaz Coban 1
Alta_Verapaz Baja_Verapaz 3
Alta_Verapaz Izabal 5
Alta_Verapaz Quiche 6
Izabal Puerto_Barrios 2
Izabal Zacapa 4
Zacapa Chiquimula 2
Zacapa El_Progreso 5
Chiquimula Jalapa 3
Chiquimula Jutiapa 5
El_Progreso Guatemala 4
El_Progreso Jalapa 3
Jalapa Jutiapa 4
Jutiapa Santa_Rosa 4
Santa_Rosa Guatemala 3
Santa_Rosa Escuintla 3
Escuintla Puerto_Quetzal 2
Escuintla Villa_Nueva 3
Guatemala Mixco 1
Guatemala Villa_Nueva 1
Mixco Sacatepequez 1
Sacatepequez Chimaltenango 2
Chimaltenango Solola 4
Chimaltenango Quiche 5
Solola Totonicapan 2
Solola Quetzaltenango 3
Totonicapan Quetzaltenango 1
Totonicapan Huehuetenango 3
Huehuetenango Quiche 4
Huehuetenango San_Marcos 5
Quetzaltenango San_Marcos 3
Quetzaltenango Retalhuleu 3
Quetzaltenango Coatepeque 4
San_Marcos Coatepeque 3
Retalhuleu Suchitepequez 2
Suchitepequez Mazatenango 1
Suchitepequez Escuintla 4
"""

# Entradas en la barra lateral
vertices_input = st.sidebar.text_input("Departamentos y Nodos:", default_vertices)
lista_vertices = [v.strip() for v in vertices_input.split(",") if v.strip()]

st.sidebar.subheader("Conexiones y Pesos")
aristas_input = st.sidebar.text_area("Lista de Aristas:", default_edges, height=180)

# Imagen del mapa vectorial blanco/transparente de Guatemala
mapa_fondo_url = st.sidebar.text_input(
    "URL del Mapa de Fondo:",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Guatemala_departments_blank.svg/800px-Guatemala_departments_blank.svg.png"
)

# Construcción del Grafo
grafo = {v: [] for v in lista_vertices}
for linea in aristas_input.strip().split("\n"):
    partes = linea.split()
    if len(partes) == 3:
        u, v, w = partes[0].strip(), partes[1].strip(), partes[2].strip()
        if u in grafo and v in grafo:
            try:
                peso = int(w)
                grafo[u].append((v, peso))
                grafo[v].append((u, peso))
            except ValueError:
                pass

# Selección de Origen y Destino
col1, col2 = st.columns(2)
with col1:
    nodo_inicial = st.selectbox("Origen:", lista_vertices if lista_vertices else [""])
with col2:
    nodo_destino = st.selectbox("Destino:", lista_vertices if lista_vertices else [""])

if st.button("🚀 Calcular Ruta Más Corta", type="primary"):
    total_nodos = len(lista_vertices)
    if total_nodos < 31:
        st.warning(f"⚠️ El grafo tiene {total_nodos} nodos. La rúbrica requiere mínimo 31 nodos.")
    else:
        st.success(f"✅ Requisito cumplido: {total_nodos} nodos ordenados en el mapa de Guatemala.")

    if nodo_inicial and nodo_destino and nodo_inicial in grafo and nodo_destino in grafo:
        distancia, previo = dijkstra(grafo, nodo_inicial)
        
        if distancia[nodo_destino] != INF:
            camino = obtener_camino(previo, nodo_destino)
            st.success(f"**Ruta encontrada:** {' ➔ '.join(camino)}")
            st.info(f"**Costo Total:** {distancia[nodo_destino]}")
        else:
            camino = []
            st.error(f"No hay conexión entre {nodo_inicial} y {nodo_destino}.")

        # --- VISUALIZACIÓN ORDENADA EN PYVIS ---
        net = Network(height="700px", width="100%", bgcolor="rgba(0,0,0,0)", font_color="white", directed=False)
        
        # Desactivar física libre para mantener las posiciones fijas y limpias
        net.set_options("""
        var options = {
          "physics": { "enabled": false },
          "nodes": {
             "font": { "size": 15, "face": "arial", "color": "#ffffff", "strokeWidth": 4, "strokeColor": "#000000" },
             "borderWidth": 2,
             "shadow": true
          },
          "edges": {
             "smooth": { "type": "continuous" },
             "font": { "size": 13, "color": "#00ffff", "strokeWidth": 4, "strokeColor": "#000000" },
             "shadow": true
          }
        }
        """)

        # Agregar nodos con coordenadas fijas (X, Y)
        for nodo in grafo:
            color = "#ff2e63" if nodo in camino else "#00adb5"
            size = 22 if nodo in camino else 14
            
            # Si el nodo tiene coordenada asignada, se fija su posición
            if nodo in POSICIONES_GEOGRAFICAS:
                x, y = POSICIONES_GEOGRAFICAS[nodo]
                net.add_node(nodo, label=nodo, color=color, size=size, x=x, y=y, physics=False)
            else:
                net.add_node(nodo, label=nodo, color=color, size=size)

        aristas_camino = set(zip(camino, camino[1:]))
        aristas_camino |= set((b, a) for a, b in aristas_camino)

        aristas_agregadas = set()
        for origen in grafo:
            for dest, peso in grafo[origen]:
                pair = tuple(sorted([origen, dest]))
                if pair not in aristas_agregadas:
                    aristas_agregadas.add(pair)
                    if (origen, dest) in aristas_camino:
                        net.add_edge(origen, dest, value=peso, title=f"Distancia: {peso}", label=str(peso), color="#ff2e63", width=6)
                    else:
                        net.add_edge(origen, dest, value=peso, title=f"Distancia: {peso}", label=str(peso), color="rgba(0, 0, 0, 0.4)", width=1.5)

        html_file = "dijkstra_guatemala_ordenado.html"
        net.save_graph(html_file)
        
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Fondo con mapa estilizado
        custom_css = f"""
        <style>
        #mynetwork {{
            background-image: linear-gradient(rgba(240, 244, 248, 0.85), rgba(240, 244, 248, 0.85)), url('{mapa_fondo_url}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            border-radius: 12px;
            border: 2px solid #ccc;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        </style>
        """
        
        components.html(custom_css + html_content, height=720)
    else:
        st.warning("Selecciona nodos de origen y destino válidos.")
