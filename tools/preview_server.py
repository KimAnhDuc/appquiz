"""
Preview server for the "Đố Vui" quiz UI – run on a PC, no TV/emulator needed.

Serves the real app/src/main/assets/{tv,phone}.html, questions.json and img/,
and mimics QuizEngine.kt (same API, same rules, same timings).
Optional bot players auto-join and auto-answer so one person can play a whole game.

    python tools/preview_server.py            # 2 bots, port 8080
    python tools/preview_server.py --bots 0   # real players only
    python tools/preview_server.py --fast     # short timers (8s question / 4s reveal)
    python tools/preview_server.py --category "Quốc kỳ"   # only one category

Open:  http://localhost:8080/tv  (TV screen)   http://localhost:8080/  (phone)
Phones on the same Wi-Fi can use http://<PC-IP>:8080/
Dev-only: this file is not part of the APK.
"""
import argparse
import json
import mimetypes
import random
import socket
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "app" / "src" / "main" / "assets"
CONTENT = ROOT / "quiz-content"  # output of build_questions.py (the "online" content)

MIN_PLAYERS, MAX_PLAYERS, MAX_NAME_LEN = 1, 12, 12
BASE_POINTS, SPEED_BONUS = 500, 500
ACTIVE_TIMEOUT, LOBBY_TIMEOUT = 15, 30
COLORS = ["#FF4F8B", "#42A5F5", "#66BB6A", "#FFCA28", "#AB47BC", "#FF7043",
          "#26C6DA", "#D4E157", "#8D6E63", "#EC407A", "#7E57C2", "#9CCC65"]
BOT_NAMES = ["Bot Tèo", "Bot Tí", "Bot Na", "Bot Bin", "Bot Su"]


def load_questions(use_online=True):
    """Online set (quiz-content/, if built) else the small bundled set – same fallback the TV app uses."""
    online = use_online and (CONTENT / "questions.json").exists()
    data = json.loads(((CONTENT if online else ASSETS) / "questions.json").read_text(encoding="utf-8"))
    out = []
    for q in data["questions"]:
        opts = q.get("options") or []
        ans = q.get("answer", 0)
        if len(opts) == 4 and ans in range(4):
            img = q.get("image") or None
            out.append(dict(category=q.get("category", "Tổng hợp"), text=q.get("q", ""), options=opts,
                            answer=ans, image=("/" + img.lstrip("/")) if img and not img.startswith("http") else img,
                            emoji=q.get("emoji") or None))
    return out, (data.get("version", "bundled") if online else "bundled"), ("online (preview)" if online else "offline")


def shuffled(q):
    order = random.sample(range(4), 4)
    return dict(q, options=[q["options"][i] for i in order], answer=order.index(q["answer"]))


