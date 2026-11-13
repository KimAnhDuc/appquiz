"""
Builds the online quiz content (questions + images) from open data.

    python tools/build_questions.py            # build everything into quiz-content/
    python tools/build_questions.py --refresh  # ignore the network cache and re-download

Sources (all free):
  * Wikidata (CC0)            – countries, capitals, currencies, landmarks, people, paintings, chemical elements
  * vi.wikipedia / Commons    – lead images of hand-picked names (see curated.py)
  * flagcdn.com               – country flags
Images are downloaded, shrunk to <=800px and stored in quiz-content/img/, so they are served from YOUR
host (GitHub Pages) and never hot-linked. Licences/authors go to quiz-content/credits.json.

Output (quiz-content/): questions.json, manifest.json, credits.json, img/*
Re-running is cheap: every network response and image is cached in tools/cache/.
"""
import argparse
import hashlib
import html
import io
import json
import random
import re
import sys
import time
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import unquote

import requests
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curated import CURATED, parse  # noqa: E402
import extra_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "quiz-content"
CACHE = Path(__file__).resolve().parent / "cache"
HAND_WRITTEN = ROOT / "app" / "src" / "main" / "assets" / "questions.json"

UA = {"User-Agent": "QuizBuilder/1.0 (hobby offline quiz generator; contact via repository owner)"}
SESSION = requests.Session()
SESSION.headers.update(UA)
REFRESH = False
random.seed(20261112)  # reproducible output

MAX_LABEL = 42
IMG_MAX = 800

# ------------------------------------------------------------------ network helpers


def cached_json(key, fetch):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (re.sub(r"[^A-Za-z0-9_.-]", "_", key)[:120] + "_" + hashlib.sha1(key.encode()).hexdigest()[:8] + ".json")
    if f.exists() and not REFRESH:
        return json.loads(f.read_text(encoding="utf-8"))
    data = fetch()
    f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def get(url, **kw):
    timeout = kw.pop("timeout", 60)
    budget = kw.pop("budget", None)  # max seconds to keep retrying (None = no limit)
    started = time.time()
    for attempt in range(5):
        if budget and time.time() - started > budget:
            return None
        try:
            r = SESSION.get(url, timeout=timeout, **kw)
            if r.status_code == 429:
                wait = min(float(r.headers.get("Retry-After", 5)), 90) + attempt * 3
                if budget and time.time() - started + wait > budget:
                    return None
                time.sleep(wait)
                continue
            if r.status_code >= 500:
                time.sleep(3 + attempt * 3)
                continue
            return r
        except requests.RequestException:
            time.sleep(3 + attempt * 3)
    return None


def sparql(name, query):
    def fetch():
        r = get("https://query.wikidata.org/sparql", params={"query": query},
                headers={"Accept": "application/sparql-results+json", **UA}, timeout=90)
        if r is None or r.status_code != 200:
            print(f"  ! sparql {name} failed ({getattr(r, 'status_code', 'no response')})")
            return []
        return r.json()["results"]["bindings"]
    rows = cached_json("sparql_" + name, fetch)
    print(f"  {name}: {len(rows)} rows")
    return rows


def val(row, key):
    return row[key]["value"] if key in row else None


def qid(uri):
    return uri.rsplit("/", 1)[-1]


def commons_name(url):
    return unquote(url.rsplit("/", 1)[-1]).replace("_", " ")


def ok_label(s):
    return bool(s) and len(s) <= MAX_LABEL and not re.fullmatch(r"Q\d+", s) and not s.isdigit()


VI = 'FILTER(LANG(?%s)="vi")'
# Atomic numbers of elements people actually know (H..Kr plus a few famous heavy ones)
COMMON_ELEMENTS = set(range(1, 37)) | {47, 50, 53, 54, 56, 74, 78, 79, 80, 82, 86, 88, 92, 94}

# ------------------------------------------------------------------ item pools
# An item is a dict: id, label, group, image (dict: commons=<file> | flag=<iso>), extra...


