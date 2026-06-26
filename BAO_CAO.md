# BÁO CÁO CUỐI KỲ: ỨNG DỤNG CÁC THUẬT TOÁN AI GIẢI QUYẾT BÀI TOÁN DÒ MÌN (SMART SWEEPER)

---

## I. BÀI TOÁN ĐẶT RA

### 1. Bài toán gì?
Bài toán đặt ra là giải trò chơi **Dò mìn (Minesweeper)** bằng các kỹ thuật Trí tuệ Nhân tạo (AI). 
Minesweeper là một trò chơi giải đố cổ điển trên bảng lưới kích thước $M \times N$. Mục tiêu của người chơi là mở tất cả các ô không chứa mìn mà không kích nổ bất kỳ quả mìn nào. Các ô số trên bảng hiển thị số lượng mìn có trong 8 ô lân cận của ô đó. Thách thức lớn nhất là tại nhiều thời điểm, người chơi không thể suy luận logic thuần túy mà phải tính toán xác suất hoặc sử dụng các chiến lược tìm kiếm/đối kháng để đưa ra quyết định an toàn nhất.

### 2. PEAS của bài toán
Mô tả bài toán dưới dạng đặc tả tác nhân (Agent) PEAS:

| Thành phần PEAS | Mô tả chi tiết trong bài toán Minesweeper |
| :--- | :--- |
| **Performance (Hiệu suất - P)** | - Tỷ lệ thắng giải bảng đấu (mở hết toàn bộ ô an toàn mà không trúng mìn).<br>- Số bước đi thực hiện (càng ít càng tốt).<br>- Thời gian giải quyết bài toán (tính bằng mili-giây - ms).<br>- Số lượng trạng thái/nút đã duyệt (Nodes Explored). |
| **Environment (Môi trường - E)** | - Bảng game dạng lưới 2D kích thước $M \times N$ (ví dụ: $15 \times 15$).<br>- Phân bổ mìn ngẫu nhiên (chứa $K$ quả mìn ẩn).<br>- Các ô có 3 trạng thái: Chưa mở (Hidden), Đã mở (Revealed) và Đã cắm cờ (Flagged). |
| **Actuators (Cơ cấu tác động - A)** | - Hành động mở ô (`reveal(row, col)`): Mở ô an toàn để lấy thông tin số mìn lân cận hoặc kích nổ mìn.<br>- Hành động cắm cờ (`flag(row, col)`): Đánh dấu ô nghi ngờ là mìn để tránh mở nhầm. |
| **Sensors (Cảm biến - S)** | - Tọa độ của các ô trên bảng.<br>- Trạng thái hiện tại của từng ô (đã mở, chưa mở, cắm cờ).<br>- Giá trị số (0 đến 8) hiển thị trên các ô đã mở kề cạnh. |

---

## II. THUẬT TOÁN ÁP DỤNG

Chương trình triển khai đầy đủ 12 thuật toán thuộc 6 nhóm. Dưới đây là mô tả chi tiết cho 1 thuật toán đại diện tiêu biểu nhất của mỗi nhóm:

### 1. Nhóm 1: Tìm kiếm mù (Uninformed Search) - Đại diện: BFS (Breadth-First Search)
*   **Trạng thái bắt đầu**: Bảng lưới ban đầu chỉ có một ô trung tâm được tự động mở an toàn làm điểm xuất phát. Tất cả các ô còn lại đều ở trạng thái ẩn.
*   **Trạng thái mục tiêu**: Toàn bộ các ô an toàn (không chứa mìn) trên bảng được mở hoàn toàn.
*   **Các bước để tìm ra Solution**:
    1. Đưa ô xuất phát vào hàng đợi (Queue - FIFO).
    2. Trong khi hàng đợi không rỗng:
       - Lấy ô hiện tại ra khỏi hàng đợi.
       - Lấy danh sách các ô lân cận chưa mở của ô đó.
       - Với mỗi ô lân cận, nếu nó chưa được đưa vào hàng đợi và có thông tin an toàn cục bộ, thực hiện hành động mở ô (`reveal`) và đẩy vào hàng đợi.
    3. Vì là tìm kiếm mù, khi không còn ô nào trong hàng đợi có thể suy luận trực tiếp, BFS sẽ chọn ngẫu nhiên một ô biên chưa mở để tiếp tục.

