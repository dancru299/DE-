# -*- coding: utf-8 -*-
"""Engine chạy & chấm bài của DE Lab. Đây là 'ông thầy' của lab này."""
import hashlib, json, os, pathlib, re, subprocess, sys, unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from noi_dung import BAI
from tu_dien import TU_DIEN, BI_DANH

GOC = pathlib.Path(__file__).resolve().parent.parent
DB = GOC / "lab.duckdb"
TIEN_DO = GOC / ".tien_do.json"
PY = GOC / "venv" / "bin" / "python"
DBT = GOC / "venv" / "bin" / "dbt"

X, V, W = "\033[32m", "\033[31m", "\033[33m"
D, R = "\033[2m", "\033[0m"


def env():
    e = os.environ.copy()
    e["DBT_PROFILES_DIR"] = str(GOC)
    return e


def chay(cmd, im=False):
    r = subprocess.run(cmd, cwd=GOC, env=env(), capture_output=True, text=True)
    out = r.stdout + r.stderr
    if not im:
        print(out)
    return r.returncode, out


def dbt(*a, im=False):
    return chay([str(DBT), *a], im=im)


def con():
    import duckdb
    return duckdb.connect(str(DB))


def hoi(sql):
    try:
        c = con()
        r = c.execute(sql).fetchall()
        c.close()
        return r
    except Exception as e:
        return ("LOI", str(e))


def co_bang(ten):
    r = hoi(f"select count(*) from {ten}")
    return not (isinstance(r, tuple) and r[0] == "LOI")


def _bo_dau(s):
    s = s.lower().strip().replace("đ", "d")
    return "".join(k for k in unicodedata.normalize("NFD", s)
                   if unicodedata.category(k) != "Mn")


def doc_td():
    if TIEN_DO.exists():
        return json.loads(TIEN_DO.read_text())
    return {"xong": [], "goi_y": {}}


def ghi_td(td):
    TIEN_DO.write_text(json.dumps(td, ensure_ascii=False, indent=2))


def danh_dau(n):
    td = doc_td()
    if n not in td["xong"]:
        td["xong"].append(n)
        td["xong"].sort()
        ghi_td(td)


# ---------------------------------------------------------------- CHẤM BÀI

def _nguon(p):
    f = GOC / p
    return f.read_text() if f.exists() else ""


def check1():
    ok, loi = True, []
    for b in ["dwh.stg_bookings", "dwh.stg_services", "dwh.stg_customers",
              "dwh.fct_bookings", "mart.mart_don_dua_don"]:
        if not co_bang(b):
            ok = False
            loi.append(f"chưa có bảng {b} -- chạy ./lab nap rồi ./lab run")
    f = GOC / "target/compiled/de_lab/models/dwh/fct_bookings.sql"
    if not f.exists():
        ok = False
        loi.append("chưa thấy file compiled -- chạy ./lab run")
    else:
        s = f.read_text()
        if "ref(" in s:
            ok = False
            loi.append("file compiled vẫn còn ref() -- có vẻ bạn đang mở nhầm file trong target/run/")
        else:
            print(f"{D}   trong file compiled, ref('stg_bookings') đã thành:{R}")
            for d in s.splitlines():
                if "stg_bookings" in d:
                    print(f"{D}      {d.strip()}{R}")
    return ok, loi


def check2():
    ok, loi = True, []
    src = _nguon("models/mart/mart_don_dua_don.sql")
    if "ref('stg_customers')" not in src and 'ref("stg_customers")' not in src:
        ok = False
        loi.append("chưa thấy ref('stg_customers') trong models/mart/mart_don_dua_don.sql")
    if '"dwh"."stg_customers"' in src or "dwh.stg_customers" in src:
        ok = False
        loi.append("đang viết tên bảng cứng -- phải thay bằng ref('stg_customers')")
    cot = [r[0] for r in hoi("select column_name from information_schema.columns "
                             "where table_schema='mart' and table_name='mart_don_dua_don'")]
    if "ho_ten" not in cot:
        ok = False
        loi.append(f"bảng mart chưa có cột ho_ten (đang có: {', '.join(cot)}) -- nhớ chạy ./lab run sau khi sửa")
    else:
        n = hoi("select count(*) from mart.mart_don_dua_don where ho_ten is null")[0][0]
        if n:
            ok = False
            loi.append(f"{n} dòng có ho_ten NULL -- join sai khoá?")
    if ok:
        for r in hoi("select booking_id, ho_ten from mart.mart_don_dua_don order by 1 limit 3"):
            print(f"{D}   {r[0]}  {r[1]}{R}")
    return ok, loi


