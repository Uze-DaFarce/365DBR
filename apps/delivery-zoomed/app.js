/**
 * app.js — Delivery Zoomed PWA Core Controller
 * Built for Coach's Pizza (Conrad, MT) & adaptable to any small-town delivery operation.
 */

import {
  TICKET_STATUSES,
  extractTicketsFromPhoto,
  extractOdometerFromPhoto,
  resolveApiKeys,
  isUuidKeyId,
  isValidShift4OrderNumber
} from "./ocr-parser.js?v=20261120_4";

const STORAGE_KEY = "delivery_zoomed_state_v1";
const SETTINGS_KEY = "delivery_zoomed_settings_v1";
const CUSTOM_RULES_KEY = "delivery_zoomed_custom_rules_v1";
const CUSTOMER_DB_KEY = "delivery_zoomed_customers_v1";
const HISTORY_DB_KEY = "delivery_zoomed_history_v1";

const state = {
  mapRules: null,
  tickets: [],
  ignoredTickets: [],
  customers: {},
  history: [],
  trainContingencyActive: false,
  selectedCrossingId: "north_crossing_bypass",
  shift: {
    date: new Date().toISOString().slice(0, 10),
    odometerStart: "",
    odometerEnd: "",
    startedAt: null,
    endedAt: null,
    startOdoPhoto: null,
    endOdoPhoto: null
  },
  settings: {
    visionProvider: "google",
    geminiApiKey: "",
    grokApiKey: "",
    apiKey: "",
    encouragementOnlyTips: true,
    uploadFromGallery: false
  }
};

async function initApp() {
  loadPersistedSettings();
  await loadMapRules();
  loadPermanentCustomerAndHistoryDb();
  loadPersistedShiftState();
  bindEvents();
  renderAll();
}

function loadPermanentCustomerAndHistoryDb() {
  try {
    const rawCust = localStorage.getItem(CUSTOMER_DB_KEY);
    if (rawCust) state.customers = JSON.parse(rawCust) || {};
  } catch (_) {}
  try {
    const rawHist = localStorage.getItem(HISTORY_DB_KEY);
    if (rawHist) state.history = Array.isArray(JSON.parse(rawHist)) ? JSON.parse(rawHist) : [];
  } catch (_) {}
}

function savePermanentCustomerAndHistoryDb() {
  localStorage.setItem(CUSTOMER_DB_KEY, JSON.stringify(state.customers));
  localStorage.setItem(HISTORY_DB_KEY, JSON.stringify(state.history));
}

async function loadMapRules() {
  try {
    const res = await fetch("./local-map-rules.json");
    const baseRules = await res.json();
    const savedCustom = localStorage.getItem(CUSTOM_RULES_KEY);
    if (savedCustom) {
      const customRules = JSON.parse(savedCustom);
      baseRules.addressRules = customRules;
    }
    state.mapRules = baseRules;
  } catch (err) {
    console.error("Failed to load local-map-rules.json:", err);
  }
}

function loadPersistedSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      const { geminiKey, grokKey } = resolveApiKeys(parsed);
      state.settings = {
        ...state.settings,
        ...parsed,
        geminiApiKey: geminiKey,
        grokApiKey: grokKey,
        apiKey: geminiKey
      };
    }
  } catch (_) {}
}

function saveSettings() {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(state.settings));
}

function loadPersistedShiftState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      state.tickets = (Array.isArray(parsed.tickets) ? parsed.tickets : []).map((t) => {
        if (!t.status || !TICKET_STATUSES.includes(t.status)) {
          t.status = t.status === "End Delivery" ? "Delivered" : "On Order";
        }
        return t;
      });
      state.ignoredTickets = Array.isArray(parsed.ignoredTickets) ? parsed.ignoredTickets : [];
      state.trainContingencyActive = Boolean(parsed.trainContingencyActive);
      if (parsed.shift) state.shift = { ...state.shift, ...parsed.shift };
      sortActiveTickets();
    }
  } catch (_) {}
}

function saveShiftState() {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      tickets: state.tickets,
      ignoredTickets: state.ignoredTickets,
      trainContingencyActive: state.trainContingencyActive,
      shift: state.shift
    })
  );
}

function bindEvents() {
  // Camera / File upload
  const fileInput = document.getElementById("ticketPhotoInput");
  fileInput?.addEventListener("change", async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await handlePhotoUpload(file);
    fileInput.value = "";
  });

  // Train Contingency Toggle
  document.getElementById("btnTrainToggle")?.addEventListener("click", () => {
    state.trainContingencyActive = !state.trainContingencyActive;
    sortActiveTickets();
    saveShiftState();
    renderAll();
  });

  // Queue Checked Tickets for Multi-Run
  document.getElementById("btnQueueSelectedRun")?.addEventListener("click", () => {
    let count = 0;
    state.tickets.forEach((t) => {
      if (t.selectedForRun && t.status !== "Delivered") {
        if (t.status === "On Order") {
          t.status = "Queued for multi-run";
        }
        count++;
      }
    });
    if (count === 0) {
      alert("Check at least one ticket checkbox first.");
      return;
    }
    sortActiveTickets();
    saveShiftState();
    renderAll();
  });

  // Launch Multi-Stop Google Maps Run
  document.getElementById("btnLaunchMultiRunNav")?.addEventListener("click", () => {
    const url = buildMultiStopNavigationUrl();
    if (!url) {
      alert("Check 1 or more tickets to include in the navigation run.");
      return;
    }
    window.open(url, "_blank", "noopener");
  });

  // Post-Rush Review Quick Modal / Form
  document.getElementById("btnOpenPostRushForm")?.addEventListener("click", () => {
    openPostRushModal("");
  });

  document.getElementById("btnSavePostRushNote")?.addEventListener("click", () => {
    savePostRushNoteFromModal();
  });

  document.getElementById("btnCancelPostRushModal")?.addEventListener("click", () => {
    document.getElementById("postRushModal")?.classList.add("hidden");
  });

  const updateKeyDiagnostics = () => {
    const diagEl = document.getElementById("keyDiagnosticStatus");
    if (!diagEl) return;
    const gVal = document.getElementById("settingGeminiApiKey")?.value.trim() || "";
    const xVal = document.getElementById("settingGrokApiKey")?.value.trim() || "";
    const { geminiKey, grokKey } = resolveApiKeys({ geminiApiKey: gVal, grokApiKey: xVal });
    const gStatus = geminiKey
      ? `✅ Google Key: ${geminiKey.slice(0, 6)}... (${geminiKey.length} chars)`
      : "⚠️ Google Key: empty";
    let xStatus = "⚠️ xAI Key: empty";
    if (isUuidKeyId(xVal)) {
      xStatus = "❌ xAI box has the Table Row ID (c8eb460f...), not the secret 'xai-...' key";
    } else if (grokKey) {
      xStatus = `✅ xAI Key: ${grokKey.slice(0, 6)}... (${grokKey.length} chars)`;
    }
    diagEl.textContent = `${gStatus}  |  ${xStatus}`;
  };

  // Settings Modal
  document.getElementById("btnOpenSettings")?.addEventListener("click", () => {
    const { geminiKey, grokKey } = resolveApiKeys(state.settings);
    document.getElementById("settingProvider").value = state.settings.visionProvider;
    document.getElementById("settingGeminiApiKey").value = geminiKey;
    document.getElementById("settingGrokApiKey").value = grokKey;
    document.getElementById("settingEncouragementOnly").checked = state.settings.encouragementOnlyTips;
    document.getElementById("settingUploadFromGallery").checked = Boolean(state.settings.uploadFromGallery);
    updateKeyDiagnostics();
    document.getElementById("settingsModal")?.classList.remove("hidden");
  });

  document.getElementById("settingGeminiApiKey")?.addEventListener("input", updateKeyDiagnostics);
  document.getElementById("settingGrokApiKey")?.addEventListener("input", updateKeyDiagnostics);

  document.getElementById("btnSaveSettings")?.addEventListener("click", () => {
    const rawGem = document.getElementById("settingGeminiApiKey").value.trim();
    const rawGrok = document.getElementById("settingGrokApiKey").value.trim();
    const { geminiKey, grokKey } = resolveApiKeys({ geminiApiKey: rawGem, grokApiKey: rawGrok });
    state.settings.visionProvider = document.getElementById("settingProvider").value;
    state.settings.geminiApiKey = geminiKey;
    state.settings.grokApiKey = grokKey;
    state.settings.apiKey = geminiKey;
    state.settings.encouragementOnlyTips = document.getElementById("settingEncouragementOnly").checked;
    state.settings.uploadFromGallery = document.getElementById("settingUploadFromGallery").checked;
    saveSettings();
    document.getElementById("settingsModal")?.classList.add("hidden");
    renderAll();
  });

  document.getElementById("btnCloseSettings")?.addEventListener("click", () => {
    document.getElementById("settingsModal")?.classList.add("hidden");
  });

  // History Modal
  const openHistoryModal = () => {
    document.getElementById("settingsModal")?.classList.add("hidden");
    renderHistoryModal();
    document.getElementById("historyModal")?.classList.remove("hidden");
    document.getElementById("historySearchInput")?.focus();
  };

  document.getElementById("btnOpenHistory")?.addEventListener("click", openHistoryModal);
  document.getElementById("btnOpenHistoryFromSettings")?.addEventListener("click", openHistoryModal);
  document.getElementById("btnCloseHistory")?.addEventListener("click", () => {
    document.getElementById("historyModal")?.classList.add("hidden");
  });
  document.getElementById("btnExportHistoryJson")?.addEventListener("click", exportHistoryJson);
  document.getElementById("historyImportInput")?.addEventListener("change", async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await importHistoryJson(file);
    e.target.value = "";
  });
  document.getElementById("btnReminderStartShift")?.addEventListener("click", () => {
    document.getElementById("shiftStartPhotoInput")?.click();
  });
  document.getElementById("btnDismissStartShiftReminder")?.addEventListener("click", () => {
    document.getElementById("startShiftReminderBanner")?.classList.add("hidden");
  });
  document.getElementById("historySearchInput")?.addEventListener("input", renderHistoryModal);
  document.getElementById("historyDateFilter")?.addEventListener("change", renderHistoryModal);

  // Start Shift & End Shift Odometer Photo Inputs
  document.getElementById("shiftStartPhotoInput")?.addEventListener("change", async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await handleOdometerPhotoUpload(file, "start");
    e.target.value = "";
  });

  document.getElementById("shiftEndPhotoInput")?.addEventListener("change", async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!confirm("Confirm End Shift? This will record your ending odometer photo and archive tonight's orders into History.")) {
      e.target.value = "";
      return;
    }
    await handleOdometerPhotoUpload(file, "end");
    e.target.value = "";
  });

  // Full Ticket Editor Modal
  document.getElementById("btnCancelEditTicket")?.addEventListener("click", () => {
    document.getElementById("editTicketModal")?.classList.add("hidden");
  });
  document.getElementById("btnSaveEditTicket")?.addEventListener("click", saveEditTicketModal);

  // Odometer Photo Viewer Modal
  document.getElementById("btnCloseOdoViewer")?.addEventListener("click", () => {
    document.getElementById("odoViewerModal")?.classList.add("hidden");
  });

  document.getElementById("btnSaveOdoViewer")?.addEventListener("click", () => {
    const modal = document.getElementById("odoViewerModal");
    const mode = modal?.dataset.odoMode || "start";
    const val = document.getElementById("odoViewerInput")?.value.trim() || "";
    if (mode === "start") {
      state.shift.odometerStart = val;
    } else {
      state.shift.odometerEnd = val;
    }
    saveShiftState();
    renderLedger();
    modal?.classList.add("hidden");
  });

  // Odometer inputs
  document.getElementById("odoStart")?.addEventListener("input", (e) => {
    state.shift.odometerStart = e.target.value;
    saveShiftState();
    renderLedger();
  });

  document.getElementById("odoEnd")?.addEventListener("input", (e) => {
    state.shift.odometerEnd = e.target.value;
    saveShiftState();
    renderLedger();
  });

  // Export JSON & CSV
  document.getElementById("btnExportJson")?.addEventListener("click", exportShiftJson);
  document.getElementById("btnExportCsv")?.addEventListener("click", exportShiftCsv);
  document.getElementById("btnClearShift")?.addEventListener("click", () => {
    if (confirm("Reset shift? This clears active tickets, odometer photos, and tonight's mileage (permanent History & Customers are kept).")) {
      state.tickets = [];
      state.ignoredTickets = [];
      state.shift = {
        date: new Date().toISOString().slice(0, 10),
        odometerStart: "",
        odometerEnd: "",
        startedAt: null,
        endedAt: null,
        startOdoPhoto: null,
        endOdoPhoto: null
      };
      document.getElementById("startShiftReminderBanner")?.classList.add("hidden");
      saveShiftState();
      renderAll();
    }
  });

  // Local Map Rules Add / Edit / Export / Reset
  document.getElementById("btnAddMapRule")?.addEventListener("click", () => openMapRuleModal(-1));
  document.getElementById("btnCancelMapRule")?.addEventListener("click", () => {
    document.getElementById("mapRuleModal")?.classList.add("hidden");
  });
  document.getElementById("btnSaveMapRule")?.addEventListener("click", saveMapRuleModal);
  document.getElementById("btnExportMapRules")?.addEventListener("click", exportMapRulesJson);
  document.getElementById("btnResetMapRules")?.addEventListener("click", async () => {
    if (!confirm("Reset Local Map Rules on this device back to the default local-map-rules.json?")) return;
    localStorage.removeItem(CUSTOM_RULES_KEY);
    await loadMapRules();
    renderAll();
  });
  document.getElementById("btnRuleUseCurrentGps")?.addEventListener("click", () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported on this browser.");
      return;
    }
    const btn = document.getElementById("btnRuleUseCurrentGps");
    const origText = btn.textContent;
    btn.textContent = "📡 Getting current GPS...";
    btn.disabled = true;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        document.getElementById("ruleCustomLat").value = pos.coords.latitude.toFixed(5);
        document.getElementById("ruleCustomLng").value = pos.coords.longitude.toFixed(5);
        document.getElementById("ruleSnapPolicy").value = "CUSTOM_PIN";
        btn.textContent = origText;
        btn.disabled = false;
      },
      (err) => {
        alert(`Could not read GPS: ${err.message}`);
        btn.textContent = origText;
        btn.disabled = false;
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  });
}