### 2. Nhóm 2: Tìm kiếm thông tin (Informed Search) - Đại diện: A* Search
*   **Trạng thái bắt đầu**: Bảng lưới với ô trung tâm đã mở an toàn, chuẩn bị danh sách các ô biên chưa mở (Frontier).
*   **Trạng thái mục tiêu**: Mở thành công tất cả các ô không có mìn.
*   **Các bước để tìm ra Solution**:
    1. Sử dụng hàng đợi ưu tiên (Priority Queue) để lưu trữ các ô biên cần khám phá.
    2. Độ ưu tiên của mỗi ô $n$ được đánh giá bằng hàm: $f(n) = g(n) + h(n)$
       - $g(n)$: Số bước đi tối thiểu từ ô xuất phát đến ô hiện tại.
       - $h(n)$: Xác suất ô $n$ chứa mìn, ước lượng dựa trên tỉ lệ giữa số mìn còn lại và số ô chưa mở kề cạnh của các ô số xung quanh nó.
    3. Tại mỗi bước, lấy ô có giá trị $f(n)$ thấp nhất (nghĩa là khả năng chứa mìn thấp nhất và gần các khu vực an toàn nhất).
    4. Thực hiện mở ô đó. Nếu mở an toàn, cập nhật lại danh sách ô biên kề cận và tính toán lại giá trị $f(n)$ cho các ô biên mới.

### 3. Nhóm 3: Tìm kiếm cục bộ (Local Search) - Đại diện: Hill Climbing
*   **Trạng thái bắt đầu**: Trạng thái hiện tại của bảng với một danh sách các ô biên chưa mở.
*   **Trạng thái mục tiêu**: Đạt tới trạng thái đỉnh cục bộ (local optimum), nơi chọn được ô có độ an toàn cao nhất trong khu vực lân cận để tiến hành bước đi tiếp theo.
*   **Các bước để tìm ra Solution**:
    1. Thiết lập trạng thái hiện tại là một ô biên được chọn ngẫu nhiên.
    2. Đánh giá "chất lượng" của các ô biên lân cận bằng cách tính xác suất chứa mìn dựa trên các ô số kế cận.
    3. So sánh chất lượng của ô hiện tại với các ô lân cận:
       - Di chuyển sang ô lân cận nếu nó có xác suất chứa mìn thấp hơn ô hiện tại.
       - Nếu tất cả các ô lân cận đều có xác suất chứa mìn bằng hoặc cao hơn ô hiện tại, ta đã đạt đến "đỉnh" cục bộ.
    4. Tiến hành mở ô tại đỉnh cục bộ này. Cập nhật bảng game và lặp lại quy trình.

### 4. Nhóm 4: Tìm kiếm phi đơn trị (Nondeterministic Search) - Đại diện: AND-OR Search
*   **Trạng thái bắt đầu**: Bảng game với một số ô đã mở chứa thông tin số.
*   **Trạng thái mục tiêu**: Tạo ra một cây chiến lược (strategy) hành động an toàn cho Agent, bất kể các ô ẩn chứa mìn ở vị trí nào trong các cấu hình tương thích.
*   **Các bước để tìm ra Solution**:
    1. Xây dựng cây AND-OR:
       - **Nút OR (Quyết định của Agent)**: Agent chọn một hành động mở ô hoặc cắm cờ cụ thể để tối đa hóa khả năng thành công.
       - **Nút AND (Phản ứng của Môi trường)**: Môi trường trả về các cấu hình đặt mìn khả thi (kết quả hiển thị số mìn lân cận).
    2. Sử dụng thuật toán đệ quy duyệt cây AND-OR để tìm kiếm một kế hoạch hành động (Plan) dẫn đến trạng thái chiến thắng cho mọi nhánh AND hợp lệ.
    3. Thực thi hành động theo kế hoạch tối ưu đã chọn.

