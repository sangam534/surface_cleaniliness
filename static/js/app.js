import { analyzeImage } from './api.js';
import {
    showToast,
    updateFileSelectedUI,
    displayResults,
    resetFlowUI,
    setAnalyzeLoading
} from './ui.js';

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const thresholdSlider = document.getElementById('threshold');
    const thresholdVal = document.getElementById('threshold-val');
    const resetBtn = document.getElementById('reset-btn');

    let currentFile = null;

    // Threshold Slider
    thresholdSlider.addEventListener('input', (e) => {
        thresholdVal.textContent = e.target.value;
    });

    // Dropzone Events
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, () => {
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');

        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFile(fileInput.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.match('image.*')) {
            showToast('Please upload an image file (PNG, JPG, WEBP)');
            return;
        }
        currentFile = file;
        updateFileSelectedUI(file);
    }

    // Analyze Button
    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        setAnalyzeLoading(true);

        try {
            const data = await analyzeImage(currentFile, thresholdSlider.value);
            displayResults(data);
        } catch (error) {
            showToast(error.message);
            setAnalyzeLoading(false);
        }
    });

    // Reset Flow
    resetBtn.addEventListener('click', () => {
        currentFile = null;
        resetFlowUI();
    });
});
