# Làm Họa Phù Lục cùng AI và GitHub

Hướng dẫn cho nhóm hai người: một người phụ trách thiết kế game, một người phụ trách kỹ thuật. Bạn có thể nhờ AI thao tác Git; phần bạn cần quyết định là game phải thay đổi thế nào và chơi thử có đạt yêu cầu không.

Repo chung: **https://github.com/duongdk099/hoa_phu_luc**.

## 1. Quy trình dùng mỗi ngày

**Tạo yêu cầu → giao một người thực hiện → AI làm trên nhánh riêng → chơi thử → tạo PR → người còn lại xem → gộp vào main.**

Ví dụ: designer muốn giảm thời gian hồi chiêu của một bùa. Designer ghi rõ bùa nào, giá trị hiện tại và giá trị mong muốn; AI sửa trên nhánh riêng; designer chơi thử; người phụ trách kỹ thuật kiểm tra PR trước khi gộp.

| Từ GitHub | Hiểu đơn giản |
| --- | --- |
| Repository / repo | Thư mục dự án chung, có lịch sử thay đổi |
| Clone | Lấy repo về máy lần đầu |
| `main` | Bản chung của nhóm đã được kiểm tra |
| Branch / nhánh | Bản làm việc riêng cho một yêu cầu |
| Commit | Một mốc thay đổi có lời mô tả |
| Push | Đưa commit từ máy lên GitHub; chưa tự gộp vào `main` |
| Pull | Lấy thay đổi từ GitHub về nhánh hiện tại |
| Issue | Phiếu mô tả việc cần làm hoặc lỗi cần sửa |
| Pull request / PR | Đề nghị đưa thay đổi từ nhánh riêng vào bản chung |
| Merge | Gộp thay đổi |
| Conflict | Git cần người quyết định cách kết hợp hai thay đổi |

GitHub lưu code và lịch sử. **Push code, gộp PR và deploy game là ba việc khác nhau.** Repo hiện chưa có cấu hình tự deploy hoặc CI được thiết lập trong repo; đừng hiểu “đã push” là “đã có link chơi bản mới”.

## 2. Chuẩn bị lần đầu

1. Mỗi người dùng tài khoản GitHub riêng.
2. Chủ repo mời người còn lại qua **Settings → Collaborators → Add people**; người được mời chấp nhận lời mời. Repo public cho phép đọc code, nhưng muốn push vào repo chung cần quyền ghi. [Hướng dẫn GitHub](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository).
3. Mỗi người làm trong thư mục clone riêng trên máy mình. Không dùng thư mục đồng bộ OneDrive/Drive chung để hai máy cùng sửa một working copy Git.
4. Cho AI truy cập đúng thư mục và kết nối GitHub bằng tài khoản của bạn. Nếu công cụ AI chỉ đọc được GitHub, nó cần Git trên máy hoặc công cụ có quyền ghi để push/tạo PR.

Copy cho AI:

```text
Tôi là game designer, chưa rành code. Hãy chuẩn bị repo này để tôi làm việc:
https://github.com/duongdk099/hoa_phu_luc

Nếu chưa clone thì clone vào một thư mục riêng; nếu đã có thì dùng repo hiện có.
Kiểm tra thư mục, remote, nhánh hiện tại và thay đổi chưa commit trước khi làm.
Không xóa hoặc ghi đè thay đổi đang có.
Đọc README.md và docs/LAM_VIEC_CHUNG.md.
Kiểm tra Git, Python và quyền truy cập GitHub; báo rõ phần nào còn thiếu.
Chạy game bằng HTTP server và đưa địa chỉ local để tôi chơi thử.
Chưa thay đổi gameplay trong bước chuẩn bị này.
```

Không cần tự nhớ lệnh. Nếu muốn chạy thủ công, trong thư mục repo dùng `python -m http.server 8000`, rồi mở http://localhost:8000. Máy chưa có Python thì nhờ AI hướng dẫn cài trước.

## 3. Viết yêu cầu để AI sửa đúng game

Mỗi Issue nên đủ nhỏ để chơi thử và kết luận “đạt/chưa đạt”. Một thay đổi có thể cần nhiều file; không cần tách mỗi file thành một Issue.

Mẫu trên GitHub: vào **Issues → New issue → Yêu cầu thiết kế hoặc báo lỗi**. Hoặc copy nội dung sau vào chat AI:

