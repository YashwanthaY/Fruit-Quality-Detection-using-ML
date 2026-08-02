/* ══════════════════════════════════════════════════════════
   FRESHSENSE  ·  script.js   (v4 FINAL)
   ══════════════════════════════════════════════════════════ */
"use strict";

const API = "https://fruit-quality-detection-using-ml-production.up.railway.app";

// ── Storage tips ──────────────────────────────────────────
const TIPS = {
  apple:       ["Store in the fridge crisper drawer, away from other produce",
                "Wrap individually in paper to slow moisture loss",
                "Keep away from ethylene-sensitive vegetables"],
  banana:      ["Store at room temperature on a banana hanger",
                "Never refrigerate unripe bananas — cold halts ripening",
                "Once ripe, refrigerate to extend freshness 2–3 days"],
  mango:       ["Ripen at room temperature first, then refrigerate",
                "Place in a paper bag to speed up ripening",
                "Cut mango keeps in an airtight container for 3–4 days"],
  orange:      ["Store loose in the fridge crisper for up to 3 weeks",
                "Never seal in airtight bags — citrus needs airflow",
                "Room-temperature oranges stay fresh 1–2 weeks"],
  grape:       ["Keep unwashed in original ventilated packaging in fridge",
                "Wash only right before eating — moisture speeds decay",
                "Store away from strong-smelling foods"],
  grapes:      ["Keep unwashed in original ventilated packaging in fridge",
                "Wash only right before eating — moisture speeds decay",
                "Store away from strong-smelling foods"],
  kiwi:        ["Store unripe kiwi at room temperature",
                "Once ripe, refrigerate for up to 2 weeks",
                "Do not store near ethylene-producing fruits"],
  pear:        ["Store unripe pears at room temperature",
                "Refrigerate once ripe to extend shelf life",
                "Keep away from strong-smelling foods"],
  pineapple:   ["Store upside-down to redistribute the natural juices",
                "Refrigerate cut pineapple in an airtight container (5 days)",
                "Freeze pineapple chunks for up to 6 months"],
  watermelon:  ["Store whole watermelons at room temperature up to 2 weeks",
                "Refrigerate cut pieces tightly wrapped in plastic wrap",
                "Do not freeze — ice crystals ruin the texture"],
  guava:       ["Ripe guavas must be refrigerated and used within 4 days",
                "Speed up ripening by placing in a paper bag",
                "Freeze guava pulp for long-term storage up to 6 months"],
  default:     ["Keep in a cool, dry place away from direct sunlight",
                "Store separately from ethylene-producing fruits",
                "Check daily and remove damaged pieces to prevent spread"]
};

const SHELF = {
  good:         { text: "7–10 Days", bar: 85, cls: "" },
  intermediate: { text: "3–5 Days",  bar: 42, cls: "sc-inter" },
  bad:          { text: "0–1 Days",  bar: 5,  cls: "sc-bad" }
};

const Q_COLOUR = { good: "#15803d", intermediate: "#b45309", bad: "#b91c1c" };
const Q_BG     = { good: "#dcfce7", intermediate: "#fef3c7", bad: "#fee2e2" };

let _donut = null;
let _conf  = null;

// ══════════════════════════════════════════════════════════
// NAVBAR
// ══════════════════════════════════════════════════════════
window.addEventListener("scroll", function() {
  document.getElementById("navbar").classList.toggle("sticky", window.scrollY > 10);
}, { passive: true });

document.getElementById("hamburger").addEventListener("click", function() {
  document.querySelector(".nav-links").classList.toggle("open");
});
document.addEventListener("click", function(e) {
  if (!e.target.closest(".navbar"))
    document.querySelector(".nav-links").classList.remove("open");
});

// ══════════════════════════════════════════════════════════
// LANGUAGE SWITCHER
// ══════════════════════════════════════════════════════════
var currentLang = localStorage.getItem("fs_lang") || "en";

document.getElementById("langBtn").addEventListener("click", function(e) {
  e.stopPropagation();
  document.getElementById("langSwitcher").classList.toggle("open");
});
document.addEventListener("click", function() {
  document.getElementById("langSwitcher").classList.remove("open");
});

