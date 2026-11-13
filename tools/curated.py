"""
Hand-picked name lists. Each name is looked up on vi.wikipedia.org, and the article's lead image is used
as the question picture. The name shown to players is exactly the string written here, so you control wording.

Format: "Tên hiển thị" or "Tên hiển thị|Tiêu đề bài Wikipedia" when the article title differs.
Add / remove names freely, then re-run build_questions.py.
"""

# group -> (category shown in the app, question wording variants, names)
CURATED = {
    "animals": ("Động vật", ["Đây là con vật nào?", "Con vật trong hình là gì?"], """
Voi|Voi (động vật) ; Hổ ; Sư tử ; Hươu cao cổ ; Gấu trúc|Gấu trúc lớn ; Ngựa vằn ; Tê giác ; Hà mã ; Báo đốm|Báo đốm Mỹ ; Báo săn|Báo săn (Cheetah)
Cá voi xanh ; Cá heo ; Cá mập trắng|Cá mập trắng lớn ; Rùa biển ; Cá ngựa ; Bạch tuộc ; Sao biển ; Cua ; Tôm hùm ; Sứa
Chim cánh cụt ; Đại bàng ; Cú mèo|Cú ; Vẹt ; Công|Công (chim) ; Hồng hạc ; Thiên nga ; Đà điểu ; Chim ruồi ; Kền kền
Khỉ đột|Khỉ đột phương Tây ; Tinh tinh ; Đười ươi|Đười ươi Borneo ; Khỉ đầu chó ; Lười|Lười ba ngón ; Gấu Bắc Cực|Gấu Bắc Cực ; Gấu nâu ; Sói xám|Sói xám ; Cáo đỏ|Cáo đỏ ; Linh cẩu
Kangaroo ; Koala ; Thú mỏ vịt ; Thú ăn kiến|Thú ăn kiến ; Tê tê ; Nhím ; Con dơi|Dơi ; Sóc ; Thỏ|Thỏ nhà ; Chuột túi
Cá sấu|Cá sấu nước mặn ; Rắn hổ mang|Rắn hổ mang chúa ; Tắc kè ; Kỳ nhông|Tắc kè hoa ; Rùa|Rùa ; Ếch|Ếch ; Kỳ giông|Kỳ giông ; Thằn lằn ; Rồng Komodo
Bướm|Bướm ; Ong mật|Ong mật ; Kiến|Kiến ; Châu chấu ; Bọ rùa|Bọ rùa ; Chuồn chuồn ; Nhện|Nhện ; Bọ cạp|Bọ cạp ; Ong bắp cày ; Gián
Chó|Chó nhà ; Mèo|Mèo nhà ; Ngựa|Ngựa ; Bò|Bò nhà ; Cừu|Cừu ; Dê|Dê nhà ; Lợn|Lợn nhà ; Gà|Gà nhà ; Vịt|Vịt nhà ; Lạc đà
Trâu|Trâu nước ; Voi ma mút|Voi ma mút ; Hươu|Hươu ; Nai sừng tấm ; Bò rừng bizon|Bò rừng bizon ; Lừa|Lừa ; Chó sói ; Báo hoa mai ; Sư tử biển ; Hải cẩu
Hải mã|Hải mã ; Rái cá|Rái cá ; Cú muỗi|Cú muỗi ; Chim gõ kiến|Chim gõ kiến ; Chim bồ câu|Bồ câu ; Quạ|Quạ ; Chim hải âu|Hải âu ; Pelican|Bồ nông ; Gà tây|Gà tây ; Chim cú mèo
"""),
    "food": ("Ẩm thực & Thực vật", ["Đây là món gì / loại quả nào?", "Hình này là gì?"], """
Táo|Táo tây ; Chuối|Chuối ; Cam|Cam ; Dứa|Dứa ; Xoài|Xoài ; Dưa hấu ; Nho|Nho ; Dâu tây ; Sầu riêng ; Măng cụt
Chôm chôm ; Vải|Vải thiều ; Thanh long ; Mít|Mít ; Ổi|Ổi ; Dừa|Dừa ; Đu đủ ; Chanh ; Lê|Lê ; Cà chua
Cà rốt ; Khoai tây ; Bắp cải ; Ớt|Ớt ; Hành tây ; Tỏi ; Bí ngô ; Dưa chuột ; Bông cải xanh|Bông cải xanh ; Ngô|Ngô (thực vật)
Hoa hướng dương|Hướng dương ; Hoa hồng ; Hoa sen ; Hoa tulip|Tulip ; Cây xương rồng|Xương rồng ; Cây tre|Tre ; Nấm|Nấm ; Cà phê|Cà phê ; Trà|Trà ; Sô cô la|Sô cô la
Sushi ; Pizza ; Hamburger ; Mì Ý|Mì ống ; Bánh croissant|Bánh sừng bò ; Kim chi ; Taco ; Bánh quy|Bánh quy ; Kem|Kem ; Bánh pancake|Pancake
"""),
    "vn_food": ("Việt Nam", ["Đây là món ăn Việt Nam nào?", "Món ăn trong hình tên là gì?"], """
Phở ; Bánh mì|Bánh mì ; Bún chả ; Bánh chưng ; Gỏi cuốn ; Chả giò|Nem rán ; Bún bò Huế ; Cao lầu ; Mì Quảng ; Cơm tấm
Bánh xèo ; Bánh cuốn ; Bún riêu ; Hủ tiếu ; Chè|Chè (món ăn) ; Cà phê sữa đá|Cà phê sữa đá ; Bánh tét ; Nước mắm ; Bún đậu mắm tôm ; Cháo lòng
Bánh bao ; Xôi ; Bánh canh ; Nem chua ; Bánh đa cua ; Bún thang ; Bánh khọt ; Chả cá Lã Vọng ; Cơm lam ; Bánh pía
"""),
    "vn_places": ("Việt Nam", ["Đây là địa danh nào của Việt Nam?", "Nơi trong hình là đâu?"], """
Vịnh Hạ Long ; Hồ Hoàn Kiếm ; Chùa Một Cột ; Dinh Độc Lập ; Phố cổ Hội An|Hội An ; Đại Nội Huế|Đại Nội (Huế) ; Văn Miếu – Quốc Tử Giám|Văn Miếu - Quốc Tử Giám ; Nhà thờ Đức Bà Sài Gòn|Nhà thờ Đức Bà Sài Gòn ; Fansipan ; Phong Nha – Kẻ Bàng|Vườn quốc gia Phong Nha - Kẻ Bàng
Cầu Rồng|Cầu Rồng (Đà Nẵng) ; Cầu Vàng|Cầu Vàng ; Thành nhà Hồ|Thành nhà Hồ ; Mỹ Sơn|Thánh địa Mỹ Sơn ; Sa Pa ; Đà Lạt ; Nha Trang ; Phú Quốc ; Địa đạo Củ Chi ; Lăng Chủ tịch Hồ Chí Minh
Chợ Bến Thành ; Hồ Gươm|Hồ Hoàn Kiếm ; Tràng An|Quần thể danh thắng Tràng An ; Ruộng bậc thang Mù Cang Chải|Mù Cang Chải ; Đèo Hải Vân|Đèo Hải Vân ; Chùa Thiên Mụ ; Bà Nà Hills|Bà Nà ; Landmark 81 ; Cột cờ Lũng Cú|Cột cờ Lũng Cú
"""),
    "vn_people": ("Việt Nam", ["Đây là nhân vật lịch sử nào?", "Người trong hình là ai?"], """
Hồ Chí Minh ; Trần Hưng Đạo ; Nguyễn Huệ|Quang Trung ; Lê Lợi ; Võ Nguyên Giáp ; Nguyễn Trãi ; Lý Thái Tổ ; Ngô Quyền ; Hai Bà Trưng ; Bà Triệu
Nguyễn Du ; Hồ Xuân Hương ; Phan Bội Châu ; Phan Châu Trinh ; Nguyễn Ái Quốc|Hồ Chí Minh ; Trương Định ; Nguyễn Trường Tộ ; Gia Long ; Minh Mạng ; Bảo Đại
Trịnh Công Sơn ; Văn Cao ; Nguyễn Nhật Ánh ; Phạm Tuyên ; Lương Thế Vinh|Lương Thế Vinh ; Trần Nhân Tông ; Lý Thường Kiệt ; Dương Văn Minh|Dương Văn Minh ; Ngô Bảo Châu ; Phạm Nhật Vượng
"""),
    "instruments": ("Âm nhạc", ["Đây là nhạc cụ nào?", "Nhạc cụ trong hình có tên là gì?"], """
Đàn piano|Piano ; Đàn guitar|Guitar ; Vĩ cầm|Violin ; Đàn cello|Cello ; Sáo|Sáo ; Kèn trumpet|Trumpet ; Kèn saxophone|Saxophone ; Trống|Trống ; Đàn hạc|Đàn hạc ; Đàn accordion|Accordion
Đàn bầu ; Đàn tranh ; Đàn nguyệt|Đàn nguyệt ; Đàn nhị ; Sáo trúc|Sáo trúc ; Kèn clarinet|Clarinet ; Đàn organ|Organ ; Kèn harmonica|Harmonica ; Đàn ukulele|Ukulele ; Trống jazz|Bộ trống
Đàn bass|Guitar bass ; Kèn trombone|Trombone ; Đàn mandolin|Mandolin ; Kèn oboe|Oboe ; Tù và ; Trống cơm ; Cồng chiêng ; Đàn t'rưng|Đàn T'rưng ; Đàn đáy ; Đàn tỳ bà|Tỳ bà
"""),
    "vehicles": ("Phương tiện", ["Đây là phương tiện nào?", "Hình này là loại phương tiện gì?"], """
Xe đạp ; Xe máy|Xe máy ; Ô tô|Ô tô ; Xe buýt|Xe buýt ; Tàu hỏa ; Máy bay|Máy bay ; Trực thăng|Trực thăng ; Tàu thủy|Tàu thủy ; Tàu ngầm ; Khinh khí cầu
Xe tăng ; Tên lửa|Tên lửa ; Tàu vũ trụ|Tàu vũ trụ ; Xe tải|Xe tải ; Xe cứu hỏa|Xe cứu hỏa ; Xe lửa cao tốc|Tàu cao tốc ; Cano|Cano ; Thuyền buồm|Thuyền buồm ; Xe xích lô|Xích lô ; Tàu điện ngầm
Xe ba gác|Xe ba gác ; Xe điện|Xe điện ; Xe trượt tuyết|Xe trượt tuyết ; Xe lăn|Xe lăn ; Ván trượt|Ván trượt ; Xe địa hình|Xe địa hình ; Thuyền kayak|Kayak ; Tàu phá băng ; Cáp treo|Cáp treo ; Xe lu|Xe lu
"""),
}


def parse(text):
    out = []
    for chunk in text.replace("\n", ";").split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        label, _, title = chunk.partition("|")
        out.append((label.strip(), (title or label).strip()))
    return out
