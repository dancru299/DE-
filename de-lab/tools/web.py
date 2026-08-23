# -*- coding: utf-8 -*-
"""Sinh trang đọc lab.html từ chính noi_dung.py + tu_dien.py.

Một nguồn nội dung duy nhất -> terminal và web không bao giờ lệch nhau.
Chạy: ./lab web
"""
import html as H
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from noi_dung import BAI
from tu_dien import TU_DIEN, BI_DANH

GOC = pathlib.Path(__file__).resolve().parent.parent
RA = GOC / "lab.html"

SO_REN_NGHE = "https://claude.ai/code/artifact/368badda-888d-4610-b708-12f806dedde4"
# bài lab nào rơi vào tuần nào của lộ trình 12 tuần
TUAN = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4}

# ---------------------------------------------------------------- tô màu code

TU_KHOA = (r"\b(select|from|where|qualify|over|row_number|count|distinct|having|"
           r"create|table|view|insert|delete|update|merge|union|desc|asc|limit|"
           r"cast|coalesce|sum|max|min|case|when|then|else|null|date_diff|with|"
           r"order by|group by|partition by|left join|inner join|drop)\b")

MAU = re.compile(
    r"(?P<jinja>\{\{[^}]*\}\}|\{%[^%]*%\})"
    r"|(?P<ghichu>&lt;-[^\n]*)"
    r"|(?P<chuoi>&#x27;[^&\n]*?&#x27;)"
    r"|^(?P<lui>[ \t]*)(?P<khoayaml>[a-z_]+)(?=:\s)"
    r"|(?P<tukhoa>" + TU_KHOA + r")", re.IGNORECASE | re.MULTILINE)


def _mau(m):
    if m.group("khoayaml"):
        return f'{m.group("lui")}<i class="t-khoayaml">{m.group("khoayaml")}</i>'
    for t in ("jinja", "ghichu", "chuoi", "tukhoa"):
        if m.group(t):
            return f'<i class="t-{t}">{m.group(t)}</i>'
    return m.group(0)


def ma(txt):
    return MAU.sub(_mau, H.escape(txt))


# ---------------------------------------------------------------- nhận dạng

DAU_MA = ("./lab ", "dbt ", "{{", "{%", "select ", "config(", "qualify",
          "version:", "name:", "config:", "snapshots:", "models:", "columns:",
          "data_tests:", "relation:", "strategy:", "bq query", "pip install",
          "gcloud ", "cd ", "from ", "left join", "inner join", "with ")

COT = re.compile(r"\S {2,}\S")
LENH = re.compile(r"(\./lab [a-z0-9\-]+(?:\s+[a-z0-9_\-\.]+)?)")
TRA = re.compile(r"^\s*(Tra thêm|Từ nào chưa rõ)\s*:\s*\./lab tudien\s*(.+)$")
MUC = re.compile(r"^(\s{0,3})(\d+\.|[a-dA-D]\)|-)\s+(.*)$")


def _lui(d):
    return len(d) - len(d.lstrip())


def loai_khoi_phang(dong):
    """Khối không còn lồng nhau: code, bảng canh cột, câu nhấn, hay văn xuôi?"""
    noi = "\n".join(dong)
    thap = noi.lower()
    if any(k in thap for k in DAU_MA):
        return "ma"
    if any(COT.search(d) for d in dong):
        return "canh"
    if len(dong) == 1 and dong[0].isupper() and len(dong[0]) > 10:
        return "nhan"
    return "van"


# ---------------------------------------------------------------- chuyển đổi

def _tach_cum(dong):
    """Vùng phẳng có cả code lẫn văn xuôi, ngăn nhau bằng dòng trống -> tách ra."""
    cum, hien = [], []
    for d in dong:
        if d.strip():
            hien.append(d)
        elif hien:
            cum.append(hien)
            hien = []
    if hien:
        cum.append(hien)
    return cum


def doan(phan, the="p", lop=""):
    t = " ".join(x.strip() for x in phan).strip()
    if not t:
        return ""
    t = H.escape(t)
    t = LENH.sub(r"<code>\1</code>", t)
    t = t.replace(" -- ", " — ").replace("-&gt;", "→")
    c = f' class="{lop}"' if lop else ""
    return f"<{the}{c}>{t}</{the}>"


