import csv
import html
import json
import re
from datetime import datetime
from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

try:
    from deep_translator import GoogleTranslator, MyMemoryTranslator
    HAS_ONLINE_TRANSLATOR = True
except ImportError:
    HAS_ONLINE_TRANSLATOR = False

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="SafeChat Pro | Lọc Tin Nhắn Rác Đa Ngôn Ngữ",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
#MainMenu, footer, [data-testid="stDecoration"] {
    display: none !important;
}
header {
    background-color: transparent !important;
}
[data-testid="stExpandSidebarButton"], [data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    color: #f8fafc !important;
}

.stApp {
    background: radial-gradient(circle at top right, #131c31 0%, #090d16 100%);
    color: #f3f4f6;
}

[data-testid="stSidebar"] {
    background-color: #0b101d;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
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
    margin-bottom: 0.7rem;
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

/* Card Phân tích */
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
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    padding: 12px 14px;
    line-height: 1.9;
    font-size: 0.92rem;
    margin-bottom: 10px;
}
.tok-spam {
    background: rgba(239, 68, 68, 0.35);
    color: #ffffff;
    border: 1px solid rgba(248, 113, 113, 0.7);
    padding: 2px 6px;
    border-radius: 6px;
    font-weight: 600;
}
.tok-ham {
    background: rgba(16, 185, 129, 0.28);
    color: #ecfdf5;
    border: 1px solid rgba(52, 211, 153, 0.6);
    padding: 2px 6px;
    border-radius: 6px;
    font-weight: 600;
}
.risk-badge {
    display: inline-block;
    background: rgba(245, 158, 11, 0.18);
    color: #fcd34d;
    border: 1px solid rgba(245, 158, 11, 0.45);
    font-size: 0.76rem;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 999px;
    margin: 2px 4px 6px 0;
}
.kw-chip-spam {
    display: inline-block;
    background: rgba(239, 68, 68, 0.15);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.35);
    font-size: 0.74rem;
    padding: 2px 8px;
    border-radius: 6px;
    margin: 2px 4px 2px 0;
}
.kw-chip-ham {
    display: inline-block;
    background: rgba(16, 185, 129, 0.15);
    color: #6ee7b7;
    border: 1px solid rgba(16, 185, 129, 0.35);
    font-size: 0.74rem;
    padding: 2px 8px;
    border-radius: 6px;
    margin: 2px 4px 2px 0;
}
.meta-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 0.86rem;
}
.meta-label {
    color: #94a3b8;
}
.meta-val {
    color: #f1f5f9;
    font-weight: 600;
}

