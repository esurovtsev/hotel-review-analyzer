import os
import tempfile
import json
from flask import Flask, request, jsonify, send_file, render_template
from text_analysis import batch_process_texts, process_and_save_generalized_topics
from report_generator import generate_report_data
from visualization import generate_pdf_report

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/generate-report", methods=["POST"])
def generate_report():
    """
    Endpoint to generate a PDF report from an uploaded CSV file.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Define directories for processing
    upload_folder = tempfile.TemporaryDirectory()
    output_folder = tempfile.TemporaryDirectory()

    # Temporary file paths
    temp_input_csv = tempfile.NamedTemporaryFile(dir=upload_folder.name, delete=False, suffix=".csv").name
    temp_analysis_json = tempfile.NamedTemporaryFile(dir=output_folder.name, delete=False, suffix=".json").name
    temp_generalized_json = tempfile.NamedTemporaryFile(dir=output_folder.name, delete=False, suffix=".json").name
    temp_report_json = tempfile.NamedTemporaryFile(dir=output_folder.name, delete=False, suffix=".json").name
    temp_pdf_report = tempfile.NamedTemporaryFile(dir=output_folder.name, delete=False, suffix=".pdf").name

    try:
        # Save the uploaded CSV file
        file.save(temp_input_csv)

        # Step 1: Perform text analysis
        batch_process_texts(temp_input_csv, temp_analysis_json, limit=10, chunk_size=100)
        process_and_save_generalized_topics(temp_analysis_json, temp_generalized_json)

        # Step 2: Generate report data JSON
        generate_report_data(temp_generalized_json, temp_report_json)

        # Step 3: Generate PDF report
        with open(temp_report_json, "r") as json_file:
            report_data = json.load(json_file)
        generate_pdf_report(report_data, output_dir=os.path.dirname(temp_pdf_report), report_name=os.path.basename(temp_pdf_report))

        # Return the PDF file
        return send_file(temp_pdf_report, as_attachment=True, download_name="final_report.pdf")

    except Exception as e:
        # Handle any exceptions and clean up
        return jsonify({"error": f"Failed to generate report: {e}"}), 500
    finally:
        # Clean up all temporary files and directories
        if os.path.exists(temp_input_csv):
            os.remove(temp_input_csv)
        if os.path.exists(temp_analysis_json):
            os.remove(temp_analysis_json)
        if os.path.exists(temp_generalized_json):
            os.remove(temp_generalized_json)
        if os.path.exists(temp_report_json):
            os.remove(temp_report_json)
        if os.path.exists(temp_pdf_report):
            os.remove(temp_pdf_report)
        upload_folder.cleanup()
        output_folder.cleanup()

if __name__ == "__main__":
    app.run(debug=True, port=5001)