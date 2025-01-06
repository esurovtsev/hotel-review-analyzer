import json
import os
from fpdf import FPDF
import matplotlib.pyplot as plt
from PIL import Image
from tempfile import NamedTemporaryFile

class PDFReport(FPDF):
    """
    A class for creating a professional PDF report for hotel review analysis.
    """

    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "Hotel Review Analysis Report", border=False, ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def cover_page(self):
        self.add_page()
        self.set_font("Helvetica", "B", 20)
        self.cell(0, 80, "Hotel Review Analysis Report", ln=True, align="C")
        self.set_font("Helvetica", "", 16)
        self.cell(0, 10, "Key Insights and Recommendations for Service Excellence", ln=True, align="C")
        self.ln(20)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def section_body(self, text):
        self.set_font("Helvetica", "", 12)
        self.multi_cell(0, 10, text)
        self.ln()

    def embed_chart(self, chart_path, title=None):
        """
        Embed a chart directly into the PDF from a file path.

        Args:
            chart_path (str): Path to the image file for the chart.
            title (str): Title of the chart.
        """
        if title:
            self.section_title(title)
        try:
            # Open the image file
            with Image.open(chart_path) as img:
                # Save the image temporarily to disk
                with NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                    temp_path = tmp_file.name
                    img.save(temp_path, format="PNG")
            
            # Embed the temporarily saved image into the PDF
            self.image(temp_path, x=10, w=190)
            self.ln(10)
            
            # Delete the temporary file after embedding
            os.remove(temp_path)
        except Exception as e:
            print(f"Error embedding chart from {chart_path}: {e}")

def generate_sentiment_bar_chart(sentiment_counts, output_path):
    """
    Generate a bar chart for sentiment distribution.

    Args:
        sentiment_counts (dict): Counts of positive, negative, and neutral reviews.
        output_path (str): Path to save the chart image.
    """
    sentiments = list(sentiment_counts.keys())
    counts = list(sentiment_counts.values())

    plt.figure(figsize=(8, 5))
    plt.bar(sentiments, counts, color=['green', 'red', 'gray'])
    plt.title("Sentiment Distribution")
    plt.xlabel("Sentiments")
    plt.ylabel("Number of Reviews")
    plt.savefig(output_path)
    plt.close()
    print(f"Sentiment bar chart saved to {output_path}")

def generate_negative_topic_pie_chart(negative_topic_percentages, output_path):
    """
    Generate a pie chart for negative topic percentages.

    Args:
        negative_topic_percentages (dict): Percentage distribution of negative topics.
        output_path (str): Path to save the chart image.
    """
    topics = list(negative_topic_percentages.keys())
    percentages = list(negative_topic_percentages.values())

    plt.figure(figsize=(8, 5))
    plt.pie(percentages, labels=topics, autopct='%1.1f%%', startangle=140)
    plt.title("Negative Topics Distribution")
    plt.savefig(output_path)
    plt.close()
    print(f"Negative topics pie chart saved to {output_path}")

def generate_pdf_report(report_data, output_dir="outputs", report_name="final_report.pdf"):
    """
    Generate the final PDF report for hotel review analysis.

    Args:
        report_data (dict): Dictionary containing all data required for the report.
        output_dir (str): Directory to save the report and intermediate outputs.
        report_name (str): Name of the final report file (default is "final_report.pdf").
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    charts_dir = os.path.join(output_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # Generate charts
    sentiment_chart_path = os.path.join(charts_dir, "sentiment_distribution.png")
    negative_topics_chart_path = os.path.join(charts_dir, "negative_topics_distribution.png")

    generate_sentiment_bar_chart(report_data["review_counts"], sentiment_chart_path)
    generate_negative_topic_pie_chart(
        report_data["percentage_distribution_by_sentiment"]["negative"],
        negative_topics_chart_path
    )

    # Initialize the PDF report
    pdf = PDFReport()

    # Step 1: Add Cover Page
    pdf.cover_page()

    # Step 2: Add Summary of Sentiments
    pdf.add_page()
    pdf.section_title("Sentiment Analysis Summary")
    pdf.section_body(f"""
        Number of Reviews by Sentiment:
        Positive: {report_data['review_counts']['positive']}
        Negative: {report_data['review_counts']['negative']}
        Neutral: {report_data['review_counts']['neutral']}
    """)

    # Step 3: Add Sentiment Distribution Chart
    pdf.embed_chart(sentiment_chart_path, title="Sentiment Distribution")

    # Step 4: Add Negative Topic Percentages Chart
    pdf.embed_chart(negative_topics_chart_path, title="Percentage Distribution of Negative Topics")

    # Step 5: Add Problem Descriptions for Top 3 Worst Topics
    pdf.add_page()
    pdf.section_title("Problem Analysis - Top 3 Worst Topics")
    for problem in report_data["problems_summary"]:
        pdf.section_title(f"Topic: {problem['topic']}")
        pdf.section_body(problem["problem_description"])

    # Step 6: Add Consolidated Findings and Recommendations
    pdf.add_page()
    pdf.section_title("Consolidated Findings and Recommendations")

    # Add consolidated problem description
    pdf.section_title("Consolidated Problem Description")
    pdf.section_body(report_data["general_problem_description"])

    # Add consolidated recommendations
    pdf.section_title("Consolidated Recommendations")
    for i, recommendation in enumerate(report_data["consolidated_recommendations"], 1):
        pdf.section_body(f"{i}. {recommendation}")

    # Save the final PDF
    final_pdf_path = os.path.join(output_dir, report_name)
    pdf.output(final_pdf_path)
    print(f"Final report saved to {final_pdf_path}")

# Example usage
if __name__ == "__main__":
    # Load report data
    input_file = "data/processed/report_data.json"
    with open(input_file, "r") as json_file:
        report_data = json.load(json_file)

    # Generate the report with a custom name
    generate_pdf_report(report_data, report_name="hotel_review_analysis.pdf")