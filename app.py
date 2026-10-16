import copy
import datetime
import json
import os
import time

import streamlit as st
import streamlit.components.v1 as components

# ───────────── EDIT THESE ─────────────
HOSTS = "Mia & Leo"                       # parents' names
REVEAL_ISO = "2026-11-09T16:00:00+01:00"  # reveal date/time with UTC offset
TIMEZONE_LABEL = "Europe/Berlin"
# Host PIN: set HOST_PIN in Streamlit secrets (default below is only for testing!)
# ──────────────────────────────────────

st.set_page_config(page_title="Our Little Baby Reveal", page_icon="🎈", layout="centered")

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
        "pop": "Let's pop the secret!", "rgirl": "It's a girl!", "rboy": "It's a boy!",
        "won": "Team {t} called it: {names}", "nobody": "Nobody guessed this one. Everyone wins!",
        "host": "Host controls", "pin": "Host PIN", "secret": "The secret", "sel": "Select…",
        "save": "Save secret", "go": "Smash! Start the reveal", "reset": "Reset everything",
    },
    "Korean (한국어)": {
        "eyebrow": "{h}의 축하 파티", "i1": "작은 비밀 하나.", "i2": "가득한 사랑.",
        "isub": "{h}의 달콤한 깜짝 소식을 함께 맞혀보세요.",
        "rev": "성별 공개", "start": "시작하기", "loved": "참여한 가족: {n}명",
        "n1": "먼저,", "n2": "당신을 알려주세요.", "yn": "이름", "yc": "현재 계신 곳 (선택)",
        "inn": "참여할게요", "needn": "이름을 입력해주세요.",
        "c1": "달콤한", "c2": "카운트다운.", "rg": "맞히러 가기",
        "cnote": "공개 직전까지 예측을 바꿀 수 있어요.",
        "g1": "당신의", "g2": "예감은?", "girl": "공주님", "boy": "왕자님",
        "mg": "이걸로 할게요", "pick": "먼저 팀을 선택해주세요.",
        "v1": "달콤한", "v2": "투표 현황.", "va": "{n}님으로 투표 중",
        "tg": "공주님 팀", "tb": "왕자님 팀", "vt": "표", "wait": "주최자가 공개를 시작하길 기다리는 중…",
        "smash": "펑!", "chg": "예측 바꾸기", "back": "← 뒤로",
        "r1": "작은 아기.", "r2": "큰 공개 에너지.", "gather": "가족을 모두 모아주세요. 지금이 하이라이트!",
        "pop": "비밀을 터뜨려요!", "rgirl": "공주님이에요!", "rboy": "왕자님이에요!",
        "won": "{t} 정답: {names}", "nobody": "아무도 못 맞혔어요. 모두가 승자!",
        "host": "주최자 설정", "pin": "주최자 PIN", "secret": "비밀 성별", "sel": "선택…",
        "save": "저장", "go": "펑! 공개 시작", "reset": "모두 초기화",
    },
    "Traditional Chinese (繁體中文)": {
        "eyebrow": "{h} 的慶祝派對", "i1": "一個小秘密。", "i2": "滿滿的愛。",
        "isub": "{h} 邀請你一起猜猜看，分享我們最甜蜜的驚喜。",
        "rev": "寶寶性別揭曉", "start": "開始", "loved": "已加入的親友：{n}",
        "n1": "首先，", "n2": "讓我們認識你。", "yn": "你的名字", "yc": "目前所在地（選填）",
        "inn": "我要參加", "needn": "請輸入你的名字。",
        "c1": "最甜蜜的", "c2": "倒數計時。", "rg": "我準備好要猜了",
        "cnote": "不用等，揭曉前都可以修改你的答案。",
        "g1": "你的", "g2": "直覺是？", "girl": "女寶", "boy": "男寶",
        "mg": "這是我的答案", "pick": "請先選擇一隊。",
        "v1": "最甜蜜的", "v2": "投票結果。", "va": "目前以 {n} 的身分投票",
        "tg": "女寶隊", "tb": "男寶隊", "vt": "票", "wait": "等待主辦人開始揭曉…",
        "smash": "砰！", "chg": "修改答案", "back": "← 返回",
        "r1": "小小人兒。", "r2": "超大揭曉能量。", "gather": "把大家都叫來，精彩時刻就要到了！",
        "pop": "戳破秘密！", "rgirl": "是女寶！", "rboy": "是男寶！",
        "won": "{t} 猜對了：{names}", "nobody": "沒人猜中，大家都是贏家！",
        "host": "主辦人控制面板", "pin": "主辦人 PIN", "secret": "秘密答案", "sel": "請選擇…",
        "save": "儲存答案", "go": "砰！開始揭曉", "reset": "全部重設",
    },
}

