/**
 * ocr-parser.js — Shift4 / SkyTab POS Ticket Vision OCR & Deterministic Rule Engine
 * Supports:
 *  1. Gemini 2.5 Flash Vision API (Structured JSON Schema, temperature: 0)
 *  2. xAI Grok Vision API (grok-2-vision-1212, temperature: 0)
 *  3. Deterministic JS Post-Verifier ensuring 100% compliance with delivery filter,
 *     surcharge rules ($3.00 standard up to $10.00), *, !!!, Soup/Salad/Drink banners,
 *     and front-curb vs. alley pin rules.
 */

export const TICKET_STATUSES = [
  "On Order",
  "Queued for multi-run",
  "Start Delivery",
  "Delivered",
  "Issue/Redelivery"
];

const SOUP_SALAD_DRINK_REGEX = /\b(salad|soup|cup of soup|bowl of soup|chili|chowder|pepsi|coke|cola|sprite|dr\.?\s*pepper|mt\.?\s*dew|mountain dew|root beer|lemonade|tea|2-?liter|2l|can|bottle|drink|soda|water)\b/i;
const ALLEY_KEYWORD_REGEX = /\b(alley|back|rear)\b/i;

/**
 * Downscales a camera photo to maxDim (default 1200px) JPEG 0.78 for fast upload & lower vision latency.
 */
