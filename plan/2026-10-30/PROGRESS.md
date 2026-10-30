# Tiến trình thực hiện (30/10/2026)

Plan chi tiết: [PLAN.md](PLAN.md)

| Giai đoạn | Nội dung | Trạng thái |
|---|---|---|
| GĐ0 | Khởi tạo git, commit hiện trạng | Xong |
| GĐ1 | Xóa file không dùng | Xong |
| GĐ2 | Tổ chức lại thư mục | Xong |
| GĐ3 | Tách thuật toán, dùng lớp chung | Xong |
| GĐ4 | Tách giao diện, dùng chung settings | Xong |
| GĐ5 | Tách vòng lặp game và ma | Xong |
| GĐ6 | Sửa lỗi | Xong |
| GĐ7 | Test, README, push lên GitHub | Xong |

## Kết quả

| Chỉ số | Trước | Sau |
|---|---|---|
| Asset | 635 file | 190 file |
| File Python lớn nhất | 990 dòng | dưới 400 dòng |
| Hàm dài nhất | 348 dòng | dưới 80 dòng |
| Test tự động | 0 | 24 |
| Cảnh báo pyflakes | 18 | 0 |

## Nhật ký

- GĐ0: repo GitHub `Thien21112005/fairy-vs-dinosaur` đang trống. Tạo bộ so sánh hành vi gồm 19 kịch bản (trạng thái game và hash ảnh màn hình).
- GĐ1: xóa 445 asset không dùng và `src tạm/`; đổi tên `Ghost_eat.mp3` thành `ghost_eat.mp3`. Hành vi giống hệt mốc.
- GĐ2: chuyển code vào `fairy_vs_dinosaur/`, đổi tên thư mục asset, đưa dữ liệu vào `data/`. Hành vi giống hệt mốc.
- GĐ3: gom phần chung vào `BasePathFinder`, bỏ `find_full_path` không dùng ở 6 thuật toán. Hành vi giống hệt mốc.
- GĐ4: tạo `widgets`, `OverlayMenu`, `GameOverScreen`, `settings_store`. Hành vi giống hệt mốc.
- GĐ5: tách `run()` theo trạng thái và tách `Ghost` thành phần di chuyển và phần vẽ. Bộ so sánh bắt được 2 sai lệch do tách code; đã sửa trước khi commit, sau đó giống hệt mốc.
- GĐ6: sửa các lỗi trong plan. Từ giai đoạn này hành vi thay đổi có chủ đích nên chuyển sang kiểm tra bằng test và ảnh chụp màn hình.
- GĐ7: thêm test, README hai ngôn ngữ, push lên GitHub.

## Lỗi phát hiện thêm trong lúc làm

Các lỗi này không có trong plan ban đầu và đã được sửa:

- Dòng `print` có emoji làm game văng lúc qua màn nếu console không dùng UTF-8.
- Ma quay đầu sai hướng: `(direction + 2) % 4` biến "ngược lại của phải" thành "lên".
- Nền của màn Level Complete dùng lại ảnh từ lần qua màn trước.
- Thiếu bản dịch `level complete`, `paused`, `resume` nên các tiêu đề hiện chữ thường chưa dịch.
- Khi không tìm được đường, AI đứng yên thay vì đi ngẫu nhiên để thoát kẹt.
- Ma ẩn vẫn bị tính phạt khi AI tìm đường, nên có hạt không tới được.
- Có hai `PauseMenu` nên âm thanh hover phát hai lần.
- Màn Settings chạy không giới hạn FPS, chiếm trọn một nhân CPU.
- High Score thiếu 10 điểm cuối khi qua màn.
- File settings có ngôn ngữ không hỗ trợ làm màn Settings văng.

## Còn lại cho bạn

- Tự chơi một ván để kiểm tra âm thanh và cảm giác chơi, vì kiểm thử chạy không có cửa sổ và không nghe được.
- Chọn giấy phép (LICENSE) nếu muốn người khác được dùng lại code.

## Lưu ý

- DFS vẫn hoàn thành màn nhưng rất chậm: khoảng 59.000 khung hình, tức khoảng 16 phút khi tắt hết ma. Đây là đặc điểm của thuật toán nên không sửa.
- High Score vẫn chỉ giữ trong một lần chơi, không lưu sang lần sau. Đây là tính năng mới nên nằm ngoài plan.
