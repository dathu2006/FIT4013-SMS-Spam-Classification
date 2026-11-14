import html
import json
import re
from datetime import datetime
from pathlib import Path
import joblib
import numpy as np
import streamlit as st

try:
    from deep_translator import GoogleTranslator, MyMemoryTranslator
    HAS_ONLINE_TRANSLATOR = True
except ImportError:
    HAS_ONLINE_TRANSLATOR = False

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="SafeChat Pro | Nền tảng Nhắn tin Đa ngôn ngữ Chống Spam AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background-color: transparent !important;}

.stApp {
    background: radial-gradient(circle at top right, #131c31 0%, #090d16 100%);
    color: #f3f4f6;
}

/* Card Đăng nhập */
.login-box {
    background: #131b2e;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    margin-top: 1.5rem;
}
.login-title {
    font-size: 1.7rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.login-sub {
    text-align: center;
    color: #94a3b8;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

/* Top Navbar */
.top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 1.4rem;
    background: #131b2e;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    margin-bottom: 1rem;
}
.nav-logo {
    font-size: 1.25rem;
    font-weight: 800;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Khung Chat */
.chat-container {
    background: #0d1322;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.2rem;
    height: 450px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin-bottom: 0.8rem;
}
.msg-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    width: 100%;
}
.msg-left {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
}
.msg-info {
    font-size: 0.74rem;
    color: #94a3b8;
    margin-bottom: 4px;
    padding: 0 6px;
}
.bubble-sent {
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    color: #ffffff;
    padding: 10px 15px;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    font-size: 0.93rem;
    line-height: 1.45;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
    word-wrap: break-word;
}
.bubble-recv {
    background: #1e293b;
    color: #f1f5f9;
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 10px 15px;
    border-radius: 18px 18px 18px 4px;
    max-width: 75%;
    font-size: 0.93rem;
    line-height: 1.45;
    word-wrap: break-word;
}
.bubble-blocked {
    background: rgba(127, 29, 29, 0.28);
    border: 1px dashed rgba(248, 113, 113, 0.65);
    color: #fca5a5;
    padding: 10px 15px;
    border-radius: 14px;
    max-width: 80%;
    font-size: 0.86rem;
    line-height: 1.45;
    word-wrap: break-word;
}
.tag-ham {
    font-size: 0.71rem;
    color: #34d399;
    margin-top: 4px;
    padding: 0 6px;
}
.tag-spam {
    font-size: 0.71rem;
    color: #f87171;
    margin-top: 4px;
    padding: 0 6px;
    font-weight: 600;
}

/* Card Phân tích bên phải */
.inspector-card {
    background: #131b2e;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}
.inspector-title {
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.7rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

/* Highlight từ khóa */
.hl-box {
    background: #090e1a;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px 12px;
    line-height: 1.85;
    font-size: 0.9rem;
    margin-bottom: 10px;
}
.tok-spam {
    background: rgba(239, 68, 68, 0.28);
    color: #fecaca;
    border-bottom: 2px solid #ef4444;
    padding: 1px 5px;
    border-radius: 5px;
    font-weight: 600;
}
.tok-ham {
    background: rgba(16, 185, 129, 0.22);
    color: #a7f3d0;
    border-bottom: 2px solid #10b981;
    padding: 1px 5px;
    border-radius: 5px;
    font-weight: 600;
}

.stTextInput input {
    background-color: #0b1120 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    color: #f8fafc !important;
    border-radius: 10px !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #2563eb, #4f46e5) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# --- ĐƯỜNG DẪN DỮ LIỆU ---
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "mnb_spam_classifier.joblib"
VEC_PATH = BASE_DIR / "models" / "tfidf_vectorizer.joblib"
USERS_DB_PATH = BASE_DIR / "users_db.json"
CHAT_DB_PATH = BASE_DIR / "chat_history.json"

OFFLINE_VI_EN_DICT = {
    "cảnh báo": "urgent warning",
    "khẩn cấp": "urgent",
    "chúc mừng": "congratulations",
    "trúng thưởng": "won prize",
    "giải thưởng": "cash prize reward",
    "tiền mặt": "cash money",
    "triệu đồng": "million vnd cash",
    "tài khoản ngân hàng": "bank account",
    "tài khoản": "account",
    "đăng nhập": "login",
    "thiết bị lạ": "unknown device",
    "truy cập ngay": "click link now",
    "bấm vào": "click here",
    "xác minh": "verify account",
    "khóa thẻ": "lock card",
    "gọi ngay": "call now",
    "gọi": "call",
    "nhận quà": "claim free gift",
    "nhận giải": "claim prize",
    "miễn phí": "free",
    "khuyến mãi": "free promotion",
    "vay vốn": "instant cash loan",
    "thuê bao": "mobile subscriber",
    "bưu kiện": "package delivery",
    "giao không thành công": "delivery failed",
    "sai địa chỉ": "wrong address",
    "cập nhật thông tin": "update your details immediately",
    "hoàn trả hàng": "return package",
    "tuyển gấp": "urgent hiring",
    "việc nhẹ lương cao": "easy work high salary",
    "thu nhập": "cash income",
    "liên hệ": "contact call",
    "chào bạn": "hey friend",
    "tối nay": "tonight",
    "chiều nay": "this afternoon",
    "họp nhóm": "group meeting",
    "báo cáo": "report",
    "thư viện": "library",
    "gửi file": "send file",
    "lâu rồi không gặp": "long time no see",
    "xem ảnh": "check out photos",
}


def fallback_offline_translate(text: str) -> str:
    res = text.lower()
    for vi_phrase, en_phrase in sorted(OFFLINE_VI_EN_DICT.items(), key=lambda x: -len(x[0])):
        res = res.replace(vi_phrase, f" {en_phrase} ")
    tokens = res.split()
    kept = [t for t in tokens if t.isascii()]
    return " ".join(kept).strip()


def detect_source_lang(text: str) -> str:
    """Nhận diện nhanh mã ngôn ngữ để truyền chuẩn xác cho API dịch nguyên câu."""
    if re.search(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', text.lower()):
        return "vi"
    if re.search(r'[\uac00-\ud7af]', text):
        return "ko"
    if re.search(r'[\u3040-\u30ff]', text):
        return "ja"
    if re.search(r'[\u4e00-\u9fff]', text):
        return "zh-CN"
    return "auto"


def translate_to_english(text: str) -> tuple[str, str]:
    """
    Dịch nguyên cả câu theo ngữ cảnh qua chuỗi 3 tầng:
    1. Google Translate API (cả câu)
    2. MyMemory Translator API (cả câu - dự phòng khi Google bị giới hạn)
    3. Offline Dictionary (chỉ dùng khi mất kết nối Internet hoàn toàn)
    """
    if text.isascii():
        return text.strip(), "Tiếng Anh gốc (Direct)"

    src_lang = detect_source_lang(text)

    if HAS_ONLINE_TRANSLATOR:
        # Tầng 1: Google Translate (dịch cả câu)
        try:
            res_google = GoogleTranslator(source=src_lang, target="en").translate(text)
            if res_google and res_google.strip() and res_google.strip().lower() != text.strip().lower():
                return res_google.strip(), f"Google Translate ({src_lang} → en)"
        except Exception:
            pass

        # Tầng 2: MyMemory Translator (dịch cả câu dự phòng)
        try:
            mm_src = "vi-VN" if src_lang == "vi" else ("ko-KR" if src_lang == "ko" else ("ja-JP" if src_lang == "ja" else ("zh-CN" if src_lang == "zh-CN" else "auto")))
            res_mm = MyMemoryTranslator(source=mm_src, target="en-US").translate(text)
            if res_mm and res_mm.strip() and res_mm.strip().lower() != text.strip().lower():
                return res_mm.strip(), f"MyMemory API ({src_lang} → en)"
        except Exception:
            pass

    # Tầng 3: Mất mạng hoàn toàn mới dùng Offline
    return fallback_offline_translate(text), "Offline Fallback (Kiểm tra lại kết nối mạng)"


def preprocess_sms_optimized(text: str) -> str:
    text = text.lower()
    text = re.sub(
        r'(http\S+|www\.\S+|\S+\.(com|co\.uk|net|org|vn|io)\S*|(bit\.ly|tinyurl\.com|goo\.gl|t\.co)/\S+)',
        ' token_url ',
        text
    )
    text = re.sub(
        r'([£$€]\s*\d+([.,]\d+)?|\d+([.,]\d+)?\s*(gbp|usd|vnd|pound|pounds|dollar|dollars|million|billion))',
        ' token_money ',
        text
    )
    text = re.sub(r'\d+', ' token_num ', text)
    text = re.sub(r'!+', ' token_exclam ', text)
    text = re.sub(r'[^a-z0-9_\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


@st.cache_resource
def load_artifacts():
    return joblib.load(VEC_PATH), joblib.load(MODEL_PATH)


def load_users() -> dict:
    if USERS_DB_PATH.exists():
        try:
            data = json.loads(USERS_DB_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict) and len(data) > 0:
                return data
        except Exception:
            pass
    default_users = {
        "quan": {"password": "123", "display_name": "Hà Minh Quân", "role": "Sinh viên"},
        "bao": {"password": "123", "display_name": "Đoàn Quốc Bảo", "role": "Thành viên nhóm"},
        "spammer": {"password": "123", "display_name": "Tổng đài Quảng cáo (+84 86888)", "role": "Tài khoản lạ"}
    }
    save_users(default_users)
    return default_users


def save_users(users: dict):
    USERS_DB_PATH.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def load_messages() -> list:
    if CHAT_DB_PATH.exists():
        try:
            data = json.loads(CHAT_DB_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list) and all(isinstance(m, dict) and "from_user" in m and "to_user" in m for m in data):
                return data
        except Exception:
            pass

    default_msgs = [
        {
            "from_user": "bao",
            "to_user": "quan",
            "text": "Quân ơi, chiều nay 3 giờ vẫn gặp nhau ở thư viện để xem lại slide báo cáo nhé?",
            "en_text": "Quan, are we still meeting at the library at 3pm this afternoon to review the report slides?",
            "trans_mode": "Google Translate (vi → en)",
            "time": "14:05",
            "prob_spam": 0.0018
        },
        {
            "from_user": "spammer",
            "to_user": "quan",
            "text": "KHẨN CẤP! Thuê bao của bạn đã trúng thưởng 50.000.000 VNĐ tiền mặt! Gọi ngay 09061701461 để nhận giải!",
            "en_text": "URGENT! Your subscriber has won a 50,000,000 VND cash prize! Call 09061701461 now to claim!",
            "trans_mode": "Google Translate (vi → en)",
            "time": "14:08",
            "prob_spam": 0.9992
        }
    ]
    save_messages(default_msgs)
    return default_msgs


def save_messages(msgs: list):
    CHAT_DB_PATH.write_text(json.dumps(msgs, ensure_ascii=False, indent=2), encoding="utf-8")


def build_highlighted_html(en_text: str, vectorizer, model) -> str:
    vocab = vectorizer.vocabulary_
    log_odds = model.feature_log_prob_[1] - model.feature_log_prob_[0]
    parts = re.split(r'(\s+)', en_text)
    html_parts = []
    for part in parts:
        if not part.strip():
            html_parts.append(part)
            continue
        norm = preprocess_sms_optimized(part)
        tokens = norm.split()
        score = sum(float(log_odds[vocab[t]]) for t in tokens if t in vocab)
        matched = any(t in vocab for t in tokens)
        safe_word = html.escape(part)
        if matched and score > 0.6:
            html_parts.append(f'<span class="tok-spam">{safe_word}</span>')
        elif matched and score < -0.6:
            html_parts.append(f'<span class="tok-ham">{safe_word}</span>')
        else:
            html_parts.append(safe_word)
    return "".join(html_parts)


def login_user(username: str):
    st.session_state.logged_in_user = username
    st.query_params["user"] = username


def logout_user():
    st.session_state.logged_in_user = None
    if "user" in st.query_params:
        del st.query_params["user"]


if not MODEL_PATH.exists() or not VEC_PATH.exists():
    st.error("Chưa tìm thấy file mô hình trong thư mục `models/`. Vui lòng chạy hết Notebook `01_eda_and_modeling.ipynb` trước.")
    st.stop()

vectorizer, model = load_artifacts()
users_db = load_users()

# --- KHÔI PHỤC PHIÊN ĐĂNG NHẬP TỪ URL KHI F5 ---
url_user = st.query_params.get("user", None)
if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    if url_user and url_user in users_db:
        st.session_state.logged_in_user = url_user
    else:
        st.session_state.logged_in_user = None

# ==============================================================================
# TRANG 1: MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ TÀI KHOẢN
# ==============================================================================
if st.session_state.logged_in_user is None or st.session_state.logged_in_user not in users_db:
    _, center_col, _ = st.columns([1, 1.35, 1])
    with center_col:
        st.markdown(
            '<div class="login-box">'
            '<div class="login-title">🛡️ SafeChat Pro</div>'
            '<div class="login-sub">Hệ thống Nhắn tin Đa ngôn ngữ Tích hợp AI Lọc Tin nhắn Rác</div>',
            unsafe_allow_html=True
        )

        tab_login, tab_reg = st.tabs(["🔐 Đăng nhập", "📝 Tạo tài khoản mới"])

        with tab_login:
            st.caption("Đăng nhập nhanh bằng tài khoản mẫu hoặc nhập thông tin bên dưới:")
            q_u1, q_u2, q_u3 = st.columns(3)
            if q_u1.button("👤 Vào nick Quân", use_container_width=True):
                login_user("quan")
                st.rerun()
            if q_u2.button("👤 Vào nick Bảo", use_container_width=True):
                login_user("bao")
                st.rerun()
            if q_u3.button("🚨 Vào nick Spammer", use_container_width=True):
                login_user("spammer")
                st.rerun()

            st.divider()
            with st.form("login_form"):
                u_input = st.text_input("Tên đăng nhập (Username):", placeholder="Ví dụ: quan")
                p_input = st.text_input("Mật khẩu:", type="password", placeholder="Mật khẩu mặc định: 123")
                btn_login = st.form_submit_button("Đăng nhập vào Phòng Chat ➤", type="primary", use_container_width=True)

                if btn_login:
                    uname = u_input.strip().lower()
                    if uname in users_db and users_db[uname]["password"] == p_input:
                        login_user(uname)
                        st.rerun()
                    else:
                        st.error("Sai tên đăng nhập hoặc mật khẩu!")

        with tab_reg:
            with st.form("register_form"):
                new_u = st.text_input("Tên đăng nhập mới (viết liền không dấu):")
                new_name = st.text_input("Tên hiển thị (Ví dụ: Nguyễn Văn A):")
                new_p = st.text_input("Mật khẩu:", type="password")
                btn_reg = st.form_submit_button("Đăng ký & Đăng nhập", type="primary", use_container_width=True)

                if btn_reg:
                    uname = new_u.strip().lower()
                    if not uname or not new_name.strip() or not new_p:
                        st.warning("Vui lòng điền đầy đủ thông tin.")
                    elif uname in users_db:
                        st.error("Tên đăng nhập này đã tồn tại!")
                    else:
                        users_db[uname] = {
                            "password": new_p,
                            "display_name": new_name.strip(),
                            "role": "Thành viên"
                        }
                        save_users(users_db)
                        login_user(uname)
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# TRANG 2: KHÔNG GIAN NHẮN TIN & PHÂN TÍCH AI CÁ NHÂN (SAU KHI ĐĂNG NHẬP)
# ==============================================================================
me = st.session_state.logged_in_user
me_info = users_db[me]

engine_badge = (
    "🌐 Dual-Engine Translation (Google + MyMemory)"
    if HAS_ONLINE_TRANSLATOR else
    "⚡ Chế độ Dịch Offline Dự phòng"
)

nav_l, nav_r = st.columns([3.5, 1])
with nav_l:
    st.markdown(
        f'<div class="top-nav">'
        f'<div class="nav-logo">🛡️ SafeChat Pro <span style="font-size:0.85rem; font-weight:500; color:#94a3b8; -webkit-text-fill-color:#94a3b8;">| Xin chào, <b>{html.escape(me_info["display_name"])}</b> (@{me})</span></div>'
        f'<div style="font-size:0.8rem; color:#34d399; background:rgba(16,185,129,0.12); padding:4px 12px; border-radius:999px; border:1px solid rgba(52,211,153,0.3);">{engine_badge}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
with nav_r:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🚪 Đăng xuất", use_container_width=True):
        logout_user()
        st.rerun()

other_users = [u for u in users_db.keys() if u != me]
c_target, c_thresh, c_reveal, c_refresh = st.columns([1.4, 1.3, 1.1, 0.7])

with c_target:
    target_user = st.selectbox(
        "💬 Đang nhắn tin với:",
        other_users,
        format_func=lambda u: f"{users_db[u]['display_name']} (@{u})"
    )
with c_thresh:
    my_threshold = st.slider(
        f"🛡️ Ngưỡng chặn Spam của {me_info['display_name']}:",
        0.10, 0.90, 0.50, 0.05
    )
with c_reveal:
    reveal_spam = st.toggle("👁️ Mở khóa xem tin rác bị chặn", value=False)
with c_refresh:
    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    if st.button("🔄 Làm mới", use_container_width=True):
        st.rerun()

all_messages = load_messages()
conv_messages = [
    m for m in all_messages
    if (m["from_user"] == me and m["to_user"] == target_user)
    or (m["from_user"] == target_user and m["to_user"] == me)
]

# --- CHIA 2 CỘT: KHUNG CHAT (TRÁI) & BẢNG PHÂN TÍCH AI RIÊNG (PHẢI) ---
col_chat, col_ai = st.columns([1.45, 1], gap="large")

with col_chat:
    chat_bubbles = []
    if not conv_messages:
        chat_bubbles.append(
            f'<div style="text-align:center; color:#64748b; margin-top:160px;">'
            f'Chưa có tin nhắn nào giữa bạn và <b>{html.escape(users_db[target_user]["display_name"])}</b>.<br>'
            f'Nhập tin nhắn bằng bất kỳ ngôn ngữ nào bên dưới!</div>'
        )
    else:
        for m in conv_messages:
            is_mine = (m["from_user"] == me)
            sender_label = "Bạn" if is_mine else users_db[m["from_user"]]["display_name"]
            safe_sender = html.escape(sender_label)
            safe_text = html.escape(m["text"])
            prob_pct = m["prob_spam"] * 100
            is_spam_for_me = (m["prob_spam"] >= my_threshold)

            if is_mine:
                status_tag = (
                    f'<div class="tag-spam">⚠️ Cảnh báo: Tin bạn gửi có {prob_pct:.1f}% dấu hiệu Spam</div>'
                    if is_spam_for_me else
                    f'<div class="tag-ham">✓ Đã gửi (Độ an toàn: {100 - prob_pct:.1f}%)</div>'
                )
                chat_bubbles.append(
                    f'<div class="msg-right">'
                    f'<div class="msg-info">{safe_sender} • {m["time"]}</div>'
                    f'<div class="bubble-sent">{safe_text}</div>'
                    f'{status_tag}'
                    f'</div>'
                )
            else:
                if is_spam_for_me:
                    if reveal_spam:
                        body = f'<div class="bubble-blocked">🚨 <b>[Tin rác đã mở khóa - {prob_pct:.1f}% Spam]</b><br>{safe_text}</div>'
                    else:
                        body = f'<div class="bubble-blocked">🔒 <i>AI đã chặn tin nhắn từ <b>{safe_sender}</b> vì phát hiện {prob_pct:.1f}% nguy cơ lừa đảo/rác. Bật nút "Mở khóa xem tin rác" phía trên để đọc.</i></div>'
                    chat_bubbles.append(
                        f'<div class="msg-left">'
                        f'<div class="msg-info">{safe_sender} • {m["time"]}</div>'
                        f'{body}'
                        f'<div class="tag-spam">🛡️ Đã lọc vào Hộp thư rác của bạn</div>'
                        f'</div>'
                    )
                else:
                    chat_bubbles.append(
                        f'<div class="msg-left">'
                        f'<div class="msg-info">{safe_sender} • {m["time"]}</div>'
                        f'<div class="bubble-recv">{safe_text}</div>'
                        f'<div class="tag-ham">✓ An toàn ({100 - prob_pct:.1f}%)</div>'
                        f'</div>'
                    )

    full_chat_html = f'<div class="chat-container">{"".join(chat_bubbles)}</div>'
    st.markdown(full_chat_html, unsafe_allow_html=True)

    # Nút chèn mẫu câu đa ngôn ngữ nhanh
    if "msg_draft" not in st.session_state:
        st.session_state.msg_draft = ""

    b1, b2, b3 = st.columns(3)
    if b1.button("🇻🇳 Tin thường (Việt)", use_container_width=True):
        st.session_state.msg_draft = "Chào bạn, tối nay nhớ gửi file báo cáo LaTeX cho mình nhé!"
    if b2.button("🚨 Tin lừa đảo (Việt)", use_container_width=True):
        st.session_state.msg_draft = "Bưu kiện của bạn giao không thành công do sai địa chỉ. Vui lòng cập nhật thông tin ngay tại bit.ly/giao-hang-vn để tránh bị hoàn trả hàng!"
    if b3.button("🇰🇷 Tin rác (Tiếng Hàn)", use_container_width=True):
        st.session_state.msg_draft = "긴급 공지! 무담보 즉시 대출 최대 5,000만원 승인 완료! 지금 바로 010-9876-5432로 전화하여 현금을 수령하세요!"

    with st.form("chat_send_form", clear_on_submit=True):
        col_in, col_btn = st.columns([4.2, 1])
        text_val = col_in.text_input(
            "Tin nhắn:",
            value=st.session_state.msg_draft,
            placeholder=f"Nhập tin nhắn bằng bất kỳ ngôn ngữ nào gửi cho {users_db[target_user]['display_name']}...",
            label_visibility="collapsed"
        )
        send_clicked = col_btn.form_submit_button("Gửi ➤", type="primary", use_container_width=True)

        if send_clicked and text_val.strip():
            en_version, trans_mode = translate_to_english(text_val.strip())
            cleaned = preprocess_sms_optimized(en_version)
            vec = vectorizer.transform([cleaned])
            prob_spam = float(model.predict_proba(vec)[0][1])

            all_messages.append({
                "from_user": me,
                "to_user": target_user,
                "text": text_val.strip(),
                "en_text": en_version,
                "trans_mode": trans_mode,
                "time": datetime.now().strftime("%H:%M"),
                "prob_spam": prob_spam
            })
            save_messages(all_messages)
            st.session_state.msg_draft = ""
            st.rerun()

with col_ai:
    my_received = [m for m in all_messages if m["to_user"] == me]
    my_spam_blocked = sum(1 for m in my_received if m["prob_spam"] >= my_threshold)
    my_ham_ok = len(my_received) - my_spam_blocked

    st.markdown(f'<div class="inspector-card"><div class="inspector-title">📊 Bộ Lọc Cá Nhân của {html.escape(me_info["display_name"])}</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    s1.metric("Tin nhận được", len(my_received))
    s2.metric("An toàn (Ham)", my_ham_ok)
    s3.metric("Đã chặn (Spam)", my_spam_blocked)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="inspector-card"><div class="inspector-title">🔬 AI X-Ray: Soi Chi Tiết Tin Nhắn</div>', unsafe_allow_html=True)
    if conv_messages:
        msg_options = list(range(len(conv_messages) - 1, -1, -1))
        selected_idx = st.selectbox(
            "Chọn tin nhắn để xem phân tích AI:",
            msg_options,
            format_func=lambda i: f"[{conv_messages[i]['time']}] {users_db[conv_messages[i]['from_user']]['display_name']}: {conv_messages[i]['text'][:32]}..."
        )
        target_msg = conv_messages[selected_idx]
        p_spam = target_msg["prob_spam"]
        is_spam_flag = p_spam >= my_threshold
        en_analyzed = target_msg.get("en_text", target_msg["text"])
        t_mode = target_msg.get("trans_mode", "Chuẩn hóa trực tiếp")

        st.caption(f"Bản dịch cả câu ({t_mode}):")
        hl_html = build_highlighted_html(en_analyzed, vectorizer, model)
        st.markdown(f'<div class="hl-box">{hl_html}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.75rem; color:#94a3b8; margin-bottom:10px;">'
            '<span class="tok-spam">Đỏ</span> = Kéo về Spam &nbsp;|&nbsp; '
            '<span class="tok-ham">Xanh</span> = Kéo về Ham'
            '</div>',
            unsafe_allow_html=True
        )

        st.progress(p_spam, text=f"Xác suất Spam: {p_spam*100:.2f}% (Ngưỡng của bạn: {my_threshold*100:.0f}%)")

        if is_spam_flag:
            st.error("🚨 Phân loại: TIN NHẮN RÁC (SPAM)")
        else:
            st.success("✅ Phân loại: TIN NHẮN THƯỜNG (HAM)")
    else:
        st.info("Cuộc trò chuyện chưa có tin nhắn nào để phân tích.")

    if st.button("🧹 Xóa lịch sử cuộc trò chuyện này", use_container_width=True):
        remaining = [
            m for m in all_messages
            if not ((m["from_user"] == me and m["to_user"] == target_user) or (m["from_user"] == target_user and m["to_user"] == me))
        ]
        save_messages(remaining)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)