```text
Tiêu đề: [Tên tính năng / lỗi]
Loại việc: gameplay / cân bằng / giao diện / hình ảnh / lỗi

Mục tiêu trải nghiệm:
[Người chơi đang gặp vấn đề gì? Muốn họ cảm thấy hoặc làm được gì?]

Hiện tại:
[Chế độ, đợt, bùa, quái hoặc màn hình liên quan; giá trị hiện tại nếu biết.]

Mong muốn:
[Hành vi và con số cụ thể. Nếu chưa chốt số, đề nghị AI đưa phương án trước.]

Phạm vi giữ nguyên:
[Ví dụ: không thay sát thương, boss, giá tiền hoặc cách lưu game.]

Cách xác nhận đạt:
1. [Thao tác người chơi thực hiện.]
2. [Kết quả quan sát được.]
3. [Trường hợp biên cần thử.]

Tham khảo:
[Ảnh/video nếu có; ghi rõ phần nào muốn học theo.]
```

Ví dụ yêu cầu tốt: “Trong chế độ Tự Do, làm cảnh báo trước đòn lao của quái charger dễ thấy hơn. Giữ nguyên thời điểm va chạm và sát thương. Đạt khi nhìn rõ hướng lao trên cả nền cỏ và đường đá, kể cả lúc có nhiều hiệu ứng.”

Nếu chỉ có cảm giác “game chưa đã”, hãy nhờ AI phân tích 2–3 phương án, nêu tác động tới nhịp chơi và cách kiểm chứng, rồi chọn phương án trước khi sửa. Không cần tự nghĩ ra tên hàm hay tên biến.

## 4. Bắt đầu một việc mới

Hai người ghi trong Issue ai đang làm và nhánh nào đang dùng. Một người/AI chính thực hiện một Issue; người còn lại có thể review hoặc làm Issue khác.

Copy cho AI, thay các phần trong ngoặc vuông:

```text
Repo: https://github.com/duongdk099/hoa_phu_luc
Yêu cầu: [link Issue hoặc nội dung yêu cầu]
Nhánh mới dự kiến: design/[tên-việc-ngắn]

Đọc README.md và docs/LAM_VIEC_CHUNG.md trước.
Kiểm tra git status, nhánh hiện tại và origin.
Nếu có thay đổi chưa commit, giữ nguyên và báo chúng thuộc việc nào trước khi chuyển nhánh.
Nếu thư mục sạch, fetch origin, chuyển main và cập nhật bằng fast-forward;
nếu main bị phân kỳ, không reset mà hãy báo cách xử lý.
Tạo nhánh mới từ origin/main; nếu nhánh cho Issue đã tồn tại, kiểm tra để tiếp tục đúng nhánh.
Đọc code liên quan rồi thực hiện đúng phạm vi yêu cầu.
Không chạy lại tools/optimize.py cho việc sửa gameplay thông thường.
Không ghi đè code bằng một file HTML cũ hoặc bản AI tạo lại toàn bộ.
Kiểm tra phần đã đổi và đưa cách chơi thử, nhánh, commit cho tôi.
Commit và push nhánh riêng, tạo PR vào main nếu có công cụ phù hợp.
Chưa gộp PR hoặc deploy trong yêu cầu này.
Nếu không thể push/tạo PR, nói rõ bước nào đã làm và bước nào chưa làm.
```

Tên nhánh gợi ý: `design/charger-warning`, `balance/early-waves`, `fix/settings-volume`. Không dùng cùng một nhánh cho hai việc không liên quan.

**Không làm hai việc song song trong cùng một thư mục clone.** Hai nhánh không tạo ra hai bộ file độc lập trong cùng working copy. Muốn hai AI chạy cùng lúc trên một máy, dùng hai clone hoặc Git worktree riêng; nhờ AI chuẩn bị.

## 5. Chia việc để ít đụng nhau

| Người | Chịu trách nhiệm chính |
| --- | --- |
| Game designer | Mục tiêu trải nghiệm, luật chơi, cân bằng, nội dung, tiêu chí chơi thử |
| Người phụ trách kỹ thuật | Cách triển khai, hiệu năng, tải tài nguyên, lưu game, xử lý conflict và phát hành |
| AI của mỗi người | Đọc code, đề xuất, sửa đúng phạm vi, kiểm tra, commit, push và trình bày thay đổi |

Code gameplay/UI hiện tập trung nhiều trong **`index.html`**, nên hai nhánh vẫn có thể đụng cùng đoạn code. Trước khi làm, báo rõ khu vực mình sẽ sửa trong Issue. Ví dụ: “Tôi sửa cảnh báo charger; chưa đụng thông số chiến đấu.”