.stTextInput input, .stTextArea textarea {
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
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
USERS_DB_PATH = DATA_DIR / "users_db.json"
CHAT_DB_PATH = DATA_DIR / "chat_history.json"
FEEDBACK_CSV_PATH = DATA_DIR / "feedback_errors.csv"

OFFLINE_VI_EN_DICT = {
    "cảnh báo": "urgent warning", "khẩn cấp": "urgent", "chúc mừng": "congratulations",
    "trúng thưởng": "won prize", "giải thưởng": "cash prize reward", "tiền mặt": "cash money",
    "triệu đồng": "million vnd cash", "tài khoản ngân hàng": "bank account", "tài khoản": "account",
    "đăng nhập": "login", "thiết bị lạ": "unknown device", "truy cập ngay": "click link now",
    "bấm vào": "click here", "xác minh": "verify account", "khóa thẻ": "lock card",
    "gọi ngay": "call now", "gọi": "call", "nhận quà": "claim free gift",
    "nhận giải": "claim prize", "miễn phí": "free", "khuyến mãi": "free promotion",
    "vay vốn": "instant cash loan", "thuê bao": "mobile subscriber", "bưu kiện": "package delivery",
    "giao không thành công": "delivery failed", "sai địa chỉ": "wrong address",
    "cập nhật thông tin": "update your details immediately", "hoàn trả hàng": "return package",
    "tuyển gấp": "urgent hiring", "việc nhẹ lương cao": "easy work high salary",
    "thu nhập": "cash income", "liên hệ": "contact call", "chào bạn": "hey friend",
    "tối nay": "tonight", "chiều nay": "this afternoon", "họp nhóm": "group meeting",
    "báo cáo": "report", "thư viện": "library", "gửi file": "send file",
    "lâu rồi không gặp": "long time no see", "xem ảnh": "check out photos",
}


def fallback_offline_translate(text: str) -> str:
    res = text.lower()
    for vi_phrase, en_phrase in sorted(OFFLINE_VI_EN_DICT.items(), key=lambda x: -len(x[0])):
        res = res.replace(vi_phrase, f" {en_phrase} ")
    tokens = res.split()
    kept = [t for t in tokens if t.isascii()]
    return " ".join(kept).strip()


def detect_source_lang(text: str) -> str:
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
    cleaned_check = re.sub(r'[£€¥₩₫]', '', text)
    if cleaned_check.isascii():
        return text.strip(), "Tiếng Anh gốc (Direct)"

    src_lang = detect_source_lang(text)
    if HAS_ONLINE_TRANSLATOR:
        try:
            res_google = GoogleTranslator(source=src_lang, target="en").translate(text)
            if res_google and res_google.strip() and res_google.strip().lower() != text.strip().lower():
                return res_google.strip(), f"Google Translate ({src_lang} → en)"
        except Exception:
            pass

        if src_lang != "auto":
            try:
                mm_map = {"vi": "vi-VN", "ko": "ko-KR", "ja": "ja-JP", "zh-CN": "zh-CN"}
                res_mm = MyMemoryTranslator(source=mm_map[src_lang], target="en-US").translate(text)
                if res_mm and res_mm.strip() and res_mm.strip().lower() != text.strip().lower():
                    return res_mm.strip(), f"MyMemory API ({src_lang} → en)"
            except Exception:
                pass

    return fallback_offline_translate(text), "Offline Fallback"


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


def compute_meta_features(raw_text: str) -> dict:
    """Trích xuất đặc trưng thống kê bề mặt của tin nhắn."""
    char_count = len(raw_text)
    words = raw_text.split()
    word_count = len(words)
    avg_word_len = round(sum(len(w) for w in words) / word_count, 1) if word_count > 0 else 0.0
    digit_count = sum(c.isdigit() for c in raw_text)
    digit_ratio = round((digit_count / char_count) * 100, 1) if char_count > 0 else 0.0
    upper_words = sum(1 for w in words if len(w) >= 2 and w.isupper())
    exclam_count = raw_text.count("!")
    has_currency = bool(re.search(r'[£$€¥₩₫]|(vnd|vnđ|usd|gbp)', raw_text.lower()))
    has_url = bool(re.search(r'(http\S+|www\.\S+|(bit\.ly|tinyurl\.com|goo\.gl|t\.co)/\S+|\S+\.(vn|com|net|org|io)/\S+)', raw_text.lower()))
    return {
        "char_count": char_count,
        "word_count": word_count,
        "avg_word_len": avg_word_len,
        "digit_count": digit_count,
        "digit_ratio": digit_ratio,
        "upper_words": upper_words,
        "exclam_count": exclam_count,
        "has_currency": has_currency,
        "has_url": has_url
    }


def analyze_message_hybrid(raw_text: str, en_text: str, vectorizer, model) -> dict:
    cleaned = preprocess_sms_optimized(en_text)
    vec = vectorizer.transform([cleaned])
    nb_prob = float(model.predict_proba(vec)[0][1])

    risk_flags = []
    boost = 0.0
    low_raw = raw_text.lower()
    low_en = en_text.lower()

    if re.search(r'(http\S+|www\.\S+|(bit\.ly|tinyurl\.com|goo\.gl|t\.co)/\S+|\S+\.(vn|com|net|org|io)/\S+)', low_raw):
        risk_flags.append("🔗 Chứa liên kết / URL lạ")
        boost += 0.35

    if re.search(r'(\+?\d[\d\-\.\s]{7,}\d)', raw_text):
        risk_flags.append("📞 Chứa số điện thoại")
        boost += 0.15

    if re.search(r'(\d+\s*(triệu|tr|vnđ|vnd|usd|\$|£|won|만원|万円)|trúng thưởng|tiền mặt|vay|prize|cash|loan)', low_raw + " " + low_en):
        risk_flags.append("💰 Dấu hiệu tiền thưởng / Tài chính")
        boost += 0.20

    if re.search(r'(khẩn cấp|cập nhật|xác minh|khóa thẻ|truy cập|bấm vào|urgent|immediately|verify|update|claim)', low_raw + " " + low_en):
        risk_flags.append("⚡ Thúc giục hành động gấp")
        boost += 0.15

    if len(risk_flags) >= 2 or "🔗 Chứa liên kết / URL lạ" in risk_flags:
        final_prob = min(0.999, max(nb_prob, nb_prob + boost * (1 - nb_prob)))
    else:
        final_prob = nb_prob

    return {
        "nb_prob": nb_prob,
        "final_prob": final_prob,
        "risk_flags": risk_flags,
        "cleaned_tokens": cleaned
    }


def extract_top_keywords(en_text: str, vectorizer, model, top_n: int = 6):
    vocab = vectorizer.vocabulary_
    log_odds = model.feature_log_prob_[1] - model.feature_log_prob_[0]
    cleaned = preprocess_sms_optimized(en_text)
    tokens = list(dict.fromkeys(cleaned.split()))

    scored = []
    for t in tokens:
        if t in vocab:
            scored.append((t, float(log_odds[vocab[t]])))

    scored.sort(key=lambda x: abs(x[1]), reverse=True)
    return scored[:top_n]


def log_active_learning_feedback(msg_obj: dict, predicted_label: str, reporter: str):
    file_exists = FEEDBACK_CSV_PATH.exists()
    corrected_label = "ham" if predicted_label == "spam" else "spam"
    with open(FEEDBACK_CSV_PATH, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "reporter", "raw_text", "en_text", "prob_spam", "ai_predicted", "user_corrected_label"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            reporter,
            msg_obj["text"],
            msg_obj.get("en_text", msg_obj["text"]),
            round(msg_obj["prob_spam"], 4),
            predicted_label,
            corrected_label
        ])


