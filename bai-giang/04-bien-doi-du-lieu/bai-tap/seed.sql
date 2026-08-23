-- ============================================================
--  BỘ DỮ LIỆU LUYỆN TẬP  ·  Shop bán lẻ giả lập
--  Toàn bộ dữ liệu do script sinh ra. Không có dữ liệu thật.
--  Chạy:  duckdb de.duckdb < seed.sql
-- ============================================================

SELECT setseed(0.42);   -- cố định ngẫu nhiên -> ai chạy cũng ra số giống nhau

-- ---------- Dimension: khách hàng ----------
CREATE OR REPLACE TABLE khach_hang AS
SELECT
  i                                                        AS khach_id,
  'KH' || lpad(i::VARCHAR, 4, '0')                         AS ma_kh,
  (['Nguyễn An','Trần Bình','Lê Chi','Phạm Dũng','Hoàng Em',
    'Vũ Phúc','Đặng Giang','Bùi Hà','Đỗ Khoa','Ngô Lan'])[1 + (i % 10)]
    || ' ' || (i / 10)::INT::VARCHAR                        AS ten,
  (['Hà Nội','TP.HCM','Đà Nẵng','Cần Thơ','Hải Phòng'])[1 + (i % 5)] AS tinh,
  (['bac','bac','bac','vang','kim_cuong'])[1 + (i % 5)]     AS hang_thanh_vien,
  DATE '2025-01-01' + ((i * 3 % 400)::INT)                         AS ngay_dang_ky
FROM generate_series(1, 200) t(i);

-- ---------- Dimension: sản phẩm ----------
CREATE OR REPLACE TABLE san_pham AS
SELECT
  i                                                        AS san_pham_id,
  'SP' || lpad(i::VARCHAR, 3, '0')                         AS ma_sp,
  (['Áo thun','Quần jean','Giày','Túi','Mũ','Tất','Khăn','Ví'])[1 + (i % 8)]
    || ' mẫu ' || i::VARCHAR                                AS ten_sp,
  (['thoi_trang','thoi_trang','phu_kien','giay_dep'])[1 + (i % 4)] AS danh_muc,
  (50000 + (i % 20) * 25000)::BIGINT                        AS gia_niem_yet
FROM generate_series(1, 40) t(i);

-- ---------- Fact: đơn hàng ----------
CREATE OR REPLACE TABLE don_hang AS
SELECT
  10000 + i                                                AS don_id,
  1 + (random() * 179)::INT                                AS khach_id,   -- cố ý: khách 181-200 chưa từng mua
  DATE '2026-01-01' + (random() * 179)::INT                AS ngay_dat,
  (['hoan_thanh','hoan_thanh','hoan_thanh','dang_giao','huy'])[1 + (random()*4.99)::INT] AS trang_thai,
  0::BIGINT                                                AS tong_tien,
  NULL::TIMESTAMP                                          AS cap_nhat_luc
FROM generate_series(1, 3000) t(i);

-- ---------- Fact: chi tiết đơn ----------
CREATE OR REPLACE TABLE chi_tiet_don AS
SELECT
  d.don_id,
  sp.san_pham_id,
  (1 + (random() * 2)::INT)::INT                           AS so_luong,
  sp.gia_niem_yet                                          AS don_gia
FROM don_hang d
CROSS JOIN generate_series(1, 3) g(n)
JOIN san_pham sp ON sp.san_pham_id = 1 + ((d.don_id * g.n * 7) % 40)
WHERE random() < 0.62;

-- tổng tiền tính lại cho khớp chi tiết
UPDATE don_hang d
SET tong_tien = COALESCE((
      SELECT SUM(c.so_luong * c.don_gia) FROM chi_tiet_don c WHERE c.don_id = d.don_id
    ), 0);

-- cap_nhat_luc: đa số bằng ngày đặt, một số về TRỄ sang hôm sau (late-arriving)
UPDATE don_hang
SET cap_nhat_luc = ngay_dat::TIMESTAMP
                 + to_hours((random() * 23)::INT)
                 + to_minutes((random() * 59)::INT)
                 + CASE WHEN random() < 0.04 THEN to_hours(26) ELSE to_hours(0) END;

