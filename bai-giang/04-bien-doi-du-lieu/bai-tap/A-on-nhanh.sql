-- ============================================================
--  PHẦN A · ÔN NHANH SQL CƠ BẢN          (6 bài · ~20 phút)
--  Chỉ để làm nóng tay. Làm xong nhanh thì sang thẳng phần B.
--  Đáp án: dap-an/A-dap-an.sql
-- ============================================================

-- A1. Liệt kê 10 đơn hàng có tổng tiền cao nhất, hiện don_id, ngay_dat, tong_tien.
-- >>>


-- A2. Mỗi tỉnh có bao nhiêu khách hàng? Chỉ hiện tỉnh có trên 35 khách,
--     sắp xếp giảm dần.
-- >>>


-- A3. Doanh thu theo danh mục sản phẩm.
--     Nối chi_tiet_don với san_pham, tính SUM(so_luong * don_gia).
-- >>>


-- A4. Mỗi khách đã đặt bao nhiêu đơn? Khách chưa đặt đơn nào phải hiện số 0,
--     không được biến mất khỏi kết quả.  (gợi ý: LEFT JOIN + COALESCE)
-- >>>


-- A5. Phân loại đơn theo giá trị: dưới 200k = 'nho', 200k–500k = 'vua',
--     trên 500k = 'lon'. Đếm số đơn mỗi loại.  (gợi ý: CASE WHEN)
-- >>>


-- A6. Dùng CTE: tính doanh thu mỗi khách, rồi lấy ra những khách
--     có doanh thu trên mức trung bình của tất cả khách.
-- >>>