def check3():
    ok, loi = True, []
    n = hoi("select count(*) from lake.bookings")
    if isinstance(n, tuple):
        return False, ["chưa có tầng lake -- chạy ./lab nap"]
    if n[0][0] < 18:
        return False, [f"lake.bookings mới có {n[0][0]} dòng, chưa nạp đợt 2 -- chạy ./lab nap2"]
    dup = hoi("select booking_id, count(*) from dwh.fct_bookings group by 1 having count(*)>1")
    if 3 in doc_td()["xong"]:
        print(f"{D}   (bài 3 đã hoàn thành trước đó){R}")
        return True, []
    if not dup:
        ok = False
        loi.append("chưa thấy dòng bị nhân đôi trong fct_bookings -- "
                   "bạn đã chạy ./lab run SAU khi nạp đợt 2 chưa?")
    else:
        print(f"{W}   tái hiện được lỗi -- các đơn bị nhân dòng:{R}")
        for b, c in dup:
            print(f"{D}      {b}: {c} dòng{R}")
    return ok, loi


def check4():
    ok, loi = True, []
    yml = _nguon("models/dwh/_models.yml") or _nguon("models/dwh/schema.yml")
    if not yml:
        return False, ["chưa có models/dwh/_models.yml"]
    if "fct_bookings" not in yml or "booking_id" not in yml:
        ok = False
        loi.append("_models.yml chưa khai báo cột booking_id của fct_bookings")
    if "unique" not in yml:
        ok = False
        loi.append("thiếu test `unique`")
    if "not_null" not in yml:
        ok = False
        loi.append("thiếu test `not_null`")
    src = _nguon("models/dwh/fct_bookings.sql")
    if "unique_key" not in src:
        ok = False
        loi.append("config của fct_bookings chưa có unique_key")
    if "qualify" not in src.lower():
        ok = False
        loi.append("chưa khử trùng lặp trong lô dữ liệu (QUALIFY) -- bài 5 sẽ rớt nếu thiếu")
    rc, out = dbt("test", "--select", "fct_bookings", im=True)
    if rc != 0:
        ok = False
        loi.append("`dbt test` chưa xanh:")
        for d in out.splitlines():
            if "FAIL" in d or "Failure" in d:
                loi.append("   " + d.strip())
    else:
        print(f"{D}   dbt test: PASS{R}")
    dup = hoi("select count(*) from (select booking_id from dwh.fct_bookings "
              "group by 1 having count(*)>1)")
    if not isinstance(dup, tuple) and dup[0][0]:
        ok = False
        loi.append(f"vẫn còn {dup[0][0]} booking_id bị trùng")
    return ok, loi


def _dau_van():
    r = hoi("select booking_id, trang_thai, tong_tien, cap_nhat_luc "
            "from dwh.fct_bookings order by booking_id")
    if isinstance(r, tuple):
        return None, 0
    return hashlib.md5(str(r).encode()).hexdigest()[:12], len(r)


def check5():
    ok, loi = True, []
    print(f"{D}   lần 1: dbt run (incremental)...{R}")
    dbt("run", "--select", "fct_bookings", "-q", im=True)
    h1, n1 = _dau_van()
    print(f"{D}   lần 2: dbt run lần nữa, không nạp thêm dữ liệu...{R}")
    dbt("run", "--select", "fct_bookings", "-q", im=True)
    h2, n2 = _dau_van()
    print(f"{D}   lần 3: dbt run --full-refresh (dựng lại từ đầu)...{R}")
    dbt("run", "--select", "fct_bookings", "--full-refresh", "-q", im=True)
    h3, n3 = _dau_van()

    print()
    print(f"      {'lần chạy':<26}{'số dòng':>9}   dấu vân tay dữ liệu")
    for ten, h, n in [("1. incremental", h1, n1), ("2. incremental lần nữa", h2, n2),
                      ("3. full-refresh", h3, n3)]:
        print(f"      {ten:<26}{n:>9}   {h}")
    print()
    if h1 != h2:
        ok = False
        loi.append("chạy lại lần 2 đã ra kết quả khác -- model KHÔNG idempotent")
    if h2 != h3:
        ok = False
        loi.append("full-refresh ra kết quả khác với incremental. "
                   "Gần như chắc chắn thiếu QUALIFY khử trùng lặp: incremental chỉ "
                   "thấy 6 dòng mới nên không lộ, full-refresh xử lý cả 18 dòng thì lộ.")
    if ok:
        print(f"{X}   cả 3 lần giống hệt nhau{R}")
    return ok, loi