# ───────────── STORAGE (Supabase if configured, else local file) ─────────────
@st.cache_resource
def sb_client():
    try:
        from supabase import create_client
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        return None


def load():
    sb = sb_client()
    if sb:
        rows = sb.table("kv").select("value").eq("key", "state").execute().data
        return rows[0]["value"] if rows else copy.deepcopy(DEFAULT)
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return copy.deepcopy(DEFAULT)


def save(state):
    sb = sb_client()
    if sb:
        sb.table("kv").upsert({"key": "state", "value": state}).execute()
    else:
        with open(DATA_FILE, "w") as f:
            json.dump(state, f)


# ───────────── STYLE ─────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,800;1,9..144,700&family=DM+Sans:wght@400;500;700&display=swap');
.stApp{background:#fbf6ee;}
html,body,[class*="css"],.stMarkdown,.stButton,input{font-family:'DM Sans',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{max-width:480px;padding-top:2rem;}
.eyebrow{color:#c0503c;font-size:.72rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;text-align:center;margin-bottom:.4rem;}
.hero{font-family:'Fraunces',serif;font-weight:800;font-size:2.6rem;line-height:1;text-align:center;color:#000;letter-spacing:-.02em;margin:.2rem 0;}
.hero em{color:#a8486a;font-weight:700;display:block;}
.sub{color:#7a7566;text-align:center;margin:.8rem 0 1.4rem;}
.card{background:#fffdf7;border:1px solid #e0d6bf;border-radius:14px;padding:1rem 1.2rem;box-shadow:5px 5px 0 #e8e0c8;margin:1rem 0;color:#333;}
.big-emoji{font-size:4.5rem;text-align:center;}
.stButton>button{width:100%;background:#b9513d;color:#fff;border:none;border-radius:10px;padding:.8rem;font-weight:700;box-shadow:0 4px 0 #8f3a2a;}
.stButton>button:hover{background:#a64632;color:#fff;}
.stTextInput input{border-radius:10px;border:1px solid #d8c9aa;padding:.8rem;}
.team{border-radius:120px 120px 20px 20px;padding:1.6rem .6rem;text-align:center;}
.team.g{background:#fde7ee;color:#a8486a;} .team.b{background:#e0eff7;color:#4a6e94;}
.team .n{font-family:'Fraunces',serif;font-weight:800;font-size:2.6rem;}
.team .l{font-weight:700;color:#000;} .team .who{font-size:.75rem;color:#777;margin-top:.4rem;}
.balloon{width:200px;height:230px;margin:1rem auto;border-radius:50% 50% 48% 48%;background:radial-gradient(circle at 35% 30%,#e8dcff,#c7a8ee);
 display:flex;align-items:center;justify-content:center;font-family:'Fraunces',serif;font-weight:800;font-size:5rem;color:#000;}
.count{font-family:'Fraunces',serif;font-weight:800;font-size:9rem;text-align:center;color:#b9513d;line-height:1.1;}
.sel{text-align:center;font-weight:700;color:#b9513d;margin:.4rem 0;}
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


def go(step):
    ss.step = step
    st.rerun()


def hero(eyebrow, l1, l2):
    st.markdown(f"<div class='eyebrow'>{eyebrow}</div><div class='hero'>{l1}<em>{l2}</em></div>", unsafe_allow_html=True)


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

step = ss.step
n_guests = len(state["votes"])

# ───────────── PAGES ─────────────
if step == "intro":
    st.markdown("<div class='big-emoji'>🎈</div>", unsafe_allow_html=True)
    hero(t["eyebrow"].format(h=HOSTS), t["i1"], t["i2"])
    st.markdown(f"<div class='sub'>{t['isub'].format(h=HOSTS)}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='card'><b>{t['rev']}</b><br>{REVEAL_DT.strftime('%A, %d %B %Y · %H:%M')}<br>{TIMEZONE_LABEL}</div>",
        unsafe_allow_html=True)
    if st.button(t["start"] + "  →"):
        go("name")
    st.caption(t["loved"].format(n=n_guests))

elif step == "name":
    hero("✦", t["n1"], t["n2"])
    ss.name = st.text_input(t["yn"], value=ss.name)
    ss.country = st.text_input("🌍 " + t["yc"], value=ss.country, placeholder="City, country")
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
    st.markdown(f"<div class='sub'>{REVEAL_DT.strftime('%d %B %Y · %H:%M')} · {TIMEZONE_LABEL}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card' style='text-align:center'>{t['cnote']}</div>", unsafe_allow_html=True)
    if st.button(t["rg"] + "  →"):
        go("guess")
    if st.button(t["back"]):
        go("name")

elif step == "guess":
    hero("♥", t["g1"], t["g2"])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='team g'><div style='font-size:3rem'>🎈</div><div class='n' style='font-size:1.8rem'>"
                    f"{t['girl']}</div></div>", unsafe_allow_html=True)
        if st.button("🩷", key="pg"):
            ss.pick = "girl"
    with c2:
        st.markdown("<div class='team b'><div style='font-size:3rem'>🎈</div><div class='n' style='font-size:1.8rem'>"
                    f"{t['boy']}</div></div>", unsafe_allow_html=True)
        if st.button("💙", key="pb"):
            ss.pick = "boy"
    if ss.pick:
        st.markdown(f"<div class='sel'>✓ {t['girl'] if ss.pick == 'girl' else t['boy']}</div>", unsafe_allow_html=True)
    if st.button(t["mg"] + "  →"):
        if ss.pick:
            state = load()
            state["votes"][ss.name] = {"guess": ss.pick, "country": ss.country}
            save(state)
            go("votes")
        else:
            st.warning(t["pick"])
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
    st.markdown("<div class='balloon'>10</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'><i><b>{t['gather']}</b></i></div>", unsafe_allow_html=True)
    if st.button(t["pop"] + " ✺"):
        ss.popped = True
        ss.step = "reveal"
        st.rerun()

elif step == "reveal":
    slot = st.empty()
    if ss.popped:
        for i in (3, 2, 1):
            slot.markdown(f"<div class='count'>{i}</div>", unsafe_allow_html=True)
            time.sleep(1)
        slot.empty()
        ss.popped = False
    secret = load()["secret"]
    is_girl = secret == "girl"
    emoji, cls = ("🩷", "g") if is_girl else ("💙", "b")
    st.markdown(f"<div class='big-emoji'>{emoji}</div>", unsafe_allow_html=True)
    hero("✦ " + HOSTS, t["rgirl"] if is_girl else t["rboy"], "")
    winners = [n for n, v in state["votes"].items() if v["guess"] == secret]
    team = t["tg"] if is_girl else t["tb"]
    st.markdown(f"<div class='card'>{t['won'].format(t=team, names=', '.join(winners)) if winners else t['nobody']}</div>",
                unsafe_allow_html=True)
    if is_girl:
        st.balloons()
    else:
        st.snow()
