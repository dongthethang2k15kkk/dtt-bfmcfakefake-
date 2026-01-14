### HỆ THỐNG KIỂM TRA AN TOÀN LÁI XE (GÓC LÁI TỐI ĐA) TRÊN ĐƯỜNG ĐUA ###

import xml.etree.ElementTree as ET
import math
import os

# ================= CẤU HÌNH (QUAN TRỌNG) =================
INPUT_FILE = "Competition_track_graph!.graphml"  # File map đã convert sang mét
WHEELBASE = 0.26          # Chiều dài trục cơ sở (mét) - ĐO XE THẬT RỒI SỬA SỐ NÀY
MAX_STEERING_ANGLE = 25   # Góc lái tối đa (độ)

# ================= HÀM TOÁN HỌC =================
def calculate_radius(p1, p2, p3):
    """Tính bán kính đường tròn đi qua 3 điểm (p1, p2, p3)"""
    x1, y1 = p1['x'], p1['y']
    x2, y2 = p2['x'], p2['y']
    x3, y3 = p3['x'], p3['y']
    
    # Độ dài các cạnh tam giác
    a = math.sqrt((x1-x2)**2 + (y1-y2)**2)
    b = math.sqrt((x2-x3)**2 + (y2-y3)**2)
    c = math.sqrt((x3-x1)**2 + (y3-y1)**2)
    
    # Diện tích tam giác (Heron)
    s = (a + b + c) / 2
    area = math.sqrt(max(0, s * (s - a) * (s - b) * (s - c))) # max(0,...) để tránh lỗi số học nhỏ
    
    if area < 1e-6: return float('inf') # 3 điểm thẳng hàng -> Bán kính vô cực
    
    # Bán kính R = abc / 4S
    return (a * b * c) / (4 * area)

def calculate_steering_angle(radius):
    """Tính góc lái Ackerman từ bán kính: angle = arctan(L / R)"""
    if radius == 0: return 90.0
    angle_rad = math.atan(WHEELBASE / radius)
    return math.degrees(angle_rad)

# ================= HÀM XỬ LÝ CHÍNH =================
def analyze_track():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Lỗi: Không tìm thấy file {INPUT_FILE}")
        return

    print(f"--- ĐANG ĐỌC FILE: {INPUT_FILE} ---")
    tree = ET.parse(INPUT_FILE)
    root = tree.getroot()
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
    
    # 1. Đọc dữ liệu Nodes
    nodes = {} # Lưu tạm: id -> {x, y}
    for node in root.findall(".//g:node", ns):
        nid = node.get('id')
        x, y = 0.0, 0.0
        # Tìm data d0 (x) và d1 (y)
        for data in node.findall("g:data", ns):
            key = data.get('key')
            if key == 'd0': x = float(data.text)
            if key == 'd1': y = float(data.text)
        nodes[nid] = {'id': nid, 'x': x, 'y': y}

    # 2. Sắp xếp lại thứ tự (Reconstruct Path)
    # Vì graphml lưu lộn xộn, ta cần đi theo mũi tên edge
    adj = {}
    for edge in root.findall(".//g:edge", ns):
        adj[edge.get('source')] = edge.get('target')

    # Tìm điểm bắt đầu (Node 0)
    # Giả sử node id="0" là bắt đầu, hoặc tìm node không có ai trỏ tới
    # Với file output của code trước, node id chạy từ "0" -> "n"
    sorted_nodes = []
    curr_id = "0" 
    
    # Fallback: Nếu không tìm thấy node 0, tìm node đầu tiên trong danh sách
    if curr_id not in nodes and len(nodes) > 0:
        curr_id = list(nodes.keys())[0]

    count = 0
    while curr_id in nodes:
        sorted_nodes.append(nodes[curr_id])
        if curr_id in adj:
            curr_id = adj[curr_id]
        else:
            break
        
        # Chống lặp vô tận
        count += 1
        if count > len(nodes) + 10: break

    print(f"-> Đã load {len(sorted_nodes)} nodes theo thứ tự đường đi.")
    
    # 3. QUÉT GÓC LÁI (Scan)
    print(f"\n--- BẮT ĐẦU KIỂM TRA (Max {MAX_STEERING_ANGLE} độ, Wheelbase {WHEELBASE}m) ---")
    violations = []
    
    # Duyệt qua từng bộ 3 điểm
    for i in range(1, len(sorted_nodes) - 1):
        p1 = sorted_nodes[i-1]
        p2 = sorted_nodes[i]   # Node khúc cua
        p3 = sorted_nodes[i+1]
        
        R = calculate_radius(p1, p2, p3)
        angle = calculate_steering_angle(R)
        
        if angle > MAX_STEERING_ANGLE:
            violations.append({
                'node_ids': f"{p1['id']} -> {p2['id']} -> {p3['id']}",
                'center_node': p2['id'],
                'angle': angle,
                'radius': R
            })

    # 4. XUẤT BÁO CÁO
    if len(violations) == 0:
        print("\n✅ TUYỆT VỜI! Không phát hiện khúc cua nào quá gắt.")
    else:
        print(f"\n⚠️ CẢNH BÁO: Phát hiện {len(violations)} điểm cua gắt!")
        print("-" * 60)
        print(f"{'BỘ NODE (Trước -> Giữa -> Sau)':<30} | {'GÓC LÁI':<10} | {'BÁN KÍNH':<10}")
        print("-" * 60)
        
        for v in violations:
            print(f"{v['node_ids']:<30} | {v['angle']:.2f}°    | {v['radius']:.3f} m")
        
        print("-" * 60)
        print("💡 GIẢI PHÁP: Hãy vào yEd, tìm các node ID ở cột 'Giữa'.")
        print("   Kéo chúng ra xa nhau hoặc làm đường cong rộng hơn.")

if __name__ == "__main__":
    analyze_track()