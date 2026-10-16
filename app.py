import copy
import datetime
import json
import os
import random
import time
from urllib.parse import quote
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components

# ───────────── EDIT THESE ─────────────
HOSTS = "Hyejin & Jay"                       # parents' names
REVEAL_ISO = "2026-11-09T16:00:00+01:00"  # reveal date/time with UTC offset
# 언어별로 보여줄 시간대 (Time zone shown for each language)
TZ_BY_LANG = {
    "English": "Europe/Berlin",
    "Korean (한국어)": "Asia/Seoul",
    "Traditional Chinese (繁體中文)": "Asia/Taipei",
}
DEBUG_DB = False   # 문제 해결 중에는 True: 화면에 DB 에러 내용을 보여줘요. 다 해결되면 False
# Host PIN: set HOST_PIN in Streamlit secrets (default below is only for testing!)
# ──────────────────────────────────────

st.set_page_config(page_title="Our Little Baby Reveal", page_icon="🎈", layout="centered", initial_sidebar_state="collapsed")

REVEAL_DT = datetime.datetime.fromisoformat(REVEAL_ISO)
DATA_FILE = "reveal_data.json"
DEFAULT = {"votes": {}, "secret": "", "started": False}

# ───────────── TRANSLATIONS ─────────────
T = {
    "English": {
        "eyebrow": "{h}'s celebration", "i1": "A little secret.", "i2": "A lot of love.",
        "isub": "{h} invite you to guess and share our sweetest surprise.",
        "rev": "Baby reveal", "start": "Let's start", "loved": "Loved ones: {n}. One little secret.",
        "n1": "First, let's", "n2": "get to know you.", "yn": "Your name", "yc": "Joining from (optional)",
        "inn": "Count me in", "needn": "Please enter your name.",
        "c1": "The sweetest", "c2": "countdown.", "rg": "I'm ready to guess",
        "cnote": "No need to wait. You can change your guess right up to the reveal.",
        "g1": "What's your", "g2": "little guess?", "girl": "A girl", "boy": "A boy",
        "mg": "That's my guess", "pick": "Please pick a team first.",
        "v1": "The sweetest", "v2": "split.", "va": "Currently voting as {n}",
        "tg": "Team Girl", "tb": "Team Boy", "vt": "votes", "wait": "Waiting for the host to start the reveal…",
        "smash": "Smash!", "chg": "Change my guess", "back": "← Back",
        "r1": "Small human.", "r2": "Big reveal energy.", "gather": "Gather your people. This is the good part.",
        "pop": "Let's pop the secret!", "rgirl": "It's a <span class='pk'>girl</span>!", "rboy": "It's a <span class='bl'>boy</span>!",
        "won": "Team {t} called it: {names}", "nobody": "Nobody guessed this one. Everyone wins!",
        "sg": "Team pink skies", "sb": "Team blue skies",
        "nh": "Please remember the exact name you enter here, including capital and lowercase letters. You will need it to change your guess later.",
        "host": "Host controls", "pin": "Host PIN", "secret": "The secret", "sel": "Select…",
        "save": "Save secret", "go": "Smash! Start the reveal", "reset": "Reset everything",
    },
    "Korean (한국어)": {
        "eyebrow": "루미의 젠더리빌", "i1": "공주님일까요?", "i2": "왕자님일까요?",
        "isub": "루미의 성별을 함께 맞혀보세요.",
        "rev": "성별 공개", "start": "시작하기", "loved": "참여한 가족: {n}명",
        "n1": "먼저,", "n2": "당신의 이름을 적어주세요.", "yn": "이름", "yc": "현재 계신 곳 (선택)",
        "inn": "다음", "needn": "이름을 입력해주세요.",
        "c1": "루미의 성별,", "c2": "공개까지 남은 시간은?", "rg": "성별 예측하러 가기",
        "cnote": "공개 직전까지 예측을 바꿀 수 있어요.",
        "g1": "공주님일까요?", "g2": "왕자님일까요?", "girl": "공주님", "boy": "왕자님",
        "mg": "이걸로 할게요", "pick": "먼저 팀을 선택해주세요.",
        "v1": "두근두근", "v2": "투표 현황.", "va": "{n}님으로 투표 중",
        "tg": "공주님 팀", "tb": "왕자님 팀", "vt": "표", "wait": "투표가 완료되었어요!",
        "smash": "펑!", "chg": "예측 바꾸기", "back": "← 뒤로",
        "r1": "두구두구두구.", "r2": "과연 결과는.", "gather": "지금부터 집중!",
        "pop": "눌러서 확인하기!", "rgirl": "루미는 <span class='pk'>공주님</span>!", "rboy": "루미는 <span class='bl'>왕자님</span>!",
        "won": "{t}이 맞혔어요: {names}", "nobody": "아무도 못 맞혔어요. 모두가 승자!",
        "sg": "핑크 팀", "sb": "블루 팀",
        "nh": "여기에 입력한 이름을 대문자·소문자까지 정확히 기억해 주세요. 나중에 예측을 바꿀 때 같은 이름을 입력해야 해요.",
        "host": "주최자 설정", "pin": "주최자 PIN", "secret": "비밀 성별", "sel": "선택…",
        "save": "저장", "go": "펑! 공개 시작", "reset": "모두 초기화",
    },
    "Traditional Chinese (繁體中文)": {
        "eyebrow": "Lumi 的性別揭曉派對", "i1": "Lumi 是小公主，", "i2": "還是小王子呢？",
        "isub": "{h} 邀請你一起來猜猜 Lumi 的性別！",
        "rev": "性別揭曉", "start": "開始", "loved": "已加入的家人：{n} 位",
        "n1": "首先，", "n2": "請告訴我們你的名字。", "yn": "你的名字", "yc": "你現在在哪裡？（選填）",
        "inn": "我要參加", "needn": "請輸入你的名字。",
        "c1": "Lumi 的", "c2": "性別倒數。", "rg": "我要來猜",
        "cnote": "揭曉前都可以修改答案喔！",
        "g1": "你的", "g2": "直覺是？", "girl": "小公主", "boy": "小王子",
        "mg": "就決定是這個！", "pick": "請先選擇一隊喔。",
        "v1": "緊張刺激的", "v2": "投票結果。", "va": "目前以 {n} 的身分投票",
        "tg": "小公主隊", "tb": "小王子隊", "vt": "票", "wait": "等待主辦人開始揭曉…",
        "smash": "砰！", "chg": "修改答案", "back": "← 返回",
        "r1": "咚咚咚咚咚…", "r2": "答案即將揭曉！", "gather": "接下來請集中注意力！",
        "pop": "Lumi 是…！！！", "rgirl": "Lumi 是<span class='pk'>小公主</span>！", "rboy": "Lumi 是<span class='bl'>小王子</span>！",
        "won": "{t}猜對了：{names}", "nobody": "沒有人猜中，大家都是贏家！",
        "sg": "粉紅天空隊", "sb": "藍色天空隊",
        "nh": "請記住你在這裡輸入的名字（包含大小寫），之後想修改答案時需要輸入相同的名字。",
        "host": "主辦人設定", "pin": "主辦人 PIN", "secret": "秘密性別", "sel": "請選擇…",
        "save": "儲存", "go": "砰！開始揭曉", "reset": "全部重設",
    },
}