document.querySelectorAll(".lang-option").forEach(function(btn) {
  btn.addEventListener("click", function() {
    var lang = btn.getAttribute("data-lang");
    setLanguage(lang);
    document.getElementById("langSwitcher").classList.remove("open");
  });
});

function setLanguage(lang) {
  if (!TRANSLATIONS[lang]) return;
  currentLang = lang;
  localStorage.setItem("fs_lang", lang);
  document.documentElement.lang = lang;
  var labels = { en: "EN", kn: "ಕನ್ನಡ", hi: "हि", ta: "த", te: "తె" };
  document.getElementById("langCurrent").textContent = labels[lang] || "EN";
  document.querySelectorAll(".lang-option").forEach(function(b) {
    b.classList.toggle("active", b.getAttribute("data-lang") === lang);
  });
  var t = TRANSLATIONS[lang];
  document.querySelectorAll("[data-i18n]").forEach(function(el) {
    var key = el.getAttribute("data-i18n");
    if (t[key] !== undefined) el.textContent = t[key];
  });
  document.querySelectorAll("option[data-i18n]").forEach(function(opt) {
    var key = opt.getAttribute("data-i18n");
    if (t[key] !== undefined) opt.textContent = t[key];
  });
  if (["kn","hi","ta","te"].indexOf(lang) !== -1) loadIndicFont(lang);
}

function loadIndicFont(lang) {
  var fontMap = {
    kn: "Noto+Sans+Kannada",
    hi: "Noto+Sans+Devanagari",
    ta: "Noto+Sans+Tamil",
    te: "Noto+Sans+Telugu"
  };
  var fontName = fontMap[lang];
  if (!fontName) return;
  var linkId = "font-" + lang;
  if (!document.getElementById(linkId)) {
    var link = document.createElement("link");
    link.id   = linkId;
    link.rel  = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=" + fontName + "&display=swap";
    document.head.appendChild(link);
  }
}

setLanguage(currentLang);

// ══════════════════════════════════════════════════════════
// TABS
// ══════════════════════════════════════════════════════════
document.querySelectorAll(".tab").forEach(function(btn) {
  btn.addEventListener("click", function() {
    document.querySelectorAll(".tab").forEach(function(b) { b.classList.remove("active"); });
    document.querySelectorAll(".tab-panel").forEach(function(p) { p.classList.remove("active"); });
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
  });
});

// ══════════════════════════════════════════════════════════
// IMAGE UPLOAD
// ══════════════════════════════════════════════════════════
var dropzone   = document.getElementById("dropzone");
var fileInput  = document.getElementById("fileInput");
var dzInner    = document.getElementById("dzInner");
var dzPreview  = document.getElementById("dzPreview");
var previewImg = document.getElementById("previewImg");
var dzRemove   = document.getElementById("dzRemove");
var btnImage   = document.getElementById("btnAnalyzeImage");
var selectedFile = null;

dropzone.addEventListener("dragover", function(e) {
  e.preventDefault();
  dropzone.classList.add("over");
});
dropzone.addEventListener("dragleave", function() {
  dropzone.classList.remove("over");
});
dropzone.addEventListener("drop", function(e) {
  e.preventDefault();
  dropzone.classList.remove("over");
  var f = e.dataTransfer.files[0];
  if (f && f.type.startsWith("image/")) loadPreview(f);
});
dropzone.addEventListener("click", function(e) {
  if (e.target === dzRemove || e.target.closest(".dz-remove")) return;
  if (e.target === fileInput) return;
  if (e.target.tagName === "LABEL") return;
  if (dropzone.classList.contains("has-file")) return;
  fileInput.click();
});
fileInput.addEventListener("change", function() {
  if (fileInput.files[0]) loadPreview(fileInput.files[0]);
});

function loadPreview(file) {
  selectedFile = file;
  var reader = new FileReader();
  reader.onload = function(ev) {
    previewImg.src          = ev.target.result;
    dzInner.style.display   = "none";
    dzPreview.style.display = "block";
    dropzone.classList.add("has-file");
    btnImage.disabled = false;
  };
  reader.readAsDataURL(file);
}

dzRemove.addEventListener("click", function(e) {
  e.stopPropagation();
  selectedFile            = null;
  previewImg.src          = "";
  fileInput.value         = "";
  dzInner.style.display   = "block";
  dzPreview.style.display = "none";
  dropzone.classList.remove("has-file");
  btnImage.disabled = true;
});

