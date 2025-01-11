import sys, os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# # Step 1: Basic Flask Server

# In this step, we:
# 1. Set up a simple Flask server.
# 2. Add a test route `/health` to check if the server is running.

# This provides a foundation for building the report generation application.

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return jsonify({"status": "Server is running!"}), 200

# curl http://127.0.0.1:5000/health



# # Step 2: Add File Upload Handling

# In this step, we:
# 1. Add an endpoint `/upload` to accept file uploads.
# 2. Save the uploaded file with a unique temporary name.
# 3. Return the filename for debugging purposes.

# This step focuses on ensuring the server can handle file uploads.

import tempfile
import os
from flask import Flask, request, jsonify

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Endpoint to handle file upload.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save the file with a unique temporary name
    temp_file = tempfile.NamedTemporaryFile(dir=UPLOAD_FOLDER, delete=False, suffix=".csv")
    file.save(temp_file.name)

    return jsonify({"uploaded_file": temp_file.name}), 200

# curl -X POST -F "file=@data/processed/sample.csv" http://127.0.0.1:5000/upload



# # Step 3: Integrate Text Analysis

# In this step, we:
# 1. Use the `batch_process_texts` and `process_and_save_generalized_topics` methods from `text_analysis.py`.
# 2. Process the uploaded file to generate analysis and generalized topics.
# 3. Generate unique temporary file paths for the input, intermediate, and output files to avoid conflicts.
# 4. Clean up temporary files after processing.

# The result will be a processed and generalized JSON file ready for report generation.

from src.text_analysis import batch_process_texts, process_and_save_generalized_topics

OUTPUT_FOLDER="./data/processed/"

@app.route("/process", methods=["POST"])
def process_file():
    """
    Endpoint to process the uploaded file and perform text analysis.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save the file with a unique temporary name
    temp_input_file = tempfile.NamedTemporaryFile(dir=UPLOAD_FOLDER, delete=False, suffix=".csv")
    file.save(temp_input_file.name)

    # Create unique file paths for intermediate and output files
    temp_analysis_file = tempfile.NamedTemporaryFile(dir=OUTPUT_FOLDER, delete=False, suffix=".json").name
    temp_generalized_file = tempfile.NamedTemporaryFile(dir=OUTPUT_FOLDER, delete=False, suffix=".json").name

    try:
        # Step 1: Perform batch processing
        batch_process_texts(temp_input_file.name, temp_analysis_file, limit=10, chunk_size=100)
        # Step 2: Process and save generalized topics
        process_and_save_generalized_topics(temp_analysis_file, temp_generalized_file)
    except Exception as e:
        return jsonify({"error": f"Processing failed: {e}"}), 500
    finally:
        # Clean up the input file
        os.remove(temp_input_file.name)
        # Clean up the analysis file
        os.remove(temp_analysis_file)

    # Return the generalized output file for debugging (can be removed in production)
    return jsonify({"generalized_file": temp_generalized_file}), 200

# curl -X POST -F "file=@data/processed/sample.csv" http://127.0.0.1:5000/process





# # Step 4: Prepare JSON File for Report

# In this step, we:
# 1. Use the `generate_report_data` function from `report_generator.py`.
# 2. Accept the generalized analysis JSON file as input.
# 3. Generate a comprehensive report data JSON file containing:
#    - Sentiment summaries.
#    - Generalized topics with their percentages.
#    - Problem descriptions for top negative topics.
#    - Consolidated findings and recommendations.
# 4. Save the generated JSON file to a temporary location for immediate use.
# 5. Ensure temporary files are cleaned up after processing.

# This functionality ensures that the server processes the analysis results into a structured format ready for visualization and PDF generation.

from flask import Flask, request, jsonify
import os
import tempfile
from src.report_generator import generate_report_data

@app.route("/generate-report-json", methods=["POST"])
def generate_report_json():
    """
    Endpoint to prepare a JSON file for the report.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded file to a temporary location
    temp_input_file = tempfile.NamedTemporaryFile(dir="data/processed", delete=False, suffix=".json")
    file.save(temp_input_file.name)

    # Create a temporary output file
    temp_output_file = tempfile.NamedTemporaryFile(dir="data/processed", delete=False, suffix=".json").name

    try:
        # Generate the report data JSON
        report_data = generate_report_data(temp_input_file.name, temp_output_file)
    except Exception as e:
        os.remove(temp_input_file.name)
        if os.path.exists(temp_output_file):
            os.remove(temp_output_file)
        return jsonify({"error": f"Report generation failed: {e}"}), 500

    # Clean up input file
    os.remove(temp_input_file.name)

    # Return the path to the output JSON file
    return jsonify({"report_data_file": temp_output_file}), 200

# curl -X POST -F "file=@data/processed/tmpp7z4g0ah.json" http://127.0.0.1:5000/generate-report-json



# # Step 5: Generate PDF Report

# In this step, we:
# 1. Use the `generate_pdf_report` function from the provided script.
# 2. Accept the prepared JSON file for the report as input.
# 3. Generate a professional-looking PDF report containing:
#    - Sentiment analysis summaries.
#    - Visualizations (embedded charts for sentiment distribution and negative topic percentages).
#    - Problem descriptions for the top 3 negative topics.
#    - Consolidated findings and actionable recommendations.
# 4. Return the generated PDF file to the user.

# The server will handle temporary files for input/output during the process to ensure a clean and conflict-free operation.



from flask import Flask, request, jsonify, send_file
import os
import tempfile
from src.visualization import generate_pdf_report
import json

@app.route("/generate-pdf-report", methods=["POST"])
def generate_pdf_report_endpoint():
    """
    Endpoint to generate a PDF report from the provided report data JSON file.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded JSON file to a temporary location
    temp_input_file = tempfile.NamedTemporaryFile(dir="data/processed", delete=False, suffix=".json")
    file.save(temp_input_file.name)

    # Generate a temporary output directory for the PDF report
    temp_output_dir = tempfile.TemporaryDirectory(dir="data/processed")
    pdf_report_path = os.path.join(temp_output_dir.name, "final_report.pdf")

    try:
        # Load the report data
        with open(temp_input_file.name, "r") as json_file:
            report_data = json.load(json_file)

        # Generate the PDF report
        generate_pdf_report(report_data, output_dir=temp_output_dir.name, report_name="final_report.pdf")
    except Exception as e:
        # Cleanup temporary files and directories
        os.remove(temp_input_file.name)
        temp_output_dir.cleanup()
        return jsonify({"error": f"PDF generation failed: {e}"}), 500

    # Cleanup input file
    os.remove(temp_input_file.name)

    # Serve the generated PDF file
    #return jsonify({"pdf_report_path": pdf_report_path}), 200
    return send_file(pdf_report_path, as_attachment=True, download_name="final_report.pdf")

# curl -X POST -F "file=@data/processed/tmph_3_afdk.json" http://127.0.0.1:5000/generate-pdf-report --output outputs/report123.pdf




if __name__ == "__main__":
    app.run(debug=True, port=5000)