function openOdometerViewer(mode) {
  const modal = document.getElementById("odoViewerModal");
  const titleEl = document.getElementById("odoViewerTitle");
  const imgEl = document.getElementById("odoViewerImg");
  const inpEl = document.getElementById("odoViewerInput");
  if (!modal || !imgEl || !inpEl) return;

  modal.dataset.odoMode = mode;
  if (mode === "start") {
    titleEl.textContent = "🚗 Shift Start Odometer Photo";
    imgEl.src = state.shift.startOdoPhoto || "";
    inpEl.value = state.shift.odometerStart || "";
  } else {
    titleEl.textContent = "🏁 Shift End Odometer Photo";
    imgEl.src = state.shift.endOdoPhoto || "";
    inpEl.value = state.shift.odometerEnd || "";
  }
  modal.classList.remove("hidden");
  inpEl.focus();
}

function openEditTicketModal(ticketId) {
  const t = state.tickets.find((x) => x.id === ticketId);
  const modal = document.getElementById("editTicketModal");
  if (!t || !modal) return;

  modal.dataset.ticketId = t.id;
  const imgEl = document.getElementById("editTicketPhotoPreview");
  if (imgEl) {
    if (t.previewUrl) {
      imgEl.src = t.previewUrl;
      imgEl.classList.remove("hidden");
    } else {
      imgEl.classList.add("hidden");
    }
  }

  document.getElementById("editOrderNumber").value = t.orderNumber || "";
  document.getElementById("editCustomerPhone").value = t.customerPhone || "";
  document.getElementById("editCustomerName").value = t.customerName || "";
  document.getElementById("editStreetAddress").value = t.address?.rawStreet || "";
  document.getElementById("editSpecialInstructions").value = t.specialInstructions || "None";
  document.getElementById("editPaymentStatus").value = t.payment?.status || "PAID_ONLINE";
  document.getElementById("editAmountDue").value = Number(t.payment?.amountDue || 0).toFixed(2);
  document.getElementById("editDeliveryFee").value = Number(t.deliveryFee?.chargedAmount || 3.0).toFixed(2);
  document.getElementById("editOnlineTip").value = Number(t.payment?.onlineTip || 0).toFixed(2);

  document.getElementById("editPizzasText").value = (t.orderSummary?.pizzas || [])
    .map((p) => `${p.qty || 1}x ${p.size || ""} ${p.crust || ""} ${p.name || ""}`.replace(/\s+/g, " ").trim())
    .join("\n");

  document.getElementById("editOtherItemsText").value = (t.orderSummary?.otherItems || [])
    .map((it) => `${it.qty || 1}x ${it.name || ""}`.replace(/\s+/g, " ").trim())
    .join("\n");

  modal.classList.remove("hidden");
  document.getElementById("editOrderNumber")?.focus();
}

