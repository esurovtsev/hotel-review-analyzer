# **Hotel Review Analyzer**

🚧 **Work in Progress** 🚧

This project is currently under active development. The README and project structure are subject to change as the implementation progresses.

**Disclaimer**: 
- Detailed documentation for each development step will be added later
- Individual development stages are being tracked in separate git branches
- The final documentation will provide comprehensive insights into the project's evolution

A project demonstrating text analysis and report generation using machine learning and data visualization. This project processes hotel reviews to extract insights, generate structured reports, and visualize data trends. It includes a web interface for user-friendly interaction, showcasing practical AI and data processing methods.


---

## **Goals**
1. Explore text analysis using OpenAI API to extract key themes, sentiment, and statistics.
2. Generate structured reports in PDF format based on analysis.
3. Visualize results with informative charts and graphs.
4. Develop a simple web interface for uploading data and downloading reports.
5. Create a clean and modular Python project to demonstrate coding best practices.

---

## **Technologies Used**
- **Programming Language**: Python
- **Libraries**:
  - **Data Processing**: `pandas`
  - **Text Analysis**: `OpenAI API`
  - **Visualization**: `matplotlib`, `plotly`
  - **Report Generation**: `fpdf`
  - **Web Interface**: `Flask`
- **Tools**:
  - Jupyter Notebook for exploratory analysis
  - Visual Studio Code for development
  - Kaggle dataset for hotel reviews

---

## **Project Structure**
```
Hotel_Review_Analyzer/
├── data/                 # Raw and processed datasets
│   ├── raw/              # Original datasets (e.g., from Kaggle)
│   ├── processed/        # Cleaned and prepared datasets
├── notebooks/            # Jupyter notebooks for exploration
├── src/                  # Source code
│   ├── data_loader.py    # Data loading and preprocessing logic
│   ├── text_analysis.py  # AI-based text analysis scripts
│   ├── report_generator.py  # Report generation scripts
│   ├── visualization.py  # Visualization scripts
│   ├── app.py           # Flask web application
│   ├── static/          # Static files for web interface
│   └── templates/       # HTML templates
├── tests/               # Unit tests
├── outputs/             # Generated reports and visualizations
├── uploads/             # Temporary storage for uploaded files
├── requirements.txt     # List of Python dependencies
├── README.md           # Project documentation
└── .gitignore         # Files and folders excluded from version control
```

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone git@github.com:esurovtsev/hotel-review-analyzer.git
cd Hotel_Review_Analyzer
```

### **2. Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Environment Configuration**
Create a `.env` file in the project root with the following content:
```
OPENAI_API_KEY=your_api_key_here
```

### **5. Prepare the Dataset**
- Download the hotel reviews dataset from Kaggle and place it in the `data/raw/` folder.
- Run the `data_loader.py` script to preprocess the data:
  ```bash
  python src/data_loader.py
  ```

### **6. Run the Application**
```bash
python src/app.py
```
The web interface will be available at `http://localhost:5001`

---

## **Key Features**
- **Text Analysis**: Sentiment analysis and keyword extraction using OpenAI API.
- **Report Generation**: Automated creation of PDF/HTML reports.
- **Data Visualization**: Clear graphs and charts for insights.
- **Web Interface**: User-friendly interface for data upload and report generation.

---

## **How to Contribute**
1. Fork the repository and create a new branch.
2. Make your changes and test thoroughly.
3. Submit a pull request with detailed explanations of your changes.

---

## **Acknowledgments**
- **Dataset**: [TripAdvisor Hotel Reviews Dataset](https://www.kaggle.com/datasets/joebeachcapital/hotel-reviews/data).
- **Inspiration**: Practical projects for AI and data visualization.

---
