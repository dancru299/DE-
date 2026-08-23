-- ============================================================
--  PHẦN B · SQL CỦA DATA ENGINEER        (14 bài · ~3 giờ)
--
--  Đây là phần chính. Mười bốn khuôn mẫu dưới đây chiếm gần hết
--  lượng SQL bạn viết trong nghề DE. Học thuộc khuôn, đổi bảng là dùng lại.
--
--  Làm theo thứ tự — bài sau dựa vào kỹ thuật của bài trước.
--  Đáp án kèm giải thích: dap-an/B-dap-an.sql
-- ============================================================


-- ---------- NHÓM 1 · KHỬ TRÙNG VÀ LÀM SẠCH ----------

-- B1. KHUÔN MẪU QUAN TRỌNG NHẤT: khử trùng lấy bản mới nhất.
--     Bảng khach_hang_raw có 220 dòng nhưng chỉ 200 khách thật —
--     20 khách bị gửi trùng, bản gửi sau có nhan_luc mới hơn và tỉnh đã đổi.
--     Lấy đúng 200 dòng, mỗi ma_kh giữ lại bản có nhan_luc mới nhất.
--     (gợi ý: ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ... DESC) rồi lọc = 1)
-- >>>


-- B2. Viết lại B1 bằng QUALIFY cho gọn (DuckDB, BigQuery, Snowflake đều có).
--     So sánh hai cách và tự trả lời: vì sao QUALIFY sạch hơn?
-- >>>


-- B3. LÀM SẠCH ĐỦ BỘ. Từ kết quả B1, xuất ra bảng chuẩn hoá:
--       - ten: bỏ khoảng trắng thừa hai đầu; các bản bị VIẾT HOA TOÀN BỘ
--              đưa về dạng Chữ Hoa Đầu Từ (DuckDB không có initcap — tự dựng lấy)
--       - tinh: NULL thì thay bằng 'khong_ro'
--       - hang_thanh_vien: đưa hết về chữ thường
--       - ngay_dang_ky: cột text đang có HAI định dạng lẫn lộn
--         ('2025-03-04' và '04/03/2025') — parse cả hai về kiểu DATE
--     (gợi ý: try_strptime() trả NULL khi không khớp, dùng COALESCE nối hai lần thử)
-- >>>


-- ---------- NHÓM 2 · HÀM CỬA SỔ (WINDOW FUNCTION) ----------

-- B4. LUỸ KẾ. Doanh thu mỗi ngày và doanh thu cộng dồn từ đầu kỳ.
--     Chỉ tính đơn trạng thái 'hoan_thanh'.
--     (gợi ý: SUM(...) OVER (ORDER BY ngay ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW))
-- >>>


-- B5. SO VỚI KỲ TRƯỚC. Với mỗi ngày, hiện doanh thu hôm đó, doanh thu hôm trước,
--     và % tăng trưởng. Ngày đầu tiên không có hôm trước thì để NULL.
--     (gợi ý: LAG)
-- >>>


-- B6. XẾP HẠNG TRONG NHÓM. Top 3 sản phẩm bán chạy nhất (theo doanh thu)
--     TRONG TỪNG danh mục.
--     Tự trả lời thêm: ROW_NUMBER, RANK và DENSE_RANK khác nhau chỗ nào,
--     và ở bài này nên dùng cái nào?
-- >>>


-- B7. LẤP NGÀY TRỐNG (date spine). Có những ngày không phát sinh đơn nào.
--     Nếu chỉ GROUP BY ngày thì các ngày đó biến mất khỏi báo cáo — biểu đồ
--     sẽ nối liền và che mất sự cố.
--     Tạo dải ngày liên tục từ 2026-01-01 đến 2026-06-30, LEFT JOIN doanh thu vào,
--     ngày không có đơn phải hiện 0.
--     (gợi ý: generate_series(DATE '...', DATE '...', INTERVAL 1 DAY))
-- >>>


-- ---------- NHÓM 3 · KHUÔN MẪU PHÂN TÍCH HÀNH VI ----------