class Engine:
    def __init__(self, bank, per_game, question_sec, reveal_sec, version="bundled", source="offline"):
        self.lock = threading.RLock()
        self.bank, self.per_game = bank, per_game
        self.bank_version, self.bank_source = version, source
        self.question_sec, self.reveal_sec = question_sec, reveal_sec
        self.deck, self.bots, self.join_url = [], set(), ""
        self.players = {}  # pid -> dict
        self.phase, self.game, self.index = "LOBBY", [], -1
        self.answers, self.deadline = {}, 0  # pid -> (choice, at)

    def current(self):
        return self.game[self.index] if 0 <= self.index < len(self.game) else None

    # ---- actions ----
    def join(self, raw, bot=False):
        with self.lock:
            if len(self.players) >= MAX_PLAYERS:
                return None, f"Phòng đã đủ {MAX_PLAYERS} người"
            base = " ".join(raw.split())[:MAX_NAME_LEN]
            if not base:
                return None, "Vui lòng nhập tên"
            name, n = base, 2
            while any(p["name"].lower() == name.lower() for p in self.players.values()):
                name, n = f"{base} {n}", n + 1
            used = {p["color"] for p in self.players.values()}
            color = next((c for c in COLORS if c not in used), COLORS[len(self.players) % len(COLORS)])
            pid = uuid.uuid4().hex[:8]
            self.players[pid] = dict(name=name, color=color, score=0, correct=0, last_gain=0,
                                     last_correct=None, last_seen=time.time())
            if bot:
                self.bots.add(pid)
            return pid, None

    def vip(self):
        # Preview-only tweak: bots can't press Start, so the first *human* is VIP.
        humans = (k for k in self.players if k not in self.bots)
        return next(humans, next(iter(self.players), None))

    def start_or_restart(self):
        with self.lock:
            if self.phase == "LOBBY" and len(self.players) >= MIN_PLAYERS and self.bank:
                self._start_game()
                return True
            if self.phase == "FINAL":
                self.phase = "LOBBY"
                return True
            return False

    def start(self, pid):
        with self.lock:
            return pid == self.vip() and self.start_or_restart()

    def again(self, pid):
        with self.lock:
            if pid != self.vip() or self.phase != "FINAL":
                return False
            self.phase = "LOBBY"
            return True

    def answer(self, pid, choice):
        with self.lock:
            if self.phase != "QUESTION" or pid not in self.players or pid in self.answers or choice not in range(4):
                return False
            self.answers[pid] = (choice, time.time())
            if all(p in self.answers for p in self._active()):
                self._reveal()
            return True

    # ---- clock ----
    def tick(self):
        with self.lock:
            now = time.time()
            for pid in self.bots:
                if pid in self.players:
                    self.players[pid]["last_seen"] = now
            if self.phase == "LOBBY":
                for pid in [k for k, p in self.players.items() if now - p["last_seen"] > LOBBY_TIMEOUT]:
                    del self.players[pid]
            elif self.phase == "QUESTION":
                if now >= self.deadline:
                    self._reveal()
                else:
                    self._bots_act()
            elif self.phase == "REVEAL" and now >= self.deadline:
                if self.index + 1 >= len(self.game):
                    self.phase = "FINAL"
                else:
                    self._next_question()

    def _bots_act(self):
        q = self.current()
        for pid in list(self.bots):
            if pid in self.players and pid not in self.answers and random.random() < 0.3:
                right = random.random() < 0.6
                choice = q["answer"] if right else random.choice([i for i in range(4) if i != q["answer"]])
                self.answer(pid, choice)
                if self.phase != "QUESTION":
                    return

    # ---- transitions ----
    def _start_game(self):
        for p in self.players.values():
            p.update(score=0, correct=0, last_gain=0, last_correct=None)
        self.game = []
        for _ in range(min(self.per_game, len(self.bank))):
            if not self.deck:
                self.deck = random.sample(self.bank, len(self.bank))
            self.game.append(shuffled(self.deck.pop()))
        self.index = -1
        self._next_question()

    def _next_question(self):
        self.index += 1
        self.answers = {}
        self.phase, self.deadline = "QUESTION", time.time() + self.question_sec

    def _reveal(self):
        q = self.current()
        for pid, p in self.players.items():
            a = self.answers.get(pid)
            p["last_correct"] = None if a is None else a[0] == q["answer"]
            if a and a[0] == q["answer"]:
                speed = min(1.0, max(0.0, (self.deadline - a[1]) / self.question_sec))
                p["last_gain"] = BASE_POINTS + round(SPEED_BONUS * speed)
                p["correct"] += 1
            else:
                p["last_gain"] = 0
            p["score"] += p["last_gain"]
        self.phase, self.deadline = "REVEAL", time.time() + self.reveal_sec

    def _active(self):
        now = time.time()
        return [k for k, p in self.players.items() if now - p["last_seen"] <= ACTIVE_TIMEOUT]

    # ---- state ----
    def state(self, pid):
        with self.lock:
            now = time.time()
            me = self.players.get(pid) if pid else None
            if me:
                me["last_seen"] = now
            timed = self.phase in ("QUESTION", "REVEAL")
            vip = self.vip()
            ranked = sorted(self.players, key=lambda k: (-self.players[k]["score"], -self.players[k]["correct"]))
            s = dict(
                phase=self.phase, index=self.index + 1,
                total=len(self.game) or min(self.per_game, len(self.bank)),
                remaining=max(0, int(self.deadline - now + 0.999)) if timed else 0,
                duration=self.question_sec, joinUrl=self.join_url, minPlayers=MIN_PLAYERS,
                bank=dict(count=len(self.bank), version=self.bank_version, source=self.bank_source),
                players=[dict(id=k, name=p["name"], color=p["color"], score=p["score"], correct=p["correct"],
                              vip=k == vip, active=now - p["last_seen"] <= ACTIVE_TIMEOUT,
                              done=self.phase == "QUESTION" and k in self.answers,
                              lastGain=p["last_gain"], lastCorrect=p["last_correct"])
                         for k, p in self.players.items()],
            )
            if me:
                a = self.answers.get(pid)
                s["me"] = dict(id=pid, name=me["name"], color=me["color"], score=me["score"], correct=me["correct"],
                               vip=pid == vip, choice=a[0] if a else None, lastGain=me["last_gain"],
                               lastCorrect=me["last_correct"], rank=ranked.index(pid) + 1)
            q = self.current()
            if q and timed:
                qj = dict(category=q["category"], text=q["text"], image=q["image"], emoji=q["emoji"], options=q["options"])
                if self.phase == "REVEAL":
                    counts = [0, 0, 0, 0]
                    for c, _ in self.answers.values():
                        counts[c] += 1
                    qj.update(answer=q["answer"], counts=counts)
                s["question"] = qj
                nxt = self.game[self.index + 1] if self.index + 1 < len(self.game) else None
                s["preload"] = nxt["image"] if nxt else None
            return s


