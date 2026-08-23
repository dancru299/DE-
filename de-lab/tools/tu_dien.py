# -*- coding: utf-8 -*-
"""Từ điển thuật ngữ. Tra bằng: ./lab tudien <từ>"""

TU_DIEN = {
"model": """MODEL = MỘT FILE .sql TRONG THƯ MỤC models/

Không có gì huyền bí. Một model là một file, bên trong là một câu SELECT.
dbt lấy câu SELECT đó, bọc thêm "tạo bảng từ kết quả này", rồi gửi xuống database.

  file  models/dwh/stg_bookings.sql
  -> tạo ra bảng/view tên  stg_bookings  trong database

TÊN FILE CHÍNH LÀ TÊN BẢNG. Đổi tên file = đổi tên bảng.
Một file = một bảng. Muốn 5 bảng thì viết 5 file.""",

"engine": """ENGINE = NƠI DỮ LIỆU THẬT SỰ NẰM VÀ PHÉP TÍNH THẬT SỰ CHẠY

BigQuery, DuckDB, ClickHouse, Postgres, Snowflake -- tất cả đều là engine.
Chúng lưu dữ liệu và thực hiện câu SQL.

dbt KHÔNG phải engine. dbt không lưu một byte dữ liệu nào và không tính
một phép tính nào. Nó soạn câu SQL rồi nhờ engine chạy hộ.

  dbt  = người viết đơn hàng
  engine = nhà bếp nấu món

Ở công ty bạn engine là BigQuery. Trong lab này engine là DuckDB.
Người viết đơn (dbt) giống hệt nhau, chỉ đổi nhà bếp.""",

"compile": """COMPILE = BIÊN DỊCH: BIẾN FILE BẠN VIẾT THÀNH SQL THUẦN

File bạn viết có những chỗ trống kiểu {{ ref('stg_bookings') }}.
Database không hiểu ký hiệu đó. Nên trước khi gửi đi, dbt phải điền vào.

  Bạn viết   :  select * from {{ ref('stg_bookings') }}
  dbt compile:  select * from "lab"."dwh"."stg_bookings"
                                  ^ đã thành tên bảng thật

Giống thư mẫu: "Kính gửi anh/chị {{ho_ten}}" -> điền tên thật trước khi gửi.

Kết quả compile nằm ở thư mục  target/compiled/
Xem nhanh:  ./lab sql <tên model>""",

"jinja": """JINJA = {{ }} VÀ {% %} -- PHẦN KHÔNG PHẢI SQL TRONG FILE CỦA BẠN

Hai ký hiệu, hai việc khác nhau:

  {{ ... }}   ĐIỀN GIÁ TRỊ VÀO ĐÂY
              {{ ref('stg_bookings') }} -> "lab"."dwh"."stg_bookings"

  {% ... %}   CÂU LỆNH ĐIỀU KHIỂN, tự nó không in ra gì
              {% if is_incremental() %} ... {% endif %}
              nghĩa là: chỉ chèn đoạn ở giữa vào khi điều kiện đúng

Cả hai BIẾN MẤT sau khi compile. Database không bao giờ nhìn thấy chúng.

BẪY: Jinja không phân biệt đâu là comment SQL. Viết {% if %} trong dòng
comment "--" thì nó vẫn cố chạy và báo lỗi. Muốn viết ra để giải thích
thì phải bọc trong {% raw %} ... {% endraw %}.""",

"ref": """ref() = "LẤY DỮ LIỆU TỪ MODEL TÊN X"

  from {{ ref('stg_bookings') }}

thay vì viết thẳng

  from dwh.stg_bookings

Hai câu cho ra kết quả y hệt. Nhưng ref() đổi thêm hai chuyện:

1. dbt BIẾT model này phụ thuộc model kia -> tự sắp thứ tự chạy.
   Viết tên cứng thì dbt mù, có thể chạy bảng con trước bảng cha -> vỡ.

2. Đổi tên hoặc đổi schema chỉ cần sửa một chỗ. Tên cứng thì phải đi
   tìm sửa từng file, sót một cái là hỏng lúc nửa đêm.

Đây là lý do người ta nói dbt "tự sinh ra lineage": nó không đoán, nó chỉ
đọc xem bạn ref() cái gì.""",

"source": """source() = "LẤY DỮ LIỆU TỪ BẢNG KHÔNG PHẢI DO dbt TẠO"

Phân biệt với ref():

  source()  bảng do hệ thống KHÁC đổ vào: Kafka Connect, CDC, job nạp file.
            dbt chỉ ĐỌC, không bao giờ ghi vào đó.
  ref()     bảng do CHÍNH dbt tạo ra từ một model khác.

Phải khai báo source trong file .yml trước khi dùng:

  sources:
    - name: lake
      schema: lake
      tables:
        - name: bookings

rồi mới gọi được  {{ source('lake', 'bookings') }}

Khai báo hơi phiền nhưng đổi lại: dbt biết ranh giới hệ thống nằm ở đâu,
và lineage của bạn bắt đầu từ đúng chỗ.""",

"materialized": """MATERIALIZED = "VẬT CHẤT HOÁ": KẾT QUẢ CÂU SELECT SẼ THÀNH CÁI GÌ

Bạn viết một câu SELECT. Nhưng lưu nó dưới dạng nào?

  view         Lưu CÂU HỎI, không lưu kết quả.
               Mỗi lần ai đó đọc thì tính lại từ đầu.
               -> luôn mới nhất, không tốn chỗ, nhưng đọc chậm nếu phức tạp.

  table        Lưu KẾT QUẢ thật thành bảng.
               -> đọc nhanh, nhưng phải chạy lại dbt mới cập nhật.

  incremental  Như table, nhưng mỗi lần chạy chỉ xử lý phần mới rồi thêm vào.
               -> dùng cho bảng to, xem mục "incremental".

Ví von: view là CÔNG THỨC NẤU ĂN, table là MÓN ĐÃ NẤU SẴN để tủ lạnh.
Công thức luôn đúng nhưng phải nấu mới ăn được; món nấu sẵn ăn ngay
nhưng có thể đã nguội.

Khai báo trong config của model, hoặc trong dbt_project.yml cho cả thư mục.""",

"incremental": """INCREMENTAL = MỖI LẦN CHẠY CHỈ XỬ LÝ PHẦN MỚI

Bảng đơn hàng có 500 triệu dòng. Mỗi ngày thêm 200 nghìn dòng mới.
Chạy lại cả 500 triệu dòng mỗi ngày là vô lý -- chậm và trên BigQuery
là đốt tiền thật.

incremental nghĩa là:
  lần chạy ĐẦU  -> dựng cả bảng, đủ 500 triệu dòng
  lần chạy SAU  -> chỉ lấy 200 nghìn dòng mới, ghi thêm vào

Làm sao dbt biết "phần mới" là gì? BẠN phải nói cho nó, bằng khối:

  {% if is_incremental() %}
    where cap_nhat_luc > (select max(cap_nhat_luc) from {{ this }})
  {% endif %}

  {{ this }} = chính cái bảng đang được dựng, phiên bản đang có sẵn.

is_incremental() đúng khi: bảng đã tồn tại VÀ bạn không chạy --full-refresh.

CẢNH BÁO: điều kiện lọc này chỉ để chạy NHANH. Nó không làm cho model
chạy ĐÚNG. Xem mục "unique_key" và "idempotent".""",

"unique_key": """unique_key = CỘT DÙNG ĐỂ NHẬN RA "ĐƠN NÀY TÔI ĐÃ CÓ RỒI"

Không khai báo unique_key thì incremental chỉ biết THÊM.
Một đơn bị sửa -> hệ nguồn gửi lại đơn đó -> dbt thêm dòng nữa -> 2 dòng
cho cùng một đơn. Không ai báo lỗi. Pipeline vẫn xanh.

  config(
      materialized = 'incremental',
      unique_key = 'booking_id',
      incremental_strategy = 'delete+insert'
  )

Có unique_key rồi, dbt biết: dòng mới nào trùng booking_id với dòng cũ thì
phải THAY chứ không THÊM.

incremental_strategy = cách thay:
  delete+insert  xoá các dòng cũ trùng khoá, rồi chèn lô mới vào (2 câu lệnh)
  merge          một câu MERGE làm cả hai việc (BigQuery hay dùng cái này)
  append         cứ thêm, không quan tâm trùng (mặc định khi không có unique_key)

Cùng ý tưởng, khác câu lệnh sinh ra. Engine nào hỗ trợ cái nào thì tra doc.""",

"full-refresh": """--full-refresh = XOÁ BẢNG, DỰNG LẠI TỪ ĐẦU

  dbt run --full-refresh          (trong lab: ./lab run-full)

Với model incremental, lệnh này bỏ qua khối is_incremental(), quét lại
TOÀN BỘ dữ liệu nguồn và dựng bảng mới hoàn toàn.

KHI NÀO CẦN:
  - Vừa sửa logic của model. Dữ liệu cũ trong bảng vẫn là dữ liệu sai --
    sửa code KHÔNG tự sửa dữ liệu đã lỡ ghi.
  - Vừa thêm/bớt cột.
  - Nghi ngờ bảng đã lệch so với nguồn.

NGUY HIỂM Ở CHỖ: trên BigQuery, full-refresh một bảng lớn quét lại toàn bộ
dữ liệu -> hoá đơn có thể gấp hàng trăm lần một lần chạy thường.
Ở công ty, ước tính chi phí TRƯỚC khi bấm, và hỏi trước nếu bảng lớn.""",

"backfill": """BACKFILL = CHẠY LẠI PIPELINE CHO DỮ LIỆU QUÁ KHỨ

Ví dụ: hôm nay bạn phát hiện model tính sai từ ngày 1/6. Sửa code xong,
dữ liệu từ 1/6 tới nay vẫn sai. Phải chạy lại cho từng ngày trong khoảng
đó -- đấy là backfill.

Ba câu hỏi luôn bị hỏi trước khi cho backfill:
  1. Chạy lại bao nhiêu ngày?
  2. Mất bao lâu, tốn bao nhiêu tiền?
  3. Trong lúc chạy lại, hệ thống downstream đọc bảng đó có bị ảnh hưởng không?

Backfill CHỈ AN TOÀN nếu model idempotent. Nếu chạy lại làm nhân dòng thì
backfill biến một lỗi thành thảm hoạ. Xem mục "idempotent".""",

"idempotent": """IDEMPOTENT = CHẠY 1 LẦN HAY 5 LẦN ĐỀU RA CÙNG MỘT KẾT QUẢ

Bấm nút gọi thang máy 1 lần hay 10 lần thì thang cũng chỉ đến 1 lần --
nút thang máy là idempotent. Còn nút "Đặt hàng" bấm 5 lần ra 5 đơn thì không.

Vì sao đây là tiêu chuẩn tối thiểu của một pipeline:
  - Airflow tự chạy lại khi task lỗi (retry). Bạn không kiểm soát được.
  - Backfill chạy lại hàng tháng dữ liệu.
  - Có người bấm nhầm nút chạy lại.

Nếu chạy 2 lần ra 2 kết quả khác nhau, bạn sẽ không bao giờ dám chạy lại.
Mà pipeline nào cũng có ngày phải chạy lại.

Cách tự kiểm tra: chạy 2 lần liên tiếp không nạp thêm dữ liệu, số dòng và
nội dung phải y hệt. Rồi chạy --full-refresh, cũng phải y hệt.
Bước cuối hay rớt nhất -- xem bài 5.""",

"window": r"""WINDOW FUNCTION = HÀM NHÌN SANG CÁC DÒNG HÀNG XÓM MÀ KHÔNG GỘP DÒNG LẠI

Khác biệt cốt lõi so với GROUP BY:

  GROUP BY          5 dòng vào -> 1 dòng ra (gộp lại, mất chi tiết)
  window function   5 dòng vào -> 5 dòng ra (giữ nguyên, thêm thông tin)

Cú pháp:

  row_number() over (partition by booking_id order by cap_nhat_luc desc)
  \_________/        \_______________________/  \___________________/
   hàm                chia thành từng nhóm       trong nhóm, sắp thế nào

Đọc thành lời: "chia các dòng thành từng nhóm theo booking_id; trong mỗi
nhóm sắp theo thời gian cập nhật GIẢM DẦN; rồi đánh số 1,2,3... cho từng dòng."

Kết quả: dòng số 1 của mỗi nhóm = dòng MỚI NHẤT của đơn đó.
Giữ lại dòng số 1, bỏ phần còn lại -> đã khử trùng lặp.

partition by ở đây KHÔNG liên quan gì tới partition của BigQuery.
Trùng tên, khác hẳn nghĩa. Xem mục "partition".""",

"qualify": """QUALIFY = MỆNH ĐỀ LỌC THEO KẾT QUẢ CỦA WINDOW FUNCTION

Bạn muốn "chỉ giữ dòng số 1 của mỗi nhóm". Tưởng là viết được:

  where row_number() over (...) = 1        <-- SAI, không chạy được

Không được, vì database chạy WHERE TRƯỚC, tính window function SAU.
Lúc WHERE chạy thì chưa có số thứ tự nào để mà lọc.

Cách cũ (dài, phải bọc thêm một tầng):

  select * from (
      select *, row_number() over (...) as rn
      from bang
  ) where rn = 1

Cách gọn (QUALIFY, có ở cả DuckDB và BigQuery):

  select * from bang
  qualify row_number() over (...) = 1

Cùng kết quả, ít hơn một tầng lồng và không phải bịa tên cột rn.
Vị trí trong câu: sau WHERE, sau GROUP BY / HAVING, trước ORDER BY.""",

"test": """dbt test = CÂU SQL ĐI TÌM DÒNG SAI

Đây là chỗ hay hiểu ngược. Test của dbt không kiểm tra "có đúng không".
Nó CHẠY MỘT CÂU SELECT ĐỂ TÌM DÒNG VI PHẠM.

  tìm được 0 dòng  -> PASS (không có gì sai)
  tìm được N dòng  -> FAIL N (có N chỗ sai)

Bốn test có sẵn, khai báo trong file .yml:

  unique         cột này có giá trị nào bị lặp không
  not_null       cột này có ô nào trống không
  accepted_values  cột này có giá trị nào ngoài danh sách cho phép không
  relationships  mọi customer_id ở bảng này có tồn tại ở bảng khách hàng không
                 (dân database gọi là khoá ngoại)

  models:
    - name: fct_bookings
      columns:
        - name: booking_id
          data_tests:
            - unique
            - not_null

Chạy: dbt test  (trong lab: ./lab test)

Khi FAIL, dbt in ra luôn câu SQL nó đã dùng -- copy chạy lại là thấy đúng
những dòng nào sai. Đây là thứ bạn sẽ đọc mỗi ngày ở công ty.""",

"snapshot": """SNAPSHOT / SCD TYPE 2 = GIỮ LẠI LỊCH SỬ THAY ĐỔI THAY VÌ GHI ĐÈ

Khách C002 đổi email. Bảng thường thì ghi đè -- email cũ mất vĩnh viễn.
Tháng sau sếp hỏi "hồi tháng 8 mình gửi mail cho khách này vào địa chỉ nào?"
-> không trả lời được.

SCD Type 2 (Slowly Changing Dimension loại 2) giải quyết bằng cách: không
ghi đè, mà THÊM DÒNG MỚI và đánh dấu khoảng thời gian hiệu lực của từng dòng.

  customer_id  email              dbt_valid_from   dbt_valid_to
  C002         binh.tt@...        2026-07-20       2026-08-06     <- đã hết hiệu lực
  C002         binh.tran@...      2026-08-06       NULL           <- đang hiệu lực

  dbt_valid_to = NULL nghĩa là "vẫn đang đúng tới bây giờ".

dbt làm việc này bằng lệnh riêng:  dbt snapshot  (KHÔNG phải dbt run).

QUAN TRỌNG: snapshot chỉ ghi nhận được thay đổi mà nó CHỨNG KIẾN. Nó so
dữ liệu hiện tại với ảnh chụp lần trước. Bỏ chạy ngày nào là mất lịch sử
ngày đó, và không backfill lại được. Vì vậy snapshot phải chạy đều đặn.

"Dimension" = bảng mô tả sự vật (khách hàng, khách sạn, sản phẩm).
"Fact" = bảng ghi sự việc xảy ra (đơn hàng, giao dịch). Xem mục "fact".""",

"fact": """FACT VÀ DIMENSION = HAI LOẠI BẢNG CƠ BẢN TRONG KHO DỮ LIỆU

  FACT (bảng sự việc)      chuyện đã xảy ra, có thời điểm, thường có số
                           để cộng/đếm: đơn hàng, giao dịch, lượt xem.
                           Rất nhiều dòng, ngày càng dài ra.
                           Đặt tên: fct_bookings, fct_orders

  DIMENSION (bảng mô tả)   sự vật để mô tả và lọc: khách hàng, khách sạn,
                           sản phẩm, ngày tháng.
                           Ít dòng hơn, thay đổi chậm.
                           Đặt tên: dim_customers, dim_hotels

Câu hỏi nghiệp vụ thường có dạng: ĐO fact, CẮT theo dimension.
"Doanh thu (fact) theo thành phố của khách (dimension) trong tháng 8."

Vì dimension thay đổi chậm mà vẫn thay đổi (khách chuyển thành phố), nên
mới sinh ra khái niệm SCD -- xem mục "snapshot".""",

"grain": """GRAIN = "MỘT DÒNG TRONG BẢNG NÀY LÀ CÁI GÌ?"

Câu hỏi phải trả lời TRƯỚC khi viết dòng SQL đầu tiên. Trả lời sai thì
mọi con số phía sau đều sai, và sai một cách rất khó phát hiện.

  "1 dòng = 1 đơn"                     -> 15 dòng cho 15 đơn
  "1 dòng = 1 đơn × 1 dịch vụ"         -> đơn có 2 dịch vụ sẽ chiếm 2 dòng

Cùng dữ liệu, hai grain khác nhau. Nếu bạn tưởng là grain thứ nhất mà thực
tế là thứ hai, rồi đi cộng tổng tiền, thì đơn có 2 dịch vụ bị tính 2 lần.
Báo cáo doanh thu sai. Không ai báo lỗi.

Cách kiểm tra grain trong 10 giây:

  select count(*), count(distinct booking_id) from bang;

Hai số bằng nhau -> grain đúng là 1 dòng/đơn.
Lệch nhau -> grain của bạn không phải như bạn nghĩ. (Đây chính là việc
mà lệnh ./lab dem đang làm cho bạn.)

Thói quen nên có: viết grain vào description của mọi model bạn tạo.""",

"cdc": """CDC (CHANGE DATA CAPTURE) = BẮT MỌI THAY ĐỔI Ở DATABASE NGUỒN

Vấn đề: hệ thống bán hàng có database riêng. Bạn cần dữ liệu đó trong kho
nhưng không được phép query thẳng vào (query nặng sẽ làm chậm hệ thống bán
hàng, khách không đặt được phòng).

CDC là công cụ đọc NHẬT KÝ GHI của database nguồn -- cuốn sổ mà database
tự ghi lại mọi lệnh thêm/sửa/xoá. Mỗi thay đổi thành một dòng gửi sang kho.

Hệ quả quan trọng, và là thứ toàn bộ bài 3-4-5 xoay quanh:

  Sửa một đơn ở hệ nguồn -> CDC gửi sang MỘT DÒNG MỚI, không ghi đè dòng cũ.
  Tầng lake vì thế có NHIỀU DÒNG cho cùng một đơn, mỗi dòng là một phiên bản.

Nên tầng lake gần như luôn "trùng khoá" -- đó là bình thường, đúng thiết kế.
Việc chọn ra phiên bản mới nhất là việc của tầng dwh, và đó là việc của BẠN.

Bên bạn: Kafka Connect làm CDC, đẩy qua Kafka.""",

"append-only": """APPEND-ONLY = CHỈ ĐƯỢC THÊM, KHÔNG SỬA, KHÔNG XOÁ

Cách tầng lake hoạt động. Dữ liệu chảy vào thì nối thêm vào cuối, không bao
giờ động vào dòng đã có.

Vì sao thiết kế như vậy:
  - Ghi thêm thì nhanh và không bao giờ tranh chấp với người đang đọc.
  - Giữ được nguyên trạng lịch sử. Nghi ngờ số liệu thì lần lại được.
  - Dựng lại toàn bộ kho từ lake khi cần.

Cái giá phải trả: lake có nhiều phiên bản của cùng một bản ghi, và mọi tầng
phía sau phải tự biết chọn phiên bản đúng. Xem mục "cdc" và "qualify".""",

"lake": """LAKE / DWH / MART = BA TẦNG CỦA KHO DỮ LIỆU

Cùng một dòng dữ liệu đi qua ba trạm, mỗi trạm một nhiệm vụ:

  LAKE   Nguyên trạng, y như nguồn gửi sang. Không sửa gì cả.
         Sai cũng để nguyên -- vì đây là bản gốc để đối chiếu về sau.
         Không do dbt tạo. dbt đọc qua source().

  DWH    Đã làm sạch: ép kiểu dữ liệu, thống nhất tên cột, khử trùng lặp,
         ghép các nguồn lại. Ai trong công ty cũng dùng được tầng này.
         Trong lab: stg_* (làm sạch 1-1) và fct_*/dim_* (đã xử lý).

  MART   Đã lọc, đã gộp, phục vụ MỘT nhu cầu cụ thể của business.
         Người đọc bảng này không cần biết gì về hai tầng dưới.

Vì sao không làm thẳng từ lake ra mart cho nhanh: vì mart thứ hai, thứ ba
sẽ phải chép lại toàn bộ logic làm sạch. Sửa một chỗ phải sửa mười nơi.

Nơi khác có thể gọi là bronze/silver/gold, hoặc raw/staging/marts.
Cùng một ý tưởng. Bên bạn gọi là lake / dwh / mart.""",

"cte": """CTE (with ... as) = ĐẶT TÊN CHO MỘT KẾT QUẢ TRUNG GIAN

  with don as (
      select * from fct_bookings where trang_thai = 'CONFIRMED'
  ),
  dua_don as (
      select * from stg_services where loai_dich_vu = 'SHUTTLE'
  )
  select * from don join dua_don on ...

"don" và "dua_don" là tên tạm, chỉ tồn tại trong câu lệnh này. Giống như
đặt biến tạm khi viết code, để không phải nhồi mọi thứ vào một câu.

Lợi ích thật sự không phải là chạy nhanh hơn (thường là như nhau) mà là
ĐỌC ĐƯỢC. Câu SQL 80 dòng lồng 4 tầng subquery thì không ai review nổi,
kể cả bạn sau 2 tuần.

Quy ước hay gặp trong dbt: mỗi CTE đầu file là một nguồn dữ liệu, các CTE
sau là từng bước biến đổi, câu select cuối cùng là kết quả.""",

"join": """JOIN = GHÉP HAI BẢNG THEO MỘT CỘT CHUNG

  from don d
  inner join dua_don dd on d.booking_id = dd.booking_id

Đọc: với mỗi dòng ở bảng don, tìm dòng ở bảng dua_don có cùng booking_id,
ghép lại thành một dòng dài hơn.

Hai loại dùng 95% thời gian:

  INNER JOIN  chỉ giữ dòng CÓ Ở CẢ HAI BÊN.
              Đơn không có dịch vụ đưa đón -> biến mất khỏi kết quả.
              Dùng khi "thiếu bên kia thì dòng này vô nghĩa".

  LEFT JOIN   giữ HẾT bên trái. Bên phải không tìm thấy thì để NULL.
              Đơn không có tên khách -> vẫn còn đơn, cột tên trống.
              Dùng khi "thiếu bên kia vẫn phải giữ dòng lại".

QUY TẮC AN TOÀN: mất một đơn hàng là mất tiền. Khi phân vân, LEFT JOIN
rồi thêm test not_null để biết có bao nhiêu dòng bị thiếu -- còn hơn dùng
INNER JOIN rồi âm thầm mất dòng mà không ai biết.

BẪY NHÂN DÒNG: nếu bên phải có 2 dòng cùng booking_id, bạn nhận về 2 dòng
thay vì 1. Join xong luôn kiểm tra lại số dòng. Xem mục "grain".""",

"partition": """PARTITION VÀ CLUSTER (BIGQUERY) = HAI DÒNG CONFIG ĐỔI CẢ HOÁ ĐƠN

BigQuery tính tiền theo LƯỢNG DỮ LIỆU CÂU QUERY PHẢI ĐỌC, không theo thời
gian chạy. Đọc ít byte = trả ít tiền.

  PARTITION  Chia bảng thành nhiều ngăn theo một cột, gần như luôn là ngày.
             Query có điều kiện lọc theo cột đó -> BigQuery chỉ mở đúng ngăn
             liên quan, các ngăn khác không đọc, không tính tiền.

             Bảng 3 năm dữ liệu, query 1 ngày:
               không partition -> đọc cả 3 năm
               có partition    -> đọc 1 ngày, rẻ hơn ~1000 lần

  CLUSTER    Trong mỗi ngăn, sắp xếp dữ liệu theo vài cột hay dùng để lọc
             (hotel_code, customer_id...). Giúp bỏ qua bớt phần không cần đọc.

  config(
      partition_by = {'field': 'ngay_nhan_phong', 'data_type': 'date'},
      cluster_by = ['hotel_code']
  )

LƯU Ý: partition ở đây KHÔNG liên quan gì tới "partition by" trong window
function. Trùng tên hoàn toàn ngẫu nhiên. Xem mục "window".

DuckDB không có khái niệm này -- đây là phần bắt buộc phải học trên
BigQuery sandbox (bài 7).""",

"bytes": """BYTES SCANNED = ĐƠN VỊ TÍNH TIỀN CỦA BIGQUERY

Trước khi chạy, Console BigQuery hiện dòng:
  "This query will process 4.2 GB when run"

Đó không phải thông tin tham khảo. Đó là hoá đơn (BigQuery tính tiền theo
lượng byte quét, hiện khoảng vài đô một TB -- kiểm tra bảng giá hiện hành).

Ba thói quen nên có từ tuần đầu:
  1. Luôn liếc con số đó trước khi bấm chạy. Thấy quá lớn thì dừng lại nghĩ.
  2. select *  quét MỌI cột. Chỉ lấy cột cần -> BigQuery là dạng cột nên
     bỏ cột là bỏ luôn tiền.
  3. Luôn lọc theo cột partition khi có thể.

"Dry run" = nhờ BigQuery ước tính mà không thật sự chạy, không mất tiền.
Trong bq CLI:  bq query --dry_run --use_legacy_sql=false '<câu sql>'

Đây là phần rất ít người mới để ý -- nên để ý là dễ được ghi nhận.""",

"lineage": """LINEAGE = SƠ ĐỒ "AI LẤY DỮ LIỆU TỪ AI"

  lake.bookings -> stg_bookings -> fct_bookings -> mart_don_dua_don

dbt tự vẽ ra sơ đồ này, KHÔNG phải bằng cách phân tích SQL của bạn, mà đơn
giản là đọc xem bạn viết ref() và source() ở đâu. Chỉ vậy thôi.

Ba việc lineage giải quyết:
  1. Thứ tự chạy. dbt tự biết phải dựng stg_bookings trước fct_bookings.
  2. Đánh giá ảnh hưởng. Sửa một model, biết ngay những bảng nào phía sau
     có thể vỡ theo.
  3. Truy nguyên. Số trên dashboard sai -> lần ngược về tận nguồn.

Xem trong lab: ./lab cay
Ở công ty: dbt docs có sơ đồ bấm được, tại tab Project.

Hệ quả: viết tên bảng cứng thay vì ref() là bạn CHỌC MÙ dbt ở đúng chỗ đó.
Sơ đồ vẫn vẽ ra, nhưng thiếu một mũi tên, và không ai biết là thiếu.""",

"dialect": """DIALECT / PHƯƠNG NGỮ SQL = MỖI ENGINE NÓI SQL HƠI KHÁC NHAU

SQL có chuẩn chung, nhưng mỗi engine thêm bớt của riêng mình. Cùng một ý,
viết khác nhau:

  Tính số ngày giữa hai mốc:
    DuckDB    date_diff('day', ngay_dau, ngay_cuoi)
    BigQuery  date_diff(ngay_cuoi, ngay_dau, DAY)     <- đảo cả thứ tự!

Đây là phần dbt KHÔNG che giấu được cho bạn. dbt lo logic và thứ tự chạy;
cú pháp SQL vẫn là chuyện giữa bạn và engine.

Cách repo thật xử lý: dùng macro có sẵn của dbt, tự sinh đúng phương ngữ:
  {{ dbt.datediff('ngay_dau', 'ngay_cuoi', 'day') }}

Không cần thuộc lòng khác biệt. Chỉ cần BIẾT LÀ CÓ khác biệt, để khi đổi
engine thì biết đường mà tìm.""",

"schema": """SCHEMA = NGĂN CHỨA BẢNG TRONG DATABASE

Một database chứa nhiều schema, mỗi schema chứa nhiều bảng. Đường dẫn đầy
đủ tới một bảng có ba tầng:

  lab       .  dwh     .  stg_bookings
  database     schema     bảng

Trong lab này: schema lake, dwh, mart -- đúng ba tầng kho dữ liệu.
Trên BigQuery từ này gọi là DATASET, cùng nghĩa. Google gọi khác thôi.

dbt quyết định schema qua config +schema trong dbt_project.yml.
Mặc định dbt tự ghép tên thành kiểu "dwh_mart" -- xấu, nên hầu hết repo
đều có macro generate_schema_name để ghi đè. Repo lab này có sẵn ở
macros/generate_schema_name.sql, repo công ty bạn gần như chắc chắn cũng có.""",

"profiles": """profiles.yml = FILE CHỨA THÔNG TIN KẾT NỐI TỚI ENGINE

Đây là file DUY NHẤT biết bạn đang chạy trên engine nào. Toàn bộ model
trong models/ hoàn toàn không biết điều đó.

  de_lab:
    target: duckdb          <- dùng cái nào khi không nói gì thêm
    outputs:
      duckdb:               <- một "target"
        type: duckdb
        path: lab.duckdb
      bq:                   <- một target khác, cùng bộ model
        type: bigquery
        project: ...

Đổi engine = đổi target:  dbt run --target bq

Ở công ty, file này thường có ít nhất dev và prod, trỏ vào hai dataset
khác nhau. NGUYÊN TẮC AN TOÀN: luôn kiểm tra mình đang ở target nào trước
khi chạy. Chạy nhầm prod là sự cố, không phải lỗi nhỏ.

File này chứa thông tin đăng nhập nên KHÔNG BAO GIỜ commit lên git.""",
}

