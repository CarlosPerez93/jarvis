// app.js - UI logic and Eel bridge for J.A.R.V.I.S. 4.0

// Initialize Eel (assumes eel is exposed globally via <script src="/eel.js"></script>)
if (typeof eel === 'undefined') {
    console.error('Eel is not loaded.');
}

// Utility: format time HH:MM:SS
function formatTime(date) {
    return date.toLocaleTimeString('es-AR', { hour12: false });
}

// Boot sequence handling
function startBootSequence() {
    const bootOverlay = document.getElementById('boot-overlay');
    const progressBar = document.getElementById('boot-progress');
    const logContainer = document.getElementById('boot-log');
    let progress = 0;
    const steps = [
        'Loading configuration...',
        'Initializing modules...',
        'Starting wake‑word detector...',
        'Connecting to LLM...',
        'Establishing UI bridge...'
    ];
    function nextStep() {
        if (progress >= steps.length) {
            // Done
            bootOverlay.classList.add('hidden');
            document.getElementById('hud').classList.remove('hidden');
            // Notify Python that UI is ready
            eel.ui_ready();
            return;
        }
        const msg = steps[progress];
        logContainer.innerHTML += `<div>${msg}</div>`;
        logContainer.scrollTop = logContainer.scrollHeight;
        progressBar.style.width = `${((progress + 1) / steps.length) * 100}%`;
        progress++;
        setTimeout(nextStep, 600);
    }
    nextStep();
}

// Clock updater
function startClock() {
    const clockEl = document.getElementById('header-clock');
    setInterval(() => {
        const now = new Date();
        clockEl.textContent = formatTime(now);
    }, 1000);
}

// UI update functions called from Python via Eel
function updateStatus(text, color = '#00ff00') {
    try {
        const statusText = document.getElementById('status-text');
        const statusDot = document.getElementById('status-dot');
        if (statusText) statusText.textContent = text;
        if (statusDot) statusDot.style.background = color;
    } catch (e) {
        console.error("Error updating status:", e);
    }
}

function addChatMessage(sender, message) {
    try {
        const container = document.getElementById('chat-messages');
        if (!container) return;
        const msgEl = document.createElement('div');
        msgEl.className = 'chat-message';
        msgEl.innerHTML = `<strong>${sender}:</strong> ${message}`;
        container.appendChild(msgEl);
        container.scrollTop = container.scrollHeight;
    } catch (e) {
        console.error("Error adding chat message:", e);
    }
}

function updateBiometrics(score, threshold) {
    try {
        const fill = document.getElementById('bio-bar-fill');
        const scoreEl = document.getElementById('bio-score');
        const threshEl = document.getElementById('bio-threshold');
        
        const safeThresh = threshold || 0.85;
        const safeScore = score || 0.0;
        const perc = Math.min((safeScore / safeThresh) * 100, 100);
        
        if (fill) fill.style.width = `${perc}%`;
        if (scoreEl) scoreEl.textContent = safeScore.toFixed(2);
        if (threshEl) threshEl.textContent = safeThresh.toFixed(2);
        
        if (fill) {
            if (safeScore >= safeThresh) {
                fill.style.background = 'limegreen';
            } else {
                fill.style.background = 'crimson';
            }
        }
    } catch (e) {
        console.error("Error updating biometrics:", e);
    }
}

function updateWaveform(dataArray) {
    try {
        const canvas = document.getElementById('waveform-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const width = canvas.width = canvas.offsetWidth;
        const height = canvas.height = canvas.offsetHeight;
        ctx.clearRect(0, 0, width, height);
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        if (!dataArray || dataArray.length === 0) return;
        
        const sliceWidth = width / dataArray.length;
        let x = 0;
        dataArray.forEach((v, i) => {
            const y = (v / 255) * height;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
            x += sliceWidth;
        });
        ctx.stroke();
    } catch (e) {
        console.error("Error updating waveform:", e);
    }
}

function updateFooter(key, value) {
    try {
        const el = document.getElementById(`footer-${key}`);
        if (el) el.textContent = value;
    } catch (e) {
        console.error("Error updating footer:", e);
    }
}

// Hook Eel exposed functions
if (typeof eel !== 'undefined') {
    eel.expose(updateStatus);
    eel.expose(addChatMessage);
    eel.expose(updateBiometrics);
    eel.expose(updateWaveform);
    eel.expose(updateFooter);
}

// DOM ready -> start boot
window.addEventListener('DOMContentLoaded', () => {
    startBootSequence();
    startClock();
});