QR_PLACEHOLDER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<rect width="100" height="100" fill="#fff"/><g fill="#14101F">
<rect x="8" y="8" width="26" height="26"/><rect x="66" y="8" width="26" height="26"/><rect x="8" y="66" width="26" height="26"/>
</g><g fill="#fff"><rect x="13" y="13" width="16" height="16"/><rect x="71" y="13" width="16" height="16"/><rect x="13" y="71" width="16" height="16"/></g>
<g fill="#14101F"><rect x="17" y="17" width="8" height="8"/><rect x="75" y="17" width="8" height="8"/><rect x="17" y="75" width="8" height="8"/></g>
<text x="62" y="62" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#14101F">QR (preview)</text>
</svg>"""


def make_handler(engine):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, code, ctype, body):
            data = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def json(self, obj):
            self.send(200, "application/json; charset=utf-8", json.dumps(obj, ensure_ascii=False))

        def do_GET(self):
            u = urlparse(self.path)
            q = parse_qs(u.query)
            if u.path in ("/", "/tv"):
                name = "phone.html" if u.path == "/" else "tv.html"
                # Read on every request so HTML edits show up on browser refresh.
                return self.send(200, "text/html; charset=utf-8", (ASSETS / name).read_text(encoding="utf-8"))
            if u.path.startswith("/img/"):
                name = unquote(u.path[5:])
                f = next((d / "img" / name for d in (CONTENT, ASSETS) if (d / "img" / name).is_file()), None)
                if "/" in name or "\\" in name or ".." in name or f is None:
                    return self.send(404, "text/plain", "Not found")
                ctype = "image/svg+xml" if f.suffix == ".svg" else (mimetypes.guess_type(f.name)[0] or "application/octet-stream")
                return self.send(200, ctype, f.read_bytes())
            if u.path == "/qr.png":
                return self.send(200, "image/svg+xml", QR_PLACEHOLDER)
            if u.path == "/api/state":
                return self.json(engine.state(q.get("pid", [""])[0] or None))
            if u.path == "/dev/ok":  # simulate the OK button on the TV remote
                return self.json(dict(ok=engine.start_or_restart()))
            self.send(404, "text/plain", "Not found")

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            form = {k: v[0] for k, v in parse_qs(self.rfile.read(length).decode("utf-8")).items()}
            pid, path = form.get("pid", ""), urlparse(self.path).path

            def res(ok, err):
                return self.json(dict(ok=True) if ok else dict(ok=False, error=err))

            if path == "/api/join":
                new_pid, err = engine.join(form.get("name", ""))
                return self.json(dict(ok=True, pid=new_pid) if new_pid else dict(ok=False, error=err))
            if path == "/api/start":
                return res(engine.start(pid), "Chỉ VIP mới bắt đầu được")
            if path == "/api/again":
                return res(engine.again(pid), "Không thể chơi lại lúc này")
            if path == "/api/answer":
                try:
                    choice = int(form.get("choice", "-1"))
                except ValueError:
                    choice = -1
                return res(engine.answer(pid, choice), "Hết giờ hoặc bạn đã trả lời rồi")
            self.send(404, "text/plain", "Not found")

    return Handler


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # no packet is sent; just picks the LAN interface
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--bots", type=int, default=2, help="number of auto players (0-5)")
    ap.add_argument("--questions", type=int, default=10, help="questions per game")
    ap.add_argument("--bundled", action="store_true", help="use only the small question set bundled in the APK")
    ap.add_argument("--category", help='only questions of this category, e.g. "Quốc kỳ"')
    ap.add_argument("--fast", action="store_true", help="short timers for quick UI checks")
    a = ap.parse_args()

    q_sec, r_sec = (8, 4) if a.fast else (20, 8)
    bank, version, source = load_questions(not a.bundled)
    if a.category:
        bank = [q for q in bank if q["category"].lower() == a.category.lower()] or bank
    engine = Engine(bank, a.questions, q_sec, r_sec, version, source)
    engine.join_url = f"http://{lan_ip()}:{a.port}"
    for name in BOT_NAMES[:max(0, min(a.bots, 5))]:
        engine.join(name, bot=True)

    def ticker():
        while True:
            time.sleep(1)
            engine.tick()
    threading.Thread(target=ticker, daemon=True).start()

    server = ThreadingHTTPServer(("0.0.0.0", a.port), make_handler(engine))
    print(f"TV screen : http://localhost:{a.port}/tv")
    print(f"Phone     : http://localhost:{a.port}/   (other devices: {engine.join_url}/)")
    print(f"TV remote OK button: http://localhost:{a.port}/dev/ok")
    print(f"{len(bank)} questions loaded ({source}, v{version}) · bots: {a.bots} · timers: {q_sec}s/{r_sec}s — Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
