# Đố Vui – game đố vui trắc nghiệm A/B/C/D cho Android TV

TV hiển thị câu hỏi (kèm hình), mọi người quét mã QR rồi chọn A/B/C/D bằng điện thoại. Đúng và nhanh thì nhiều điểm; cuối ván có bảng tổng điểm và người vô địch.

> **Hai repo riêng:** repo này chứa mã nguồn app + công cụ sinh câu hỏi. Nội dung câu hỏi/ảnh (`quiz-content/`) nằm ở repo
> https://github.com/KimAnhDuc/partygame và bị bỏ qua bởi `.gitignore` của repo này. Sau khi `git clone` repo app, muốn chạy
> script/xem thử hãy clone repo câu hỏi vào đúng thư mục `quiz-content/`:
> `git clone https://github.com/KimAnhDuc/partygame.git quiz-content`
> Muốn build APK cần Android SDK và tạo file `local.properties` chứa `sdk.dir=...` (file này không được đưa lên git).

## Câu hỏi nằm trên mạng, không nằm trong app

```
quiz-content/          <- thư mục này được đưa lên GitHub Pages
  manifest.json        <- rất nhẹ, TV kiểm tra mỗi lần mở app: {"version": "...", ...}
  questions.json       <- toàn bộ câu hỏi, chỉ tải lại khi "version" đổi
  img/                 <- ảnh câu hỏi (JPEG ≤ 800px), TV tải trực tiếp từ đây
  credits.json         <- tác giả + giấy phép từng ảnh
```

* Mở app: TV tải `manifest.json`; nếu có phiên bản mới thì tải `questions.json`, lưu vào bộ nhớ TV.
* Mất mạng / host lỗi: dùng bản đã lưu; chưa từng tải thì dùng bộ ~100 câu nhỏ đi kèm app (`app/src/main/assets/questions.json`).
* App đang mở lâu: cứ 30 phút tự kiểm tra lại. Ván đang chơi không bị ảnh hưởng.
* **Cập nhật câu hỏi = đẩy file mới lên host, không cần cài lại app.**

## Lần đầu: đưa nội dung lên GitHub Pages (miễn phí)

1. Tạo repo mới trên GitHub, ví dụ `dovui-content` (Public).
2. Trong thư mục `quiz-content/`:
   ```
   git init
   git add .
   git commit -m "Quiz content"
   git branch -M main
   git remote add origin https://github.com/<tên-github>/dovui-content.git
   git push -u origin main
   ```
3. Trên GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch → `main` / `(root)` → Save.**
4. Đợi 1–2 phút, kiểm tra `https://<tên-github>.github.io/dovui-content/manifest.json` mở ra được.
5. Điền địa chỉ đó (có dấu `/` ở cuối) vào `app/src/main/res/values/strings.xml`:
   ```xml
   <string name="content_base_url" translatable="false">https://<tên-github>.github.io/dovui-content/</string>
   ```
6. Build lại APK (`gradlew assembleRelease`) và cài lên TV **một lần duy nhất**. Từ đó trở đi chỉ cần cập nhật nội dung.

## Cập nhật / thêm câu hỏi sau này

Cách 1 – sinh tự động từ dữ liệu mở (Wikidata, Wikipedia, Commons):
```
python tools/build_questions.py          # tạo lại quiz-content/ (có cache, chạy lại rất nhanh)
cd quiz-content && git add -A && git commit -m "Update" && git push
```
* Thêm câu hỏi chữ: sửa `tools/extra_text.py` (mỗi dòng: `Lĩnh vực | Câu hỏi | Đáp án ĐÚNG | Sai 1 | Sai 2 | Sai 3`).
* Thêm câu hỏi có ảnh theo tên (con vật, món ăn, địa danh…): sửa danh sách trong `tools/curated.py`.
* Chỉnh số câu mỗi nhóm: biến `CAPS` trong `tools/build_questions.py`.

Cách 2 – sửa trực tiếp `quiz-content/questions.json` rồi đổi `version` trong cả hai file `questions.json` và `manifest.json` (đổi version thì TV mới tải lại).

Một câu hỏi: `{"category":"Địa lý","q":"Câu hỏi?","options":["Đáp án ĐÚNG","Sai 1","Sai 2","Sai 3"],"image":"img/ten.jpg"}`.
Đáp án đúng để vị trí đầu; app tự xáo A/B/C/D. `image` là đường dẫn trong `img/` hoặc link `https://…`.

## Xem thử trên máy tính (không cần TV)

```
python tools/preview_server.py            # TV: http://localhost:8080/tv   Điện thoại: http://localhost:8080/
python tools/preview_server.py --fast     # thời gian ngắn để xem nhanh
python tools/preview_server.py --bots 0   # không có bot
python tools/preview_server.py --bundled  # chỉ bộ câu nhỏ đi kèm app
```
Server xem thử dùng `quiz-content/` nếu đã build. Sửa `tv.html`/`phone.html` rồi bấm F5 là thấy ngay.

## Bản quyền ảnh

Ảnh lấy từ Wikimedia Commons (giấy phép CC / public domain) và cờ từ flagcdn.com. Tác giả + giấy phép từng ảnh nằm trong `quiz-content/credits.json`; nếu công khai app rộng rãi, hãy ghi nguồn "Wikimedia Commons, Wikidata" trong mô tả app. Dữ liệu Wikidata là CC0.