def chip_tudien(d):
    m = TRA.match(d)
    if not m:
        return None
    ra = []
    for t in m.group(2).split("|"):
        t = t.strip()
        k = t if t in TU_DIEN else BI_DANH.get(t)
        if k:
            ra.append(f'<a class="chip" href="#tu-{k}">{H.escape(t)}</a>')
    return f'<p class="tra"><span>Tra thêm</span>{"".join(ra)}</p>' if ra else None


def sang_html(txt, nguong=4):
    dong = txt.split("\n")
    out, van = [], []
    i, n = 0, len(dong)

    def xa():
        if van:
            out.append(doan(van))
            van.clear()

    while i < n:
        d = dong[i]
        if not d.strip():
            xa()
            i += 1
            continue

        # ---------- danh sách (xét trước, để dấu đầu dòng không thành khối) ----------
        m = MUC.match(d)
        if m and _lui(d) <= 3:
            xa()
            thu_tu = bool(re.match(r"\d+\.", m.group(2)))
            muc = []
            while i < n:
                if not dong[i].strip():
                    j = i + 1
                    while j < n and not dong[j].strip():
                        j += 1
                    if j < n and MUC.match(dong[j]) and _lui(dong[j]) <= 3:
                        i = j
                        continue
                    break
                mm = MUC.match(dong[i])
                if not mm or _lui(dong[i]) > 3:
                    break
                cai = len(mm.group(1))
                phan = [mm.group(3)]
                i += 1
                while i < n and dong[i].strip() and _lui(dong[i]) > cai \
                        and not MUC.match(dong[i]):
                    phan.append(dong[i])
                    i += 1
                muc.append(doan(phan, "li"))
            the = "ol" if thu_tu else "ul"
            out.append(f"<{the}>{''.join(muc)}</{the}>")
            continue

        # ---------- vùng thụt lề ----------
        if _lui(d) >= nguong:
            xa()
            khoi = []
            while i < n:
                if not dong[i].strip():
                    j = i + 1
                    while j < n and not dong[j].strip():
                        j += 1
                    if j >= n or _lui(dong[j]) < nguong:
                        break
                    khoi.append("")
                    i = j
                    continue
                if _lui(dong[i]) < nguong:
                    break
                khoi.append(dong[i])
                i += 1
            while khoi and not khoi[-1].strip():
                khoi.pop()

            goc = min(_lui(x) for x in khoi if x.strip())
            lui_ra = [x[goc:] if x.strip() else "" for x in khoi]

            # còn lồng nhau -> đệ quy, để tầng trong tự phân loại
            if any(_lui(x) >= 4 for x in lui_ra if x.strip()):
                out.append(sang_html(chr(10).join(lui_ra), nguong))
                continue

            for cum in _tach_cum(lui_ra):
                loai = loai_khoi_phang(cum)
                if loai == "van":
                    # câu đơn ngay dưới một tiêu đề -> câu nhấn, không phải đoạn thường
                    if len(cum) == 1 and out and out[-1].startswith("<h3"):
                        out.append(f'<p class="nhan">{H.escape(cum[0].strip())}</p>')
                    else:
                        out.append(doan(cum))
                elif loai == "nhan":
                    out.append(f'<p class="nhan">{H.escape(cum[0])}</p>')
                elif loai == "canh":
                    out.append(f'<pre class="canh">{ma(chr(10).join(cum))}</pre>')
                else:
                    out.append('<div class="ma"><button class="chep" type="button">'
                               f'chép</button><pre>{ma(chr(10).join(cum))}</pre></div>')
            continue

        # ---------- dòng tra từ điển ----------
        c = chip_tudien(d)
        if c:
            xa()
            out.append(c)
            i += 1
            continue

        t = d.strip()
        if re.match(r"^(PHẦN|BƯỚC)\s+\d+", t):
            xa()
            out.append(f"<h3>{H.escape(t)}</h3>")
        elif re.match(r"^\d\)\s", t):
            xa()
            out.append(f"<h4>{H.escape(t)}</h4>")
        elif t.isupper() and len(t) > 6 and sum(x.isalpha() for x in t) > 4:
            xa()
            out.append(f"<h3>{H.escape(t)}</h3>")
        else:
            van.append(t)
        i += 1

    xa()
    return "\n".join(x for x in out if x)