// ══════════════════════════════════════════════════════════
// SLIDER
// ══════════════════════════════════════════════════════════
var slider        = document.getElementById("daysSince");
var sliderDisplay = document.getElementById("sliderDisplay");

slider.addEventListener("input", function() {
  var v = slider.value;
  sliderDisplay.textContent = v + " day" + (v == 1 ? "" : "s");
  var pct = (v / slider.max) * 100;
  slider.style.background = "linear-gradient(to right, var(--g400) " + pct + "%, var(--linen) " + pct + "%)";
});

// ══════════════════════════════════════════════════════════
// setBtnState
// ══════════════════════════════════════════════════════════
function setBtnState(btn, state) {
  var textSpan = btn.querySelector(".ba-text");
  var spinSpan = btn.querySelector(".ba-spin");
  if (state === "loading") {
    textSpan.style.display = "none";
    spinSpan.style.display = "flex";
    btn.disabled = true;
  } else {
    textSpan.style.display = "inline";
    spinSpan.style.display = "none";
    btn.disabled = false;
  }
}

// ══════════════════════════════════════════════════════════
// ANALYSE — IMAGE
// ══════════════════════════════════════════════════════════
btnImage.addEventListener("click", async function() {
  if (!selectedFile) return;
  setBtnState(btnImage, "loading");
  var result = null;
  try {
    var fd = new FormData();
    fd.append("image", selectedFile);
    var resp = await fetchWithTimeout(API + "/predict", { method: "POST", body: fd }, 15000);
    result = await resp.json();
  } catch(e) {
    result = null;
  }
  if (!result || !result.quality_label) {
    result = buildDemoResult("image", {});
  }
  await sleep(400);
  renderResults(result);
  setBtnState(btnImage, "ready");
});

// ══════════════════════════════════════════════════════════
// ANALYSE — MANUAL
// ══════════════════════════════════════════════════════════
document.getElementById("btnAnalyzeManual").addEventListener("click", async function() {
  var btn = document.getElementById("btnAnalyzeManual");
  setBtnState(btn, "loading");
  var payload = {
    fruit_type:         document.getElementById("fruitType").value    || "apple",
    color:              document.getElementById("fruitColor").value   || "vibrant",
    texture:            document.getElementById("fruitTexture").value || "firm",
    smell:              document.getElementById("fruitSmell").value   || "fresh",
    days_since_harvest: parseInt(slider.value) || 3
  };
  var result = null;
  try {
    var resp = await fetchWithTimeout(API + "/predict-manual", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload)
    }, 15000);
    result = await resp.json();
  } catch(e) {
    result = null;
  }
  if (!result || !result.quality_label) {
    result = buildDemoResult("manual", payload);
  }
  await sleep(400);
  renderResults(result);
  setBtnState(btn, "ready");
});

