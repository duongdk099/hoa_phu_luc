# Họa Phù Lục

Game roguelike vẽ bùa, chạy bằng JavaScript và Canvas trong trình duyệt.

## Làm việc chung

Đọc [hướng dẫn cho game designer và AI](docs/LAM_VIEC_CHUNG.md): bắt đầu với GitHub, viết yêu cầu, dùng nhánh/PR, chơi thử, phối hợp hai người và xử lý conflict. Có prompt copy sẵn, mẫu Issue và mẫu PR.

## Chạy thử

Tại thư mục repo:

```sh
python -m http.server 8000
```

Mở http://localhost:8000. Dùng HTTP server để kiểm tra đúng cách tải tài nguyên khi deploy.

## Deploy

Đưa `index.html`, `runtime.js` và toàn bộ thư mục `assets/` lên static hosting. Không cần build hay backend. Với itch.io, ZIP phải có `index.html` ngay ở gốc.

Game vẫn tải Tailwind và Google Fonts qua HTTPS. Cài đặt và bản đồ dùng localStorage theo trình duyệt và địa chỉ website; không tự đồng bộ giữa các tên miền.

## Tối ưu đã áp dụng

- Tách ảnh PNG nhúng base64 thành tài nguyên riêng để trình duyệt có thể cache độc lập.
- Dùng cùng một file cho các ảnh có nội dung giống hệt nhau.
- Chuyển sang WebP lossless khi nhỏ hơn PNG; kiểm tra RGBA từng pixel sau mã hóa, bao gồm alpha.
- Avatar/logo 2048×2048 giảm xuống 512×512, chân dung 2202×1229 giảm xuống 1024×572. Các frame animation và sprite sheet giữ nguyên kích thước. Ảnh thu nhỏ được đối chiếu với kết quả resample, không phải pixel của bản gốc.
- Chỉ tải nhóm animation đang dùng (hành động + hướng), tối đa 3 nhóm đang chờ và 6 ảnh decode đồng thời. Chỉ công bố nhóm khi mọi frame decode xong; SVG sẵn có hiển thị trong lúc chờ.
- Tải ảnh môi trường khi render cần tới; tạo sprite quái/boss bằng code khi lần đầu sử dụng. Ảnh dialogue ẩn dùng lazy loading; không render thế giới sau lớp lobby.
- Cache lớp ánh sáng để tái sử dụng giữa sprite/frame. Vị trí tương đối của ánh sáng được làm tròn theo bước 16 world units, cường độ theo bước 1/32. Đây là đánh đổi nhỏ về độ chính xác hiệu ứng ánh sáng, không thay đổi tọa độ hoặc sát thương.
- Địa hình dùng ô 550×550 thay cho 4 canvas 2200×2200. Khi zoom rộng cần hơn 20 ô, độ phân giải cache địa hình giảm một nửa; tọa độ thế giới giữ nguyên.
- Cache ảnh, animation, địa hình, bóng, ánh sáng và pattern dùng LRU theo ngân sách; bóng có cạnh dài tối đa 512 px.
- Giữ nguyên âm thanh base64 vì Web Audio hiện giải mã trực tiếp định dạng này.
- Giữ nguyên luật chơi, thông số chiến đấu và vòng lặp game.

Số liệu nằm trong `optimization-report.json`. Bản HTML gốc được giữ ngoài repo ở thư mục làm việc ban đầu.

| Thành phần | Trước | Sau |
| --- | ---: | ---: |
| HTML | 72,89 MB | 2,03 MB |
| Ảnh tách riêng | — | 21,60 MB |
| Runtime JS | — | 0,009 MB |
| Tổng file phục vụ game | 72,89 MB | 23,64 MB |

Giảm khoảng **67,6%** dung lượng file chưa tính nén HTTP. So với bản tối ưu đầu tiên 29,39 MB, giảm thêm khoảng **19,6%**. Đây không phải số đo lưu lượng tải thực tế hoặc FPS.

Các đường dẫn ảnh cũ trong HTML/CSS cũng được cập nhật để không phát sinh yêu cầu tới file thiếu trước khi JavaScript gán tài nguyên.

## Tái tạo từ bản HTML gốc

```sh
python -m pip install -r requirements.txt
python tools/optimize.py "path/to/original.html"
```

Kiểm tra khởi động và bắt đầu trận trên Chromium:

```sh
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tools/smoke.py
python tools/check_runtime.py
python tools/benchmark.py
```

## Ngân sách cache

| Cache | Trần dữ liệu pixel |
| --- | ---: |
| Ảnh được runtime quản lý | 24 MiB |
| Animation | 20 MiB, tối đa 6 nhóm |
| Địa hình | 24 MiB |
| Bóng | 12 MiB |
| Lớp ánh sáng | 16 MiB |
| Pattern | 8 MiB |

Đây là ước lượng pixel cho tài nguyên cache, không phải giới hạn RAM toàn bộ tab. DOM, browser cache, tài nguyên đang decode, canvas scratch, JavaScript và GPU dùng bộ nhớ riêng. Xem trạng thái bằng `GFX.cacheStats()` trong console.

## Đo hiệu năng

`tools/benchmark.py` so sánh với commit `48c45d0`, cùng viewport 1366×768, seed và cảnh 240 quái; đợi ảnh decode rồi đo 30 lần draw/update. Kết quả chi tiết trong `docs/performance.json`. Đây là thời gian thực thi hàm JavaScript trong Chromium headless, không bao gồm đầy đủ thời gian raster/compositor và không suy ra FPS trên máy người chơi.

Kết quả trên môi trường phát triển ngày 30/10/2026:

| Chỉ số | Bản đầu | Bản hiện tại |
| --- | ---: | ---: |
| Draw trung bình | 154,64 ms | 56,94 ms |
| Draw p95 | 161,20 ms | 93,90 ms |
| Update trung bình | 5,47 ms | 5,61 ms |
| Request ảnh lúc ở lobby | 248 | 7 |
| Dữ liệu ảnh lobby | 17,28 MB | 2,57 MB |
| Pixel cache địa hình trong cảnh đo | 77,44 MB | 14,52 MB |

Thời gian gọi hàm vẽ giảm khoảng 63%; update gần như không đổi. Dữ liệu ảnh được tính qua Resource Timing trên HTTP server cục bộ không nén. Kết quả tùy máy và trạng thái cache; tài nguyên tải sau khi vào trận không được tính vào số liệu lobby.

Kiểm tra runtime bao gồm 20 nhóm animation, 9 tổ hợp camera/zoom, 5 loại boss, ngân sách cache và so sánh raster địa hình giữa ô lớn/ô nhỏ. Các bài này chưa thay thế kiểm thử trọn vẹn 25 đợt hoặc mọi kỹ năng.

Việc build CSS Tailwind và lưu font cục bộ chưa thực hiện; game vẫn cần các CDN nêu trên.