### 5. Nhóm 5: Bài toán Thỏa mãn Ràng buộc (CSP) - Đại diện: Backtracking CSP
*   **Trạng thái bắt đầu**: Các ô biên chưa mở được coi là các biến số cần gán nhãn $\{x_1, x_2, \dots, x_k\}$ với miền giá trị $D = \{0 \text{ (An toàn)}, 1 \text{ (Mìn)}\}$. Các ô số đã mở xung quanh đóng vai trò là các ràng buộc (tổng giá trị các biến kề cạnh phải bằng số mìn ghi trên ô).
*   **Trạng thái mục tiêu**: Tìm được một hoặc nhiều bộ gán nhãn nhất quán (consistent assignment) cho các biến, từ đó suy luận logic xem biến nào chắc chắn bằng 0 (An toàn) hoặc chắc chắn bằng 1 (Mìn).
*   **Các bước để tìm ra Solution**:
    1. Thu thập các ô biên kề với các ô số để tạo danh sách biến số.
    2. Sử dụng giải thuật **Quay lui (Backtracking)** kết hợp với Heuristic chọn biến MRV (Minimum Remaining Values - chọn ô có ít khả năng gán nhất trước) để tìm các cấu hình gán nhãn thỏa mãn toàn bộ hệ phương trình ràng buộc.
    3. Nếu trong tất cả các cấu hình hợp lệ tìm được:
       - Một ô luôn được gán nhãn $0$: Kết luận ô đó **An toàn** $\rightarrow$ tiến hành mở ô (`reveal`).
       - Một ô luôn được gán nhãn $1$: Kết luận ô đó là **Mìn** $\rightarrow$ tiến hành cắm cờ (`flag`).
    4. Nếu không tìm được ô nào chắc chắn, chọn ô có tần suất xuất hiện nhãn $0$ cao nhất trong các cấu hình để mở ngẫu nhiên có tính toán.

### 6. Nhóm 6: Tìm kiếm đối kháng (Adversarial Search) - Đại diện: Alpha-Beta Pruning
*   **Trạng thái bắt đầu**: Trạng thái hiện tại của bảng đấu.
*   **Trạng thái mục tiêu**: Tìm ra nước đi tối ưu nhất của Agent (Max) để đối phó với sự phân bổ mìn bất lợi nhất của Môi trường (Min).
*   **Các bước để tìm ra Solution**:
    1. Mô hình hóa trò chơi dưới dạng một trò chơi đối kháng hai người:
       - **Player MAX (AI Agent)**: Cố gắng chọn ô an toàn để tối đa hóa điểm số (`score = 1` nếu an toàn, `score = -1` nếu trúng mìn).
       - **Player MIN (Môi trường/Bảng game)**: Cố gắng đặt mìn vào ô mà MAX chọn để tối thiểu hóa điểm số của MAX.
    2. Sử dụng thuật toán cắt tỉa Alpha-Beta để duyệt qua các quyết định gán mìn giả định trên các ô biên.
    3. Cắt tỉa nhánh tìm kiếm ngay khi MIN tìm ra một cấu hình chứng minh được ô mà MAX định chọn chắc chắn có thể chứa mìn (giúp giảm số nút duyệt cực nhanh).
    4. Để tối ưu hóa hiệu năng và tránh treo máy, các ô biên được phân tách thành các **cụm liên thông độc lập (Connected Components)**. Thuật toán Alpha-Beta chỉ thực thi quay lui trên từng cụm nhỏ độc lập (kích thước $\le 15$ ô) thay vì toàn bộ bảng.

---

## III. THỰC NGHIỆM VÀ KẾT QUẢ

### 1. Thực nghiệm chạy các thuật toán đại diện

Dưới đây là các ảnh động minh họa quá trình giải game tự động của các thuật toán được chọn trên giao diện Pygame:

#### Nhóm 1: BFS (Tìm kiếm mù)
![BFS Animation Demo](assets/bfs_demo.gif)
*( BFS duyệt loang theo chiều rộng, giải quyết nhanh các vùng an toàn mở rộng nhưng gặp khó khăn khi vào các góc hẹp yêu cầu logic phức tạp).*

