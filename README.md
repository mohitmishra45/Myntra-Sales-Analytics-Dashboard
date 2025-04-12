# Myntra Sales Analytics Dashboard

## 📊 Project Overview
This project is a comprehensive Data Science solution that uses Python and Streamlit to analyze sales data from Myntra, a leading e-commerce platform. It transforms raw sales data into an interactive dashboard with rich visualizations, AI-powered insights, and a real-time Gemini-based chat assistant.

The dashboard helps stakeholders:
- Understand sales trends and customer behavior
- Evaluate product, brand, and category performance
- Make data-driven decisions using AI recommendations

---

## 👨‍💻 Submitted By
**Name:** Mohit Kumar Mishra  
**Registration No:** 12310399  
**Programme & Section:** BTECH-CSE, K23SG  
**Course Code:** INT375  
**Under Guidance Of:**  
Dr. Manpreet Singh Sehgal  
Assistant Professor, School of Computer Science  
Lovely Professional University, Phagwara  

---

## 📁 Dataset Source
- **Name:** Myntra Sales Dataset  
- **Source:** [GitHub - Myntra Dataset](https://github.com/fingertipsDIS/Myntra-Analysis-Power-BI/blob/main/PowerBI%20Dataset%20%26%20Related%20Files/Myntra%20dataset.xlsx)  
- **Features:**  
  - Order ID, Customer ID, Product ID, Date, Price, Discount%, Customer Age  
  - City, State, Category, Sub-category, Brand, Size, Color, Ratings

---

## 🔧 Tools & Technologies Used
- **Languages:** Python  
- **Libraries:** Pandas, NumPy, Matplotlib, Seaborn, scikit-learn  
- **Framework:** Streamlit  
- **AI Assistant:** Gemini API (Mock integrated)  

---

## 🧹 Data Preprocessing
- Handling missing values & duplicates  
- Feature engineering (e.g., extracting month/year/hour from date)  
- Encoding and normalization of categorical values  
- Filtering data for active/inactive customers  

---

## 📈 Key Features of the Dashboard

### 1. Sales Trend Over Time  
![Sales Trend]![image](https://github.com/user-attachments/assets/034e0b01-fc32-4baf-a296-958769d7b39c)


---

### 2. Category Distribution  
![Category Distribution]![image](https://github.com/user-attachments/assets/ec459d2f-c124-49e1-a134-7d78caf0c457)


---

### 3. Sub-category Distribution  
![Sub-category Distribution]![image](https://github.com/user-attachments/assets/e9c6b7bb-f123-47e2-80af-6b894ccf79b7)


---

### 4. Top Brands by Sales  
![Top Brands]![image](https://github.com/user-attachments/assets/ad1d6b86-6b93-47ae-888b-e672b03bcc7f)


---

### 5. Brand Performance Over Time  
![Brand Performance]![image](https://github.com/user-attachments/assets/bcc3adaa-5f57-4a98-9241-bbf43638cbaf)


---

### 6. Customer Age Distribution  
![Customer Age Distribution](images/customer_age_distribution.png)

---

### 7. Rating Distribution  
![Rating Distribution]![image](https://github.com/user-attachments/assets/dadcba9a-d242-46b1-a2cc-7efdf90a0a84)


---

### 8. Geographical Analysis  
![Geographical Analysis]![image](https://github.com/user-attachments/assets/af59d0c2-0eaa-4624-a0f2-14fa0544dc8a)


---

### 9. Holistic Sales Trend Analysis  
![Holistic Sales]![image](https://github.com/user-attachments/assets/2a432757-0fba-417d-9d2e-6adfba41171b)


---
### 10. Average Monthly Sales  
![Average Monthly Sales]![image](https://github.com/user-attachments/assets/e7302394-51d3-48bb-ba13-5330b020d9fe)


---

### 11. Average Yearly Sales  
![Average Yearly Sales]![image](https://github.com/user-attachments/assets/05e0c9ca-279d-41aa-b008-e7b331a27738)


---

### 13. AI Sales Analysis & Optimization  
🤖 Insights and recommendations based on ML algorithms  
_(Graph or Summary not displayed in image, visible on dashboard interface)_
![image](https://github.com/user-attachments/assets/c20edb33-1d09-4333-ac49-4bef78f5a131)

---

### 14. Low Performance Analysis  
![Low Performance]![image](https://github.com/user-attachments/assets/464bfee1-b928-4a4b-a3d2-91214bc3a7bc)


---

### 15. Optimization Suggestions  
📌 Textual Recommendations & Strategy Table  
_(Snapshot or visual from Streamlit dashboard)_  
![Optimization Tips]![image](https://github.com/user-attachments/assets/537dba38-e536-4aca-a8dd-122fece155c5)


---

### 16. Filters (State & Category)
🎛 Dynamic filtering capability for detailed insights  
![Filters](images/filters_section.png)

---

### 17. Gemini-based Chat Assistant  
💬 Integrated AI Assistant to answer dataset-related questions  
![Chat Assistant]![image](https://github.com/user-attachments/assets/2e8cf393-75f0-4f18-8261-c230d7574510)


---

## ✅ Conclusion
The Myntra Sales Analytics Dashboard demonstrates the power of Python and AI in turning raw data into business intelligence. With interactive charts and smart recommendations, it empowers decision-makers to enhance efficiency and customer satisfaction.

---

## 🚀 Future Enhancements
- Real-time API-based data streaming  
- NLP-based voice assistant for interactive queries  
- Multilingual chat assistant support  
- Predictive analytics for stock and customer segmentation  
- ROI calculator for campaign evaluation

---

## 📚 References
- Python (Pandas, NumPy, Seaborn, Matplotlib)  
- Streamlit Docs: https://docs.streamlit.io  
- scikit-learn for ML models  
- Maven Analytics for dataset structure guidance  
- Gemini AI Documentation  

---

## 📌 How to Run

```bash
# Step 1: Clone the Repository
git clone https://github.com/yourusername/myntra-sales-dashboard.git

# Step 2: Navigate to Project Directory
cd myntra-sales-dashboard

# Step 3: Install Dependencies
pip install -r requirements.txt

# Step 4: Run the Dashboard
streamlit run app.py