Nếu hai việc đụng cùng hệ thống, nên hoàn thành và gộp việc thứ nhất trước, rồi cập nhật việc thứ hai từ `main`. Không thay cả file `index.html` chỉ để lấy một thay đổi nhỏ.

Khi ai đó nói “đã push”, hãy gửi **link PR hoặc nhánh + commit**, không chỉ gửi một file HTML qua chat. Nếu cần thử nghiệm ngoài repo, đưa kết quả trở lại nhánh và mô tả khác biệt trước khi gộp.

## 6. Những file AI cần hiểu trong repo này

| File/thư mục | Vai trò và cách xử lý |
| --- | --- |
| `index.html` | Bản game hiện chạy: gameplay, UI, dữ liệu và manifest ảnh. Sửa trực tiếp cho công việc gameplay hiện tại; giữ thay đổi nhỏ, có mục tiêu. |
| `runtime.js` | Tải tài nguyên theo nhu cầu, cache ảnh/animation/địa hình/bóng/ánh sáng. Khi sửa cần kiểm tra tải ảnh và hiệu năng. |
| `assets/` | Ảnh đã tối ưu, tên theo hash. Không đổi tên hoặc xóa riêng lẻ mà bỏ quên nơi tham chiếu. |
| `tools/optimize.py` | Nhận HTML gốc bên ngoài repo, tạo lại `index.html`, ảnh và báo cáo; còn có bước xóa ảnh sinh tự động không còn trong manifest mới. |
| `tools/runtime_build.py` | Chèn các thay đổi runtime vào HTML gốc khi chạy optimizer. Khi đổi quy trình sinh file, kiểm tra cả script này và bản game được sinh ra. |
| `optimization-report.json` | Báo cáo do optimizer sinh; không sửa số liệu thủ công để làm đẹp kết quả. |
| `docs/performance.json` | Kết quả benchmark đã lưu. Chỉ thay khi đo lại và ghi điều kiện đo. |
| `tools/smoke.py` | Kiểm tra lobby và bắt đầu trận trên Chromium. |
| `tools/check_runtime.py` | Kiểm tra animation, cache, camera/zoom, boss và raster địa hình. |
| `tools/benchmark.py` | Đo so sánh với commit đầu tiên, cần lịch sử Git chứa commit `48c45d0`. |

**Điểm dễ mất công nhất:** HTML gốc hiện nằm ngoài repo, còn `index.html` đã có thể được sửa tiếp. Chạy optimizer từ HTML cũ có thể ghi đè gameplay mới và xóa ảnh vừa thêm. Đây chưa phải bước build thông thường cho mọi lần sửa game. Nếu cần chạy lại, AI phải đối chiếu các thay đổi từ sau bản gốc và chuẩn bị cách giữ chúng trước; nên giao riêng việc thay đổi pipeline cho người phụ trách kỹ thuật.

## 7. Chơi thử và gửi phản hồi

Nhờ AI checkout đúng nhánh PR trong thư mục sạch hoặc mở worktree riêng, chạy server và đưa link local. Kiểm tra lại tên nhánh/commit để biết mình đang thử đúng bản. Repo hiện không tự tạo preview cho từng PR; một link website cũ có thể vẫn đang chạy bản khác.

Designer thử theo tiêu chí của Issue, ghi lại:

```text
Đang thử: [link PR, nhánh hoặc commit]
Thiết bị/trình duyệt: [...]
Chế độ và đợt: [...]
Các bước đã làm: [...]
Mong đợi: [...]
Thực tế: [...]
Lặp lại: [luôn xảy ra / thỉnh thoảng / mới gặp một lần]
Kết luận: đạt / cần sửa
Ảnh hoặc video: [đính kèm nếu có]
```

Sửa chưa đạt thì tiếp tục **trên nhánh PR đó**. Ghi yêu cầu mới vào Issue/PR để người còn lại đọc được; AI ở phiên chat khác không tự biết những gì hai người đã bàn riêng.

Game dùng localStorage theo địa chỉ website và trình duyệt. Nên dùng cùng địa chỉ/port khi cần thử cùng dữ liệu lưu; dùng profile trình duyệt riêng cho lượt thử sạch. Trước khi xóa dữ liệu trình duyệt, xuất bản lưu trong game nếu cần giữ tiến trình.

## 8. Review và gộp vào bản chung

AI nên viết PR bằng ngôn ngữ người chưa đọc code cũng hiểu: trước đây xảy ra gì, sau thay đổi xảy ra gì, cách thử và phần chưa kiểm tra. Mẫu PR đã có sẵn trong repo.