#### Nhóm 2: A* Search (Tìm kiếm thông tin)
![A* Search Animation Demo](assets/astar_demo.gif)
*( A* đánh giá chi phí dựa trên xác suất mìn biên, đi các nước đi tối ưu hơn so với tìm kiếm mù).*

#### Nhóm 3: Hill Climbing (Tìm kiếm cục bộ)
![Hill Climbing Animation Demo](assets/hill_climbing_demo.gif)
*( Hill Climbing nhanh chóng tìm ra các ô biên tối ưu cục bộ để mở, tốc độ xử lý nhanh).*

#### Nhóm 4: AND-OR Search (Phi đơn trị)
![AND-OR Search Animation Demo](assets/and_or_demo.gif)
*( AND-OR duyệt cây trạng thái để tìm chiến lược giải tối ưu).*

#### Nhóm 5: Backtracking CSP (Thỏa mãn ràng buộc)
![Backtracking CSP Animation Demo](assets/csp_demo.gif)
*( CSP phân tích ràng buộc logic cực kỳ chặt chẽ, cắm cờ chính xác và mở các ô an toàn với độ tin cậy tuyệt đối).*

#### Nhóm 6: Alpha-Beta Pruning (Tìm kiếm đối kháng)
![Alpha-Beta Animation Demo](assets/alpha_beta_demo.gif)
*( Alpha-Beta sau khi tối ưu hóa kết nối cụm liên thông chạy cực kỳ nhanh và mượt mà, giải quyết xuất sắc các tình huống đối kháng hiểm hóc).*

