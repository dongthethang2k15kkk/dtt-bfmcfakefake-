import xml.etree.ElementTree as ET
import xml.dom.minidom
import math

INPUT_FILE = "BFMC_Track_graph!.graphml"        
OUTPUT_FILE = "Competition_track_graph!.graphml" 
REAL_DISTANCE = 3.0                             

def read_and_convert():
    print(f"--- Đang đọc file {INPUT_FILE}... ---")
    try:
        tree = ET.parse(INPUT_FILE)
        root = tree.getroot()
        ns = {'g': 'http://graphml.graphdrawing.org/xmlns', 'y': 'http://www.yworks.com/xml/graphml'}
        
        # 1. Tìm ORIGIN và REF_X để tính tỷ lệ
        origin_pos = None
        ref_pos = None
        
        # Quét lần 1: Chỉ để tìm 2 điểm mốc
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

        if not origin_pos or not ref_pos: 
            print("LỖI: Không tìm thấy node 'ORIGIN' hoặc 'REF_X'.")
            return None, None

        # Tính tỷ lệ
        pixel_dist = math.sqrt((ref_pos[0]-origin_pos[0])**2 + (ref_pos[1]-origin_pos[1])**2)
        scale = REAL_DISTANCE / pixel_dist
        print(f"-> Tỷ lệ: 1 đơn vị = {scale:.6f} m")

        # 2. Xử lý TẤT CẢ các Node (Không bỏ sót thằng nào)
        final_nodes = {} # Map: old_id -> new_data
        node_mapping = {} # Map: old_id -> new_id (0, 1, 2...)
        
        counter = 0
        for node in root.findall(".//g:node", ns):
            old_id = node.get('id')
            geo = node.find(".//y:Geometry", ns)
            if geo is None: continue
            
            # Bỏ qua node ORIGIN và REF_X trong danh sách điểm chạy xe
            node_label = node.find(".//y:NodeLabel", ns)
            lbl = node_label.text.strip() if node_label is not None else ""
            if "ORIGIN" in lbl or "REF_X" in lbl:
                continue

            rx = float(geo.get('x'))
            ry = float(geo.get('y'))
            
            # Chuyển đổi tọa độ
            mx = (rx - origin_pos[0]) * scale
            my = (origin_pos[1] - ry) * scale 
            
            final_nodes[counter] = (mx, my)
            node_mapping[old_id] = str(counter)
            counter += 1

        print(f"-> Đã xử lý {len(final_nodes)} nodes.")

        # 3. Xử lý TẤT CẢ các Edge (Giữ nguyên tính kết nối)
        final_edges = []
        # --- ĐOẠN CẦN SỬA (Thay thế từ dòng 76 đến 83 trong code cũ) ---
       # --- ĐOẠN CODE ĐÃ SỬA ---
        for edge in root.findall(".//g:edge", ns):
            src = edge.get('source')
            tgt = edge.get('target')
            
            # Giá trị mặc định
            is_dotted = False
            
            # Quét thẻ data để tìm thuộc tính dotted (ID là d10 trong file code1)
            for data in edge.findall("g:data", ns):
                # QUAN TRỌNG: Sửa d2 thành d10 khớp với file input
                if data.get('key') == 'd10': 
                    if data.text:
                        # Chuẩn hóa về chữ thường và xóa khoảng trắng thừa
                        val = data.text.strip().lower()
                        
                        # Logic: 1 hoặc 'true' => True
                        if val == 'true' or val == '1':
                            is_dotted = True
                        # Logic: 0 hoặc 'false' => False (mặc định đã là False rồi)
                        elif val == 'false' or val == '0':
                            is_dotted = False

            # Chỉ lấy cạnh nếu cả 2 đầu đều là node hợp lệ
            if src in node_mapping and tgt in node_mapping:
                new_src = node_mapping[src]
                new_tgt = node_mapping[tgt]
                # Lưu vào danh sách
                final_edges.append((new_src, new_tgt, is_dotted)) 
        # ------------------------
        print(f"-> Đã xử lý {len(final_edges)} edges.")
        
        return final_nodes, final_edges

    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return None, None

def export_to_xml(nodes, edges):
    print(f"--- Đang xuất ra file {OUTPUT_FILE}... ---")
    
    ET.register_namespace('', "http://graphml.graphdrawing.org/xmlns")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    
    root = ET.Element('graphml', {
        'xmlns': "http://graphml.graphdrawing.org/xmlns",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
    })

    ET.SubElement(root, 'key', {'id': 'd2', 'for': 'edge', 'attr.name': 'dotted', 'attr.type': 'boolean'})
    ET.SubElement(root, 'key', {'id': 'd1', 'for': 'node', 'attr.name': 'y', 'attr.type': 'double'})
    ET.SubElement(root, 'key', {'id': 'd0', 'for': 'node', 'attr.name': 'x', 'attr.type': 'double'})

    graph = ET.SubElement(root, 'graph', {'edgedefault': 'directed'})

    # Ghi Nodes
    # nodes là dict {id_mới: (x, y)}
    for new_id, (x, y) in nodes.items():
        node = ET.SubElement(graph, 'node', {'id': str(new_id)})
        d0 = ET.SubElement(node, 'data', {'key': 'd0'})
        d0.text = f"{x:.4f}" 
        d1 = ET.SubElement(node, 'data', {'key': 'd1'})
        d1.text = f"{y:.4f}"

    
    # --- ĐOẠN CẦN SỬA (Thay thế từ dòng 116 đến 119) ---
    # Phải unpack thêm biến is_dotted
    for src, tgt, is_dotted in edges:
        edge = ET.SubElement(graph, 'edge', {'source': src, 'target': tgt})
        d2 = ET.SubElement(edge, 'data', {'key': 'd2'}) # d2 này là ID trong file OUTPUT
        # Ghi giá trị True/False thực tế vào
        d2.text = str(is_dotted) 
    # ---------------------------------------------------

    # Format XML đẹp
    xml_str = ET.tostring(root, encoding='utf-8')
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")
    clean_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(clean_xml)
        
    print(f"✅ Xong! File {OUTPUT_FILE} đã được export đầy đủ cấu trúc đồ thị.")

# ================= CHẠY CHƯƠNG TRÌNH =================
if __name__ == "__main__":
    nodes_data, edges_data = read_and_convert()
    if nodes_data:
        export_to_xml(nodes_data, edges_data)