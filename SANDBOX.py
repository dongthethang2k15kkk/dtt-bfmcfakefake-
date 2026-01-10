import matplotlib.pyplot as plt

# Dữ liệu từ hình ảnh của bạn
x = [3.598, 4.046, 4.195, 4.346, 4.376, 4.519, 4.398, 4.398, 4.304]
y = [0.697, 0.675, 0.717, 0.885, 2.178, 2.593, 2.774, 3.408, 3.783]
labels = ['n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8', 'n9', 'n10']

plt.figure(figsize=(6, 8))
plt.plot(x, y, '-o', color='blue', label='Path') # Nối các điểm

# Hiển thị tên điểm để soi lỗi
for i, txt in enumerate(labels):
    plt.annotate(txt, (x[i], y[i]), textcoords="offset points", xytext=(5,5))

plt.title("Kiểm tra độ mượt quỹ đạo (Trajectory Smoothness)")
plt.xlabel("X (m)")
plt.ylabel("Y (m)")
plt.grid(True)
plt.axis('equal') # Quan trọng: để tỉ lệ X và Y bằng nhau như thực tế
plt.show()