def check6():
    if not (GOC / "snapshots/snap_customers.yml").exists() and \
       not (GOC / "snapshots/snap_customers.sql").exists():
        return False, ["chưa có file snapshots/snap_customers.yml"]

    print(f"{D}   dựng lại tình huống: về đợt 1 -> chụp ảnh -> nạp đợt 2 -> chụp ảnh...{R}")
    c = con(); c.execute("drop table if exists dwh.snap_customers"); c.close()
    chay([str(PY), "tools/nap_lake.py"], im=True)
    dbt("run", "-q", im=True)
    rc, out = dbt("snapshot", "-q", im=True)
    if rc != 0:
        return False, ["`dbt snapshot` lỗi:", *[d for d in out.splitlines() if "Error" in d or "error" in d][:6]]
    chay([str(PY), "tools/nap_lake.py", "--dot2"], im=True)
    dbt("run", "-q", im=True)
    dbt("snapshot", "-q", im=True)

    r = hoi("select email, thanh_pho, dbt_valid_to is null as dang_hieu_luc "
            "from dwh.snap_customers where customer_id='C002' order by dbt_valid_from")
    if isinstance(r, tuple):
        return False, ["không đọc được bảng dwh.snap_customers -- kiểm tra schema trong config"]
    ok, loi = True, []
    if len(r) != 2:
        ok = False
        loi.append(f"C002 phải có 2 dòng lịch sử, đang có {len(r)}. "
                   "Kiểm tra unique_key / strategy / updated_at trong file yml.")
    else:
        hl = [x for x in r if x[2]]
        if len(hl) != 1:
            ok = False
            loi.append(f"phải có đúng 1 dòng đang hiệu lực (dbt_valid_to null), đang có {len(hl)}")
        elif "binh.tran" not in hl[0][0]:
            ok = False
            loi.append(f"dòng đang hiệu lực phải là email mới, đang là {hl[0][0]}")
        else:
            print(f"{X}   lịch sử của C002:{R}")
            for e, tp, hieu_luc in r:
                print(f"{D}      {e:<40} {'<- đang hiệu lực' if hieu_luc else '(đã hết hiệu lực)'}{R}")
    return ok, loi


def check7():
    print(f"{W}   Bài 7 không chấm tự động.{R}")
    print("   Tự đánh dấu xong khi bạn đã chạy được `dbt run --target bq`,")
    print("   hoặc đã đọc hiểu phần (b)(c)(d) nếu chưa có sandbox:")
    print("       ./lab xong 7")
    return False, []


CHECK = {1: check1, 2: check2, 3: check3, 4: check4, 5: check5, 6: check6, 7: check7}


# ---------------------------------------------------------------- GIAO DIỆN

def bang_dieu_khien():
    td = doc_td()
    xong = td["xong"]
    print()
    print(f"  {'DE LAB':<44} {len(xong)}/7 bài")
    print("  " + "─" * 52)
    for n, b in BAI.items():
        if n in xong:
            dau, mau = "✓", X
        elif n == min([k for k in BAI if k not in xong], default=99):
            dau, mau = "▶", W
        else:
            dau, mau = " ", D
        print(f"  {mau}{dau} {n}. {b['ten']:<42}{R}{D}{b['thoi_gian']}{R}")
    print("  " + "─" * 52)
    ke = min([k for k in BAI if k not in xong], default=None)
    if ke:
        print(f"\n  Tiếp theo:  ./lab bai {ke}")
    else:
        print(f"\n  {X}Xong cả 7 bài.{R}")
    print(f"\n  {D}./lab bai N · check N · goiy N · dapan N · tudien <từ>{R}")
    print(f"  {W}./lab web{R}{D} — mở phần giảng ở trình duyệt cho dễ đọc{R}")
    print(f"  {D}./lab nap · nap2 · run · test · dem · cay · sql <model> · soi \"<sql>\" · reset{R}\n")