def tien_do():
    f = GOC / ".tien_do.json"
    if f.exists():
        try:
            return set(json.loads(f.read_text()).get("xong", []))
        except Exception:
            pass
    return set()


# ---------------------------------------------------------------- dựng trang

CSS = """
:root{
  --ground:#F5F3F2; --surface:#FFFFFF; --sunk:#EFEBEA; --sunk2:#E8E2E1;
  --ink:#1E1A1B; --muted:#6B6265; --faint:#918789;
  --line:#E4DEDD; --line-strong:#CFC6C5;
  --accent:#8A2E3B; --accent-soft:#F5E7E9;
  --ok:#3F7A55; --wait:#9A6A1F;
  --k-key:#8A2E3B; --k-jinja:#1F6F6B; --k-str:#7A5A12; --k-note:#8C8285; --k-yaml:#2F5A96;
  --mono:ui-monospace,"JetBrains Mono","SF Mono","DejaVu Sans Mono",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Cantarell,Ubuntu,"Helvetica Neue",sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#161314; --surface:#1E1A1B; --sunk:#241F21; --sunk2:#2B2426;
  --ink:#EDE7E6; --muted:#A79D9F; --faint:#7C7274;
  --line:#332C2E; --line-strong:#4A4143;
  --accent:#D98A94; --accent-soft:#38252A;
  --ok:#7FB894; --wait:#D3A857;
  --k-key:#D98A94; --k-jinja:#6FC0BA; --k-str:#D8B872; --k-note:#8A8083; --k-yaml:#8FB4E3;
}}
:root[data-theme="dark"]{
  --ground:#161314; --surface:#1E1A1B; --sunk:#241F21; --sunk2:#2B2426;
  --ink:#EDE7E6; --muted:#A79D9F; --faint:#7C7274;
  --line:#332C2E; --line-strong:#4A4143;
  --accent:#D98A94; --accent-soft:#38252A;
  --ok:#7FB894; --wait:#D3A857;
  --k-key:#D98A94; --k-jinja:#6FC0BA; --k-str:#D8B872; --k-note:#8A8083; --k-yaml:#8FB4E3;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);
  font-size:16.5px;line-height:1.72;-webkit-font-smoothing:antialiased}
.khung{display:grid;grid-template-columns:262px minmax(0,1fr);gap:0;
  max-width:1180px;margin:0 auto}

/* ---- cột trái ---- */
.ben{position:sticky;top:0;height:100vh;overflow-y:auto;padding:26px 20px 30px;
  border-right:1px solid var(--line)}
.hieu{font-family:var(--mono);font-size:12px;letter-spacing:.15em;text-transform:uppercase;
  color:var(--accent);font-weight:600;margin:0 0 3px}
.hieu-phu{font-size:12.5px;color:var(--faint);margin:0 0 18px}
.do{height:5px;background:var(--sunk2);border-radius:99px;overflow:hidden;margin-bottom:6px}
.do i{display:block;height:100%;background:var(--ok)}
.do-so{font-family:var(--mono);font-size:11.5px;color:var(--faint);margin-bottom:20px}
nav ol{list-style:none;margin:0 0 22px;padding:0;display:flex;flex-direction:column;gap:1px}
nav a{display:flex;gap:9px;align-items:baseline;padding:7px 9px;border-radius:5px;
  text-decoration:none;color:var(--muted);font-size:13.6px;line-height:1.4}
nav a:hover{background:var(--sunk);color:var(--ink)}
nav a.dang{background:var(--accent-soft);color:var(--ink)}
nav a b{font-family:var(--mono);font-size:11.5px;color:var(--faint);flex:none;width:16px}
nav a.roi b{color:var(--ok)}
nav a.dang b{color:var(--accent)}
.tim{width:100%;padding:7px 10px;border:1px solid var(--line-strong);border-radius:5px;
  background:var(--surface);color:var(--ink);font-family:var(--mono);font-size:12.5px}
.tim:focus{outline:2px solid var(--accent);outline-offset:1px}
.doc{display:block;margin:18px 0 0;padding:11px 13px;border:1px solid var(--line-strong);
  border-radius:6px;text-decoration:none;background:var(--surface);line-height:1.45}
.doc:hover{border-color:var(--accent)}
.doc b{display:block;font-family:var(--mono);font-size:10.5px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--accent);margin-bottom:3px}
.doc span{font-size:12.5px;color:var(--muted)}
a.ve{color:var(--accent);text-decoration:none;border-bottom:1px dashed var(--line-strong)}
a.ve:hover{border-bottom-style:solid}
.nhac{margin:14px 0 0;padding-top:14px;border-top:1px solid var(--line);
  font-size:12.3px;color:var(--faint);line-height:1.6}
.nhac code{font-family:var(--mono);font-size:11.8px;color:var(--muted)}

/* ---- cột phải ---- */
main{padding:30px 40px 100px;min-width:0}
.dau{padding:26px 0 30px;border-bottom:2px solid var(--ink);margin-bottom:14px}
h1{font-family:var(--mono);font-size:clamp(26px,4vw,38px);line-height:1.08;
  letter-spacing:-.02em;margin:0 0 12px;text-wrap:balance}
.dau p{margin:0;color:var(--muted);max-width:64ch;font-size:15.5px}
section.bai{padding:44px 0;border-bottom:1px solid var(--line);scroll-margin-top:16px}
.so{font-family:var(--mono);font-size:11.5px;letter-spacing:.15em;text-transform:uppercase;
  color:var(--accent);margin:0 0 7px}
h2{font-size:26px;line-height:1.2;letter-spacing:-.015em;margin:0 0 14px;text-wrap:balance}
.y{display:flex;gap:12px;padding:13px 16px;background:var(--accent-soft);
  border-radius:6px;margin:0 0 8px;font-size:14.6px;max-width:70ch}
.y b{font-family:var(--mono);font-size:10.5px;letter-spacing:.11em;text-transform:uppercase;
  color:var(--accent);flex:none;padding-top:3px}
.gio{font-family:var(--mono);font-size:12px;color:var(--faint);margin:0 0 26px}
.moc{display:flex;align-items:center;gap:12px;margin:36px 0 20px}
.moc span{font-family:var(--mono);font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;
  color:var(--surface);background:var(--ink);padding:4px 9px;border-radius:3px;white-space:nowrap}
.moc i{flex:1;height:1px;background:var(--line-strong)}
main h3{font-family:var(--mono);font-size:14px;letter-spacing:.02em;font-weight:700;
  margin:32px 0 10px;color:var(--ink);text-wrap:balance}
main h4{font-size:16px;font-weight:650;margin:26px 0 8px;color:var(--ink)}
main p{margin:0 0 14px;max-width:68ch}
main ul,main ol{margin:0 0 16px;padding-left:22px;max-width:68ch}
main li{margin-bottom:7px}
main code{font-family:var(--mono);font-size:.88em;background:var(--sunk);
  padding:1.5px 5px;border-radius:3px;color:var(--accent);white-space:nowrap}
p.nhan{border-left:3px solid var(--accent);padding:2px 0 2px 15px;margin:16px 0 18px;
  font-size:17px;font-weight:600;line-height:1.5;max-width:62ch}
p.tra{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin:18px 0 20px}
p.tra span{font-family:var(--mono);font-size:10.5px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--faint)}
.chip{font-family:var(--mono);font-size:12px;text-decoration:none;color:var(--muted);
  background:var(--sunk);border:1px solid var(--line);padding:2px 9px;border-radius:99px}
.chip:hover{color:var(--accent);border-color:var(--accent)}

/* ---- khối mã ---- */
.ma{position:relative;margin:0 0 18px;border:1px solid var(--line);border-radius:7px;
  background:var(--sunk);overflow:hidden}
.ma pre{margin:0;padding:15px 18px;overflow-x:auto}
.chep{position:absolute;top:7px;right:7px;font-family:var(--mono);font-size:10.5px;
  letter-spacing:.08em;text-transform:uppercase;background:var(--surface);color:var(--faint);
  border:1px solid var(--line-strong);border-radius:4px;padding:3px 8px;cursor:pointer;opacity:0}
.ma:hover .chep,.chep:focus{opacity:1}
.chep.xong{color:var(--ok);border-color:var(--ok)}
pre{font-family:var(--mono);font-size:13.2px;line-height:1.62;margin:0 0 18px;
  overflow-x:auto;color:var(--ink)}
pre.canh{background:transparent;border-left:2px solid var(--line-strong);
  padding:3px 0 3px 16px;color:var(--muted);font-size:13px}
.t-tukhoa{font-style:normal;color:var(--k-key);font-weight:600}
.t-jinja{font-style:normal;color:var(--k-jinja)}
.t-chuoi{font-style:normal;color:var(--k-str)}
.t-ghichu{font-style:normal;color:var(--k-note)}
.t-khoayaml{font-style:normal;color:var(--k-yaml);font-weight:600}

/* ---- gợi ý / đáp án ---- */
details{border:1px solid var(--line);border-radius:7px;background:var(--surface);
  margin-bottom:9px;max-width:74ch}
details[open]{background:var(--surface)}
summary{cursor:pointer;padding:11px 15px;font-family:var(--mono);font-size:12.5px;
  color:var(--muted);list-style:none;display:flex;justify-content:space-between;gap:10px}
summary::-webkit-details-marker{display:none}
summary:hover{color:var(--ink)}
summary b{color:var(--accent);font-weight:600}
details .noi{padding:0 15px 14px;font-size:14.5px}
details .noi pre{font-size:12.8px}
.canhbao summary b{color:var(--wait)}

/* ---- từ điển ---- */
.tu{padding:16px 0;border-bottom:1px solid var(--line);scroll-margin-top:16px}
.tu h3{margin:0 0 8px;font-size:13.5px}
.tu.an{display:none}
#khong{color:var(--faint);font-size:14px;padding:20px 0;display:none}

@media (max-width:900px){
  .khung{grid-template-columns:1fr}
  .ben{position:static;height:auto;border-right:none;border-bottom:1px solid var(--line)}
  nav ol{flex-direction:row;flex-wrap:wrap;gap:5px}
  nav a{background:var(--sunk);font-size:12.5px;padding:5px 9px}
  main{padding:22px 20px 80px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""


def _details(nhan, than, lop=""):
    return (f'<details class="{lop}"><summary><b>{nhan}</b><span>+</span></summary>'
            f'<div class="noi">{than}</div></details>')


def dung_trang():
    xong = tien_do()
    pt = int(len(xong) / len(BAI) * 100)

    nav = "".join(
        f'<li><a href="#bai-{n}" class="{"roi" if n in xong else ""}" data-bai="{n}">'
        f'<b>{"✓" if n in xong else f"{n:02d}"}</b><span>{H.escape(b["ten"])}</span></a></li>'
        for n, b in BAI.items())

    than = []
    for n, b in BAI.items():
        goi = "".join(
            _details(f"Gợi ý {i + 1}", sang_html(g, nguong=2))
            for i, g in enumerate(b["goi_y"]))
        dap = _details("Đáp án — chỉ mở khi đã thử thật sự",
                       sang_html(b["dap_an"], nguong=2), "canhbao")
        than.append(f'''<section class="bai" id="bai-{n}">
<p class="so">Bài {n:02d}{" · đã xong" if n in xong else ""}</p>
<h2>{H.escape(b["ten"])}</h2>
<p class="y"><b>Ý chính</b><span>{H.escape(b["hoc"])}</span></p>
<p class="gio">{H.escape(b["thoi_gian"])} · <a class="ve" href="{SO_REN_NGHE}#tuan-{TUAN[n]}"
   target="_blank" rel="noopener">tuần {TUAN[n]} của lộ trình 12 tuần &rarr;</a></p>
<div class="moc"><span>Trước khi làm, hiểu đã</span><i></i></div>
{sang_html(b["nen"])}
<div class="moc"><span>Làm</span><i></i></div>
{sang_html(b["de"])}
<div class="moc"><span>Bí thì mở</span><i></i></div>
{goi}{dap}
</section>''')

    tu = "".join(
        f'<article class="tu" id="tu-{k}" data-tu="{H.escape(k)}">'
        f'{sang_html(v, nguong=2)}</article>'
        for k, v in sorted(TU_DIEN.items()))

    return f"""<meta charset="utf-8">
