import re
from pathlib import Path
import joblib
import streamlit as st

st.set_page_config(page_title="FIT4013 - Phân loại Tin nhắn Rác", page_icon="🛡️", layout="centered")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "mnb_spam_classifier.joblib"
VEC_PATH = BASE_DIR / "models" / "tfidf_vectorizer.joblib"

def preprocess_sms_optimized(text: str) -> str:
    text = text.lower()
    text = re.sub(r'(http\S+|www\.\S+|\S+\.(com|co\.uk|net|org)\S*)', ' token_url ', text)
    text = re.sub(r'([£$€]\s*\d+([.,]\d+)?|\d+([.,]\d+)?\s*(gbp|usd|pound|pounds))', ' token_money ', text)
    text = re.sub(r'\d+', ' token_num ', text)
    text = re.sub(r'!+', ' token_exclam ', text)
    text = re.sub(r'[^a-z0-9_\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@st.cache_resource
def load_artifacts():
    vectorizer = joblib.load(VEC_PATH)
    model = joblib.load(MODEL_PATH)
    return vectorizer, model

st.title("🛡️ Hệ thống Phân loại Tin nhắn Rác (SMS Spam Detection)")
st.caption("Bài tập lớn Học phần Nhập môn Học máy (FIT4013) - Đề tài 3")

if not MODEL_PATH.exists() or not VEC_PATH.exists():
    st.error("Chưa tìm thấy file mô hình trong thư mục `models/`. Vui lòng chạy hết Notebook `01_eda_and_modeling.ipynb` trước.")
    st.stop()

vectorizer, model = load_artifacts()

# Các ví dụ mẫu để bấm thử nhanh khi bảo vệ
st.subheader("1. Chọn tin nhắn mẫu hoặc tự nhập nội dung")
sample_choice = st.selectbox(
    "Thử nhanh với các mẫu có sẵn:",
    [
        "-- Tự nhập tin nhắn bên dưới --",
        "URGENT! Your Mobile No 07808726822 was awarded a £2,000 Bonus Caller Prize! Call 0871-872-9758 now!",
        "FreeMsg: Txt CALL to No: 86888 & claim your reward of 3 hours talk time now!",
        "Ok lar... Joking wif u oni... See you at the library at 3pm.",
        "Hey, are we still meeting for the machine learning project review tonight?"
    ]
)

default_text = "" if sample_choice.startswith("--") else sample_choice
user_input = st.text_area("Nội dung tin nhắn SMS (tiếng Anh):", value=default_text, height=120)

if st.button("🔍 Kiểm tra tin nhắn", type="primary"):
    if not user_input.strip():
        st.warning("Vui lòng nhập nội dung tin nhắn cần kiểm tra.")
    else:
        cleaned_text = preprocess_sms_optimized(user_input)
        features = vectorizer.transform([cleaned_text])
        pred = model.predict(features)[0]
        proba = model.predict_proba(features)[0]

        st.divider()
        st.subheader("2. Kết quả phân tích")
        if pred == 1:
            st.error(f"🚨 **CẢNH BÁO: TIN NHẮN RÁC (SPAM)** — Độ tin cậy: **{proba[1]*100:.2f}%**")
        else:
            st.success(f"✅ **AN TOÀN: TIN NHẮN THƯỜNG (HAM)** — Độ tin cậy: **{proba[0]*100:.2f}%**")

        with st.expander("Xem chi tiết quá trình tiền xử lý đặc trưng"):
            st.code(cleaned_text, language="text")