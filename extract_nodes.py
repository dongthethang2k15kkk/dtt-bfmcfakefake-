import xml.etree.ElementTree as ET
import xml.dom.minidom  # <--- Thêm thư viện này để format đẹp
import math

# ================= CẤU HÌNH =================
INPUT_FILE = "BFMC_Track_graph.graphml"        
OUTPUT_FILE = "Competition_track_graphfake.graphml" 
REAL_DISTANCE = 3                           

# ================= HÀM XỬ LÝ =================

def read_and_convert():
    print(f"--- Đang đọc file {INPUT_FILE}... ---")
    try:
        tree = ET.parse(INPUT_FILE)
        root = tree.getroot()
        ns = {'g': 'http://graphml.graphdrawing.org/xmlns', 'y': 'http://www.yworks.com/xml/graphml'}
        
        raw_nodes = {}
        origin_pos, ref_pos = None, None
        
        # 1. Lấy thông tin Nodes
        for node in root.findall(".//g:node", ns):
            geo = node.find(".//y:Geometry", ns)
            if geo is None: continue
            
            node_label = node.find(".//y:NodeLabel", ns)
            lbl = node_label.text.strip() if node_label is not None else ""
            
            x = float(geo.get('x'))
            y = float(geo.get('y'))
            
            if "ORIGIN" in lbl: 
                origin_pos = (x, y)
                print(f"-> Tìm thấy ORIGIN tại: {origin_pos}")
            elif "REF_X" in lbl: 
                ref_pos = (x, y)
                print(f"-> Tìm thấy REF_X tại: {ref_pos}")
            else: 
                raw_nodes[node.get('id')] = {'x': x, 'y': y}

        if not origin_pos or not ref_pos: 
            print("LỖI: Không tìm thấy node 'ORIGIN' hoặc 'REF_X'.")
            return None
        
        # 2. Tính tỷ lệ
        pixel_dist = math.sqrt((ref_pos[0]-origin_pos[0])**2 + (ref_pos[1]-origin_pos[1])**2)
        scale = REAL_DISTANCE / pixel_dist
        print(f"-> Tỷ lệ: 1 đơn vị = {scale:.6f} m")
        
        # 3. Lấy Edges
        adjacency = {}
        for edge in root.findall(".//g:edge", ns):
            adjacency[edge.get('source')] = edge.get('target')

        # 4. Sắp xếp điểm
        ordered_pts = []
        targets = set(adjacency.values())
        start_node_id = list(adjacency.keys())[0] 
        for n in adjacency.keys():
            if n not in targets: 
                start_node_id = n
                break
                
        curr = start_node_id
        loop_check = set()
        
        while curr:
            if curr in raw_nodes:
                rx, ry = raw_nodes[curr]['x'], raw_nodes[curr]['y']
                mx = (rx - origin_pos[0]) * scale
                my = (origin_pos[1] - ry) * scale 
                ordered_pts.append((mx, my))
            
            loop_check.add(curr)
            curr = adjacency.get(curr)
            if curr == start_node_id or curr in loop_check: 
                if curr == start_node_id and len(ordered_pts) > 0:
                     ordered_pts.append(ordered_pts[0])
                break

        return ordered_pts

    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return None

def export_to_xml(points):
    print(f"--- Đang xuất ra file {OUTPUT_FILE}... ---")
    
    # Tạo namespace
    ET.register_namespace('', "http://graphml.graphdrawing.org/xmlns")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    
    root = ET.Element('graphml', {
        'xmlns': "http://graphml.graphdrawing.org/xmlns",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
    })

    # Key định nghĩa
    ET.SubElement(root, 'key', {'id': 'd2', 'for': 'edge', 'attr.name': 'dotted', 'attr.type': 'boolean'})
    ET.SubElement(root, 'key', {'id': 'd1', 'for': 'node', 'attr.name': 'y', 'attr.type': 'double'})
    ET.SubElement(root, 'key', {'id': 'd0', 'for': 'node', 'attr.name': 'x', 'attr.type': 'double'})

    graph = ET.SubElement(root, 'graph', {'edgedefault': 'directed'})

    # Tạo Nodes
    for i, (x, y) in enumerate(points):
        node = ET.SubElement(graph, 'node', {'id': str(i)})
        d0 = ET.SubElement(node, 'data', {'key': 'd0'})
        d0.text = f"{x:.2f}" 
        d1 = ET.SubElement(node, 'data', {'key': 'd1'})
        d1.text = f"{y:.2f}"

    # Tạo Edges
    for i in range(len(points) - 1):
        edge = ET.SubElement(graph, 'edge', {'source': str(i), 'target': str(i+1)})
        d2 = ET.SubElement(edge, 'data', {'key': 'd2'})
        d2.text = "False"

    # --- ĐOẠN NÀY LÀM ĐẸP XML ---
    # Chuyển cây XML thành chuỗi
    xml_str = ET.tostring(root, encoding='utf-8')
    
    # Dùng minidom để format lại (xuống dòng, thụt đầu dòng)
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")
    
    # Xóa các dòng trắng thừa do minidom tạo ra (nếu có)
    clean_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])

    # Ghi đè vào file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(clean_xml)
        
    print(f"✅ Xong! File {OUTPUT_FILE} đã được format đẹp.")

# ================= CHẠY CHƯƠNG TRÌNH =================
if __name__ == "__main__":
    raw_points = read_and_convert()
    if raw_points:
        export_to_xml(raw_points)