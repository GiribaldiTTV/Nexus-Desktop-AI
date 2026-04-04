const body = document.body;
const backCanvas = document.getElementById("fx-back");
const frontCanvas = document.getElementById("fx-front");
const bctx = backCanvas.getContext("2d");
const fctx = frontCanvas.getContext("2d");
const commandOverlay = document.getElementById("command-overlay");
const commandHint = document.getElementById("command-hint");
const commandInputText = document.getElementById("command-input-text");
const commandStatus = document.getElementById("command-status");
const commandAmbiguous = document.getElementById("command-ambiguous");
const commandConfirmation = document.getElementById("command-confirmation");
const commandConfirmRequest = document.getElementById("command-confirm-request");
const commandConfirmTitle = document.getElementById("command-confirm-title");
const commandConfirmKind = document.getElementById("command-confirm-kind");
const commandConfirmTarget = document.getElementById("command-confirm-target");

let w = 0;
let h = 0;
let cx = 0;
let cy = 0;
let t = 0;

let currentState = "boot";
let ignition = 0.0;
let lastState = "boot";
let bootStartTime = null;

let voiceLevel = 0.0;
let smoothedVoiceLevel = 0.0;
let commandOverlayState = {
  visible: false,
  phase: "hidden",
  input_text: "",
  status_kind: "idle",
  status_text: "",
  typed_request: "",
  pending_action: null,
  ambiguous_titles: []
};

const backParticles = [];
const frontParticles = [];
const orbitersBack = [];
const orbitersFront = [];
const orbitTrails = [];
const spokes = [];
const swarms = [];
const filaments = [];
const blips = [];
const shellArcs = [];
const fogBands = [];
const relayBursts = [];

function resize() {
  w = backCanvas.width = frontCanvas.width = window.innerWidth;
  h = backCanvas.height = frontCanvas.height = window.innerHeight;
  cx = w * 0.5;
  cy = h * 0.5;
}
window.addEventListener("resize", resize);
resize();

function rand(min, max) {
  return Math.random() * (max - min) + min;
}

function lerp(a, b, m) {
  return a + (b - a) * m;
}

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function easeOutCubic(x) {
  x = clamp(x, 0, 1);
  return 1 - Math.pow(1 - x, 3);
}

function easeInOutCubic(x) {
  x = clamp(x, 0, 1);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
}

function stagedProgress(startMs, endMs) {
  if (currentState !== "boot" || bootStartTime === null) return 1.0;
  const elapsed = t - bootStartTime;
  return clamp((elapsed - startMs) / (endMs - startMs), 0, 1);
}

function bootStage(stage) {
  if (currentState !== "boot") return 1.0;

  switch (stage) {
    case "ambient":
      return easeOutCubic(stagedProgress(0, 900));
    case "spark":
      return easeOutCubic(stagedProgress(450, 1450));
    case "rings":
      return easeOutCubic(stagedProgress(1000, 2400));
    case "orbiters":
      return easeOutCubic(stagedProgress(1700, 3200));
    case "network":
      return easeOutCubic(stagedProgress(2400, 3900));
    case "stabilize":
      return easeInOutCubic(stagedProgress(3200, 4700));
    default:
      return 1.0;
  }
}

function effectiveVoiceLevel() {
  if (currentState !== "speaking") return 0.0;
  return smoothedVoiceLevel;
}

function speakingBoost(base = 1.0, multiplier = 1.0) {
  return base + effectiveVoiceLevel() * multiplier;
}

function pickProbeRole(isFront, satType) {
  if (satType !== "major") return null;

  const roles = isFront
    ? ["scanner", "ping", "beam", "blink"]
    : ["ping", "beam", "blink", "scanner"];

  return roles[Math.floor(rand(0, roles.length))];
}

function buildOrbiter(isFront, base, idx) {
  const band = idx % 4;
  const bandMin = [0.11, 0.15, 0.20, 0.24][band];
  const bandMax = [0.15, 0.20, 0.25, 0.31][band];

  const bandSpeedMin = [0.0011, 0.0016, 0.0022, 0.0028][band];
  const bandSpeedMax = [0.0022, 0.0032, 0.0044, 0.0056][band];

  const satType = Math.random() > 0.78 ? "major" : "minor";
  const probeRole = pickProbeRole(isFront, satType);

  return {
    angle: rand(0, Math.PI * 2),
    radius: rand(base * bandMin, base * bandMax),
    speed: rand(bandSpeedMin, bandSpeedMax) * (Math.random() > 0.5 ? 1 : -1),
    size: isFront ? rand(1.0, 3.4) : rand(0.7, 2.7),
    alpha: isFront ? rand(0.24, 0.90) : rand(0.18, 0.72),
    wobble: rand(0.003, 0.012),
    wobblePhase: rand(0, 1000),
    ellipseX: rand(0.88, 1.18),
    ellipseY: rand(0.82, 1.16),
    tilt: rand(-0.35, 0.35),
    satType,
    escortCount: Math.random() > 0.72 ? Math.floor(rand(1, 3.99)) : 0,
    linkChance: rand(0.03, 0.18),
    pulsePhase: rand(0, 3000),

    probeRole,
    probePhase: rand(0, 4000),
    probeRate: rand(0.0007, 0.0022),
    pingRadius: rand(8, 22),
    scanArc: rand(0.18, 0.42),
    beamBias: rand(-0.35, 0.35)
  };
}