function saveEditTicketModal() {
  const modal = document.getElementById("editTicketModal");
  const ticketId = modal?.dataset.ticketId;
  const t = state.tickets.find((x) => x.id === ticketId);
  if (!t) return;

  const newOrderNum = document.getElementById("editOrderNumber").value.trim().replace(/^#/, "") || t.orderNumber;
  t.orderNumber = newOrderNum;
  t.customerPhone = document.getElementById("editCustomerPhone").value.trim();
  t.customerName = document.getElementById("editCustomerName").value.trim() || "Valued Customer";

  const newStreet = document.getElementById("editStreetAddress").value.trim() || t.address?.rawStreet || "";
  const city = t.address?.city || state.mapRules?.defaultCity || "Conrad";
  const st = t.address?.state || state.mapRules?.defaultState || "MT";
  const zip = t.address?.zip || state.mapRules?.defaultZip || "59425";
  t.address = {
    ...t.address,
    rawStreet: newStreet,
    normalizedKey: newStreet.toUpperCase().replace(/[.,#]/g, "").replace(/\s+/g, " ").trim(),
    fullFormatted: `${newStreet}, ${city}, ${st} ${zip}`
  };

  const instr = document.getElementById("editSpecialInstructions").value.trim();
  t.specialInstructions = instr || "None";
  t.allowAlleyAccess = /\b(alley|back|rear)\b/i.test(t.specialInstructions);

  const payStatus = document.getElementById("editPaymentStatus").value;
  const amtDue = payStatus === "PAID_ONLINE" ? 0.0 : Number(document.getElementById("editAmountDue").value || 0);
  const tip = Number(document.getElementById("editOnlineTip").value || 0);
  t.payment = {
    ...t.payment,
    status: payStatus,
    amountDue: amtDue,
    onlineTip: tip,
    displayBanner:
      payStatus === "PAID_ONLINE"
        ? "CC (Paid Online) — $0.00 Due"
        : `COLLECT PAYMENT (Cash or In-Person CC) — $${amtDue.toFixed(2)} Due`
  };

  const fee = Math.max(0, Number(document.getElementById("editDeliveryFee").value || 3.0));
  t.deliveryFee.chargedAmount = fee;
  t.deliveryFee.extraOverStandard = Math.max(0, Number((fee - 3.0).toFixed(2)));
  t.financials.driverDeliveryFeeEarned = fee;
  t.financials.onlineTip = tip;

  const pizzaLines = document
    .getElementById("editPizzasText")
    .value.split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
  t.orderSummary.pizzas = pizzaLines.map((line) => {
    const m = line.match(/^(\d+)\s*x\s+(.*)$/i);
    return {
      qty: m ? Number(m[1]) : 1,
      size: "",
      crust: "Edited",
      name: m ? m[2].trim() : line,
      optionsLines: []
    };
  });
  t.orderSummary.pizzaCount = t.orderSummary.pizzas.reduce((s, p) => s + Number(p.qty || 1), 0);

  const otherLines = document
    .getElementById("editOtherItemsText")
    .value.split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
  t.orderSummary.otherItems = otherLines.map((line) => {
    const m = line.match(/^(\d+)\s*x\s+(.*)$/i);
    return {
      qty: m ? Number(m[1]) : 1,
      name: m ? m[2].trim() : line,
      modifierLines: []
    };
  });
  t.orderSummary.otherItemCount = t.orderSummary.otherItems.reduce((s, it) => s + Number(it.qty || 1), 0);

  // Clear or update invalid Order # warning based on >= 2000 rule
  t.specialAlerts = (t.specialAlerts || []).filter((al) => !al.isOrderNumWarning);
  if (!isValidShift4OrderNumber(t.orderNumber)) {
    t.specialAlerts.unshift({
      category: "SOUP_SALAD_DRINK",
      isOrderNumWarning: true,
      bannerText: `INVALID ORDER # (#${t.orderNumber}) — Expected #2000+. Ticket clipped on board? Re-snap or tap ✏️ Edit!`
    });
  }

  saveShiftState();
  renderAll();
  modal.classList.add("hidden");
}

async function handleOdometerPhotoUpload(file, mode) {
  const statusEl = document.getElementById("ocrStatusBanner");
  try {
    statusEl.className = "ocr-status active";
    const result = await extractOdometerFromPhoto(file, state.settings, (msg) => {
      statusEl.textContent = msg;
    });
    if (mode === "start") {
      state.shift.startedAt = result.timestamp;
      state.shift.startOdoPhoto = result.previewUrl;
      if (result.odometerReading) {
        state.shift.odometerStart = String(result.odometerReading);
      }
      statusEl.textContent = result.odometerReading
        ? `✅ Shift Started! Odometer read as ${result.odometerReading} mi (via ${result.modelName}).`
        : "📸 Start odometer photo saved — view photo to enter mileage.";
    } else {
      state.shift.endedAt = result.timestamp;
      state.shift.endOdoPhoto = result.previewUrl;
      if (result.odometerReading) {
        state.shift.odometerEnd = String(result.odometerReading);
      }
      statusEl.textContent = result.odometerReading
        ? `🏁 Shift Ended! Odometer read as ${result.odometerReading} mi (via ${result.modelName}).`
        : "📸 End odometer photo saved — view photo to enter mileage.";
    }
    statusEl.className = "ocr-status success";
    saveShiftState();
    renderLedger();

    // If OCR could not auto-read the digits, automatically pop open the full-size photo viewer + input
    if (!result.odometerReading) {
      openOdometerViewer(mode);
    }
  } catch (err) {
    statusEl.textContent = `⚠️ Odometer photo error: ${err.message}`;
    statusEl.className = "ocr-status error";
  }
}

async function handlePhotoUpload(file) {
  const statusEl = document.getElementById("ocrStatusBanner");
  try {
    statusEl.textContent = "📸 Compressing ticket photo...";
    statusEl.className = "ocr-status active";
    const parsedBatch = await extractTicketsFromPhoto(
      file,
      state.settings,
      state.mapRules,
      (progressMsg) => {
        statusEl.textContent = progressMsg;
      }
    );
    const summary = ingestParsedBatch(parsedBatch);
    const winningModel = parsedBatch[0]?.parsedByModel || "Vision API";
    const failover = parsedBatch[0]?.failoverNotice;
    const parts = [`✅ Added ${summary.addedCount} new ticket(s)`];
    if (summary.skippedDuplicates.length > 0) {
      parts.push(`skipped ${summary.skippedDuplicates.length} active duplicate(s) (#${summary.skippedDuplicates.join(", #")})`);
    }
    if (summary.diffWarnings.length > 0) {
      parts.push(`⚠️ detail diff flagged on #${summary.diffWarnings.join(", #")}`);
    }
    if (failover) {
      parts.push(`(Failover note: ${failover})`);
    }
    statusEl.textContent = `${parts.join(" • ")} [${winningModel}].`;
    statusEl.className = "ocr-status success";

    if (!state.shift.startedAt && !state.shift.odometerStart && !state.shift.startOdoPhoto) {
      document.getElementById("startShiftReminderBanner")?.classList.remove("hidden");
    }
  } catch (err) {
    statusEl.textContent = `⚠️ ${err.message}`;
    statusEl.className = "ocr-status error";
  }
}

function normalizeNameForCompare(name) {
  return String(name || "")
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "");
}

function compareAndMergeRescanDetails(existing, incoming) {
  const diffs = [];

  const exName = normalizeNameForCompare(existing.customerName);
  const inName = normalizeNameForCompare(incoming.customerName);
  if (exName && inName && exName !== inName) {
    diffs.push(`Customer Name ("${existing.customerName}" vs "${incoming.customerName}")`);
  }

  const exAddr = String(existing.address?.normalizedKey || "");
  const inAddr = String(incoming.address?.normalizedKey || "");
  if (exAddr && inAddr && exAddr !== inAddr) {
    diffs.push(`Address ("${existing.address?.rawStreet}" vs "${incoming.address?.rawStreet}")`);
  }

  if (existing.orderSummary?.pizzaCount !== incoming.orderSummary?.pizzaCount) {
    diffs.push(`Pizza count (${existing.orderSummary?.pizzaCount} vs ${incoming.orderSummary?.pizzaCount})`);
  }

  if (existing.orderSummary?.otherItemCount !== incoming.orderSummary?.otherItemCount) {
    diffs.push(`Other items count (${existing.orderSummary?.otherItemCount} vs ${incoming.orderSummary?.otherItemCount})`);
  }

  const exDue = Number(existing.payment?.amountDue || 0).toFixed(2);
  const inDue = Number(incoming.payment?.amountDue || 0).toFixed(2);
  if (exDue !== inDue || existing.payment?.status !== incoming.payment?.status) {
    diffs.push(`Payment (${existing.payment?.displayBanner} vs ${incoming.payment?.displayBanner})`);
  }

  // Merge any newly discovered special alerts from the re-scan
  const existingAlertSet = new Set(
    (existing.specialAlerts || []).map((a) => `${a.category}::${a.bannerText.toUpperCase()}`)
  );
  for (const al of incoming.specialAlerts || []) {
    const key = `${al.category}::${al.bannerText.toUpperCase()}`;
    if (!existingAlertSet.has(key)) {
      existing.specialAlerts.push(al);
      diffs.push(`Added missed alert "${al.bannerText}"`);
    }
  }

  return diffs;
}

function ingestParsedBatch(batch) {
  let addedCount = 0;
  const skippedDuplicates = [];
  const diffWarnings = [];

  for (const item of batch) {
    if (!item.isDelivery) {
      const alreadyIgnored = state.ignoredTickets.some((ig) => ig.orderNumber === item.orderNumber);
      if (!alreadyIgnored) {
        state.ignoredTickets.unshift(item);
      }
      continue;
    }

    // Active tickets are any with status other than "Delivered" or "Issue/Redelivery"
    const activeMatch = state.tickets.find((t) => {
      if (t.status === "Delivered" || t.status === "Issue/Redelivery") return false;
      const sameOrder = String(t.orderNumber) === String(item.orderNumber);
      const sameName =
        normalizeNameForCompare(t.customerName) !== "" &&
        normalizeNameForCompare(t.customerName) === normalizeNameForCompare(item.customerName);
      return sameOrder || (sameName && t.address?.normalizedKey === item.address?.normalizedKey);
    });

    if (activeMatch) {
      skippedDuplicates.push(activeMatch.orderNumber);
      const diffs = compareAndMergeRescanDetails(activeMatch, item);
      if (diffs.length > 0) {
        activeMatch.rescanDiffNotice = `⚠️ Re-Scan Double-Check: ${diffs.join(" • ")}`;
        diffWarnings.push(activeMatch.orderNumber);
      }
      continue;
    }

    // Enrich with permanent customer profile (keyed by customerName + customerPhone)
    enrichTicketFromCustomerDb(item);
    state.tickets.push(item);
    addedCount++;
  }

  sortActiveTickets();
  saveShiftState();
  renderAll();
  return { addedCount, skippedDuplicates, diffWarnings };
}

function getCustomerProfileKey(customerName, customerPhone, fallbackAddrKey = "") {
  const normName = normalizeNameForCompare(customerName) || "CUSTOMER";
  const normPhone = String(customerPhone || "").replace(/[^0-9]/g, "");
  if (normPhone.length >= 7) {
    return `${normName}::${normPhone.slice(-10)}`;
  }
  return `${normName}::${String(fallbackAddrKey || "CONRAD").replace(/\s+/g, "_")}`;
}

function enrichTicketFromCustomerDb(ticket) {
  const key = getCustomerProfileKey(ticket.customerName, ticket.customerPhone, ticket.address?.normalizedKey);
  const profile = state.customers[key];
  if (!profile) return;
  ticket.customerProfileKey = key;
  ticket.customerRepeatCount = profile.deliveryCount || 0;
  if (profile.generousTipCount > 0 && ticket.routing) {
    ticket.routing.tipHistory = {
      ...(ticket.routing.tipHistory || {}),
      generousRegular: true
    };
  }
}

function recordCustomerAndHistoryOnDelivery(ticket) {
  const key = getCustomerProfileKey(ticket.customerName, ticket.customerPhone, ticket.address?.normalizedKey);
  const nowIso = new Date().toISOString();
  const existing = state.customers[key] || {
    key,
    customerName: ticket.customerName,
    customerPhone: ticket.customerPhone || "",
    deliveryCount: 0,
    generousTipCount: 0,
    addressesVisited: [],
    lastSpecialInstructions: "None",
    lastDeliveredAt: null
  };

  existing.customerName = ticket.customerName || existing.customerName;
  if (ticket.customerPhone) existing.customerPhone = ticket.customerPhone;
  existing.deliveryCount = (existing.deliveryCount || 0) + 1;

  const generousThreshold = state.mapRules?.deliveryFeePolicy?.generousTipEncouragementThreshold || 5.0;
  if (Number(ticket.payment?.onlineTip || 0) >= generousThreshold) {
    existing.generousTipCount = (existing.generousTipCount || 0) + 1;
  }

  const addrStr = ticket.address?.rawStreet || "";
  if (addrStr && !existing.addressesVisited.includes(addrStr)) {
    existing.addressesVisited.push(addrStr);
  }
  if (ticket.specialInstructions && ticket.specialInstructions !== "None") {
    existing.lastSpecialInstructions = ticket.specialInstructions;
  }
  existing.lastDeliveredAt = nowIso;
  state.customers[key] = existing;

  // Upsert into permanent delivery history
  const shiftDate = state.shift.date || nowIso.slice(0, 10);
  const histEntry = {
    ...JSON.parse(JSON.stringify(ticket)),
    shiftDate,
    customerProfileKey: key
  };
  const idx = state.history.findIndex((h) => h.id === ticket.id);
  if (idx !== -1) {
    state.history[idx] = histEntry;
  } else {
    state.history.unshift(histEntry);
  }

  savePermanentCustomerAndHistoryDb();
}

const STATUS_PRIORITY_RANK = {
  "Issue/Redelivery": 1,
  "Start Delivery": 2,
  "Queued for multi-run": 3,
  "On Order": 4,
  "Delivered": 5
};

/**
 * Auto-sorts active tickets by status priority so what you are focused on is always at the top.
 * Within the same status, respects Train Contingency shop-side ordering if active.
 */
function sortActiveTickets() {
  state.tickets.sort((a, b) => {
    const rankA = STATUS_PRIORITY_RANK[a.status] ?? 4;
    const rankB = STATUS_PRIORITY_RANK[b.status] ?? 4;
    if (rankA !== rankB) return rankA - rankB;

    if (state.trainContingencyActive) {
      const aSide = a.routing?.trackSide === "ACROSS_TRACKS" ? 1 : 0;
      const bSide = b.routing?.trackSide === "ACROSS_TRACKS" ? 1 : 0;
      if (aSide !== bSide) return aSide - bSide;
    }
    return 0;
  });
}

function applyTrainTrackContingencyOrdering() {
  sortActiveTickets();
}

function getShopOriginParam() {
  const shopName = state.mapRules?.shop?.name || "Coaches Corner Pizza Inc";
  const shopAddr = state.mapRules?.shop?.address || "608 S Front St, Conrad, MT 59425";
  return encodeURIComponent(`${shopName}, ${shopAddr}`);
}

/**
 * Builds a single-stop Google Maps navigation URL using exact front-curb / custom pin coordinates.
 * Never injects synthetic pass-through coordinates into &waypoints= because Google Maps treats every waypoint as an extra delivery stop.
 */
function buildSingleStopNavUrl(ticket) {
  const originStr = getShopOriginParam();
  let destStr;
  if (ticket.routing?.destinationPin) {
    destStr = `${ticket.routing.destinationPin.lat},${ticket.routing.destinationPin.lng}`;
  } else {
    destStr = encodeURIComponent(ticket.address.fullFormatted);
  }

  return `https://www.google.com/maps/dir/?api=1&origin=${originStr}&destination=${destStr}&travelmode=driving`;
}

/**
 * Builds a multi-stop Google Maps deep link containing ONLY the checked delivery tickets in current card order.
 */
function buildMultiStopNavigationUrl() {
  const selected = state.tickets.filter((t) => t.selectedForRun && t.status !== "Delivered");
  if (selected.length === 0) return null;
  if (selected.length === 1) return buildSingleStopNavUrl(selected[0]);

  const originStr = getShopOriginParam();
  const waypoints = [];

  selected.slice(0, -1).forEach((t) => {
    if (t.routing?.destinationPin) {
      waypoints.push(`${t.routing.destinationPin.lat},${t.routing.destinationPin.lng}`);
    } else {
      waypoints.push(encodeURIComponent(t.address.fullFormatted));
    }
  });

  const last = selected[selected.length - 1];
  const destStr = last.routing?.destinationPin
    ? `${last.routing.destinationPin.lat},${last.routing.destinationPin.lng}`
    : encodeURIComponent(last.address.fullFormatted);

  const wpParam = waypoints.length > 0 ? `&waypoints=${waypoints.join("|")}` : "";
  return `https://www.google.com/maps/dir/?api=1&origin=${originStr}${wpParam}&destination=${destStr}&travelmode=driving`;
}

/**
 * Status Progression Handler with Tamarack SMS Gate & Automatic Drive Time Calculation
 */
function updateTicketStatus(ticketId, nextStatus) {
  const ticket = state.tickets.find((t) => t.id === ticketId);
  if (!ticket) return;

  // Enforce Tamarack Apartments pre-departure SMS gate before starting delivery
  if (
    nextStatus === "Start Delivery" &&
    ticket.routing?.requireSmsBeforeStart &&
    !ticket.smsPreDepartureSent
  ) {
    alert("🔒 Locked Building Rule: Tap the 'Text Customer Before Leaving Shop' button first so the customer meets you at the entry.");
    return;
  }

  const nowIso = new Date().toISOString();
  ticket.status = nextStatus || "On Order";

  if (ticket.status === "Queued for multi-run") {
    ticket.selectedForRun = true;
  } else if (ticket.status === "On Order") {
    ticket.selectedForRun = false;
  } else if (ticket.status === "Start Delivery") {
    ticket.metrics.startDeliveryAt = nowIso;
    ticket.selectedForRun = true;
  } else if (ticket.status === "Delivered") {
    ticket.metrics.deliveredAt = nowIso;
    ticket.metrics.endDeliveryAt = nowIso;
    if (ticket.metrics.startDeliveryAt && !ticket.metrics.driveTimeMinutes) {
      const diffMs = new Date(nowIso) - new Date(ticket.metrics.startDeliveryAt);
      const mins = Math.max(1, Math.round((diffMs / 60000) * 10) / 10);
      ticket.metrics.driveTimeMinutes = mins;
    }
    const normalMins = state.mapRules?.deliveryFeePolicy?.normalDriveMinutes || 7;
    if ((ticket.metrics.driveTimeMinutes || 0) > normalMins && ticket.deliveryFee.chargedAmount <= 3.0) {
      ticket.deliveryFee.underchargedWarning = true;
    }
    if (ticket.payment.status === "COLLECT" && ticket.financials.cashCollected === 0) {
      ticket.financials.cashCollected = ticket.payment.amountDue;
    }
    ticket.selectedForRun = false;
    recordCustomerAndHistoryOnDelivery(ticket);
  }

  sortActiveTickets();
  saveShiftState();
  renderAll();
}

function openPostRushModal(orderNumber = "") {
  const modal = document.getElementById("postRushModal");
  const orderInput = document.getElementById("postRushOrderNum");
  const noteInput = document.getElementById("postRushNoteInput");

  const existing = state.tickets.find((t) => t.orderNumber === String(orderNumber));
  orderInput.value = orderNumber;
  if (existing?.postRushReview?.note) {
    noteInput.value = existing.postRushReview.note;
  } else if (existing && existing.deliveryFee.chargedAmount <= 3.0) {
    noteInput.value = `Far run (${existing.metrics.driveTimeMinutes || "?"}m / ${existing.metrics.mileageMiles || "?"} mi) at $3.00 fee — consider +$2 fee & extra ETA next time so we underpromise and overdeliver.`;
  } else {
    noteInput.value = "";
  }
  modal.classList.remove("hidden");
  noteInput.focus();
}

function savePostRushNoteFromModal() {
  const orderNum = document.getElementById("postRushOrderNum").value.trim().replace(/^#/, "");
  const note = document.getElementById("postRushNoteInput").value.trim();
  if (!orderNum || !note) {
    alert("Enter both the Order # and a short note for post-rush review.");
    return;
  }

  const ticket = state.tickets.find((t) => t.orderNumber === orderNum);
  if (ticket) {
    ticket.postRushReview = {
      flagged: true,
      orderNumber: orderNum,
      note,
      flaggedAt: new Date().toISOString()
    };
  } else {
    // Allow flagging an order number even if ticket wasn't scanned yet
    state.tickets.push({
      id: `tkt_manual_${Date.now()}`,
      orderNumber: orderNum,
      isDelivery: true,
      customerName: "Manual Post-Rush Flag",
      address: {
        rawStreet: "See Ticket",
        fullFormatted: "Conrad, MT 59425"
      },
      specialInstructions: "None",
      allowAlleyAccess: false,
      routing: { trackSide: "SHOP_SIDE", snapMode: "FRONT_CURB" },
      payment: { status: "PAID_ONLINE", amountDue: 0, onlineTip: 0, displayBanner: "Manual Entry" },
      deliveryFee: { chargedAmount: 3.0, standardBase: 3.0, extraOverStandard: 0, underchargedWarning: true },
      orderSummary: { pizzaCount: 0, pizzas: [], otherItemCount: 0, otherItems: [] },
      specialAlerts: [],
      status: "Delivered",
      selectedForRun: false,
      metrics: { mileageMiles: null, driveTimeMinutes: null },
      postRushReview: { flagged: true, orderNumber: orderNum, note, flaggedAt: new Date().toISOString() },
      financials: { driverDeliveryFeeEarned: 3.0, cashCollected: 0, onlineTip: 0, cashTip: 0 }
    });
  }

  saveShiftState();
  document.getElementById("postRushModal")?.classList.add("hidden");
  renderAll();
}

function renderAll() {
  renderSnapTixButton();
  renderTrainBar();
  renderIgnoredTickets();
  renderDeliveryCards();
  renderAddressRulesPanel();
  renderLedger();
}

function renderSnapTixButton() {
  const input = document.getElementById("ticketPhotoInput");
  const startOdoInput = document.getElementById("shiftStartPhotoInput");
  const endOdoInput = document.getElementById("shiftEndPhotoInput");
  const reminderBtn = document.getElementById("btnReminderStartShift");
  const labelText = document.getElementById("snapTixBtnText");
  const labelWrap = document.getElementById("snapTixLabel");
  if (!input || !labelText) return;

  const photoInputs = [input, startOdoInput, endOdoInput].filter(Boolean);

  if (state.settings.uploadFromGallery) {
    photoInputs.forEach((el) => el.removeAttribute("capture"));
    labelText.textContent = "📁 Upload";
    if (labelWrap) labelWrap.title = "Upload ticket photo from gallery/files";
    if (reminderBtn) reminderBtn.textContent = "📁 Upload Odo";
  } else {
    photoInputs.forEach((el) => el.setAttribute("capture", "environment"));
    labelText.textContent = "📷 SnapTix";
    if (labelWrap) labelWrap.title = "Snap 1–4 Tickets";
    if (reminderBtn) reminderBtn.textContent = "📸 Snap Odo";
  }
}

function renderTrainBar() {
  const btn = document.getElementById("btnTrainToggle");
  const statusText = document.getElementById("trainStatusSubtext");
  if (!btn) return;

  const acrossCount = state.tickets.filter(
    (t) => t.status !== "Delivered" && t.routing?.trackSide === "ACROSS_TRACKS"
  ).length;

  if (state.trainContingencyActive) {
    btn.className = "btn-nav-train active";
    btn.textContent = "🚂 PivotON!";
    if (statusText) {
      statusText.textContent =
        acrossCount > 0
          ? `• 🚂 Shop-Side sorted first (${acrossCount} across tracks)`
          : "• 🚂 Pivot ON (All stops on Shop Side)";
    }
  } else {
    btn.className = "btn-nav-train";
    btn.textContent = "🚂 Train?Pivot!";
    if (statusText) {
      statusText.textContent =
        acrossCount > 0 ? `• (${acrossCount} across tracks)` : "";
    }
  }
}

function renderIgnoredTickets() {
  const container = document.getElementById("ignoredTicketsContainer");
  if (!container) return;
  if (state.ignoredTickets.length === 0) {
    container.innerHTML = "";
    return;
  }

  container.innerHTML = state.ignoredTickets
    .map(
      (ig) => `
      <div class="ignored-ticket-pill">
        <span>🚫 ${escapeHtml(ig.ignoredBanner)}</span>
        <button class="btn-dismiss-ignored" data-id="${ig.id}" title="Dismiss">✕</button>
      </div>`
    )
    .join("");

  container.querySelectorAll(".btn-dismiss-ignored").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.ignoredTickets = state.ignoredTickets.filter((i) => i.id !== btn.dataset.id);
      saveShiftState();
      renderIgnoredTickets();
    });
  });
}

