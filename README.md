# FIT4013 - Bài tập lớn Nhập môn Học máy: Phân loại Tin nhắn Rác (SMS Spam Classification)

Dự án thực hiện bài tập lớn cuối kỳ học phần **Nhập môn Học máy (FIT4013)** – **Đề tài 3: Phân loại tin nhắn rác** (nhóm đề tài Xử lý Ngôn ngữ Tự nhiên).

- **Trường:** Đại học Đại Nam – Khoa Công nghệ Thông tin
- **Giảng viên hướng dẫn:** ThS. Lê Thị Thùy Trang
- **Nhóm thực hiện:** Nhóm 10
- **Sinh viên thực hiện:** Đoàn Quốc Bảo, Hà Minh Quân

---

## 1. Giới thiệu bài toán và nguồn dữ liệu

### 1.1. Mục tiêu
Xây dựng quy trình học máy hoàn chỉnh và có khả năng tái tạo để phân loại tin nhắn SMS thành hai nhóm:
- **`ham` (0):** Tin nhắn hợp lệ, thông thường.
- **`spam` (1):** Tin nhắn rác, quảng cáo trái phép hoặc lừa đảo.

Do dữ liệu mất cân bằng lớp nghiêm trọng và chi phí chặn nhầm tin nhắn quan trọng cao hơn bỏ sót tin rác, hệ thống tập trung tối ưu hóa đồng thời **Precision**, **Recall** và **F1-score** trên lớp `spam`.

### 1.2. Nguồn dữ liệu
Bộ dữ liệu **SMS Spam Collection v.1** được thu thập và công bố bởi Tiago A. Almeida và José María Gómez Hidalgo:
- **Trang chủ dữ liệu:** http://www.dt.fee.unicamp.br/~tiago/smsspamcollection/
- **Bài báo tham chiếu:** Almeida, T.A., Gómez Hidalgo, J.M., Yamakami, A. *"Contributions to the study of SMS Spam Filtering: New Collection and Results"*, ACM DOCENG'11.
- **Quy mô thực tế:** Tệp `SMSSpamCollection` gồm **5.572** tin nhắn SMS tiếng Anh (4.825 `ham` chiếm **86,59%** và 747 `spam` chiếm **13,41%**), không có giá trị khuyết thiếu và có **403** mẫu trùng lặp (đã được loại bỏ trước khi chia tập huấn luyện/kiểm thử để tránh rò rỉ dữ liệu).

---

## 2. Cấu trúc thư mục dự án

```text
FIT4013-SMS-Spam-Classification/
├── data/
│   └── SMSSpamCollection               # Bộ dữ liệu gốc (phân tách bằng ký tự Tab)
├── models/
│   ├── mnb_spam_classifier.joblib      # Mô hình Multinomial Naive Bayes tốt nhất (alpha=0.2)
│   └── tfidf_vectorizer.joblib         # Bộ trích xuất đặc trưng TF-IDF đã huấn luyện
├── notebooks/
│   └── 01_eda_and_modeling.ipynb       # Notebook thực hiện toàn bộ quy trình EDA -> Error Analysis
├── reports/
│   ├── figures/                        # Thư mục chứa 4 biểu đồ và ảnh minh họa kết quả
│   │   ├── eda_overview.png            # Biểu đồ phân tích khám phá dữ liệu (EDA)
│   │   ├── confusion_matrices.png      # So sánh ma trận nhầm lẫn Baseline vs Tối ưu
│   │   ├── top_features.png            # Top 15 đặc trưng (Unigram/Bigram) nhận diện Spam
│   │   └── demo_app.png                # Ảnh chụp giao diện ứng dụng Web Demo
│   ├── main.tex                        # Mã nguồn báo cáo khoa học LaTeX
│   └── Bao_cao_BTL_FIT4013.pdf         # Báo cáo bài tập lớn định dạng PDF hoàn chỉnh
├── app.py                              # Ứng dụng Web Demo phân loại tin nhắn thời gian thực (Streamlit)
├── requirements.txt                    # Danh sách thư viện Python cần thiết
├── AI_USAGE.md                         # Khai báo minh bạch việc sử dụng công cụ AI hỗ trợ
└── README.md                           # Hướng dẫn cài đặt và vận hành dự án
```