<title>Cẩm Nang DE Lab</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{CSS}</style>
<div class="khung">
<aside class="ben">
  <p class="hieu">DE Lab</p>
  <p class="hieu-phu">Đọc ở đây · làm ở terminal</p>
  <div class="do"><i style="width:{pt}%"></i></div>
  <p class="do-so">{len(xong)}/{len(BAI)} bài xong</p>
  <nav><ol>{nav}</ol></nav>
  <input class="tim" id="tim" type="search" placeholder="tìm thuật ngữ…"
         aria-label="Tìm thuật ngữ">
  <a class="doc" href="{SO_REN_NGHE}" target="_blank" rel="noopener">
    <b>Lộ trình 12 tuần</b><span>Lab + việc thật ở công ty + bằng chứng &rarr;</span></a>
  <p class="nhac">Trang này sinh ra từ chính nội dung lab.<br>
    Cập nhật tiến độ: chạy lại <code>./lab web</code></p>
</aside>
<main>
  <header class="dau">
    <h1>Cẩm nang DE Lab</h1>
    <p>Bảy bài thực hành dbt trên DuckDB, cho người mới hoàn toàn với data.
       Phần giảng đọc ở trang này; phần chạy lệnh và chấm bài vẫn ở terminal.</p>
  </header>
  {"".join(than)}
  <section class="bai" id="tudien">
    <p class="so">Tra cứu</p>
    <h2>Từ điển thuật ngữ</h2>
    <p>{len(TU_DIEN)} mục. Ở terminal tra bằng <code>./lab tudien &lt;từ&gt;</code>.</p>
    {tu}
    <p id="khong">Không có mục nào khớp.</p>
  </section>
