import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider, Button
import os

# --- CẤU HÌNH FILE ---
# Đảm bảo file Sahinh.png đã được cắt sát viền!
GRAPH_FILE = "Competition_track_graphfake.graphml"
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

# Tính toán khung bao (Bounding Box) của các node
min_x, max_x = min(all_x), max(all_x)
min_y, max_y = min(all_y), max(all_y)

# Tâm của hệ thống node
center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2

# Chiều rộng và chiều cao thực tế của hệ thống node
# (Nếu ảnh cắt chuẩn, tỷ lệ width/height này sẽ khớp với tỷ lệ ảnh)
base_width = max_x - min_x
base_height = max_y - min_y

print(f"Kích thước thực tế của track: Rộng {base_width:.2f}m x Cao {base_height:.2f}m")

img = mpimg.imread(IMG_FILE)

# --- THIẾT LẬP GIAO DIỆN ---
fig, ax = plt.subplots(figsize=(12, 8)) # Tăng size cửa sổ cho dễ nhìn
plt.subplots_adjust(left=0.1, bottom=0.35) 

# Vẽ Graph
nx.draw_networkx_nodes(G, pos, ax=ax, node_size=15, node_color='red')

# Vẽ ảnh nền ban đầu
initial_scale = 1.1 # Bắt đầu với scale nhỏ hơn vì ảnh đã cắt sát
initial_dx = 0
initial_dy = 0

def calculate_extent(scale, dx, dy):
    # Tính toán kích thước hiển thị dựa trên scale
    current_w = base_width * scale
    current_h = base_height * scale
    
    # Tính toán tâm mới sau khi dịch chuyển
    cx = center_x + dx
    cy = center_y + dy
    
    # Trả về [left, right, bottom, top]
    return [cx - current_w/2, cx + current_w/2, cy - current_h/2, cy + current_h/2]

# QUAN TRỌNG: Dùng aspect='equal' để không bị méo hình
img_obj = ax.imshow(img, extent=calculate_extent(initial_scale, 0, 0), aspect='equal', alpha=0.6)

ax.set_title("KÉO THANH TRƯỢT ĐỂ CHỈNH - SAU ĐÓ COPY SỐ Ở DƯỚI")
ax.grid(True, linestyle='--', alpha=0.5) # Thêm lưới cho dễ căn

# --- TẠO CÁC THANH TRƯỢT (SLIDERS) ---
axcolor = 'lightgoldenrodyellow'

ax_scale = plt.axes([0.2, 0.2, 0.6, 0.03], facecolor=axcolor)
# Scale cho phép nhỏ hơn 1 tí để thu hình nếu cần
s_scale = Slider(ax_scale, 'Độ Phóng (Scale)', 0.5, 5.0, valinit=initial_scale, valstep=0.01)

ax_dx = plt.axes([0.2, 0.15, 0.6, 0.03], facecolor=axcolor)
s_dx = Slider(ax_dx, 'Dịch Ngang (X)', -20.0, 20.0, valinit=0, valstep=0.05)

ax_dy = plt.axes([0.2, 0.1, 0.6, 0.03], facecolor=axcolor)
s_dy = Slider(ax_dy, 'Dịch Dọc (Y)', -20.0, 20.0, valinit=0, valstep=0.05)

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
    print("Bộ số cần tìm (MY_EXTENT):")
    print(f"[{ext[0]:.4f}, {ext[1]:.4f}, {ext[2]:.4f}, {ext[3]:.4f}]")
    print("="*40 + "\n")

button.on_clicked(print_result)

plt.show()