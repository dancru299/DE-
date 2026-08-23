# Bài tập SQL cho Data Engineer

Bộ luyện tập đi kèm bài giảng [`../sql-cho-de.html`](../sql-cho-de.html).
**25 bài SQL + 7 bài dbt**, tất cả chạy được ngay trên máy, không cần dựng hạ tầng.

Dữ liệu là một shop bán lẻ **giả lập hoàn toàn**, do `seed.sql` sinh ra bằng công thức.
Không có dữ liệu thật của bất kỳ ai.

---

## Bắt đầu trong 30 giây

```bash
./chay.sh
```

Lệnh này dựng lại database rồi thả bạn vào shell DuckDB. Không cần cài gì —
`duckdb` đã có sẵn trên máy.

Làm bài thì mở file đề trong editor, viết câu trả lời vào chỗ `-- >>>`,
rồi dán vào shell chạy thử. Muốn làm lại từ đầu thì cứ `./chay.sh` lần nữa.

---

## Dữ liệu có gì

| Bảng | Số dòng | Vai trò |
|------|---------|---------|
| `khach_hang` | 200 | Dimension sạch |
| `san_pham` | 40 | Dimension sạch |
| `don_hang` | 3.000 | Fact — 6 tháng đầu 2026 |
| `chi_tiet_don` | 5.588 | Fact chi tiết |
| `su_kien_web` | 12.000 | Sự kiện, dùng cho bài chia phiên |
| `khach_hang_raw` | 220 | **Bảng bẩn** — dùng cho bài làm sạch |
| `khach_hang_thay_doi` | 40 | Lịch sử đổi tỉnh/hạng, dùng cho bài SCD2 |

### Lỗi được cài sẵn có chủ đích

Bộ dữ liệu này **cố ý bẩn** — đó là điểm mấu chốt. Dữ liệu sạch không dạy được gì.

| Lỗi | Số lượng | Bài liên quan |
|-----|----------|---------------|
| 20 khách bị gửi trùng (bản sau mới hơn, tỉnh đã đổi) | 20 | B1, B2 |
| `tinh` bị NULL | 15 | B3, C2 |
| Tên thừa khoảng trắng và VIẾT HOA TOÀN BỘ | 18 | B3 |
| Ngày lẫn lộn hai định dạng `2025-03-04` và `04/03/2025` | 40 | B3 |
| `hang_thanh_vien` có giá trị lạ `'BAC'` | 28 | C3 |
| Đơn có `tong_tien` lệch so với chi tiết | 31 | C5, D7 |
| Đơn về **trễ** sang ngày hôm sau | 120 | B14, D3 |
| Khách chưa từng mua hàng | 20 | A4, B11 |

---

## Thứ tự làm

| File | Nội dung | Số bài | Thời gian |
|------|----------|--------|-----------|
| `A-on-nhanh.sql` | Ôn SQL cơ bản cho nóng tay | 6 | ~20 phút |
| `B-sql-cho-de.sql` | **Phần chính** — 14 khuôn mẫu SQL của nghề DE | 14 | ~3 giờ |
| `C-kiem-thu-du-lieu.sql` | Viết query kiểm thử chất lượng dữ liệu | 5 | ~30 phút |
| `dbt-lab/` | Chuyển toàn bộ những thứ trên sang dbt | 7 | ~2 giờ |

Đáp án nằm trong `dap-an/`, **có giải thích kèm theo** — đọc phần giải thích
kể cả khi bạn làm đúng, vì nhiều bài có bẫy mà kết quả vẫn ra đúng.

> Làm theo thứ tự A → B → C → dbt. Phần dbt dựa hoàn toàn vào các khuôn mẫu
> đã luyện ở phần B; nhảy cóc vào dbt trước sẽ chỉ là chép cú pháp.

---

## Phần dbt

Xem [`dbt-lab/README.md`](dbt-lab/README.md). Lab đã cài sẵn `dbt-duckdb` trong
`dbt-lab/.venv` và **đã chạy kiểm chứng**, dùng chung đúng file `de.duckdb` với phần SQL.

> `.venv` nặng **354 MB**. Không cần thì xoá thoải mái:
> ```bash
> rm -rf dbt-lab/.venv
> ```
> Cài lại lúc nào cũng được: `python3 -m venv dbt-lab/.venv && dbt-lab/.venv/bin/pip install dbt-duckdb`

---

## Tự kiểm tra

Nhiều bài có ghi sẵn số dòng đúng trong đề (ví dụ B1 phải ra đúng 200 dòng,
C5 phải ra 31 dòng). Ra khác số đó là biết mình sai ngay, không cần mở đáp án.