function buildSceneData() {
  backParticles.length = 0;
  frontParticles.length = 0;
  orbitersBack.length = 0;
  orbitersFront.length = 0;
  orbitTrails.length = 0;
  spokes.length = 0;
  swarms.length = 0;
  filaments.length = 0;
  blips.length = 0;
  shellArcs.length = 0;
  fogBands.length = 0;
  relayBursts.length = 0;

  const base = Math.min(w, h);

  for (let i = 0; i < 170; i++) {
    backParticles.push({
      angle: rand(0, Math.PI * 2),
      radius: rand(base * 0.10, base * 0.40),
      speed: rand(0.0005, 0.0028),
      size: rand(0.4, 1.7),
      alpha: rand(0.02, 0.24),
      phase: rand(0, 3000),
      drift: rand(-0.12, 0.12)
    });
  }

  for (let i = 0; i < 42; i++) {
    frontParticles.push({
      x: rand(0, w),
      y: rand(0, h),
      vx: rand(-0.02, 0.02),
      vy: rand(-0.02, 0.02),
      size: rand(0.7, 2.4),
      alpha: rand(0.03, 0.14),
      depth: rand(0.6, 1.2),
      phase: rand(0, 3000)
    });
  }

  for (let i = 0; i < 26; i++) {
    orbitersBack.push(buildOrbiter(false, base, i));
  }

  for (let i = 0; i < 20; i++) {
    orbitersFront.push(buildOrbiter(true, base, i));
  }

  for (let i = 0; i < 18; i++) {
    orbitTrails.push({
      angle: rand(0, Math.PI * 2),
      radius: rand(base * 0.13, base * 0.30),
      span: rand(0.08, 0.22),
      width: rand(0.5, 1.7),
      alpha: rand(0.02, 0.08),
      speed: rand(-0.00075, 0.00075),
      ellipseX: rand(0.90, 1.16),
      ellipseY: rand(0.86, 1.12),
      tilt: rand(-0.30, 0.30)
    });
  }

  for (let i = 0; i < 22; i++) {
    spokes.push({
      angle: rand(0, Math.PI * 2),
      length: rand(base * 0.05, base * 0.20),
      alpha: rand(0.025, 0.10),
      width: rand(0.4, 1.1),
      drift: rand(-0.0007, 0.0007)
    });
  }

  for (let i = 0; i < 5; i++) {
    swarms.push({
      baseAngle: rand(0, Math.PI * 2),
      spread: rand(0.22, 0.52),
      radiusMin: rand(base * 0.14, base * 0.18),
      radiusMax: rand(base * 0.22, base * 0.33),
      drift: rand(-0.0009, 0.0009),
      density: Math.floor(rand(14, 26)),
      phase: rand(0, 2000)
    });
  }

  for (let i = 0; i < 11; i++) {
    filaments.push({
      a1: rand(0, Math.PI * 2),
      a2: rand(0, Math.PI * 2),
      r1: rand(base * 0.08, base * 0.18),
      r2: rand(base * 0.14, base * 0.30),
      alpha: rand(0.025, 0.11),
      life: rand(0.2, 1.0),
      decay: rand(0.002, 0.007)
    });
  }

  for (let i = 0; i < 13; i++) {
    shellArcs.push({
      radius: rand(base * 0.16, base * 0.25),
      start: rand(0, Math.PI * 2),
      span: rand(0.18, 0.86),
      width: rand(0.5, 2.2),
      alpha: rand(0.03, 0.13),
      speed: rand(-0.0015, 0.0015),
      jitter: rand(0, 1000)
    });
  }

  for (let i = 0; i < 4; i++) {
    fogBands.push({
      angle: rand(0, Math.PI * 2),
      radius: rand(base * 0.18, base * 0.28),
      width: rand(base * 0.02, base * 0.06),
      alpha: rand(0.015, 0.05),
      speed: rand(-0.0005, 0.0005),
      phase: rand(0, 2000)
    });
  }
}
buildSceneData();
window.addEventListener("resize", buildSceneData);

function stateSpeedMultiplier() {
  let base;
  switch (currentState) {
    case "speaking": base = 1.45; break;
    case "processing": base = 2.0; break;
    case "dormant": base = 0.38; break;
    case "boot": base = 0.68; break;
    default: base = 1.0;
  }
  return base * speakingBoost(1.0, 0.30);
}

function stateParticleSpeedMultiplier() {
  let base;
  switch (currentState) {
    case "speaking": base = 1.45; break;
    case "processing": base = 2.2; break;
    case "dormant": base = 0.45; break;
    case "boot": base = 0.70; break;
    default: base = 1.0;
  }
  return base * speakingBoost(1.0, 0.22);
}

function stateEnergyMultiplier() {
  let base;
  switch (currentState) {
    case "speaking": base = 1.25; break;
    case "processing": base = 1.65; break;
    case "dormant": base = 0.52; break;
    case "boot": base = ignition; break;
    default: base = 1.0;
  }
  return base * speakingBoost(1.0, 0.55);
}

function bootIntensity() {
  if (currentState !== "boot") return 1.0;
  ignition = Math.min(1, ignition + 0.0036);
  return ignition;
}

function clear() {
  bctx.clearRect(0, 0, w, h);
  fctx.clearRect(0, 0, w, h);
}

function drawBackgroundNoise() {
  const baseCount = currentState === "processing" ? 58 : 32;
  const count = Math.floor(baseCount * bootStage("ambient"));
  for (let i = 0; i < count; i++) {
    const x = rand(0, w);
    const y = rand(0, h);
    const a = rand(0.008, 0.045) * bootStage("ambient") * speakingBoost(1.0, 0.30);
    bctx.fillStyle = `rgba(110,220,255,${a})`;
    bctx.fillRect(x, y, 1, 1);
  }
}

