### HỆ THỐNG TÌM RA BỘ SỐ EXTENT CHUẨN CHO ẢNH NỀN SAHINH.PNG ###

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider, Button
import os

# --- CẤU HÌNH FILE ---
GRAPH_FILE = "Competition_track_graph!.graphml"
IMG_FILE = "Sahinh.png"

# --- KIỂM TRA FILE ---
if not os.path.exists(GRAPH_FILE) or not os.path.exists(IMG_FILE):
    print(f"LỖI: Không tìm thấy file {GRAPH_FILE} hoặc {IMG_FILE}")
    exit()

# --- LOAD DỮ LIỆU ---
G = nx.read_graphml(GRAPH_FILE)
pos = {}
all_x, all_y = [], []
for n, data in G.nodes(data=True):
    x = float(data.get('x', data.get('d0', 0)))
    y = float(data.get('y', data.get('d1', 0)))
    pos[n] = (x, y)
    all_x.append(x)
    all_y.append(y)

# Tính tâm của đồ thị
center_x = (min(all_x) + max(all_x)) / 2
center_y = (min(all_y) + max(all_y)) / 2

# === [SỬA ĐOẠN NÀY] ===
# Thay vì lấy width/height riêng, ta lấy cạnh lớn nhất để đảm bảo khung ảnh VUÔNG
# (Giả sử ảnh Sahinh.png của bạn là hình vuông hoặc gần vuông)
# --- TÍNH TOÁN TỶ LỆ ẢNH CHUẨN (Sửa đoạn này) ---
img = mpimg.imread(IMG_FILE) # Đọc ảnh trước để lấy kích thước thật
img_h, img_w = img.shape[:2] # Lấy chiều cao và chiều rộng pixel
img_aspect_ratio = img_w / img_h # Tính tỷ lệ khung hình (ví dụ 1.77 cho 16:9)

# Tính kích thước vùng bao của các node dữ liệu
data_width = max(all_x) - min(all_x)
data_height = max(all_y) - min(all_y)
max_dim = max(data_width, data_height)

# Thiết lập kích thước khung nền dựa trên tỷ lệ thật của ảnh
# Lấy cạnh lớn nhất của dữ liệu làm chuẩn chiều cao
base_height = max_dim 
# Chiều rộng sẽ tự động co giãn theo tỷ lệ ảnh gốc
base_width = max_dim * img_aspect_ratio 

print(f"-> Đã phát hiện ảnh gốc kích thước: {img_w}x{img_h} (Tỷ lệ: {img_aspect_ratio:.2f})")

# --- THIẾT LẬP GIAO DIỆN ---
fig, ax = plt.subplots(figsize=(14, 8))
plt.subplots_adjust(left=0.1, bottom=0.35) 

# 1. Khai báo biến khởi tạo TRƯỚC
initial_scale = 1.45 
initial_dx = 0
initial_dy = 0

# 2. Định nghĩa hàm tính toán TRƯỚC KHI DÙNG (Quan trọng!)
def calculate_extent(scale, dx, dy):
    new_w = base_width * scale
    new_h = base_height * scale
    
    cx = center_x + dx
    cy = center_y + dy
    
    return [cx - new_w/2, cx + new_w/2, cy - new_h/2, cy + new_h/2]

# 3. Bây giờ mới vẽ ảnh nền (vì đã có hàm calculate_extent để dùng)
img_obj = ax.imshow(img, extent=calculate_extent(initial_scale, 0, 0), aspect='equal', alpha=0.7)

# 4. Vẽ các Node ĐÈ LÊN TRÊN ảnh
nx.draw_networkx_nodes(G, pos, ax=ax, node_size=10, node_color='red', edgecolors='black')

ax.set_title("KÉO THANH TRƯỢT ĐỂ CHỈNH - SAU ĐÓ COPY SỐ Ở DƯỚI")

# --- TẠO CÁC THANH TRƯỢT (SLIDERS) ---
axcolor = 'lightgoldenrodyellow'

ax_scale = plt.axes([0.2, 0.2, 0.6, 0.03], facecolor=axcolor)
s_scale = Slider(ax_scale, 'Độ Phóng (Scale)', 0.1, 10.0, valinit=initial_scale, valstep=0.01)

ax_dx = plt.axes([0.2, 0.15, 0.6, 0.03], facecolor=axcolor)
s_dx = Slider(ax_dx, 'Dịch Ngang (X)', -50.0, 50.0, valinit=0, valstep=0.1)

ax_dy = plt.axes([0.2, 0.1, 0.6, 0.03], facecolor=axcolor)
s_dy = Slider(ax_dy, 'Dịch Dọc (Y)', -50.0, 50.0, valinit=0, valstep=0.1)

# --- HÀM CẬP NHẬT KHI KÉO ---
def update(val):
    scale = s_scale.val
    dx = s_dx.val
    dy = s_dy.val
    
    new_extent = calculate_extent(scale, dx, dy)
    
    img_obj.set_extent(new_extent)
    fig.canvas.draw_idle()

s_scale.on_changed(update)
s_dx.on_changed(update)
s_dy.on_changed(update)

# --- NÚT IN KẾT QUẢ ---
resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'In Tọa Độ', color=axcolor, hovercolor='0.975')

def print_result(event):
    ext = calculate_extent(s_scale.val, s_dx.val, s_dy.val)
    print("\n" + "="*40)
    print("Bộ số cần tìm:")
    print(f"MY_EXTENT = [{ext[0]:.4f}, {ext[1]:.4f}, {ext[2]:.4f}, {ext[3]:.4f}]")
    print("="*40 + "\n")

button.on_clicked(print_result)

plt.show()