def in_bai(n):
    b = BAI[n]
    print()
    print(f"  {'━' * 66}")
    print(f"  BÀI {n}: {b['ten'].upper()}")
    print(f"  {'━' * 66}")
    print(f"  {W}Ý chính:{R} {b['hoc']}")
    print(f"  {D}Thời lượng: {b['thoi_gian']}{R}")
    if b.get("nen"):
        print()
        print(f"  {W}{'─' * 20} TRƯỚC KHI LÀM, HIỂU ĐÃ {'─' * 21}{R}")
        print(b["nen"])
        print(f"  {W}{'─' * 29} LÀM {'─' * 32}{R}")
    print(b["de"])
    print(f"  {D}Từ nào lạ: ./lab tudien <từ>     ·     Bí: ./lab goiy {n}{R}\n")


def in_goi_y(n):
    td = doc_td()
    da = td["goi_y"].get(str(n), 0)
    gy = BAI[n]["goi_y"]
    if da >= len(gy):
        print(f"\n  {W}Hết gợi ý rồi. Xem đáp án: ./lab dapan {n}{R}\n")
        return
    print(f"\n  {W}Gợi ý {da + 1}/{len(gy)}:{R}\n")
    for d in gy[da].split("\n"):
        print("    " + d)
    td["goi_y"][str(n)] = da + 1
    ghi_td(td)
    print(f"\n  {D}Chưa thông thì: ./lab goiy {n}{R}\n")


