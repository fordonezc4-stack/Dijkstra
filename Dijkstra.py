import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import heapq
import base64

def obtener_imagen_base64(ruta_imagen):
    with open(ruta_imagen, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

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

# Coordenadas geográficas distribuidas para formar el mapa de Guatemala de manera ordenada
POSICIONES_GEOGRAFICAS = {
    "Peten": (0, -320),
    "Flores": (60, -350),
    "Sayaxche": (-60, -240),
    "Alta_Verapaz": (20, -130),
    "Coban": (-40, -140),
    "Baja_Verapaz": (-20, -50),
    "Izabal": (250, -140),
    "Puerto_Barrios": (310, -150),
    "Zacapa": (170, -40),
    "Chiquimula": (190, 30),
    "El_Progreso": (90, -40),
    "Jalapa": (110, 60),
    "Jutiapa": (160, 160),
    "Santa_Rosa": (60, 170),
    "Escuintla": (-30, 170),
    "Puerto_Quetzal": (-30, 230),
    "Guatemala": (30, 40),
    "Mixco": (-10, 30),
    "Villa_Nueva": (20, 80),
    "Sacatepequez": (-30, 50),
    "Chimaltenango": (-80, 30),
    "Solola": (-150, 40),
    "Quiche": (-90, -80),
    "Huehuetenango": (-220, -100),
    "San_Marcos": (-280, 10),
    "Quetzaltenango": (-200, 30),
    "Totonicapan": (-160, -10),
    "Retalhuleu": (-230, 100),
    "Suchitepequez": (-140, 110),
    "Coatepeque": (-260, 60),
    "Mazatenango": (-120, 130)
}

default_vertices = ", ".join(POSICIONES_GEOGRAFICAS.keys())

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

vertices_input = st.sidebar.text_input("Departamentos y Nodos:", default_vertices)
lista_vertices = [v.strip() for v in vertices_input.split(",") if v.strip()]

st.sidebar.subheader("Conexiones y Pesos")
aristas_input = st.sidebar.text_area("Lista de Aristas:", default_edges, height=180)

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
        st.success(f"✅ Requisito cumplido: {total_nodos} nodos distribuidos en el mapa.")

    if nodo_inicial and nodo_destino and nodo_inicial in grafo and nodo_destino in grafo:
        distancia, previo = dijkstra(grafo, nodo_inicial)
        
        if distancia[nodo_destino] != INF:
            camino = obtener_camino(previo, nodo_destino)
            st.success(f"**Ruta encontrada:** {' ➔ '.join(camino)}")
            st.info(f"**Costo Total:** {distancia[nodo_destino]}")
        else:
            camino = []
            st.error(f"No hay conexión entre {nodo_inicial} y {nodo_destino}.")

        # --- CREACIÓN DE LA RED PYVIS ---
        net = Network(height="650px", width="100%", bgcolor="rgba(0,0,0,0)", font_color="black", directed=False)
        
        net.set_options("""
        var options = {
          "physics": { "enabled": false },
          "nodes": {
             "font": { "size": 13, "face": "arial", "color": "#000000", "strokeWidth": 2, "strokeColor": "#ffffff" },
             "borderWidth": 2,
             "shadow": true
          },
          "edges": {
             "smooth": { "type": "continuous" },
             "font": { "size": 12, "color": "#004d40", "strokeWidth": 2, "strokeColor": "#ffffff" },
             "shadow": true
          }
        }
        """)

        # Añadir nodos ordenados geográficamente
        for nodo in grafo:
            color = "#ff2e63" if nodo in camino else "#00adb5"
            size = 18 if nodo in camino else 12
            tooltip = f"Departamento: {nodo}"
            
            if nodo in POSICIONES_GEOGRAFICAS:
                x, y = POSICIONES_GEOGRAFICAS[nodo]
                net.add_node(nodo, label=nodo, title=tooltip, color=color, size=size, x=x, y=y, physics=False)
            else:
                net.add_node(nodo, label=nodo, title=tooltip, color=color, size=size)

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
                        net.add_edge(origen, dest, value=peso, title=f"Distancia: {peso}", label=str(peso), color="rgba(120,120,120,0.5)", width=1.5)

        html_file = "dijkstra_mapa_final.html"
        net.save_graph(html_file)
        
        with open(html_file, "r", encoding="utf-8") as f:
            pyvis_html = f.read()



        # Forzar fondo transparente al HTML de Pyvis para eliminar el bloque blanco ajsbhaduabbd
        pyvis_html = pyvis_html.replace("</head>", "<style>body { background: transparent !important; }</style></head>")

        # Convierte la imagen local a Base64 para que Streamlit la lea sin problemas
        img_base64 = obtener_imagen_base64("mapa.png") 
        mapa_url = f"data:image/png;base64,{img_base64}"
        
        contenedor_maestro = f"""
        <div style="position: relative; width: 100%; height: 680px; background: transparent; overflow: hidden;">
            <!-- Capa 1: Imagen del mapa con mezcla para eliminar su fondo blanco -->
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; display: flex; justify-content: center; align-items: center;">
                <img src="{mapa_url}" style="max-height: 90%; opacity: 0.35; mix-blend-mode: multiply; pointer-events: none;">
            </div>
            <!-- Capa 2: Grafo interactivo transparente -->
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2;">
                <iframe srcdoc="{pyvis_html.replace('"', '&quot;')}" style="width: 100%; height: 100%; border: none; background: transparent;"></iframe>
            </div>
        </div>
        """
        
        components.html(contenedor_maestro, height=700)
        
        components.html(contenedor_maestro, height=700)
        
        components.html(contenedor_maestro, height=700)
    else:
        st.warning("Selecciona nodos de origen y destino válidos.")
    