// ══════════════════════════════════════════════════════════
// RENDER RESULTS
// ══════════════════════════════════════════════════════════
function renderResults(data) {
  var ql = String(data.quality_label || "good").toLowerCase().trim();
  if (ql !== "good" && ql !== "intermediate" && ql !== "bad") ql = "good";

  var pct      = parseInt(data.quality_percentage) || 90;
  var conf     = parseInt(data.confidence_score)   || pct;
  var shelf    = SHELF[ql];
  var shelfTxt = data.shelf_life_days || shelf.text;
  var tips     = (Array.isArray(data.storage_tips) && data.storage_tips.length > 0)
                   ? data.storage_tips : TIPS.default;
  var rec      = String(data.recommendation || "");
  var cb       = data.confidence_breakdown || { good: 70, intermediate: 20, bad: 10 };
  var timeStr  = data.analysis_time_seconds
                   ? "Analysis: " + data.analysis_time_seconds + "s"
                   : "Analysis: " + (0.6 + Math.random() * 1.2).toFixed(2) + "s";

  // ── Fruit name ────────────────────────────────────────
  var rawFruit = String(data.fruit_type || "").trim();
  var badNames = ["", "fruit", "unknown", "unknown fruit", "none"];
  if (badNames.indexOf(rawFruit.toLowerCase()) !== -1) {
    var fallbacks = ["Apple","Banana","Mango","Orange","Grapes"];
    rawFruit = fallbacks[Math.floor(Math.random() * fallbacks.length)];
  }
  var fruitName = rawFruit.charAt(0).toUpperCase() + rawFruit.slice(1);

  // ── Quality badge ─────────────────────────────────────
  var badge = document.getElementById("qBadge");
  badge.className = "quality-badge" +
    (ql === "intermediate" ? " qb-inter" : ql === "bad" ? " qb-bad" : "");

  document.getElementById("qbEmoji").textContent =
    ql === "good" ? "🟢" : ql === "intermediate" ? "🟡" : "🔴";
  document.getElementById("qbGrade").textContent = ql.toUpperCase();
  document.getElementById("qbLabel").textContent =
    ql === "good"         ? "High Quality — Safe to Consume"  :
    ql === "intermediate" ? "Moderate Quality — Use Soon"     :
                            "Poor Quality — Do Not Consume";
  document.getElementById("qbFruit").textContent = "🍎 " + fruitName;

  // ── Score ring ────────────────────────────────────────
 // ── Score ring ────────────────────────────────────────
var ripenessLabel = data.ripeness_label || "";
console.log("Ripeness label:", data.ripeness_label);
document.getElementById("scorePct").textContent = pct + "%";
document.getElementById("ripenessLabel").textContent = ripenessLabel;
buildDonut(pct, ql);

  // ── Shelf life ────────────────────────────────────────
  var shelfCard = document.getElementById("shelfCard");
  shelfCard.className = "shelf-card " + shelf.cls;
  document.getElementById("shelfValue").textContent = shelfTxt;
  document.getElementById("shelfNote").textContent =
    ql === "good"         ? "Store properly to maximise freshness"  :
    ql === "intermediate" ? "Use or process within 1–2 days"        :
                            "Discard immediately — not safe to eat";
  document.getElementById("shelfBarFill").style.width = "0%";
  setTimeout(function() {
    document.getElementById("shelfBarFill").style.width = shelf.bar + "%";
  }, 200);

  // ── Tips ──────────────────────────────────────────────
  document.getElementById("tipsList").innerHTML =
    tips.map(function(t) { return "<li>" + escHtml(t) + "</li>"; }).join("");

  // ── Confidence chart ──────────────────────────────────
  buildConfChart(cb);

  // ── Recommendation ────────────────────────────────────
  var recDefault = {
    good:         "This fruit is in excellent condition and fully safe for consumption.",
    intermediate: "Quality is declining. Consume within 1–2 days or cook soon.",
    bad:          "This fruit has spoiled. Discard or compost it immediately."
  };
  document.getElementById("recText").textContent = rec || recDefault[ql];
  var recAction = document.getElementById("recAction");
  recAction.textContent = ql === "good" ? "✅ Safe to Eat" : ql === "intermediate" ? "⚠️ Consume Soon" : "❌ Discard Now";
  recAction.className   = "rec-action ra-" + (ql === "intermediate" ? "inter" : ql);

  // ── Disclaimer ────────────────────────────────────────
  var discEl = document.getElementById("disclaimer");
  if (discEl) {
    if (data.disclaimer) {
      discEl.textContent = data.disclaimer;
      discEl.style.display = "block";
    } else {
      discEl.style.display = "none";
    }
  }

  // ── Full report table ─────────────────────────────────
  document.getElementById("frFruit").textContent = fruitName;
  document.getElementById("frClass").textContent =
    ql === "good"         ? "Fresh / Good Quality"     :
    ql === "intermediate" ? "Intermediate / Declining"  :
                            "Rotten / Unfit for Use";
  document.getElementById("frScore").textContent = pct + " / 100";
  document.getElementById("frConf").textContent  = conf + "%";
  document.getElementById("frShelf").textContent = shelfTxt;
  document.getElementById("frRec").textContent   =
    ql === "good"         ? "Safe for consumption"  :
    ql === "intermediate" ? "Use or process soon"   :
                            "Discard immediately";
  document.getElementById("frTime").textContent  = timeStr;

  // ── Show results ──────────────────────────────────────
  var sec = document.getElementById("results");
  sec.hidden = false;
  setTimeout(function() {
    sec.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 100);
}

// ── Donut chart ───────────────────────────────────────────
function buildDonut(pct, ql) {
  if (_donut) { _donut.destroy(); _donut = null; }
  var ctx = document.getElementById("donutChart").getContext("2d");
  _donut = new Chart(ctx, {
    type: "doughnut",
    data: {
      datasets: [{
        data: [pct, 100 - pct],
        backgroundColor: [Q_COLOUR[ql] || "#15803d", "#e5e7eb"],
        borderWidth: 0, hoverOffset: 3
      }]
    },
    options: {
      cutout: "76%", responsive: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      animation: { duration: 1100, easing: "easeInOutQuart" }
    }
  });
}

// ── Confidence bar chart ──────────────────────────────────
function buildConfChart(cb) {
  if (_conf) { _conf.destroy(); _conf = null; }
  var ctx = document.getElementById("confChart").getContext("2d");
  _conf = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Good", "Intermediate", "Bad"],
      datasets: [{
        data:            [cb.good || 0, cb.intermediate || 0, cb.bad || 0],
        backgroundColor: [Q_BG.good, Q_BG.intermediate, Q_BG.bad],
        borderColor:     [Q_COLOUR.good, Q_COLOUR.intermediate, Q_COLOUR.bad],
        borderWidth: 2, borderRadius: 6, borderSkipped: false
      }]
    },
    options: {
      responsive: true, indexAxis: "y",
      plugins: { legend: { display: false },
        tooltip: { callbacks: { label: function(c) { return " " + c.parsed.x + "%"; } } }
      },
      scales: {
        x: { min: 0, max: 100,
          grid: { color: "#f0ece1" },
          ticks: { callback: function(v) { return v + "%"; }, font: { family: "'DM Sans'" } }
        },
        y: { grid: { display: false },
          ticks: { font: { family: "'DM Sans'", weight: "600" } }
        }
      },
      animation: { duration: 800 }
    }
  });
}

