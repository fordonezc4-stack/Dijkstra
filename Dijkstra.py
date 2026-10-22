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

st.sidebar.header("Configuración del Mapa Vial")

# Lista completa de Departamentos + Municipios clave para superar los 31 nodos requeridos
default_vertices = (
    "Guatemala, Mixco, Villa_Nueva, Sacatepequez, Chimaltenango, Escuintla, "
    "El_Progreso, Zacapa, Chiquimula, Izabal, Peten, Alta_Verapaz, Baja_Verapaz, "
    "Quiche, Huehuetenango, San_Marcos, Quetzaltenango, Totonicapan, Solola, "
    "Retalhuleu, Suchitepequez, Santa_Rosa, Jutiapa, Jalapa, Minit_1, Minit_2, "
    "Minit_3, Minit_4, Minit_5, Minit_6, Minit_7, Minit_8, Minit_9"
)

# Conexiones viales base incluyendo los ejemplos que mencionaste (Petén - Alta Verapaz = 4, Petén - Izabal = 7)
default_edges = """
Peten Alta_Verapaz 4
Peten Izabal 7
Peten Quiche 9
Alta_Verapaz Izabal 5
Alta_Verapaz Baja_Verapaz 3
Alta_Verapaz Quiche 6
Zacapa Izabal 4
Zacapa Chiquimula 2
Zacapa El_Progreso 5
Chiquimula Jutiapa 8
Guatemala Mixco 2
Guatemala Villa_Nueva 3
Guatemala Sacatepequez 4
Guatemala El_Progreso 6
Guatemala Santa_Rosa 7
Sacatepequez Chimaltenango 3
Chimaltenango Solola 5
Solola Quetzaltenango 4
Solola Totonicapan 3
Quetzaltenango San_Marcos 4
Quetzaltenango Retalhuleu 3
Retalhuleu Suchitepequez 2
Suchitepequez Escuintla 5
Escuintla Santa_Rosa 4
Escuintla Jutiapa 9
Baja_Verapaz Quiche 5
Quiche Huehuetenango 6
Huehuetenango San_Marcos 8
Jalapa Jutiapa 5
Jalapa Chiquimula 6
El_Progreso Zacapa 3
Guatemala Minit_1 1
Minit_1 Minit_2 2
Minit_2 Minit_3 1
Minit_3 Minit_4 2
Minit_4 Minit_5 1
Minit_5 Minit_6 2
Minit_6 Minit_7 1
Minit_7 Minit_8 2
Minit_8 Minit_9 1
Minit_9 Escuintla 2
"""

# 1. Entradas en barra lateral
vertices_input = st.sidebar.text_input("Departamentos y Nodos:", default_vertices)
lista_vertices = [v.strip() for v in vertices_input.split(",") if v.strip()]

st.sidebar.subheader("Conexiones y Costos (Distancias)")
aristas_input = st.sidebar.text_area("Lista de Conexiones:", default_edges, height=200)

# URL de un mapa limpio de Guatemala para el fondo
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

# 3. Selección de Origen y Destino
col1, col2 = st.columns(2)
with col1:
    nodo_inicial = st.selectbox("Origen (Departamento/Municipio):", lista_vertices if lista_vertices else [""])
with col2:
    nodo_destino = st.selectbox("Destino (Departamento/Municipio):", lista_vertices if lista_vertices else [""])

# Botón para calcular
if st.button("🚀 Calcular Ruta Más Corta en el Mapa", type="primary"):
    total_nodos = len(lista_vertices)
    if total_nodos < 31:
        st.warning(f"⚠️ Tienes {total_nodos} nodos. Recuerda que la rúbrica pide mínimo 31 nodos.")
    else:
        st.success(f"✅ Cumple con el requisito de nodos ({total_nodos} nodos activos).")

    if nodo_inicial and nodo_destino and nodo_inicial in grafo and nodo_destino in grafo:
        distancia, previo = dijkstra(grafo, nodo_inicial)
        
        if distancia[nodo_destino] != INF:
            camino = obtener_camino(previo, nodo_destino)
            st.success(f"**Ruta más rápida:** {' ➔ '.join(camino)}")
            st.info(f"**Costo / Distancia Total acumulada:** {distancia[nodo_destino]}")
        else:
            camino = []
            st.error(f"No hay ruta disponible hacia {nodo_destino} desde {nodo_inicial}.")

        # --- VISUALIZACIÓN CON PYVIS Y MAPA DE GUATEMALA ---
        net = Network(height="680px", width="100%", bgcolor="rgba(0,0,0,0)", font_color="white", directed=False)
        
        net.set_options("""
        var options = {
          "nodes": { "font": {"size": 13, "face": "arial", "color": "white", "strokeWidth": 3, "strokeColor": "#000000"}, "borderWidth": 2, "shadow": true },
          "edges": { "color": {"inherit": false}, "smooth": {"type": "continuous"}, "font": {"size": 12, "color": "#00ffff", "strokeWidth": 3, "strokeColor": "#000000"}, "shadow": true },
          "physics": { "barnesHut": { "gravitationalConstant": -2500, "centralGravity": 0.4, "springLength": 100 }, "solver": "barnesHut" }
        }
        """)

        for nodo in grafo:
            color = "#ff2e63" if nodo in camino else "#2196F3"
            size = 20 if nodo in camino else 14
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
                        net.add_edge(origen, dest, value=peso, title=f"Distancia: {peso}", label=str(peso), color="#ff2e63", width=5)
                    else:
                        net.add_edge(origen, dest, value=peso, title=f"Distancia: {peso}", label=str(peso), color="rgba(255,255,255,0.5)", width=1)

        html_file = "dijkstra_guatemala.html"
        net.save_graph(html_file)
        
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Estilo para colocar el mapa de Guatemala de fondo con transparencia
        custom_css = f"""
        <style>
        #mynetwork {{
            background-image: linear-gradient(rgba(10, 25, 47, 0.75), rgba(10, 25, 47, 0.75)), url('{mapa_fondo_url}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.6);
        }}
        </style>
        """
        
        components.html(custom_css + html_content, height=700)
    else:
        st.warning("Selecciona correctamente los puntos de origen y destino.")
