import xml.etree.ElementTree as ET
import xml.dom.minidom
import math

# --- CẤU HÌNH ---
INPUT_FILE = "BFMC_Track_graph!.graphml"        # Tên file gốc (từ yEd)
OUTPUT_FILE = "Competition_track_graph_FINAL.graphml" # Tên file đích
REAL_DISTANCE = 3.0                             # Khoảng cách thực tế giữa ORIGIN và REF_X (mét)

def read_and_convert():
    print(f"--- 1. Đang đọc file {INPUT_FILE}... ---")
    try:
        tree = ET.parse(INPUT_FILE)
        root = tree.getroot()
        # Định nghĩa namespace để tìm thẻ chính xác
        ns = {'g': 'http://graphml.graphdrawing.org/xmlns', 'y': 'http://www.yworks.com/xml/graphml'}
        
        # --- BƯỚC 1: TÌM TỌA ĐỘ PIXEL CỦA 2 ĐIỂM MỐC ---
        origin_pos = None
        ref_pos = None
        
        for node in root.findall(".//g:node", ns):
            geo = node.find(".//y:Geometry", ns)
            if geo is None: continue
            
            node_label = node.find(".//y:NodeLabel", ns)
            lbl = node_label.text.strip() if node_label is not None else ""
            
            x = float(geo.get('x'))
            y = float(geo.get('y'))
            
            if "ORIGIN" in lbl: 
                origin_pos = (x, y)
                print(f"   -> Tìm thấy ORIGIN (pixel): {origin_pos}")
            elif "REF_X" in lbl: 
                ref_pos = (x, y)
                print(f"   -> Tìm thấy REF_X (pixel): {ref_pos}")

        if not origin_pos or not ref_pos: 
            print("!!! LỖI: Không tìm thấy node có nhãn 'ORIGIN' hoặc 'REF_X' trong file yEd.")
            return None, None

        # --- BƯỚC 2: TÍNH TỶ LỆ (SCALE) ---
        pixel_dist = math.sqrt((ref_pos[0]-origin_pos[0])**2 + (ref_pos[1]-origin_pos[1])**2)
        scale = REAL_DISTANCE / pixel_dist
        print(f"   -> Tỷ lệ tính được: 1 pixel = {scale:.6f} mét")

        # --- BƯỚC 3: XỬ LÝ TOÀN BỘ NODE (BAO GỒM CẢ ĐIỂM MỐC) ---
        final_nodes = {}      # Lưu {new_id: (x_met, y_met)}
        node_mapping = {}     # Lưu {old_id_yed: new_id}
        
        counter = 0
        
        for node in root.findall(".//g:node", ns):
            old_id = node.get('id')
            geo = node.find(".//y:Geometry", ns)
            if geo is None: continue
            
            # Lấy nhãn để kiểm tra
            node_label = node.find(".//y:NodeLabel", ns)
            lbl = node_label.text.strip() if node_label is not None else ""
            
            # === [PHẦN SỬA ĐỔI QUAN TRỌNG] ===
            # Nếu là điểm mốc, gán ID cứng và Tọa độ cứng, KHÔNG được bỏ qua
            if "ORIGIN" in lbl:
                final_nodes["ORIGIN"] = (0.0, 0.0) # Gốc luôn là 0,0
                node_mapping[old_id] = "ORIGIN"
                print("   -> Đã thêm node: ORIGIN (0.0, 0.0)")
                continue # Xong node này, sang node tiếp theo

            if "REF_X" in lbl:
                final_nodes["REF_X"] = (REAL_DISTANCE, 0.0) # Luôn nằm trên trục X
                node_mapping[old_id] = "REF_X"
                print(f"   -> Đã thêm node: REF_X ({REAL_DISTANCE}, 0.0)")
                continue
            # ==================================

            # Các node đường đua bình thường -> Tính toán theo công thức
            rx = float(geo.get('x'))
            ry = float(geo.get('y'))
            
            # Công thức chuyển đổi hệ tọa độ ảnh sang hệ tọa độ mét
            mx = (rx - origin_pos[0]) * scale
            my = (origin_pos[1] - ry) * scale # Lật trục Y vì trục Y của ảnh hướng xuống
            
            final_nodes[str(counter)] = (mx, my)
            node_mapping[old_id] = str(counter)
            counter += 1

        print(f"   -> Tổng cộng đã xử lý: {len(final_nodes)} nodes.")

        # --- BƯỚC 4: XỬ LÝ (EDGE) ---
        final_edges = []
        for edge in root.findall(".//g:edge", ns):
            src = edge.get('source')
            tgt = edge.get('target')
            
            # Kiểm tra nét đứt (dotted)
            is_dotted = False
            for data in edge.findall("g:data", ns):
                # Lưu ý: Kiểm tra kỹ key d10 hay d? trong file input của bạn
                # Thông thường yEd xuất ra d9 hoặc d10 cho visual style
                if data.text and ('true' in data.text.lower() or 'dashed' in data.text.lower()):
                     # Đây là cách check đơn giản, nếu cần chính xác phải soi ID
                     pass 
                
                # Check theo logic cũ của bạn (key d10)
                if data.get('key') == 'd10':
                    val = data.text.strip().lower()
                    if val == 'true' or val == '1': is_dotted = True

            if src in node_mapping and tgt in node_mapping:
                final_edges.append((node_mapping[src], node_mapping[tgt], is_dotted))
        
        print(f"   -> Tổng cộng đã xử lý: {len(final_edges)} edges.")
        return final_nodes, final_edges

    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return None, None

def export_to_xml(nodes, edges):
    print(f"--- 2. Đang xuất ra file {OUTPUT_FILE}... ---")
    
    # Tạo root XML
    root = ET.Element('graphml', {
        'xmlns': "http://graphml.graphdrawing.org/xmlns",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
    })

    # Định nghĩa các Key Attribute
    ET.SubElement(root, 'key', {'id': 'd0', 'for': 'node', 'attr.name': 'x', 'attr.type': 'double'})
    ET.SubElement(root, 'key', {'id': 'd1', 'for': 'node', 'attr.name': 'y', 'attr.type': 'double'})
    ET.SubElement(root, 'key', {'id': 'd2', 'for': 'edge', 'attr.name': 'dotted', 'attr.type': 'boolean'})

    graph = ET.SubElement(root, 'graph', {'edgedefault': 'directed'})

    # Ghi Nodes
    for node_id, (x, y) in nodes.items():
        node = ET.SubElement(graph, 'node', {'id': str(node_id)})
        
        # Thẻ d0 (X)
        d0 = ET.SubElement(node, 'data', {'key': 'd0'})
        d0.text = f"{x:.4f}"
        
        # Thẻ d1 (Y)
        d1 = ET.SubElement(node, 'data', {'key': 'd1'})
        d1.text = f"{y:.4f}"

    
    for src, tgt, is_dotted in edges:
        edge = ET.SubElement(graph, 'edge', {'source': src, 'target': tgt})
        d2 = ET.SubElement(edge, 'data', {'key': 'd2'})
        d2.text = str(is_dotted) # True/False

   
    xml_str = ET.tostring(root, encoding='utf-8')
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")
    
    
    clean_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(clean_xml)
        
    print("✅ Xong!")

#CHẠY 
if __name__ == "__main__":
    nodes_data, edges_data = read_and_convert()
    if nodes_data:
        export_to_xml(nodes_data, edges_data)