# một số tên gọi khác cùng trỏ về một mục
BI_DANH = {
    "view": "materialized", "table": "materialized", "materialize": "materialized",
    "is_incremental": "incremental", "this": "incremental",
    "delete+insert": "unique_key", "merge": "unique_key", "strategy": "unique_key",
    "row_number": "window", "over": "window", "window function": "window",
    "scd": "snapshot", "scd2": "snapshot", "dimension": "fact", "dim": "fact",
    "dwh": "lake", "mart": "lake", "medallion": "lake", "staging": "lake",
    "stg": "lake", "bronze": "lake", "silver": "lake", "gold": "lake",
    "with": "cte", "subquery": "cte",
    "left join": "join", "inner join": "join", "khoa ngoai": "join",
    "cluster": "partition", "partition_by": "partition", "cluster_by": "partition",
    "chi phi": "bytes", "dry run": "bytes", "dry_run": "bytes", "gia": "bytes",
    "dag": "lineage", "phu thuoc": "lineage",
    "kafka connect": "cdc", "redpanda": "cdc",
    "target": "profiles", "connection": "profiles",
    "dataset": "schema",
    "idempotency": "idempotent",
    "unique": "test", "not_null": "test", "data_tests": "test",
    "compiled": "compile", "target/": "compile",
    "duckdb": "engine", "bigquery": "engine", "clickhouse": "engine",
}