# ───────────── STORAGE (Supabase if configured, else local file) ─────────────
@st.cache_resource
def sb_client():
    try:
        from supabase import create_client
        url = str(st.secrets["SUPABASE_URL"]).strip().strip('"').rstrip("/")
        for tail in ("/rest/v1", "/rest"):
            if url.endswith(tail):
                url = url[: -len(tail)]
        return create_client(url, str(st.secrets["SUPABASE_KEY"]).strip())
    except Exception:
        return None


def describe_error(e):
    parts = [getattr(e, k, "") for k in ("code", "message", "details", "hint")]
    text = " | ".join(str(x) for x in parts if x)
    return text or repr(e)


def load():
    sb = sb_client()
    if sb:
        try:
            rows = sb.table("kv").select("value").eq("key", "state").execute().data
            return rows[0]["value"] if rows else copy.deepcopy(DEFAULT)
        except Exception as e:
            st.session_state["db_error"] = describe_error(e)
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return copy.deepcopy(DEFAULT)


def save(state):
    sb = sb_client()
    if sb:
        try:
            sb.table("kv").upsert({"key": "state", "value": state}).execute()
            return
        except Exception as e:
            st.session_state["db_error"] = describe_error(e)
    with open(DATA_FILE, "w") as f:
        json.dump(state, f)


