"""
Nạp dữ liệu thô vào tầng LAKE của lab.duckdb.

Vì sao có file này?
  Tầng lake trong thực tế KHÔNG do dbt tạo ra. Nó do hệ thống khác đổ vào:
  Kafka Connect (CDC), Redpanda Connect, batch job, v.v.
  dbt chỉ ĐỌC nó qua source(). File này đóng vai "hệ thống khác" đó.

  Lake ở đây là append-only, giống hệt output của CDC: một booking bị sửa
  sẽ sinh ra một DÒNG MỚI chứ không ghi đè dòng cũ. Đây chính là lý do
  tầng dwh phải biết khử trùng lặp — bài 3 sẽ đụng vào chuyện này.
"""
import sys, pathlib, duckdb

GOC = pathlib.Path(__file__).resolve().parent.parent
DATA = GOC / "data"
DB = GOC / "lab.duckdb"

BANG = {
    "bookings":  ("bookings.csv",  "bookings_dot2.csv"),
    "services":  ("services.csv",  "services_dot2.csv"),
    "customers": ("customers.csv", "customers_dot2.csv"),
}


def nap(dot: int):
    con = duckdb.connect(str(DB))
    con.execute("create schema if not exists lake")

    if dot == 1:
        for ten, (f1, _) in BANG.items():
            con.execute(f"drop table if exists lake.{ten}")
            con.execute(
                f"create table lake.{ten} as "
                f"select * from read_csv_auto('{DATA / f1}', header=true)"
            )
        print("Đã nạp ĐỢT 1 vào lake (làm mới hoàn toàn).")
    else:
        for ten, (_, f2) in BANG.items():
            duong_dan = DATA / f2
            con.execute(
                f"insert into lake.{ten} "
                f"select * from read_csv_auto('{duong_dan}', header=true)"
            )
        print("Đã nạp ĐỢT 2 vào lake (CHÈN THÊM, không ghi đè).")

    print()
    print(f"{'bảng':<12} {'số dòng':>8} {'số key duy nhất':>16}")
    print("-" * 40)
    for ten, key in [("bookings", "booking_id"), ("services", "service_id"),
                     ("customers", "customer_id")]:
        n, k = con.execute(
            f"select count(*), count(distinct {key}) from lake.{ten}"
        ).fetchone()
        canh_bao = "   <-- có bản ghi trùng key!" if n != k else ""
        print(f"{ten:<12} {n:>8} {k:>16}{canh_bao}")
    con.close()


if __name__ == "__main__":
    dot = 2 if "--dot2" in sys.argv else 1
    nap(dot)