</main>
</div>
<script>
function bao(b){{b.textContent="đã chép";b.classList.add("xong");
  setTimeout(()=>{{b.textContent="chép";b.classList.remove("xong")}},1400);}}
function luiChep(t,b){{const a=document.createElement("textarea");a.value=t;
  a.style.cssText="position:fixed;opacity:0";document.body.appendChild(a);a.select();
  try{{document.execCommand("copy");bao(b);}}catch(e){{b.textContent="ctrl+c";}}
  a.remove();}}
document.querySelectorAll(".chep").forEach(b=>b.addEventListener("click",()=>{{
  const t=b.parentElement.querySelector("pre").innerText;
  if(navigator.clipboard&&window.isSecureContext){{
    navigator.clipboard.writeText(t).then(()=>bao(b)).catch(()=>luiChep(t,b));
  }}else{{luiChep(t,b);}}
}}));
const lien=[...document.querySelectorAll("nav a")];
const qs=new IntersectionObserver(es=>{{
  es.forEach(e=>{{if(e.isIntersecting){{
    const id=e.target.id.replace("bai-","");
    lien.forEach(a=>a.classList.toggle("dang",a.dataset.bai===id));
  }}}});
}},{{rootMargin:"-15% 0px -75% 0px"}});
document.querySelectorAll("section.bai[id^=bai-]").forEach(s=>qs.observe(s));
const o=document.getElementById("tim"),mu=[...document.querySelectorAll(".tu")],
      kh=document.getElementById("khong");
o.addEventListener("input",()=>{{
  const q=o.value.trim().toLowerCase();
  if(q&&!location.hash.startsWith("#tudien"))document.getElementById("tudien").scrollIntoView();
  let n=0;
  mu.forEach(m=>{{
    const hop=!q||m.dataset.tu.includes(q)||m.textContent.toLowerCase().includes(q);
    m.classList.toggle("an",!hop); if(hop)n++;
  }});
  kh.style.display=n?"none":"block";
}});
</script>"""


if __name__ == "__main__":
    RA.write_text(dung_trang(), encoding="utf-8")
    print(f"Đã dựng: {RA}")
