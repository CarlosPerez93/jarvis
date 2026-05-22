// app.js — Fullscreen Orb Engine for J.A.R.V.I.S. 4.0
// Canvas-based orb with organic rings, flower of life, voice wave distortion,
// orbiting dots, biometrics arc, and boot sequence.

// ─── Eel Guard ───
if (typeof eel === 'undefined') {
  console.error('Eel is not loaded.');
}

// ─── Global State ───
const state = {
  // Boot
  bootPhase: 'building', // 'building' | 'complete'
  ringReveal: 0,         // 0→1 how much of the orb is revealed
  orbOpacity: 0,         // 0→1 master opacity for the orb

  // Audio
  audioData: new Float32Array(128).fill(128),
  smoothAudio: new Float32Array(128).fill(128),
  audioEnergy: 0,
  targetEnergy: 0,

  // Biometrics
  bio: { score: 0, targetScore: 0, threshold: 0.85, visible: false },

  // Status
  status: { text: 'INITIALIZING', color: '#00ff00' },

  // Effects
  pulseWaves: [],   // { birth, color, maxRadius }

  // Particles
  particles: [],

  // Time
  time: 0,
};

// ─── Canvas Setup ───
const canvas = document.getElementById('orb-canvas');
const ctx = canvas.getContext('2d');
let W, H, cx, cy, R; // width, height, center, base radius
const dpr = window.devicePixelRatio || 1;

function resize() {
  W = window.innerWidth;
  H = window.innerHeight;
  canvas.width = W * dpr;
  canvas.height = H * dpr;
  canvas.style.width = W + 'px';
  canvas.style.height = H + 'px';
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  cx = W / 2;
  cy = H / 2 - H * 0.04; // slightly above vertical center
  R = Math.min(W, H) * 0.27;

  initParticles();
}

window.addEventListener('resize', resize);
resize();

// ══════════════════════════════════════════════
//  PARTICLES
// ══════════════════════════════════════════════
function initParticles() {
  state.particles = [];
  const count = Math.floor(Math.min(W, H) * 0.06);
  for (let i = 0; i < count; i++) {
    state.particles.push({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.25,
      size: Math.random() * 1.5 + 0.3,
      baseOpacity: Math.random() * 0.25 + 0.05,
    });
  }
}