class Pools:
    def __init__(self):
        self.pools = defaultdict(list)

    def add(self, pool, **item):
        item["pool"] = pool
        self.pools[pool].append(item)

    def distractors(self, item, n=3, same_group=0.0, key="label"):
        """n wrong labels from the same pool; `same_group` = share taken from the same item['group']."""
        pool = [x for x in self.pools[item["pool"]] if x[key] and x[key].lower() != item[key].lower()]
        chosen, seen = [], {item[key].lower()}
        mates = [x for x in pool if item.get("group") and x.get("group") == item.get("group")]
        random.shuffle(mates)
        for x in mates[: round(n * same_group)]:
            if x[key].lower() not in seen:
                chosen.append(x[key]); seen.add(x[key].lower())
        random.shuffle(pool)
        for x in pool:
            if len(chosen) >= n:
                break
            if x[key].lower() not in seen:
                chosen.append(x[key]); seen.add(x[key].lower())
        return chosen if len(chosen) == n else None


def collect_wikidata(P):
    print("Wikidata: countries")
    rows = sparql("countries", f"""SELECT ?c ?l ?iso ?capl ?contl ?curl WHERE {{
      ?c wdt:P31 wd:Q3624078; wdt:P297 ?iso; rdfs:label ?l {VI % 'l'}
      OPTIONAL {{ ?c wdt:P36 ?cap. ?cap rdfs:label ?capl {VI % 'capl'} }}
      OPTIONAL {{ ?c wdt:P30 ?cont. ?cont rdfs:label ?contl {VI % 'contl'} }}
      OPTIONAL {{ ?c wdt:P38 ?cur. ?cur rdfs:label ?curl {VI % 'curl'} }} }}""")
    agg = {}
    for r in rows:
        c = agg.setdefault(qid(val(r, "c")), dict(label=val(r, "l"), iso=val(r, "iso"), cap=set(), cont=set(), cur=set()))
        for k, f in (("cap", "capl"), ("cont", "contl"), ("cur", "curl")):
            if val(r, f):
                c[k].add(val(r, f))
    for cid, c in agg.items():
        if not ok_label(c["label"]) or not c["iso"]:
            continue
        cont = next(iter(c["cont"])) if len(c["cont"]) == 1 else None
        P.add("country", id=cid, label=c["label"], group=cont, iso=c["iso"].lower(),
              cap=next(iter(c["cap"])) if len(c["cap"]) == 1 else None,
              cur=next(iter(c["cur"])) if len(c["cur"]) == 1 else None)

    print("Wikidata: landmarks (UNESCO World Heritage)")
    seen = set()
    for r in sparql("landmarks", f"""SELECT ?s ?l ?img ?sl WHERE {{
      ?s wdt:P1435 wd:Q9259; wdt:P18 ?img; wikibase:sitelinks ?sl; rdfs:label ?l {VI % 'l'} }}
      ORDER BY DESC(?sl) LIMIT 400"""):
        i = qid(val(r, "s"))
        if i in seen or not ok_label(val(r, "l")):
            continue
        seen.add(i)
        P.add("landmark", id=i, label=val(r, "l"), image=dict(commons=commons_name(val(r, "img"))))

    print("Wikidata: people")
    occupations = {  # QID: (group label, min sitelinks, limit)
        "Q169470": ("nhà vật lý", 90, 40), "Q593644": ("nhà hóa học", 75, 25), "Q170790": ("nhà toán học", 90, 30),
        "Q11063": ("nhà thiên văn", 80, 20), "Q205375": ("nhà phát minh", 80, 25), "Q4964182": ("triết gia", 100, 30),
        "Q36180": ("nhà văn", 130, 45), "Q49757": ("nhà thơ", 130, 25), "Q36834": ("nhà soạn nhạc", 130, 35),
        "Q2526255": ("đạo diễn", 100, 30), "Q33999": ("diễn viên", 130, 40), "Q177220": ("ca sĩ", 130, 35),
        "Q937857": ("cầu thủ bóng đá", 90, 40), "Q3665646": ("cầu thủ bóng rổ", 80, 20),
        "Q10833314": ("vận động viên quần vợt", 80, 20), "Q82955": ("chính trị gia", 160, 40),
    }
    seen = set()
    for q_, (grp, min_sl, limit) in occupations.items():
        for r in sparql("people_" + q_, f"""SELECT ?s ?l ?img ?sl WHERE {{
          ?s wdt:P106 wd:{q_}; wdt:P18 ?img; wikibase:sitelinks ?sl; rdfs:label ?l {VI % 'l'} FILTER(?sl>{min_sl}) }}
          ORDER BY DESC(?sl) LIMIT {limit}"""):
            i = qid(val(r, "s"))
            if i in seen or not ok_label(val(r, "l")):
                continue
            seen.add(i)
            P.add("person", id=i, label=val(r, "l"), group=grp, image=dict(commons=commons_name(val(r, "img"))))

    print("Wikidata: paintings")
    painters = sparql("painters", f"""SELECT ?s ?l ?sl WHERE {{ ?s wdt:P106 wd:Q1028181; wikibase:sitelinks ?sl;
      rdfs:label ?l {VI % 'l'} FILTER(?sl>110) }} ORDER BY DESC(?sl) LIMIT 80""")
    pids = " ".join("wd:" + qid(val(r, "s")) for r in painters)
    seen = set()
    for r in sparql("paintings", f"""SELECT ?s ?l ?img ?a ?al ?sl WHERE {{ VALUES ?a {{ {pids} }}
      ?s wdt:P170 ?a; wdt:P31 wd:Q3305213; wdt:P18 ?img; wikibase:sitelinks ?sl; rdfs:label ?l {VI % 'l'}
      ?a rdfs:label ?al {VI % 'al'} FILTER(?sl>18) }} ORDER BY DESC(?sl) LIMIT 400"""):
        i = qid(val(r, "s"))
        if i in seen or not ok_label(val(r, "al")):
            continue
        seen.add(i)
        P.add("painting", id=i, label=val(r, "al"), title=val(r, "l"),  # label = painter (the answer)
              image=dict(commons=commons_name(val(r, "img"))))

    print("Wikidata: chemical elements")
    for r in sparql("elements", f"""SELECT ?e ?l ?sym ?num WHERE {{ ?e wdt:P31 wd:Q11344; wdt:P246 ?sym; wdt:P1086 ?num;
      rdfs:label ?l {VI % 'l'} FILTER(?num<=103) }}"""):
        if int(float(val(r, "num"))) in COMMON_ELEMENTS:
            P.add("element", id=qid(val(r, "e")), label=val(r, "l"), sym=val(r, "sym"))

    print("Wikidata: dishes")
    seen = set()
    for r in sparql("dishes", f"""SELECT ?s ?l ?img ?sl WHERE {{ ?s wdt:P31 wd:Q746549; wdt:P18 ?img; wikibase:sitelinks ?sl;
      rdfs:label ?l {VI % 'l'} }} ORDER BY DESC(?sl) LIMIT 120"""):
        i = qid(val(r, "s"))
        if i in seen or not ok_label(val(r, "l")):
            continue
        seen.add(i)
        P.add("dish", id=i, label=val(r, "l"), image=dict(commons=commons_name(val(r, "img"))))