export async function compressTicketPhoto(file, maxDim = 1200, quality = 0.78) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("Failed to read image file."));
    reader.onload = (e) => {
      const img = new Image();
      img.onerror = () => reject(new Error("Invalid image format."));
      img.onload = () => {
        let { width, height } = img;
        if (width > maxDim || height > maxDim) {
          if (width >= height) {
            height = Math.round((height * maxDim) / width);
            width = maxDim;
          } else {
            width = Math.round((width * maxDim) / height);
            height = maxDim;
          }
        }
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);
        const dataUrl = canvas.toDataURL("image/jpeg", quality);
        const base64Data = dataUrl.split(",")[1];
        resolve({ base64Data, mimeType: "image/jpeg", width, height, previewUrl: dataUrl });
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

/**
 * Strict extraction prompt shared by Gemini 2.5 Flash and Grok Vision.
 */
function buildExtractionSystemPrompt() {
  return `You are a strict POS thermal receipt OCR extractor for Shift4 / SkyTab POS tickets at Coach's Pizza in Conrad, MT 59425.
An image may contain 1 to 4 separate POS tickets. Inspect EVERY ticket visible in the photo.

STRICT DELIVERY FILTER:
- A ticket is ONLY a valid delivery if it explicitly contains the word "Delivery" OR has a Delivery / Total Surcharge of $3.00 or more (typically $3.00 up to $10.00).
- If a ticket has NEITHER "Delivery" NOR a >= $3.00 surcharge, set:
  "isDelivery": false,
  "orderNumber": "<Order Number>",
  "ignoredOutput": "Order #<Number> - PICKUP / IN-HOUSE (Ignore)"
  and leave other fields empty.

FOR EVERY VALID DELIVERY TICKET, EXTRACT verbatim:
1. "orderNumber": string (Shift4 daily order numbers start at 2000 and count upward, e.g. "2001", "2018", "2045". If the top of the ticket is cut off/unreadable, output whatever partial characters are visible.)
2. "customerName": string
3. "customerPhone": string (if printed, else "")
4. "streetAddress": string (the street line, e.g. "412 S Main St")
5. "specialDeliveryInstructions": Look specifically between the street address line and "Conrad, MT". If any text is there (e.g. "in the alley", gate codes, door notes, apartment #), extract it verbatim. If nothing extra is between the street address and "Conrad, MT", output "None".
6. "deliverySurcharge": number (default 3.00 if standard delivery, or exact dollar surcharge from $3.00 to $10.00+ printed on ticket).
7. "paymentType": "PAID_ONLINE" if "Credit - st-online" or online pre-payment is shown; otherwise "COLLECT".
8. "totalDue": number (0.00 if paid online, or exact dollar total due if unpaid).
9. "onlineTip": number (any online/pre-authorized tip shown on receipt, else 0).
10. "pizzas": array of objects { "qty": number, "name": string, "size": "Sm"|"Med"|"Lg"|string, "crust": "Double Crust"|"Regular"|"Thin"|string, "optionsLines": [string] }
11. "otherItems": array of objects { "qty": number, "name": string, "modifierLines": [string] }
12. "rawAlertLines": array of verbatim lines from the ticket that:
    - start with an asterisk "*" (e.g., "* Salt The Fries :)")
    - start with "Pizza Options:" or contain any exclamation marks "!" (e.g., "Pie Cut!!!")
    - mention any Salad, Soup (including "Cup Of Soup"), or Drink.

Return ONLY valid JSON with a top-level key "tickets" containing an array of extracted ticket objects.`;
}

/**
 * Call Gemini 2.5 Flash Vision API with temperature 0 and JSON output.
 */
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function isUuidKeyId(str) {
  return UUID_REGEX.test(String(str || "").trim());
}

/**
 * Auto-detects and normalizes Google (AQ.Ab... / AQ.... / AIza...) vs xAI (xai-...) keys.
 */
export function resolveApiKeys(settings = {}) {
  const clean = (val) => String(val || "").trim().replace(/^["']|["']$/g, "");
  const rawGem = clean(settings.geminiApiKey);
  const rawGrok = clean(settings.grokApiKey);
  const rawLegacy = clean(settings.apiKey);

  const isGoogleKey = (k) => k.startsWith("AQ.") || k.startsWith("AIza");
  const isGrokKey = (k) => k.startsWith("xai-");

  let geminiKey = "";
  let grokKey = "";

  for (const k of [rawGem, rawGrok, rawLegacy].filter(Boolean)) {
    if (isUuidKeyId(k)) continue; // Ignore 36-char xAI table Key ID UUIDs
    if (isGoogleKey(k) && !geminiKey) {
      geminiKey = k;
    } else if (isGrokKey(k) && !grokKey) {
      grokKey = k;
    }
  }

  if (!geminiKey && rawGem && !isGrokKey(rawGem) && !isUuidKeyId(rawGem)) geminiKey = rawGem;
  if (!geminiKey && rawLegacy && !isGrokKey(rawLegacy) && !isUuidKeyId(rawLegacy)) geminiKey = rawLegacy;
  if (!grokKey && rawGrok && !isGoogleKey(rawGrok) && !isUuidKeyId(rawGrok)) grokKey = rawGrok;

  return { geminiKey, grokKey };
}

export async function extractTicketsFromPhoto(file, settings, mapRules, onProgress = () => {}) {
  onProgress("📸 Compressing ticket photo...");
  const compressed = await compressTicketPhoto(file);
  const sizeKb = Math.round((compressed.base64Data.length * 3) / 4 / 1024);
  onProgress(`📸 Photo compressed (${compressed.width}×${compressed.height}, ${sizeKb} KB). Sending to Vision OCR...`);

  const provider = settings.visionProvider || "google";
  const { geminiKey, grokKey } = resolveApiKeys(settings);

  if (!geminiKey && !grokKey) {
    throw new Error("No valid Vision API key found. Open ⚙️ Settings to verify your AQ.Ab... Google key.");
  }

  let rawTickets = [];
  let winningModel = "";
  const errors = [];

  const order = provider === "grok" && grokKey ? ["grok", "google"] : ["google", "grok"];

  for (const engine of order) {
    if (engine === "google" && geminiKey) {
      try {
        const res = await callGoogleVisionCascade(compressed, geminiKey, onProgress);
        rawTickets = res.tickets;
        winningModel = res.modelName;
        break;
      } catch (err) {
        errors.push(`Google Vision: ${err.message}`);
      }
    } else if (engine === "grok" && grokKey) {
      try {
        const res = await callGrokVision(compressed, grokKey, onProgress);
        rawTickets = res.tickets;
        winningModel = res.modelName;
        break;
      } catch (err) {
        errors.push(`xAI Grok: ${err.message}`);
      }
    }
  }

  if (!rawTickets || rawTickets.length === 0) {
    throw new Error(errors.join(" | ") || "Vision extraction returned no tickets.");
  }

  onProgress(`✅ Parsed ${rawTickets.length} ticket(s) using ${winningModel}!`);

  return rawTickets.map((raw, idx) => {
    const t = normalizeAndVerifyTicket(raw, mapRules, compressed.previewUrl, idx);
    t.parsedByModel = winningModel;
    t.failoverNotice = errors.length > 0 ? errors[0] : null;
    return t;
  });
}

/**
 * Compresses an odometer photo and reads the mileage digits via gemini-4-hydrogen.
 * Always returns { previewUrl, timestamp, odometerReading, modelName } so photo proof is saved even if OCR is skipped.
 */
export async function extractOdometerFromPhoto(file, settings, onProgress = () => {}) {
  onProgress("📸 Compressing odometer photo...");
  const compressed = await compressTicketPhoto(file, 1200, 0.82);
  const timestamp = new Date().toISOString();
  const { geminiKey } = resolveApiKeys(settings);

  if (!geminiKey) {
    return { previewUrl: compressed.previewUrl, timestamp, odometerReading: null, modelName: "manual" };
  }

  const modelsToTry = getOrderedGoogleModels();

  const payload = {
    contents: [
      {
        role: "user",
        parts: [
          { inlineData: { mimeType: compressed.mimeType, data: compressed.base64Data } },
          {
            text: 'Read the main vehicle total odometer mileage number from this dashboard photo (ignore trip meter A/B, clock, temperature, and MPH/RPM). Return ONLY valid JSON like {"odometer": 142510} or {"odometer": null} if unreadable.'
          }
        ]
      }
    ],
    generationConfig: {
      temperature: 0,
      responseMimeType: "application/json"
    }
  };

  for (const modelName of modelsToTry) {
    const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(modelName)}:generateContent?key=${encodeURIComponent(geminiKey)}`;
    try {
      onProgress(`⚡ Reading odometer with ${modelName}...`);
      const res = await fetchWithTimeout(
        endpoint,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        },
        25000
      );
      if (res.ok) {
        const data = await res.json();
        const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
        const parsed = extractJsonObject(text);
        const num = Number(String(parsed.odometer ?? "").replace(/[^0-9.]/g, ""));
        lastWorkingGoogleModel = modelName;
        if (modelName === HYDROGEN_MODEL) recordHydrogenSuccess();
        if (num > 0) {
          return { previewUrl: compressed.previewUrl, timestamp, odometerReading: num, modelName };
        }
        // Valid response from model, just couldn't read digits -> open manual photo viewer
        break;
      }
      if (modelName === HYDROGEN_MODEL) recordHydrogenFailure();
    } catch (_) {
      if (modelName === HYDROGEN_MODEL) recordHydrogenFailure();
    }
  }

  return { previewUrl: compressed.previewUrl, timestamp, odometerReading: null, modelName: "manual" };
}

// Verified working models on your key: gemini-4-hydrogen first, with Flash models as backup.
// After 2 consecutive Hydrogen failures, prioritize Flash for 12 hours, then auto-retry Hydrogen.
const HYDROGEN_MODEL = "gemini-4-hydrogen";
const HYDROGEN_COOLDOWN_KEY = "delivery_zoomed_hydrogen_cooldown_v1";
const HYDROGEN_COOLDOWN_MS = 12 * 60 * 60 * 1000;
const LIVE_PRIORITY_MODELS = [
  HYDROGEN_MODEL,
  "gemini-3.6-flash",
  "gemini-3.7-flash",
  "gemini-3.5-flash",
  "gemini-3.8-flash"
];

let lastWorkingGoogleModel = "";

function readHydrogenState() {
  try {
    const raw = localStorage.getItem(HYDROGEN_COOLDOWN_KEY);
    if (raw) return JSON.parse(raw);
  } catch (_) {}
  return { consecutiveFailures: 0, cooldownUntil: 0 };
}

function writeHydrogenState(st) {
  try {
    localStorage.setItem(HYDROGEN_COOLDOWN_KEY, JSON.stringify(st));
  } catch (_) {}
}

function recordHydrogenSuccess() {
  writeHydrogenState({ consecutiveFailures: 0, cooldownUntil: 0 });
}

function recordHydrogenFailure() {
  const st = readHydrogenState();
  const nextFailures = (st.consecutiveFailures || 0) + 1;
  const cooldownUntil = nextFailures >= 2 ? Date.now() + HYDROGEN_COOLDOWN_MS : 0;
  writeHydrogenState({ consecutiveFailures: nextFailures, cooldownUntil });
}

function getOrderedGoogleModels() {
  const st = readHydrogenState();
  if (st.cooldownUntil && Date.now() < st.cooldownUntil) {
    return [...LIVE_PRIORITY_MODELS.filter((m) => m !== HYDROGEN_MODEL), HYDROGEN_MODEL];
  }
  return LIVE_PRIORITY_MODELS;
}

async function discoverLiveGoogleCascade() {
  const models = getOrderedGoogleModels();
  return {
    modelsToTry: models,
    allDiscovered: LIVE_PRIORITY_MODELS
  };
}

function extractJsonObject(rawText) {
  const cleaned = String(rawText || "")
    .trim()
    .replace(/^```(?:json)?\s*/i, "")
    .replace(/\s*```$/i, "")
    .trim();
  try {
    return JSON.parse(cleaned);
  } catch (_) {
    const firstBrace = cleaned.indexOf("{");
    const lastBrace = cleaned.lastIndexOf("}");
    if (firstBrace !== -1 && lastBrace > firstBrace) {
      return JSON.parse(cleaned.slice(firstBrace, lastBrace + 1));
    }
    throw new Error("Model did not return valid JSON.");
  }
}

async function fetchWithTimeout(url, options, timeoutMs = 60000, onTick = null) {
  const controller = new AbortController();
  const start = Date.now();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  const ticker = onTick
    ? setInterval(() => {
        const elapsed = Math.round((Date.now() - start) / 1000);
        onTick(elapsed);
      }, 1000)
    : null;

  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error(`Timed out after ${Math.round(timeoutMs / 1000)}s`);
    }
    throw err;
  } finally {
    clearTimeout(timer);
    if (ticker) clearInterval(ticker);
  }
}

function buildGooglePayloadForModel(modelName, compressed) {
  const isGemma = /gemma/i.test(modelName);
  const promptText = `${buildExtractionSystemPrompt()}\n\nExtract all Shift4 / SkyTab POS tickets in this photo into the strict JSON format with top-level key "tickets". Output ONLY valid JSON.`;

  if (isGemma) {
    // Gemma-3-27b-it requires prompt inside user contents (does not support systemInstruction or responseMimeType)
    return {
      contents: [
        {
          role: "user",
          parts: [
            {
              inlineData: {
                mimeType: compressed.mimeType,
                data: compressed.base64Data
              }
            },
            { text: promptText }
          ]
        }
      ],
      generationConfig: {
        temperature: 0
      }
    };
  }

  // Backup: gemini-3.8-flash
  return {
    systemInstruction: {
      parts: [{ text: buildExtractionSystemPrompt() }]
    },
    contents: [
      {
        role: "user",
        parts: [
          {
            inlineData: {
              mimeType: compressed.mimeType,
              data: compressed.base64Data
            }
          },
          {
            text: "Extract all Shift4 / SkyTab POS tickets in this photo into the strict JSON format."
          }
        ]
      }
    ],
    generationConfig: {
      temperature: 0,
      responseMimeType: "application/json"
    }
  };
}

async function callGoogleVisionCascade(compressed, apiKey, onProgress = () => {}) {
  const modelErrors = [];
  const { modelsToTry } = await discoverLiveGoogleCascade(apiKey);

  for (const modelName of modelsToTry) {
    const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(modelName)}:generateContent?key=${encodeURIComponent(apiKey)}`;
    const payload = buildGooglePayloadForModel(modelName, compressed);

    onProgress(`⚡ Scanning with ${modelName}...`);
    let res;
    try {
      res = await fetchWithTimeout(
        endpoint,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        },
        45000,
        (sec) => onProgress(`⚡ Waiting on ${modelName} (${sec}s elapsed)...`)
      );
    } catch (timeoutErr) {
      if (modelName === HYDROGEN_MODEL) recordHydrogenFailure();
      modelErrors.push(`(${modelName}): ${timeoutErr.message}`);
      continue;
    }

    if (res.ok) {
      const data = await res.json();
      const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
      const parsed = extractJsonObject(text);
      const tickets = Array.isArray(parsed.tickets) ? parsed.tickets : [parsed];
      lastWorkingGoogleModel = modelName;
      if (modelName === HYDROGEN_MODEL) recordHydrogenSuccess();
      console.log(`✅ OCR succeeded with model: ${modelName}`, tickets);
      return { tickets, modelName };
    }

    if (modelName === HYDROGEN_MODEL) recordHydrogenFailure();
    const errText = await res.text();
    modelErrors.push(`(${modelName} • HTTP ${res.status}): ${errText}`);
  }

  const masked = apiKey.length > 8 ? `${apiKey.slice(0, 6)}...${apiKey.slice(-3)} (len ${apiKey.length})` : apiKey;
  throw new Error(
    `Vision scan failed with key [${masked}]: ${modelErrors.join(" → ")}`
  );
}

async function callGrokVision(compressed, apiKey, onProgress = () => {}) {
  const endpoint = "https://api.x.ai/v1/chat/completions";
  let candidateModels = ["grok-2-vision-1212", "grok-2-vision-latest"];

  try {
    const modelsRes = await fetch("https://api.x.ai/v1/models", {
      headers: { Authorization: `Bearer ${apiKey}` }
    });
    if (modelsRes.ok) {
      const mData = await modelsRes.json();
      const visionIds = (mData.data || [])
        .map((m) => m.id)
        .filter((id) => /vision/i.test(id));
      if (visionIds.length > 0) {
        candidateModels = [...new Set([...visionIds, ...candidateModels])];
      }
    }
  } catch (_) {}

  const errors = [];
  for (const modelId of candidateModels) {
    onProgress(`⚡ Scanning with xAI Grok (${modelId})...`);
    const payload = {
      model: modelId,
      temperature: 0,
      messages: [
        { role: "system", content: buildExtractionSystemPrompt() },
        {
          role: "user",
          content: [
            {
              type: "image_url",
              image_url: {
                url: `data:${compressed.mimeType};base64,${compressed.base64Data}`,
                detail: "high"
              }
            },
            {
              type: "text",
              text: "Extract all Shift4 / SkyTab POS tickets in this photo into strict JSON with top-level key 'tickets'. Output raw JSON only."
            }
          ]
        }
      ]
    };

    let res;
    try {
      res = await fetchWithTimeout(
        endpoint,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`
          },
          body: JSON.stringify(payload)
        },
        40000,
        (sec) => onProgress(`⚡ Waiting on xAI Grok (${modelId} • ${sec}s elapsed)...`)
      );
    } catch (timeoutErr) {
      errors.push(`(${modelId}): ${timeoutErr.message}`);
      continue;
    }

    if (res.ok) {
      const data = await res.json();
      const content = data?.choices?.[0]?.message?.content || "{}";
      const parsed = extractJsonObject(content);
      const tickets = Array.isArray(parsed.tickets) ? parsed.tickets : [parsed];
      console.log(`✅ OCR succeeded with model: ${modelId}`, tickets);
      return { tickets, modelName: modelId };
    }

    const errText = await res.text();
    console.warn(`⚠️ xAI Grok (${modelId}) HTTP ${res.status}:`, errText);
    errors.push(`(${modelId} • ${res.status}): ${errText}`);
    if (res.status === 401 || res.status === 403) break;
  }

  throw new Error(`Grok Vision API error: ${errors.join(" → ")}`);
}

export function isValidShift4OrderNumber(orderNum) {
  const clean = String(orderNum || "").replace(/^#/, "").trim();
  return /^\d{4,}$/.test(clean) && Number(clean) >= 2000;
}

/**
 * Deterministic Post-OCR Verifier & Local Knowledge Enricher.
 * Guarantees that every rule in Part 1, Part 2, and Part 3 is enforced consistently.
 */
export function normalizeAndVerifyTicket(raw, mapRules, previewUrl = null, batchIndex = 0) {
  const nowIso = new Date().toISOString();
  const dynamicSeed = `${Date.now()}_${batchIndex}`;
  const orderNumber = String(raw.orderNumber || "").replace(/^#/, "").trim() || "UNREAD";
  const validOrderNum = isValidShift4OrderNumber(orderNumber);

  const deliverySurcharge = Number(raw.deliverySurcharge ?? raw.surcharge ?? 0);
  const explicitDelivery = Boolean(raw.isDelivery) || deliverySurcharge >= 3.0;

  // STRICT RULE 1: Non-Delivery Filter
  if (!explicitDelivery) {
    return {
      id: `tkt_${dynamicSeed}`,
      orderNumber,
      isDelivery: false,
      ignoredBanner: `Order #${orderNumber} - PICKUP / IN-HOUSE (Ignore)`
    };
  }

  const streetRaw = (raw.streetAddress || raw.address?.rawStreet || "Unknown Street").trim();
  const normalizedStreetKey = streetRaw.toUpperCase().replace(/[.,#]/g, "").replace(/\s+/g, " ").trim();

  // Match against local-map-rules.json
  const matchedRule = findMatchingAddressRule(normalizedStreetKey, raw.customerName || "", mapRules);

  // Rule #3: Special Delivery Instructions between street line and "Conrad, MT"
  const specialInstructions =
    raw.specialDeliveryInstructions &&
    String(raw.specialDeliveryInstructions).trim() !== "" &&
    String(raw.specialDeliveryInstructions).trim().toLowerCase() !== "none"
      ? String(raw.specialDeliveryInstructions).trim()
      : "None";

  // Part 2 Rule: Never snap to an alley or rear parking lot UNLESS Rule #3 contains "alley" or "back"
  const allowAlleyAccess = ALLEY_KEYWORD_REGEX.test(specialInstructions);

  // Payment & Total Due formatting
  const isPaidOnline =
    raw.paymentType === "PAID_ONLINE" ||
    /st-online|paid online|online/i.test(String(raw.paymentMethod || raw.paymentType || ""));
  const totalDue = isPaidOnline ? 0.0 : Number(raw.totalDue ?? 0);
  const onlineTip = Number(raw.onlineTip ?? 0);

  const paymentBanner = isPaidOnline
    ? `CC (Paid Online) — $0.00 Due`
    : `COLLECT PAYMENT (Cash or In-Person CC) — $${totalDue.toFixed(2)} Due`;

  // Order Summary & Deterministic Alert Scanner
  const pizzas = Array.isArray(raw.pizzas) ? raw.pizzas : [];
  const otherItems = Array.isArray(raw.otherItems) ? raw.otherItems : [];
  const pizzaTotalCount = pizzas.reduce((sum, p) => sum + Number(p.qty || 1), 0);
  const otherTotalCount = otherItems.reduce((sum, item) => sum + Number(item.qty || 1), 0);

  const specialAlerts = buildSpecialAlerts(pizzas, otherItems, raw.rawAlertLines || [], matchedRule);
  if (!validOrderNum) {
    specialAlerts.unshift({
      category: "SOUP_SALAD_DRINK",
      isOrderNumWarning: true,
      bannerText: `INVALID ORDER # (#${orderNumber}) — Expected #2000+. Ticket clipped on board? Re-snap or tap ✏️ Edit!`
    });
  }

  // Fee & Distance Check:
  // Actual delivery fee ($3.00 standard up to $10.00+)
  const actualFee = deliverySurcharge >= 3.0 ? deliverySurcharge : 3.0;
  const extraFeeOverStandard = Math.max(0, Number((actualFee - 3.0).toFixed(2)));
  const isExtendedZone = Boolean(matchedRule?.isExtendedDistance);
  // Capture cases where we SHOULD charge more (extended distance) but surcharge was NOT over $3.00
  const underchargedDistanceFlag = isExtendedZone && actualFee <= 3.0;

  // Resolve Navigation Coordinates (Custom Override Pin vs Front Street Curb vs Alley Allowed)
  const routing = resolveTicketCoordinates(streetRaw, matchedRule, allowAlleyAccess, mapRules);

  return {
    id: `tkt_${dynamicSeed}`,
    orderNumber,
    createdAt: nowIso,
    previewUrl,
    isDelivery: true,
    ignoredBanner: null,
    customerName: (raw.customerName || "Valued Customer").trim(),
    customerPhone: (raw.customerPhone || "").trim(),
    address: {
      rawStreet: streetRaw,
      normalizedKey: matchedRule ? matchedRule.normalizedKey : normalizedStreetKey,
      city: mapRules?.defaultCity || "Conrad",
      state: mapRules?.defaultState || "MT",
      zip: mapRules?.defaultZip || "59425",
      fullFormatted: `${streetRaw}, ${mapRules?.defaultCity || "Conrad"}, ${mapRules?.defaultState || "MT"} ${mapRules?.defaultZip || "59425"}`
    },
    specialInstructions,
    allowAlleyAccess,
    routing,
    payment: {
      status: isPaidOnline ? "PAID_ONLINE" : "COLLECT",
      amountDue: totalDue,
      onlineTip,
      displayBanner: paymentBanner
    },
    deliveryFee: {
      chargedAmount: actualFee,
      standardBase: 3.0,
      extraOverStandard: extraFeeOverStandard,
      isExtendedZone,
      recommendedFee: matchedRule?.recommendedFee || 3.0,
      underchargedWarning: underchargedDistanceFlag
    },
    orderSummary: {
      pizzaCount: pizzaTotalCount,
      pizzas: pizzas.map((p) => ({
        qty: Number(p.qty || 1),
        name: p.name || "Pizza",
        size: p.size || "Lg",
        crust: p.crust || "Regular",
        optionsLines: Array.isArray(p.optionsLines) ? p.optionsLines : []
      })),
      otherItemCount: otherTotalCount,
      otherItems: otherItems.map((it) => ({
        qty: Number(it.qty || 1),
        name: it.name || "Item",
        modifierLines: Array.isArray(it.modifierLines) ? it.modifierLines : []
      }))
    },
    specialAlerts,
    status: "On Order",
    selectedForRun: false,
    runId: null,
    smsPreDepartureSent: false,
    metrics: {
      mileageMiles: null,
      driveTimeMinutes: null,
      startDeliveryAt: null,
      endDeliveryAt: null,
      deliveredAt: null
    },
    postRushReview: {
      flagged: false,
      orderNumber,
      note: ""
    },
    financials: {
      driverDeliveryFeeEarned: actualFee,
      cashCollected: 0,
      onlineTip,
      cashTip: 0
    }
  };
}

function findMatchingAddressRule(normalizedStreetKey, customerName, mapRules) {
  const rules = mapRules?.addressRules || [];
  const upperCustomer = (customerName || "").toUpperCase();
  for (const rule of rules) {
    if (rule.normalizedKey === normalizedStreetKey) return rule;
    if (Array.isArray(rule.matchPatterns)) {
      for (const pat of rule.matchPatterns) {
        const upPat = pat.toUpperCase();
        if (normalizedStreetKey.includes(upPat) || upperCustomer.includes(upPat)) {
          return rule;
        }
      }
    }
  }
  return null;
}

function buildSpecialAlerts(pizzas, otherItems, rawAlertLines, matchedRule) {
  const alerts = [];
  const seen = new Set();

  const pushUnique = (category, bannerText) => {
    const key = `${category}::${bannerText.toUpperCase()}`;
    if (!seen.has(key)) {
      seen.add(key);
      alerts.push({ category, bannerText });
    }
  };

  // 1. Check Pizzas for "Pizza Options:" or "!"
  for (const p of pizzas) {
    for (const opt of p.optionsLines || []) {
      const trimmed = String(opt).trim();
      if (!trimmed) continue;
      if (/pizza options/i.test(trimmed) || trimmed.includes("!")) {
        pushUnique("PIZZA_OPTION", trimmed.startsWith("Pizza Options") ? trimmed : `Pizza Options: ${trimmed}`);
      } else if (trimmed.startsWith("*")) {
        pushUnique("ASTERISK_NOTE", trimmed);
      }
    }
  }

  // 2. Check Other Items for Salads, Soups ("Cup Of Soup"), Drinks, or "*" modifiers
  for (const item of otherItems) {
    const name = String(item.name || "").trim();
    if (SOUP_SALAD_DRINK_REGEX.test(name)) {
      pushUnique("SOUP_SALAD_DRINK", `DON'T FORGET: ${item.qty || 1}x ${name.toUpperCase()}`);
    }
    for (const mod of item.modifierLines || []) {
      const trimmed = String(mod).trim();
      if (!trimmed) continue;
      if (trimmed.startsWith("*")) {
        pushUnique("ASTERISK_NOTE", trimmed);
      } else if (trimmed.includes("!")) {
        pushUnique("PIZZA_OPTION", trimmed);
      } else if (SOUP_SALAD_DRINK_REGEX.test(trimmed)) {
        pushUnique("SOUP_SALAD_DRINK", `DON'T FORGET: ${trimmed.toUpperCase()}`);
      }
    }
  }

  // 3. Scan rawAlertLines for anything starting with "*", containing "!", or matching Soup/Salad/Drink
  for (const line of rawAlertLines) {
    const trimmed = String(line || "").trim();
    if (!trimmed) continue;
    if (trimmed.startsWith("*")) {
      pushUnique("ASTERISK_NOTE", trimmed);
    } else if (/pizza options/i.test(trimmed) || trimmed.includes("!")) {
      pushUnique("PIZZA_OPTION", trimmed);
    } else if (SOUP_SALAD_DRINK_REGEX.test(trimmed)) {
      pushUnique("SOUP_SALAD_DRINK", `DON'T FORGET: ${trimmed.toUpperCase()}`);
    }
  }

  // 4. Attach Building Pre-Departure Alert if applicable
  if (matchedRule?.driverNotes?.permanentAlert) {
    pushUnique("BUILDING_RULE", matchedRule.driverNotes.permanentAlert);
  }

  return alerts;
}

function resolveTicketCoordinates(streetRaw, matchedRule, allowAlleyAccess, mapRules) {
  if (matchedRule) {
    const geo = matchedRule.geofence || {};
    const destPin =
      geo.snapPolicy === "CUSTOM_PIN" && geo.customOverridePin
        ? geo.customOverridePin
        : geo.frontCurbPin || { lat: 48.1695, lng: -111.9435 };

    return {
      ruleMatched: matchedRule.displayName,
      trackSide: matchedRule.trackSide || "SHOP_SIDE",
      snapMode: allowAlleyAccess ? "ALLEY_EXPLICITLY_REQUESTED" : geo.snapPolicy || "FRONT_CURB_CENTERLINE",
      destinationPin: destPin,
      approachWaypoint: geo.approachWaypoint || null,
      requireSmsBeforeStart: Boolean(matchedRule.preDepartureRule?.requireSmsBeforeStart),
      smsButtonLabel: matchedRule.preDepartureRule?.buttonLabel || null,
      smsTemplate: matchedRule.preDepartureRule?.smsTemplate || null,
      driverNotes: matchedRule.driverNotes || null,
      tipHistory: matchedRule.tipHistory || null
    };
  }

  // Default Conrad front-street curb geocoding heuristic (no alley snapping unless Rule #3 says alley/back)
  const isWestOfTracks = /\b(bench|west|w\s+|RR|rural|hwy\s*91)\b/i.test(streetRaw);
  return {
    ruleMatched: null,
    trackSide: isWestOfTracks ? "ACROSS_TRACKS" : "SHOP_SIDE",
    snapMode: allowAlleyAccess ? "ALLEY_EXPLICITLY_REQUESTED" : "FRONT_CURB_CENTERLINE (No Alley)",
    destinationPin: null,
    approachWaypoint: null,
    requireSmsBeforeStart: false,
    smsButtonLabel: null,
    smsTemplate: null,
    driverNotes: null,
    tipHistory: null
  };
}

/**
 * Generates a realistic multi-ticket Shift4 / SkyTab test batch seeded dynamically from Date.now()
 * (Never uses static 0101 / trivial IDs).
 */
export function generateDynamicShiftBatch(mapRules) {
  const seedBase = Number(String(Date.now()).slice(-3));
  const rawBatch = [
    {
      // Ticket 1: Tamarack Apartments, Paid Online with generous pre-tip, Cup of Soup + Pie Cut!!! + * Salt The Fries :)
      orderNumber: String(seedBase + 11),
      isDelivery: true,
      customerName: " Sarah Jenkins",
      customerPhone: "406-278-5512",
      streetAddress: "600 S Main St (Tamarack Apartments)",
      specialDeliveryInstructions: "Apt 204 - call or text on way",
      deliverySurcharge: 3.00,
      paymentType: "PAID_ONLINE",
      paymentMethod: "Credit - st-online",
      totalDue: 0.00,
      onlineTip: 6.50,
      pizzas: [
        {
          qty: 1,
          name: "Coach's Special",
          size: "Lg",
          crust: "Double Crust",
          optionsLines: ["Pizza Options: Pie Cut!!!"]
        }
      ],
      otherItems: [
        { qty: 1, name: "Cup Of Soup", modifierLines: [] },
        { qty: 1, name: "Seasoned Fries", modifierLines: ["* Salt The Fries :)"] }
      ],
      rawAlertLines: ["Pizza Options: Pie Cut!!!", "* Salt The Fries :)", "Cup Of Soup"]
    },
    {
      // Ticket 2: The Lodge (Custom GPS Entry Pin Override + Unpaid Cash/CC Collect + 2-Liter Pepsi + Garden Salad)
      orderNumber: String(seedBase + 14),
      isDelivery: true,
      customerName: "Walt Miller",
      customerPhone: "406-278-9940",
      streetAddress: "310 S Virginia St - The Lodge",
      specialDeliveryInstructions: "None",
      deliverySurcharge: 3.00,
      paymentType: "COLLECT",
      totalDue: 34.50,
      onlineTip: 0,
      pizzas: [
        {
          qty: 1,
          name: "Pepperoni & Mushroom",
          size: "Med",
          crust: "Regular",
          optionsLines: []
        },
        {
          qty: 1,
          name: "Canadian Bacon",
          size: "Sm",
          crust: "Thin",
          optionsLines: ["* Well Done Crust!"]
        }
      ],
      otherItems: [
        { qty: 1, name: "Garden Salad", modifierLines: ["* Extra Ranch on side"] },
        { qty: 1, name: "2-Liter Pepsi", modifierLines: [] }
      ],
      rawAlertLines: ["* Well Done Crust!", "* Extra Ranch on side", "Garden Salad", "2-Liter Pepsi"]
    },
    {
      // Ticket 3: Extended Distance Across Tracks where surcharge was NOT over $3.00 (Should trigger Post-Rush Review prompt)
      orderNumber: String(seedBase + 18),
      isDelivery: true,
      customerName: "Dave Larson",
      customerPhone: "406-278-3319",
      streetAddress: "1480 W Bench Rd",
      specialDeliveryInstructions: "Park by red shop in the back alley",
      deliverySurcharge: 3.00,
      paymentType: "PAID_ONLINE",
      paymentMethod: "Credit - st-online",
      totalDue: 0.00,
      onlineTip: 5.00,
      pizzas: [
        {
          qty: 2,
          name: "Meat Lovers",
          size: "Lg",
          crust: "Double Crust",
          optionsLines: []
        }
      ],
      otherItems: [],
      rawAlertLines: []
    },
    {
      // Ticket 4: Non-Delivery Pickup Ticket (Must be filtered out strictly as PICKUP / IN-HOUSE (Ignore))
      orderNumber: String(seedBase + 19),
      isDelivery: false,
      deliverySurcharge: 0.00,
      customerName: "Walk-In Pickup"
    }
  ];

  return rawBatch.map((raw, idx) => normalizeAndVerifyTicket(raw, mapRules, null, idx));
}
