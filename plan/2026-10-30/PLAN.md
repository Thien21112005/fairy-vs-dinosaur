# Plan cải thiện FairyvsDinosaur (30/10/2026)

Trạng thái: **chờ duyệt, chưa sửa gì trong dự án.** Plan gồm 7 giai đoạn, mỗi giai đoạn một hoặc vài commit, làm hết trong ngày 30/10/2026.

## Hiện trạng

- **Code:** 26 file `.py` nằm hết ở thư mục gốc. File lớn nhất là `main.py` (990 dòng), `endgame.py` (818), `ghost.py` (808) và `pause_menu.py` (726).
- **Hàm quá dài:** `PacmanGame.run` 348 dòng, `Ghost.update` 219 dòng, `Ghost.__init__` 165 dòng.
- **Code trùng lặp:**
  - `endgame.py` và `pause_menu.py` trùng khoảng 68%.
  - 7 file thuật toán trùng nhau 47–78%.
  - `Blinky.draw` giống `Ghost.draw` 95%.
- **Asset:** game chỉ dùng 190/635 file.

## Lỗi đã tìm thấy

### Đã xác nhận bằng cách chạy thử

| # | Lỗi | Vị trí |
|---|---|---|
| 1 | AI bị kẹt tùy thời gian mỗi khung hình: cả 7 thuật toán kẹt nếu khung cố định 16ms hoặc 33ms. Nguyên nhân suy ra từ code, sẽ xác nhận khi sửa. | [pac.py:99](../../pac.py#L99) |
| 2 | DFS và Hill Climbing không ăn hết pellet dù đã tắt hết ma, chạy 25.000 khung (~7 phút). DFS còn 242/244, Hill Climbing còn 61/244. | `dfs.py`, `hill_climbing.py` |
| 3 | Số liệu History sai: `path_length` thực ra là số lần gọi thuật toán, còn BFS của ma ghi đè số liệu của fairy. Vì vậy so sánh thuật toán không đáng tin. | [main.py:966](../../main.py#L966), [ghost.py:278](../../ghost.py#L278) |
| 4 | History ghi level cao hơn thực tế 1 (qua level 1 nhưng ghi level 2). | [endgame.py:118](../../endgame.py#L118) |
| 5 | Chết khi ma đang về nhà thì âm thanh `turn_egg` lặp mãi; ma đang bị ăn cũng không được reset `eaten`. | [main.py:806](../../main.py#L806) |
| 6 | Pause rồi tiếp tục thì mất nhạc power mode. | [pause_menu.py:708](../../pause_menu.py#L708) |
| 7 | Sang màn mới không reset frightened và phase, tốc độ ma cũng không tăng theo level. | [main.py:874](../../main.py#L874), [ghost.py:24](../../ghost.py#L24) |
| 8 | Code gọi `ghost_eat.mp3` nhưng file tên `Ghost_eat.mp3`, nên sẽ lỗi trên Linux/macOS. | [sounds.py:15](../../sounds.py#L15) |
| 9 | Vẽ header và chữ READY một lần đã mở file JSON 4 lần, vì `get_translation` đọc đĩa mỗi lần gọi. | [dich.py:193](../../dich.py#L193) |
| 10 | Log debug in ra mỗi khung hình: 1.821 dòng qua các lần qua màn trong bài chạy thử. | [endgame.py:122](../../endgame.py#L122) |

### Mới thấy khi đọc code, sẽ kiểm lại lúc sửa

- Thời gian hiển thị sai dạng `01:75` ([endgame.py:812](../../endgame.py#L812)).
- Sprite fairy bị vẽ đè khi bật hint lúc qua màn ([main.py:540](../../main.py#L540)).
- Có thể văng `IndexError` ở đường hầm, dù rất hiếm ([pac.py:168](../../pac.py#L168)).
- Game tạo lại font mỗi khung hình ([main.py:437](../../main.py#L437)).
- Game chỉ chạy được khi đứng đúng thư mục dự án, vì đường dẫn là tương đối.
- Có 3 bản `load_settings` khác nhau, và bản trong `main.py` không gộp giá trị mặc định.
- Nhiều `except:` trần nuốt mất lỗi.

## Các giai đoạn

### GĐ0: Khởi tạo git

- Chạy `git init` trên nhánh `main`, thêm `.gitignore` (`__pycache__/`, `.idea/`, dữ liệu runtime).
- Commit toàn bộ hiện trạng **trước khi xóa**, nên file xóa nhầm vẫn lấy lại được.
- Commit: `chore: initialize repository with project baseline`

### GĐ1: Xóa file không dùng

Danh sách lấy từ log asset game thực sự load khi chạy, đối chiếu với lệnh load trong code.

| Xóa | Số file |
|---|---|
| `assets/Dino/` | 338 |
| `assets/Photos1/` | 16 |
| Ảnh lẻ trong `assets/Photos/` (tile phụ, nền không dùng) | 18 |
| Ảnh lẻ trong `assets/Pac-man/` và thư mục `green/` | 22 |
| Ảnh gốc `move`, `bite`... trong `assets/Ghost/` | 37 |
| Âm thanh thừa trong `assets/Sound/` | 7 |
| `assets/Fairy/`, `assets/Font/`, 2 nền thừa trong `assets/Mainmenu/` | 7 |
| Thư mục trống `assets/Game over/` | 0 |

Ngoài ra xóa `src tạm/` và `__pycache__/`, tổng cộng khoảng 7 MB asset cùng 2,4 MB trong `src tạm/`. Riêng `Ghost_eat.mp3` được đổi tên chứ không xóa, dù bản quét liệt nó vào nhóm không dùng.

- Commit: `chore(assets): remove unused sprites, sounds and fonts`, `chore: remove temporary source folder`

### GĐ2: Tổ chức lại thư mục

Giai đoạn này chỉ di chuyển file và đổi import, không đổi logic.

```
FairyvsDinosaur/
├── main.py                  # điểm chạy duy nhất (thay mainmenu.py)
├── requirements.txt, README.md, .gitignore
├── assets/                  # images/{fairy,dinosaurs,tiles,menu,score,level_complete}, sounds/
├── data/                    # settings và history (không commit, giữ dữ liệu hiện có)
├── tests/
└── fairy_vs_dinosaur/
    ├── config.py            # đường dẫn, hằng số
    ├── settings_store.py    # một nơi duy nhất đọc/ghi settings
    ├── i18n/                # bản dịch (dich.py hiện tại)
    ├── audio/               # SoundManager
    ├── core/                # game, game_states, level, board, modes, history
    ├── entities/            # player, ghost, blinky, pinky, inky, clyde
    ├── pathfinding/         # base, bfs, dfs, ucs, astar, greedy, beam, hill_climbing
    └── ui/                  # widgets, hud, overlay_menu, pause_menu, level_complete, screens/
```

- Commit: `refactor: move source into package structure`, `refactor(assets): rename asset folders and centralize paths`, `build: add requirements and README`

### GĐ3–5: Tách file lớn, bỏ trùng lặp

**Mục tiêu:** không file nào quá khoảng 400 dòng, không hàm nào quá khoảng 80 dòng.

- **GĐ3, thuật toán:** gom phần chung vào `BasePathFinder`, mỗi thuật toán chỉ giữ phần riêng.
  - Commit: `refactor(pathfinding): extract shared base class`
- **GĐ4, giao diện:** đưa code chung vào `OverlayMenu` và `widgets`, dùng chung `settings_store`.
  - Commit: `refactor(ui): share overlay menu and widgets`, `refactor(settings): use single settings store`
- **GĐ5, game và ma:**
  - Tách `run()` thành các hàm theo trạng thái (đếm ngược, chết, game over, qua màn, đang chơi).
  - Tách `Ghost` thành phần di chuyển, chọn hướng và vẽ. Gộp `Blinky.draw` vào lớp cha.
  - Commit: `refactor(core): split game loop into state handlers`, `refactor(entities): split ghost logic and rendering`

**Cách đảm bảo không đổi hành vi:** trước khi tách, ghi lại kết quả chạy với seed cố định (số khung, điểm, pellet) và ảnh chụp các màn hình. Sau mỗi giai đoạn so lại, lệch là sửa trước khi commit. Vì vậy phần sửa lỗi để sang GĐ6.

### GĐ6: Sửa lỗi

Mỗi nhóm lỗi một commit, kèm test nếu kiểm tra tự động được:

- `fix(ai): make pathing independent of frame time`
- `fix(ai): prevent DFS and hill climbing from getting stuck`
- `fix(history): record correct metrics and level`
- `fix(audio): stop leaked loops and restore power sound after pause`
- `fix(core): reset ghost and mode state on death and next level`
- `fix(entities): scale ghost speed with level`
- `perf(i18n): cache translations instead of reading disk`
- `fix: remove debug prints, bare excepts and dead code`

### GĐ7: Chốt lại

- Chạy lại toàn bộ test và `pyflakes` (hiện có 18 cảnh báo).
- Cập nhật README: cách chạy, cấu trúc, thuật toán.
- Commit: `test: add headless smoke tests`, `docs: update README`

## Những thay đổi sẽ thấy khi chơi

- **Ma nhanh hơn từ level 2**, đúng với cài đặt có sẵn trong code nhưng trước giờ chưa chạy. Game sẽ khó hơn.
- **Bỏ phím SPACE**, vì phím này dịch chuyển fairy về hàng 24 ([main.py:241](../../main.py#L241)), có vẻ là code debug còn sót.
- **Dòng cũ trong `history.json` không được sửa lại**, nên số liệu cũ vẫn sai; chỉ dòng mới là đúng.

## Giới hạn

- **Âm thanh và cảm giác chơi:** kiểm thử chạy không có cửa sổ nên không nghe hay chơi thử được. Cuối cùng cần tự chơi một ván.
- **Commit:** dùng config git toàn cục hiện có, tức `Thien211105 <huyalex009@gmail.com>`, không có dòng Co-Authored-By. Chỉ commit ở máy, không push.
- **Dung lượng repo:** các file bị xóa vẫn nằm trong commit đầu tiên, nên thư mục `.git` không nhỏ đi.