function drawBackParticles() {
  const intensity = bootIntensity() * bootStage("ambient") * speakingBoost(1.0, 0.38);

  backParticles.forEach((p, idx) => {
    p.angle += p.speed * stateParticleSpeedMultiplier();
    const radialDrift = Math.sin(t * 0.0008 + p.phase) * (2.0 + p.drift * 5.0 + effectiveVoiceLevel() * 2.2);
    const x = cx + Math.cos(p.angle + p.phase * 0.0006) * (p.radius + radialDrift);
    const y = cy + Math.sin(p.angle + p.phase * 0.0005) * (p.radius - radialDrift * 0.7);

    const flicker = 0.35 + 0.65 * Math.sin(t * 0.0018 + p.phase + idx);

    bctx.beginPath();
    bctx.arc(x, y, p.size, 0, Math.PI * 2);
    bctx.fillStyle = `rgba(110,230,255,${p.alpha * flicker * intensity})`;
    bctx.shadowBlur = 8 + effectiveVoiceLevel() * 5;
    bctx.shadowColor = "rgba(100,220,255,0.16)";
    bctx.fill();
  });

  bctx.shadowBlur = 0;
}

function drawFrontParticles() {
  const energy = stateEnergyMultiplier() * bootStage("orbiters");

  frontParticles.forEach((p, i) => {
    p.x += p.vx * p.depth * energy;
    p.y += p.vy * p.depth * energy;

    if (p.x < -20) p.x = w + 20;
    if (p.x > w + 20) p.x = -20;
    if (p.y < -20) p.y = h + 20;
    if (p.y > h + 20) p.y = -20;

    const flicker = 0.45 + 0.55 * Math.sin(t * 0.001 + p.phase + i);

    fctx.beginPath();
    fctx.arc(p.x, p.y, p.size * speakingBoost(1.0, 0.22), 0, Math.PI * 2);
    fctx.fillStyle = `rgba(160,240,255,${p.alpha * flicker * speakingBoost(1.0, 0.45)})`;
    fctx.shadowBlur = 6 + effectiveVoiceLevel() * 4;
    fctx.shadowColor = "rgba(130,230,255,0.12)";
    fctx.fill();
  });

  fctx.shadowBlur = 0;
}

function drawAtmosphericBands() {
  const intensity = bootIntensity() * bootStage("ambient") * speakingBoost(1.0, 0.28);

  fogBands.forEach((band) => {
    band.angle += band.speed * stateSpeedMultiplier();
    const x = cx + Math.cos(band.angle) * band.radius;
    const y = cy + Math.sin(band.angle) * band.radius;
    const alpha = band.alpha * (0.6 + 0.4 * Math.sin(t * 0.001 + band.phase)) * intensity;

    bctx.beginPath();
    bctx.arc(x, y, band.width * speakingBoost(1.0, 0.18), 0, Math.PI * 2);
    bctx.fillStyle = `rgba(100,220,255,${alpha})`;
    bctx.shadowBlur = 20 + effectiveVoiceLevel() * 7;
    bctx.shadowColor = "rgba(80,190,255,0.10)";
    bctx.fill();
  });

  bctx.shadowBlur = 0;
}

function drawSpokes() {
  const intensity = bootIntensity() * bootStage("rings") * speakingBoost(1.0, 0.25);
  bctx.save();
  bctx.translate(cx, cy);

  spokes.forEach((s, idx) => {
    s.angle += s.drift * stateSpeedMultiplier();
    const a = s.angle + Math.sin(t * 0.00045 + idx * 1.7) * (0.18 + effectiveVoiceLevel() * 0.06);
    const r1 = Math.min(w, h) * 0.045;
    const r2 = r1 + s.length + effectiveVoiceLevel() * 4.0;

    bctx.beginPath();
    bctx.moveTo(Math.cos(a) * r1, Math.sin(a) * r1);
    bctx.lineTo(Math.cos(a) * r2, Math.sin(a) * r2);
    bctx.lineWidth = s.width * speakingBoost(1.0, 0.10);
    bctx.strokeStyle = `rgba(90,220,255,${s.alpha * intensity})`;
    bctx.stroke();
  });

  bctx.restore();
}

function drawArcBand(radius, rotation, count, spanDeg, alpha, width, blur, irregularity = 0.0) {
  bctx.save();
  bctx.translate(cx, cy);
  bctx.rotate(rotation);
  bctx.lineCap = "round";
  bctx.lineWidth = width * speakingBoost(1.0, 0.08);
  bctx.shadowBlur = blur + effectiveVoiceLevel() * 7;
  bctx.shadowColor = "rgba(80,210,255,0.18)";

  for (let i = 0; i < count; i++) {
    const start = (Math.PI * 2 / count) * i + Math.sin(t * 0.0011 + i * 1.3) * (irregularity + effectiveVoiceLevel() * 0.02);
    const end = start + (Math.PI / 180) * (spanDeg + Math.sin(t * 0.0014 + i) * (3.5 + effectiveVoiceLevel() * 4.0));

    bctx.beginPath();
    bctx.strokeStyle = `rgba(100,230,255,${alpha * speakingBoost(1.0, 0.45)})`;
    bctx.arc(0, 0, radius * speakingBoost(1.0, 0.02), start, end);
    bctx.stroke();
  }

  bctx.restore();
  bctx.shadowBlur = 0;
}