-- B8. CHIA PHIÊN (sessionization) — bài khó nhất phần này, và là bài
--     phân biệt người biết window function thật với người chỉ học thuộc.
--     Trong su_kien_web, gom sự kiện của mỗi khách thành các phiên.
--     Quy tắc: hai sự kiện liên tiếp cách nhau QUÁ 30 PHÚT thì tính là phiên mới.
--     Trả về: khach_id, so_phien, tong_su_kien.
--     (gợi ý ba bước:
--        1. LAG lấy thời gian sự kiện trước của cùng khách
--        2. cột moc_phien_moi = 1 nếu khoảng cách > 30 phút, ngược lại 0
--        3. SUM(moc_phien_moi) OVER (PARTITION BY khach ORDER BY thoi_gian) = số hiệu phiên)
-- >>>


-- B9. PHỄU CHUYỂN ĐỔI (funnel). Trong su_kien_web, tính:
--     số khách từng 'xem_trang', số khách từng 'them_gio', số khách từng 'thanh_toan',
--     và tỉ lệ chuyển đổi giữa các bước.
-- >>>


-- B10. GIỮ CHÂN THEO NHÓM (cohort retention).
--      Nhóm khách theo THÁNG có đơn đầu tiên. Với mỗi nhóm, đếm xem
--      bao nhiêu khách còn quay lại mua ở tháng thứ 0, 1, 2, 3...
--      Trả về: thang_nhom, thang_thu, so_khach.
--      (đây là báo cáo bị hỏi nhiều nhất ở mọi công ty có sản phẩm)
-- >>>


-- B11. TÌM CÁI KHÔNG CÓ (anti-join). Liệt kê khách đã đăng ký
--      nhưng CHƯA TỪNG có đơn hoàn thành nào.
--      Viết bằng hai cách — NOT EXISTS và LEFT JOIN ... IS NULL —
--      rồi tự trả lời: vì sao KHÔNG nên dùng NOT IN ở đây?
-- >>>


-- B12. XOAY BẢNG (pivot). Doanh thu theo tỉnh (dòng) × tháng (cột).
--      Viết bằng CASE WHEN thủ công trước cho hiểu bản chất,
--      rồi thử lại bằng cú pháp PIVOT của DuckDB.
-- >>>


-- ---------- NHÓM 4 · HAI KHUÔN MẪU CỐT LÕI CỦA PIPELINE ----------

-- B13. SCD TYPE 2 — chiều thay đổi chậm.
--      Bảng khach_hang_thay_doi ghi lại các lần khách đổi tỉnh / đổi hạng,
--      mỗi lần một dòng kèm ghi_nhan_ngay. Dựng bảng lịch sử đầy đủ:
--        ma_kh, tinh, hang_thanh_vien, hieu_luc_tu, hieu_luc_den, la_ban_hien_tai
--      Quy tắc: hieu_luc_den của một dòng = ghi_nhan_ngay của dòng kế tiếp trừ 1 ngày.
--      Dòng mới nhất có hieu_luc_den = DATE '9999-12-31' và la_ban_hien_tai = true.
--      (gợi ý: LEAD)
--      Vì sao phải làm vậy? Vì nếu ghi đè tỉnh mới lên, toàn bộ báo cáo doanh thu
--      theo tỉnh của QUÁ KHỨ sẽ bị viết lại — và sai.
-- >>>


-- B14. NẠP TĂNG DẦN, CHẠY LẠI AN TOÀN (idempotent incremental).
--      Giả sử bạn chạy job mỗi ngày để nạp bảng tổng hợp doanh_thu_ngay.
--      Viết đoạn SQL nạp dữ liệu CHO ĐÚNG MỘT NGÀY sao cho chạy lại
--      bao nhiêu lần cũng ra kết quả y hệt, không nhân đôi.
--      Bước 1: tạo bảng đích doanh_thu_ngay (ngay DATE, so_don INT, doanh_thu BIGINT).
--      Bước 2: viết đoạn nạp idempotent cho ngày 2026-03-15.
--      Bước 3: CHẠY ĐOẠN ĐÓ BA LẦN rồi kiểm tra bảng vẫn chỉ có 1 dòng cho ngày đó.
--      (gợi ý: DELETE theo phân vùng ngày rồi INSERT lại — đừng chỉ INSERT)
--
--      Câu hỏi mở rộng, nghĩ kỹ trước khi xem đáp án:
--      đơn đặt lúc 23:58 ngày 15/03 nhưng cap_nhat_luc là 01:30 ngày 16/03
--      (dữ liệu về trễ). Job chạy đêm 15/03 sẽ BỎ SÓT nó. Xử lý thế nào?
-- >>>
