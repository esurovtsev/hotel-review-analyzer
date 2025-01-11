document.addEventListener('DOMContentLoaded', () => {
    const fileUpload = document.getElementById('file-upload');
    const uploadContent = document.getElementById('upload-content');
    const fileInfo = document.getElementById('file-info');
    const selectedFilename = document.getElementById('selected-filename');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    // Drag and drop functionality
    const dropZone = document.querySelector('label[for="file-upload"]');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('drag-over');
    }

    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileUpload.files = files;
        handleFileSelect(files[0]);
    }

    // File selection handling
    fileUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFileSelect(file);
    });

    function handleFileSelect(file) {
        if (file) {
            if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
                selectedFilename.textContent = file.name;
                fileInfo.classList.remove('hidden');
                analyzeBtn.classList.remove('hidden');
                errorMessage.classList.add('hidden');
            } else {
                showError('Please upload a CSV file');
                resetFileUpload();
            }
        }
    }

    // Analysis handling
    analyzeBtn.addEventListener('click', async () => {
        const file = fileUpload.files[0];
        if (!file) {
            showError('Please select a file first');
            return;
        }

        // Show loading state
        loading.classList.remove('hidden');
        analyzeBtn.classList.add('hidden');
        errorMessage.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:5001/generate-report', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            // Handle successful response
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'hotel_review_analysis.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Reset the form
            resetFileUpload();
        } catch (error) {
            showError('Failed to generate report. Please try again.');
            console.error('Error:', error);
        } finally {
            loading.classList.add('hidden');
            analyzeBtn.classList.remove('hidden');
        }
    });

    function showError(message) {
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
    }

    function resetFileUpload() {
        fileUpload.value = '';
        fileInfo.classList.add('hidden');
        analyzeBtn.classList.add('hidden');
    }
});