def count_feedback_samples() -> int:
    if not FEEDBACK_CSV_PATH.exists():
        return 0
    try:
        with open(FEEDBACK_CSV_PATH, mode="r", encoding="utf-8-sig") as f:
            return max(0, sum(1 for _ in f) - 1)
    except Exception:
        return 0


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
            "prob_spam": 0.0018,
            "nb_prob": 0.0018,
            "risk_flags": []
        },
        {
            "from_user": "spammer",
            "to_user": "quan",
            "text": "KHẨN CẤP! Thuê bao của bạn đã trúng thưởng 50.000.000 VNĐ tiền mặt! Gọi ngay 09061701461 để nhận giải!",
            "en_text": "URGENT! Your subscriber has won a 50,000,000 VND cash prize! Call 09061701461 now to claim!",
            "trans_mode": "Google Translate (vi → en)",
            "time": "14:08",
            "prob_spam": 0.9992,
            "nb_prob": 0.9992,
            "risk_flags": ["📞 Chứa số điện thoại", "💰 Dấu hiệu tiền thưởng / Tài chính", "⚡ Thúc giục hành động gấp"]
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
    st.markdown("""
    <style>
    div[data-testid="column"]:nth-of-type(2) [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(19, 27, 46, 0.92);
        border: 1px solid rgba(56, 189, 248, 0.22) !important;
        border-radius: 22px !important;
        padding: 1.8rem 2rem 2rem 2rem !important;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.65);
        margin-top: 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0b1120;
        padding: 5px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1;
        justify-content: center;
        border-radius: 8px;
        padding: 8px 12px;
        font-weight: 600;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(37, 99, 235, 0.25), rgba(79, 70, 229, 0.25)) !important;
        color: #38bdf8 !important;
        border-bottom: none !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    _, center_col, _ = st.columns([1.15, 1.2, 1.15])
    with center_col:
        with st.container(border=True):
            st.markdown(
                '<div style="text-align:center; margin-bottom: 1.2rem;">'
                '<div style="font-size:2.4rem; line-height:1.1; margin-bottom:0.3rem;">🛡️</div>'
                '<div class="login-title" style="margin-bottom:0.2rem;">SafeChat Pro</div>'
                '<div style="color:#94a3b8; font-size:0.86rem;">Nền tảng Nhắn tin Đa ngôn ngữ &amp; Lọc Tin nhắn Rác AI</div>'
                '</div>',
                unsafe_allow_html=True
            )

            tab_login, tab_reg = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký tài khoản"])

            with tab_login:
                st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
                with st.form("login_form", border=False):
                    u_input = st.text_input("Tên đăng nhập", placeholder="Nhập username (vd: bao, quan)...")
                    p_input = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu (mặc định: 123)...")
                    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
                    btn_login = st.form_submit_button("Đăng nhập vào Phòng Chat ➤", type="primary", use_container_width=True)

                    if btn_login:
                        uname = u_input.strip().lower()
                        if uname in users_db and users_db[uname]["password"] == p_input:
                            login_user(uname)
                            st.rerun()
                        else:
                            st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")

                st.markdown(
                    '<div style="text-align:center; color:#64748b; font-size:0.78rem; margin: 0.9rem 0 0.6rem 0;">'
                    '— hoặc truy cập nhanh tài khoản Demo —'
                    '</div>',
                    unsafe_allow_html=True
                )
                q_u1, q_u2, q_u3 = st.columns(3)
                if q_u1.button("👤 Quân", use_container_width=True, help="Đăng nhập nhanh nick Hà Minh Quân"):
                    login_user("quan")
                    st.rerun()
                if q_u2.button("👤 Bảo", use_container_width=True, help="Đăng nhập nhanh nick Đoàn Quốc Bảo"):
                    login_user("bao")
                    st.rerun()
                if q_u3.button("🚨 Spammer", use_container_width=True, help="Đăng nhập nhanh nick Tổng đài Quảng cáo"):
                    login_user("spammer")
                    st.rerun()

            with tab_reg:
                st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
                with st.form("register_form", border=False):
                    new_name = st.text_input("Tên hiển thị", placeholder="Ví dụ: Nguyễn Văn A")
                    new_u = st.text_input("Tên đăng nhập (viết liền không dấu)", placeholder="Ví dụ: nguyenvana")
                    c_p1, c_p2 = st.columns(2)
                    new_p = c_p1.text_input("Mật khẩu", type="password", placeholder="••••••••")
                    new_p2 = c_p2.text_input("Xác nhận mật khẩu", type="password", placeholder="••••••••")
                    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
                    btn_reg = st.form_submit_button("Tạo tài khoản & Bắt đầu ➤", type="primary", use_container_width=True)

                    if btn_reg:
                        uname = new_u.strip().lower()
                        if not uname or not new_name.strip() or not new_p:
                            st.warning("Vui lòng điền đầy đủ tất cả các trường.")
                        elif not re.match(r'^[a-z0-9_]{3,20}$', uname):
                            st.warning("Tên đăng nhập dài 3–20 ký tự, chỉ gồm chữ thường không dấu, số hoặc dấu gạch dưới (_).")
                        elif new_p != new_p2:
                            st.error("Mật khẩu xác nhận không khớp!")
                        elif uname in users_db:
                            st.error("Tên đăng nhập này đã có người sử dụng!")
                        else:
                            users_db[uname] = {
                                "password": new_p,
                                "display_name": new_name.strip(),
                                "role": "Thành viên"
                            }
                            save_users(users_db)
                            login_user(uname)
                            st.rerun()
    st.stop()

# ==============================================================================
# TRANG 2: KHÔNG GIAN LÀM VIỆC CHÍNH
# ==============================================================================
me = st.session_state.logged_in_user
me_info = users_db[me]
other_users = [u for u in users_db.keys() if u != me]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛡️ SafeChat Pro")
    st.caption(f"Tài khoản: **{me_info['display_name']}** (`@{me}`)")
    st.divider()

    st.markdown("#### ⚙️ Cấu hình Bộ lọc AI")
    my_threshold = st.slider(
        "Ngưỡng chặn Spam:",
        min_value=0.10, max_value=0.90, value=0.50, step=0.05,
        help="Tin nhắn có xác suất Spam lớn hơn ngưỡng này sẽ tự động bị chặn."
    )
    use_hybrid_boost = st.toggle(
        "🧠 Bật Hybrid AI (Bắt Link Phishing)",
        value=True,
        help="Kết hợp Naive Bayes với bộ nhận diện URL rút gọn, số điện thoại và tiền thưởng."
    )
    reveal_spam = st.toggle("👁️ Mở khóa xem tin rác bị chặn", value=False)

    st.divider()
    st.markdown("#### 🔄 Active Learning")
    fb_count = count_feedback_samples()
    st.caption(f"Mẫu báo cáo sai đã lưu: **{fb_count}** mẫu (`feedback_errors.csv`)")

    st.divider()
    st.markdown("#### 🗂️ Quản lý Dữ liệu")
    confirm_clear = st.checkbox("Xác nhận xóa đoạn chat hiện tại")
    btn_clear_chat = st.button("🧹 Xóa lịch sử chat", disabled=not confirm_clear, use_container_width=True)

    st.divider()
    engine_text = "Online (Google + MyMemory)" if HAS_ONLINE_TRANSLATOR else "Offline Dictionary"
    st.caption(f"🌐 Dịch thuật: **{engine_text}**")
    if st.button("🚪 Đăng xuất", use_container_width=True):
        logout_user()
        st.rerun()

# --- TABS CHỨC NĂNG CHÍNH (3 CHẾ ĐỘ ĐẦY ĐỦ) ---
tab_quick_mode, tab_chat_mode, tab_batch_mode = st.tabs([
    "🔍 Kiểm tra Nhanh (Đơn lẻ)",
    "💬 Phòng Chat & AI X-Ray",
    "📂 Quét File Hàng Loạt (Batch Audit)"
])

# ==============================================================================
# TAB 1: KIỂM TRA NHANH TIN NHẮN ĐƠN LẺ (SANDBOX / INSPECTOR)
# ==============================================================================
with tab_quick_mode:
    st.markdown("#### 🔍 Kiểm Tra & Giải Thích Tin Nhắn Đơn Lẻ")
    st.caption("Dán trực tiếp một tin nhắn bất kỳ (Tiếng Anh, Tiếng Việt, Hàn, Nhật, Trung...) để phân tích đặc trưng và giải thích quyết định của mô hình AI.")

    quick_samples = {
        "— Chọn nhanh tin nhắn mẫu để kiểm thử —": "",
        "🚨 [SPAM - Tiếng Anh gốc]: PRIVATE! Your 2004 Account Statement for 07742676969 shows 786 unredeemed Bonus Points...": "PRIVATE! Your 2004 Account Statement for 07742676969 shows 786 unredeemed Bonus Points. To claim call 08719180248 Identifier Code: 45239",
        "🚨 [SPAM - Phishing Tiếng Việt]: Bưu kiện giao thất bại, cập nhật địa chỉ tại bit.ly/giao-hang-vn": "Bưu kiện của bạn giao không thành công do sai địa chỉ. Vui lòng cập nhật thông tin ngay tại bit.ly/giao-hang-vn để tránh bị hoàn trả hàng!",
        "🚨 [SPAM - Tiếng Hàn]: Cho vay tín chấp khẩn cấp 50 triệu Won": "긴급 공지! 무담보 즉시 대출 최대 5,000만원 승인 완료! 지금 바로 010-9876-5432로 전화하여 현금을 수령하세요!",
        "✅ [HAM - Tiếng Anh gốc]: Nhắc lịch học nhóm Database Systems": "Hi Quan, reminder that our Database Systems lab session tomorrow is moved to Room 402 at 1:30 PM. See you there!",
        "✅ [HAM - Tiếng Việt]: Hẹn gặp thư viện chiều nay": "Quân ơi, chiều nay 3 giờ vẫn gặp nhau ở thư viện để xem lại slide báo cáo nhé?"
    }

    if "quick_input_text" not in st.session_state:
        st.session_state.quick_input_text = ""

    col_q_sel, col_q_clr = st.columns([4.5, 1])
    with col_q_sel:
        q_choice = st.selectbox("Mẫu thử nhanh:", list(quick_samples.keys()), label_visibility="collapsed", key="q_sample_box")
    with col_q_clr:
        if st.button("🗑️ Xóa trắng", use_container_width=True, key="btn_q_clear"):
            st.session_state.quick_input_text = ""
            st.session_state.pop("quick_last_result", None)
            st.rerun()

    if quick_samples[q_choice]:
        st.session_state.quick_input_text = quick_samples[q_choice]

    raw_quick = st.text_area(
        "Nội dung tin nhắn cần kiểm tra:",
        value=st.session_state.quick_input_text,
        height=105,
        placeholder="Nhập hoặc dán nội dung tin nhắn SMS cần kiểm tra vào đây..."
    )

    btn_analyze_quick = st.button("🔍 PHÂN TÍCH & DỰ ĐOÁN NGAY", type="primary", use_container_width=True)

    if btn_analyze_quick and raw_quick.strip():
        st.session_state.quick_input_text = raw_quick.strip()
        en_q, t_mode_q = translate_to_english(raw_quick.strip())
        res_q = analyze_message_hybrid(raw_quick.strip(), en_q, vectorizer, model)
        meta_q = compute_meta_features(raw_quick.strip())
        kws_q = extract_top_keywords(en_q, vectorizer, model, top_n=8)
        st.session_state.quick_last_result = {
            "raw": raw_quick.strip(),
            "en": en_q,
            "trans_mode": t_mode_q,
            "analysis": res_q,
            "meta": meta_q,
            "keywords": kws_q
        }

    if "quick_last_result" in st.session_state:
        q_res = st.session_state.quick_last_result
        ana = q_res["analysis"]
        meta = q_res["meta"]
        score_q = ana["final_prob"] if use_hybrid_boost else ana["nb_prob"]
        is_spam_q = score_q >= my_threshold

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if is_spam_q:
            st.error(f"🚨 KẾT LUẬN: TIN NHẮN RÁC (SPAM) — Xác suất rủi ro: {score_q*100:.2f}% (Ngưỡng hiện tại: {my_threshold*100:.0f}%)")
        else:
            st.success(f"✅ KẾT LUẬN: TIN NHẮN HỢP LỆ (HAM) — Độ an toàn: {(1 - score_q)*100:.2f}% | Xác suất Spam: {score_q*100:.2f}%")

        q_left, q_right = st.columns([1, 1.35], gap="large")

        with q_left:
            st.markdown('<div class="inspector-card"><div class="inspector-title">📐 Đặc trưng Thống kê Bề mặt (Meta-Features)</div>', unsafe_allow_html=True)
            meta_rows = [
                ("Tổng số ký tự (char_count)", f"{meta['char_count']} ký tự"),
                ("Tổng số từ (word_count)", f"{meta['word_count']} từ (TB: {meta['avg_word_len']} ký tự/từ)"),
                ("Số lượng chữ số (digit_count)", f"{meta['digit_count']} chữ số ({meta['digit_ratio']}%)"),
                ("Số từ viết IN HOA (upper_words)", f"{meta['upper_words']} từ"),
                ("Số dấu chấm than (!)", f"{meta['exclam_count']}"),
                ("Ký hiệu tiền tệ (£, $, €, VNĐ)", "CÓ" if meta["has_currency"] else "KHÔNG"),
                ("Đường dẫn URL / Website", "CÓ" if meta["has_url"] else "KHÔNG"),
                ("Điểm Multinomial Naive Bayes gốc", f"{ana['nb_prob']*100:.2f}%"),
                ("Điểm Hybrid AI tổng hợp", f"{ana['final_prob']*100:.2f}%"),
            ]
            rows_html = "".join(
                f'<div class="meta-row"><span class="meta-label">{k}</span><span class="meta-val">{v}</span></div>'
                for k, v in meta_rows
            )
            st.markdown(rows_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with q_right:
            st.markdown('<div class="inspector-card"><div class="inspector-title">🔬 Giải thích Quyết định Mô hình (Explainable AI)</div>', unsafe_allow_html=True)

            if ana["risk_flags"]:
                badges_q = "".join(f'<span class="risk-badge">{html.escape(f)}</span>' for f in ana["risk_flags"])
                st.markdown(f'<div style="margin-bottom:8px;">{badges_q}</div>', unsafe_allow_html=True)

            st.caption(f"1. Bản dịch trung gian ({q_res['trans_mode']}) & Tô màu trọng số:")
            hl_q = build_highlighted_html(q_res["en"], vectorizer, model)
            st.markdown(f'<div class="hl-box">{hl_q}</div>', unsafe_allow_html=True)

            st.caption("2. Chuỗi văn bản sau Tiền xử lý chuyên biệt SMS (Tokenization):")
            st.code(ana["cleaned_tokens"], language="text")

            if q_res["keywords"]:
                st.caption("3. Top Token / N-gram ảnh hưởng mạnh nhất (Log-Odds Spam vs Ham):")
                df_kw = pd.DataFrame([
                    {
                        "Token / Đặc trưng": tok,
                        "Trọng số Log-Odds": f"{sc:+.3f}",
                        "Xu hướng tác động": "Tăng khả năng SPAM (+)" if sc > 0 else "Tăng khả năng HAM (-)"
                    }
                    for tok, sc in q_res["keywords"]
                ])
                st.dataframe(df_kw, use_container_width=True, hide_index=True)

            q_fb1, q_fb2 = st.columns(2)
            pred_q_str = "spam" if is_spam_q else "ham"
            if q_fb1.button("👍 Kết quả chuẩn xác", key="q_fb_ok", use_container_width=True):
                st.toast("Đã ghi nhận đánh giá chính xác!", icon="✅")
            if q_fb2.button("👎 Báo cáo đoán sai (Active Learning)", key="q_fb_err", use_container_width=True):
                log_active_learning_feedback(
                    {"text": q_res["raw"], "en_text": q_res["en"], "prob_spam": score_q},
                    pred_q_str,
                    me
                )
                st.toast("Đã lưu mẫu sai vào data/feedback_errors.csv!", icon="📝")

            st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# TAB 2: PHÒNG CHAT BẢO MẬT & X-RAY
# ==============================================================================
with tab_chat_mode:
    c_target, c_refresh = st.columns([4.5, 1])
    with c_target:
        target_user = st.selectbox(
            "💬 Đang trò chuyện cùng:",
            other_users,
            format_func=lambda u: f"{users_db[u]['display_name']} (@{u})",
            label_visibility="collapsed"
        )
    with c_refresh:
        if st.button("🔄 Làm mới", use_container_width=True):
            st.rerun()

    all_messages = load_messages()

    if btn_clear_chat and confirm_clear:
        remaining = [
            m for m in all_messages
            if not ((m["from_user"] == me and m["to_user"] == target_user) or (m["from_user"] == target_user and m["to_user"] == me))
        ]
        save_messages(remaining)
        st.rerun()

    conv_messages = [
        m for m in all_messages
        if (m["from_user"] == me and m["to_user"] == target_user)
        or (m["from_user"] == target_user and m["to_user"] == me)
    ]

    col_chat, col_ai = st.columns([1.45, 1], gap="large")

    with col_chat:
        chat_bubbles = []
        if not conv_messages:
            chat_bubbles.append(
                f'<div style="text-align:center; color:#64748b; margin-top:165px;">'
                f'Chưa có tin nhắn nào giữa bạn và <b>{html.escape(users_db[target_user]["display_name"])}</b>.<br>'
                f'Nhập tin nhắn bằng bất kỳ ngôn ngữ nào bên dưới!</div>'
            )
        else:
            for m in conv_messages:
                is_mine = (m["from_user"] == me)
                sender_label = "Bạn" if is_mine else users_db[m["from_user"]]["display_name"]
                safe_sender = html.escape(sender_label)
                safe_text = html.escape(m["text"])
                effective_prob = m["prob_spam"] if use_hybrid_boost else m.get("nb_prob", m["prob_spam"])
                prob_pct = effective_prob * 100
                is_spam_for_me = (effective_prob >= my_threshold)

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
                            body = f'<div class="bubble-blocked">🔒 <i>AI đã chặn tin nhắn từ <b>{safe_sender}</b> ({prob_pct:.1f}% nguy cơ lừa đảo). Bật "Mở khóa xem tin rác" ở thanh bên trái để đọc.</i></div>'
                        chat_bubbles.append(
                            f'<div class="msg-left">'
                            f'<div class="msg-info">{safe_sender} • {m["time"]}</div>'
                            f'{body}'
                            f'<div class="tag-spam">🛡️ Đã lọc vào Hộp thư rác</div>'
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

        st.markdown(f'<div class="chat-container">{"".join(chat_bubbles)}</div>', unsafe_allow_html=True)

        if "msg_draft" not in st.session_state:
            st.session_state.msg_draft = ""

        sample_map = {
            "— Chọn nhanh mẫu tin nhắn thử nghiệm —": "",
            "🇻🇳 Tin thường: Hẹn gửi báo cáo LaTeX": "Chào bạn, tối nay nhớ gửi file báo cáo LaTeX cho mình nhé!",
            "🚨 Lừa đảo (Việt): Giả mạo giao hàng bit.ly": "Bưu kiện của bạn giao không thành công do sai địa chỉ. Vui lòng cập nhật thông tin ngay tại bit.ly/giao-hang-vn để tránh bị hoàn trả hàng!",
            "🇰🇷 Tin rác (Hàn): Cho vay tiền mặt khẩn cấp": "긴급 공지! 무담보 즉시 대출 최대 5,000만원 승인 완료! 지금 바로 010-9876-5432로 전화하여 현금을 수령하세요!"
        }
        selected_sample = st.selectbox(
            "Mẫu thử nhanh:",
            list(sample_map.keys()),
            label_visibility="collapsed"
        )
        if sample_map[selected_sample]:
            st.session_state.msg_draft = sample_map[selected_sample]

        with st.form("chat_send_form", clear_on_submit=True):
            col_in, col_btn = st.columns([4.5, 1])
            text_val = col_in.text_input(
                "Tin nhắn:",
                value=st.session_state.msg_draft,
                placeholder=f"Nhập tin nhắn bằng bất kỳ ngôn ngữ nào gửi cho {users_db[target_user]['display_name']}...",
                label_visibility="collapsed"
            )
            send_clicked = col_btn.form_submit_button("Gửi ➤", type="primary", use_container_width=True)

            if send_clicked and text_val.strip():
                en_version, trans_mode = translate_to_english(text_val.strip())
                analysis = analyze_message_hybrid(text_val.strip(), en_version, vectorizer, model)

                all_messages.append({
                    "from_user": me,
                    "to_user": target_user,
                    "text": text_val.strip(),
                    "en_text": en_version,
                    "trans_mode": trans_mode,
                    "time": datetime.now().strftime("%H:%M"),
                    "prob_spam": analysis["final_prob"],
                    "nb_prob": analysis["nb_prob"],
                    "risk_flags": analysis["risk_flags"]
                })
                save_messages(all_messages)
                st.session_state.msg_draft = ""
                st.rerun()

    with col_ai:
        my_received = [m for m in all_messages if m["to_user"] == me]
        my_spam_blocked = sum(
            1 for m in my_received
            if (m["prob_spam"] if use_hybrid_boost else m.get("nb_prob", m["prob_spam"])) >= my_threshold
        )
        my_ham_ok = len(my_received) - my_spam_blocked

        st.markdown(f'<div class="inspector-card"><div class="inspector-title">📊 Thống Kê Bộ Lọc ({html.escape(me_info["display_name"])})</div>', unsafe_allow_html=True)
        s0, s1, s2, s3 = st.columns(4)
        s0.metric("Hội thoại", len(conv_messages))
        s1.metric("Đã nhận", len(my_received))
        s2.metric("An toàn", my_ham_ok)
        s3.metric("Đã chặn", my_spam_blocked)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="inspector-card"><div class="inspector-title">🔬 AI X-Ray: Soi Chi Tiết Tin Nhắn</div>', unsafe_allow_html=True)
        if conv_messages:
            msg_options = list(range(len(conv_messages) - 1, -1, -1))
            selected_idx = st.selectbox(
                "Tin nhắn đang phân tích (mặc định mới nhất):",
                msg_options,
                format_func=lambda i: f"[{conv_messages[i]['time']}] {users_db[conv_messages[i]['from_user']]['display_name']}: {conv_messages[i]['text'][:32]}..."
            )
            target_msg = conv_messages[selected_idx]
            nb_p = target_msg.get("nb_prob", target_msg["prob_spam"])
            p_spam = target_msg["prob_spam"] if use_hybrid_boost else nb_p
            is_spam_flag = p_spam >= my_threshold
            en_analyzed = target_msg.get("en_text", target_msg["text"])
            t_mode = target_msg.get("trans_mode", "Chuẩn hóa trực tiếp")
            flags = target_msg.get("risk_flags", [])

            if flags:
                badges_html = "".join(f'<span class="risk-badge">{html.escape(f)}</span>' for f in flags)
                st.markdown(f'<div style="margin-bottom:6px;">{badges_html}</div>', unsafe_allow_html=True)

            st.caption(f"Bản dịch chuẩn hóa ({t_mode}):")
            hl_html = build_highlighted_html(en_analyzed, vectorizer, model)
            st.markdown(f'<div class="hl-box">{hl_html}</div>', unsafe_allow_html=True)

            top_kws = extract_top_keywords(en_analyzed, vectorizer, model, top_n=5)
            if top_kws:
                kw_chips = []
                for tok, sc in top_kws:
                    if sc > 0:
                        kw_chips.append(f'<span class="kw-chip-spam">{html.escape(tok)} (+{sc:.2f})</span>')
                    else:
                        kw_chips.append(f'<span class="kw-chip-ham">{html.escape(tok)} ({sc:.2f})</span>')
                st.markdown(
                    f'<div style="font-size:0.76rem; color:#94a3b8; margin-bottom:10px;">'
                    f'<b>Top từ khóa quyết định (Log-Odds):</b><br>{"".join(kw_chips)}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.progress(p_spam, text=f"Điểm rủi ro tổng hợp: {p_spam*100:.2f}% (Naive Bayes gốc: {nb_p*100:.1f}%)")

            if is_spam_flag:
                st.error("🚨 Phân loại: TIN NHẮN RÁC (SPAM)")
            else:
                st.success("✅ Phân loại: TIN NHẮN THƯỜNG (HAM)")

            fb_c1, fb_c2 = st.columns(2)
            pred_str = "spam" if is_spam_flag else "ham"
            if fb_c1.button("👍 AI đoán chuẩn", key=f"ok_{selected_idx}", use_container_width=True):
                st.toast("Đã ghi nhận đánh giá chính xác!", icon="✅")
            if fb_c2.button("👎 Báo cáo đoán sai", key=f"err_{selected_idx}", use_container_width=True):
                log_active_learning_feedback(target_msg, pred_str, me)
                st.toast("Đã lưu mẫu sai vào data/feedback_errors.csv để tái huấn luyện!", icon="📝")
        else:
            st.info("Cuộc trò chuyện chưa có tin nhắn nào để phân tích.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# TAB 3: QUÉT FILE HÀNG LOẠT (BATCH AUDIT)
# ==============================================================================
with tab_batch_mode:
    st.markdown("### 📂 Kiểm Tra & Lọc Tin Nhắn Hàng Loạt (Batch Audit)")
    st.caption("Tải lên tệp `.txt` (mỗi dòng 1 tin nhắn) hoặc `.csv` (có cột `text` / `message` / `sms`) để quét tự động bằng Hybrid AI.")

    b_col1, b_col2 = st.columns([2, 1])
    with b_col1:
        uploaded_file = st.file_uploader("Chọn tệp tin nhắn cần quét:", type=["txt", "csv"])
    with b_col2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        run_sample_batch = st.button("⚡ Chạy thử bộ dữ liệu mẫu (10 tin đa ngôn ngữ)", use_container_width=True)

    batch_texts = []
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".txt"):
                content = uploaded_file.read().decode("utf-8", errors="ignore")
                batch_texts = [line.strip() for line in content.splitlines() if line.strip()]
            elif uploaded_file.name.endswith(".csv"):
                df_up = pd.read_csv(uploaded_file)
                target_col = next((c for c in df_up.columns if c.lower() in ["text", "message", "sms", "content", "v2"]), df_up.columns[0])
                batch_texts = df_up[target_col].dropna().astype(str).tolist()
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")

    elif run_sample_batch:
        batch_texts = [
            "Chào cậu, sáng mai 7h30 có tiết thực hành mạng máy tính nhé.",
            "CHÚC MỪNG! Bạn nhận được gói vay ưu đãi 80 triệu lãi suất 0%. Đăng ký tại bit.ly/vay-nhanh-24h",
            "URGENT! You have won a £1,000 Walmart gift card. Go to http://bit.ly/claim-now to claim!",
            "Mẹ ơi tối nay con về muộn một chút vì họp nhóm đồ án ở trường.",
            "Cảnh báo: Tài khoản ngân hàng của bạn bị tạm khóa. Truy cập www.bank-verify-vn.com để mở lại.",
            "긴급 공지! 무담보 즉시 대출 최대 5,000만원 승인 완료! 지금 바로 010-9876-5432로 전화하세요!",
            "Hey, are we still grabbing lunch at 12:30 today?",
            "FREE entry in 2 a wkly comp to win FA Cup final tkts! Text FA to 87121 now!",
            "Nhờ bạn gửi giúp mình file slide thuyết trình FIT4013 qua email nhé.",
            "Thuê bao quý khách được tặng 500.000đ vào tài khoản khuyến mãi, soạn DK gửi 9029 ngay!"
        ]

    if batch_texts:
        results = []
        prog_bar = st.progress(0, text="Đang phân tích dữ liệu...")
        total_items = len(batch_texts)

        for idx, raw_t in enumerate(batch_texts):
            en_t, _ = translate_to_english(raw_t)
            res = analyze_message_hybrid(raw_t, en_t, vectorizer, model)
            score = res["final_prob"] if use_hybrid_boost else res["nb_prob"]
            label = "SPAM" if score >= my_threshold else "HAM"
            results.append({
                "STT": idx + 1,
                "Tin nhắn gốc": raw_t,
                "Bản dịch chuẩn hóa": en_t,
                "Phân loại": label,
                "Xác suất Spam (%)": round(score * 100, 2),
                "Dấu hiệu phát hiện": ", ".join(res["risk_flags"]) if res["risk_flags"] else "Không có"
            })
            prog_bar.progress((idx + 1) / total_items, text=f"Đã quét {idx + 1}/{total_items} tin nhắn...")

        prog_bar.empty()
        df_res = pd.DataFrame(results)

        spam_cnt = int((df_res["Phân loại"] == "SPAM").sum())
        ham_cnt = total_items - spam_cnt

        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng tin đã quét", total_items)
        m2.metric("Tin an toàn (HAM)", ham_cnt)
        m3.metric("Tin rác phát hiện (SPAM)", spam_cnt)

        st.dataframe(df_res, use_container_width=True, hide_index=True)

        csv_bytes = df_res.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="📥 Tải xuống Báo cáo Kết quả (.CSV)",
            data=csv_bytes,
            file_name=f"safechat_audit_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary"
        )