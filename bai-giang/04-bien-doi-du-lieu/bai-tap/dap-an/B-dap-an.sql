-- ============================================================
--  PHẦN B · ĐÁP ÁN KÈM GIẢI THÍCH
-- ============================================================

-- ---------- B1 · khử trùng lấy bản mới nhất ----------
-- Khuôn mẫu này bạn sẽ viết hàng trăm lần. Nhớ ba chỗ:
--   PARTITION BY = khoá tự nhiên (cái gì được coi là "một thực thể")
--   ORDER BY     = tiêu chí "mới hơn"  (thời gian nhận, thời gian cập nhật)
--   rn = 1       = giữ lại đúng một bản
WITH danh_so AS (
  SELECT *,
         row_number() OVER (PARTITION BY ma_kh ORDER BY nhan_luc DESC) AS rn
  FROM khach_hang_raw
)
SELECT * EXCLUDE (rn) FROM danh_so WHERE rn = 1;   -- 200 dòng


-- ---------- B2 · cũng vậy nhưng dùng QUALIFY ----------
-- QUALIFY = mệnh đề WHERE dành riêng cho hàm cửa sổ.
-- Không có nó thì buộc phải bọc thêm một tầng CTE chỉ để lọc rn — thừa.
-- Thứ tự thực thi: FROM -> WHERE -> GROUP BY -> HAVING -> WINDOW -> QUALIFY -> ORDER BY
SELECT *
FROM khach_hang_raw
QUALIFY row_number() OVER (PARTITION BY ma_kh ORDER BY nhan_luc DESC) = 1;


-- ---------- B3 · làm sạch đủ bộ ----------
WITH moi_nhat AS (
  SELECT * FROM khach_hang_raw
  QUALIFY row_number() OVER (PARTITION BY ma_kh ORDER BY nhan_luc DESC) = 1
)
SELECT
  ma_kh,
  -- DuckDB không có initcap: tách từ -> viết hoa chữ đầu -> nối lại
  array_to_string(
    list_transform(string_split(lower(trim(ten)), ' '),
                   lambda x: CASE WHEN x = '' THEN x ELSE upper(x[1]) || x[2:] END),
    ' ')                                            AS ten,
  COALESCE(tinh, 'khong_ro')                        AS tinh,
  lower(hang_thanh_vien)                            AS hang_thanh_vien,
  -- HAI định dạng ngày lẫn lộn: thử lần lượt, cái nào khớp thì lấy.
  -- try_strptime trả NULL khi không khớp (strptime thường sẽ NÉM LỖI và giết cả job).
  COALESCE(
    try_strptime(ngay_dang_ky_text, '%Y-%m-%d'),
    try_strptime(ngay_dang_ky_text, '%d/%m/%Y')
  )::DATE                                           AS ngay_dang_ky
FROM moi_nhat
ORDER BY ma_kh;
-- Kiểm tra lại: phải 0 dòng NULL ngày -> nếu >0 là còn định dạng thứ ba chưa xử lý
--   SELECT count(*) FROM (...) WHERE ngay_dang_ky IS NULL;


