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
st.set_page_config(page_title="Algoritmo de Dijkstra con Mapa", layout="wide")
st.title("🌐 Visualizador de Rutas Mínimas - Dijkstra (con Mapa de Fondo)")

st.sidebar.header("Configuración del Grafo (Mínimo 31 Nodos)")

# Generar por defecto una lista amplia para cumplir con los 31 nodos exigidos
default_vertices = ", ".join([f"N{i}" for i in range(1, 35)])
default_edges = "\n".join([f"N{i} N{i+1} {(i*3)%15 + 2}" for i in range(1, 34)])
default_edges += "\nN34 N1 10\nN1 N15 7\nN5 N20 12"

# 1. Entrada de Vértices
vertices_input = st.sidebar.text_input("Vértices (separados por coma):", default_vertices)
lista_vertices = [v.strip() for v in vertices_input.split(",") if v.strip()]

# 2. Entrada de Aristas
st.sidebar.subheader("Aristas y Pesos")
st.sidebar.caption("Formato por línea: origen destino peso (ej: N1 N2 5)")
aristas_input = st.sidebar.text_area("Lista de Aristas:", default_edges, height=150)

# Opción para mapa de fondo (URL de una imagen de mapa o plano)
st.sidebar.subheader("Personalización del Mapa")
mapa_fondo_url = st.sidebar.text_input(
    "URL de imagen de mapa de fondo:", 
    "https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=1000&auto=format&fit=crop"
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
                if peso < 0:
                    st.sidebar.warning(f"Advertencia: Peso negativo detectado en {u}-{v}. Dijkstra no maneja pesos negativos.")
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
if st.button("🚀 Calcular Ruta Más Corta", type="primary"):
    if len(lista_vertices) < 31:
        st.warning(f"⚠️ Atención: Tienes {len(lista_vertices)} vértices. La rúbrica exige un mínimo de 31 nodos para Dijkstra.")

    if nodo_inicial and nodo_destino and nodo_inicial in grafo and nodo_destino in grafo:
        distancia, previo = dijkstra(grafo, nodo_inicial)
        
        if distancia[nodo_destino] != INF:
            camino = obtener_camino(previo, nodo_destino)
            st.success(f"**Ruta más corta encontrada:** {' ➔ '.join(camino)}")
            st.info(f"**Costo / Distancia Total:** {distancia[nodo_destino]}")
        else:
            camino = []
            st.error(f"El nodo {nodo_destino} no es alcanzable desde {nodo_inicial}.")

        # --- GENERACIÓN Y VISUALIZACIÓN CON PYVIS Y MAPA DE FONDO ---
        net = Network(height="650px", width="100%", bgcolor="rgba(0,0,0,0)", font_color="white", directed=False)
        
        net.set_options("""
        var options = {
          "nodes": { "font": {"size": 14, "face": "arial", "color": "white"}, "borderWidth": 2, "shadow": true },
          "edges": { "color": {"inherit": false}, "smooth": {"type": "continuous"}, "font": {"size": 12, "color": "#ffeb3b"}, "shadow": true },
          "physics": { "barnesHut": { "gravitationalConstant": -2000, "centralGravity": 0.3, "springLength": 90 }, "solver": "barnesHut" }
        }
        """)

        # Agregar nodos (destacando los del camino más corto)
        for nodo in grafo:
            color = "#ff2e63" if nodo in camino else "#00b4d8"
            size = 22 if nodo in camino else 16
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
                        net.add_edge(origen, dest, value=peso, title=f"Costo: {peso}", label=str(peso), color="#ff2e63", width=5)
                    else:
                        net.add_edge(origen, dest, value=peso, title=f"Costo: {peso}", label=str(peso), color="rgba(255,255,255,0.4)", width=1)

        html_file = "dijkstra_temp.html"
        net.save_graph(html_file)
        
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Inyectar estilos CSS avanzados para colocar la imagen de mapa de fondo detrás del grafo de Pyvis
        custom_css = f"""
        <style>
        #mynetwork {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('{mapa_fondo_url}');
            background-size: cover;
            background-position: center;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }}
        </style>
        """
        
        components.html(custom_css + html_content, height=670)
    else:
        st.warning("Asegúrate de seleccionar nodos de origen y destino válidos.")