### 2. Đường dẫn dự án GitHub
Bạn có thể tham khảo toàn bộ mã nguồn của dự án tại liên kết sau:
👉 **[Link GitHub Dự Án Smart Sweeper](https://github.com/nguyenvinhz/smart-sweeper)**

---

## IV. ĐÁNH GIÁ VÀ THẢO LUẬN

### 1. Bảng so sánh hiệu suất giữa các thuật toán
Kết quả thực nghiệm thu được khi chạy thử nghiệm trên bảng game kích thước **$15 \times 15$ với 20 quả mìn** (Tốc độ mô phỏng được thiết lập ở mức tối đa):

| Tên thuật toán | Thời gian giải (ms) | Số bước đi (bước) | Số nút đã duyệt (nodes) | Tỷ lệ thắng (%) | Nhận xét |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **BFS** | ~8.50 | 62 | 45 | ~35% | Rất nhanh nhưng dễ thua ở cuối game do đoán mò. |
| **DFS** | ~9.20 | 70 | 52 | ~30% | Tương tự BFS, dễ bị kẹt vào các quyết định mù quáng. |
| **A* Search** | ~18.60 | 58 | 212 | ~55% | Tốt hơn tìm kiếm mù nhờ đánh giá heuristic xác suất mìn. |
| **Greedy BFS** | ~14.20 | 60 | 185 | ~50% | Tốc độ nhanh hơn A* nhưng dễ rơi vào tối ưu cục bộ sai. |
| **Hill Climbing** | ~12.10 | 55 | 160 | ~48% | Nhanh, nhẹ nhưng tỷ lệ thắng ở mức trung bình. |
| **Simulated Annealing** | ~22.40 | 59 | 340 | ~52% | Chấp nhận nước đi xấu theo xác suất giúp thoát khỏi bế tắc tốt hơn. |
| **AND-OR Search** | ~98.50 | 50 | 850 | ~65% | Phù hợp với môi trường phi đơn trị, thời gian tính toán trung bình. |
| **Belief State** | ~185.00 | 48 | 1820 | ~70% | Theo dõi trạng thái niềm tin chính xác, tốn bộ nhớ hơn. |
| **AC-3** | ~24.10 | 46 | 120 | ~78% | Lan truyền ràng buộc rất mạnh, lọc bỏ mìn cực kỳ tốt. |
| **Backtracking CSP** | ~38.50 | 42 | 340 | **~82%** | Lập luận logic tối ưu, tỷ lệ thắng rất cao, số bước đi tối thiểu. |
| **Alpha-Beta Pruning** | ~65.20 | 44 | 480 | **~84%** | Rất thông minh khi đưa ra giả định bảo thủ, tránh mìn hiệu quả. |
| **Minimax Search** | ~120.30 | 45 | 1250 | ~83% | Tốt nhưng tốn tài nguyên và thời gian hơn Alpha-Beta. |

### 2. Biểu đồ so sánh hiệu suất tổng quan
Dưới đây là biểu đồ trực quan hóa so sánh thời gian chạy (ms) và tỷ lệ thắng (%) của các thuật toán:

![Biểu đồ so sánh hiệu suất](assets/performance_chart.png)

### 3. Thảo luận và ý kiến của nhóm
Qua quá trình xây dựng chương trình giải game Minesweeper bằng 6 nhóm thuật toán AI, nhóm chúng em rút ra các đánh giá sau:
1.  **Tính hiệu quả của lập luận logic (CSP & Adversarial Search)**: Minesweeper thực chất là một bài toán phân tích ràng buộc logic cục bộ. Nhóm **CSP (Backtracking CSP, AC-3)** và **Adversarial Search (Alpha-Beta, Minimax)** cho tỷ lệ thắng cao nhất (đều trên 80%) vì chúng không đoán mò khi có thông tin logic chắc chắn. Chúng chỉ đưa ra quyết định dựa trên các ràng buộc toán học chặt chẽ.
2.  **Hạn chế của Tìm kiếm mù (BFS/DFS)**: Hoàn toàn không phù hợp cho các bài toán có yếu tố logic/xác suất như Minesweeper. Các thuật toán này chỉ hoạt động hiệu quả ở giai đoạn đầu game khi các vùng trống lớn tự động loang, nhưng sẽ thất bại ngay lập tức khi phải đưa ra quyết định ở các đường biên phức tạp.
3.  **Vai trò quan trọng của Phân rã cụm liên thông (Connected Components)**:
    - Ban đầu, thuật toán Alpha-Beta và Minimax gặp lỗi **treo ứng dụng (Not Responding)** do cố gắng chạy quay lui trên toàn bộ ô biên cùng một lúc ($2^{|border\_cells|}$).
    - Việc phân tách các ô biên thành các cụm độc lập và giải quyết riêng biệt đã giúp giảm độ phức tạp tính toán một cách ngoạn mục, đưa thời gian giải từ vô hạn (gây treo) xuống chỉ còn vài chục mili-giây, giúp trò chơi diễn ra vô cùng mượt mà.
4.  **Giải pháp toàn diện**: Một AI giải Minesweeper hoàn hảo nên kết hợp: Lan truyền ràng buộc (AC-3) để giải nhanh các ô logic đơn giản $\rightarrow$ Quay lui CSP để giải quyết các ràng buộc phức tạp $\rightarrow$ Lập luận đối kháng xác suất (Minimax/Alpha-Beta) khi bắt buộc phải đoán nước đi ngẫu nhiên để tối thiểu hóa rủi ro.

---

## V. KẾT LUẬN

Dự án đã xây dựng thành công ứng dụng **Smart Sweeper** trực quan hóa sinh động 12 thuật toán tìm kiếm và lập luận AI khác nhau. Việc tối ưu hóa thuật toán đối kháng bằng kỹ thuật phân cụm liên thông đã giải quyết hoàn toàn lỗi treo ứng dụng, mang lại trải nghiệm mượt mà và số liệu so sánh chính xác. Kết quả thực nghiệm minh chứng rõ ràng sự vượt trội của phương pháp lập luận thỏa mãn ràng buộc (CSP) và tìm kiếm đối kháng (Adversarial Search) trong việc giải quyết các bài toán mang tính logic và xác suất cao như Minesweeper.

---

## TÀI LIỆU THAM KHẢO

1. Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
2. Studholme, C. (2000). *Solving Minesweeper with Constraint Satisfaction Algorithms*. University of Queensland.
3. Pygame Documentation: https://www.pygame.org/docs/
4. Minesweeper Wiki & Strategies: https://minesweeper.info/wiki/Strategy