function renderDeliveryCards() {
  const container = document.getElementById("cardsContainer");
  const selectedCountEl = document.getElementById("selectedRunCount");
  const historyCountEl = document.getElementById("deliveredHistoryCount");
  if (!container) return;

  const activeTickets = state.tickets.filter((t) => t.status !== "Delivered");
  const deliveredTonightCount = state.tickets.filter((t) => t.status === "Delivered").length;
  if (historyCountEl) {
    historyCountEl.textContent = String(Math.max(deliveredTonightCount, state.history.length));
  }

  const selectedCount = activeTickets.filter((t) => t.selectedForRun).length;
  if (selectedCountEl) selectedCountEl.textContent = String(selectedCount);

  if (activeTickets.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <p>${
          deliveredTonightCount > 0
            ? `All ${deliveredTonightCount} scanned order(s) tonight are delivered! Tap <strong>📷 SnapTix</strong> for new tickets or <strong>📜 History</strong> to view/search delivered orders.`
            : `Tap <strong>📷 SnapTix</strong> in the top bar to scan 1–4 POS tickets.`
        }</p>
      </div>`;
    return;
  }

  const generousThreshold = state.mapRules?.deliveryFeePolicy?.generousTipEncouragementThreshold || 5.0;

  container.innerHTML = activeTickets
    .map((t) => {
      const fullIndex = state.tickets.findIndex((x) => x.id === t.id);
      const currentStatus = t.status || "On Order";
      const statusSlug = currentStatus.toLowerCase().replace(/[^a-z]+/g, "-");
      const navUrl = buildSingleStopNavUrl(t);

      // 1. Special Alerts Banners with Dismiss (✕) button once verified
      const alertsHtml = (t.specialAlerts || [])
        .map((al, alIdx) => {
          if (al.dismissed) return "";
          const cls =
            al.category === "SOUP_SALAD_DRINK"
              ? "alert-banner alert-food-item"
              : al.category === "BUILDING_RULE"
              ? "alert-banner alert-building"
              : "alert-banner alert-modifier";
          return `
            <div class="${cls} dismissible-banner">
              <span>🚨 ${escapeHtml(al.bannerText)}</span>
              <button class="btn-dismiss-banner" data-action="dismiss-alert" data-id="${t.id}" data-alert-index="${alIdx}" title="Checked / Hide reminder">✕</button>
            </div>`;
        })
        .join("");

      // 2. Positive-Only Encouragement Tip Badge (Never displays $0 or discouraging badges)
      let tipBadgeHtml = "";
      const onlineTip = Number(t.payment?.onlineTip || 0);
      const isGenerousRegular = Boolean(t.routing?.tipHistory?.generousRegular);
      if (!t.tipBadgeDismissed) {
        if (onlineTip >= generousThreshold) {
          tipBadgeHtml = `
            <div class="encouragement-badge dismissible-banner">
              <span>🌟 Extra Service Blessing: $${onlineTip.toFixed(2)} Pre-Tip Included — Thank Customer Warmly!</span>
              <button class="btn-dismiss-banner" data-action="dismiss-tip-badge" data-id="${t.id}" title="Hide">✕</button>
            </div>`;
        } else if (isGenerousRegular) {
          tipBadgeHtml = `
            <div class="encouragement-badge dismissible-banner">
              <span>🌟 Valued Regular Supporter — Great Customer!</span>
              <button class="btn-dismiss-banner" data-action="dismiss-tip-badge" data-id="${t.id}" title="Hide">✕</button>
            </div>`;
        } else if (!state.settings.encouragementOnlyTips && onlineTip > 0) {
          tipBadgeHtml = `<div class="encouragement-badge subtle">Pre-Tip: $${onlineTip.toFixed(2)}</div>`;
        }
      }

      // 3. Surcharge Payout (> $3.00) vs Undercharged Extended Distance (NOT over $3.00)
      let feeBannerHtml = "";
      if (t.deliveryFee.chargedAmount > 3.0) {
        feeBannerHtml = `
          <div class="fee-banner extended-paid">
            💵 <strong>$${t.deliveryFee.chargedAmount.toFixed(2)} Delivery Charge</strong> (+$${t.deliveryFee.extraOverStandard.toFixed(2)} over standard $3.00 goes to you at closeout)
          </div>`;
      } else if (t.deliveryFee.underchargedWarning && !t.postRushReview?.flagged) {
        feeBannerHtml = `
          <div class="fee-banner undercharged-notice">
            💡 <strong>Extended Run at Standard $3.00 Fee</strong> — Consider flagging for Post-Rush Review so you & boss can adjust future fee/ETA.
          </div>`;
      }

      // 4. Tamarack Apartments Pre-Departure SMS Gate (Dismissible with ✕ after texting)
      let smsGateHtml = "";
      if (t.routing?.requireSmsBeforeStart && !t.smsBoxDismissed) {
        const phone = t.customerPhone || "";
        const body = encodeURIComponent(t.routing.smsTemplate || "Hi! Your Coach's Pizza driver is heading out now and will arrive in 5-7 mins!");
        const smsHref = `sms:${phone}?body=${body}`;
        smsGateHtml = `
          <div class="sms-gate-box ${t.smsPreDepartureSent ? "cleared" : "pending"} dismissible-banner">
            <a href="${smsHref}" class="btn-sms-gate" data-ticket-id="${t.id}">
              ${t.smsPreDepartureSent ? "✅ Pre-Departure Text Sent" : escapeHtml(t.routing.smsButtonLabel)}
            </a>
            ${
              t.smsPreDepartureSent
                ? `<button class="btn-dismiss-banner" data-action="dismiss-sms-box" data-id="${t.id}" title="Hide SMS box">✕</button>`
                : ""
            }
          </div>`;
      }

      // 5. Order Summary (Pizzas + Other Items)
      const pizzasListHtml = (t.orderSummary?.pizzas || [])
        .map(
          (p) =>
            `<li><strong>${p.qty}x ${escapeHtml(p.size)} ${escapeHtml(p.name)}</strong> (${escapeHtml(p.crust)})${
              p.optionsLines?.length ? ` — <span class="opt-highlight">${escapeHtml(p.optionsLines.join(", "))}</span>` : ""
            }</li>`
        )
        .join("");

      const otherListHtml = (t.orderSummary?.otherItems || [])
        .map(
          (it) =>
            `<li><strong>${it.qty}x ${escapeHtml(it.name)}</strong>${
              it.modifierLines?.length ? ` — <span class="opt-highlight">${escapeHtml(it.modifierLines.join(", "))}</span>` : ""
            }</li>`
        )
        .join("");

      // 6. Status Stepper Buttons
      const statusButtonsHtml = TICKET_STATUSES.map((st) => {
        const stSlug = st.toLowerCase().replace(/[^a-z]+/g, "-");
        const activeCls = currentStatus === st ? `status-pill active status-pill-${stSlug}` : `status-pill status-pill-${stSlug}`;
        return `<button class="${activeCls}" data-action="set-status" data-id="${t.id}" data-status="${st}">${escapeHtml(st)}</button>`;
      }).join("");

      return `
      <article class="delivery-card ${t.selectedForRun ? "selected-for-run" : ""} status-${statusSlug}">
        <header class="card-header status-header-${statusSlug}">
          <input type="checkbox" id="run-cb-${t.id}" class="run-checkbox" data-id="${t.id}" ${t.selectedForRun ? "checked" : ""}/>
          <label for="run-cb-${t.id}" class="order-badge status-badge-${statusSlug}">#${escapeHtml(t.orderNumber)} • ${escapeHtml(currentStatus)}</label>
          <button class="btn-icon btn-arrow-mini" data-action="move-up" data-index="${fullIndex}" title="Move stop earlier">▲</button>
          <button class="btn-icon btn-edit-mini" data-action="edit-ticket" data-id="${t.id}" title="Edit misread ticket details">✏️</button>
          <span class="customer-name">${escapeHtml(t.customerName)}${
            t.customerRepeatCount > 0 ? ` <small class="repeat-tag">(${t.customerRepeatCount + 1}x)</small>` : ""
          }</span>
          <button class="btn-icon btn-arrow-mini" data-action="move-down" data-index="${fullIndex}" title="Move stop later">▼</button>
        </header>

        ${
          t.rescanDiffNotice
            ? `<div class="alert-banner alert-modifier dismissible-banner">
                <span>${escapeHtml(t.rescanDiffNotice)}</span>
                <button class="btn-dismiss-banner" data-action="dismiss-rescan-diff" data-id="${t.id}" title="Dismiss">✕</button>
              </div>`
            : ""
        }
        ${alertsHtml}
        ${tipBadgeHtml}
        ${feeBannerHtml}

        <div class="address-routing-block">
          <div class="address-main">
            <a href="${navUrl}" target="_blank" rel="noopener" class="address-nav-link">
              📍 ${escapeHtml(t.address.rawStreet)}, ${escapeHtml(t.address.city)}, ${escapeHtml(t.address.state)} ${escapeHtml(t.address.zip)}
            </a>
            <span class="track-badge ${t.routing?.trackSide === "ACROSS_TRACKS" ? "across" : "shop-side"}">
              ${t.routing?.trackSide === "ACROSS_TRACKS" ? "⚠️ Across Tracks" : "✓ Shop Side"}
            </span>
          </div>
          <div class="special-instructions-line">
            <strong>Delivery Instructions:</strong>
            <span class="${t.specialInstructions !== "None" ? "highlight-instr" : ""}">${escapeHtml(t.specialInstructions)}</span>
          </div>
          <div class="routing-policy-line" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.4rem;">
            <div>
              <span>🧭 Pin Policy: <strong>${escapeHtml(t.routing?.snapMode || "FRONT_CURB")}</strong></span>
              ${
                t.routing?.approachWaypoint
                  ? `<span class="approach-chip">↪ Right-Side Curb Approach Active</span>`
                  : ""
              }
            </div>
            <button type="button" class="btn-secondary btn-nav-compact" data-action="save-map-rule-from-ticket" data-id="${t.id}" title="Save or edit Local Map Rule for this address">➕ Map Rule</button>
          </div>
          ${
            t.routing?.driverNotes?.parkingSpot
              ? `<div class="driver-note-line">🅿️ ${escapeHtml(t.routing.driverNotes.parkingSpot)}</div>`
              : ""
          }
        </div>

        ${smsGateHtml}

        <div class="payment-banner ${t.payment.status === "PAID_ONLINE" ? "paid-online" : "collect-due"}">
          <span>${escapeHtml(t.payment.displayBanner)}</span>
          <div class="fee-adjuster">
            <span>POS Deliv Fee: <strong>$${t.deliveryFee.chargedAmount.toFixed(2)}</strong></span>
          </div>
        </div>

        <div class="order-summary-rows">
          ${
            t.orderSummary.pizzaCount > 0
              ? `<div class="summary-row">
                  <h4>🍕 Pizzas (${t.orderSummary.pizzaCount})</h4>
                  <ul>${pizzasListHtml}</ul>
                </div>`
              : ""
          }
          ${
            t.orderSummary.otherItemCount > 0
              ? `<div class="summary-row">
                  <h4>🥗 Other Items (${t.orderSummary.otherItemCount})</h4>
                  <ul>${otherListHtml}</ul>
                </div>`
              : ""
          }
        </div>

        <div class="status-progression-bar">
          <div class="status-label-row">
            <span>Status: <strong>${escapeHtml(t.status)}</strong></span>
            <a href="${navUrl}" target="_blank" rel="noopener" class="btn-one-tap-nav">🗺️ Navigate Stop</a>
          </div>
          <div class="status-pills-wrap">
            ${statusButtonsHtml}
          </div>
        </div>

        <footer class="card-footer-metrics">
          <div class="metric-inputs">
            <label>
              ⏱️ Drive (min):
              <input type="number" step="0.5" min="0" class="input-metric" data-action="edit-drivetime" data-id="${t.id}" value="${t.metrics.driveTimeMinutes ?? ""}" placeholder="Auto"/>
            </label>
            <label>
              🚗 Miles:
              <input type="number" step="0.1" min="0" class="input-metric" data-action="edit-mileage" data-id="${t.id}" value="${t.metrics.mileageMiles ?? ""}" placeholder="0.0"/>
            </label>
          </div>
          <button class="btn-post-rush ${t.postRushReview?.flagged ? "flagged" : ""}" data-action="flag-post-rush" data-order="${escapeHtml(t.orderNumber)}">
            ${t.postRushReview?.flagged ? "🚩 Flagged for Post-Rush Review" : "🏳️ Flag for Post-Rush Review"}
          </button>
        </footer>
        ${
          t.postRushReview?.flagged
            ? `<div class="post-rush-note-preview">📝 <strong>Post-Rush Note (#${escapeHtml(t.orderNumber)}):</strong> ${escapeHtml(t.postRushReview.note)}</div>`
            : ""
        }
      </article>`;
    })
    .join("");

  bindCardEvents(container);
}

function bindCardEvents(container) {
  // Run selection checkboxes (Syncs with "Queued for multi-run" / "On Order")
  container.querySelectorAll(".run-checkbox").forEach((cb) => {
    cb.addEventListener("change", () => {
      const t = state.tickets.find((x) => x.id === cb.dataset.id);
      if (t) {
        t.selectedForRun = cb.checked;
        if (cb.checked && (!t.status || t.status === "On Order")) {
          t.status = "Queued for multi-run";
        } else if (!cb.checked && t.status === "Queued for multi-run") {
          t.status = "On Order";
        }
        sortActiveTickets();
        saveShiftState();
        renderAll();
      }
    });
  });

  // Up / Down stop reordering among active (non-Delivered) cards
  container.querySelectorAll("[data-action='move-up']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = Number(btn.dataset.index);
      let prevActiveIdx = idx - 1;
      while (prevActiveIdx >= 0 && state.tickets[prevActiveIdx].status === "Delivered") {
        prevActiveIdx--;
      }
      if (prevActiveIdx >= 0) {
        const tmp = state.tickets[prevActiveIdx];
        state.tickets[prevActiveIdx] = state.tickets[idx];
        state.tickets[idx] = tmp;
        saveShiftState();
        renderDeliveryCards();
      }
    });
  });

  container.querySelectorAll("[data-action='move-down']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = Number(btn.dataset.index);
      let nextActiveIdx = idx + 1;
      while (nextActiveIdx < state.tickets.length && state.tickets[nextActiveIdx].status === "Delivered") {
        nextActiveIdx++;
      }
      if (nextActiveIdx < state.tickets.length) {
        const tmp = state.tickets[nextActiveIdx];
        state.tickets[nextActiveIdx] = state.tickets[idx];
        state.tickets[idx] = tmp;
        saveShiftState();
        renderDeliveryCards();
      }
    });
  });

  // Tamarack SMS Pre-Departure Gate
  container.querySelectorAll(".btn-sms-gate").forEach((link) => {
    link.addEventListener("click", () => {
      const t = state.tickets.find((x) => x.id === link.dataset.ticketId);
      if (t) {
        t.smsPreDepartureSent = true;
        saveShiftState();
        setTimeout(() => renderDeliveryCards(), 300);
      }
    });
  });

  // Dismiss (✕) Reminder Banners, Tip Badge, Rescan Diff, and Locked-Building SMS Box
  container.querySelectorAll("[data-action='dismiss-alert']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const t = state.tickets.find((x) => x.id === btn.dataset.id);
      const idx = Number(btn.dataset.alertIndex);
      if (t && t.specialAlerts?.[idx]) {
        t.specialAlerts[idx].dismissed = true;
        saveShiftState();
        renderDeliveryCards();
      }
    });
  });

  container.querySelectorAll("[data-action='dismiss-sms-box']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const t = state.tickets.find((x) => x.id === btn.dataset.id);
      if (t) {
        t.smsBoxDismissed = true;
        saveShiftState();
        renderDeliveryCards();
      }
    });
  });

  container.querySelectorAll("[data-action='dismiss-tip-badge']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const t = state.tickets.find((x) => x.id === btn.dataset.id);
      if (t) {
        t.tipBadgeDismissed = true;
        saveShiftState();
        renderDeliveryCards();
      }
    });
  });

  container.querySelectorAll("[data-action='dismiss-rescan-diff']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const t = state.tickets.find((x) => x.id === btn.dataset.id);
      if (t) {
        t.rescanDiffNotice = null;
        saveShiftState();
        renderDeliveryCards();
      }
    });
  });

  // Status Pills
  container.querySelectorAll("[data-action='set-status']").forEach((btn) => {
    btn.addEventListener("click", () => {
      updateTicketStatus(btn.dataset.id, btn.dataset.status);
    });
  });

  // Drive Time & Mileage Inputs
  container.querySelectorAll("[data-action='edit-drivetime']").forEach((inp) => {
    inp.addEventListener("change", () => {
      const t = state.tickets.find((x) => x.id === inp.dataset.id);
      if (!t) return;
      t.metrics.driveTimeMinutes = inp.value !== "" ? Number(inp.value) : null;
      const normalMins = state.mapRules?.deliveryFeePolicy?.normalDriveMinutes || 7;
      if (t.metrics.driveTimeMinutes > normalMins && t.deliveryFee.chargedAmount <= 3.0) {
        t.deliveryFee.underchargedWarning = true;
      }
      saveShiftState();
      renderAll();
    });
  });

  container.querySelectorAll("[data-action='edit-mileage']").forEach((inp) => {
    inp.addEventListener("change", () => {
      const t = state.tickets.find((x) => x.id === inp.dataset.id);
      if (!t) return;
      t.metrics.mileageMiles = inp.value !== "" ? Number(inp.value) : null;
      const normalMiles = state.mapRules?.deliveryFeePolicy?.normalRadiusMiles || 1.8;
      if (t.metrics.mileageMiles > normalMiles && t.deliveryFee.chargedAmount <= 3.0) {
        t.deliveryFee.underchargedWarning = true;
      }
      saveShiftState();
      renderAll();
    });
  });

  // Edit Ticket Details Button
  container.querySelectorAll("[data-action='edit-ticket']").forEach((btn) => {
    btn.addEventListener("click", () => {
      openEditTicketModal(btn.dataset.id);
    });
  });

  // Post-Rush Review Flag Button
  container.querySelectorAll("[data-action='flag-post-rush']").forEach((btn) => {
    btn.addEventListener("click", () => {
      openPostRushModal(btn.dataset.order);
    });
  });

  // Save / Edit Local Map Rule directly from delivery card
  container.querySelectorAll("[data-action='save-map-rule-from-ticket']").forEach((btn) => {
    btn.addEventListener("click", () => {
      openMapRuleFromTicket(btn.dataset.id);
    });
  });
}

function saveCustomMapRules() {
  if (!state.mapRules) return;
  localStorage.setItem(CUSTOM_RULES_KEY, JSON.stringify(state.mapRules.addressRules || []));
}

function openMapRuleFromTicket(ticketId) {
  const t = state.tickets.find((x) => x.id === ticketId);
  if (!t) return;
  const rawStreet = (t.address?.rawStreet || "").trim();
  const haystack = `${rawStreet} ${t.customerName || ""}`.toUpperCase();
  const rules = state.mapRules?.addressRules || [];
  const matchIdx = rules.findIndex((r) =>
    (r.matchPatterns || []).some((p) => p && haystack.includes(String(p).toUpperCase()))
  );
  if (matchIdx >= 0) {
    openMapRuleModal(matchIdx);
    return;
  }
  const fee = Number(t.deliveryFee?.chargedAmount || 3.0);
  openMapRuleModal(-1, {
    displayName: rawStreet || t.customerName || "",
    matchPatterns: rawStreet ? [rawStreet.toUpperCase()] : [],
    trackSide: t.routing?.trackSide || "SHOP_SIDE",
    snapPolicy: t.routing?.snapMode || "FRONT_CURB",
    recommendedFee: fee,
    isExtendedDistance: fee > 3.0,
    parkingSpot: t.routing?.driverNotes?.parkingSpot || "",
    permanentAlert: t.specialInstructions && t.specialInstructions !== "None" ? t.specialInstructions : ""
  });
}

function openMapRuleModal(ruleIndex = -1, prefill = null) {
  const modal = document.getElementById("mapRuleModal");
  const titleEl = document.getElementById("mapRuleModalTitle");
  if (!modal) return;

  const rules = state.mapRules?.addressRules || [];
  const existing = ruleIndex >= 0 ? rules[ruleIndex] : null;
  modal.dataset.ruleIndex = String(existing ? ruleIndex : -1);
  if (titleEl) titleEl.textContent = existing ? "✏️ Edit Local Map Rule" : "🧭 Add Local Map Rule";

  document.getElementById("ruleDisplayName").value = existing?.displayName || prefill?.displayName || "";
  document.getElementById("ruleMatchPatterns").value = (existing?.matchPatterns || prefill?.matchPatterns || []).join(", ");
  document.getElementById("ruleTrackSide").value = existing?.trackSide || prefill?.trackSide || "SHOP_SIDE";
  document.getElementById("ruleSnapPolicy").value = existing?.geofence?.snapPolicy || prefill?.snapPolicy || "FRONT_CURB";
  document.getElementById("ruleRecommendedFee").value = Number(existing?.recommendedFee ?? prefill?.recommendedFee ?? 3.0).toFixed(2);
  document.getElementById("ruleIsExtended").checked = Boolean(existing?.isExtendedDistance ?? prefill?.isExtendedDistance);

  const pin = existing?.geofence?.customOverridePin || existing?.geofence?.frontCurbPin;
  document.getElementById("ruleCustomLat").value = pin?.lat ?? "";
  document.getElementById("ruleCustomLng").value = pin?.lng ?? "";

  document.getElementById("ruleParkingSpot").value = existing?.driverNotes?.parkingSpot || prefill?.parkingSpot || "";
  document.getElementById("ruleDirectionNote").value = existing?.geofence?.approachWaypoint?.directionNote || "";
  document.getElementById("rulePermanentAlert").value = existing?.driverNotes?.permanentAlert || prefill?.permanentAlert || "";
  document.getElementById("ruleRequireSms").checked = Boolean(existing?.preDepartureRule?.requireSmsBeforeStart);
  document.getElementById("ruleSmsTemplate").value = existing?.preDepartureRule?.smsTemplate || "";

  modal.classList.remove("hidden");
  document.getElementById("ruleDisplayName")?.focus();
}

function saveMapRuleModal() {
  const modal = document.getElementById("mapRuleModal");
  if (!modal || !state.mapRules) return;

  const displayName = document.getElementById("ruleDisplayName").value.trim();
  const patternsRaw = document.getElementById("ruleMatchPatterns").value.trim();
  if (!displayName || !patternsRaw) {
    alert("Enter both a Display Name and at least one Match Pattern (e.g. street address or building name).");
    return;
  }

  const matchPatterns = patternsRaw
    .split(",")
    .map((p) => p.trim().toUpperCase())
    .filter(Boolean);

  const ruleIndex = Number(modal.dataset.ruleIndex ?? -1);
  const rules = Array.isArray(state.mapRules.addressRules) ? state.mapRules.addressRules : [];
  const existing = ruleIndex >= 0 ? rules[ruleIndex] : null;

  const latStr = document.getElementById("ruleCustomLat").value.trim();
  const lngStr = document.getElementById("ruleCustomLng").value.trim();
  const hasCoords = latStr !== "" && lngStr !== "" && Number.isFinite(Number(latStr)) && Number.isFinite(Number(lngStr));
  const customPin = hasCoords ? { lat: Number(latStr), lng: Number(lngStr) } : null;

  const snapPolicy = document.getElementById("ruleSnapPolicy").value;
  const dirNote = document.getElementById("ruleDirectionNote").value.trim();
  const requireSms = document.getElementById("ruleRequireSms").checked;
  const smsTemplate = document.getElementById("ruleSmsTemplate").value.trim();

  const updatedRule = {
    ...(existing || {}),
    normalizedKey: existing?.normalizedKey || displayName.toUpperCase().replace(/[^A-Z0-9 ]/g, "").trim(),
    displayName,
    matchPatterns,
    trackSide: document.getElementById("ruleTrackSide").value,
    isExtendedDistance: document.getElementById("ruleIsExtended").checked,
    recommendedFee: Math.max(0, Number(document.getElementById("ruleRecommendedFee").value || 3.0)),
    geofence: {
      ...(existing?.geofence || {}),
      frontCurbPin: existing?.geofence?.frontCurbPin || (snapPolicy === "FRONT_CURB" ? customPin : null),
      customOverridePin: snapPolicy === "CUSTOM_PIN" ? customPin : existing?.geofence?.customOverridePin || null,
      snapPolicy,
      approachWaypoint: dirNote
        ? { ...(existing?.geofence?.approachWaypoint || {}), directionNote: dirNote }
        : null
    },
    preDepartureRule: {
      requireSmsBeforeStart: requireSms,
      buttonLabel: requireSms ? `📱 Text Customer Before Leaving Shop (${displayName})` : null,
      smsTemplate: requireSms
        ? smsTemplate || `Hi! This is your Coach's Pizza driver. I'm heading out now and will arrive at ${displayName} in about 5-7 minutes!`
        : null
    },
    driverNotes: {
      ...(existing?.driverNotes || {}),
      parkingSpot: document.getElementById("ruleParkingSpot").value.trim() || "Front street curb",
      permanentAlert: document.getElementById("rulePermanentAlert").value.trim() || ""
    },
    tipHistory: existing?.tipHistory || {
      totalDeliveries: 0,
      averageTip: 0,
      lastTip: 0,
      generousRegular: false
    }
  };

  if (existing) {
    rules[ruleIndex] = updatedRule;
  } else {
    rules.push(updatedRule);
  }
  state.mapRules.addressRules = rules;
  saveCustomMapRules();
  renderAddressRulesPanel();
  modal.classList.add("hidden");
}

function exportMapRulesJson() {
  if (!state.mapRules) return;
  downloadBlob(
    JSON.stringify(state.mapRules, null, 2),
    "local-map-rules.json",
    "application/json"
  );
}

function renderAddressRulesPanel() {
  const container = document.getElementById("addressRulesList");
  if (!container || !state.mapRules?.addressRules) return;

  if (state.mapRules.addressRules.length === 0) {
    container.innerHTML = `<p class="muted">No local map rules configured yet. Tap <strong>➕ Add Rule</strong> to create one.</p>`;
    return;
  }

  container.innerHTML = state.mapRules.addressRules
    .map(
      (r, idx) => `
      <div class="rule-item-card">
        <div class="rule-title-row">
          <strong>${escapeHtml(r.displayName)}</strong>
          <div class="rule-title-actions">
            <span class="rule-chip">${escapeHtml(r.geofence?.snapPolicy || "FRONT_CURB")}</span>
            <button class="btn-icon btn-edit-mini" data-action="edit-map-rule" data-index="${idx}" title="Edit rule">✏️</button>
            <button class="btn-icon btn-edit-mini" data-action="delete-map-rule" data-index="${idx}" title="Delete rule">🗑️</button>
          </div>
        </div>
        <div class="rule-detail">Patterns: <code>${escapeHtml((r.matchPatterns || []).join(", "))}</code> • ${
          r.trackSide === "ACROSS_TRACKS" ? "⚠️ Across Tracks" : "✓ Shop Side"
        }${Number(r.recommendedFee || 3) > 3 ? ` • 💵 $${Number(r.recommendedFee).toFixed(2)}` : ""}</div>
        <div class="rule-detail">🅿️ ${escapeHtml(r.driverNotes?.parkingSpot || "Front street curb")}</div>
        ${
          r.geofence?.approachWaypoint?.directionNote
            ? `<div class="rule-detail">↪ ${escapeHtml(r.geofence.approachWaypoint.directionNote)}</div>`
            : ""
        }
        ${
          r.driverNotes?.permanentAlert
            ? `<div class="rule-detail">🚨 ${escapeHtml(r.driverNotes.permanentAlert)}</div>`
            : ""
        }
      </div>`
    )
    .join("");

  container.querySelectorAll("[data-action='edit-map-rule']").forEach((btn) => {
    btn.addEventListener("click", () => openMapRuleModal(Number(btn.dataset.index)));
  });

  container.querySelectorAll("[data-action='delete-map-rule']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = Number(btn.dataset.index);
      const target = state.mapRules.addressRules[idx];
      if (!target) return;
      if (!confirm(`Delete map rule "${target.displayName}"?`)) return;
      state.mapRules.addressRules.splice(idx, 1);
      saveCustomMapRules();
      renderAddressRulesPanel();
    });
  });
}

function renderLedger() {
  const odoStartEl = document.getElementById("odoStart");
  const odoEndEl = document.getElementById("odoEnd");
  if (odoStartEl && odoStartEl.value !== String(state.shift.odometerStart)) {
    odoStartEl.value = state.shift.odometerStart;
  }
  if (odoEndEl && odoEndEl.value !== String(state.shift.odometerEnd)) {
    odoEndEl.value = state.shift.odometerEnd;
  }

  if (state.shift.startedAt || state.shift.odometerStart || state.shift.startOdoPhoto) {
    document.getElementById("startShiftReminderBanner")?.classList.add("hidden");
  }

  const startLabelEl = document.getElementById("shiftStartBtnText");
  const endLabelEl = document.getElementById("shiftEndBtnText");
  if (startLabelEl) {
    startLabelEl.textContent = state.shift.startedAt
      ? `✅ Shift Started (${state.shift.odometerStart || "Photo Saved"})`
      : "🚗 Start Shift (Odometer Photo)";
  }
  if (endLabelEl) {
    endLabelEl.textContent = state.shift.endedAt
      ? `🏁 Shift Ended (${state.shift.odometerEnd || "Photo Saved"})`
      : "🏁 End Shift (Odometer Photo)";
  }

  const odoPhotosEl = document.getElementById("odoPhotosPreview");
  if (odoPhotosEl) {
    const startHtml = state.shift.startOdoPhoto
      ? `<button type="button" class="odo-thumb-box" data-open-odo="start" style="cursor:pointer; color:inherit; text-align:left;"><img src="${state.shift.startOdoPhoto}" alt="Start Odometer"/><span>Start: <strong>${escapeHtml(state.shift.odometerStart || "Tap to enter")}</strong> (${new Date(state.shift.startedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}) 🔍</span></button>`
      : "";
    const endHtml = state.shift.endOdoPhoto
      ? `<button type="button" class="odo-thumb-box" data-open-odo="end" style="cursor:pointer; color:inherit; text-align:left;"><img src="${state.shift.endOdoPhoto}" alt="End Odometer"/><span>End: <strong>${escapeHtml(state.shift.odometerEnd || "Tap to enter")}</strong> (${new Date(state.shift.endedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}) 🔍</span></button>`
      : "";
    odoPhotosEl.innerHTML = startHtml + endHtml;
    odoPhotosEl.querySelectorAll("[data-open-odo]").forEach((btn) => {
      btn.addEventListener("click", () => openOdometerViewer(btn.dataset.openOdo));
    });
  }

  const completed = state.tickets.filter((t) => t.status === "Delivered" || t.status === "End Delivery");
  const totalDeliveries = completed.length;
  const standardFeeSum = totalDeliveries * 3.0;
  const extendedFeeTickets = completed.filter((t) => t.deliveryFee.chargedAmount > 3.0);
  const extraFeeSum = extendedFeeTickets.reduce((sum, t) => sum + t.deliveryFee.extraOverStandard, 0);
  const totalDriverFeeEarned = standardFeeSum + extraFeeSum;

  const cashCollectedSum = completed.reduce((sum, t) => sum + Number(t.payment.amountDue || 0), 0);
  const ticketMilesSum = state.tickets.reduce((sum, t) => sum + Number(t.metrics?.mileageMiles || 0), 0);

  const odoDiff =
    state.shift.odometerEnd && state.shift.odometerStart
      ? Math.max(0, Number(state.shift.odometerEnd) - Number(state.shift.odometerStart))
      : ticketMilesSum;

  const flaggedReviews = state.tickets.filter((t) => t.postRushReview?.flagged);

  const summaryEl = document.getElementById("ledgerSummaryMetrics");
  if (summaryEl) {
    const statCards = [];
    if (totalDeliveries > 0) {
      statCards.push(`
        <div class="ledger-stat">
          <span class="stat-label">Completed Deliveries</span>
          <span class="stat-value">${totalDeliveries}</span>
        </div>`);
    }
    if (standardFeeSum > 0) {
      statCards.push(`
        <div class="ledger-stat">
          <span class="stat-label">Base Fees ($3.00 × ${totalDeliveries})</span>
          <span class="stat-value">$${standardFeeSum.toFixed(2)}</span>
        </div>`);
    }
    if (extraFeeSum > 0) {
      statCards.push(`
        <div class="ledger-stat highlight">
          <span class="stat-label">Extended Fees (> $3.00) Owed to You</span>
          <span class="stat-value">+$${extraFeeSum.toFixed(2)}</span>
        </div>`);
    }
    if (totalDriverFeeEarned > 0) {
      statCards.push(`
        <div class="ledger-stat total-payout">
          <span class="stat-label">Total 1099 Delivery Fees Earned</span>
          <span class="stat-value">$${totalDriverFeeEarned.toFixed(2)}</span>
        </div>`);
    }
    if (cashCollectedSum > 0) {
      statCards.push(`
        <div class="ledger-stat">
          <span class="stat-label">Cash/In-Person Total to Reconcile</span>
          <span class="stat-value">$${cashCollectedSum.toFixed(2)}</span>
        </div>`);
    }
    if (odoDiff > 0) {
      statCards.push(`
        <div class="ledger-stat">
          <span class="stat-label">1099 Tax Mileage Logged</span>
          <span class="stat-value">${odoDiff.toFixed(1)} mi</span>
        </div>`);
    }

    summaryEl.innerHTML =
      statCards.length > 0
        ? statCards.join("")
        : `<p class="muted" style="grid-column: 1 / -1;">No completed deliveries or mileage logged yet tonight.</p>`;
  }

  const reviewListEl = document.getElementById("postRushReviewList");
  if (reviewListEl) {
    if (flaggedReviews.length === 0) {
      reviewListEl.innerHTML = `<p class="muted">No orders flagged for post-rush boss debrief yet.</p>`;
    } else {
      reviewListEl.innerHTML = flaggedReviews
        .map(
          (t) => `
          <div class="review-debrief-item">
            <strong>Order #${escapeHtml(t.orderNumber)}</strong> (${escapeHtml(t.address?.rawStreet || "")} — Fee charged: $${t.deliveryFee.chargedAmount.toFixed(2)}, Drive: ${t.metrics.driveTimeMinutes ?? "?"}m, Miles: ${t.metrics.mileageMiles ?? "?"} mi)
            <div>👉 <em>${escapeHtml(t.postRushReview.note)}</em></div>
          </div>`
        )
        .join("");
    }
  }
}

function exportShiftJson() {
  const payload = {
    exportedAt: new Date().toISOString(),
    app: "delivery-zoomed",
    town: state.mapRules?.townName || "Conrad, MT",
    shift: state.shift,
    tickets: state.tickets,
    postRushReviews: state.tickets
      .filter((t) => t.postRushReview?.flagged)
      .map((t) => ({
        orderNumber: t.orderNumber,
        address: t.address?.fullFormatted,
        chargedFee: t.deliveryFee?.chargedAmount,
        driveTimeMinutes: t.metrics?.driveTimeMinutes,
        mileageMiles: t.metrics?.mileageMiles,
        note: t.postRushReview.note
      }))
  };
  downloadBlob(
    JSON.stringify(payload, null, 2),
    `delivery-zoomed-shift-${state.shift.date}.json`,
    "application/json"
  );
}

function exportShiftCsv() {
  const headers = [
    "OrderNumber",
    "Status",
    "CustomerName",
    "StreetAddress",
    "DeliveryFeeEarned",
    "ExtraOver3DollarBase",
    "PaymentStatus",
    "AmountDueCollected",
    "OnlineTip",
    "DriveTimeMinutes",
    "MileageMiles",
    "PostRushReviewFlagged",
    "PostRushReviewNote"
  ];
  const rows = state.tickets.map((t) => [
    t.orderNumber,
    t.status,
    t.customerName,
    t.address?.rawStreet || "",
    t.deliveryFee?.chargedAmount?.toFixed(2) || "3.00",
    t.deliveryFee?.extraOverStandard?.toFixed(2) || "0.00",
    t.payment?.status || "",
    t.payment?.amountDue?.toFixed(2) || "0.00",
    t.payment?.onlineTip?.toFixed(2) || "0.00",
    t.metrics?.driveTimeMinutes ?? "",
    t.metrics?.mileageMiles ?? "",
    t.postRushReview?.flagged ? "YES" : "NO",
    t.postRushReview?.note || ""
  ]);

  const csvContent = [headers, ...rows]
    .map((r) => r.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
    .join("\n");

  downloadBlob(csvContent, `delivery-zoomed-shift-${state.shift.date}.csv`, "text/csv;charset=utf-8;");
}

function exportHistoryJson() {
  const payload = {
    exportedAt: new Date().toISOString(),
    app: "delivery-zoomed-history",
    history: state.history,
    customers: state.customers
  };
  const dateTag = new Date().toISOString().slice(0, 10);
  downloadBlob(
    JSON.stringify(payload, null, 2),
    `delivery-zoomed-history-backup-${dateTag}.json`,
    "application/json"
  );
}

async function importHistoryJson(file) {
  try {
    const text = await file.text();
    const data = JSON.parse(text);
    const incomingHist = Array.isArray(data.history) ? data.history : [];
    const incomingCust = data.customers && typeof data.customers === "object" ? data.customers : {};

    const existingIds = new Set(state.history.map((h) => h.id));
    let addedHist = 0;
    for (const h of incomingHist) {
      if (h?.id && !existingIds.has(h.id)) {
        state.history.push(h);
        existingIds.add(h.id);
        addedHist++;
      }
    }

    let mergedCust = 0;
    for (const [k, v] of Object.entries(incomingCust)) {
      if (!state.customers[k]) {
        state.customers[k] = v;
        mergedCust++;
      } else {
        const cur = state.customers[k];
        cur.deliveryCount = Math.max(cur.deliveryCount || 0, v.deliveryCount || 0);
        cur.generousTipCount = Math.max(cur.generousTipCount || 0, v.generousTipCount || 0);
        if (!cur.customerPhone && v.customerPhone) cur.customerPhone = v.customerPhone;
        const addrs = new Set([...(cur.addressesVisited || []), ...(v.addressesVisited || [])]);
        cur.addressesVisited = Array.from(addrs);
      }
    }

    savePermanentCustomerAndHistoryDb();
    renderAll();
    renderHistoryModal();
    alert(`✅ Imported ${addedHist} delivered order(s) and ${mergedCust} new customer profile(s).`);
  } catch (err) {
    alert(`⚠️ Could not import history JSON: ${err.message}`);
  }
}

function downloadBlob(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function renderHistoryModal() {
  const listEl = document.getElementById("historyResultsList");
  const dateSelect = document.getElementById("historyDateFilter");
  const searchInput = document.getElementById("historySearchInput");
  if (!listEl) return;

  // Combine tonight's delivered tickets + permanent archived history (deduplicated by ticket id)
  const combinedMap = new Map();
  for (const t of state.tickets.filter((x) => x.status === "Delivered")) {
    combinedMap.set(t.id, { ...t, shiftDate: state.shift.date });
  }
  for (const h of state.history) {
    if (!combinedMap.has(h.id)) {
      combinedMap.set(h.id, h);
    }
  }
  const allDelivered = Array.from(combinedMap.values());

  // Populate shift dates dropdown
  if (dateSelect) {
    const currentVal = dateSelect.value || "ALL";
    const uniqueDates = [...new Set(allDelivered.map((x) => x.shiftDate).filter(Boolean))].sort().reverse();
    dateSelect.innerHTML =
      `<option value="ALL">All Nights (${allDelivered.length})</option>` +
      uniqueDates.map((d) => `<option value="${escapeHtml(d)}">${escapeHtml(d)}</option>`).join("");
    if (uniqueDates.includes(currentVal) || currentVal === "ALL") {
      dateSelect.value = currentVal;
    }
  }

  const selectedDate = dateSelect?.value || "ALL";
  const rawQuery = (searchInput?.value || "").trim().toLowerCase();
  const queryTokens = rawQuery ? rawQuery.split(/\s+/).filter(Boolean) : [];

  const filtered = allDelivered.filter((item) => {
    if (selectedDate !== "ALL" && item.shiftDate !== selectedDate) return false;
    if (queryTokens.length === 0) return true;
    const haystack = [
      item.orderNumber,
      item.customerName,
      item.customerPhone,
      item.address?.rawStreet,
      item.specialInstructions,
      item.postRushReview?.note
    ]
      .join(" ")
      .toLowerCase();
    // Every word in search query (e.g. first name, last name, or both, or order #) must match
    return queryTokens.every((tok) => haystack.includes(tok));
  });

  if (filtered.length === 0) {
    listEl.innerHTML = `<p class="muted">No delivered orders match your search.</p>`;
    return;
  }

  listEl.innerHTML = filtered
    .map((item) => {
      const custKey =
        item.customerProfileKey ||
        getCustomerProfileKey(item.customerName, item.customerPhone, item.address?.normalizedKey);
      const profile = state.customers[custKey];
      const pizzaSummary = (item.orderSummary?.pizzas || [])
        .map((p) => `${p.qty}x ${p.size} ${p.name}`)
        .join(", ");
      const otherSummary = (item.orderSummary?.otherItems || [])
        .map((it) => `${it.qty}x ${it.name}`)
        .join(", ");
      const itemsLine = [pizzaSummary, otherSummary].filter(Boolean).join(" • ") || "No items listed";

      return `
      <div class="history-item-card">
        <div class="history-item-top">
          <div>
            <span class="order-badge status-badge-delivered">#${escapeHtml(item.orderNumber)}</span>
            <strong>${escapeHtml(item.customerName)}</strong>
            ${item.customerPhone ? `<span class="muted">(${escapeHtml(item.customerPhone)})</span>` : ""}
          </div>
          <span class="muted">${escapeHtml(item.shiftDate || "")}</span>
        </div>
        <div class="history-item-detail">📍 ${escapeHtml(item.address?.rawStreet || "")} ${
          item.specialInstructions && item.specialInstructions !== "None"
            ? `• <em>${escapeHtml(item.specialInstructions)}</em>`
            : ""
        }</div>
        <div class="history-item-detail">🍕 ${escapeHtml(itemsLine)}</div>
        <div class="history-item-detail">
          💵 ${escapeHtml(item.payment?.displayBanner || "")} • Fee: $${Number(item.deliveryFee?.chargedAmount || 3).toFixed(2)} •
          ⏱️ Drive: ${item.metrics?.driveTimeMinutes ?? "?"}m • 🚗 Miles: ${item.metrics?.mileageMiles ?? "?"}
          ${profile ? ` • 👤 Repeat Customer (${profile.deliveryCount}x, ${profile.addressesVisited?.length || 1} addr)` : ""}
        </div>
        ${
          item.postRushReview?.flagged
            ? `<div class="post-rush-note-preview">🚩 ${escapeHtml(item.postRushReview.note)}</div>`
            : ""
        }
        <div class="history-item-actions">
          <button class="btn-secondary btn-nav-compact" data-action="reopen-delivered" data-id="${item.id}" data-status="On Order">↩️ Reopen to Active Queue</button>
          <button class="btn-secondary btn-nav-compact" data-action="reopen-delivered" data-id="${item.id}" data-status="Issue/Redelivery">🚨 Mark Issue/Redelivery</button>
        </div>
      </div>`;
    })
    .join("");

  listEl.querySelectorAll("[data-action='reopen-delivered']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.id;
      const nextStatus = btn.dataset.status || "On Order";
      let ticket = state.tickets.find((t) => t.id === targetId);
      if (!ticket) {
        const fromHist = state.history.find((h) => h.id === targetId);
        if (fromHist) {
          ticket = JSON.parse(JSON.stringify(fromHist));
          state.tickets.push(ticket);
        }
      }
      if (ticket) {
        ticket.status = nextStatus;
        sortActiveTickets();
        saveShiftState();
        renderAll();
        document.getElementById("historyModal")?.classList.add("hidden");
      }
    });
  });
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", () => {
  initApp();
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch((err) => {
      console.warn("Service worker registration skipped:", err);
    });
  }
});
