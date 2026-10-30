# Họa Phù Lục

Game roguelike vẽ bùa, chạy bằng JavaScript và Canvas trong trình duyệt.

## Chạy thử

Tại thư mục repo:

```sh
python -m http.server 8000
```

Mở http://localhost:8000. Dùng HTTP server để kiểm tra đúng cách tải tài nguyên khi deploy.

## Deploy

Đưa `index.html` và toàn bộ thư mục `assets/` lên static hosting. Không cần build hay backend. Với itch.io, ZIP phải có `index.html` ngay ở gốc.

Game vẫn tải Tailwind và Google Fonts qua HTTPS. Cài đặt và bản đồ dùng localStorage theo trình duyệt và địa chỉ website; không tự đồng bộ giữa các tên miền.

## Tối ưu đã áp dụng

- Tách ảnh PNG nhúng base64 thành tài nguyên riêng để trình duyệt có thể cache độc lập.
- Dùng cùng một file cho các ảnh có nội dung giống hệt nhau.
- Chuyển sang WebP lossless khi nhỏ hơn PNG; giữ nguyên kích thước và kiểm tra RGBA từng pixel, bao gồm alpha.
- Giữ nguyên âm thanh base64 vì Web Audio hiện giải mã trực tiếp định dạng này.
- Giữ nguyên luật chơi, thông số chiến đấu và vòng lặp game.

Số liệu nằm trong `optimization-report.json`. Bản HTML gốc được giữ ngoài repo ở thư mục làm việc ban đầu.

| Thành phần | Trước | Sau |
| --- | ---: | ---: |
| HTML | 72,89 MB | 2,04 MB |
| Ảnh tách riêng | — | 27,35 MB |
| Tổng HTML và ảnh | 72,89 MB | 29,39 MB |

Giảm khoảng **59,7%** dung lượng file chưa tính nén HTTP. Đây không phải số đo lưu lượng tải thực tế hoặc FPS.

Các đường dẫn ảnh cũ trong HTML/CSS cũng được cập nhật để không phát sinh yêu cầu tới file thiếu trước khi JavaScript gán tài nguyên.

## Tái tạo từ bản HTML gốc

```sh
python -m pip install -r requirements.txt
python tools/optimize.py "path/to/original.html"
```

Kiểm tra khởi động và bắt đầu trận trên Chromium:

```sh
python -m pip install playwright
python -m playwright install chromium
python tools/smoke.py
```

## Hướng tối ưu tiếp

1. **Tải theo nhu cầu:** ưu tiên ảnh lobby, trì hoãn ảnh quái/boss và nội dung chưa dùng. Thêm cơ chế đợi ảnh decode trước khi tạo cache sprite/địa hình để tránh cache khung trống.
2. **Giảm dung lượng thêm:** đo kích thước hiển thị của avatar/logo; cân nhắc thu nhỏ và WebP lossy sau khi so sánh trực quan. Không resize sprite sheet khi chưa kiểm tra tọa độ frame.
3. **Ổn định FPS:** profile trận đông quái trước; kiểm tra chi phí shadowBlur, ánh sáng động, minimap và các vòng lặp va chạm. Đã có cache địa hình và sprite, nên không thay hàng loạt khi chưa đo.
4. **Giảm RAM:** đo kích thước ảnh sau decode và canvas cache; WebP giảm tải mạng nhưng không tự giảm bộ nhớ pixel. Giới hạn cache theo vùng nhìn nếu số liệu cho thấy cần thiết.
5. **Độc lập CDN:** build CSS Tailwind cục bộ, lưu font cần dùng và thêm cache policy phù hợp trên hosting.

Chưa có số liệu FPS trước/sau để khẳng định tăng tốc render.