def collect_curated(P):
    print("vi.wikipedia: curated lists")
    for group, (_cat, _wording, text) in CURATED.items():
        entries = parse(text)
        titles = [t for _, t in entries]
        images = {}
        for i in range(0, len(titles), 50):
            batch = titles[i:i + 50]

            def fetch(batch=batch):
                r = get("https://vi.wikipedia.org/w/api.php", params=dict(
                    action="query", format="json", redirects=1, prop="pageimages", piprop="name",
                    titles="|".join(batch)))
                return r.json() if r is not None and r.status_code == 200 else {}
            data = cached_json("vipages_" + "|".join(batch), fetch).get("query", {})
            rename = {}
            for n in data.get("normalized", []):
                rename[n["from"]] = n["to"]
            for n in data.get("redirects", []):
                rename[n["from"]] = n["to"]
            pages = {p["title"]: p for p in data.get("pages", {}).values()}
            for t in batch:
                cur = t
                for _ in range(3):
                    cur = rename.get(cur, cur)
                p = pages.get(cur)
                if p and p.get("pageimage"):
                    images[t] = p["pageimage"]
        used = set()
        for label, title in entries:
            img = images.get(title)
            if not img or img in used or not ok_label(label) or img.lower().endswith((".svg", ".gif", ".webm", ".ogv", ".pdf")) and group != "vn_places":
                continue
            used.add(img)
            P.add("cur_" + group, id=title, label=label, group=group, image=dict(commons=img.replace("_", " ")))
        print(f"  {group}: {len([x for x in P.pools['cur_' + group]])}/{len(entries)} with images")