function drawParticles(t) {
  const particles = state.particles;
  for (let i = 0; i < particles.length; i++) {
    const p = particles[i];
    p.x += p.vx;
    p.y += p.vy;

    // Wrap
    if (p.x < -5) p.x = W + 5;
    if (p.x > W + 5) p.x = -5;
    if (p.y < -5) p.y = H + 5;
    if (p.y > H + 5) p.y = -5;

    // Subtle attraction to orb center
    const dx = cx - p.x;
    const dy = cy - p.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > R * 0.5 && dist < R * 3) {
      const force = 0.0001 / Math.max(dist * 0.01, 0.1);
      p.vx += dx * force;
      p.vy += dy * force;
    }

    // Damping
    p.vx *= 0.999;
    p.vy *= 0.999;

    const glow = dist < R * 1.5 ? (1 - dist / (R * 1.5)) * 0.15 : 0;
    const alpha = (p.baseOpacity + glow) * state.orbOpacity;

    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0, 220, 200, ${alpha})`;
    ctx.fill();
  }
}

// ══════════════════════════════════════════════
//  BACKGROUND GLOW
// ══════════════════════════════════════════════
function drawBackgroundGlow() {
  const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 2.8);
  grad.addColorStop(0, `rgba(0, 50, 50, ${0.45 * state.orbOpacity})`);
  grad.addColorStop(0.4, `rgba(0, 25, 30, ${0.2 * state.orbOpacity})`);
  grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);
}

// ══════════════════════════════════════════════
//  CORE GLOW
// ══════════════════════════════════════════════
function drawCoreGlow(t) {
  const pulse = 1 + Math.sin(t * 0.7) * 0.08;
  const glowR = R * 0.2 * pulse;

  // Outer soft glow
  const g1 = ctx.createRadialGradient(cx, cy, 0, cx, cy, glowR * 4);
  g1.addColorStop(0, `rgba(0, 255, 220, ${0.12 * state.orbOpacity})`);
  g1.addColorStop(0.4, `rgba(0, 200, 180, ${0.04 * state.orbOpacity})`);
  g1.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = g1;
  ctx.beginPath();
  ctx.arc(cx, cy, glowR * 4, 0, Math.PI * 2);
  ctx.fill();

  // Inner bright core
  const g2 = ctx.createRadialGradient(cx, cy, 0, cx, cy, glowR * 0.6);
  g2.addColorStop(0, `rgba(0, 255, 235, ${0.25 * state.orbOpacity})`);
  g2.addColorStop(1, 'rgba(0, 255, 230, 0)');
  ctx.fillStyle = g2;
  ctx.beginPath();
  ctx.arc(cx, cy, glowR * 0.6, 0, Math.PI * 2);
  ctx.fill();
}

// ══════════════════════════════════════════════
//  ORGANIC RINGS
// ══════════════════════════════════════════════
const RINGS = [
  // Outermost → innermost
  { rf: 1.00, lw: 2.8, op: 0.65, freqs: [3, 5, 8],   amps: [5, 2.5, 1.2],  spd: [0.28, 0.45, 0.18], ph: [0,    1.2, 2.5] },
  { rf: 0.86, lw: 2.0, op: 0.50, freqs: [4, 7, 11],  amps: [4, 2.0, 0.9],  spd: [0.35, 0.30, 0.50], ph: [0.5,  2.0, 3.8] },
  { rf: 0.72, lw: 1.6, op: 0.40, freqs: [5, 9, 14],  amps: [3, 1.5, 0.7],  spd: [0.42, 0.38, 0.30], ph: [1.0,  3.0, 0.7] },
  { rf: 0.56, lw: 1.2, op: 0.30, freqs: [6, 11, 16], amps: [2.5, 1.0, 0.5], spd: [0.30, 0.55, 0.40], ph: [2.0, 0.5, 1.5] },
];

const RING_SEGMENTS = 300;

function drawRing(ring, reveal, audioLvl, t) {
  if (reveal <= 0) return;

  const radius = R * ring.rf;
  const alpha = ring.op * reveal * state.orbOpacity;
  if (alpha < 0.005) return;

  ctx.beginPath();
  ctx.strokeStyle = `rgba(0, 220, 200, ${alpha})`;
  ctx.lineWidth = ring.lw;
  ctx.shadowColor = `rgba(0, 255, 220, ${0.35 * reveal})`;
  ctx.shadowBlur = 10 * reveal;

  for (let i = 0; i <= RING_SEGMENTS; i++) {
    const angle = (i / RING_SEGMENTS) * Math.PI * 2;

    // Organic noise — multiple sine harmonics
    let noise = 0;
    for (let h = 0; h < ring.freqs.length; h++) {
      noise += ring.amps[h] * Math.sin(
        ring.freqs[h] * angle + ring.ph[h] + t * ring.spd[h]
      );
    }

    // Voice wave distortion mapped angularly
    let voiceOffset = 0;
    if (audioLvl > 0.008) {
      const idx = Math.floor((i / RING_SEGMENTS) * state.smoothAudio.length) % state.smoothAudio.length;
      const val = (state.smoothAudio[idx] - 128) / 128; // −1 … 1
      voiceOffset = val * audioLvl * R * 0.10;
    }

    const r = (radius + noise + voiceOffset) * reveal;
    const x = cx + Math.cos(angle) * r;
    const y = cy + Math.sin(angle) * r;

    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }

  ctx.closePath();
  ctx.stroke();
  ctx.shadowBlur = 0;
}

// ══════════════════════════════════════════════
//  FLOWER OF LIFE (Sacred Geometry)
// ══════════════════════════════════════════════
function drawFlowerOfLife(opacity, t) {
  if (opacity <= 0) return;

  const r = R * 0.16;
  // 7 circle centers: center + 6 surrounding
  const centers = [{ x: 0, y: 0 }];
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2 - Math.PI / 6;
    centers.push({ x: Math.cos(a) * r, y: Math.sin(a) * r });
  }

  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(t * 0.04);
  ctx.globalAlpha = opacity * 0.30 * state.orbOpacity;
  ctx.strokeStyle = 'rgba(0, 220, 200, 0.7)';
  ctx.lineWidth = 0.7;
  ctx.shadowColor = 'rgba(0, 255, 220, 0.25)';
  ctx.shadowBlur = 3;

  // Inner circles
  for (const c of centers) {
    ctx.beginPath();
    ctx.arc(c.x, c.y, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Outer bounding circle
  ctx.strokeStyle = 'rgba(0, 220, 200, 0.20)';
  ctx.beginPath();
  ctx.arc(0, 0, r * 2.05, 0, Math.PI * 2);
  ctx.stroke();

  // 6 radial lines for tech feel
  ctx.strokeStyle = 'rgba(0, 220, 200, 0.10)';
  ctx.lineWidth = 0.4;
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(a) * r * 2, Math.sin(a) * r * 2);
    ctx.stroke();
  }

  ctx.restore();
  ctx.shadowBlur = 0;
}

// ══════════════════════════════════════════════
//  ORBITING DOTS
// ══════════════════════════════════════════════
const ORBITS = [
  { rf: 1.12, speed: 0.25,  size: 2.8, offset: 0   },
  { rf: 1.20, speed: -0.18, size: 2.2, offset: 2.1  },
  { rf: 1.28, speed: 0.12,  size: 1.8, offset: 4.3  },
];

function drawOrbitingDots(t) {
  for (const o of ORBITS) {
    const angle = t * o.speed + o.offset;
    const r = R * o.rf;
    const x = cx + Math.cos(angle) * r;
    const y = cy + Math.sin(angle) * r;

    ctx.beginPath();
    ctx.arc(x, y, o.size, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0, 200, 240, ${0.55 * state.orbOpacity})`;
    ctx.shadowColor = 'rgba(0, 200, 255, 0.45)';
    ctx.shadowBlur = 8;
    ctx.fill();
    ctx.shadowBlur = 0;
  }

  // Faint dashed orbit tracks
  ctx.setLineDash([4, 8]);
  for (const o of ORBITS) {
    ctx.beginPath();
    ctx.arc(cx, cy, R * o.rf, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(0, 220, 200, ${0.06 * state.orbOpacity})`;
    ctx.lineWidth = 0.5;
    ctx.stroke();
  }
  ctx.setLineDash([]);
}

// ══════════════════════════════════════════════
//  BIOMETRICS ARC (subtle)
// ══════════════════════════════════════════════
function drawBioArc(t) {
  const bio = state.bio;

  // Smooth interpolation
  bio.score += (bio.targetScore - bio.score) * 0.04;
  if (bio.score < 0.001 && bio.targetScore < 0.001) {
    bio.visible = false;
    return;
  }
  bio.visible = true;

  const radius = R * 1.06;
  const fill = Math.min(bio.score / bio.threshold, 1);
  const startAngle = -Math.PI / 2;
  const sweepAngle = fill * Math.PI * 2;
  const authed = bio.score >= bio.threshold;

  // Background track
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.strokeStyle = `rgba(0, 220, 200, ${0.06 * state.orbOpacity})`;
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // Fill arc
  if (fill > 0.001) {
    ctx.beginPath();
    ctx.arc(cx, cy, radius, startAngle, startAngle + sweepAngle);
    const color = authed
      ? `rgba(0, 255, 110, ${0.65 * state.orbOpacity})`
      : `rgba(255, 70, 70, ${0.55 * state.orbOpacity})`;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.shadowColor = authed ? 'rgba(0, 255, 110, 0.4)' : 'rgba(255, 70, 70, 0.35)';
    ctx.shadowBlur = 6;
    ctx.stroke();
    ctx.shadowBlur = 0;
  }
}

// ══════════════════════════════════════════════
//  PULSE WAVES (triggered by status changes)
// ══════════════════════════════════════════════
function spawnPulse(color) {
  state.pulseWaves.push({
    birth: state.time,
    color: color || 'rgba(0, 255, 220, ALPHA)',
    maxRadius: R * 1.6,
  });
}

function drawPulseWaves(t) {
  const alive = [];
  for (const pw of state.pulseWaves) {
    const age = t - pw.birth;
    const duration = 1.2;
    if (age > duration) continue;

    const progress = age / duration;
    const radius = R * 0.5 + pw.maxRadius * progress;
    const alpha = (1 - progress) * 0.45;

    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.strokeStyle = pw.color.replace('ALPHA', alpha.toFixed(3));
    ctx.lineWidth = 2 * (1 - progress);
    ctx.shadowColor = pw.color.replace('ALPHA', (alpha * 0.6).toFixed(3));
    ctx.shadowBlur = 12 * (1 - progress);
    ctx.stroke();
    ctx.shadowBlur = 0;

    alive.push(pw);
  }
  state.pulseWaves = alive;
}

// ══════════════════════════════════════════════
//  MAIN RENDER LOOP
// ══════════════════════════════════════════════
function render(ts) {
  const t = ts * 0.001;
  state.time = t;

  ctx.clearRect(0, 0, W, H);

  // ── Smooth audio ──
  const sa = state.smoothAudio;
  const ad = state.audioData;
  for (let i = 0; i < sa.length; i++) {
    sa[i] = sa[i] * 0.78 + ad[i] * 0.22;
  }

  // Audio energy (smoothed)
  let energy = 0;
  for (let i = 0; i < sa.length; i++) {
    energy += Math.abs(sa[i] - 128);
  }
  state.targetEnergy = energy / sa.length / 128;
  state.audioEnergy += (state.targetEnergy - state.audioEnergy) * 0.12;

  // ── Draw layers ──
  drawBackgroundGlow();
  drawParticles(t);
  drawCoreGlow(t);

  // Rings — inner first during boot
  const rv = Math.min(1, state.ringReveal);
  const numRings = RINGS.length;
  for (let i = 0; i < numRings; i++) {
    const reverseI = numRings - 1 - i; // innermost reveals first
    const ringRv = Math.max(0, Math.min(1, rv * numRings - reverseI));
    drawRing(RINGS[i], ringRv, state.audioEnergy, t);
  }

  // Flower of life — appears early in the reveal
  const flowerRv = Math.max(0, Math.min(1, (rv - 0.08) / 0.25));
  drawFlowerOfLife(flowerRv, t);

  // Orbiting dots
  if (rv > 0.6) {
    drawOrbitingDots(t);
  }

  // Biometrics arc
  drawBioArc(t);

  // Pulse effects
  drawPulseWaves(t);

  requestAnimationFrame(render);
}

// ══════════════════════════════════════════════
//  BOOT SEQUENCE
// ══════════════════════════════════════════════
function startBootSequence() {
  const overlay = document.getElementById('boot-overlay');
  const logEl = document.getElementById('boot-log');
  const statusArea = document.getElementById('status-area');
  const footer = document.getElementById('hud-footer');
  const clock = document.getElementById('header-clock');

  // Boot log messages (staggered)
  const steps = [
    { text: '> Loading neural configuration…', delay: 200  },
    { text: '> Initializing wake-word detector…', delay: 700  },
    { text: '> Connecting to Gemini LLM…', delay: 1200 },
    { text: '> Voice biometrics calibrating…', delay: 1800 },
    { text: '> All systems nominal.', delay: 2500 },
  ];

  steps.forEach(s => {
    setTimeout(() => {
      const div = document.createElement('div');
      div.textContent = s.text;
      logEl.appendChild(div);
    }, s.delay);
  });

  // Orb build animation
  const BUILD_MS = 3200;
  const buildStart = performance.now();

  function animateBuild(now) {
    const elapsed = now - buildStart;
    const p = Math.min(1, elapsed / BUILD_MS);

    // Ease-out cubic for smooth deceleration
    state.ringReveal = 1 - Math.pow(1 - p, 3);
    state.orbOpacity = Math.min(1, p * 1.6);

    if (p < 1) {
      requestAnimationFrame(animateBuild);
    } else {
      // Build complete
      state.bootPhase = 'complete';
      setTimeout(() => {
        overlay.classList.add('hidden');
        statusArea.classList.remove('hidden');
        footer.classList.remove('hidden');
        if (clock) clock.classList.add('visible');

        // Notify Python
        if (typeof eel !== 'undefined') {
          eel.ui_ready();
        }
      }, 600);
    }
  }

  requestAnimationFrame(animateBuild);
}

// ══════════════════════════════════════════════
//  CLOCK
// ══════════════════════════════════════════════
function startClock() {
  const el = document.getElementById('header-clock');
  if (!el) return;
  function tick() {
    el.textContent = new Date().toLocaleTimeString('es-AR', { hour12: false });
  }
  tick();
  setInterval(tick, 1000);
}

// ══════════════════════════════════════════════
//  EEL-EXPOSED UI UPDATE FUNCTIONS
//  (Signatures preserved — backend contract intact)
// ══════════════════════════════════════════════
function updateStatus(text, color) {
  try {
    color = color || '#00ff00';
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');
    if (statusText) statusText.textContent = text;
    if (statusDot) {
      statusDot.style.background = color;
      statusDot.style.boxShadow = `0 0 10px ${color}`;
    }
    state.status = { text, color };

    // Visual pulse on the orb
    spawnPulse(color.replace('#', 'rgba(') === color
      ? `rgba(0, 255, 220, ALPHA)` // fallback if not hex
      : hexToRgbaPulse(color));
  } catch (e) {
    console.error('Error updating status:', e);
  }
}

function addChatMessage(sender, message) {
  // Chat removed — silent log to keep Eel contract
  console.log(`[CHAT] ${sender}: ${message}`);
}

function updateBiometrics(score, threshold) {
  try {
    state.bio.targetScore = score || 0;
    state.bio.threshold = threshold || 0.85;
  } catch (e) {
    console.error('Error updating biometrics:', e);
  }
}

function updateWaveform(dataArray) {
  try {
    if (!dataArray || dataArray.length === 0) return;
    if (state.audioData.length !== dataArray.length) {
      state.audioData = new Float32Array(dataArray.length).fill(128);
      state.smoothAudio = new Float32Array(dataArray.length).fill(128);
    }
    for (let i = 0; i < dataArray.length; i++) {
      state.audioData[i] = dataArray[i];
    }
  } catch (e) {
    console.error('Error updating waveform:', e);
  }
}

function updateFooter(key, value) {
  try {
    const el = document.getElementById(`footer-${key}`);
    if (el) el.textContent = value;
  } catch (e) {
    console.error('Error updating footer:', e);
  }
}

// ── Utility: hex color → rgba pulse string ──
function hexToRgbaPulse(hex) {
  const h = hex.replace('#', '');
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ALPHA)`;
}

// ── Eel Expose ──
if (typeof eel !== 'undefined') {
  eel.expose(updateStatus);
  eel.expose(addChatMessage);
  eel.expose(updateBiometrics);
  eel.expose(updateWaveform);
  eel.expose(updateFooter);
}

// ══════════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════════
window.addEventListener('DOMContentLoaded', () => {
  requestAnimationFrame(render);
  startBootSequence();
  startClock();
});
