// web/app.js

const COLORS = {
  N: "#ffffff",
  R: "#ff4d4d",
  B: "#4d79ff",
  Y: "#ffd24d",
  P: "#b84dff", // R+B
  O: "#ff944d", // R+Y
  G: "#4dff88", // B+Y
  K: "#111111", // R+B+Y
};

const C2B = { N: 0, R: 1, B: 2, Y: 4 };
const B2C = { 0: "N", 1: "R", 2: "B", 4: "Y", 3: "P", 5: "O", 6: "G", 7: "K" };

const RUN_BANKS = ["easy", "normal", "hard", "expert", "elite"];
const WRONG_PENALTY_MS = 10_000;

function rot90(mat) {
  const out = Array.from({ length: 3 }, () => Array(3).fill("N"));
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      out[r][c] = mat[2 - c][r];
    }
  }
  return out;
}
function rotate(mat, k) {
  let out = mat;
  for (let i = 0; i < (k % 4); i++) out = rot90(out);
  return out;
}

function overlayCell(vals) {
  const bits = vals.filter(v => v !== "N").map(v => C2B[v]);
  if (bits.length === 0) return { cell: "N", ok: true };

  const cnt = new Map();
  for (const b of bits) cnt.set(b, (cnt.get(b) || 0) + 1);

  // same color stacking allowed
  if (cnt.size === 1) {
    return { cell: B2C[[...cnt.keys()][0]], ok: true };
  }

  // mixing valid only if each distinct color appears exactly once (1:1)
  for (const v of cnt.values()) {
    if (v !== 1) return { cell: "N", ok: false };
  }

  let mask = 0;
  for (const k of cnt.keys()) mask |= k;
  return { cell: B2C[mask], ok: true };
}

function overlay(mats3) {
  const target = Array.from({ length: 3 }, () => Array(3).fill("N"));
  let ok = true;

  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      const res = overlayCell([mats3[0][r][c], mats3[1][r][c], mats3[2][r][c]]);
      if (!res.ok) ok = false;
      target[r][c] = res.cell;
    }
  }
  return { target, ok };
}

function equalGrid(a, b) {
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      if (a[r][c] !== b[r][c]) return false;
    }
  }
  return true;
}

function renderGrid(el, grid) {
  el.innerHTML = "";
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      const d = document.createElement("div");
      d.className = "cell";
      const v = grid[r][c];
      d.style.background = COLORS[v];
      d.title = v;
      el.appendChild(d);
    }
  }
}

function makeCardEl(index, mat) {
  const wrap = document.createElement("div");
  wrap.className = "card";
  wrap.dataset.idx = String(index);

  const head = document.createElement("div");
  head.className = "card-head";

  const num = document.createElement("div");
  num.className = "card-num";
  num.textContent = `#${index + 1}`;
  head.appendChild(num);

  wrap.appendChild(head);

  const grid = document.createElement("div");
  grid.className = "grid grid-card";
  wrap.appendChild(grid);

  renderGrid(grid, mat);
  return wrap;
}

// Mental rotation check: selected 3 cards correct if any rotations match
function selectionMatches(cards, target, sel) {
  for (let r1 = 0; r1 < 4; r1++) {
    for (let r2 = 0; r2 < 4; r2++) {
      for (let r3 = 0; r3 < 4; r3++) {
        const mats = [
          rotate(cards[sel[0]], r1),
          rotate(cards[sel[1]], r2),
          rotate(cards[sel[2]], r3),
        ];
        const out = overlay(mats);
        if (out.ok && equalGrid(out.target, target)) return true;
      }
    }
  }
  return false;
}

/* ===== Time helpers ===== */
function formatTime(ms) {
  const total = Math.max(0, ms);
  const m = Math.floor(total / 60000);
  const s = Math.floor((total % 60000) / 1000);
  const d = Math.floor((total % 1000) / 100); // 0.1s
  const mm = String(m).padStart(2, "0");
  const ss = String(s).padStart(2, "0");
  return `${mm}:${ss}.${d}`;
}

