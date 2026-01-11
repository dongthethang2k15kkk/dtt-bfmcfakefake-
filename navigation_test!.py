import networkx as nx
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

# --- PHẦN 1: CÁC HÀM TÍNH TOÁN ---

def calculate_distance(p1, p2):
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

def get_angle(p1, p2, p3):
    v1 = np.array([p2['x'] - p1['x'], p2['y'] - p1['y']])
    v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y']])
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 == 0 or n2 == 0: return 0
    dot = np.dot(v1/n1, v2/n2)
    return np.degrees(np.arccos(np.clip(dot, -1.0, 1.0)))

# --- PHẦN 2: XỬ LÝ ĐỒ THỊ VÀ LỚP HIỂN THỊ ---

def run_layered_optimization(graph_file, img_file, points_list):
    if not os.path.exists(graph_file):
        print(f"Lỗi: Không tìm thấy file {graph_file}")
        return

    G = nx.read_graphml(graph_file)
    
    # Chuẩn hóa tọa độ cho toàn bộ các nút
    for n in G.nodes():
        G.nodes[n]['x'] = float(G.nodes[n].get('x', G.nodes[n].get('d0', 0)))
        G.nodes[n]['y'] = float(G.nodes[n].get('y', G.nodes[n].get('d1', 0)))

    # 1. Tính toán trọng số (Weight) cho toàn bộ đồ thị
    V_MAX = 1.0
    V_CURVE_MIN = 0.3
    for u, v in G.edges():
        dist = calculate_distance(G.nodes[u], G.nodes[v])
        velocity = V_MAX
        successors = list(G.successors(v))
        if successors:
            angle = get_angle(G.nodes[u], G.nodes[v], G.nodes[successors[0]])
            if angle > 10:
                velocity = max(V_MAX * (1 - (angle/100)), V_CURVE_MIN)
        G[u][v]['weight'] = dist / velocity

    # 2. Tìm đường đi tối ưu qua danh sách các Waypoints
    full_path = []
    for i in range(len(points_list) - 1):
        start, end = points_list[i], points_list[i+1]
        try:
            segment = nx.dijkstra_path(G, source=start, target=end, weight='weight')
            if i == 0:
                full_path.extend(segment)
            else:
                full_path.extend(segment[1:])
        except nx.NetworkXNoPath:
            print(f"LỖI: Không tìm thấy đường từ {start} đến {end}!")
            return

    # --- PHẦN 3: HIỂN THỊ THEO LỚP ---
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Layer 0: Ảnh nền
    if os.path.exists(img_file):
        img = mpimg.imread(img_file)
        # Sử dụng extent bạn đã căn chỉnh
        myextent = [-0.0923, 12.2724, -0.7284, 8.8704] 
        ax.imshow(img, extent=myextent, aspect='auto')

    pos = {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G.nodes()}

    # Layer 1 (Dưới): Toàn bộ mạng lưới đường đua
    # Vẽ các cạnh mờ màu trắng/xanh để thấy cấu trúc tổng thể
    nx.draw_networkx_edges(
        G, pos, ax=ax, 
        edge_color='white', 
        width=0.5, 
        alpha=0.15, # Độ trong suốt thấp để làm nền
        arrows=False
    )
    # Vẽ các điểm nút nhỏ mờ
    nx.draw_networkx_nodes(
        G, pos, ax=ax, 
        node_size=2, 
        node_color='gray', 
        alpha=0.3
    )

    # Layer 2 (Trên): Đường đi tối ưu
    path_edges = list(zip(full_path, full_path[1:]))
    # Vẽ các cạnh của đường đi màu đỏ rực rỡ
    nx.draw_networkx_edges(
        G, pos, 
        edgelist=path_edges, 
        edge_color='#ff3300', 
        width=3, 
        ax=ax, 
        arrows=True, 
        arrowsize=12
    )
    # Vẽ các nút trên đường đi màu vàng
    nx.draw_networkx_nodes(
        G, pos, 
        nodelist=full_path, 
        node_size=10, 
        node_color='yellow', 
        ax=ax
    )

    # Layer 3: Các điểm Waypoints đích (Xanh dương to)
    nx.draw_networkx_nodes(
        G, pos, 
        nodelist=points_list, 
        node_size=80, 
        node_color='cyan', 
        label='Waypoints', 
        edgecolors='white'
    )

    plt.title(f"Lộ trình tối ưu đè lên mạng lưới đường đua\nWaypoints: {' -> '.join(points_list)}")
    plt.legend()
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# --- CHẠY CHƯƠNG TRÌNH ---
my_waypoints = ["4", "69", "36", "67"] 
# Đảm bảo file .graphml và .png nằm cùng thư mục
run_layered_optimization("Competition_track_graph!.graphml", "Sahinh.png .", my_waypoints)