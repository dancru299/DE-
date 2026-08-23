# Lab dbt

Bảy bài tập chuyển những gì bạn vừa viết tay ở phần B và C sang dbt.
Dùng chung file `../de.duckdb` — nghĩa là dbt sẽ đọc đúng bộ dữ liệu bạn đã quen.

## Chạy

```bash
.venv/bin/dbt build --profiles-dir .
```

Cờ `--profiles-dir .` là bắt buộc, vì `profiles.yml` để ngay trong lab
cho tự chứa thay vì nằm ở `~/.dbt/` như mặc định.

Các lệnh hay dùng:

| Lệnh | Làm gì |
|------|--------|
| `dbt run` | Chạy model, dựng bảng/view |
| `dbt test` | Chỉ chạy kiểm thử |
| `dbt build` | Chạy model + test + snapshot theo đúng thứ tự phụ thuộc |
| `dbt run -s stg_khach_hang+` | Chạy model đó **và mọi thứ phụ thuộc vào nó** |
| `dbt compile` | Xem SQL thật sau khi Jinja được dịch — dùng khi debug |
| `dbt docs generate && dbt docs serve` | Xem sơ đồ lineage |

> Debug Jinja: mở `target/compiled/de_lab/models/...` để đọc SQL cuối cùng
> dbt gửi xuống kho. 90% lỗi Jinja lộ ra ngay khi nhìn file này.

## Bảy bài

| Bài | File | Học được gì |
|-----|------|-------------|
| D1 | `models/staging/stg_khach_hang.sql` | `source()`, quy tắc tầng staging, khử trùng |
| D2 | `models/staging/stg_don_hang.sql` | Chuẩn hoá kiểu và khoá nối |
| D2b | `models/marts/dim_khach_hang.sql` | `ref()` và lineage |
| D3 | `models/marts/fct_doanh_thu_ngay.sql` | **Model incremental + cửa sổ nhìn lại** |
| D4 | `models/marts/schema.yml` | Bốn generic test của dbt |
| D5 | `snapshots/snap_khach_hang.sql` | Snapshot = SCD Type 2 tự động |
| D6 | `macros/tien_te.sql` | Macro Jinja |
| D7 | `tests/assert_tong_tien_khop.sql` | Singular test viết tay |

Đáp án đầy đủ trong `dap-an/`, cùng cấu trúc thư mục. Muốn xem bản hoàn chỉnh chạy thế nào:

```bash
cp -rf dap-an/models/. models/ && cp -rf dap-an/snapshots/. snapshots/ \
  && cp -rf dap-an/macros/. macros/ && cp -rf dap-an/tests/. tests/
.venv/bin/dbt build --profiles-dir .
```

## Kết quả mong đợi

Với đáp án đầy đủ: **17 test PASS, 1 test FAIL**.

Cái FAIL đó là `assert_tong_tien_khop` với thông báo `Got 31 results`.
**Đây không phải lỗi cài đặt — nó đúng như thiết kế.** Dữ liệu nguồn có sẵn
31 đơn lệch tổng tiền, và test của bạn vừa bắt được chúng.

Đó chính là cảm giác một sự cố dữ liệu thật: pipeline chạy xanh, model dựng xong,
nhưng test đỏ lên và chỉ đúng vào 31 dòng có vấn đề. Nếu không có test này,
31 đơn sai đó sẽ lặng lẽ đi thẳng vào báo cáo.

## Kiểm chứng model incremental

Đây là bài đáng bỏ công nhất. Chạy `dbt build` ba lần liên tiếp rồi đếm:

```bash
duckdb ../de.duckdb -c "SELECT count(*), sum(so_don), sum(doanh_thu) FROM fct_doanh_thu_ngay;"
```

Ba lần phải ra **số y hệt nhau** (180 ngày · 1.521 đơn · 1.655.582.000đ),
và khớp chính xác với nguồn:

```bash
duckdb ../de.duckdb -c "SELECT count(DISTINCT ngay_dat), count(*), sum(tong_tien) FROM don_hang WHERE trang_thai='hoan_thanh';"
```

Số không đổi qua nhiều lần chạy = model **idempotent**. Nếu bạn viết `insert`
thuần thay vì `delete+insert`, chạy ba lần doanh thu sẽ gấp ba — và không có
gì báo lỗi cả.
