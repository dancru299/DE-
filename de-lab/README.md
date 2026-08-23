# DE Lab — dbt + DuckDB

Sân tập để phá thoải mái. Không đụng gì tới prod, không tốn tiền, không cần xin quyền ai.

## Chạy ngay

```bash
cd ~/Desktop/Test/de-lab
./lab
```

Chỉ cần nhớ một lệnh đó. Nó luôn nói cho bạn biết đang ở đâu và làm gì tiếp.

## Đọc ở trình duyệt cho đỡ mỏi mắt

```bash
./lab web
```

Sinh ra `lab.html` và mở luôn: phần giảng của cả 7 bài + từ điển, có mục lục,
có tô màu code, có nút chép lệnh. Trang này sinh ra **từ chính nội dung lab**
nên không bao giờ lệch với terminal. Chạy lại sau khi xong thêm bài để cập nhật
tiến độ trong trang.

Cách dùng hợp lý nhất: **đọc ở trình duyệt, gõ lệnh ở terminal.**

## Bộ lệnh

| Lệnh | Việc |
|---|---|
| `./lab` | bảng tiến độ + việc tiếp theo |
| `./lab bai N` | đề bài N |
| `./lab check N` | chấm bài N |
| `./lab goiy N` | gợi ý, mỗi lần gọi mở thêm 1 mức |
| `./lab tudien <từ>` | tra thuật ngữ — 29 mục, gõ không dấu cũng ra |
| `./lab web` | dựng + mở trang đọc `lab.html` trong trình duyệt |
| `./lab dapan N` | đáp án đầy đủ |
| `./lab nap` / `nap2` | đổ dữ liệu đợt 1 / đợt 2 vào lake |
| `./lab run` / `run-full` | dbt run / dbt run --full-refresh |
| `./lab test` / `snapshot` | dbt test / dbt snapshot |
| `./lab dem` | đếm dòng từng tầng — công cụ soi bug chính |
| `./lab cay` | cây phụ thuộc (lineage) |
| `./lab sql <model>` | xem SQL dbt thật sự gửi xuống engine |
| `./lab soi "<sql>"` | chạy nhanh một câu SQL trên lab.duckdb |
| `./lab reset` | về trạng thái ban đầu, xoá tiến độ |

## Cách dùng cho đúng

0. **Đọc hết mục "Trước khi làm, hiểu đã" của mỗi bài.** Phần đó giải thích khái niệm từ số không — materialize, incremental, window function, SCD2 — trước khi bắt bạn dùng chúng. Gặp từ lạ giữa chừng thì `./lab tudien <từ>`, không cần rời terminal.
1. **Đọc đề, làm trước, bí mới xem gợi ý.** Gợi ý mở dần từng mức có lý do — xem hết một lượt thì mất phần lớn giá trị của bài.
2. **Sai là đúng quy trình.** Bài 3 và bài 4 CỐ TÌNH bắt bạn tạo ra dữ liệu sai rồi tự tìm. Ở công ty bạn không được phép làm thế.
3. **Một bài coi là xong** khi hôm sau bạn làm lại từ đầu, không Google, dưới 20 phút.

## Bản đồ: cái gì ở đây tương ứng cái gì ở công ty

| Lab này | Công ty bạn |
|---|---|
| `tools/nap_lake.py` đổ vào schema `lake` | Kafka Connect / Redpanda Connect (CDC) |
| DuckDB (file `lab.duckdb`) | BigQuery — sắp có thêm ClickHouse |
| `models/dwh/`, `models/mart/` | đúng 3 tầng lake / dwh / mart bên bạn |
| `./lab run` | Airflow gọi `dbt run` theo lịch |
| `./lab test` | dbt test trong CI, chặn PR |

**Phần dbt là giống nhau gần như 100%.** Đó là lý do lab này chạy trên DuckDB
mà vẫn dùng được: bạn tập cơ chế dbt, không tập DuckDB.

## Cái lab này KHÔNG dạy được

DuckDB không có, phải học trên BigQuery sandbox (bài 7):

- `partition_by` / `cluster_by`
- bytes scanned, slot, dry-run ước tính chi phí
- vài khác biệt phương ngữ SQL (`date_diff` là ví dụ rõ nhất)

Đây là ranh giới cần thuộc: **dbt lo logic và thứ tự, engine lo lưu trữ, tốc độ và chi phí.**

## Dữ liệu trong lab

Đơn đặt phòng khách sạn + dịch vụ đi kèm, trong đó có `SHUTTLE` (đưa đón).
Bảng cuối `mart_don_dua_don` = đơn đã xác nhận có dịch vụ đưa đón — cùng
hình dạng bài toán với task đầu tiên của bạn, nhưng dữ liệu hoàn toàn bịa.

Lake là **append-only**: sửa một đơn thì sinh dòng mới chứ không ghi đè —
đúng hành vi CDC. Toàn bộ bài 3, 4, 5 xoay quanh hệ quả của điều này.
