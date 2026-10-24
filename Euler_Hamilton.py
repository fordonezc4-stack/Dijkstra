import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import sys

# Ampliar el límite de recursión para soportar grafos grandes en Hamilton
sys.setrecursionlimit(3000)

st.set_page_config(page_title="Caminos y Ciclos de Euler y Hamilton", layout="wide")

st.title("🔄 Análisis de Caminos y Ciclos de Euler y Hamilton (45 Vértices)")
st.markdown("---")

# ---------------------------------------------------------
# 1. Configuración Inicial del Grafo (45 Vértices optimizados)
# ---------------------------------------------------------
if 'graph' not in st.session_state:
    G = nx.Graph()
    # Generar 45 vértices (N1 hasta N45)
    nodes = [f"N{i}" for i in range(1, 46)]
    
    # Crear un circuito base que conecte todos los nodos en orden secuencial
    edges = [(f"N{i}", f"N{i+1}") for i in range(1, 45)] + [("N45", "N1")]
    
    # Agregar conexiones adicionales estratégicas para enriquecer la red
    extra_edges = [
        ("N1", "N15"), ("N15", "N30"), ("N30", "N45"),
        ("N5", "N25"), ("N10", "N35"), ("N20", "N40"),
        ("N2", "N22"), ("N12", "N32"), ("N18", "N38")
    ]
    
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    for u, v in extra_edges:
        if not G.has_edge(u, v):
            G.add_edge(u, v)
            
    st.session_state.graph = G

G = st.session_state.graph

# ---------------------------------------------------------
# Sidebar: Gestión y edición del Grafo
# ---------------------------------------------------------
st.sidebar.header("🛠️ Edición del Grafo")
st.sidebar.info(f"Vértices actuales en memoria: **{len(G.nodes)}**")

col_add1, col_add2 = st.sidebar.columns(2)
new_node = col_add1.text_input("Nuevo Vértice", "").strip().upper()
if col_add2.button("➕ Agregar Vértice"):
    if new_node and new_node not in G.nodes():
        G.add_node(new_node)
        st.sidebar.success(f"Vértice '{new_node}' agregado.")
        st.rerun()
    elif new_node in G.nodes():
        st.sidebar.warning("El vértice ya existe.")

st.sidebar.subheader("Agregar Arista")
col_e1, col_e2 = st.sidebar.columns(2)
node1 = col_e1.selectbox("Vértice Origen", list(G.nodes()), key="n1")
node2 = col_e2.selectbox("Vértice Destino", list(G.nodes()), key="n2")

if st.sidebar.button("➕ Agregar Arista"):
    if node1 != node2:
        if not G.has_edge(node1, node2):
            G.add_edge(node1, node2)
            st.sidebar.success(f"Arista {node1}-{node2} agregada.")
            st.rerun()
        else:
            st.sidebar.warning("La arista ya existe.")
    else:
        st.sidebar.error("No se permiten lazos (mismo vértice).")

if st.sidebar.button("🗑️ Reiniciar Grafo a 45 Nodos"):
    del st.session_state.graph
    st.rerun()

# ---------------------------------------------------------
# Lógica de Algoritmos (Euler y Hamilton)
# ---------------------------------------------------------
def analizar_euler(graph):
    if len(graph.nodes) == 0:
        return "Grafo vacío", False, False
    
    is_connected = nx.is_connected(graph) if len(graph.nodes) > 1 else True
    degrees = dict(graph.degree())
    odd_nodes = [node for node, deg in degrees.items() if deg % 2 != 0]
    
    has_euler_circuit = is_connected and len(odd_nodes) == 0
    has_euler_path = is_connected and (len(odd_nodes) == 0 or len(odd_nodes) == 2)
    
    path_seq = None
    circuit_seq = None
    
    if has_euler_circuit:
        circuit_seq = list(nx.eulerian_circuit(graph))
    elif has_euler_path:
        path_seq = list(nx.eulerian_path(graph))
        
    return is_connected, degrees, odd_nodes, has_euler_circuit, circuit_seq, has_euler_path, path_seq

def buscar_hamilton(graph):
    nodes = list(graph.nodes())
    n = len(nodes)
    if n == 0:
        return None, None
    
    path_found = []
    circuit_found = []

    def backtracking(v, visited, current_path):
        nonlocal path_found, circuit_found
        if len(current_path) == n:
            if not path_found:
                path_found = list(current_path)
            if current_path[0] in graph.neighbors(v):
                circuit_found = list(current_path) + [current_path[0]]
            return

        for neighbor in graph.neighbors(v):
            if neighbor not in visited:
                visited.add(neighbor)
                current_path.append(neighbor)
                
                backtracking(neighbor, visited, current_path)
                
                if path_found and circuit_found:
                    return
                current_path.pop()
                visited.remove(neighbor)

    for start_node in nodes:
        backtracking(start_node, {start_node}, [start_node])
        if path_found or circuit_found:
            break

    return path_found, circuit_found

# ---------------------------------------------------------
# Resultados y Análisis
# ---------------------------------------------------------
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 Análisis Teórico y Resultados")
    
    if len(G.nodes) == 0:
        st.warning("El grafo está vacío. Agrega vértices y aristas desde la barra lateral.")
    else:
        is_conn, degrees, odd_nodes, has_e_circ, e_circ, has_e_path, e_path = analizar_euler(G)
        
        # Para evitar congelamientos con 45 nodos en la búsqueda exhaustiva de Hamilton, 
        # informamos el estado de manera segura.
        st.write(f"**Total de Vértices:** {len(G.nodes)}")
        st.write(f"**¿Es Conexo?:** {'Sí' if is_conn else 'No'}")
        st.write(f"**Vértices de Grado Impar ({len(odd_nodes)}):** {odd_nodes}")
        st.markdown("---")
        
        # --- EULER ---
        st.markdown("### 🔹 Análisis de Euler")
        if has_e_circ:
            seq = " ➔ ".join([u for u, v in e_circ] + [e_circ[-1][1]])
            st.success(f"**Ciclo de Euler (Existe):**\n`{seq[:150]}... (secuencia completa disponible)`")
        else:
            st.error(f"**Ciclo de Euler:** No existe. (Tiene {len(odd_nodes)} vértices de grado impar).")
            
        if has_e_path:
            st.success("**Camino de Euler (Existe)** en la estructura del grafo.")
        else:
            st.error("**Camino de Euler:** No existe.")

        # --- HAMILTON ---
        st.markdown("### 🔹 Análisis de Hamilton")
        with st.spinner("Calculando rutas de Hamilton para 45 nodos..."):
            h_path, h_circ = buscar_hamilton(G)

        if h_circ:
            st.success(f"**Ciclo de Hamilton (Existe):** Conecta los 45 nodos de forma continua.")
        else:
            st.error("**Ciclo de Hamilton:** No existe en la configuración actual.")
            
        if h_path:
            st.success(f"**Camino de Hamilton (Existe):** Visita los 45 nodos exactamente una vez.")
        else:
            st.error("**Camino de Hamilton:** No encontrado con esta topología.")

with col_right:
    st.subheader("🌐 Visualización Interactiva (45 Nodos)")
    
    if len(G.nodes) > 0:
        net = Network(height="550px", width="100%", bgcolor="#222222", font_color="white")
        
        for n in G.nodes():
            color = "#ff4b4b" if n in odd_nodes else "#00c853"
            net.add_node(n, label=str(n), color=color, title=f"Grado: {G.degree(n)}")
            
        for u, v in G.edges():
            net.add_edge(u, v)
            
        net.save_graph("graph_45.html")
        HtmlFile = open("graph_45.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        components.html(source_code, height=570)
