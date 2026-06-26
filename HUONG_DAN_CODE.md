# HƯỚNG DẪN CẤU TRÚC MÃ NGUỒN DỰ ÁN SMART SWEEPER

Tài liệu này cung cấp cái nhìn tổng quan về kiến trúc phần mềm, cấu trúc thư mục, chức năng của các file chính và hướng dẫn vận hành mã nguồn dự án **Smart Sweeper - Giải game Dò mìn bằng AI**.

---

## 1. Cấu Trúc Thư Mục Dự Án

Mã nguồn được tổ chức thành các thư mục chức năng rõ ràng:

```text
smart-sweeper/
│
├── core/                   # Chứa logic cốt lõi của trò chơi
│   └── board.py            # Lớp quản lý trạng thái bảng Dò mìn (Board)
│
├── algorithms/             # Chứa các thuật toán giải game bằng AI
│   ├── __init__.py         # Khởi tạo package và factory tạo thuật toán
│   ├── base.py             # Lớp cơ sở (Algorithm) định nghĩa khung thuật toán
│   │
│   ├── uninformed/         # Nhóm 1: BFS, DFS
│   ├── informed/           # Nhóm 2: A*, Greedy Best-First
│   ├── local_search/       # Nhóm 3: Hill Climbing, Simulated Annealing
│   ├── nondeterministic/   # Nhóm 4: AND-OR, Belief State
│   ├── csp/                # Nhóm 5: AC-3, Backtracking CSP
│   └── adversarial/        # Nhóm 6: Minimax, Alpha-Beta Pruning
│
├── ui/                     # Chứa logic vẽ giao diện đồ họa (GUI)
│   ├── helpers.py          # Hàm bổ trợ vẽ nút, văn bản, hiệu ứng 3D
│   └── renderer.py         # Lớp Renderer quản lý vẽ toàn bộ màn hình
│
├── config/                 # Cấu hình hệ thống và giao diện
│   └── settings.py         # Định nghĩa màu sắc, kích thước, danh sách thuật toán
│
├── assets/                 # Chứa hình ảnh, biểu đồ hiệu suất, tài nguyên giao diện
│   ├── icons/              # Icon biểu tượng
│   └── performance_chart.png # Biểu đồ so sánh hiệu suất sinh tự động
│
├── main.py                 # Điểm khởi chạy chương trình (Main Loop)
├── BAO_CAO.md              # Báo cáo cuối kỳ chi tiết của dự án
└── HUONG_DAN_CODE.md       # Hướng dẫn cấu trúc mã nguồn (tài liệu này)
```

---

## 2. Chi Tiết Các Thành Phần Chính