def main():
    a = sys.argv[1:]
    if not a:
        return bang_dieu_khien()
    c = a[0]

    if c == "bai":
        return in_bai(int(a[1]))
    if c == "goiy":
        return in_goi_y(int(a[1]))
    if c == "dapan":
        print(f"\n  {W}ĐÁP ÁN BÀI {a[1]}{R}")
        print(BAI[int(a[1])]["dap_an"], "\n")
        return
    if c == "xong":
        danh_dau(int(a[1]))
        print(f"  {X}Đã đánh dấu xong bài {a[1]}.{R}")
        return bang_dieu_khien()

    if c == "check":
        n = int(a[1])
        print(f"\n  Đang chấm bài {n}: {BAI[n]['ten']}\n")
        ok, loi = CHECK[n]()
        print()
        if ok:
            danh_dau(n)
            print(f"  {X}ĐẠT — bài {n} xong.{R}")
            ke = min([k for k in BAI if k not in doc_td()["xong"]], default=None)
            if ke:
                print(f"  Tiếp:  ./lab bai {ke}\n")
            else:
                print(f"  {X}Hết bài. Bạn vừa đi qua đủ vòng đời một model dbt.{R}\n")
        else:
            print(f"  {V}CHƯA ĐẠT{R}")
            for l in loi:
                print(f"    · {l}")
            print(f"\n  {D}./lab goiy {n}{R}\n")
        return

    if c == "nap":
        return chay([str(PY), "tools/nap_lake.py"])[0]
    if c == "nap2":
        return chay([str(PY), "tools/nap_lake.py", "--dot2"])[0]
    if c == "run":
        return dbt("run")[0]
    if c == "run-full":
        return dbt("run", "--full-refresh")[0]
    if c == "test":
        return dbt("test")[0]
    if c == "snapshot":
        return dbt("snapshot")[0]
    if c == "cay":
        _, out = dbt("ls", "--select", "+mart_don_dua_don", "--output", "path", im=True)
        duong = [d.strip() for d in out.splitlines()
                 if d.strip().startswith(("models/", "snapshots/"))
                 and d.strip().endswith(".sql")]
        tang = {"dwh": [], "mart": [], "khac": []}
        for d in duong:
            (tang["dwh"] if "/dwh/" in d else tang["mart"] if "/mart/" in d
             else tang["khac"]).append(d.split("/")[-1].replace(".sql", ""))
        print("\n  Thứ tự dbt sẽ chạy, tự suy ra từ ref()/source() -- không ai khai báo tay:\n")
        print(f"    {D}lake (nguồn -- bookings, services, customers; dbt chỉ đọc){R}")
        print(f"    {D}  |{R}")
        for ten, nhan in [("dwh", "dwh  (chuẩn hoá)"), ("mart", "mart (phục vụ)")]:
            if tang[ten]:
                print(f"    {W}{nhan}{R}")
                for m in sorted(set(tang[ten])):
                    print(f"       - {m}")
                if ten == "dwh":
                    print(f"    {D}  |{R}")
        print(f"\n  {D}Đổi một ref() trong model -> cây này tự đổi theo.{R}\n")
        return
    if c == "sql":
        f = GOC / f"target/compiled/de_lab/models/dwh/{a[1]}.sql"
        if not f.exists():
            f = GOC / f"target/compiled/de_lab/models/mart/{a[1]}.sql"
        if not f.exists():
            print(f"  {V}Chưa có file compiled. Chạy ./lab run trước.{R}")
            return
        print(f"\n  {D}--- SQL dbt thật sự gửi xuống engine ---{R}\n")
        print(f.read_text())
        return
    if c == "web":
        rc, out = chay([str(PY), "tools/web.py"], im=True)
        f = GOC / "lab.html"
        if rc or not f.exists():
            print(f"  {V}Dựng trang lỗi:{R}\n{out}")
            return
        print(f"\n  {X}Đã dựng trang đọc:{R} {f}")
        subprocess.run(["xdg-open", str(f)], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        print(f"  {D}Đang mở trong trình duyệt. Tick thêm bài rồi chạy lại để cập nhật tiến độ.{R}\n")
        return

    if c == "tudien":
        if len(a) < 2:
            print(f"\n  {W}TỪ ĐIỂN — {len(TU_DIEN)} mục. Tra bằng: ./lab tudien <từ>{R}\n")
            ds = sorted(TU_DIEN)
            for i in range(0, len(ds), 4):
                print("    " + "".join(f"{x:<17}" for x in ds[i:i + 4]))
            print()
            return
        tim = _bo_dau(" ".join(a[1:]))
        khoa = None
        for nguon in (TU_DIEN, BI_DANH):
            for k in nguon:
                if _bo_dau(k) == tim:
                    khoa = k if nguon is TU_DIEN else BI_DANH[k]
                    break
            if khoa:
                break
        if not khoa:
            gan = [k for k in list(TU_DIEN) + list(BI_DANH) if tim in _bo_dau(k) or _bo_dau(k) in tim]
            if len(gan) == 1:
                khoa = gan[0] if gan[0] in TU_DIEN else BI_DANH[gan[0]]
            elif gan:
                print(f"\n  {W}Ý bạn là mục nào?{R}  " + " · ".join(sorted(set(gan))[:8]) + "\n")
                return
            else:
                print(f"\n  {V}Chưa có mục '{' '.join(a[1:])}'.{R} Xem danh sách: ./lab tudien\n")
                return
        print()
        for d in TU_DIEN[khoa].strip().split("\n"):
            print("  " + d)
        print()
        return

    if c == "soi":
        r = hoi(a[1])
        if isinstance(r, tuple):
            print(f"  {V}{r[1]}{R}")
        else:
            for d in r:
                print("   ", d)
        return
    if c == "dem":
        print()
        print(f"  {'bảng':<26}{'dòng':>7}{'khoá duy nhất':>16}")
        print("  " + "─" * 49)
        for b, k in [("lake.bookings", "booking_id"), ("dwh.stg_bookings", "booking_id"),
                     ("dwh.fct_bookings", "booking_id"), ("mart.mart_don_dua_don", "booking_id")]:
            r = hoi(f"select count(*), count(distinct {k}) from {b}")
            if isinstance(r, tuple):
                print(f"  {b:<26}{'--':>7}{'chưa dựng':>16}")
            else:
                n, u = r[0]
                cb = f"  {V}<- lệch{R}" if n != u else ""
                print(f"  {b:<26}{n:>7}{u:>16}{cb}")
        print()
        return
    if c == "reset":
        for p in [DB, TIEN_DO]:
            p.unlink(missing_ok=True)
        chay([str(PY), "tools/nap_lake.py"])
        print(f"  {X}Đã reset về trạng thái ban đầu.{R}")
        return

    print(f"  {V}Không hiểu lệnh '{c}'. Chạy ./lab để xem danh sách.{R}")


if __name__ == "__main__":
    main()