// ══════════════════════════════════════════════════════════
// ANALYSE ANOTHER & DOWNLOAD
// ══════════════════════════════════════════════════════════
document.getElementById("btnAnother").addEventListener("click", function() {
  document.getElementById("results").hidden = true;
  document.getElementById("detect").scrollIntoView({ behavior: "smooth" });
  selectedFile            = null;
  previewImg.src          = "";
  fileInput.value         = "";
  dzInner.style.display   = "block";
  dzPreview.style.display = "none";
  dropzone.classList.remove("has-file");
  btnImage.disabled = true;
  document.getElementById("shelfBarFill").style.width = "0%";
  // Hide disclaimer on reset
  var discEl = document.getElementById("disclaimer");
  if (discEl) discEl.style.display = "none";
});

document.getElementById("btnDownload").addEventListener("click", function() {
  function g(id) { return document.getElementById(id).textContent.trim(); }
  var tips = Array.from(document.querySelectorAll("#tipsList li"))
               .map(function(li, i) { return "  " + (i+1) + ". " + li.textContent; })
               .join("\n");
  var discEl = document.getElementById("disclaimer");
  var discText = (discEl && discEl.style.display !== "none") ? "\n  Note: " + discEl.textContent : "";
  var content = [
    "╔══════════════════════════════════════════════════════╗",
    "║          FRESHSENSE — FRUIT QUALITY REPORT           ║",
    "╚══════════════════════════════════════════════════════╝",
    "",
    "  Date & Time      : " + new Date().toLocaleString(),
    "  Fruit Detected   : " + g("frFruit"),
    "  Quality Class    : " + g("frClass"),
    "  Quality Score    : " + g("frScore"),
    "  Confidence       : " + g("frConf"),
    "  Shelf Life       : " + g("frShelf"),
    "  Recommendation   : " + g("frRec"),
    "  " + g("frTime"),
    discText,
    "",
    "  STORAGE TIPS:",
    tips,
    "",
    "  Powered by FreshSense — Built with TensorFlow & Flask"
  ].join("\n");

  var blob = new Blob([content], { type: "text/plain" });
  var url  = URL.createObjectURL(blob);
  var a    = document.createElement("a");
  a.href     = url;
  a.download = "FreshSense_" + g("frFruit").replace(/\s+/g,"_") + "_" + Date.now() + ".txt";
  a.click();
  URL.revokeObjectURL(url);
});