# ------------------------------------------------------------------ question builders

def pick(lst):
    return random.choice(lst)


def make(P, item, text, correct, wrong, category, image=None, kind=""):
    if wrong is None or not correct:
        return None
    opts = [correct] + wrong
    if len({o.lower() for o in opts}) != 4:
        return None
    q = dict(id=hashlib.sha1(f"{kind}|{item['id']}".encode()).hexdigest()[:8], category=category, q=text, options=opts)
    if image:
        q["image"] = image
    return q


def build_questions(P):
    qs = defaultdict(list)  # bucket -> questions
    C = P.pools["country"]
    for c in C:
        flag = dict(flag=c["iso"])
        qs["flag"].append(make(P, c, pick(["Đây là quốc kỳ của nước nào?", "Lá cờ này thuộc quốc gia nào?"]),
                               c["label"], P.distractors(c, 3, 0.0), "Quốc kỳ", flag, "flag"))
        if c["cap"] and ok_label(c["cap"]):
            caps = [x for x in C if x["cap"] and x["cap"].lower() != c["cap"].lower()]
            random.shuffle(caps)
            mates = [x["cap"] for x in caps if c["group"] and x["group"] == c["group"]][:2]
            wrong = mates + [x["cap"] for x in caps if x["cap"] not in mates][: 3 - len(mates)]
            qs["capital"].append(make(P, c, pick(["Thủ đô của {} là thành phố nào?", "Đâu là thủ đô của {}?"]).format(c["label"]),
                                      c["cap"], wrong if len(wrong) == 3 else None, "Địa lý", flag, "capital"))
            qs["capital_rev"].append(make(P, c, f"{c['cap']} là thủ đô của quốc gia nào?", c["label"],
                                          P.distractors(c, 3, 0.67), "Địa lý", None, "caprev"))
        if c["cur"] and ok_label(c["cur"]):
            curs = list({x["cur"] for x in C if x["cur"] and x["cur"].lower() != c["cur"].lower() and ok_label(x["cur"])})
            random.shuffle(curs)
            qs["currency"].append(make(P, c, f"Đơn vị tiền tệ của {c['label']} là gì?", c["cur"], curs[:3] if len(curs) >= 3 else None,
                                       "Địa lý", None, "currency"))
        if c["group"]:
            conts = sorted({x["group"] for x in C if x["group"] and x["group"] != c["group"]})
            random.shuffle(conts)
            qs["continent"].append(make(P, c, f"{c['label']} thuộc châu lục nào?", c["group"], conts[:3] if len(conts) >= 3 else None,
                                        "Địa lý", None, "continent"))
    for x in P.pools["landmark"]:
        qs["landmark"].append(make(P, x, pick(["Đây là địa danh / di sản thế giới nào?", "Nơi trong hình là đâu?"]), x["label"],
                                   P.distractors(x, 3), "Địa danh", x["image"], "landmark"))
    by_group = defaultdict(list)
    for x in P.pools["person"]:
        by_group[x["group"]].append(make(P, x, pick(["Người trong ảnh là ai?", "Đây là chân dung của ai?"]), x["label"],
                                         P.distractors(x, 3, 1.0), "Nhân vật", x["image"], "person"))
    qs["person"] = [q for grp in by_group.values() for q in grp[:24]]  # cap per occupation for variety
    for x in P.pools["painting"]:
        qs["painting"].append(make(P, x, pick(["Ai là họa sĩ của bức tranh này?", "Bức tranh này do ai vẽ?"]), x["label"],
                                   P.distractors(x, 3), "Hội họa", x["image"], "painting"))
    el = P.pools["element"]
    for x in el:
        qs["element"].append(make(P, x, f"Ký hiệu hóa học của nguyên tố {x['label']} là gì?", x["sym"],
                                  [y["sym"] for y in random.sample([y for y in el if y["sym"] != x["sym"]], 3)], "Hóa học", None, "elsym"))
        qs["element"].append(make(P, x, f"Nguyên tố có ký hiệu {x['sym']} là gì?", x["label"],
                                  [y["label"] for y in random.sample([y for y in el if y["label"] != x["label"]], 3)], "Hóa học", None, "elname"))
    for x in P.pools["dish"]:
        qs["dish"].append(make(P, x, pick(["Món ăn / thức uống này là gì?", "Hình này là món gì?"]), x["label"],
                               P.distractors(x, 3), "Ẩm thực", x["image"], "dish"))
    for group, (category, wording, _t) in CURATED.items():
        for x in P.pools["cur_" + group]:
            qs["cur_" + group].append(make(P, x, pick(wording), x["label"], P.distractors(x, 3), category, x["image"], "cur"))
    return {k: [q for q in v if q] for k, v in qs.items()}