function drawBrokenShells() {
  const intensity = bootIntensity() * bootStage("rings") * speakingBoost(1.0, 0.35);

  shellArcs.forEach((arc, idx) => {
    arc.start += arc.speed * stateSpeedMultiplier();
    const pulse = 0.5 + 0.5 * Math.sin(t * 0.0011 + arc.jitter);

    bctx.beginPath();
    bctx.arc(
      cx,
      cy,
      arc.radius + Math.sin(t * 0.0007 + idx) * (2.2 + effectiveVoiceLevel() * 2.8),
      arc.start,
      arc.start + arc.span + pulse * 0.12
    );
    bctx.lineWidth = arc.width * speakingBoost(1.0, 0.10);
    bctx.strokeStyle = `rgba(120,235,255,${arc.alpha * pulse * intensity})`;
    bctx.shadowBlur = 12 + effectiveVoiceLevel() * 6;
    bctx.shadowColor = "rgba(100,220,255,0.14)";
    bctx.stroke();
  });

  bctx.shadowBlur = 0;
}

function drawOrbitTrails() {
  const intensity = bootIntensity() * bootStage("orbiters") * speakingBoost(1.0, 0.42);

  orbitTrails.forEach((trail) => {
    trail.angle += trail.speed * stateSpeedMultiplier();

    bctx.save();
    bctx.translate(cx, cy);
    bctx.rotate(trail.tilt);

    const segments = 8;
    for (let s = 0; s < segments; s++) {
      const localStart = trail.angle + s * 0.08;
      const localEnd = localStart + trail.span * (1 - s / segments);

      bctx.beginPath();
      for (let a = localStart; a <= localEnd; a += 0.04) {
        const x = Math.cos(a) * trail.radius * trail.ellipseX;
        const y = Math.sin(a) * trail.radius * trail.ellipseY;
        if (a === localStart) bctx.moveTo(x, y);
        else bctx.lineTo(x, y);
      }
      bctx.lineWidth = trail.width * (1 - s / (segments + 2)) * speakingBoost(1.0, 0.12);
      bctx.strokeStyle = `rgba(120,235,255,${trail.alpha * (1 - s / segments) * intensity})`;
      bctx.stroke();
    }

    bctx.restore();
  });
}

function orbiterPosition(o) {
  const localRadius = o.radius + Math.sin(t * o.wobble + o.wobblePhase) * (6.5 + effectiveVoiceLevel() * 4.0);
  const rawX = Math.cos(o.angle) * localRadius * o.ellipseX;
  const rawY = Math.sin(o.angle) * localRadius * o.ellipseY;

  const cosT = Math.cos(o.tilt);
  const sinT = Math.sin(o.tilt);

  return {
    x: cx + rawX * cosT - rawY * sinT,
    y: cy + rawX * sinT + rawY * cosT
  };
}

function spawnRelayBurst(x1, y1, x2, y2, alpha) {
  if (relayBursts.length > 14) return;
  relayBursts.push({
    x1, y1, x2, y2,
    life: 1.0,
    alpha,
    speed: rand(0.0015, 0.003)
  });
}

function drawProbeSatellite(ctx, o, pos, r, front, intensity) {
  if (!o.probeRole) return;

  const energy = stateEnergyMultiplier();
  const phase = t * o.probeRate + o.probePhase;
  const probeAlpha = intensity * (0.35 + 0.65 * Math.abs(Math.sin(phase))) * speakingBoost(1.0, 0.55);

  if (o.probeRole === "scanner") {
    const angle = o.angle + o.beamBias + Math.sin(phase * 0.7) * 0.18;
    const coneLen = r * (8.0 + effectiveVoiceLevel() * 3.5);

    ctx.save();
    ctx.translate(pos.x, pos.y);
    ctx.rotate(angle);

    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, coneLen, -o.scanArc, o.scanArc);
    ctx.closePath();
    ctx.fillStyle = `rgba(150,240,255,${0.08 * probeAlpha * energy})`;
    ctx.filter = "blur(2px)";
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(coneLen, 0);
    ctx.lineWidth = 0.7 + effectiveVoiceLevel() * 0.35;
    ctx.strokeStyle = `rgba(180,245,255,${0.12 * probeAlpha})`;
    ctx.stroke();

    ctx.restore();
    ctx.filter = "none";
  }

  if (o.probeRole === "ping") {
    const pingProgress = (Math.sin(phase) + 1) * 0.5;
    const pr = r * (1.8 + pingProgress * (4.5 + effectiveVoiceLevel() * 2.2));

    ctx.beginPath();
    ctx.arc(pos.x, pos.y, pr, 0, Math.PI * 2);
    ctx.lineWidth = 0.9 + effectiveVoiceLevel() * 0.25;
    ctx.strokeStyle = `rgba(160,240,255,${0.12 * (1 - pingProgress) * probeAlpha})`;
    ctx.stroke();
  }

  if (o.probeRole === "beam") {
    const toCoreX = cx - pos.x;
    const toCoreY = cy - pos.y;
    const len = Math.hypot(toCoreX, toCoreY);
    if (len > 0) {
      const nx = toCoreX / len;
      const ny = toCoreY / len;
      const beamLen = Math.min(len * (0.55 + effectiveVoiceLevel() * 0.12), r * 18);

      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
      ctx.lineTo(pos.x + nx * beamLen, pos.y + ny * beamLen);
      ctx.lineWidth = (front ? 0.9 : 0.7) + effectiveVoiceLevel() * 0.25;
      ctx.strokeStyle = `rgba(160,240,255,${0.10 * probeAlpha})`;
      ctx.shadowBlur = 10 + effectiveVoiceLevel() * 8;
      ctx.shadowColor = "rgba(120,220,255,0.18)";
      ctx.stroke();
      ctx.shadowBlur = 0;
    }
  }

  if (o.probeRole === "blink") {
    const blink = Math.pow((Math.sin(phase * 2.2) + 1) * 0.5, 3);

    ctx.beginPath();
    ctx.arc(pos.x, pos.y, r * (1.15 + blink * (0.55 + effectiveVoiceLevel() * 0.35)), 0, Math.PI * 2);
    ctx.fillStyle = `rgba(220,250,255,${0.22 * blink * probeAlpha})`;
    ctx.shadowBlur = 14 + effectiveVoiceLevel() * 8;
    ctx.shadowColor = "rgba(180,245,255,0.30)";
    ctx.fill();
    ctx.shadowBlur = 0;
  }
}