-- ---------- B4 · doanh thu luỹ kế ----------
WITH theo_ngay AS (
  SELECT ngay_dat AS ngay, sum(tong_tien) AS doanh_thu
  FROM don_hang WHERE trang_thai = 'hoan_thanh' GROUP BY 1
)
SELECT ngay, doanh_thu,
       sum(doanh_thu) OVER (ORDER BY ngay
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS luy_ke
FROM theo_ngay ORDER BY ngay LIMIT 15;
-- Bỏ mệnh đề ROWS đi vẫn ra kết quả giống ở đây, nhưng mặc định là RANGE —
-- khi cột ORDER BY có giá trị trùng, RANGE gộp cả cụm trùng vào một lần.
-- Viết rõ ROWS là thói quen tốt: nói đúng ý mình, không phụ thuộc mặc định.


-- ---------- B5 · so với ngày hôm trước ----------
WITH theo_ngay AS (
  SELECT ngay_dat AS ngay, sum(tong_tien) AS doanh_thu
  FROM don_hang WHERE trang_thai = 'hoan_thanh' GROUP BY 1
)
SELECT ngay, doanh_thu,
       lag(doanh_thu) OVER (ORDER BY ngay) AS hom_truoc,
       round(100.0 * (doanh_thu - lag(doanh_thu) OVER (ORDER BY ngay))
             / nullif(lag(doanh_thu) OVER (ORDER BY ngay), 0), 1) AS pct_tang
FROM theo_ngay ORDER BY ngay LIMIT 15;
-- nullif(x, 0) là cái chốt an toàn: hôm trước = 0 thì chia cho 0 -> lỗi hoặc inf.
-- Đây là lỗi làm gãy dashboard nhiều nhất mà không ai ngờ tới.


-- ---------- B6 · top 3 mỗi danh mục ----------
WITH dt_sp AS (
  SELECT sp.danh_muc, sp.ten_sp, sum(c.so_luong * c.don_gia) AS doanh_thu
  FROM chi_tiet_don c
  JOIN san_pham sp USING (san_pham_id)
  JOIN don_hang  d USING (don_id)
  WHERE d.trang_thai = 'hoan_thanh'
  GROUP BY 1, 2
)
SELECT * FROM dt_sp
QUALIFY row_number() OVER (PARTITION BY danh_muc ORDER BY doanh_thu DESC) <= 3
ORDER BY danh_muc, doanh_thu DESC;
-- ROW_NUMBER : 1,2,3,4     luôn đúng N dòng, hoà thì cắt tuỳ tiện
-- RANK       : 1,2,2,4     hoà cùng hạng, nhảy số
-- DENSE_RANK : 1,2,2,3     hoà cùng hạng, không nhảy số
-- Cần "đúng 3 dòng mỗi nhóm" -> ROW_NUMBER.
-- Cần "mọi sản phẩm đồng hạng ba đều được vào" -> DENSE_RANK.


-- ---------- B7 · lấp ngày trống ----------
WITH dai_ngay AS (
  SELECT ngay::DATE AS ngay
  FROM generate_series(DATE '2026-01-01', DATE '2026-06-30', INTERVAL 1 DAY) t(ngay)
), dt AS (
  SELECT ngay_dat AS ngay, sum(tong_tien) AS doanh_thu
  FROM don_hang WHERE trang_thai = 'hoan_thanh' GROUP BY 1
)
SELECT s.ngay, COALESCE(dt.doanh_thu, 0) AS doanh_thu
FROM dai_ngay s LEFT JOIN dt ON dt.ngay = s.ngay
ORDER BY s.ngay LIMIT 15;
-- Vì sao quan trọng: ngày pipeline chết sẽ không có dòng nào.
-- Không có date spine thì biểu đồ NỐI LIỀN qua chỗ trống và che mất sự cố.
-- Có date spine thì nó tụt xuống 0 — nhìn phát biết ngay.


-- ---------- B8 · chia phiên (sessionization) ----------
-- Ba bước kinh điển: LAG -> đánh mốc -> cộng dồn mốc.
WITH b1 AS (
  SELECT khach_id, thoi_gian,
         lag(thoi_gian) OVER (PARTITION BY khach_id ORDER BY thoi_gian) AS lan_truoc
  FROM su_kien_web
), b2 AS (
  SELECT *,
         CASE WHEN lan_truoc IS NULL
                OR thoi_gian - lan_truoc > INTERVAL 30 MINUTE
              THEN 1 ELSE 0 END AS moc_phien_moi
  FROM b1
), b3 AS (
  SELECT *,
         sum(moc_phien_moi) OVER (PARTITION BY khach_id ORDER BY thoi_gian
              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS so_hieu_phien
  FROM b2
)
SELECT khach_id, max(so_hieu_phien) AS so_phien, count(*) AS tong_su_kien
FROM b3 GROUP BY 1 ORDER BY so_phien DESC LIMIT 15;
-- Mẹo nhớ cả đời: "cộng dồn một cột cờ 0/1" chính là cách đánh số nhóm
-- cho mọi bài toán chuỗi liên tiếp — phiên truy cập, chuỗi ngày đăng nhập
-- liên tục, khoảng thời gian máy chạy liên tục...


-- ---------- B9 · phễu chuyển đổi ----------
WITH buoc AS (
  SELECT count(DISTINCT CASE WHEN loai = 'xem_trang'  THEN khach_id END) AS xem,
         count(DISTINCT CASE WHEN loai = 'them_gio'   THEN khach_id END) AS gio,
         count(DISTINCT CASE WHEN loai = 'thanh_toan' THEN khach_id END) AS mua
  FROM su_kien_web
)
SELECT xem, gio, mua,
       round(100.0 * gio / nullif(xem, 0), 1) AS pct_xem_den_gio,
       round(100.0 * mua / nullif(gio, 0), 1) AS pct_gio_den_mua
FROM buoc;
-- Lưu ý: dữ liệu này sinh ngẫu nhiên nên tỉ lệ gần 100%.
-- Phễu thật phải ràng buộc THỨ TỰ THỜI GIAN (thêm giỏ SAU khi xem trang),
-- nếu không con số sẽ đẹp giả tạo. Đây là lỗi phân tích rất hay gặp.


-- ---------- B10 · giữ chân theo nhóm (cohort) ----------
WITH lan_dau AS (
  SELECT khach_id, date_trunc('month', min(ngay_dat)) AS thang_nhom
  FROM don_hang WHERE trang_thai = 'hoan_thanh' GROUP BY 1
), hoat_dong AS (
  SELECT d.khach_id, l.thang_nhom,
         date_trunc('month', d.ngay_dat) AS thang_hd
  FROM don_hang d JOIN lan_dau l USING (khach_id)
  WHERE d.trang_thai = 'hoan_thanh'
)
SELECT thang_nhom::DATE                                AS thang_nhom,
       datediff('month', thang_nhom, thang_hd)         AS thang_thu,
       count(DISTINCT khach_id)                        AS so_khach
FROM hoat_dong GROUP BY 1, 2 ORDER BY 1, 2;
-- Đọc bảng này: cột thang_thu = 0 là quy mô nhóm ban đầu.
-- Các cột sau tụt bao nhiêu chính là tỉ lệ rơi rụng.


-- ---------- B11 · anti-join ----------
-- Cách 1 — NOT EXISTS (nên dùng)
SELECT k.khach_id, k.ten
FROM khach_hang k
WHERE NOT EXISTS (SELECT 1 FROM don_hang d
                  WHERE d.khach_id = k.khach_id AND d.trang_thai = 'hoan_thanh')
ORDER BY k.khach_id;

-- Cách 2 — LEFT JOIN ... IS NULL (tương đương, đọc khó hơn một chút)
SELECT k.khach_id, k.ten
FROM khach_hang k
LEFT JOIN (SELECT DISTINCT khach_id FROM don_hang WHERE trang_thai = 'hoan_thanh') d
       ON d.khach_id = k.khach_id
WHERE d.khach_id IS NULL
ORDER BY k.khach_id;

-- Vì sao KHÔNG dùng NOT IN:
-- nếu danh sách con chứa dù chỉ MỘT giá trị NULL, thì NOT IN trả về
-- UNKNOWN cho mọi dòng -> kết quả RỖNG SẠCH mà không báo lỗi gì cả.
-- Đây là cái bẫy im lặng kinh điển của SQL. NOT EXISTS không bị.


-- ---------- B12 · xoay bảng ----------
-- Cách thủ công: hiểu bản chất "mỗi cột là một CASE WHEN"
SELECT k.tinh,
       sum(CASE WHEN month(d.ngay_dat) = 1 THEN d.tong_tien ELSE 0 END) AS t01,
       sum(CASE WHEN month(d.ngay_dat) = 2 THEN d.tong_tien ELSE 0 END) AS t02,
       sum(CASE WHEN month(d.ngay_dat) = 3 THEN d.tong_tien ELSE 0 END) AS t03,
       sum(CASE WHEN month(d.ngay_dat) = 4 THEN d.tong_tien ELSE 0 END) AS t04,
       sum(CASE WHEN month(d.ngay_dat) = 5 THEN d.tong_tien ELSE 0 END) AS t05,
       sum(CASE WHEN month(d.ngay_dat) = 6 THEN d.tong_tien ELSE 0 END) AS t06
FROM don_hang d JOIN khach_hang k USING (khach_id)
WHERE d.trang_thai = 'hoan_thanh'
GROUP BY 1 ORDER BY 1;

-- Cách ngắn của DuckDB
PIVOT (SELECT k.tinh, month(d.ngay_dat) AS thang, d.tong_tien
       FROM don_hang d JOIN khach_hang k USING (khach_id)
       WHERE d.trang_thai = 'hoan_thanh')
ON thang USING sum(tong_tien) GROUP BY tinh ORDER BY tinh;
-- Nhớ hiểu cách thủ công trước. Cú pháp PIVOT mỗi hệ một kiểu,
-- còn CASE WHEN thì chạy được ở mọi nơi.


-- ---------- B13 · SCD Type 2 ----------
WITH co_dong_sau AS (
  SELECT ma_kh, tinh, hang_thanh_vien, ghi_nhan_ngay,
         lead(ghi_nhan_ngay) OVER (PARTITION BY ma_kh ORDER BY ghi_nhan_ngay) AS ngay_ban_sau
  FROM khach_hang_thay_doi
)
SELECT ma_kh, tinh, hang_thanh_vien,
       ghi_nhan_ngay                                  AS hieu_luc_tu,
       COALESCE(ngay_ban_sau - 1, DATE '9999-12-31')  AS hieu_luc_den,
       ngay_ban_sau IS NULL                           AS la_ban_hien_tai
FROM co_dong_sau
ORDER BY ma_kh, hieu_luc_tu;
-- Dùng bảng này thế nào: nối theo NGÀY GIAO DỊCH, không nối theo bản hiện tại
--   JOIN scd s ON s.ma_kh = d.ma_kh
--             AND d.ngay_dat BETWEEN s.hieu_luc_tu AND s.hieu_luc_den
-- Nhờ vậy đơn tháng 2 vẫn tính cho tỉnh cũ, đơn tháng 5 tính cho tỉnh mới.
-- Dùng 9999-12-31 thay cho NULL để BETWEEN luôn hoạt động, khỏi xử lý NULL riêng.


-- ---------- B14 · nạp tăng dần, chạy lại an toàn ----------
CREATE OR REPLACE TABLE doanh_thu_ngay (ngay DATE, so_don INTEGER, doanh_thu BIGINT);

-- ĐOẠN NẠP IDEMPOTENT — chạy lại bao nhiêu lần cũng ra một kết quả.
-- Bí quyết nằm ở dòng DELETE: mỗi lần chạy tự dọn phần của chính nó trước.
DELETE FROM doanh_thu_ngay WHERE ngay = DATE '2026-03-15';
INSERT INTO doanh_thu_ngay
SELECT ngay_dat, count(*), sum(tong_tien)
FROM don_hang
WHERE ngay_dat = DATE '2026-03-15' AND trang_thai = 'hoan_thanh'
GROUP BY 1;

-- Chạy lại lần 2 và lần 3 — kết quả không đổi
DELETE FROM doanh_thu_ngay WHERE ngay = DATE '2026-03-15';
INSERT INTO doanh_thu_ngay
SELECT ngay_dat, count(*), sum(tong_tien) FROM don_hang
WHERE ngay_dat = DATE '2026-03-15' AND trang_thai = 'hoan_thanh' GROUP BY 1;

DELETE FROM doanh_thu_ngay WHERE ngay = DATE '2026-03-15';
INSERT INTO doanh_thu_ngay
SELECT ngay_dat, count(*), sum(tong_tien) FROM don_hang
WHERE ngay_dat = DATE '2026-03-15' AND trang_thai = 'hoan_thanh' GROUP BY 1;

SELECT count(*) AS so_dong_phai_bang_1 FROM doanh_thu_ngay WHERE ngay = DATE '2026-03-15';

-- Nếu chỉ INSERT mà không DELETE: chạy 3 lần -> 3 dòng -> doanh thu gấp ba.
-- Job lỗi giữa chừng rồi chạy lại là chuyện hằng tuần, nên đây không phải
-- chuyện lý thuyết.

-- CÂU HỎI MỞ RỘNG — dữ liệu về trễ:
-- Đơn đặt 23:58 ngày 15/03 nhưng cap_nhat_luc là 01:30 ngày 16/03.
-- Job chạy đêm 15 sẽ bỏ sót. Hai cách xử lý:
--   1. CỬA SỔ NHÌN LẠI: mỗi lần chạy thì tính lại 3 ngày gần nhất, không chỉ 1 ngày.
--      Đơn giản, hiệu quả, và chỉ làm được vì job đã idempotent.
--   2. LỌC THEO cap_nhat_luc thay vì ngay_dat, giữ một mốc nước (watermark)
--      là cap_nhat_luc lớn nhất đã xử lý, lần sau lấy tiếp từ đó.
-- Thực tế phần lớn đội chọn cách 1 vì đơn giản và khó sai.
SELECT count(*) AS don_ve_tre_trong_du_lieu
FROM don_hang WHERE cap_nhat_luc::DATE > ngay_dat;
