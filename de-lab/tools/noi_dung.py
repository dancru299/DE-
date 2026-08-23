# -*- coding: utf-8 -*-
"""Nội dung 7 bài lab.

Mỗi bài có 3 phần:
  nen    -- giải thích khái niệm, đọc trước khi làm. Viết cho người chưa biết gì.
  de     -- các bước phải làm
  goi_y  -- mở dần từng mức khi bí
"""

BAI = {
1: {
  "ten": "Chạy được, và hiểu dbt thực ra làm gì",
  "hoc": "dbt KHÔNG chạy SQL. Nó soạn SQL rồi nhờ database chạy hộ.",
  "thoi_gian": "30 phút",
  "nen": """
NGƯỜI TA HAY NÓI "dbt LÀ CÔNG CỤ TRANSFORM DỮ LIỆU". Câu đó đúng mà vô dụng,
vì nó không nói cho bạn biết dbt thật sự làm gì. Nói lại cho chính xác:

    dbt là một công cụ SOẠN CÂU SQL rồi GỬI CHO DATABASE CHẠY HỘ.

Nó không lưu một byte dữ liệu nào. Nó không tính một phép tính nào. Bạn có
thể làm mọi thứ dbt làm bằng tay -- chỉ là sẽ mất vài tuần và sai be bét.

BỐN THỨ CẦN HIỂU TRƯỚC KHI BẤM LỆNH ĐẦU TIÊN

1) MODEL LÀ MỘT FILE .sql. Hết.

   Mở models/dwh/stg_bookings.sql ra xem: bên trong chỉ là một câu SELECT.
   dbt lấy câu SELECT đó, bọc thêm "hãy tạo bảng từ kết quả này", gửi xuống
   database. Tên file thành tên bảng.

   Một file = một bảng. Lab này có 5 file trong models/, nên tạo ra 5 bảng.

2) ENGINE LÀ NƠI DỮ LIỆU THẬT SỰ NẰM.

   DuckDB (trong lab này), BigQuery (ở công ty bạn), ClickHouse, Postgres --
   tất cả đều là engine. Chúng chứa dữ liệu và làm phép tính.

   dbt đứng ngoài, không phải engine.
   Ví von: dbt là người viết đơn đặt món, engine là nhà bếp nấu.

3) {{ }} LÀ CHỖ TRỐNG SẼ ĐƯỢC ĐIỀN.

   Trong file model bạn sẽ thấy:  from {{ ref('stg_bookings') }}

   Database không hiểu ký hiệu {{ }}. Nên trước khi gửi đi, dbt phải điền
   vào chỗ trống đó bằng tên bảng thật. Bước điền này gọi là COMPILE.

   Giống thư mẫu: viết sẵn "Kính gửi anh/chị {{ho_ten}}", tới lúc gửi thật
   thì điền tên vào. Người nhận không bao giờ thấy {{ho_ten}}.

4) VIEW HAY TABLE -- KẾT QUẢ SẼ LƯU DƯỚI DẠNG GÌ.

   Cùng một câu SELECT, lưu được hai kiểu:

     view   Lưu CÂU HỎI, không lưu kết quả. Ai đọc thì tính lại từ đầu.
            -> luôn mới nhất, không tốn chỗ, đọc chậm nếu logic phức tạp.
     table  Lưu KẾT QUẢ thật. Đọc nhanh, nhưng phải chạy lại dbt mới cập nhật.

   Ví von: view là CÔNG THỨC NẤU ĂN, table là MÓN NẤU SẴN để tủ lạnh.

   Trong lab: tầng dwh để view, tầng mart để table -- khai báo ở dbt_project.yml.

BÀY TRÍ CỦA LAB NÀY

    data/          file CSV, đóng vai dữ liệu từ hệ nguồn gửi sang
    tools/         script nạp dữ liệu vào tầng lake (đóng vai Kafka Connect)
    models/dwh/    tầng làm sạch
    models/mart/   tầng phục vụ business
    lab.duckdb     TOÀN BỘ database nằm trong 1 file này. Xoá là làm lại từ đầu.
    target/        dbt tự sinh ra sau khi chạy -- chứa SQL đã compile

Từ nào chưa rõ:  ./lab tudien model     (hoặc engine, compile, materialized...)
""",
  "de": """
BƯỚC 1 -- Chạy 2 lệnh:

    ./lab nap        đổ dữ liệu thô vào tầng lake (chưa liên quan gì tới dbt)
    ./lab run        dbt dựng 5 model

Bạn sẽ thấy dbt in ra từng model một, kèm "OK created sql view model..."
Nếu 5 dòng đều OK là xong bước 1.

BƯỚC 2 -- Đây mới là phần đáng giá của bài này.

Mở 2 file sau đặt cạnh nhau:

    models/dwh/fct_bookings.sql                            <- BẠN viết
    target/compiled/de_lab/models/dwh/fct_bookings.sql     <- dbt SINH RA

(không muốn mở editor thì gõ:  ./lab sql fct_bookings)

Tìm 2 khác biệt:

  KHÁC BIỆT 1
    bạn viết       from {{ ref('stg_bookings') }}
    dbt sinh ra    from "lab"."dwh"."stg_bookings"

    Chỗ trống đã được điền bằng tên bảng thật, đủ 3 tầng:
    database "lab", schema "dwh", bảng "stg_bookings".

  KHÁC BIỆT 2
    Ở cuối file bạn viết có khối {% if is_incremental() %} ... {% endif %}
    Trong file dbt sinh ra, khối đó BIẾN MẤT HOÀN TOÀN.

    Vì đây là lần chạy đầu tiên, bảng chưa tồn tại, nên câu hỏi
    "đây có phải lần chạy thêm không?" trả lời là KHÔNG -> không chèn gì cả.

File thứ hai chính là câu SQL mà DuckDB nhận được. Không hơn không kém.
Ở công ty, câu tương đương chính là thứ BigQuery nhận và tính tiền bạn.

BƯỚC 3 -- Tự trả lời trước khi sang bài sau:

  Nếu dbt chỉ làm mỗi việc thay thế chuỗi như vậy, thì nó giải quyết được
  vấn đề gì mà viết SQL tay không giải quyết được?

  (Bài 2 sẽ trả lời. Nhưng thử tự nghĩ trước sẽ nhớ lâu hơn nhiều.)

    ./lab check 1
""",
  "goi_y": [
    "Thư mục target/ chỉ xuất hiện SAU khi chạy `./lab run` lần đầu. Chưa thấy thì chạy lại.",
    "Cẩn thận nhầm thư mục: target/compiled/ là SQL đã điền chỗ trống (cái bạn cần xem). target/run/ là câu đó đã bọc thêm 'create table' -- cũng đọc được nhưng dài hơn.",
    "Không muốn mở editor: ./lab sql fct_bookings",
  ],
  "dap_an": """
Bài này không có code để chép. Nhưng câu hỏi ở bước 3 có đáp án:

dbt giải quyết 3 việc mà SQL tay không làm được khi số model lớn dần:

  1. THỨ TỰ CHẠY. 200 model phụ thuộc lẫn nhau, ai chạy trước ai? dbt tự
     suy ra từ ref(). Làm tay thì phải duy trì danh sách thứ tự, và nó sẽ sai.

  2. MÔI TRƯỜNG. Cùng bộ code chạy được trên dev và prod, chỉ đổi một dòng
     cấu hình. SQL tay thì phải sửa tên dataset trong từng file.

  3. TÁI SỬ DỤNG. Sửa logic làm sạch ở một model, mọi model dùng nó tự có
     logic mới. Copy-paste SQL thì sửa một chỗ phải nhớ sửa mười nơi.
""",
},

2: {
  "ten": "ref() và lineage: dạy cho dbt biết ai phụ thuộc ai",
  "hoc": "ref() không phải cách viết cho đẹp. Nó là thứ DUY NHẤT tạo ra thứ tự chạy.",
  "thoi_gian": "45 phút",
  "nen": """
BÀI 1 KẾT THÚC BẰNG CÂU HỎI "dbt giải quyết vấn đề gì". Đây là câu trả lời.

VẤN ĐỀ: THỨ TỰ

Kho dữ liệu công ty bạn có hàng trăm bảng, bảng này lấy dữ liệu từ bảng kia.
mart cần fct, fct cần stg, stg cần lake. Chạy sai thứ tự thì đọc phải bảng
chưa được dựng, hoặc tệ hơn: đọc phải bảng dựng từ hôm qua mà không biết.

Cách thủ công là duy trì một danh sách thứ tự chạy. Danh sách đó sẽ sai,
vì mỗi lần ai đó thêm model là phải nhớ cập nhật, và sẽ có ngày quên.

CÁCH dbt LÀM: BẮT BẠN KHAI BÁO NGUỒN, RỒI TỰ SUY RA THỨ TỰ

Hai cách khai báo, dùng cho hai loại nguồn khác nhau:

    {{ ref('stg_bookings') }}          bảng do CHÍNH dbt tạo ra
    {{ source('lake', 'bookings') }}   bảng do hệ thống KHÁC đổ vào
                                       (Kafka Connect, CDC, job nạp file)
                                       dbt chỉ đọc, không bao giờ ghi

Từ những khai báo đó dbt vẽ ra sơ đồ phụ thuộc, gọi là LINEAGE:

    lake.bookings -> stg_bookings -> fct_bookings -> mart_don_dua_don

Chú ý điều này: dbt KHÔNG phân tích câu SQL của bạn để đoán ra sơ đồ.
Nó chỉ đọc xem bạn viết ref() ở đâu. Chỉ vậy thôi.

HỆ QUẢ QUAN TRỌNG NHẤT CỦA BÀI NÀY

Nếu bạn viết thẳng tên bảng thay vì ref():

    from dwh.stg_customers          <- vẫn chạy được!

thì câu SQL vẫn đúng, kết quả vẫn ra, không ai báo lỗi. NHƯNG dbt bị mù ở
đúng chỗ đó. Sơ đồ vẫn vẽ, chỉ thiếu một mũi tên, và không ai biết là thiếu.

Tới một ngày:
  - dbt chạy mart TRƯỚC stg_customers vì nó tưởng hai bảng không liên quan
  - hoặc ai đó đổi tên stg_customers, mọi ref() tự cập nhật, riêng chỗ này vỡ
  - hoặc bạn cần biết "sửa stg_customers thì ảnh hưởng bảng nào" -- và sót

Loại lỗi này không xuất hiện lúc bạn viết. Nó xuất hiện sau 3 tháng, lúc
người viết đã quên, và rất khó lần ra.

HAI THỨ CÚ PHÁP SẼ DÙNG TRONG BÀI

  CTE (with ... as)  đặt tên cho một kết quả trung gian:

      with don as (
          select * from {{ ref('fct_bookings') }} where trang_thai = 'CONFIRMED'
      )
      select * from don

    "don" là tên tạm, chỉ sống trong câu lệnh này. Giống biến tạm khi code.
    Lợi ích không phải chạy nhanh hơn, mà là ĐỌC ĐƯỢC.

  JOIN  ghép hai bảng theo cột chung:

      inner join   chỉ giữ dòng CÓ Ở CẢ HAI bên. Thiếu bên kia -> mất dòng.
      left  join   giữ HẾT bên trái, bên phải thiếu thì để trống (NULL).

    Quy tắc an toàn: mất một đơn hàng là mất tiền. Phân vân thì LEFT JOIN,
    rồi thêm test để biết có bao nhiêu dòng thiếu -- còn hơn INNER JOIN rồi
    âm thầm mất đơn mà không ai biết.

Tra thêm:  ./lab tudien ref | source | lineage | cte | join
""",
  "de": """
BƯỚC 1 -- Xem cây phụ thuộc hiện tại và GHI LẠI (lát nữa so):

    ./lab cay

BƯỚC 2 -- Nhiệm vụ thật:

Đội marketing muốn bảng mart có thêm TÊN KHÁCH HÀNG để cá nhân hoá tin nhắn.

Sửa file  models/mart/mart_don_dua_don.sql  để thêm cột  ho_ten.
Tên khách lấy từ model  stg_customers  (đã có sẵn, không phải viết mới).

RÀNG BUỘC -- chính là bài học:
    PHẢI dùng {{ ref('stg_customers') }}
    KHÔNG được viết thẳng dwh.stg_customers

BƯỚC 3 -- Chạy lại và so cây:

    ./lab run
    ./lab cay

Cây đã tự đổi, dù bạn không hề khai báo thứ tự chạy ở bất kỳ đâu.
Bạn chỉ nói "tôi lấy dữ liệu từ stg_customers", dbt tự suy ra phần còn lại.

BƯỚC 4 -- Thí nghiệm (không bắt buộc, nhưng làm thì hiểu sâu hơn nhiều):

Tạm thay ref('stg_customers') bằng tên cứng "dwh"."stg_customers", chạy
./lab run. NÓ VẪN CHẠY ĐƯỢC, kết quả y hệt.

Rồi chạy ./lab cay -- mũi tên tới stg_customers đã biến mất khỏi sơ đồ.

Đó là toàn bộ cái bẫy: sai mà không báo lỗi, chỉ âm thầm mất thông tin.
Nhớ đổi lại ref() trước khi check.

    ./lab check 2
""",
  "goi_y": [
    "Thêm một CTE nữa ở đầu, cạnh 2 CTE đã có:\n\nkhach as (\n    select * from {{ ref('stg_customers') }}\n)\n\nNhớ dấu phẩy ngăn cách giữa các CTE, và CTE cuối cùng KHÔNG có dấu phẩy.",
    "Rồi ghép vào phần cuối câu:\n\nleft join khach k on d.customer_id = k.customer_id",
    "Dùng LEFT JOIN chứ đừng INNER JOIN. Nếu một đơn có customer_id không tìm thấy trong bảng khách, INNER JOIN sẽ làm biến mất luôn cả đơn đó. Mất đơn là mất tiền.",
    "Cuối cùng nhớ thêm k.ho_ten vào danh sách cột ở câu select (phần sau chữ select, trước chữ from). Quên bước này thì join xong mà cột vẫn không xuất hiện.",
  ],
  "dap_an": """
Thêm CTE thứ ba, thêm cột vào select, thêm left join:

with don as (
    select * from {{ ref('fct_bookings') }}
    where trang_thai = 'CONFIRMED'
),

dua_don as (
    select * from {{ ref('stg_services') }}
    where loai_dich_vu = 'SHUTTLE'
),

khach as (
    select * from {{ ref('stg_customers') }}
)

select
    d.booking_id,
    k.ho_ten,                      <- cột mới
    d.customer_id,
    d.hotel_code,
    d.ngay_nhan_phong,
    d.so_dem,
    d.tong_tien,
    dd.gio_don,
    dd.so_tien           as tien_dua_don,
    d.cap_nhat_luc

from don d
inner join dua_don dd
        on d.booking_id = dd.booking_id
left join khach k                  <- join mới
        on d.customer_id = k.customer_id
""",
},

3: {
  "ten": "Tái hiện lỗi nhân dòng của incremental",
  "hoc": "Bài này KHÔNG sửa gì cả. Mục tiêu là nhìn tận mắt dữ liệu sai trông như thế nào.",
  "thoi_gian": "45 phút",
  "nen": """
BÀI NÀY LÀ BÀI QUAN TRỌNG NHẤT TRONG 7 BÀI. Không phải vì kỹ thuật khó,
mà vì nó cho bạn thấy loại lỗi mà pipeline KHÔNG BAO GIỜ tự báo.

PHẦN 1 -- VÌ SAO TẦNG LAKE LẠI CÓ DỮ LIỆU TRÙNG

Hệ thống bán hàng có database riêng. Bạn cần dữ liệu đó nhưng không được
query thẳng vào -- query nặng làm chậm hệ thống bán hàng, khách không đặt
được phòng, và đó là sự cố thật.

Giải pháp là CDC (Change Data Capture). CDC đọc NHẬT KÝ GHI của database
nguồn -- cuốn sổ mà database tự ghi lại mọi lệnh thêm/sửa/xoá -- rồi gửi
từng thay đổi sang kho. Bên bạn Kafka Connect làm việc này.

Hệ quả, và đây là điểm mấu chốt:

    Sửa MỘT đơn ở hệ nguồn -> CDC gửi sang MỘT DÒNG MỚI, không ghi đè.

Nên tầng lake là APPEND-ONLY: chỉ nối thêm vào cuối, không bao giờ động vào
dòng cũ. Một đơn bị sửa 3 lần thì lake có 4 dòng cho đơn đó -- 1 dòng lúc
tạo và 3 phiên bản sau mỗi lần sửa.

ĐÂY LÀ THIẾT KẾ ĐÚNG, KHÔNG PHẢI LỖI. Giữ nguyên trạng để còn đối chiếu
khi nghi ngờ số liệu. Nhưng nó chuyển việc "chọn phiên bản đúng" xuống cho
tầng dwh -- tức là cho BẠN.

PHẦN 2 -- CƠ CHẾ INCREMENTAL, VÀ CHỖ NÓ HỞ

Bảng đơn hàng có 500 triệu dòng, mỗi ngày thêm 200 nghìn. Quét lại cả 500
triệu mỗi ngày là vô lý -- trên BigQuery đó là tiền thật.

incremental nghĩa là: lần đầu dựng cả bảng, những lần sau chỉ xử lý phần
mới. Nhưng dbt không tự biết "phần mới" là gì. BẠN phải nói, bằng khối:

    {% if is_incremental() %}
      where cap_nhat_luc > (select max(cap_nhat_luc) from {{ this }})
    {% endif %}

    {{ this }}       = chính bảng đang dựng, phiên bản hiện có
    is_incremental() = "bảng đã tồn tại và không chạy --full-refresh?"

Đọc thành lời: "lấy những dòng có thời gian cập nhật mới hơn dòng mới nhất
mà tôi đang có."

Nghe hợp lý. Nhưng hãy hỏi tiếp một câu:

    Lấy được 6 dòng đó rồi, dbt LÀM GÌ với chúng?

Mặc định, khi bạn không nói gì thêm: nó CHÈN THÊM cả 6 dòng vào bảng.

Vấn đề là trong 6 dòng đó, có những dòng là PHIÊN BẢN MỚI của đơn ĐÃ CÓ
trong bảng. Không ai bảo nó xoá dòng cũ đi. Kết quả: 2 dòng cho 1 đơn.

Điều kiện lọc kia chỉ giúp chạy NHANH. Nó hoàn toàn không giúp chạy ĐÚNG.
Đây là chỗ hiểu nhầm phổ biến nhất về incremental.

PHẦN 3 -- CÔNG CỤ ĐỂ PHÁT HIỆN: SO SÁNH 2 CON SỐ

    select count(*), count(distinct booking_id) from bang;

    count(*)                  tổng số dòng
    count(distinct booking_id) số đơn KHÁC NHAU

Hai số bằng nhau -> mỗi đơn đúng 1 dòng.
Lệch nhau       -> có đơn chiếm nhiều hơn 1 dòng.

Đây chính xác là việc mà ./lab dem làm cho bạn ở cả 4 tầng cùng lúc.

Câu hỏi "một dòng trong bảng này là cái gì" có tên riêng: GRAIN. Trả lời
sai grain thì mọi phép cộng phía sau đều sai, và sai rất khó thấy.

Tra thêm:  ./lab tudien cdc | append-only | incremental | grain
""",
  "de": """
BƯỚC 1 -- Ghi lại hiện trạng trước đã:

    ./lab dem

Lúc này mọi tầng đều 12 dòng / 12 đơn -- cân bằng, chưa có gì sai.

BƯỚC 2 -- Đổ đợt dữ liệu thứ hai vào lake:

    ./lab nap2

Đợt này gồm 3 đơn MỚI (B0013-B0015) và 3 đơn CŨ VỪA BỊ SỬA:
    B0003  PENDING   -> CONFIRMED     (khách đã thanh toán)
    B0010  PENDING   -> CANCELLED     (khách huỷ)
    B0002  đổi ngày trả phòng và tổng tiền  (khách ở thêm)

Đọc kỹ output: lake giờ 18 dòng nhưng chỉ 15 booking_id. Đúng như phần nền
đã nói -- lake append-only, sửa đơn thì sinh dòng mới.

BƯỚC 3 -- Chạy lại pipeline rồi đếm lại:

    ./lab run
    ./lab dem

fct_bookings: 18 dòng / 15 đơn. Ba đơn đã bị NHÂN ĐÔI.

BƯỚC 4 -- Nhìn tận mắt một đơn bị nhân đôi:

    ./lab soi "select booking_id, trang_thai, tong_tien, cap_nhat_luc from dwh.fct_bookings where booking_id = 'B0002' order by cap_nhat_luc"

Hai dòng: một dòng cũ, một dòng mới. Cả hai cùng nằm trong bảng, ngang hàng
nhau, không có gì đánh dấu dòng nào mới hơn ngoài cột thời gian.

Bây giờ tưởng tượng ai đó chạy: select sum(tong_tien) from dwh.fct_bookings
-> B0002 được cộng 2 lần. Báo cáo doanh thu sai. Không ai báo lỗi.

BƯỚC 5 -- Ba câu hỏi, tự trả lời trước khi xem gợi ý:

  a) Vì sao đúng 3 đơn đó bị nhân đôi mà 12 đơn kia thì không?

  b) Chạy ./lab dem lại: mart chỉ nhân đôi 1 đơn thay vì 3. Vì sao?

  c) Nếu bảng mart này đẩy sang hệ thống gửi tin nhắn, khách của đơn B0002
     nhận được mấy tin?

Câu (c) là lý do người ta sợ loại lỗi này. Pipeline không đỏ. Log sạch.
dbt báo "Completed successfully". Nó chỉ âm thầm gửi tin 2 lần cho khách.

    ./lab check 3
""",
  "goi_y": [
    "Xem câu SQL đang THẬT SỰ chạy: ./lab sql fct_bookings -- lần này khối is_incremental đã hiện ra (khác bài 1), vì bảng đã tồn tại rồi.",
    "Điều kiện là `cap_nhat_luc > (select max(cap_nhat_luc) from bảng_này)`. Dòng mới nhất trong bảng có cap_nhat_luc là 2026-08-05 17:30. Cả 6 dòng đợt 2 đều mới hơn mốc đó, nên cả 6 lọt qua bộ lọc. Đúng như mong muốn.",
    "Câu hỏi tiếp theo mới là chỗ hở: lấy được 6 dòng đó rồi thì dbt LÀM GÌ? Mặc định nó CHÈN THÊM cả 6. Nhưng 3 trong 6 dòng là phiên bản mới của đơn đã nằm sẵn trong bảng. Không có ai xoá dòng cũ đi cả -> 2 dòng cho 1 đơn.",
    "Câu (b): mart lọc trang_thai='CONFIRMED' VÀ phải có dịch vụ SHUTTLE. B0003 chỉ có dịch vụ DINING nên bị loại, B0010 đã thành CANCELLED nên bị loại. Chỉ B0002 lọt qua. Nghĩa là bug ở tầng dưới chỉ lộ 1/3 lên tầng trên -- nên KHÔNG BAO GIỜ chỉ kiểm tra bảng cuối rồi kết luận là ổn.",
  ],
  "dap_an": """
a) Vì lệnh chèn chỉ biết THÊM, không biết THAY.
   6 dòng đợt 2 lọt qua bộ lọc và được chèn hết vào bảng. Trong đó 3 dòng
   là phiên bản mới của B0002/B0003/B0010 đã tồn tại -> mỗi đơn thành 2 dòng.

   Model đang thiếu đúng 2 thứ:
     - unique_key: khoá để dbt nhận ra "đơn này tôi đã có rồi"
     - incremental_strategy: cách xử lý khi trùng khoá (thay vì cứ thêm)

b) mart lọc CONFIRMED + có SHUTTLE. B0003 (dịch vụ DINING) và B0010
   (đã CANCELLED) bị loại từ trước. Chỉ B0002 lọt qua.
   Bài học: bug ở tầng dưới lộ lên tầng trên một cách không đầy đủ. Bảng
   cuối trông "gần đúng" không có nghĩa là tầng dưới đúng.

c) 2 tin nhắn.
   Và không có gì trong hệ thống báo cho bạn biết. Pipeline xanh, log sạch,
   dbt in "Completed successfully". Bạn chỉ biết khi khách phàn nàn, hoặc
   khi ai đó tình cờ đối soát.

   Bài 4 sẽ dựng cái bẫy để MÁY bắt được chuyện này thay cho bạn.
""",
},

4: {
  "ten": "Viết test bắt lỗi trước, sửa sau",
  "hoc": "Thứ tự đúng là: test đỏ trước, sửa sau. Test viết sau khi sửa thì không chứng minh được gì.",
  "thoi_gian": "75 phút",
  "nen": """
BÀI 3 KẾT THÚC VỚI 3 ĐƠN BỊ NHÂN ĐÔI VÀ KHÔNG AI BÁO. Bài này làm 2 việc:
dựng cái bẫy để máy tự báo, rồi mới sửa.

PHẦN 1 -- dbt test THẬT RA LÀ GÌ

Chỗ này hay hiểu ngược. Test của dbt KHÔNG kiểm tra "dữ liệu có đúng không".
Nó chạy một câu SELECT ĐI TÌM DÒNG SAI:

    tìm được 0 dòng  -> PASS   (không có gì sai)
    tìm được N dòng  -> FAIL N (có N chỗ sai)

Test `unique` trên cột booking_id, dịch ra tiếng Việt, là câu:
"tìm cho tôi những booking_id xuất hiện nhiều hơn 1 lần".
Bài 3 đã có 3 đơn như vậy, nên test sẽ trả về FAIL 3.

Bốn test có sẵn, không phải cài gì:
    unique            cột này có giá trị nào bị lặp không
    not_null          cột này có ô nào trống không
    accepted_values   có giá trị nào ngoài danh sách cho phép không
    relationships     mọi customer_id ở đây có tồn tại bên bảng khách không

Khai báo trong file .yml (không phải .sql). File .yml là file cấu hình,
dùng thụt lề để thể hiện cấp bậc -- thụt lề sai là báo lỗi, nên cẩn thận.

PHẦN 2 -- VÌ SAO PHẢI VIẾT TEST TRƯỚC KHI SỬA

Test viết SAU khi sửa xong thì bao giờ cũng xanh. Xanh nhưng chẳng chứng
minh được gì -- bạn không biết nó có thật sự bắt được lỗi hay không.

Viết TRƯỚC, thấy nó ĐỎ, rồi sửa cho XANH: lúc đó bạn có 2 bằng chứng --
cái bẫy hoạt động, và bản sửa của bạn thật sự giải quyết đúng vấn đề đó.

Đây cũng là cách bạn nên làm ở công ty với mọi bug: tái hiện được lỗi
trước, rồi mới sửa.

PHẦN 3 -- HAI THỨ CẦN ĐỂ SỬA, KHÔNG ĐƯỢC THIẾU CÁI NÀO

(a) DẠY dbt CÁCH THAY VÌ CÁCH THÊM -- sửa trong config:

    unique_key = 'booking_id'
        Cột nhận dạng một đơn. Có nó, dbt biết dòng mới nào trùng khoá với
        dòng cũ thì phải THAY chứ không THÊM.

    incremental_strategy = 'delete+insert'
        Cách thay. Ba lựa chọn hay gặp:
          append         cứ thêm, kệ trùng (mặc định khi không có unique_key)
          delete+insert  xoá dòng cũ trùng khoá, rồi chèn lô mới vào
          merge          một câu MERGE làm cả hai việc cùng lúc

        DuckDB dùng delete+insert. BigQuery thường dùng merge. Cùng ý tưởng,
        khác câu lệnh sinh ra. Không cần thuộc -- cần biết là có lựa chọn.

(b) KHỬ TRÙNG LẶP NGAY TRONG MỘT LÔ -- sửa trong SQL:

    Phần (a) xử lý trùng giữa dòng CŨ và dòng MỚI. Nhưng nếu ngay trong một
    lô đã có 2 phiên bản của cùng một đơn thì sao? Vẫn trùng.

    Giải bằng WINDOW FUNCTION. Đây là khái niệm mới, giải thích từ đầu:

    Khác biệt với GROUP BY:
        GROUP BY         5 dòng vào -> 1 dòng ra (gộp lại, mất chi tiết)
        window function  5 dòng vào -> 5 dòng ra (giữ nguyên, THÊM thông tin)

    Câu cần dùng:

        row_number() over (partition by booking_id order by cap_nhat_luc desc)
        \\_________/        \\______________________/  \\____________________/
         hàm                 chia nhóm theo đơn        trong nhóm sắp thế nào

    Đọc thành lời: "chia các dòng thành từng nhóm theo booking_id; trong mỗi
    nhóm sắp theo thời gian cập nhật GIẢM DẦN; rồi đánh số 1, 2, 3... "

    Kết quả: dòng số 1 của mỗi nhóm chính là phiên bản MỚI NHẤT của đơn đó.
    Giữ dòng số 1, bỏ phần còn lại -> đã khử trùng lặp.

    Giữ bằng cách nào? KHÔNG dùng được WHERE:

        where row_number() over (...) = 1        <-- SAI, chạy không được

    Vì database chạy WHERE TRƯỚC, tính window function SAU. Lúc WHERE chạy
    thì chưa có số thứ tự nào để mà lọc.

    Dùng QUALIFY -- mệnh đề sinh ra đúng cho việc này:

        qualify row_number() over (...) = 1

    Có ở cả DuckDB và BigQuery. Đặt ở cuối câu, sau WHERE.

    Bạn đã có sẵn một ví dụ chạy được: mở models/dwh/stg_services.sql đọc.
    Bài này chỉ là áp dụng đúng mẫu đó sang một cột khác.

Tra thêm:  ./lab tudien test | unique_key | window | qualify
""",
  "de": """
BƯỚC 1 -- DỰNG BẪY (làm khi dữ liệu còn đang sai)

Tạo file mới:  models/dwh/_models.yml

Khai báo test unique và not_null cho cột booking_id của model fct_bookings.
(Chưa biết viết .yml thế nào thì xem gợi ý 1 -- có khung sẵn để chép.)

    ./lab test

Test PHẢI ĐỎ, và phải đỏ đúng con số 3.
Nếu nó xanh thì bẫy đặt sai chỗ -- xem lại tên model và tên cột.

Đọc kỹ dòng lỗi. dbt in ra số dòng vi phạm, và in luôn đường dẫn tới câu
SQL nó đã dùng để tìm. Mở câu đó chạy lại là thấy đúng những dòng nào sai.
Đây là thứ bạn sẽ đọc mỗi ngày ở công ty.

BƯỚC 2 -- SỬA

Sửa  models/dwh/fct_bookings.sql, đủ cả 2 phần đã nói ở mục nền:
    (a) config: thêm unique_key và incremental_strategy
    (b) SQL: thêm QUALIFY khử trùng lặp trong lô

Thiếu (b) thì bài 5 sẽ rớt. Đừng bỏ qua.

    ./lab run
    ./lab test

BƯỚC 3 -- VÌ SAO TEST VẪN ĐỎ DÙ BẠN ĐÃ SỬA ĐÚNG?

Đừng hoảng, và đừng sửa tiếp. Chạy ./lab dem: fct_bookings VẪN 18 dòng.

Lý do: bạn vừa sửa CÔNG THỨC, nhưng 3 dòng rác đã nằm sẵn trong bảng từ
lần chạy trước. Lần chạy incremental này đi tìm dòng mới hơn dòng mới nhất
-- không có dòng nào -- nên nó không làm gì cả. Rác vẫn nguyên tại chỗ.

Đây là bài học đắt nhất của cả lab:

    SỬA CODE KHÔNG SỬA ĐƯỢC DỮ LIỆU ĐÃ LỠ SAI TRONG KHO.

Sửa code chỉ chặn cái sai TỪ GIỜ TRỞ ĐI. Phần đã sai rồi phải dựng lại
bằng tay. Việc dựng lại đó ở công ty gọi là BACKFILL:

    ./lab run-full        dbt run --full-refresh: xoá bảng, dựng lại từ đầu
    ./lab dem             giờ mới 15 dòng / 15 đơn
    ./lab test            giờ mới xanh

Nhớ kỹ cảm giác này. Ngày bạn phát hiện một model ở prod sai từ 3 tuần
trước, câu hỏi đầu tiên sếp hỏi sẽ là "backfill được không, mất bao lâu,
tốn bao nhiêu tiền". Và trên BigQuery, full-refresh một bảng lớn có thể
đắt gấp hàng trăm lần một lần chạy thường -- nên câu trả lời không hiển nhiên.

    ./lab check 4
""",
  "goi_y": [
    "Khung file models/dwh/_models.yml -- chú ý thụt lề, .yml rất khó tính:\n\nversion: 2\nmodels:\n  - name: fct_bookings\n    columns:\n      - name: booking_id\n        data_tests:\n          - unique\n          - not_null",
    "Phần (a), sửa khối config ở đầu fct_bookings.sql thành:\n\n{{\n    config(\n        materialized = 'incremental',\n        unique_key = 'booking_id',\n        incremental_strategy = 'delete+insert'\n    )\n}}",
    "Phần (b), thêm vào CUỐI file, sau khối {% endif %}:\n\nqualify row_number() over (\n            partition by booking_id\n            order by cap_nhat_luc desc\n        ) = 1\n\nĐọc lại models/dwh/stg_services.sql -- ở đó có đúng mẫu này, chỉ khác tên cột.",
    "Sửa đủ cả 2 phần rồi mà test vẫn đỏ, ./lab dem vẫn 18 dòng? Đọc lại BƯỚC 3 của đề bài. Bạn cần ./lab run-full. Dữ liệu rác cũ không tự biến mất khi bạn sửa code.",
  ],
  "dap_an": """
FILE 1 -- models/dwh/_models.yml (tạo mới)

    version: 2
    models:
      - name: fct_bookings
        description: "Bảng fact đơn đặt phòng, 1 dòng = 1 đơn (bản mới nhất)"
        columns:
          - name: booking_id
            description: "Khoá nghiệp vụ của đơn"
            data_tests:
              - unique
              - not_null

FILE 2 -- models/dwh/fct_bookings.sql, sửa khối config ở đầu:

    {{
        config(
            materialized = 'incremental',
            unique_key = 'booking_id',
            incremental_strategy = 'delete+insert'
        )
    }}

và thêm vào CUỐI file, sau khối {% endif %}:

    qualify row_number() over (
                partition by booking_id
                order by cap_nhat_luc desc
            ) = 1

SAU ĐÓ BẮT BUỘC:

    ./lab run-full        vì sửa code không sửa dữ liệu đã sai trong bảng
    ./lab test            lúc này mới xanh
""",
},

5: {
  "ten": "Idempotency: chạy 3 lần phải ra đúng một kết quả",
  "hoc": "Đây là tiêu chuẩn tối thiểu của một pipeline dùng được. Không đạt thì không dám backfill.",
  "thoi_gian": "45 phút",
  "nen": """
IDEMPOTENT LÀ TỪ NGHE ĐÁNG SỢ NHƯNG Ý RẤT ĐƠN GIẢN:

    Chạy 1 lần hay 5 lần đều ra CÙNG MỘT kết quả.

Nút gọi thang máy là idempotent -- bấm 1 lần hay 10 lần thì thang cũng chỉ
đến một lần. Nút "Đặt hàng" thì không -- bấm 5 lần ra 5 đơn.

Model của bạn phải giống nút thang máy.

VÌ SAO ĐÂY LÀ TIÊU CHUẨN TỐI THIỂU, KHÔNG PHẢI THỨ "TỐT THÌ CÓ"

Ba tình huống chắc chắn sẽ xảy ra, không phải nếu mà là khi nào:

  1. Airflow tự chạy lại khi task lỗi. Đây là hành vi mặc định, bạn không
     kiểm soát được. Task chết giữa chừng vì mạng chập -> nó chạy lại.
  2. Backfill chạy lại hàng tháng dữ liệu quá khứ.
  3. Có người bấm nhầm nút chạy lại. Sẽ có ngày đó.

Nếu chạy 2 lần ra 2 kết quả khác nhau, bạn sẽ không bao giờ dám chạy lại.
Mà pipeline nào cũng có ngày phải chạy lại. Lúc đó bạn kẹt hoàn toàn.

CÁCH KIỂM TRA, VÀ VÌ SAO BƯỚC 3 MỚI LÀ BƯỚC THẬT

  Lần 1: chạy incremental
  Lần 2: chạy incremental lần nữa, KHÔNG nạp thêm dữ liệu
         -> phải y hệt lần 1
  Lần 3: chạy --full-refresh, dựng lại bảng TỪ ĐẦU
         -> vẫn phải y hệt

Bước 3 là bước hay rớt nhất, và lý do rất đáng để hiểu:

    Chạy incremental chỉ xử lý 6 dòng mới lọt qua bộ lọc.
    Chạy full-refresh xử lý CẢ 18 dòng trong stg_bookings -- trong đó có
    những đơn xuất hiện 2 lần.

Nghĩa là: nếu ở bài 4 bạn chỉ khai báo unique_key mà không khử trùng lặp
bằng QUALIFY, thì incremental chạy đúng nhưng full-refresh sẽ nhân dòng
trở lại. Bộ lọc incremental đã vô tình che giấu lỗi -- nó chỉ đưa vào 6
dòng không trùng nhau, nên không lộ.

Đây là loại bug tệ nhất: chạy hàng ngày thì đúng, chỉ sai đúng lúc ai đó
chạy full-refresh -- thường là lúc nửa đêm đang xử lý sự cố khác.

NGUYÊN TẮC RÚT RA, ĐÁNG CHÉP VÀO SỔ:

    Điều kiện lọc incremental là để chạy NHANH, không phải để chạy ĐÚNG.
    Model phải cho kết quả đúng cả khi bỏ hết điều kiện lọc đi.

Tra thêm:  ./lab tudien idempotent | full-refresh | backfill
""",
  "de": """
Bài này không phải viết thêm code. Nó kiểm tra bản sửa ở bài 4 có thật sự
đúng hay chỉ đúng một nửa.

    ./lab check 5

Lệnh này tự làm 3 việc và đối chiếu:
    1. chạy fct_bookings 2 lần liên tiếp, không nạp thêm dữ liệu
    2. chạy dbt run --full-refresh, dựng lại bảng từ đầu
    3. so cả 3 lần: số dòng và "dấu vân tay" nội dung phải y hệt nhau

Dấu vân tay là một chuỗi ký tự tính từ toàn bộ nội dung bảng. Hai lần chạy
ra cùng dấu vân tay nghĩa là dữ liệu giống hệt nhau tới từng ô -- chặt hơn
nhiều so với chỉ so số dòng.

Muốn tự chạy tay để xem thay vì để máy làm:

    ./lab run        rồi  ./lab dem
    ./lab run        rồi  ./lab dem     (phải y hệt)
    ./lab run-full   rồi  ./lab dem     (vẫn phải y hệt)
""",
  "goi_y": [
    "Rớt ở lần 3 (full-refresh ra 18 dòng thay vì 15)? Model của bạn thiếu QUALIFY khử trùng lặp. Quay lại gợi ý 3 của bài 4.",
    "Rớt ở lần 2 (chạy lại 2 lần ra khác nhau)? Hiếm hơn -- kiểm tra unique_key có đúng tên cột booking_id không, và incremental_strategy đã khai báo chưa.",
    "Nguyên tắc để nhớ lâu: bỏ hết khối is_incremental đi, model có còn cho kết quả đúng không? Nếu không thì model đang dựa vào bộ lọc để che lỗi, chứ không phải để chạy nhanh.",
  ],
  "dap_an": "Không có code mới. Nếu rớt, quay lại bài 4 và sửa cho đủ cả phần (a) và (b) -- gần như luôn là thiếu phần (b) QUALIFY.",
},

6: {
  "ten": "Snapshot / SCD Type 2: giữ lại lịch sử thay đổi",
  "hoc": "Bảng thường ghi đè quá khứ. Câu hỏi nghiệp vụ thì lại luôn cần quá khứ.",
  "thoi_gian": "60 phút",
  "nen": """
PHẦN 1 -- HAI LOẠI BẢNG TRONG MỌI KHO DỮ LIỆU

  FACT (bảng sự việc)       chuyện đã xảy ra, có thời điểm, có số để cộng:
                            đơn hàng, giao dịch, lượt xem.
                            Rất nhiều dòng, ngày càng dài ra.
                            Đặt tên: fct_bookings

  DIMENSION (bảng mô tả)    sự vật để mô tả và cắt lát: khách hàng, khách sạn,
                            sản phẩm. Ít dòng, thay đổi chậm.
                            Đặt tên: dim_customers

Câu hỏi nghiệp vụ gần như luôn có dạng: ĐO fact, CẮT theo dimension.
"Doanh thu (fact) theo thành phố của khách (dimension) trong tháng 8."

PHẦN 2 -- VẤN ĐỀ: DIMENSION THAY ĐỔI CHẬM, NHƯNG VẪN THAY ĐỔI

Khách C002 đổi email. Bảng thường thì ghi đè -- email cũ mất vĩnh viễn.

Thử chạy để thấy:
    ./lab soi "select customer_id, email, thanh_pho from dwh.stg_customers where customer_id in ('C002','C005')"

Chỉ thấy giá trị mới. Không dấu vết gì của giá trị cũ.

Tháng sau sếp hỏi: "hồi tháng 8 mình gửi mail cho khách C002 vào địa chỉ
nào?" -- bảng hiện tại không trả lời được. Câu hỏi này rất hay gặp khi phải
đối soát với hệ thống downstream, hoặc khi khách khiếu nại.

PHẦN 3 -- CÁCH GIẢI: SCD TYPE 2

SCD = Slowly Changing Dimension, bảng mô tả thay đổi chậm. Có nhiều "Type",
nhưng Type 2 là loại bạn sẽ gặp 90% thời gian. Cách làm:

    Không ghi đè. Thêm DÒNG MỚI, và đánh dấu khoảng thời gian hiệu lực.

    customer_id  email            dbt_valid_from  dbt_valid_to
    C002         binh.tt@...      2026-07-20      2026-08-06    <- đã hết hiệu lực
    C002         binh.tran@...    2026-08-06      NULL          <- đang hiệu lực

    dbt_valid_to = NULL nghĩa là "vẫn đang đúng cho tới bây giờ".

Muốn biết email hiện tại: lọc dbt_valid_to is null.
Muốn biết email hồi 15/07: lọc valid_from <= '2026-07-15' < valid_to.

PHẦN 4 -- dbt LÀM VIỆC NÀY BẰNG LỆNH RIÊNG

    dbt snapshot        KHÔNG PHẢI dbt run

Đây là điểm hay quên. snapshot là loại tài nguyên riêng, nằm ở thư mục
snapshots/, chạy bằng lệnh riêng, và ở công ty thường có lịch chạy riêng
trong Airflow.

Từ dbt 1.9 trở đi, snapshot khai báo bằng file .yml (kiểu cũ viết trong
file .sql với khối {% snapshot %} nay đã lỗi thời -- đọc tài liệu cũ trên
mạng sẽ hay gặp kiểu cũ, đừng chép theo).

Hai chiến lược phát hiện thay đổi:

    strategy: timestamp    có cột thời gian đáng tin -> so cột đó.
                           Rẻ và chính xác. Dùng cái này khi có thể.
    strategy: check        không có cột thời gian -> so từng cột một.
                           Đắt hơn, phải liệt kê cột cần theo dõi.

PHẦN 5 -- ĐIỀU QUAN TRỌNG NHẤT, VÀ HAY BỊ HIỂU NHẦM

    Snapshot chỉ ghi nhận được thay đổi mà nó CHỨNG KIẾN.

Cách nó hoạt động là so dữ liệu hiện tại với ảnh chụp lần trước. Nếu bạn
chạy snapshot lần đầu lúc dữ liệu đã là bản mới, nó coi bản mới là điểm
khởi đầu -- và bạn chỉ có 1 dòng cho mỗi khách, không có lịch sử nào cả.

Hệ quả ngoài đời: snapshot phải chạy ĐỀU ĐẶN. Bỏ ngày nào là mất lịch sử
ngày đó, VĨNH VIỄN, không backfill lại được. Đây là một trong số rất ít
thứ trong data engineering không sửa lại được sau khi lỡ.

Vì thế ./lab check 6 sẽ tự dựng lại tình huống cho bạn: reset về đợt 1 ->
chụp ảnh -> nạp đợt 2 -> chụp ảnh lần nữa. Có 2 lần chụp mới có lịch sử.

Tra thêm:  ./lab tudien snapshot | fact | dimension
""",
  "de": """
BƯỚC 1 -- Xem tận mắt cái đang bị mất:

    ./lab soi "select customer_id, email, thanh_pho, cap_nhat_luc from dwh.stg_customers where customer_id in ('C002','C005')"

Ở đợt 2, C002 đã đổi email và C005 đã chuyển từ Hà Nội vào Đà Nẵng.
Bạn chỉ thấy giá trị mới. Giá trị cũ không còn dấu vết.

BƯỚC 2 -- Nhiệm vụ:

Tạo file  snapshots/snap_customers.yml  để dbt theo dõi thay đổi của
model stg_customers.

Cần khai báo 4 thứ (xem gợi ý 1 nếu chưa rõ cú pháp):
    - lấy dữ liệu từ đâu           (model stg_customers)
    - khoá nhận dạng một khách     (customer_id)
    - phát hiện thay đổi kiểu gì   (timestamp)
    - dựa vào cột thời gian nào    (cap_nhat_luc)

BƯỚC 3 -- Chạy và xem kết quả:

    ./lab snapshot

    ./lab soi "select customer_id, email, thanh_pho, dbt_valid_from, dbt_valid_to from dwh.snap_customers order by customer_id, dbt_valid_from"

Lần đầu chạy bạn sẽ chỉ thấy 1 dòng mỗi khách -- đúng như phần nền đã cảnh
báo, vì mới chụp ảnh có một lần. Chưa có gì để so.

BƯỚC 4 -- Để máy dựng lại tình huống đầy đủ:

    ./lab check 6

Lệnh này tự: reset về đợt 1 -> chạy snapshot (ảnh chụp 1) -> nạp đợt 2 ->
chạy snapshot lần nữa (ảnh chụp 2). Có 2 ảnh mới có lịch sử để so.

Xong rồi xem lại:

    ./lab soi "select customer_id, email, dbt_valid_from, dbt_valid_to from dwh.snap_customers where customer_id='C002' order by dbt_valid_from"

Hai dòng: email cũ đã có ngày hết hiệu lực, email mới có dbt_valid_to là NULL.
""",
  "goi_y": [
    "Khung file snapshots/snap_customers.yml:\n\nsnapshots:\n  - name: snap_customers\n    relation: ref('stg_customers')\n    config:\n      schema: dwh\n      unique_key: customer_id\n      strategy: timestamp\n      updated_at: cap_nhat_luc",
    "Chú ý 2 chỗ hay sai: `relation` chứ không phải `select` (đó là cú pháp cũ), và `updated_at` phải trỏ đúng tên cột thời gian trong stg_customers -- ở đây cột đó tên cap_nhat_luc chứ không phải updated_at.",
    "Chạy bằng `./lab snapshot` (tức dbt snapshot), KHÔNG phải `./lab run`. dbt run bỏ qua hoàn toàn thư mục snapshots/.",
  ],
  "dap_an": """
snapshots/snap_customers.yml:

    snapshots:
      - name: snap_customers
        relation: ref('stg_customers')
        config:
          schema: dwh
          unique_key: customer_id
          strategy: timestamp
          updated_at: cap_nhat_luc

Sau khi chạy đủ 2 lần (trước và sau khi nạp đợt 2), C002 có 2 dòng:
    dòng cũ : email binh.tt@example.com,       dbt_valid_to = lúc phát hiện đổi
    dòng mới: email binh.tran@vinpearl-...,    dbt_valid_to = NULL (đang hiệu lực)

4 cột dbt_* là do dbt tự thêm, bạn không khai báo:
    dbt_valid_from  dòng này bắt đầu đúng từ lúc nào
    dbt_valid_to    hết đúng từ lúc nào (NULL = vẫn đang đúng)
    dbt_scd_id      mã nội bộ của dbt cho từng phiên bản
    dbt_updated_at  lúc dbt ghi nhận
""",
},

7: {
  "ten": "Cùng bộ code, đổi engine sang BigQuery",
  "hoc": "Chốt lại cả lab: dbt lo logic, engine lo lưu trữ và chi phí. Và ranh giới nằm ở đâu.",
  "thoi_gian": "90 phút (cần tài khoản BigQuery sandbox)",
  "nen": """
BÀI NÀY TRẢ LỜI CÂU HỎI BAN ĐẦU CỦA BẠN: học trên DuckDB thì có dùng được
cho BigQuery không, và phần nào thì KHÔNG.

RANH GIỚI CẦN THUỘC

    dbt lo   LOGIC và THỨ TỰ CHẠY
    engine lo LƯU TRỮ, TỐC ĐỘ và CHI PHÍ

Mọi thứ bạn học ở bài 1-6 nằm bên trái ranh giới, nên chuyển sang BigQuery
gần như nguyên vẹn: ref, source, lineage, materialization, incremental,
unique_key, test, snapshot -- giống hệt.

Ba thứ nằm bên phải ranh giới, DuckDB không dạy được:

1) PHƯƠNG NGỮ SQL (dialect)

   Mỗi engine nói SQL hơi khác nhau. Cùng một ý, viết khác:

       Tính số ngày giữa 2 mốc:
         DuckDB    date_diff('day', ngay_dau, ngay_cuoi)
         BigQuery  date_diff(ngay_cuoi, ngay_dau, DAY)    <- đảo cả thứ tự

   dbt không che được chuyện này. Cách repo thật xử lý là dùng macro có sẵn
   tự sinh đúng phương ngữ:  {{ dbt.datediff('a', 'b', 'day') }}

   Không cần thuộc khác biệt. Chỉ cần BIẾT LÀ CÓ, để khi đổi engine thì
   biết đường mà tra.

2) PARTITION VÀ CLUSTER -- HAI DÒNG CONFIG ĐỔI CẢ HOÁ ĐƠN

   BigQuery tính tiền theo LƯỢNG DỮ LIỆU CÂU QUERY PHẢI ĐỌC (bytes scanned),
   không theo thời gian chạy. Đọc ít byte = trả ít tiền.

     PARTITION  chia bảng thành nhiều ngăn theo một cột, gần như luôn là ngày.
                Query lọc theo cột đó -> BigQuery chỉ mở đúng ngăn liên quan.

                Bảng 3 năm dữ liệu, query 1 ngày:
                  không partition -> đọc cả 3 năm
                  có partition    -> đọc 1 ngày, rẻ hơn khoảng 1000 lần

     CLUSTER    trong mỗi ngăn, sắp xếp theo vài cột hay dùng để lọc.
                Giúp bỏ qua bớt phần không cần đọc.

   LƯU Ý DỄ NHẦM: "partition" ở đây KHÔNG liên quan gì tới "partition by"
   trong window function ở bài 4. Hai khái niệm hoàn toàn khác nhau, trùng
   tên hoàn toàn ngẫu nhiên.

3) NHÌN THẤY CHI PHÍ TRƯỚC KHI TIÊU

   Console BigQuery hiện dòng "This query will process 4.2 GB when run"
   TRƯỚC khi bạn bấm chạy. Đó không phải thông tin tham khảo -- đó là hoá đơn.

   Ba thói quen nên có từ tuần đầu ở công ty:
     - luôn liếc con số đó trước khi bấm chạy
     - đừng select * (BigQuery là dạng cột, bỏ cột là bỏ luôn tiền)
     - luôn lọc theo cột partition khi có thể

Tra thêm:  ./lab tudien dialect | partition | bytes
""",
  "de": """
Bài này không chấm tự động và không bắt buộc. Làm sau khi xong bài 1-6.

BƯỚC 1 -- Tạo BigQuery sandbox
    console.cloud.google.com -- miễn phí, không cần thẻ, 1TB query/tháng.
    Quá đủ cho lab này.

BƯỚC 2 -- Cài adapter và mở khoá target bq
        ./venv/bin/pip install dbt-bigquery
        gcloud auth application-default login
    Rồi mở profiles.yml, bỏ comment khối `bq:`, điền project của bạn.

    (profiles.yml là file chứa thông tin kết nối -- xem ./lab tudien profiles)

BƯỚC 3 -- Đưa dữ liệu lên
    Nạp 3 file CSV trong data/ lên BigQuery vào dataset tên `lake`
    (Console -> Create table -> Upload).

BƯỚC 4 -- Chạy CHÍNH BỘ MODEL ĐÓ, không sửa một dòng
        ./venv/bin/dbt run --target bq

QUAN SÁT

  a) Phần lớn model chạy thẳng. ref, source, test, snapshot, incremental --
     giống hệt. Đó là giá trị thật của dbt, và là lý do lab này chạy trên
     DuckDB mà vẫn dùng được.

  b) date_diff sẽ báo lỗi -- BigQuery đảo thứ tự tham số. Sửa tay, hoặc
     thử dùng {{ dbt.datediff(...) }} để chạy được trên cả hai.

  c) incremental_strategy 'delete+insert' đổi sang 'merge' cho hợp BigQuery.

  d) THÊM PARTITION VÀ ĐO CHI PHÍ -- phần quan trọng nhất của bài này.

     Thêm vào config của fct_bookings:

         partition_by = {'field': 'ngay_nhan_phong', 'data_type': 'date'},
         cluster_by = ['hotel_code']

     Rồi vào Console chạy một câu select có lọc theo ngay_nhan_phong, xem
     dòng "This query will process X bytes" TRƯỚC và SAU khi có partition.

     Con số chênh lệch đó chính là tiền. Đây là thứ không bao giờ học được
     ở DuckDB, và cũng là thứ rất ít người mới để ý tới -- nên để ý là dễ
     được ghi nhận.

Xong thì tự đánh dấu:  ./lab xong 7
""",
  "goi_y": [
    "Không có sandbox cũng nên đọc hết phần nền và phần quan sát (b)(c)(d). Biết trước ranh giới ở đâu đã có giá trị, kể cả chưa tự tay chạy.",
    "Lỗi xác thực khi chạy --target bq: kiểm tra đã chạy `gcloud auth application-default login` chưa, và project trong profiles.yml có đúng project sandbox của bạn không.",
    "Muốn tách phương ngữ SQL cho gọn: dbt có sẵn macro dbt.datediff(), dbt.dateadd(), dbt.current_timestamp()... chạy được trên mọi engine. Đó là cách repo thật xử lý chuyện này.",
  ],
  "dap_an": "Bài mở, không có đáp án cố định. Điểm cần đạt: chạy được `dbt run --target bq` với cùng bộ model, và tự đo được chênh lệch bytes scanned trước/sau khi thêm partition.",
},
}