---

## 3. Hướng dẫn cài đặt và chạy chương trình

### Bước 1: Sao chép kho mã nguồn và cài đặt thư viện
Yêu cầu máy tính đã cài đặt **Python 3.9+**. Mở Terminal (PowerShell hoặc Command Prompt) tại thư mục gốc của dự án và chạy lệnh:

```bash
git clone https://github.com/dathu2006/FIT4013-SMS-Spam-Classification.git
cd FIT4013-SMS-Spam-Classification
py -m pip install -r requirements.txt
py -m pip install notebook deep-translator
```

### Bước 2: Chạy quy trình phân tích dữ liệu, huấn luyện và đánh giá mô hình
1. Đảm bảo tệp dữ liệu `SMSSpamCollection` đã nằm trong thư mục `data/` (mã nguồn sử dụng đường dẫn tương đối `Path.cwd().parent / 'data' / 'SMSSpamCollection'`, tuyệt đối không dùng đường dẫn cứng cá nhân).
2. Khởi động **Jupyter Notebook** trên trình duyệt web bằng lệnh:
   ```bash
   py -m jupyter notebook
   ```
3. Truy cập thư mục `notebooks/`, mở tệp `01_eda_and_modeling.ipynb` và chọn **Run All** để thực thi toàn bộ quy trình từ khám phá dữ liệu (EDA), làm sạch trùng lặp, tiền xử lý, vector hóa, huấn luyện mô hình, phân tích lỗi đến xuất tệp mô hình vào `models/` và lưu biểu đồ vào `reports/figures/`.

### Bước 3: Khởi chạy ứng dụng Web Demo (Streamlit)
Sau khi mô hình đã được huấn luyện và lưu trong thư mục `models/`, chạy lệnh sau tại thư mục gốc để mở giao diện kiểm thử trực quan trên trình duyệt:

```bash
py -m streamlit run app.py
```

Ứng dụng sẽ khởi chạy tại địa chỉ mặc định: `http://localhost:8501`.

---

## 4. Tóm tắt kết quả thực nghiệm chính

Toàn bộ thí nghiệm được chia theo tỷ lệ **80% Train (4.135 mẫu) – 20% Test (1.034 mẫu)** với `stratify=y` và `random_state=42`:

| Kịch bản thí nghiệm | Accuracy (%) | Precision Spam (%) | Recall Spam (%) | F1-score Spam (%) |
| :--- | :---: | :---: | :---: | :---: |
| 1. [Baseline] MNB (`alpha=1.0`) + BOW cơ bản | 98,07 | 93,70 | 90,84 | 92,25 |
| 2. Decision Tree (`max_depth=20`) + BOW cơ bản | 96,71 | 90,08 | 83,21 | 86,51 |
| 3. K-NN (`k=5`, cosine) + BOW cơ bản | 97,00 | 95,45 | 80,15 | 87,14 |
| 4. MNB (`alpha=1.0`) + TF-IDF cải tiến | 97,39 | 100,00 | 79,39 | 88,51 |
| **5. MNB (`alpha=0.2`) + TF-IDF cải tiến** | **98,84** | **100,00** | **90,84** | **95,20** |
| 6. Decision Tree (`max_depth=20`) + TF-IDF cải tiến | 97,49 | 92,68 | 87,02 | 89,76 |
| 7. K-NN (`k=5`, cosine) + TF-IDF cải tiến | 97,10 | 98,10 | 78,63 | 87,29 |

---

## 5. Tài liệu tham khảo & Khai báo AI
- Chi tiết về việc sử dụng công cụ AI hỗ trợ trong quá trình phát triển dự án được ghi rõ tại tệp [`AI_USAGE.md`](./AI_USAGE.md).
- Báo cáo khoa học đầy đủ được trình bày tại tệp [`reports/Bao_cao_BTL_FIT4013.pdf`](./reports/Bao_cao_BTL_FIT4013.pdf) (mã nguồn LaTeX tại [`reports/main.tex`](./reports/main.tex)).