# ───────────── STYLE ─────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,800;1,9..144,700&family=DM+Sans:wght@400;500;700&family=Noto+Serif+KR:wght@600;700&family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+TC:wght@600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap');
.stApp{background:#fbf6ee;}
html,body,[class*="css"],.stMarkdown,.stButton,input{font-family:'DM Sans',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stExpandSidebarButton"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{visibility:visible!important;}
.block-container{max-width:480px;padding-top:2rem;}
.eyebrow{color:#000;font-size:.72rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;text-align:center;margin-bottom:.4rem;}
.hero{font-family:'Fraunces',serif;font-weight:800;font-size:2.6rem;line-height:1;text-align:center;color:#000;letter-spacing:-.02em;margin:.2rem 0;}
.hero em{color:#000;font-weight:700;display:block;font-style:normal;}
.hero .pk{color:#F08784;} .hero .bl{color:#70C2FA;}
.hero.color{color:#F08784;} .hero.color em{color:#70C2FA;}
.sub{color:#7a7566;text-align:center;margin:.8rem 0 1.4rem;}
.card{background:#fffdf7;border:1px solid #e0d6bf;border-radius:14px;padding:1rem 1.2rem;box-shadow:5px 5px 0 #e8e0c8;margin:1rem 0;color:#333;}
.big-emoji{font-size:4.5rem;text-align:center;}
[data-testid="stButton"],div.stElementContainer:has(>[data-testid="stButton"]){width:100%!important;}
.stButton>button{width:100%;background:#b9513d;color:#fff;border:none;border-radius:10px;padding:.8rem;font-weight:700;box-shadow:0 4px 0 #8f3a2a;}
.stButton>button:hover{background:#a64632;color:#fff;}
.stTextInput input{border-radius:10px;border:1px solid #d8c9aa;padding:.8rem;}
.team{border-radius:120px 120px 20px 20px;padding:1.6rem .6rem;text-align:center;}
.team.g{background:#fde7ee;color:#F08784;} .team.b{background:#e0eff7;color:#70C2FA;}
.team .n{font-family:'Fraunces',serif;font-weight:800;font-size:2.6rem;}
.team .l{font-weight:700;color:#000;} .team .who{font-size:.75rem;color:#777;margin-top:.4rem;}
.rb{width:min(78vw,320px);margin:.5rem auto;animation:float 3.5s ease-in-out infinite;}
.float{animation:float 4s ease-in-out infinite;} .float.d{animation-delay:-2s;}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.confetti{position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:5;}
.confetti i{position:absolute;top:-6vh;display:block;opacity:.9;animation-name:fall;animation-timing-function:linear;animation-iteration-count:infinite;}
@keyframes fall{0%{transform:translateY(0) rotate(0) translateX(0)}50%{transform:translateY(60vh) rotate(360deg) translateX(20px)}100%{transform:translateY(112vh) rotate(720deg) translateX(-10px)}}
.count{font-family:'Fraunces',serif;font-weight:800;font-size:9rem;text-align:center;color:#b9513d;line-height:1.1;}
.sel{text-align:center;font-weight:700;color:#b9513d;margin:.4rem 0;}
[data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.6rem!important;}
[data-testid="stColumn"],[data-testid="column"]{min-width:0!important;flex:1 1 0!important;width:auto!important;}
</style>
""", unsafe_allow_html=True)

# ───────────── STATE / NAV ─────────────
ss = st.session_state
ss.setdefault("step", "intro")
ss.setdefault("name", "")
ss.setdefault("country", "")
ss.setdefault("pick", "")
ss.setdefault("popped", False)

lang = st.selectbox("🌐 Language / 언어 / 語言", list(T.keys()), label_visibility="collapsed")
t = T[lang]
state = load()
if DEBUG_DB and st.session_state.get("db_error"):
    st.error("DB error (debug): " + st.session_state["db_error"])

TZ_NAME = TZ_BY_LANG[lang]
LOCAL_DT = REVEAL_DT.astimezone(ZoneInfo(TZ_NAME))
if lang.startswith("Korean"):
    DATE_TXT = f"{LOCAL_DT.year}년 {LOCAL_DT.month}월 {LOCAL_DT.day}일 {LOCAL_DT.strftime('%H:%M')}"
elif lang.startswith("Traditional"):
    DATE_TXT = f"{LOCAL_DT.year}年{LOCAL_DT.month}月{LOCAL_DT.day}日 {LOCAL_DT.strftime('%H:%M')}"
else:
    DATE_TXT = LOCAL_DT.strftime("%A, %d %B %Y · %H:%M")


CJK = not lang.startswith("English")
if lang.startswith("Korean"):
    HF, BF = "'Noto Serif KR'", "'Noto Sans KR'"
elif lang.startswith("Traditional"):
    HF, BF = "'Noto Serif TC'", "'Noto Sans TC'"
else:
    HF, BF = "'Fraunces'", "'DM Sans'"
PICK_REM = "1.6rem" if CJK else "2rem"
if CJK:
    st.markdown(f"""<style>
.hero{{font-family:{HF},serif!important;font-size:1.9rem!important;line-height:1.45!important;letter-spacing:0!important;font-weight:700!important;word-break:keep-all;}}
html,body,[class*="css"],.stMarkdown,.stButton button,input{{font-family:{BF},'DM Sans',sans-serif!important;}}
.sub,.card{{line-height:1.7;word-break:keep-all;}}
</style>""", unsafe_allow_html=True)


def go(step):
    ss.step = step
    st.rerun()


def hero_html(eyebrow, l1, l2, colored=False):
    cls = "hero color" if colored else "hero"
    return f"<div class='eyebrow'>{eyebrow}</div><div class='{cls}'>{l1}<em>{l2}</em></div>"


def hero(eyebrow, l1, l2, colored=False):
    st.markdown(hero_html(eyebrow, l1, l2, colored), unsafe_allow_html=True)


def hot_balloon(c1, c2):
    return ("<svg viewBox='0 0 100 130' xmlns='http://www.w3.org/2000/svg' style='width:100%;height:auto;display:block'>"
            f"<ellipse cx='50' cy='45' rx='36' ry='42' fill='{c1}'/>"
            f"<ellipse cx='50' cy='45' rx='14' ry='42' fill='{c2}'/>"
            "<path d='M30 82 L44 106 M70 82 L56 106' stroke='#9a8a78' stroke-width='1.5'/>"
            "<rect x='42' y='106' width='16' height='13' rx='2' fill='#d8b48f'/></svg>")


def balloon_uri(c1, c2):
    return "data:image/svg+xml;utf8," + quote(hot_balloon(c1, c2))


PINK, PINK2, BLUE, BLUE2 = "#eda0bb", "#fbc9db", "#8fc6dc", "#cbe6f3"


def intro_art():
    return ("<div style='display:flex;justify-content:center;align-items:flex-end;gap:8px;margin-bottom:.6rem'>"
            f"<div class='float d' style='width:105px'>{hot_balloon(BLUE, BLUE2)}</div>"
            f"<div class='float' style='width:140px;margin-bottom:22px'>{hot_balloon(PINK, PINK2)}</div></div>")


def round_balloon(text):
    return ("<div class='rb'><svg viewBox='0 0 200 280' xmlns='http://www.w3.org/2000/svg' style='width:100%;height:auto;display:block'>"
            "<path d='M100 10 C150 10 185 50 185 105 C185 160 140 205 100 215 C60 205 15 160 15 105 C15 50 50 10 100 10 Z' fill='#111'/>"
            "<ellipse cx='68' cy='62' rx='14' ry='28' fill='#fff' opacity='.12' transform='rotate(-25 68 62)'/>"
            "<path d='M92 214 L108 214 L100 228 Z' fill='#111'/>"
            "<path d='M100 228 C86 244 114 256 100 276' stroke='#555' fill='none' stroke-width='2'/>"
            f"<text x='100' y='108' text-anchor='middle' dominant-baseline='central' font-family='Fraunces, serif' font-size='140' font-weight='800' fill='#fff'>{text}</text>"
            "</svg></div>")


def confetti_html(colors, n=50):
    rnd = random.Random(7)
    bits = []
    for _ in range(n):
        w, h = rnd.randint(6, 11), rnd.randint(10, 18)
        r = "50%" if rnd.random() < .3 else "2px"
        bits.append(f"<i style='left:{rnd.randint(0, 100)}%;width:{w}px;height:{h}px;background:{rnd.choice(colors)};"
                    f"border-radius:{r};animation-duration:{rnd.uniform(5, 10):.1f}s;animation-delay:-{rnd.uniform(0, 10):.1f}s'></i>")
    return "<div class='confetti'>" + "".join(bits) + "</div>"


# ───────────── HOST SIDEBAR ─────────────
with st.sidebar:
    with st.expander(t["host"]):
        pin = st.text_input(t["pin"], type="password")
        if pin and pin == str(st.secrets.get("HOST_PIN", "1234")):
            opts = [t["sel"], t["girl"], t["boy"]]
            cur = {"girl": 1, "boy": 2}.get(state["secret"], 0)
            choice = st.selectbox(t["secret"], opts, index=cur)
            if st.button(t["save"]):
                state["secret"] = {1: "girl", 2: "boy"}.get(opts.index(choice), "")
                save(state)
                st.success("✓")
            if st.button(t["go"]):
                if state["secret"]:
                    state["started"] = True
                    save(state)
                    ss.step = "ready"
                    st.rerun()
                else:
                    st.warning(t["sel"])
            if st.button(t["reset"]):
                save(copy.deepcopy(DEFAULT))
                ss.step, ss.popped = "intro", False
                st.rerun()

if state["started"] and ss.step in ("intro", "name", "countdown", "guess", "votes"):
    ss.step = "ready"
step = ss.step
n_guests = len(state["votes"])

# ───────────── PAGES ─────────────
if step == "intro":
    st.markdown(intro_art(), unsafe_allow_html=True)
    hero(t["eyebrow"].format(h=HOSTS), t["i1"], t["i2"], colored=True)
    st.markdown(f"<div class='sub'>{t['isub'].format(h=HOSTS)}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='card'><b>{t['rev']}</b><br>{DATE_TXT}<br>{TZ_NAME}</div>",
        unsafe_allow_html=True)
    if st.button(t["start"] + "  →"):
        go("name")
    st.caption(t["loved"].format(n=n_guests))

elif step == "name":
    hero("✦", t["n1"], t["n2"])
    ss.name = st.text_input(t["yn"], value=ss.name)
    ss.country = st.text_input("🌍 " + t["yc"], value=ss.country, placeholder="City, country")
    st.caption("✎ " + t["nh"])
    if st.button(t["inn"] + "  →"):
        if ss.name.strip():
            ss.name = ss.name.strip()
            existing = state["votes"].get(ss.name)
            if existing:
                ss.pick = existing["guess"]
            go("countdown")
        else:
            st.error(t["needn"])
    if st.button(t["back"]):
        go("intro")

elif step == "countdown":
    hero("● " + t["rev"], t["c1"], t["c2"])
    components.html(f"""
    <div id="cd" style="display:flex;gap:8px;justify-content:center;font-family:'Fraunces',serif"></div>
    <script>
    const target=new Date("{REVEAL_ISO}").getTime();
    function tick(){{
      let d=Math.max(0,target-Date.now())/1000;
      const v=[["DAYS",Math.floor(d/86400)],["HOURS",Math.floor(d%86400/3600)],["MINS",Math.floor(d%3600/60)],["SECS",Math.floor(d%60)]];
      document.getElementById("cd").innerHTML=v.map(x=>`<div style="background:#fffdf7;border:1px solid #e0d6bf;border-radius:12px;box-shadow:0 4px 0 #e8e0c8;padding:12px 0;width:80px;text-align:center"><div style="font-size:2.2rem;font-weight:800">${{String(x[1]).padStart(2,"0")}}</div><div style="font:700 .6rem 'DM Sans',sans-serif;color:#777;letter-spacing:.1em">${{x[0]}}</div></div>`).join("");
    }}
    tick();setInterval(tick,1000);
    </script>""", height=110)
    st.markdown(f"<div class='sub'>{DATE_TXT} · {TZ_NAME}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card' style='text-align:center'>{t['cnote']}</div>", unsafe_allow_html=True)
    if st.button(t["rg"] + "  →"):
        go("guess")
    if st.button(t["back"]):
        go("name")

elif step == "guess":
    hero("♥", t["g1"], t["g2"], colored=True)

    def choose(v):
        stt = load()
        if stt["started"]:
            ss.step = "ready"
            return
        ss.pick = v
        stt["votes"][ss.name] = {"guess": v, "country": ss.country}
        save(stt)
        ss.step = "votes"

    selected_css = ""
    if ss.pick:
        selected_css = (f".st-key-pick_{ss.pick} button{{border:3px solid #b9513d!important;"
                        "box-shadow:0 0 0 6px #e3d8ec!important;}")
    st.markdown(f"""<style>
.block-container{{padding-left:.8rem!important;padding-right:.8rem!important;}}
.st-key-pick_girl,.st-key-pick_boy,.st-key-pick_girl [data-testid="stButton"],.st-key-pick_boy [data-testid="stButton"]{{width:100%!important;}}
.st-key-pick_girl button,.st-key-pick_boy button{{
  width:100%;height:auto;aspect-ratio:0.76;border-radius:120px 120px 26px 26px;border:3px solid transparent!important;
  box-shadow:none!important;background-repeat:no-repeat!important;background-position:center 12%!important;
  background-size:50% auto!important;display:flex;align-items:flex-end;justify-content:center;padding:0 0 1.1rem;}}
.st-key-pick_girl button{{background-color:#fde7ee!important;background-image:url("{balloon_uri(PINK, PINK2)}")!important;}}
.st-key-pick_boy button{{background-color:#e0eff7!important;background-image:url("{balloon_uri(BLUE, BLUE2)}")!important;}}
.st-key-pick_girl button p,.st-key-pick_boy button p{{font-family:{HF},serif!important;font-weight:800;font-size:{PICK_REM};line-height:1.2;margin:0;text-align:center;}}
.st-key-pick_girl button p::after,.st-key-pick_boy button p::after{{display:block;font-family:{BF},sans-serif;font-weight:500;font-size:.72rem;margin-top:.5rem;opacity:.85;}}
.st-key-pick_girl button p::after{{content:"{t['sg']}";}} .st-key-pick_boy button p::after{{content:"{t['sb']}";}}
.st-key-pick_girl button p{{color:#F08784!important;}} .st-key-pick_boy button p{{color:#70C2FA!important;}}
.st-key-pick_girl button:hover,.st-key-pick_boy button:hover{{filter:brightness(.97);}}
{selected_css}
</style>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.button(t["girl"], key="pick_girl", on_click=choose, args=("girl",))
    with c2:
        st.button(t["boy"], key="pick_boy", on_click=choose, args=("boy",))
    if st.button(t["back"]):
        go("countdown")

elif step == "votes":
    hero("✦", t["v1"], t["v2"])
    st.markdown(f"<div class='card'>{t['va'].format(n=ss.name)}<br><small>{t['tg'] if ss.pick == 'girl' else t['tb']}</small></div>",
                unsafe_allow_html=True)

    def who(side):
        names = [f"{n}{' (' + v['country'] + ')' if v.get('country') else ''}" for n, v in state["votes"].items() if v["guess"] == side]
        return ", ".join(names) or "—"

    g = sum(v["guess"] == "girl" for v in state["votes"].values())
    b = len(state["votes"]) - g
    c1, c2 = st.columns(2)
    c1.markdown(f"<div class='team g'><div class='n'>{g}</div><div>{t['vt']}</div><div class='l'>{t['tg']}</div><div class='who'>{who('girl')}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='team b'><div class='n'>{b}</div><div>{t['vt']}</div><div class='l'>{t['tb']}</div><div class='who'>{who('boy')}</div></div>", unsafe_allow_html=True)

    if st.button(t["chg"]):
        go("guess")
    st.info(t["wait"])

    @st.fragment(run_every=5)
    def watch():
        if load()["started"]:
            ss.step = "ready"
            st.rerun(scope="app")

    watch()

elif step == "ready":
    hero(f"{HOSTS} · {t['rev']}", t["r1"], t["r2"])
    st.markdown(round_balloon(3), unsafe_allow_html=True)
    st.markdown(f"<div class='sub'><i><b>{t['gather']}</b></i></div>", unsafe_allow_html=True)
    if st.button(t["pop"] + " ✺"):
        ss.popped = True
        ss.step = "reveal"
        st.rerun()

elif step == "reveal":
    slot = st.empty()
    for _ in range(4):
        st.empty()  # covers leftovers from the previous page while counting down
    if ss.popped:
        for i in (3, 2, 1):
            slot.markdown(hero_html(f"{HOSTS} · {t['rev']}", t["r1"], t["r2"]) + round_balloon(i), unsafe_allow_html=True)
            time.sleep(1)
        ss.popped = False
    secret = load()["secret"]
    is_girl = secret == "girl"
    c1_, c2_ = (PINK, PINK2) if is_girl else (BLUE, BLUE2)
    colors = ["#F08784", "#f7b6c8", "#fbd36b", "#c9a8ee", "#70C2FA", "#fff"] if is_girl else \
             ["#70C2FA", "#a9dbf5", "#fbd36b", "#c9a8ee", "#F08784", "#fff"]
    winners = [n for n, v in state["votes"].items() if v["guess"] == secret]
    team = t["tg"] if is_girl else t["tb"]
    msg = t["won"].format(t=team, names=", ".join(winners)) if winners else t["nobody"]
    slot.markdown(
        confetti_html(colors)
        + f"<div class='rb' style='width:170px'>{hot_balloon(c1_, c2_)}</div>"
        + hero_html("✦ " + HOSTS, t["rgirl"] if is_girl else t["rboy"], "")
        + f"<div class='card'>{msg}</div>",
        unsafe_allow_html=True)
