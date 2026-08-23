-- ============================================================
--  PHẦN C · KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU   (5 bài · ~30 phút)
--
--  Đây là 5 câu query bạn sẽ viết đi viết lại suốt sự nghiệp DE.
--  Nguyên tắc chung: một bài kiểm thử tốt phải trả về
--  KHÔNG DÒNG NÀO khi dữ liệu sạch, và trả về đúng những dòng
--  có vấn đề khi dữ liệu bẩn. Sau này dbt test hoạt động y hệt.
--
--  Đáp án: dap-an/C-dap-an.sql
-- ============================================================

-- C1. TRÙNG KHOÁ.  Tìm những ma_kh xuất hiện nhiều hơn một lần
--     trong khach_hang_raw. Hiện ma_kh và số lần xuất hiện.
--     (kết quả đúng: 20 dòng)
-- >>>


-- C2. NULL KHÔNG ĐƯỢC PHÉP.  Cột tinh là bắt buộc.
--     Đếm và liệt kê các dòng vi phạm trong khach_hang_raw.
--     (kết quả đúng: 15 dòng)
-- >>>


-- C3. GIÁ TRỊ LẠ.  Cột hang_thanh_vien chỉ được nhận đúng 3 giá trị:
--     'bac', 'vang', 'kim_cuong'. Tìm mọi giá trị nằm ngoài danh sách này,
--     kèm số lần xuất hiện.
--     (gợi ý: sẽ lòi ra một giá trị viết hoa — đây là lỗi thật, không phải bẫy)
-- >>>


-- C4. ĐỘ TƯƠI (freshness).  Bản ghi mới nhất trong don_hang là lúc nào,
--     và so với BÂY GIỜ thì nó đã cũ bao nhiêu giờ?
--     Trả về thêm cột canh_bao = true nếu cũ quá 24 giờ.
--     (gợi ý: dùng cap_nhat_luc, không dùng ngay_dat)
-- >>>


-- C5. ĐỐI CHIẾU CHÉO.  Cột don_hang.tong_tien phải luôn bằng
--     tổng (so_luong * don_gia) của chi tiết đơn đó.
--     Tìm mọi đơn bị lệch, hiện don_id, tong_tien_ghi, tong_tien_that, chenh_lech.
--     (kết quả đúng: 31 dòng — đây là loại lỗi âm thầm nguy hiểm nhất,
--      vì pipeline vẫn chạy xanh mà số liệu thì sai)
-- >>>
