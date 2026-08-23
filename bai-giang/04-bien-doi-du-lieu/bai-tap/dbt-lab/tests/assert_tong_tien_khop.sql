-- D7 · Singular test — bài kiểm thử viết tay
--
-- Bốn test khai báo trong schema.yml chỉ kiểm được từng cột.
-- Quy tắc nghiệp vụ phức tạp thì viết hẳn một câu SQL, đặt trong thư mục tests/.
--
-- Quy ước dbt: query này phải trả về RỖNG thì mới đạt.
-- Trả về dòng nào = có dòng đó vi phạm = test FAIL.
--
-- Nhiệm vụ: tìm đơn có tong_tien không khớp tổng chi tiết (bài C5).
-- (dữ liệu đang cài sẵn 31 đơn lệch, nên test này PHẢI fail — đúng như ý đồ)

select 1 where false
-- TODO: viết query thật
