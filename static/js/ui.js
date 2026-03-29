// --- Elements ---
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const analyzeBtn = document.getElementById('analyze-btn');
const thresholdSlider = document.getElementById('threshold');
const thresholdVal = document.getElementById('threshold-val');
const uploadSection = document.getElementById('upload-section');
const resultSection = document.getElementById('result-section');
const resetBtn = document.getElementById('reset-btn');
const outputImage = document.getElementById('output-image');

const scoreCircle = document.getElementById('score-circle');
const scoreValue = document.getElementById('score-value');
const statusText = document.getElementById('status-text');
const statusCard = document.getElementById('status-card');
const actionText = document.getElementById('action-text');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toast-message');

/**
 * Shows a temporary error notification toast.
 * @param {string} message 
 */
export function showToast(message) {
    toastMessage.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

/**
 * Updates UI to indicate a file has been selected via browse/drop
 * @param {File} file 
 */
export function updateFileSelectedUI(file) {
    document.querySelector('.drop-content h3').textContent = 'Image Selected';
    document.querySelector('.drop-content p').textContent = file.name;
    analyzeBtn.disabled = false;
    analyzeBtn.classList.add('ready');
}

/**
 * Number counting animation for percentage
 */
function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        obj.innerHTML = (start + easeOut * (end - start)).toFixed(1);

        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerHTML = end.toFixed(1);
        }
    };
    window.requestAnimationFrame(step);
}

/**
 * Displays the result data from the backend.
 * @param {Object} data 
 */
export function displayResults(data) {
    uploadSection.classList.add('hidden');

    setTimeout(() => {
        uploadSection.style.display = 'none';
        resultSection.classList.remove('hidden');
        resultSection.style.display = 'block';

        const imgWrapper = document.querySelector('.image-wrapper');
        imgWrapper.classList.add('scanning');

        // Bypassing cache if the same file is updated
        outputImage.src = data.result_image_url + '?t=' + new Date().getTime();

        const score = data.cleanliness_percentage;
        animateValue(scoreValue, 0, score, 1500);

        setTimeout(() => {
            scoreCircle.setAttribute('stroke-dasharray', `${score}, 100`);
        }, 100);

        const isClean = data.status.toLowerCase().includes('clean');
        statusCard.classList.remove('status-clean', 'status-dirty');
        statusCard.classList.add(isClean ? 'status-clean' : 'status-dirty');

        statusText.textContent = data.status;
        actionText.textContent = isClean ? 'Ready for Use' : 'Needs Wipe Down';

        setTimeout(() => {
            imgWrapper.classList.remove('scanning');
        }, 3000);

    }, 300);
}

/**
 * Resets the UI flow to upload a new file.
 */
export function resetFlowUI() {
    fileInput.value = '';
    document.querySelector('.drop-content h3').textContent = 'Upload Table Image';
    document.querySelector('.drop-content p').innerHTML = 'Drag & drop or <span class="browse">browse files</span>';

    analyzeBtn.disabled = true;
    analyzeBtn.classList.remove('loading', 'ready');

    scoreCircle.setAttribute('stroke-dasharray', '0, 100');
    scoreValue.textContent = '0';

    resultSection.classList.add('hidden');
    setTimeout(() => {
        resultSection.style.display = 'none';
        uploadSection.style.display = 'block';
        setTimeout(() => uploadSection.classList.remove('hidden'), 50);
    }, 300);
}

/**
 * Enables the loading spinner state on the analyze button
 */
export function setAnalyzeLoading(loading) {
    if (loading) {
        analyzeBtn.classList.add('loading');
        analyzeBtn.disabled = true;
    } else {
        analyzeBtn.classList.remove('loading');
        analyzeBtn.disabled = false;
    }
}
