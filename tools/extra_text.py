"""
Hand-written text questions (no pictures) that fill the fields Wikidata can't generate well.
One per line:  Lĩnh vực | Câu hỏi | Đáp án ĐÚNG | Sai 1 | Sai 2 | Sai 3
build_questions.py merges these into the online question set. Add your own lines freely.
"""

EXTRA = """
Lịch sử Việt Nam | Ai là vị vua đầu tiên của triều Nguyễn? | Gia Long | Minh Mạng | Thiệu Trị | Tự Đức
Lịch sử Việt Nam | Khởi nghĩa Lam Sơn do ai lãnh đạo? | Lê Lợi | Nguyễn Huệ | Trần Hưng Đạo | Lý Bí
Lịch sử Việt Nam | Trận Bạch Đằng năm 1288 đánh bại quân xâm lược nào? | Nguyên – Mông | Tống | Minh | Thanh
Lịch sử Việt Nam | Nhà Lý dời đô từ Hoa Lư về Thăng Long vào năm nào? | 1010 | 938 | 1070 | 1225
Lịch sử Việt Nam | Ai là người lãnh đạo cuộc khởi nghĩa Tây Sơn? | Nguyễn Huệ | Lê Lợi | Phan Đình Phùng | Hoàng Hoa Thám
Lịch sử Việt Nam | Ngày Quốc khánh nước Cộng hòa Xã hội Chủ nghĩa Việt Nam là ngày nào? | 2/9 | 30/4 | 19/8 | 7/5
Lịch sử Việt Nam | Chiến dịch Hồ Chí Minh giải phóng miền Nam kết thúc vào ngày nào? | 30/4/1975 | 2/9/1945 | 7/5/1954 | 19/5/1975
Lịch sử Việt Nam | Quốc hiệu "Đại Cồ Việt" được đặt dưới triều vua nào? | Đinh Tiên Hoàng | Lý Thái Tổ | Lê Đại Hành | Ngô Quyền
Lịch sử Việt Nam | Hiệp định Giơ-ne-vơ về Đông Dương được ký năm nào? | 1954 | 1945 | 1973 | 1960
Lịch sử Việt Nam | Hiệp định Paris về chấm dứt chiến tranh ở Việt Nam được ký năm nào? | 1973 | 1954 | 1968 | 1975
Lịch sử Việt Nam | Thủ đô của nước Việt Nam thống nhất từ năm 1976 là? | Hà Nội | Huế | Sài Gòn | Đà Nẵng
Lịch sử Việt Nam | Ai là tác giả "Bình Ngô đại cáo"? | Nguyễn Trãi | Lê Lợi | Nguyễn Du | Lý Thường Kiệt
Lịch sử Việt Nam | Bài thơ "Nam quốc sơn hà" gắn với cuộc kháng chiến chống quân xâm lược nào? | Tống | Nguyên – Mông | Minh | Thanh
Lịch sử thế giới | Cách mạng Pháp bùng nổ năm nào? | 1789 | 1776 | 1815 | 1848
Lịch sử thế giới | Ai là Tổng thống đầu tiên của Hoa Kỳ? | George Washington | Abraham Lincoln | Thomas Jefferson | John Adams
Lịch sử thế giới | Bức tường Berlin sụp đổ năm nào? | 1989 | 1961 | 1975 | 1991
Lịch sử thế giới | Cristoforo Colombo tìm ra châu Mỹ vào năm nào? | 1492 | 1453 | 1519 | 1607
Lịch sử thế giới | Đế quốc nào xây dựng đấu trường Colosseum? | La Mã | Hy Lạp | Ba Tư | Ottoman
Lịch sử thế giới | Chiến tranh thế giới thứ nhất bắt đầu năm nào? | 1914 | 1905 | 1918 | 1939
Lịch sử thế giới | Ai là nữ hoàng Ai Cập nổi tiếng gắn với Caesar và Antony? | Cleopatra | Nefertiti | Hatshepsut | Isis
Lịch sử thế giới | Thành phố nào bị núi lửa Vesuvius chôn vùi năm 79? | Pompeii | Athens | Carthage | Troy
Lịch sử thế giới | Cuộc cách mạng công nghiệp bắt đầu đầu tiên ở nước nào? | Anh | Pháp | Đức | Mỹ
Lịch sử thế giới | Liên Xô tan rã vào năm nào? | 1991 | 1985 | 1989 | 1999
Lịch sử thế giới | Ai là người lãnh đạo phong trào đấu tranh chống chủ nghĩa apartheid ở Nam Phi và sau là tổng thống? | Nelson Mandela | Mahatma Gandhi | Martin Luther King | Kofi Annan
Văn học | Tác giả của "Dế Mèn phiêu lưu ký" là ai? | Tô Hoài | Nam Cao | Nguyễn Nhật Ánh | Kim Lân
Văn học | "Lão Hạc" là tác phẩm của nhà văn nào? | Nam Cao | Ngô Tất Tố | Vũ Trọng Phụng | Nguyên Hồng
Văn học | "Tắt đèn" là tác phẩm của nhà văn nào? | Ngô Tất Tố | Nam Cao | Nguyễn Công Hoan | Thạch Lam
Văn học | Tác giả của "Những ngày thơ ấu" là ai? | Nguyên Hồng | Tô Hoài | Thạch Lam | Nam Cao
Văn học | "Đất rừng phương Nam" là tác phẩm của nhà văn nào? | Đoàn Giỏi | Tô Hoài | Nguyễn Huy Thiệp | Bùi Hiển
Văn học | "Cho tôi xin một vé đi tuổi thơ" là tác phẩm của nhà văn nào? | Nguyễn Nhật Ánh | Tô Hoài | Nguyễn Ngọc Tư | Dương Thụy
Văn học | Nhà thơ nào được mệnh danh là "Bà chúa thơ Nôm"? | Hồ Xuân Hương | Đoàn Thị Điểm | Bà Huyện Thanh Quan | Ngô Chi Lan
Văn học | "Chinh phụ ngâm" được dịch ra chữ Nôm bởi ai (theo giả thuyết phổ biến)? | Đoàn Thị Điểm | Nguyễn Du | Hồ Xuân Hương | Nguyễn Gia Thiều
Văn học | "Don Quixote" là tác phẩm nổi tiếng của nhà văn nước nào? | Tây Ban Nha | Pháp | Ý | Anh
Văn học | Ai là tác giả "Những người khốn khổ" (Les Misérables)? | Victor Hugo | Alexandre Dumas | Honoré de Balzac | Émile Zola
Văn học | Ai là tác giả bộ tiểu thuyết "Chiến tranh và hòa bình"? | Lev Tolstoy | Fyodor Dostoevsky | Anton Chekhov | Maxim Gorky
Văn học | Ai là tác giả "Ông già và biển cả"? | Ernest Hemingway | Mark Twain | John Steinbeck | F. Scott Fitzgerald
Văn học | Ai là tác giả "Hoàng tử bé"? | Antoine de Saint-Exupéry | Jules Verne | Victor Hugo | Albert Camus
Văn học | "Chúa tể những chiếc nhẫn" là tác phẩm của ai? | J.R.R. Tolkien | J.K. Rowling | C.S. Lewis | George R.R. Martin
Văn học | Nhà văn nào sáng tạo nhân vật thám tử Sherlock Holmes? | Arthur Conan Doyle | Agatha Christie | Edgar Allan Poe | Dan Brown
Khoa học | Nguyên tố nào có ký hiệu hóa học là Fe? | Sắt | Flo | Franxi | Phốt pho
Khoa học | Hành tinh nào có hệ thống vành đai nổi bật nhất? | Sao Thổ | Sao Mộc | Sao Thiên Vương | Sao Hải Vương
Khoa học | Đơn vị đo cường độ dòng điện là gì? | Ampe | Vôn | Ôm | Oát
Khoa học | Quá trình thực vật tạo ra chất dinh dưỡng nhờ ánh sáng gọi là gì? | Quang hợp | Hô hấp | Thoát hơi nước | Lên men
Khoa học | Loại khí nào chúng ta hít vào để duy trì sự sống? | Oxy | Nitơ | Hiđrô | Heli
Khoa học | Nhóm máu nào được coi là "người cho phổ quát"? | O | A | B | AB
Khoa học | Bộ phận nào của cơ thể bơm máu đi khắp nơi? | Tim | Gan | Thận | Phổi
Khoa học | Nhà khoa học nào phát hiện ra định luật vạn vật hấp dẫn? | Isaac Newton | Albert Einstein | Galileo Galilei | Stephen Hawking
Khoa học | Ai phát minh ra bóng đèn sợi đốt thương mại hóa phổ biến? | Thomas Edison | Nikola Tesla | Alexander Bell | Michael Faraday
Khoa học | Marie Curie đoạt giải Nobel về lĩnh vực nào? | Vật lý và Hóa học | Y học | Văn học | Hòa bình
Khoa học | Độ pH của nước tinh khiết ở 25°C là bao nhiêu? | 7 | 0 | 14 | 1
Khoa học | Âm thanh không thể truyền trong môi trường nào? | Chân không | Không khí | Nước | Thép
Khoa học | Vật thể nào hút các vật bằng sắt? | Nam châm | Gương | Thấu kính | Lăng kính
Khoa học | Quá trình nước chuyển từ thể lỏng sang thể hơi gọi là gì? | Bay hơi | Ngưng tụ | Đông đặc | Thăng hoa
Khoa học | Hợp chất nào được dùng làm muối ăn? | NaCl | KCl | CaCO₃ | NaOH
Khoa học | Loại axit có trong dạ dày của người là gì? | Axit clohiđric | Axit sunfuric | Axit nitric | Axit axetic
Khoa học | DNA là viết tắt của gì? | Axit deoxyribonucleic | Axit ribonucleic | Axit amin | Axit béo
Khoa học | Loài động vật nào đẻ trứng nhưng là động vật có vú? | Thú mỏ vịt | Dơi | Cá heo | Kangaroo
Vũ trụ | Mặt Trăng quay quanh hành tinh nào? | Trái Đất | Sao Hỏa | Sao Kim | Sao Mộc
Vũ trụ | Ngôi sao gần Trái Đất nhất là gì? | Mặt Trời | Sao Bắc Cực | Sirius | Proxima Centauri
Vũ trụ | Hệ Mặt Trời có bao nhiêu hành tinh? | 8 | 9 | 7 | 10
Vũ trụ | Thiên hà chứa Hệ Mặt Trời tên là gì? | Ngân Hà | Tiên Nữ | Tam Giác | Xoáy Ốc
Vũ trụ | Ai là người đầu tiên bay vào không gian? | Yuri Gagarin | Neil Armstrong | Alan Shepard | John Glenn
Vũ trụ | Hành tinh nào nóng nhất Hệ Mặt Trời? | Sao Kim | Sao Thủy | Sao Hỏa | Sao Mộc
Vũ trụ | Tàu Apollo 11 đưa con người lên Mặt Trăng năm nào? | 1969 | 1961 | 1972 | 1957
Vũ trụ | Vệ tinh nhân tạo đầu tiên của loài người có tên là gì? | Sputnik 1 | Explorer 1 | Vostok 1 | Apollo 1
Địa lý | Thành phố nào là thành phố đông dân nhất Việt Nam? | TP. Hồ Chí Minh | Hà Nội | Đà Nẵng | Hải Phòng
Địa lý | Con sông dài nhất thế giới thường được nêu là sông nào? | Sông Nile | Sông Amazon | Sông Dương Tử | Sông Mississippi
Địa lý | Đỉnh núi cao nhất thế giới là? | Everest | K2 | Kilimanjaro | Mont Blanc
Địa lý | Hồ nước ngọt lớn nhất thế giới theo diện tích là? | Hồ Superior | Hồ Baikal | Hồ Victoria | Hồ Michigan
Địa lý | Châu lục nào có diện tích lớn nhất? | Châu Á | Châu Phi | Châu Mỹ | Châu Âu
Địa lý | Quốc gia nào có nhiều hòn đảo nhất thế giới? | Thụy Điển | Indonesia | Philippines | Nhật Bản
Địa lý | Eo biển nào ngăn cách châu Á và Bắc Mỹ? | Eo biển Bering | Eo biển Gibraltar | Eo biển Malacca | Eo biển Hormuz
Địa lý | Thác nước Niagara nằm giữa biên giới hai nước nào? | Mỹ và Canada | Mỹ và Mexico | Brazil và Argentina | Zambia và Zimbabwe
Địa lý | Biển nào là biển mặn nhất, nơi người ta có thể nổi trên mặt nước? | Biển Chết | Biển Đỏ | Biển Đen | Biển Caspi
Địa lý | Vĩ tuyến 0° còn được gọi là gì? | Xích đạo | Chí tuyến Bắc | Chí tuyến Nam | Vòng cực Bắc
Địa lý | Nước nào có dân số đông nhất châu Phi? | Nigeria | Ai Cập | Ethiopia | Nam Phi
Địa lý | Quần đảo Hoàng Sa và Trường Sa thuộc chủ quyền của nước nào? | Việt Nam | Philippines | Malaysia | Indonesia
Thể thao | World Cup bóng đá được tổ chức mấy năm một lần? | 4 năm | 2 năm | 3 năm | 5 năm
Thể thao | Quốc gia nào vô địch World Cup bóng đá nhiều lần nhất? | Brazil | Đức | Ý | Argentina
Thể thao | Một trận bóng rổ chính thức mỗi đội có bao nhiêu cầu thủ trên sân? | 5 | 6 | 7 | 11
Thể thao | Môn thể thao nào dùng quả cầu lông (shuttlecock)? | Cầu lông | Quần vợt | Bóng bàn | Bóng chuyền
Thể thao | Marathon có cự ly khoảng bao nhiêu km? | 42 km | 21 km | 10 km | 50 km
Thể thao | Giải quần vợt nào được chơi trên sân đất nện? | Roland Garros | Wimbledon | US Open | Australian Open
Thể thao | Đội tuyển Việt Nam vô địch AFF Cup lần đầu vào năm nào? | 2008 | 1998 | 2018 | 2014
Thể thao | Huy chương vàng Olympic đầu tiên của Việt Nam thuộc về ai? | Hoàng Xuân Vinh | Nguyễn Thị Ánh Viên | Trần Hiếu Ngân | Lê Văn Công
Thể thao | Messi sinh ra ở quốc gia nào? | Argentina | Tây Ban Nha | Brazil | Uruguay
Thể thao | Cầu thủ nào giành nhiều Quả bóng vàng nhất? | Lionel Messi | Cristiano Ronaldo | Michel Platini | Johan Cruyff
Thể thao | Môn thể thao "vua của các môn thể thao" ở Olympic thường được gọi là? | Điền kinh | Bơi lội | Thể dục dụng cụ | Cử tạ
Thể thao | Cờ vua có tổng cộng bao nhiêu ô trên bàn cờ? | 64 | 32 | 81 | 100
Toán học | Số Pi xấp xỉ bằng bao nhiêu? | 3,14 | 2,71 | 1,62 | 4,13
Toán học | Hình tam giác đều có mấy trục đối xứng? | 3 | 1 | 2 | 6
Toán học | 15% của 200 là bao nhiêu? | 30 | 15 | 20 | 45
Toán học | Hình lập phương có bao nhiêu mặt? | 6 | 4 | 8 | 12
Toán học | Chu vi hình vuông cạnh 5 cm là? | 20 cm | 10 cm | 25 cm | 15 cm
Toán học | 2 mũ 10 bằng bao nhiêu? | 1024 | 512 | 2048 | 1000
Toán học | Số La Mã "XIV" có giá trị là? | 14 | 16 | 6 | 24
Toán học | Số nào là số chẵn? | 108 | 77 | 91 | 53
Công nghệ | Ngôn ngữ nào thường dùng để tạo cấu trúc trang web? | HTML | Python | SQL | Java
Công nghệ | Mạng xã hội nào có biểu tượng chim xanh trước khi đổi tên? | Twitter | Facebook | Instagram | Snapchat
Công nghệ | Công ty nào sản xuất iPhone? | Apple | Samsung | Sony | Nokia
Công nghệ | "AI" trong công nghệ là viết tắt của gì? | Artificial Intelligence | Automatic Internet | Advanced Input | Applied Interface
Công nghệ | Bộ nhớ nào bị mất dữ liệu khi tắt nguồn? | RAM | SSD | Ổ cứng HDD | USB
Công nghệ | Ai là người sáng lập hãng vũ trụ SpaceX? | Elon Musk | Jeff Bezos | Bill Gates | Mark Zuckerberg
Công nghệ | Google ban đầu ra đời như một dự án của ai? | Larry Page và Sergey Brin | Steve Jobs và Steve Wozniak | Bill Gates và Paul Allen | Jack Ma
Công nghệ | Wi-Fi là công nghệ dùng để làm gì? | Kết nối mạng không dây | Sạc pin | Chụp ảnh | Phát nhạc qua dây
Công nghệ | Ký hiệu "@" trong địa chỉ email đọc tiếng Việt thường gọi là gì? | A còng | Dấu sao | Dấu thăng | Dấu và
Công nghệ | Thiết bị đầu vào nào dùng để gõ chữ? | Bàn phím | Màn hình | Loa | Máy in
Âm nhạc | Ca khúc "Tiến quân ca" do nhạc sĩ nào sáng tác? | Văn Cao | Phạm Tuyên | Hoàng Vân | Lưu Hữu Phước
Âm nhạc | Ban nhạc The Beatles đến từ thành phố nào của Anh? | Liverpool | London | Manchester | Birmingham
Âm nhạc | "Ông hoàng nhạc Pop" là biệt danh của ca sĩ nào? | Michael Jackson | Elvis Presley | Prince | Justin Bieber
Âm nhạc | Một dàn nhạc giao hưởng thường được chỉ huy bởi ai? | Nhạc trưởng | Ca sĩ chính | Nhạc công piano | Nhà soạn nhạc
Âm nhạc | Bao nhiêu nốt nhạc cơ bản trong một quãng tám (không tính nốt lặp)? | 7 | 5 | 8 | 12
Âm nhạc | Nhạc sĩ "Mozart" đến từ quốc gia nào? | Áo | Đức | Ý | Pháp
Điện ảnh | Phim hoạt hình "Vua sư tử" có nhân vật chính tên là gì? | Simba | Mufasa | Scar | Nala
Điện ảnh | "Titanic" kể về sự kiện nào? | Con tàu đắm năm 1912 | Chiến tranh thế giới | Cuộc đua vũ trụ | Cơn bão lớn
Điện ảnh | Hãng phim nào sản xuất "Toy Story"? | Pixar | DreamWorks | Illumination | Ghibli
Điện ảnh | "Spirited Away" (Vùng đất linh hồn) là phim của hãng nào? | Studio Ghibli | Pixar | Disney | Toei
Điện ảnh | Ai là đạo diễn bộ phim "Inception" và "Interstellar"? | Christopher Nolan | Steven Spielberg | James Cameron | Ridley Scott
Điện ảnh | "Avengers" là siêu anh hùng của hãng nào? | Marvel | DC | Pixar | Lucasfilm
Văn hóa Việt Nam | Tết Nguyên Đán thường diễn ra vào mùa nào? | Mùa xuân | Mùa hè | Mùa thu | Mùa đông
Văn hóa Việt Nam | Tết Trung thu diễn ra vào ngày nào âm lịch? | 15/8 | 5/5 | 1/1 | 15/1
Văn hóa Việt Nam | Bánh chưng thường được gói bằng loại lá nào? | Lá dong | Lá chuối | Lá sen | Lá tre
Văn hóa Việt Nam | Trang phục truyền thống của phụ nữ Việt Nam là gì? | Áo dài | Áo bà ba | Áo tứ thân | Áo yếm
Văn hóa Việt Nam | Làn điệu "Quan họ" là di sản văn hóa của tỉnh nào? | Bắc Ninh | Thanh Hóa | Nghệ An | Huế
Văn hóa Việt Nam | Nghệ thuật múa rối nước truyền thống phát triển mạnh ở vùng nào? | Đồng bằng Bắc Bộ | Tây Nguyên | Đồng bằng sông Cửu Long | Duyên hải Nam Trung Bộ
Văn hóa Việt Nam | Lễ hội Đền Hùng được tổ chức vào ngày nào âm lịch? | 10/3 | 15/1 | 5/5 | 15/7
Văn hóa Việt Nam | Quốc ngữ chữ Latinh của Việt Nam được hoàn thiện bởi ai? | Alexandre de Rhodes | Phan Châu Trinh | Trương Vĩnh Ký | Nguyễn Trường Tộ
Văn hóa Việt Nam | Loại cây nào được xem là biểu tượng của làng quê Việt Nam? | Tre | Thông | Phượng | Bàng
Văn hóa Việt Nam | Con vật nào đứng đầu trong 12 con giáp? | Chuột (Tý) | Trâu (Sửu) | Hổ (Dần) | Mèo (Mão)
Văn hóa Việt Nam | Trong 12 con giáp của Việt Nam, con giáp thứ tư là gì? | Mèo (Mão) | Rồng (Thìn) | Hổ (Dần) | Dê (Mùi)
Sinh học | Cây xanh thải ra khí nào khi quang hợp? | Oxy | Cacbonic | Nitơ | Metan
Sinh học | Động vật nào sau đây là loài lưỡng cư? | Ếch | Cá sấu | Rùa | Thằn lằn
Sinh học | Cơ thể người có bao nhiêu nhiễm sắc thể? | 46 | 23 | 48 | 44
Sinh học | Máu mang oxy đi nuôi cơ thể nhờ thành phần nào? | Hồng cầu | Bạch cầu | Tiểu cầu | Huyết tương
Sinh học | Bộ phận nào của cây hút nước từ đất? | Rễ | Thân | Lá | Hoa
Sinh học | Loài động vật nào ngủ đông vào mùa lạnh? | Gấu | Voi | Sư tử | Hươu cao cổ
Sinh học | Ruột non dài khoảng bao nhiêu mét ở người trưởng thành? | Khoảng 6 mét | Khoảng 1 mét | Khoảng 20 mét | Khoảng 50 cm
Sinh học | Ong thợ thu thập gì từ hoa để làm mật? | Mật hoa | Phấn hoa khô | Nước mưa | Nhựa cây
"""


def parse():
    out = []
    for line in EXTRA.strip().splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 6 or not all(parts):
            continue
        cat, q, *opts = parts
        out.append(dict(category=cat, q=q, options=opts))
    return out
