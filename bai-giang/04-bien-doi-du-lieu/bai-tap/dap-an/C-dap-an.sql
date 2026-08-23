-- ===== PHẦN C · ĐÁP ÁN =====
-- Ghi nhớ: query kiểm thử tốt = trả về RỖNG khi dữ liệu sạch.
-- Đúng nguyên tắc dbt test dùng sau này.

-- C1 · trùng khoá (20 dòng)
SELECT ma_kh, count(*) AS so_lan
FROM khach_hang_raw GROUP BY ma_kh HAVING count(*) > 1
ORDER BY ma_kh;

-- C2 · null không được phép (15 dòng)
SELECT ma_kh, ten, tinh FROM khach_hang_raw WHERE tinh IS NULL ORDER BY ma_kh;

-- C3 · giá trị lạ  -> lòi ra 'BAC' (28 dòng)
SELECT hang_thanh_vien, count(*) AS so_lan
FROM khach_hang_raw
WHERE hang_thanh_vien NOT IN ('bac', 'vang', 'kim_cuong')
GROUP BY 1 ORDER BY 2 DESC;
-- Cảnh báo: nếu cột có NULL thì NOT IN sẽ ÂM THẦM bỏ sót dòng NULL.
-- An toàn hơn:  WHERE hang_thanh_vien IS NULL OR hang_thanh_vien NOT IN (...)

-- C4 · độ tươi
SELECT max(cap_nhat_luc)                                                AS moi_nhat,
       round(datediff('minute', max(cap_nhat_luc), now()) / 60.0, 1)     AS cu_bao_nhieu_gio,
       datediff('hour', max(cap_nhat_luc), now()) > 24                   AS canh_bao
FROM don_hang;

-- C5 · đối chiếu chéo (31 dòng)
WITH that AS (
  SELECT don_id, sum(so_luong * don_gia) AS tong_tien_that
  FROM chi_tiet_don GROUP BY 1
)
SELECT d.don_id, d.tong_tien AS tong_tien_ghi,
       COALESCE(t.tong_tien_that, 0) AS tong_tien_that,
       d.tong_tien - COALESCE(t.tong_tien_that, 0) AS chenh_lech
FROM don_hang d LEFT JOIN that t USING (don_id)
WHERE d.tong_tien <> COALESCE(t.tong_tien_that, 0)
ORDER BY abs(chenh_lech) DESC;