function drawOrbiterSet(ctx, set, front = false) {
  const intensity = bootIntensity() * bootStage("orbiters") * speakingBoost(1.0, 0.48);
  const energy = stateEnergyMultiplier() * bootStage("network") * speakingBoost(1.0, 0.40);
  const positions = [];

  set.forEach((o, idx) => {
    o.angle += o.speed * stateSpeedMultiplier();
    const pos = orbiterPosition(o);
    positions.push(pos);

    const pulse = 0.55 + 0.45 * Math.sin(t * 0.002 + o.pulsePhase);
    const r = o.size * (o.satType === "major" ? 1.35 : 1.0) * speakingBoost(1.0, 0.08);

    drawProbeSatellite(ctx, o, pos, r, front, intensity);

    ctx.beginPath();
    ctx.arc(pos.x, pos.y, r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(175,242,255,${o.alpha * pulse * intensity})`;
    ctx.shadowBlur = (front ? 18 : 14) + effectiveVoiceLevel() * 8;
    ctx.shadowColor = front ? "rgba(120,230,255,0.55)" : "rgba(100,220,255,0.38)";
    ctx.fill();

    if (o.satType === "major") {
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, r * (2.3 + effectiveVoiceLevel() * 0.18), 0, Math.PI * 2);
      ctx.lineWidth = 0.8 + effectiveVoiceLevel() * 0.12;
      ctx.strokeStyle = `rgba(140,235,255,${0.12 * pulse * intensity})`;
      ctx.stroke();
    }

    for (let e = 0; e < o.escortCount; e++) {
      const ea = o.angle + (e + 1) * 0.22 + Math.sin(t * 0.0011 + idx + e) * (0.03 + effectiveVoiceLevel() * 0.02);
      const er = r * (2.2 + e * 0.75 + effectiveVoiceLevel() * 0.4);
      const ex = pos.x + Math.cos(ea) * er;
      const ey = pos.y + Math.sin(ea) * er;

      ctx.beginPath();
      ctx.arc(ex, ey, Math.max(0.65, r * 0.28) * speakingBoost(1.0, 0.10), 0, Math.PI * 2);
      ctx.fillStyle = `rgba(150,235,255,${0.28 * pulse * intensity})`;
      ctx.shadowBlur = 8 + effectiveVoiceLevel() * 6;
      ctx.shadowColor = "rgba(120,230,255,0.20)";
      ctx.fill();

      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
      ctx.lineTo(ex, ey);
      ctx.lineWidth = 0.5 + effectiveVoiceLevel() * 0.08;
      ctx.strokeStyle = `rgba(120,230,255,${0.06 * intensity})`;
      ctx.stroke();
    }

    if (Math.random() < o.linkChance * energy) {
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(pos.x, pos.y);
      ctx.lineWidth = (front ? 0.55 : 0.4) + effectiveVoiceLevel() * 0.08;
      ctx.strokeStyle = `rgba(100,220,255,${0.05 * intensity})`;
      ctx.stroke();
    }
  });

  for (let i = 0; i < positions.length; i++) {
    if (Math.random() > 0.035 * energy) continue;
    const j = Math.floor(rand(0, positions.length));
    if (i === j) continue;
    const p1 = positions[i];
    const p2 = positions[j];
    const alpha = front ? 0.14 : 0.09;

    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.lineWidth = 0.55 + effectiveVoiceLevel() * 0.12;
    ctx.strokeStyle = `rgba(130,235,255,${alpha * intensity * bootStage("network") * speakingBoost(1.0, 0.55)})`;
    ctx.shadowBlur = 10 + effectiveVoiceLevel() * 6;
    ctx.shadowColor = "rgba(120,225,255,0.14)";
    ctx.stroke();

    if (Math.random() > 0.6 && bootStage("network") > 0.15) {
      spawnRelayBurst(p1.x, p1.y, p2.x, p2.y, alpha * bootStage("network") * speakingBoost(1.0, 0.65));
    }
  }

  ctx.shadowBlur = 0;
}

function drawRelayBursts() {
  const gate = bootStage("network") * speakingBoost(1.0, 0.70);

  for (let i = relayBursts.length - 1; i >= 0; i--) {
    const r = relayBursts[i];
    r.life -= r.speed * Math.max(0.5, gate);

    if (r.life <= 0) {
      relayBursts.splice(i, 1);
      continue;
    }

    const progress = Math.pow(1 - r.life, 1.6);
    const px = lerp(r.x1, r.x2, progress);
    const py = lerp(r.y1, r.y2, progress);

    fctx.beginPath();
    fctx.arc(px, py, 2.1 + effectiveVoiceLevel() * 0.9, 0, Math.PI * 2);
    fctx.fillStyle = `rgba(200,248,255,${r.alpha * r.life * gate})`;
    fctx.shadowBlur = 12 + effectiveVoiceLevel() * 10;
    fctx.shadowColor = "rgba(150,240,255,0.35)";
    fctx.fill();
  }
  fctx.shadowBlur = 0;
}

function drawSwarms() {
  const energy = stateEnergyMultiplier() * bootStage("rings");
  const intensity = bootIntensity() * bootStage("rings") * speakingBoost(1.0, 0.35);

  swarms.forEach((swarm, si) => {
    swarm.baseAngle += swarm.drift * stateSpeedMultiplier();

    for (let i = 0; i < swarm.density; i++) {
      const local = i / swarm.density;
      const angle =
        swarm.baseAngle +
        (local - 0.5) * swarm.spread +
        Math.sin(t * 0.0013 + swarm.phase + i) * 0.04;

      const r = lerp(swarm.radiusMin, swarm.radiusMax, local) +
        Math.sin(t * 0.001 + i + si * 10) * (4.0 + effectiveVoiceLevel() * 2.0);

      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;

      const alpha = (0.05 + local * 0.13) * intensity * energy;
      const size = (0.5 + local * 1.6) * speakingBoost(1.0, 0.08);

      bctx.beginPath();
      bctx.arc(x, y, size, 0, Math.PI * 2);
      bctx.fillStyle = `rgba(140,238,255,${alpha})`;
      bctx.shadowBlur = 9 + effectiveVoiceLevel() * 6;
      bctx.shadowColor = "rgba(110,225,255,0.18)";
      bctx.fill();
    }
  });

  bctx.shadowBlur = 0;
}

function refreshFilaments() {
  for (let i = 0; i < filaments.length; i++) {
    const f = filaments[i];
    f.life -= f.decay * (currentState === "processing" ? 2.0 : 1.0);

    if (f.life <= 0) {
      const base = Math.min(w, h);
      filaments[i] = {
        a1: rand(0, Math.PI * 2),
        a2: rand(0, Math.PI * 2),
        r1: rand(base * 0.08, base * 0.18),
        r2: rand(base * 0.14, base * 0.30),
        alpha: rand(0.025, 0.11),
        life: rand(0.4, 1.0),
        decay: rand(0.002, 0.007)
      };
    }
  }
}

function drawFilaments() {
  const stage = bootStage("rings");
  refreshFilaments();
  const intensity = bootIntensity() * stage * speakingBoost(1.0, 0.42);

  filaments.forEach((f, idx) => {
    const a1 = f.a1 + Math.sin(t * 0.0008 + idx) * 0.12;
    const a2 = f.a2 + Math.cos(t * 0.0010 + idx * 1.2) * 0.15;

    const x1 = cx + Math.cos(a1) * f.r1;
    const y1 = cy + Math.sin(a1) * f.r1;
    const x2 = cx + Math.cos(a2) * f.r2;
    const y2 = cy + Math.sin(a2) * f.r2;

    const mx = (x1 + x2) * 0.5 + Math.sin(t * 0.0015 + idx) * (8 + effectiveVoiceLevel() * 4);
    const my = (y1 + y2) * 0.5 + Math.cos(t * 0.0012 + idx) * (8 + effectiveVoiceLevel() * 4);

    bctx.beginPath();
    bctx.moveTo(x1, y1);
    bctx.quadraticCurveTo(mx, my, x2, y2);
    bctx.lineWidth = 0.8 + effectiveVoiceLevel() * 0.22;
    bctx.strokeStyle = `rgba(120,235,255,${f.alpha * f.life * intensity})`;
    bctx.shadowBlur = 10 + effectiveVoiceLevel() * 8;
    bctx.shadowColor = "rgba(100,220,255,0.14)";
    bctx.stroke();
  });

  bctx.shadowBlur = 0;
}

function spawnBlip() {
  if (bootStage("network") < 0.25 && currentState === "boot") return;

  const chance =
    currentState === "processing" ? 0.21 :
    currentState === "speaking" ? 0.11 + effectiveVoiceLevel() * 0.08 :
    currentState === "boot" ? 0.05 :
    0.04;

  if (Math.random() > chance) return;

  const r = rand(Math.min(w, h) * 0.11, Math.min(w, h) * 0.31);
  const a = rand(0, Math.PI * 2);

  blips.push({
    x: cx + Math.cos(a) * r,
    y: cy + Math.sin(a) * r,
    life: 1.0,
    size: rand(1.0, 2.8)
  });
}

function drawBlips() {
  const gate = currentState === "boot" ? bootStage("network") : 1.0;
  spawnBlip();

  for (let i = blips.length - 1; i >= 0; i--) {
    const b = blips[i];
    b.life -= currentState === "processing" ? 0.045 : 0.026;

    if (b.life <= 0) {
      blips.splice(i, 1);
      continue;
    }

    fctx.beginPath();
    fctx.arc(b.x, b.y, b.size * speakingBoost(1.0, 0.15), 0, Math.PI * 2);
    fctx.fillStyle = `rgba(185,245,255,${b.life * gate * speakingBoost(1.0, 0.42)})`;
    fctx.shadowBlur = 20 + effectiveVoiceLevel() * 8;
    fctx.shadowColor = "rgba(120,230,255,0.78)";
    fctx.fill();

    fctx.beginPath();
    fctx.moveTo(b.x - 7, b.y);
    fctx.lineTo(b.x + 7, b.y);
    fctx.moveTo(b.x, b.y - 7);
    fctx.lineTo(b.x, b.y + 7);
    fctx.strokeStyle = `rgba(120,230,255,${0.18 * b.life * gate * speakingBoost(1.0, 0.45)})`;
    fctx.lineWidth = 1 + effectiveVoiceLevel() * 0.15;
    fctx.stroke();
  }

  fctx.shadowBlur = 0;
}

function drawOrganicSpeechCore(ctx, x, y, baseRadius, voice, spark, intensity) {
  const points = 72;

  // reduced deformation so the shape stays controlled
  const deform = 0.05 + voice * 0.16;

  // cleaner, lower-frequency motion
  const lobeA = 2.4 + voice * 1.2;
  const lobeB = 3.6 + voice * 1.6;
  const lobeC = 5.2 + voice * 2.0;

  ctx.beginPath();

  for (let i = 0; i <= points; i++) {
    const a = (i / points) * Math.PI * 2;

    const wave1 = Math.sin(a * lobeA + t * 0.006) * deform;
    const wave2 = Math.sin(a * lobeB - t * 0.004 + 1.2) * deform * 0.45;
    const wave3 = Math.sin(a * lobeC + t * 0.008 + 2.1) * deform * 0.25;

    const frontBias =
      Math.max(0, Math.cos(a - Math.sin(t * 0.002) * 0.22)) *
      voice * 0.13;

    const radius = baseRadius * (1 + wave1 + wave2 + wave3 + frontBias);

    const px = x + Math.cos(a) * radius;
    const py = y + Math.sin(a) * radius;

    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }

  ctx.closePath();
  ctx.fillStyle = `rgba(140,235,255,${0.050 * intensity * speakingBoost(1.0, 1.03)})`;
  ctx.shadowBlur = 18 + voice * 20;
  ctx.shadowColor = "rgba(100,220,255,0.38)";
  ctx.fill();

  // calmer inner shell
  ctx.beginPath();
  for (let i = 0; i <= points; i++) {
    const a = (i / points) * Math.PI * 2;

    const wave1 =
      Math.sin(a * (lobeA + 0.8) - t * 0.007 + 0.8) *
      deform * 0.5;

    const wave2 =
      Math.sin(a * (lobeB + 1.5) + t * 0.005 + 2.0) *
      deform * 0.22;

    const radius = baseRadius * 0.72 * (1 + wave1 + wave2);

    const px = x + Math.cos(a) * radius;
    const py = y + Math.sin(a) * radius;

    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }

  ctx.closePath();
  ctx.fillStyle = `rgba(170,242,255,${0.03 + voice * 0.07})`;
  ctx.shadowBlur = 12 + voice * 14;
  ctx.shadowColor = "rgba(130,225,255,0.30)";
  ctx.fill();

  ctx.shadowBlur = 0;
}

function drawCoreSheen() {
  const base = Math.min(w, h);
  const intensity = bootIntensity();
  const energy = stateEnergyMultiplier();

  const spark = bootStage("spark");
  const voice = effectiveVoiceLevel();

  const ox = Math.sin(t * 0.0012) * 4.5 * spark * speakingBoost(1.0, 0.45);
  const oy = Math.cos(t * 0.0009) * 3.8 * spark * speakingBoost(1.0, 0.45);

  const outerRadius =
    base * (0.018 + 0.042 * spark) *
    (1.0 + voice * 0.42);

  if (voice > 0.04 && currentState === "speaking") {
    drawOrganicSpeechCore(
      bctx,
      cx + ox,
      cy + oy,
      outerRadius,
      voice,
      spark,
      intensity * energy * spark
    );
  } else {
    bctx.beginPath();
    bctx.arc(cx + ox, cy + oy, outerRadius, 0, Math.PI * 2);
    bctx.fillStyle = `rgba(140,235,255,${0.05 * intensity * energy * spark * speakingBoost(1.0, 0.95)})`;
    bctx.shadowBlur = 48 * spark + voice * 34;
    bctx.shadowColor = "rgba(100,220,255,0.34)";
    bctx.fill();
    bctx.shadowBlur = 0;
  }

  const innerRadius =
    base * (0.006 + 0.012 * spark) *
    (1.0 + voice * 0.78);

  fctx.beginPath();
  fctx.arc(cx + ox * 0.45, cy + oy * 0.45, innerRadius, 0, Math.PI * 2);
  fctx.fillStyle = `rgba(235,250,255,${0.82 * intensity * spark * speakingBoost(1.0, 1.05)})`;
  fctx.shadowBlur = 26 * spark + voice * 30;
  fctx.shadowColor = "rgba(180,245,255,0.92)";
  fctx.fill();

  if (voice > 0.08) {
    const bloomRadius =
      base * (0.012 + 0.020 * spark) *
      (1.0 + voice * 0.95);

    fctx.beginPath();
    fctx.arc(cx, cy, bloomRadius, 0, Math.PI * 2);
    fctx.fillStyle = `rgba(170,240,255,${0.05 + voice * 0.14})`;
    fctx.shadowBlur = 24 + voice * 30;
    fctx.shadowColor = "rgba(130,225,255,0.40)";
    fctx.fill();
  }

  bctx.shadowBlur = 0;
  fctx.shadowBlur = 0;
}

function drawArrivalPulse() {
  if (currentState !== "boot") return;

  const base = Math.min(w, h);
  const e = bootStage("spark");
  const ringR = lerp(base * 0.02, base * 0.21, e);

  fctx.beginPath();
  fctx.arc(cx, cy, ringR, 0, Math.PI * 2);
  fctx.lineWidth = 2.0;
  fctx.strokeStyle = `rgba(180,245,255,${0.32 * (1 - e)})`;
  fctx.shadowBlur = 20 * e;
  fctx.shadowColor = "rgba(130,235,255,0.28)";
  fctx.stroke();
  fctx.shadowBlur = 0;
}

function drawAnimatedRings() {
  const base = Math.min(w, h);
  const s = stateSpeedMultiplier();
  const intensity = bootIntensity() * bootStage("rings");

  drawArcBand(base * 0.122, t * 0.00028 * s, 7, 15, 0.09 * intensity, 1.9, 12, 0.12);
  drawArcBand(base * 0.152, -t * 0.00019 * s, 9, 11, 0.07 * intensity, 1.4, 10, 0.15);
  drawArcBand(base * 0.186, t * 0.00014 * s, 11, 8, 0.055 * intensity, 1.1, 8, 0.18);
}

function drawForegroundSweep() {
  const energy = stateEnergyMultiplier() * bootStage("network") * speakingBoost(1.0, 0.70);
  const r = Math.min(w, h) * 0.23;
  const a = t * 0.00028 * stateSpeedMultiplier();

  fctx.save();
  fctx.translate(cx, cy);
  fctx.rotate(a);
  fctx.beginPath();
  fctx.moveTo(0, 0);
  fctx.arc(0, 0, r * speakingBoost(1.0, 0.03), -0.10, 0.12 + effectiveVoiceLevel() * 0.06);
  fctx.closePath();
  fctx.fillStyle = `rgba(130,235,255,${0.035 * energy})`;
  fctx.filter = "blur(4px)";
  fctx.fill();
  fctx.restore();
  fctx.filter = "none";
}

function renderCommandOverlay() {
  if (!commandOverlay) return;

  const state = commandOverlayState || {};
  const isVisible = Boolean(state.visible);
  commandOverlay.classList.toggle("visible", isVisible);
  commandOverlay.setAttribute("aria-hidden", isVisible ? "false" : "true");

  if (!isVisible) {
    return;
  }

  if (commandInputText) {
    commandInputText.textContent = state.input_text || "";
  }

  if (commandStatus) {
    commandStatus.className = "command-status";
    if (state.status_kind && state.status_kind !== "idle") {
      commandStatus.classList.add(`status-${state.status_kind}`);
    }
    commandStatus.textContent = state.status_text || "";
  }

  if (commandAmbiguous) {
    const titles = Array.isArray(state.ambiguous_titles) ? state.ambiguous_titles : [];
    commandAmbiguous.textContent =
      titles.length > 0 ? `Matches: ${titles.join(" • ")}` : "";
  }

  if (commandHint) {
    commandHint.textContent =
      state.phase === "confirm"
        ? "Review the resolved action before execution."
        : state.phase === "result"
        ? "Returning to passive desktop mode."
        : "Type a saved action or alias, then press Enter.";
  }

  const action = state.pending_action || null;
  const showConfirm = state.phase === "confirm" && action;
  if (commandConfirmation) {
    commandConfirmation.hidden = !showConfirm;
  }

  if (showConfirm) {
    if (commandConfirmRequest) {
      commandConfirmRequest.textContent = state.typed_request || "";
    }
    if (commandConfirmTitle) {
      commandConfirmTitle.textContent = action.title || "";
    }
    if (commandConfirmKind) {
      commandConfirmKind.textContent = action.target_kind || "";
    }
    if (commandConfirmTarget) {
      commandConfirmTarget.textContent = action.target || "";
    }
  }
}

function frame(ts) {
  t = ts;
  if (currentState === "boot" && bootStartTime === null) bootStartTime = t;

if (voiceLevel > smoothedVoiceLevel) {
  smoothedVoiceLevel = lerp(smoothedVoiceLevel, voiceLevel, 0.42);
} else {
  smoothedVoiceLevel = lerp(smoothedVoiceLevel, voiceLevel, 0.16);
}

  clear();
  drawBackgroundNoise();
  drawAtmosphericBands();
  drawBackParticles();
  drawSpokes();
  drawBrokenShells();
  drawOrbitTrails();
  drawAnimatedRings();
  drawSwarms();
  drawFilaments();
  drawOrbiterSet(bctx, orbitersBack, false);
  drawCoreSheen();
  drawArrivalPulse();
  drawFrontParticles();
  drawOrbiterSet(fctx, orbitersFront, true);
  drawRelayBursts();
  drawBlips();
  drawForegroundSweep();
  requestAnimationFrame(frame);
}

window.setJarvisState = function (stateName) {
  lastState = currentState;
  currentState = stateName || "idle";

  if (currentState === "boot") {
    ignition = 0.0;
    bootStartTime = null;
  } else if (lastState === "boot") {
    ignition = 1.0;
  } else if (currentState !== "boot") {
    ignition = 1.0;
  }

  body.classList.remove(
    "state-boot",
    "state-idle",
    "state-speaking",
    "state-processing",
    "state-dormant"
  );
  body.classList.add(`state-${currentState}`);
};

window.setJarvisVoiceLevel = function(level) {
  voiceLevel = clamp(Number(level) || 0, 0, 1);
};

window.setCommandOverlayState = function(state) {
  commandOverlayState = Object.assign({}, commandOverlayState, state || {});
  renderCommandOverlay();
};

window.setJarvisState("boot");
window.setJarvisVoiceLevel(0);
window.setCommandOverlayState({ visible: false });
requestAnimationFrame(frame);