# ------------------------------------------------------------------ images

def commons_info(files):
    """file name -> dict(thumb, author, license, page) for Commons files (batched 50 per API call)."""
    info = {}
    files = sorted(set(files))
    for i in range(0, len(files), 50):
        batch = files[i:i + 50]

        def fetch(batch=batch):
            r = get("https://commons.wikimedia.org/w/api.php", params=dict(
                action="query", format="json", prop="imageinfo", iiprop="url|extmetadata|size|mime",
                iiurlwidth=IMG_MAX, titles="|".join("File:" + b for b in batch)))
            return r.json() if r is not None and r.status_code == 200 else {}
        data = cached_json("commons_" + "|".join(batch), fetch).get("query", {})
        norm = {n["to"]: n["from"] for n in data.get("normalized", [])}
        for p in data.get("pages", {}).values():
            ii = (p.get("imageinfo") or [None])[0]
            if not ii or not ii.get("mime", "").startswith("image/") or ii.get("width", 0) < 300:
                continue
            name = norm.get(p["title"], p["title"])[5:]
            meta = ii.get("extmetadata", {})
            clean = lambda k: html.unescape(re.sub(r"<[^>]+>", "", meta.get(k, {}).get("value", ""))).strip()  # noqa: E731
            info[name] = dict(thumb=ii.get("thumburl") or ii["url"], author=clean("Artist")[:120] or "unknown",
                              license=clean("LicenseShortName") or "see source",
                              page=ii.get("descriptionurl", ""))
        print(f"  commons metadata {min(i + 50, len(files))}/{len(files)}", end="\r")
    print()
    return info


