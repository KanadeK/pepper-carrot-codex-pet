const atlasUrl = "assets/spritesheet.webp";
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const canvases = [...document.querySelectorAll("[data-pet-canvas]")];
const statusElement = document.querySelector("[data-preview-status]");
const controlsElement = document.querySelector("[data-state-controls]");
const stateNameElement = document.querySelector("[data-state-name]");
const frameReadoutElement = document.querySelector("[data-frame-readout]");
const copyButton = document.querySelector("[data-copy-command]");
const copyFeedback = document.querySelector("[data-copy-feedback]");

let configuration;
let atlas;
let activeState;
let animationFrame;
let frameIndex = 0;
let lastFrameAt = 0;

function sourceCell(state, index) {
  if (state.rows) {
    const rowOffset = Math.floor(index / configuration.atlas.columns);
    return {
      column: index % configuration.atlas.columns,
      row: state.rows[rowOffset],
    };
  }
  return {column: index, row: state.row};
}

function drawFrame(index) {
  const cell = sourceCell(activeState, index);
  for (const canvas of canvases) {
    const context = canvas.getContext("2d", {alpha: true});
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = "high";
    context.drawImage(
      atlas,
      cell.column * configuration.cell.width,
      cell.row * configuration.cell.height,
      configuration.cell.width,
      configuration.cell.height,
      0,
      0,
      canvas.width,
      canvas.height,
    );
    canvas.setAttribute(
      "aria-label",
      `Pepper ${activeState.label.toLowerCase()} animation, frame ${index + 1}`,
    );
  }
  if (stateNameElement) {
    stateNameElement.textContent = activeState.label;
  }
  if (frameReadoutElement) {
    frameReadoutElement.textContent = `Frame ${index + 1} of ${activeState.frames}`;
  }
}

function animate(timestamp) {
  if (!atlas || !activeState) {
    return;
  }
  if (reducedMotion.matches || document.hidden) {
    frameIndex = 0;
    drawFrame(frameIndex);
    animationFrame = undefined;
    return;
  }
  const interval = 1000 / activeState.fps;
  if (timestamp - lastFrameAt >= interval) {
    frameIndex = (frameIndex + 1) % activeState.frames;
    lastFrameAt = timestamp;
    drawFrame(frameIndex);
  }
  animationFrame = requestAnimationFrame(animate);
}

function startAnimation() {
  if (animationFrame !== undefined) {
    cancelAnimationFrame(animationFrame);
  }
  lastFrameAt = 0;
  drawFrame(frameIndex);
  if (!reducedMotion.matches && !document.hidden) {
    animationFrame = requestAnimationFrame(animate);
  } else {
    animationFrame = undefined;
  }
}

function selectState(stateId) {
  const next = configuration.states.find((state) => state.id === stateId);
  if (!next) {
    return;
  }
  activeState = next;
  frameIndex = 0;
  for (const button of controlsElement.querySelectorAll("button")) {
    button.setAttribute("aria-pressed", String(button.dataset.stateId === stateId));
  }
  startAnimation();
}

function buildControls() {
  for (const state of configuration.states) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.stateId = state.id;
    button.textContent = state.label;
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => selectState(state.id));
    controlsElement.append(button);
  }
}

async function loadPreview() {
  try {
    const response = await fetch("states.json");
    if (!response.ok) {
      throw new Error(`State data returned ${response.status}`);
    }
    configuration = await response.json();
    atlas = new Image();
    atlas.decoding = "async";
    atlas.src = atlasUrl;
    await atlas.decode();
    if (
      atlas.naturalWidth !== configuration.atlas.width ||
      atlas.naturalHeight !== configuration.atlas.height
    ) {
      throw new Error("Atlas dimensions do not match states.json");
    }
    buildControls();
    activeState = configuration.states[0];
    selectState(activeState.id);
    statusElement.textContent = "Rendered from the installable Codex v2 atlas";
  } catch (error) {
    statusElement.textContent =
      "Preview unavailable. The installable files remain on GitHub.";
    console.error(error);
  }
}

async function copyCommand() {
  const command = "pepper-pet doctor --source pet --json";
  try {
    await navigator.clipboard.writeText(command);
    copyFeedback.textContent = "Command copied.";
  } catch {
    copyFeedback.textContent = `Copy this command: ${command}`;
  }
}

reducedMotion.addEventListener("change", () => {
  if (activeState) {
    frameIndex = 0;
    startAnimation();
  }
});

document.addEventListener("visibilitychange", () => {
  if (activeState) {
    startAnimation();
  }
});

copyButton.addEventListener("click", copyCommand);
loadPreview();
