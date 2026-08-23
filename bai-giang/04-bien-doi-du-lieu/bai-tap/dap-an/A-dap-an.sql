-- ===== PHẦN A · ĐÁP ÁN =====

-- A1
SELECT don_id, ngay_dat, tong_tien
FROM don_hang ORDER BY tong_tien DESC LIMIT 10;

-- A2
SELECT tinh, count(*) AS so_khach
FROM khach_hang GROUP BY tinh
HAVING count(*) > 35 ORDER BY so_khach DESC;

-- A3
SELECT sp.danh_muc, sum(c.so_luong * c.don_gia) AS doanh_thu
FROM chi_tiet_don c JOIN san_pham sp USING (san_pham_id)
GROUP BY 1 ORDER BY 2 DESC;

-- A4  — count(d.don_id) tự trả 0 cho khách không có đơn.
-- Nếu viết count(*) sẽ SAI: LEFT JOIN vẫn sinh 1 dòng NULL nên count(*) = 1.
SELECT k.khach_id, k.ten, count(d.don_id) AS so_don
FROM khach_hang k LEFT JOIN don_hang d ON d.khach_id = k.khach_id
GROUP BY 1, 2 ORDER BY so_don, k.khach_id LIMIT 25;

-- A5
SELECT CASE WHEN tong_tien < 200000 THEN 'nho'
            WHEN tong_tien <= 500000 THEN 'vua'
            ELSE 'lon' END AS nhom_gia_tri,
       count(*) AS so_don
FROM don_hang GROUP BY 1 ORDER BY so_don DESC;

-- A6
WITH dt_khach AS (
  SELECT khach_id, sum(tong_tien) AS doanh_thu
  FROM don_hang WHERE trang_thai = 'hoan_thanh' GROUP BY 1
)
SELECT khach_id, doanh_thu
FROM dt_khach
WHERE doanh_thu > (SELECT avg(doanh_thu) FROM dt_khach)
ORDER BY doanh_thu DESC LIMIT 15;