-- CÀI LỖI 1: ~1% đơn có tổng tiền lệch so với chi tiết
UPDATE don_hang SET tong_tien = tong_tien + 99000
WHERE don_id % 97 = 0;

-- ---------- Fact: sự kiện web ----------
CREATE OR REPLACE TABLE su_kien_web AS
SELECT
  row_number() OVER ()                                     AS su_kien_id,
  1 + (random() * 179)::INT                                AS khach_id,   -- cố ý: khách 181-200 chưa từng mua
  (['xem_trang','xem_trang','xem_trang','them_gio','thanh_toan'])[1 + (random()*4.99)::INT] AS loai,
  TIMESTAMP '2026-06-01 00:00:00'
    + to_minutes((random() * 43200)::INT)                  AS thoi_gian
FROM generate_series(1, 12000) t(i);

-- ---------- Bảng THÔ: bẩn có chủ đích, dùng cho bài làm sạch ----------
CREATE OR REPLACE TABLE khach_hang_raw AS
SELECT
  ma_kh,
  CASE WHEN khach_id % 11 = 0 THEN '  ' || upper(ten) || ' ' ELSE ten END AS ten,
  CASE WHEN khach_id % 13 = 0 THEN NULL ELSE tinh END                     AS tinh,
  CASE WHEN khach_id % 7  = 0 THEN 'BAC' ELSE hang_thanh_vien END         AS hang_thanh_vien,
  CASE WHEN khach_id % 5  = 0 THEN strftime(ngay_dang_ky, '%d/%m/%Y')
       ELSE strftime(ngay_dang_ky, '%Y-%m-%d') END                        AS ngay_dang_ky_text,
  ngay_dang_ky::TIMESTAMP + to_hours(khach_id % 24)                       AS nhan_luc
FROM khach_hang
UNION ALL   -- CÀI LỖI 2: 20 khách bị gửi trùng, bản sau mới hơn
SELECT
  ma_kh, ten,
  (['Hà Nội','TP.HCM','Đà Nẵng'])[1 + (khach_id % 3)],
  hang_thanh_vien,
  strftime(ngay_dang_ky, '%Y-%m-%d'),
  ngay_dang_ky::TIMESTAMP + to_hours(48)
FROM khach_hang WHERE khach_id % 10 = 0;

-- ---------- Bảng lịch sử kiểu SCD2, dùng cho bài chiều thay đổi chậm ----------
CREATE OR REPLACE TABLE khach_hang_thay_doi AS
SELECT ma_kh, tinh, hang_thanh_vien, DATE '2026-01-01' AS ghi_nhan_ngay
FROM khach_hang WHERE khach_id <= 30
UNION ALL
SELECT ma_kh,
       (['Đà Nẵng','Cần Thơ','Hà Nội'])[1 + (khach_id % 3)],
       CASE WHEN khach_id % 2 = 0 THEN 'vang' ELSE hang_thanh_vien END,
       DATE '2026-04-15'
FROM khach_hang WHERE khach_id <= 30 AND khach_id % 3 = 0;

-- ---------- Báo cáo nhanh ----------
.print ''
.print '  ĐÃ DỰNG XONG BỘ DỮ LIỆU'
SELECT 'khach_hang' AS bang, count(*) AS so_dong FROM khach_hang
UNION ALL SELECT 'san_pham',            count(*) FROM san_pham
UNION ALL SELECT 'don_hang',            count(*) FROM don_hang
UNION ALL SELECT 'chi_tiet_don',        count(*) FROM chi_tiet_don
UNION ALL SELECT 'su_kien_web',         count(*) FROM su_kien_web
UNION ALL SELECT 'khach_hang_raw',      count(*) FROM khach_hang_raw
UNION ALL SELECT 'khach_hang_thay_doi', count(*) FROM khach_hang_thay_doi
ORDER BY 1;