Trước khi gộp:

- Designer xác nhận đạt tiêu chí trải nghiệm.
- Người còn lại xem phạm vi thay đổi và kiểm tra kỹ thuật phù hợp.
- Nhánh đã được cập nhật với `main` nếu có thay đổi mới ảnh hưởng tới việc này; xử lý conflict và kiểm tra lại nếu cần.
- PR ghi rõ đã chạy kiểm tra nào, kết quả gì; không coi “AI nói xong” là bằng chứng game chạy đúng.

Đây là **quy ước làm việc đề xuất**, chưa phải cơ chế GitHub bắt buộc. Tài liệu và template không tự chặn push thẳng vào `main`; muốn bắt buộc review thì chủ repo cần cấu hình ruleset/branch protection riêng.

Khi hai người đã xem và muốn đưa vào bản chung, copy:

```text
PR [link] đã được designer và người phụ trách kỹ thuật xác nhận.
Hãy kiểm tra trạng thái PR, cập nhật với main nếu cần và xử lý phần kiểm tra còn thiếu.
Nếu có xung đột về luật chơi, nêu rõ hai ý định để chúng tôi quyết định.
Nếu đạt các tiêu chí đã thống nhất, gộp PR bằng squash merge và xác nhận commit trên main.
Sau đó cập nhật clone local khi thư mục sạch.
Chưa deploy trong yêu cầu này.
```

Chọn squash merge giúp mỗi PR thành một commit trên `main`, dễ xem lại và hoàn tác theo tính năng. Mỗi việc nhỏ có một PR sẽ dễ xử lý hơn PR gộp cân bằng, UI và tối ưu cùng lúc. [Tài liệu PR của GitHub](https://docs.github.com/en/pull-requests).

## 9. Khi gặp trục trặc

| Tình huống | Nói với AI |
| --- | --- |
| “Push rejected”, nhánh phía GitHub mới hơn | “Fetch và xem khác biệt với nhánh remote. Giữ cả thay đổi của người kia; giải quyết đồng bộ trên nhánh riêng, không force push.” |
| Conflict khi cập nhật hoặc gộp | “Cho biết hai bên đang thay gì và ở đâu. Kết hợp theo mục tiêu của hai Issue, không chọn toàn bộ ours/theirs để làm hết dấu conflict. Kiểm tra lại phần đã kết hợp.” |
| Có file đang sửa dở khi đổi việc | “Giữ nguyên công việc này, xác định nó thuộc nhánh nào. Dùng commit WIP hoặc worktree riêng phù hợp; không reset, clean hoặc bỏ file của tôi.” |
| AI không có quyền GitHub | “Giữ thay đổi local và báo commit/nhánh. Hướng dẫn đăng nhập hoặc quyền còn thiếu; không nói đã push khi chưa có.” |
| Bản trên máy khác bản của đồng đội | “Đối chiếu remote, nhánh và commit trước; xác định PR đã merge chưa. Không chép đè cả thư mục để đồng bộ.” |
| Game lỗi sau khi merge | “Xác định commit/PR gây lỗi, tạo nhánh sửa hoặc revert bằng commit mới. Giữ lịch sử main, rồi tạo PR và kiểm tra lại.” |

Nếu Issue A đổi cooldown thành 4 giây còn Issue B muốn 6 giây, đó là quyết định thiết kế; AI cần hỏi hai người chốt. Nếu chỉ là khác dòng hoặc khác vị trí code, AI có thể kết hợp và kiểm tra mà không cần bạn hiểu từng dòng. [Tài liệu về conflict](https://docs.github.com/en/pull-requests).

## 10. Kết thúc mỗi phiên làm việc

Nhờ AI trả lại một ghi chú ngắn để phiên sau hoặc người còn lại tiếp tục được:

```text
Issue / mục tiêu:
Nhánh:
Commit mới nhất:
Link PR:
Đã thay đổi:
Đã kiểm tra và kết quả:
Cách chạy/chơi thử:
Việc còn lại hoặc điều cần chốt:
Trạng thái: local / đã push / đã merge / đã deploy (ghi đúng từng bước).
```

Lưu ghi chú vào Issue/PR tương ứng khi bạn yêu cầu AI đăng lên GitHub; nếu AI chưa có công cụ ghi, copy nội dung vào đó. Người nhận chỉ cần link này để tìm lại bối cảnh, code và cách kiểm chứng.
