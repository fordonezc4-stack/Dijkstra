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
st.set_page_config(page_title="Algoritmo de Dijkstra", layout="wide")
st.title("🌐 Visualizador del Algoritmo de Dijkstra")

st.sidebar.header("Configuración del Grafo")

# 1. Entrada de Vértices
vertices_input = st.sidebar.text_input("Vértices (separados por coma):", "A, B, C, D, E")
lista_vertices = [v.strip() for v in vertices_input.split(",") if v.strip()]

# 2. Entrada de Aristas
st.sidebar.subheader("Aristas")
st.sidebar.caption("Formato por línea: origen destino peso (ej: A B 5)")
aristas_input = st.sidebar.text_area("Lista de Aristas:", "A B 4\nA C 2\nB C 1\nB D 5\nC D 8\nC E 10\nD E 2")

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
    nodo_inicial = st.selectbox("Nodo Origen:", lista_vertices if lista_vertices else [""])
with col2:
    nodo_destino = st.selectbox("Nodo Destino:", lista_vertices if lista_vertices else [""])

# Botón para calcular
if st.button("🚀 Calcular Camino Más Corto", type="primary"):
    if nodo_inicial and nodo_destino and nodo_inicial in grafo and nodo_destino in grafo:
        distancia, previo = dijkstra(grafo, nodo_inicial)
        
        if distancia[nodo_destino] != INF:
            camino = obtener_camino(previo, nodo_destino)
            st.success(f"**Camino más corto:** {' ➔ '.join(camino)}")
            st.info(f"**Distancia total:** {distancia[nodo_destino]}")
        else:
            camino = []
            st.error(f"No existe un camino entre {nodo_inicial} y {nodo_destino}.")

        # --- GENERACIÓN Y VISUALIZACIÓN CON PYVIS ---
        net = Network(height="600px", width="100%", bgcolor="#1a1a2e", font_color="white", directed=False)
        
        # Opciones de animación/física
        net.set_options("""
        var options = {
          "nodes": { "font": {"size": 20, "face": "arial", "color": "white"}, "borderWidth": 3, "shadow": true },
          "edges": { "color": {"inherit": false}, "smooth": {"type": "continuous"}, "font": {"size": 16, "color": "#eeeeee"}, "shadow": true },
          "physics": { "forceAtlas2Based": { "gravitationalConstant": -90, "centralGravity": 0.01, "springLength": 160, "springConstant": 0.08 }, "solver": "forceAtlas2Based" }
        }
        """)

        # Agregar nodos
        for nodo in grafo:
            color = "#ff2e63" if nodo in camino else "#4cc9f0"
            net.add_node(nodo, label=nodo, color=color, size=28)

        # Aristas en el camino crítico
        aristas_camino = set(zip(camino, camino[1:]))
        aristas_camino |= set((b, a) for a, b in aristas_camino)

        # Agregar aristas
        aristas_agregadas = set()
        for origen in grafo:
            for dest, peso in grafo[origen]:
                pair = tuple(sorted([origen, dest]))
                if pair not in aristas_agregadas:
                    aristas_agregadas.add(pair)
                    if (origen, dest) in aristas_camino:
                        net.add_edge(origen, dest, value=peso, title=f"Peso: {peso}", label=str(peso), color="#ff2e63", width=6)
                    else:
                        net.add_edge(origen, dest, value=peso, title=f"Peso: {peso}", label=str(peso), color="#777777", width=2)

        # Guardar en HTML temporal para renderizarlo en Streamlit
        html_file = "grafo_temp.html"
        net.save_graph(html_file)
        
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        components.html(html_content, height=620)
    else:
        st.warning("Asegúrate de ingresar vértices válidos.")