/* ===== Leaderboard ===== */
const LB_KEY = "pixel_puzzle_top5";
function loadLeaderboard() {
  try {
    const raw = localStorage.getItem(LB_KEY);
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}
function saveLeaderboard(arr) {
  localStorage.setItem(LB_KEY, JSON.stringify(arr));
}
function renderLeaderboard() {
  const list = loadLeaderboard();
  const el = document.getElementById("leaderboard");
  el.innerHTML = "";
  if (list.length === 0) {
    const li = document.createElement("li");
    li.textContent = "No records yet.";
    el.appendChild(li);
    return;
  }
  list.forEach(item => {
    const li = document.createElement("li");
    const when = new Date(item.ts).toLocaleString();
    li.textContent = `${formatTime(item.totalMs)}  (penalty ${formatTime(item.penaltyMs)}) — ${when}`;
    el.appendChild(li);
  });
}
function addRecord(totalMs, penaltyMs) {
  const list = loadLeaderboard();
  list.push({ totalMs, penaltyMs, ts: Date.now() });
  list.sort((a, b) => a.totalMs - b.totalMs);
  const top5 = list.slice(0, 5);
  saveLeaderboard(top5);
  renderLeaderboard();
}

/* ===== App State ===== */
const state = {
  data: null,
  puzzle: null,
  selected: [],

  // run mode
  runActive: false,
  roundIndex: 0,        // 0..4
  penaltyMs: 0,
  startTs: 0,
  timerId: null,
};

/* ===== HUD ===== */
function setHud() {
  const roundEl = document.getElementById("hudRound");
  const bankEl = document.getElementById("hudBank");
  const timeEl = document.getElementById("hudTime");
  const penEl = document.getElementById("hudPenalty");

  if (!state.runActive) {
    roundEl.textContent = "Round: -";
    bankEl.textContent = "Bank: -";
    timeEl.textContent = "Time: 00:00.0";
    penEl.textContent = "Penalty: +0.0s";
    return;
  }

  roundEl.textContent = `Round: ${state.roundIndex + 1}/5`;
  bankEl.textContent = `Bank: ${RUN_BANKS[state.roundIndex]}`;
  const baseMs = Date.now() - state.startTs;
  timeEl.textContent = `Time: ${formatTime(baseMs + state.penaltyMs)}`;
  penEl.textContent = `Penalty: +${formatTime(state.penaltyMs)}`;
}

function startTimer() {
  stopTimer();
  state.timerId = setInterval(() => setHud(), 100);
}
function stopTimer() {
  if (state.timerId) clearInterval(state.timerId);
  state.timerId = null;
}

/* ===== Selection UI ===== */
function setSelectedStyles() {
  document.querySelectorAll("#cardsWrap .card").forEach(el => {
    const i = Number(el.dataset.idx);
    el.classList.toggle("selected", state.selected.includes(i));

    // badge order
    const existing = el.querySelector(".badge");
    if (existing) existing.remove();
    const pos = state.selected.indexOf(i);
    if (pos >= 0) {
      const b = document.createElement("div");
      b.className = "badge";
      b.textContent = String(pos + 1);
      el.appendChild(b);
    }
  });

  const sb = document.getElementById("submitBtn");
  sb.disabled = state.selected.length !== 3;
  sb.textContent = state.selected.length === 3 ? "Submit" : "Submit (need 3 cards)";
}

/* ===== Puzzle loading ===== */
function pickRandomPuzzle(bank) {
  const list = state.data[bank];
  return list[Math.floor(Math.random() * list.length)];
}

function loadPuzzleByBank(bank) {
  state.puzzle = pickRandomPuzzle(bank);
  state.selected = [];
  document.getElementById("result").textContent = "";

  renderGrid(document.getElementById("targetGrid"), state.puzzle.target);

  const cardsWrap = document.getElementById("cardsWrap");
  cardsWrap.innerHTML = "";

  state.puzzle.cards.forEach((mat, idx) => {
    const el = makeCardEl(idx, mat);

    el.onclick = () => {
      if (!state.puzzle) return;

      const pos = state.selected.indexOf(idx);
      if (pos >= 0) {
        state.selected.splice(pos, 1);
      } else {
        // allow 3 selections; if already 3, ignore (you can change to "drop oldest" later)
        if (state.selected.length >= 3) return;
        state.selected.push(idx);
      }
      setSelectedStyles();
    };

    cardsWrap.appendChild(el);
  });

  setSelectedStyles();
}

function loadCurrentRoundPuzzle() {
  const bank = RUN_BANKS[state.roundIndex];
  loadPuzzleByBank(bank);
  setHud();
}

/* ===== Run control ===== */
function startRun() {
  state.runActive = true;
  state.roundIndex = 0;
  state.penaltyMs = 0;
  state.startTs = Date.now();

  // lock manual bank switching while run (optional)
  document.getElementById("bankSelect").disabled = true;

  loadCurrentRoundPuzzle();
  startTimer();

  document.getElementById("result").textContent = "Run started.";
}

function finishRun() {
  stopTimer();
  const totalMs = (Date.now() - state.startTs) + state.penaltyMs;

  addRecord(totalMs, state.penaltyMs);

  state.runActive = false;
  document.getElementById("bankSelect").disabled = false;

  setHud();
  document.getElementById("result").textContent = `✅ Finished! Total: ${formatTime(totalMs)} (penalty +${formatTime(state.penaltyMs)})`;
}

function resetRun() {
  stopTimer();
  state.runActive = false;
  state.roundIndex = 0;
  state.penaltyMs = 0;
  state.startTs = 0;
  document.getElementById("bankSelect").disabled = false;
  setHud();
  document.getElementById("result").textContent = "";
}

/* ===== Main ===== */
async function main() {
  const res = await fetch("puzzles.json");
  state.data = await res.json();

  // initial leaderboard
  renderLeaderboard();

  const bankSelect = document.getElementById("bankSelect");

  // Manual new puzzle (outside run): uses selected bank
  document.getElementById("newBtn").onclick = () => {
    if (state.runActive) return; // keep run strict
    loadPuzzleByBank(bankSelect.value);
  };

  document.getElementById("startBtn").onclick = () => {
    if (state.runActive) return;
    startRun();
  };

  document.getElementById("resetBtn").onclick = () => {
    resetRun();
    // reload a manual puzzle for convenience
    loadPuzzleByBank(bankSelect.value);
  };

  document.getElementById("submitBtn").onclick = () => {
    if (!state.puzzle) return;
    if (state.selected.length !== 3) return;

    const ok = selectionMatches(state.puzzle.cards, state.puzzle.target, state.selected);

    if (ok) {
      document.getElementById("result").textContent = "✅ Correct";

      if (state.runActive) {
        // next round or finish
        if (state.roundIndex < 4) {
          state.roundIndex += 1;
          loadCurrentRoundPuzzle();
        } else {
          finishRun();
        }
      }
    } else {
      document.getElementById("result").textContent = "❌ Wrong (+10s)";
      if (state.runActive) {
        state.penaltyMs += WRONG_PENALTY_MS;
        setHud();
      }
    }
  };

  // Initial: show a manual puzzle
  resetRun();
  loadPuzzleByBank(bankSelect.value);
}

main();
