# Thư viện bài giảng

Tập hợp các bài giảng HTML rải rác trong workspace, gom về một chỗ và **xếp theo
đúng dòng chảy dữ liệu** — trùng với bản đồ 6 tầng trong bài `00-tong-quan`.

Mọi file đều **tự chứa**: mở thẳng bằng trình duyệt, không cần server, không cần mạng
(trừ phần font chữ, thiếu mạng thì tự rơi về font hệ thống).

> Đây là **bản sao**. Bản gốc vẫn nằm nguyên trong từng project — xem cột "Bản gốc"
> bên dưới. Sửa bản gốc thì bản sao ở đây không tự cập nhật theo.

## Thứ tự đọc gợi ý

Đọc `00` trước để có bản đồ tổng thể, rồi đi tuần tự `01` → `05`. Mỗi thư mục con
tương ứng một tầng trong bản đồ đó.

| # | Thư mục | Tầng trong bản đồ dữ liệu |
|---|---------|---------------------------|
| 00 | `00-tong-quan` | Toàn cảnh — đọc trước tiên |
| 01 | `01-nen-tang-ha-tang` | Nền tảng chạy mọi thứ |
| 02 | `02-thu-thap-du-lieu` | Tầng 2 — Thu thập |
| 03 | `03-luu-tru-truy-van` | Tầng 3 & 5 — Lưu trữ |
| 04 | `04-bien-doi-du-lieu` | Tầng 4 — Biến đổi **(có bài tập)** |
| 05 | `05-dieu-phoi` | Xuyên suốt — Điều phối |
| 06 | `06-van-hanh-trien-khai` | Xuyên suốt — Vận hành |

## Danh mục đầy đủ

### 00 — Tổng quan

| Bài | Nội dung | Bản gốc |
|-----|----------|---------|
| `data-engineering-toan-canh.html` | Bản đồ 6 tầng của hệ thống dữ liệu, phân biệt DE/DA/DS/AE/MLE, ETL vs ELT, ba lớp medallion, từ điển thuật ngữ, lộ trình 90 ngày | *soạn mới 2026-08-21* |

### 01 — Nền tảng hạ tầng

| Bài | Nội dung | Bản gốc |
|-----|----------|---------|
| `docker-nhap-mon.html` | Image / container / registry, Dockerfile, `-p` và `-v`, Compose, 5 lỗi người mới | *soạn mới 2026-08-21* |
| `kubernetes-nhap-mon.html` | Vòng lặp mong muốn vs thực tế, Pod / Deployment / Service / Ingress, kubectl, cách đọc lỗi | *soạn mới 2026-08-21* |

### 02 — Thu thập dữ liệu

| Bài | Nội dung | Bản gốc |
|-----|----------|---------|
| `kafka-connect-flow.html` | Luồng dữ liệu Kafka Connect (CDC) × Redpanda Connect | `Apache_Kafka/kafka-connect-flow.html` |
| `cdc-pipeline-simulator.html` | Trình giả lập pipeline CDC, chạy thử ngay trong trình duyệt | `Apache_Kafka/cdc-pipeline-simulator.html` |

### 03 — Lưu trữ & truy vấn

| Bài | Nội dung | Bản gốc |
|-----|----------|---------|
| `clickhouse-lab-mo-phong.html` | Mô phỏng ClickHouse — thấy tận mắt cơ chế bên trong | `ClickHouse/lab-mo-phong-clickhouse.html` |
| `clickhouse-materialized-view.html` | Materialized View: `page_views` → MV → `views_hourly` | `ClickHouse/bai4-mo-phong-mv.html` |

### 04 — Biến đổi dữ liệu

| Bài | Nội dung | Bản gốc |
|-----|----------|---------|
| `sql-cho-de.html` | Hàm cửa sổ, khử trùng, chia phiên, SCD2, idempotency, 4 cái bẫy im lặng, dbt từ `ref()` tới model incremental | *soạn mới 2026-08-21* |
| `bai-tap/` | **25 bài SQL + 7 bài dbt** chạy được ngay bằng DuckDB | *soạn mới 2026-08-21* |

Đây là mục duy nhất có phần thực hành. Bắt đầu bằng:

```bash
cd 04-bien-doi-du-lieu/bai-tap && ./chay.sh
```

Chi tiết trong [`04-bien-doi-du-lieu/bai-tap/README.md`](04-bien-doi-du-lieu/bai-tap/README.md).

### 05 — Điều phối

| Bài | Nội dung | Bản gốc |
|-----|----------|---------|
| `airflow-ui-huong-dan.html` | Hướng dẫn dùng giao diện Airflow | `Apache Spark/airflow_ui_guide/huong_dan_airflow_ui.html` |
| `mo-xe-mot-file-dag.html` | Mổ xẻ một file DAG, đọc từng phần | `ShopVN/huong-dan-doc-dag.html` |

### 06 — Vận hành & triển khai

| Bài | Nội dung | Bản gốc |
|-----|----------|---------|
| `gitlab-cicd-deploy-airflow.html` | Nghiên cứu pipeline CI/CD deploy Airflow từ GitLab | `ShopVN/research_gitlab_cicd_airflow.html` |

## Ghi chú cần nhớ

- **`airflow-ui-huong-dan.html` là file sinh tự động.** Bản gốc do
  `Apache Spark/airflow_ui_guide/build_guide.py` tạo ra. Muốn sửa nội dung thì sửa script
  rồi chạy lại, đừng sửa tay file HTML — chạy script là mất hết.
  File này cũng **không có thẻ `<title>`**, nên tab trình duyệt sẽ hiện tên file thay vì tiêu đề.
- **Bài tập SQL cần DuckDB**, đã có sẵn trên máy (`duckdb v1.5.5`). Phần dbt dùng
  venv riêng tại `04-bien-doi-du-lieu/bai-tap/dbt-lab/.venv` (**354 MB** — xoá được nếu không cần).
- **`de-lab/` cố ý không gom vào đây** — đó là thư mục lab đang làm việc, để nguyên tại chỗ.
- **`dbt + BigQuery/target/index.html` cũng không gom** — đó là tài liệu dbt sinh ra khi build,
  không phải bài giảng, và sẽ bị ghi đè mỗi lần chạy `dbt docs generate`.

## Bản online

Ba bài soạn mới cũng có bản đọc trên web:

- Docker — https://claude.ai/code/artifact/893118a7-1117-4e4f-bef5-9dbe8e5bb11d
- Kubernetes — https://claude.ai/code/artifact/88885fa4-0cba-4d33-9c47-8db779b41078
- Data Engineering — https://claude.ai/code/artifact/210da0ae-8dc4-4368-900b-88a849fc61e2