def save_image(data, dest, png=False):
    im = Image.open(io.BytesIO(data))
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, "white")
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[3])
        im = bg
    im = im.convert("RGB")
    im.thumbnail((IMG_MAX, IMG_MAX), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if png:
        im.save(dest, "PNG", optimize=True)
    else:
        im.save(dest, "JPEG", quality=82, optimize=True, progressive=True)


def download(url, dest, png=False):
    if dest.exists():
        return True
    for _ in range(2):
        r = get(url, timeout=20, budget=45)
        if r is not None and r.status_code == 200 and r.content:
            try:
                save_image(r.content, dest, png)
                time.sleep(0.8)  # stay well under Wikimedia's thumbnail rate limit
                return True
            except Exception:
                return False
        time.sleep(1.5)
    return False


def process_images(questions):
    img_dir = OUT / "img"
    needed = [q["image"] for q in questions if "image" in q]
    info = commons_info([i["commons"] for i in needed if "commons" in i])
    credits, failed = {}, 0

    def fetch_one(q):
        spec = q["image"]
        if "flag" in spec:
            rel = f"img/flag_{spec['flag']}.png"
            ok = download(f"https://flagcdn.com/w640/{spec['flag']}.png", OUT / rel, png=True)
            return rel, ok, dict(author="flagcdn.com", license="Public domain flag", page="https://flagcdn.com")
        meta = info.get(spec["commons"])
        rel = f"img/{hashlib.sha1(spec['commons'].encode()).hexdigest()[:10]}.jpg"
        t0 = time.time()
        ok = bool(meta) and download(meta["thumb"], OUT / rel)
        print(f"  [{'ok' if ok else 'FAIL'} {time.time() - t0:4.1f}s] {spec['commons'][:60]}", flush=True)
        return rel, ok, meta

    from concurrent.futures import ThreadPoolExecutor
    with_img = [q for q in questions if "image" in q]
    with ThreadPoolExecutor(max_workers=1) as pool:  # Wikimedia answers 429 to parallel thumbnail requests
        results = list(pool.map(fetch_one, with_img))
    for n, (q, (rel, ok, credit)) in enumerate(zip(with_img, results), 1):
        q.pop("image", None)
        if ok:
            q["image"] = rel
            credits[rel] = credit
        else:
            failed += 1
            questions.remove(q)
        if n % 40 == 0:
            print(f"  images {n}/{len(needed)} (failed so far: {failed})", end="\r")
    print(f"\n  images done, {failed} questions dropped (no usable image)")
    return credits


# ------------------------------------------------------------------ main

def load_hand_written():
    if not HAND_WRITTEN.exists():
        return []
    out = []
    for q in json.loads(HAND_WRITTEN.read_text(encoding="utf-8"))["questions"]:
        if "image" in q:  # bundled-SVG questions are replaced by generated ones
            continue
        q = {k: v for k, v in q.items() if k != "answer" or v != 0}
        q["id"] = hashlib.sha1(("hand|" + q["q"]).encode()).hexdigest()[:8]
        out.append(q)
    return out


ORDERED = {"dish", "landmark"}  # query results come most-famous first; keep the head, don't sample randomly
CAPS = dict(flag=150, capital=80, capital_rev=70, currency=50, continent=40, landmark=200, person=330, painting=110,
            element=70, dish=45, cur_animals=130, cur_food=50, cur_vn_food=40, cur_vn_places=40, cur_vn_people=30,
            cur_instruments=40, cur_vehicles=40)


def main():
    global REFRESH
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--no-images", action="store_true", help="dry run: skip downloading images")
    a = ap.parse_args()
    REFRESH = a.refresh

    P = Pools()
    collect_wikidata(P)
    collect_curated(P)
    buckets = build_questions(P)

    questions = []
    print("\nQuestions per bucket (kept/available):")
    for k, v in buckets.items():
        if k not in ORDERED:
            random.shuffle(v)
        keep = v[:CAPS.get(k, 60)]
        questions += keep
        print(f"  {k:16} {len(keep):4}/{len(v)}")
    hand = load_hand_written()
    for q in extra_text.parse():
        q["id"] = hashlib.sha1(("extra|" + q["q"]).encode()).hexdigest()[:8]
        hand.append(q)
    print(f"  hand-written+extra {len(hand)}")

    if a.no_images:
        for q in questions:
            q.pop("image", None)
        credits = {}
    else:
        print("\nDownloading images…")
        credits = process_images(questions)
    questions += hand

    seen, unique = set(), []
    for q in questions:
        key = (q["q"], q["options"][0])
        if key not in seen:
            seen.add(key)
            unique.append(q)
    random.shuffle(unique)

    OUT.mkdir(exist_ok=True)
    version = date.today().strftime("%Y.%m.%d") + "." + hashlib.sha1(json.dumps(unique, sort_keys=True).encode()).hexdigest()[:6]
    (OUT / "questions.json").write_text(json.dumps(dict(version=version, questions=unique), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(dict(version=version, count=len(unique), updated=date.today().isoformat(),
                                                       questions="questions.json"), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "credits.json").write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    used = {q["image"] for q in unique if "image" in q}
    for f in (OUT / "img").glob("*") if (OUT / "img").exists() else []:  # drop orphaned images
        if f"img/{f.name}" not in used:
            f.unlink()
    size = sum(f.stat().st_size for f in (OUT / "img").glob("*")) / 1e6 if (OUT / "img").exists() else 0
    cats = defaultdict(int)
    for q in unique:
        cats[q["category"]] += 1
    print(f"\nTotal {len(unique)} questions ({sum(1 for q in unique if 'image' in q)} with images), images {size:.1f} MB, version {version}")
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {c:22} {n}")


if __name__ == "__main__":
    main()