### 2.1. Logic trò chơi (`core/board.py`)
Lớp [Board](file:///c:/Users/quangvinh/.gemini/antigravity/scratch/smart-sweeper/core/board.py) chịu trách nhiệm quản lý toàn bộ trạng thái của một ván chơi Dò mìn:
- Khởi tạo bảng với số dòng, cột và số lượng mìn.
- Đặt mìn ngẫu nhiên sau click đầu tiên để đảm bảo nước đi đầu tiên luôn an toàn.
- Quản lý tập hợp các ô đã mở (`revealed`), cắm cờ (`flagged`) và vị trí mìn (`mines`).
- Thực hiện logic mở ô (`reveal`) kết hợp thuật toán loang (Flood Fill) khi mở trúng ô trống (số 0).
- Cung cấp các hàm API trả về thông tin biên cho AI như `get_frontier_cells()`, `get_neighbors(..., hidden_only=True)`.

### 2.2. Lớp cơ sở thuật toán (`algorithms/base.py`)
Mọi thuật toán AI đều kế thừa từ lớp [Algorithm](file:///c:/Users/quangvinh/.gemini/antigravity/scratch/smart-sweeper/algorithms/base.py):
- Quản lý một bản sao riêng của bảng game (`self.board`) để tính toán độc lập mà không ảnh hưởng trực tiếp đến bảng hiển thị của UI.
- Ghi nhận lịch sử các bước đi (`self.steps`) để UI có thể mô phỏng lại từng bước.
- Thu thập các chỉ số đo lường hiệu suất (`self.metrics`) bao gồm thời gian chạy (ms), số bước đi, số node đã duyệt, tỷ lệ hoàn thành, và kết quả thắng/thua.
- Cung cấp các hàm bổ trợ tính toán xác suất mìn biên (`get_mine_probability`) và áp dụng luật nhất quán cơ bản (`apply_basic_rules`).

### 2.3. Giao diện đồ họa (`ui/renderer.py` & `ui/helpers.py`)
Giao diện trò chơi được xây dựng bằng thư viện Pygame:
- **Renderer**: Quản lý việc vẽ lưới ô mìn dạng 3D nổi khối sang trọng, vẽ sidebar danh sách thuật toán phân cấp theo nhóm (có thể đóng/mở danh mục), vẽ toolbar điều khiển và bảng thống kê kết quả.
- **Helpers**: Cung cấp các hàm vẽ nút bấm mềm mịn, thanh tiến trình loang màu gradient hiện đại, vẽ bóng đổ giả lập 3D và tự động quấn dòng (wrap text) cho mô tả thuật toán.

### 2.4. Vòng lặp chính điều khiển (`main.py`)
Quản lý luồng hoạt động chính của chương trình:
- Nhận diện sự kiện click chuột, phím bấm để điều chỉnh kích thước bảng, số lượng mìn, tốc độ chạy mô phỏng.
- Khi người dùng bấm **Chạy (Play)** hoặc **Bước (Step)**: Kích hoạt thuật toán AI tương ứng giải trên bảng bản sao, thu thập toàn bộ các bước đi và cập nhật trạng thái UI để tiến hành diễn hoạt (animation) từng bước đi theo tốc độ được cấu hình.
- Khi người dùng bấm **So sánh tất cả (So sánh tất cả)**: Chương trình chạy tuần tự tất cả 12 thuật toán trên cùng một bản sao của bảng game hiện tại, thu thập chỉ số hiệu năng và hiển thị bảng xếp hạng so sánh (Leaderboard) trực quan.

---

## 3. Hướng Dẫn Vận Hành Dự Án

### 3.1. Cài đặt môi trường
Mã nguồn yêu cầu Python 3.8+ và thư viện Pygame. 
Cài đặt thư viện phụ thuộc bằng pip:
```bash
pip install pygame
```

### 3.2. Khởi chạy chương trình
Từ thư mục gốc của dự án, chạy lệnh:
```bash
python main.py
```

### 3.3. Các tính năng trên giao diện
1. **Thiết lập bảng đấu**: Thay đổi số hàng, số cột, số mìn và tốc độ diễn hoạt trực tiếp ở sidebar bên trái. Bấm nút **Tạo bảng** để tạo mới một bảng game ngẫu nhiên.
2. **Chọn thuật toán**: Chọn 1 trong 12 thuật toán giải thuộc 6 nhóm hiển thị ở danh sách cây thư mục bên trái.
3. **Chạy mô phỏng đơn lẻ**:
   - Bấm nút **Chạy (Play)**: AI sẽ tự động giải bảng game hiện tại theo thời gian thực với tốc độ đã chọn.
   - Bấm nút **Bước (Step)**: Thực hiện từng bước đi đơn lẻ của AI để quan sát logic lập luận.
   - Bấm nút **Đặt lại (Reset)**: Khôi phục bảng game về trạng thái ban đầu để chạy lại hoặc chọn thuật toán khác.
4. **So sánh tổng quan**: Bấm nút **So sánh tất cả (So sánh tất cả)** để hệ thống tự động chạy đồng loạt 12 thuật toán trên cùng một cấu hình bảng, sau đó hiển thị bảng xếp hạng so sánh hiệu năng trực quan ngay trên màn hình chính.