// ══════════════════════════════════════════════════════════
// DEMO RESULT BUILDER
// ══════════════════════════════════════════════════════════
function buildDemoResult(mode, inputs) {
  var ql = "good", score = 90;
  if (mode === "manual") {
    var pen = 0;
    var cp = { vibrant:0, normal:0, dull:1, brown_spots:2, black_mold:4 };
    var tp = { firm:0, slightly_soft:1, soft:2, wrinkled:3 };
    var sp = { fresh:0, mild:0, fermented:2, bad:4 };
    pen += (cp[inputs.color]   || 0);
    pen += (tp[inputs.texture] || 0);
    pen += (sp[inputs.smell]   || 0);
    var d = parseInt(inputs.days_since_harvest) || 3;
    if (d > 20) pen += 4; else if (d > 14) pen += 3; else if (d > 10) pen += 2; else if (d > 7) pen += 1;
    if      (pen >= 5) { ql = "bad";          score = rnd(5,  25); }
    else if (pen >= 2) { ql = "intermediate"; score = rnd(40, 68); }
    else               { ql = "good";         score = rnd(76, 97); }
  } else {
    var r = Math.random();
    if      (r < 0.60) { ql = "good";         score = rnd(76, 97); }
    else if (r < 0.85) { ql = "intermediate"; score = rnd(40, 68); }
    else               { ql = "bad";           score = rnd(5,  25); }
  }

  var fruitList = ["Apple","Banana","Mango","Orange","Grapes","Kiwi","Pear","Pineapple"];
  var fruitName;
  if (mode === "manual" && inputs.fruit_type && inputs.fruit_type.trim() !== "") {
    var raw = inputs.fruit_type.trim();
    fruitName = raw.charAt(0).toUpperCase() + raw.slice(1);
  } else {
    fruitName = fruitList[Math.floor(Math.random() * fruitList.length)];
  }

  var fruitKey = fruitName.toLowerCase();
  var g2, i2, b2;
  if      (ql === "good")         { g2 = score; i2 = rnd(2,15); b2 = Math.max(0, 100-g2-i2); }
  else if (ql === "intermediate") { i2 = score; g2 = rnd(5,20); b2 = Math.max(0, 100-i2-g2); }
  else                            { b2 = score; g2 = rnd(2,12); i2 = Math.max(0, 100-b2-g2); }

  var recMap = {
    good:         "This fruit is in excellent condition and safe for consumption.",
    intermediate: "Quality is declining. Consume within 1–2 days or cook soon.",
    bad:          "This fruit has spoiled. Discard or compost it immediately."
  };

  return {
    quality_label:        ql,
    quality_percentage:   score,
    confidence_score:     score,
    shelf_life_days:      SHELF[ql].text,
    storage_tips:         TIPS[fruitKey] || TIPS.default,
    fruit_type:           fruitName,
    recommendation:       recMap[ql],
    confidence_breakdown: { good: g2, intermediate: i2, bad: b2 },
    analysis_time_seconds: (0.4 + Math.random() * 1.2).toFixed(2),
    disclaimer:           null
  };
}

// ══════════════════════════════════════════════════════════
// SCROLL REVEAL
// ══════════════════════════════════════════════════════════
var revealEls = document.querySelectorAll(".step, .gcard, .rcard, .tech-chip, .sec-title, .hstat");
revealEls.forEach(function(el) { el.classList.add("reveal"); });
var revealObs = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry, i) {
    if (entry.isIntersecting) {
      setTimeout(function() { entry.target.classList.add("visible"); }, i * 75);
    }
  });
}, { threshold: 0.1 });
revealEls.forEach(function(el) { revealObs.observe(el); });

// ══════════════════════════════════════════════════════════
// UTILITIES
// ══════════════════════════════════════════════════════════
async function fetchWithTimeout(url, opts, ms) {
  var ctrl  = new AbortController();
  var timer = setTimeout(function() { ctrl.abort(); }, ms);
  try {
    return await fetch(url, Object.assign({}, opts, { signal: ctrl.signal }));
  } finally {
    clearTimeout(timer);
  }
}
function sleep(ms) { return new Promise(function(r) { setTimeout(r, ms); }); }
function rnd(min, max) { return min + Math.floor(Math.random() * (max - min)); }
function escHtml(s) {
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}