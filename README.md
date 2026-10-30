# Fairy vs Dinosaur

A maze arcade game built with Python and Pygame, where seven search algorithms can play the game and be compared side by side.

[English](#english) | [Tiếng Việt](#tiếng-việt)

![Gameplay with path hints enabled](docs/images/gameplay.png)

---

## English

### Overview

You control a fairy through a maze, collecting every pellet while four dinosaurs hunt you down. Power pellets turn the tables for a few seconds, letting you defeat dinosaurs for bonus points.

Instead of playing by hand, you can hand control to a search algorithm and watch it play. Each AI run is recorded, and the History screen compares the algorithms using tables and charts.

The project was created at Ho Chi Minh City University of Technology and Education (HCMUTE).

### Features

- Seven pathfinding algorithms the fairy can use: BFS, DFS, UCS, A*, Greedy, Beam Search and Hill Climbing
- Four dinosaurs with distinct chase and patrol behaviour, including scatter, chase and frightened modes
- Path hints that visualize what the fairy and each dinosaur are planning
- Performance history with comparison charts for every algorithm
- English, Vietnamese, French and Spanish interface
- Adjustable music and sound effects, with three control schemes

### Getting started

Requirements: Python 3 (tested on 3.13) and the packages in `requirements.txt`.

```bash
git clone https://github.com/Thien21112005/fairy-vs-dinosaur.git
cd fairy-vs-dinosaur
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS and Linux
pip install -r requirements.txt
python main.py
```

### How to play

| Action | Control |
|---|---|
| Move | Arrow keys or WASD, set in Settings |
| Pause and resume | Esc, or the pause button |
| Let an algorithm play | Click SOLVE and choose an algorithm |
| Show planned paths | Click HINT |
| Show or hide a dinosaur | Click B, P, I or C |

Choosing an algorithm and pressing a movement key are mutually exclusive: the first one you use locks the mode for that game. Only AI games are recorded in History.

### Algorithms

| Algorithm | Strategy when choosing the next pellet |
|---|---|
| BFS | Fewest steps to the closest pellet |
| DFS | First pellet found going deep; it finishes the level but takes far longer than the others |
| UCS | Lowest total cost, where cells near a dinosaur cost more |
| A* | Lowest cost, guided by the distance to the nearest pellet |
| Greedy | Whatever looks closest to a pellet, avoiding cells next to a dinosaur |
| Beam Search | Like A*, but keeps only the 5 best candidates at each depth |
| Hill Climbing | Randomly moves to neighbours that get closer, and commits to the route it finds |

The History screen reports these values per game:

| Value | Meaning |
|---|---|
| Time | Total time spent searching, in seconds |
| Nodes | Total nodes expanded |
| Path | Cells the fairy actually walked |
| Memory | Peak memory use, estimated from the size of the search structures |
| Success | Share of games that cleared the level |

### Project structure

```
main.py                  Entry point
assets/                  Images and sounds
data/                    Settings and history, created on first run and not tracked by git
tests/                   Automated tests
fairy_vs_dinosaur/
    config.py            File locations
    settings_store.py    Reads and writes settings
    audio/               Sound effects and music
    core/                Game loop, input, rendering, level and history
    entities/            Fairy and dinosaurs
    i18n/                Translations
    pathfinding/         The seven algorithms and their shared base class
    ui/                  HUD, overlay menus and full-screen menus
```

### Running the tests

```bash
python -m unittest discover -s tests -t .
```

The tests run without a window or sound device and take about a minute. They do not touch your saved settings or history.

### Team

| Member | Role |
|---|---|
| Nguyễn Ngọc Thiện | Lead programmer: gameplay, AI pathfinding and systems integration |
| Nghiêm Phú Đăng Quân | UI/UX and sound: interface, menus and audio |
| Nguyễn Quốc Khoa | Graphics and levels: assets, level layouts and visual effects |

### License

The source code is released under the [MIT License](LICENSE). Files in `assets/` may be subject to the terms of their original creators and are not covered by this license.

---

## Tiếng Việt

### Giới thiệu

Bạn điều khiển một nàng tiên đi qua mê cung, ăn hết các hạt trong khi bốn con khủng long săn đuổi. Hạt năng lượng đảo ngược tình thế trong vài giây, cho phép bạn hạ khủng long để nhận điểm thưởng.

Thay vì tự chơi, bạn có thể giao quyền điều khiển cho một thuật toán tìm kiếm và xem nó chơi. Mỗi lượt chơi bằng AI đều được lưu lại, và màn hình History so sánh các thuật toán bằng bảng và biểu đồ.

Dự án được thực hiện tại Trường Đại học Sư phạm Kỹ thuật TP.HCM (HCMUTE).

### Tính năng

- Bảy thuật toán tìm đường cho nàng tiên: BFS, DFS, UCS, A*, Greedy, Beam Search và Hill Climbing
- Bốn con khủng long với cách đuổi và tuần tra riêng, gồm các chế độ tản ra, truy đuổi và hoảng sợ
- Gợi ý đường đi, hiển thị kế hoạch của nàng tiên và từng con khủng long
- Lịch sử hiệu năng với biểu đồ so sánh các thuật toán
- Giao diện tiếng Anh, tiếng Việt, tiếng Pháp và tiếng Tây Ban Nha
- Tùy chỉnh nhạc nền, hiệu ứng âm thanh và ba kiểu điều khiển

### Cài đặt và chạy

Yêu cầu: Python 3 (đã kiểm thử trên 3.13) và các gói trong `requirements.txt`.

```bash
git clone https://github.com/Thien21112005/fairy-vs-dinosaur.git
cd fairy-vs-dinosaur
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS và Linux
pip install -r requirements.txt
python main.py
```

### Cách chơi

| Thao tác | Điều khiển |
|---|---|
| Di chuyển | Phím mũi tên hoặc WASD, chọn trong Settings |
| Tạm dừng và tiếp tục | Esc, hoặc nút tạm dừng |
| Để thuật toán chơi | Bấm SOLVE rồi chọn thuật toán |
| Hiện đường đi dự kiến | Bấm HINT |
| Hiện hoặc ẩn một con khủng long | Bấm B, P, I hoặc C |

Chọn thuật toán và bấm phím di chuyển loại trừ nhau: thao tác nào dùng trước sẽ khóa chế độ của ván đó. Chỉ các ván chơi bằng AI mới được lưu vào History.

### Các thuật toán

| Thuật toán | Cách chọn hạt tiếp theo |
|---|---|
| BFS | Ít bước nhất tới hạt gần nhất |
| DFS | Hạt đầu tiên gặp khi đi theo chiều sâu; vẫn hoàn thành màn nhưng lâu hơn hẳn các thuật toán khác |
| UCS | Tổng chi phí thấp nhất, ô gần khủng long có chi phí cao hơn |
| A* | Chi phí thấp nhất, có định hướng theo khoảng cách tới hạt gần nhất |
| Greedy | Ô có vẻ gần hạt nhất, tránh các ô sát khủng long |
| Beam Search | Giống A* nhưng chỉ giữ 5 ứng viên tốt nhất ở mỗi độ sâu |
| Hill Climbing | Đi ngẫu nhiên tới ô kề gần hạt hơn và theo hết đường đã tìm được |

Màn hình History báo cáo các giá trị sau cho mỗi ván:

| Giá trị | Ý nghĩa |
|---|---|
| Time | Tổng thời gian tìm đường, tính bằng giây |
| Nodes | Tổng số nút đã mở rộng |
| Path | Số ô nàng tiên thực sự đã đi |
| Memory | Bộ nhớ cao nhất, ước lượng theo kích thước các cấu trúc tìm kiếm |
| Success | Tỷ lệ ván hoàn thành màn chơi |

### Cấu trúc dự án

```
main.py                  Điểm chạy chương trình
assets/                  Hình ảnh và âm thanh
data/                    Settings và history, tự tạo khi chạy lần đầu, không đưa lên git
tests/                   Kiểm thử tự động
fairy_vs_dinosaur/
    config.py            Đường dẫn file
    settings_store.py    Đọc và ghi settings
    audio/               Hiệu ứng âm thanh và nhạc nền
    core/                Vòng lặp game, xử lý nhập, vẽ, màn chơi và lịch sử
    entities/            Nàng tiên và khủng long
    i18n/                Bản dịch
    pathfinding/         Bảy thuật toán và lớp cơ sở dùng chung
    ui/                  HUD, menu nổi và các màn hình menu
```

### Chạy kiểm thử

```bash
python -m unittest discover -s tests -t .
```

Bộ kiểm thử chạy không cần cửa sổ hay thiết bị âm thanh, mất khoảng một phút và không ảnh hưởng tới settings hay history đã lưu.

### Nhóm thực hiện

| Thành viên | Vai trò |
|---|---|
| Nguyễn Ngọc Thiện | Lập trình chính: lối chơi, thuật toán tìm đường và tích hợp hệ thống |
| Nghiêm Phú Đăng Quân | Giao diện và âm thanh: giao diện, menu và âm thanh |
| Nguyễn Quốc Khoa | Đồ họa và màn chơi: tài nguyên, bố cục màn chơi và hiệu ứng hình ảnh |

### Giấy phép

Mã nguồn được phát hành theo [Giấy phép MIT](LICENSE). Các file trong `assets/` có thể thuộc điều khoản của tác giả gốc và không nằm trong phạm vi giấy phép này.
