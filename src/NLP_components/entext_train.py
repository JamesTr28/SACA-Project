# install (first time only)
# pip install -U spacy negspacy dateparser regex spacy-lookups-data
# python -m spacy download en_core_web_sm

import os, sys, csv, re, json
import regex as rxx
import dateparser
import spacy
from spacy.matcher import PhraseMatcher
from collections import defaultdict
from datetime import datetime

# ---------- Robust spaCy loader (auto fallback) ----------
from dataclasses import dataclass

@dataclass
class NlpCtx:
    nlp: any
    symptom_matcher: any
    disease_matcher: any

def bootstrap_pipeline() -> NlpCtx:
    # Wrap already-initialized globals into a context
    return NlpCtx(
        nlp=nlp,
        symptom_matcher=symptom_matcher,
        disease_matcher=disease_matcher
    )
def get_nlp():
    try:
        return spacy.load("en_core_web_sm", disable=["ner"])
    except Exception:
        try:
            import spacy.cli
            spacy.cli.download("en_core_web_sm")
            return spacy.load("en_core_web_sm", disable=["ner"])
        except Exception:
            nlp = spacy.blank("en")
            try:
                nlp.add_pipe("lemmatizer", config={"mode": "rule"})
            except Exception:
                pass
            if "sentencizer" not in nlp.pipe_names:
                nlp.add_pipe("sentencizer")
            return nlp

nlp = get_nlp()
print("spaCy pipeline:", nlp.pipe_names)

# ---------- Locate CSV path ----------
# ---------- Locate data files & load dictionaries with priority ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TWO_COL = os.path.join(BASE_DIR, "Disease_symptom_and_patient_profile_dataset.csv")
DICT_CSV        = os.path.join(BASE_DIR, "dictionary.csv")       # preferred
WIDE_CSV        = os.path.join(BASE_DIR, "cleaned_wide.csv")     # optional wide matrix

# CLI for uploaded CSV 
csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TWO_COL

def normalize_term(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[_/]+", " ", s)
    s = re.sub(r"[^a-z0-9 \-']+", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\.+$", "", s)  # regurgitation.1 -> regurgitation
    return s

def _sniff_delimiter(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        sample = f.read(4096)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
            return dialect.delimiter
        except Exception:
            return ","

def load_terms_prefer_dictionary():
    symptom_terms, disease_terms = set(), set()

    # 1) dictionary.csv (preferred)
    if os.path.exists(DICT_CSV):
        sep = _sniff_delimiter(DICT_CSV)
        with open(DICT_CSV, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=sep)
            headers = [h.strip() for h in (reader.fieldnames or [])]
            dcol = next((h for h in headers if h.lower() in ("disease", "diseases", "diagnosis", "condition")), None)
            scol = next((h for h in headers if h.lower() in ("symptom", "symptoms")), None)
            if not dcol or not scol:
                raise ValueError("dictionary.csv must have columns 'Disease' and 'Symptom'.")
            for row in reader:
                dis = normalize_term(row.get(dcol, ""))
                sym = normalize_term(row.get(scol, ""))
                if dis: disease_terms.add(dis)
                if sym and len(sym) > 2: symptom_terms.add(sym)
        return symptom_terms, disease_terms, "dictionary.csv"

    # 2) cleaned_wide.csv (wide matrix: first col disease, others symptoms 0/1)
    if os.path.exists(WIDE_CSV):
        sep = _sniff_delimiter(WIDE_CSV)
        with open(WIDE_CSV, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=sep)
            rows = list(reader)
        if not rows:
            raise ValueError("cleaned_wide.csv is empty.")
        headers = [normalize_term(h) for h in rows[0]]
        # diseases
        for r in rows[1:]:
            if r and r[0]:
                disease_terms.add(normalize_term(r[0]))
        # symptoms from header (skip first col)
        for h in headers[1:]:
            if h and len(h) > 2:
                symptom_terms.add(h)
        return symptom_terms, disease_terms, "cleaned_wide.csv"

    # 3) fallback: two-column dataset (Disease, Symptom)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"No dictionary.csv or cleaned_wide.csv found.\n"
            f"Also missing fallback file: {csv_path}"
        )
    sep = _sniff_delimiter(csv_path)
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=sep)
        headers = [h.strip() for h in (reader.fieldnames or [])]
        dcol = next((h for h in headers if h.lower() in ("disease","diseases")), None)
        scol = next((h for h in headers if h.lower() in ("symptom","symptoms")), None)
        if not dcol or not scol:
            raise ValueError(f"CSV headers not found. Got: {headers}. "
                             f"Expected 'Disease' and 'Symptom' columns.")
        for row in reader:
            dis = normalize_term(row.get(dcol, ""))
            sym = normalize_term(row.get(scol, ""))
            if dis: disease_terms.add(dis)
            # symptom could be 'a;b and c/or d'
            for s in re.split(r"[;,/]|(?:\band\b)|(?:\bor\b)", sym):
                s = normalize_term(s)
                if len(s) > 2:
                    symptom_terms.add(s)
    return symptom_terms, disease_terms, os.path.basename(csv_path)

# ---- actually load dictionaries ----
symptom_terms, disease_terms, source_used = load_terms_prefer_dictionary()
print(f"Loaded dictionary from {source_used} → diseases: {len(disease_terms)}, symptoms: {len(symptom_terms)}")

# ---- optional seeds (keep as supplement) ----
seed_symptoms = {
    "chest pain", "shortness of breath", "fever", "mild fever",
    "headache", "cough", "sore throat", "back pain", "lower back pain",
    "nausea", "vomiting", "diarrhea", "runny nose", "wheezing", "chest tightness"
}
seed_diseases = {"flu", "pneumonia", "asthma", "hypertension", "diabetes", "covid-19", "common cold"}

symptom_terms |= {s.lower() for s in seed_symptoms}
disease_terms |= {d.lower() for d in seed_diseases}

# filter trivial
STOP_LIKE = {"and","or","the","a","an","with","of","in","to","on"}
symptom_terms = {t for t in symptom_terms if t not in STOP_LIKE and len(t) > 2}
disease_terms = {t for t in disease_terms if t not in STOP_LIKE and len(t) > 2}



## additional hardcoded seed terms (fix bug disease output empty)
# ---- Fallback seed terms so tests work even with a tiny CSV ----
seed_symptoms = {
    "chest pain", "shortness of breath", "fever", "mild fever",
    "headache", "cough", "sore throat", "back pain", "lower back pain",
    "nausea", "vomiting", "diarrhea", "runny nose", "wheezing", "chest tightness"
}

#temp 
seed_diseases = {"flu", "pneumonia", "asthma", "hypertension", "diabetes", "covid-19", "common cold"}


symptom_terms |= {s.lower() for s in seed_symptoms}
disease_terms |= {d.lower() for d in seed_diseases}

# remove too short/common words
stop_like = {"and","or","the","a","an","with","of","in","to","on"}
symptom_terms = {t for t in symptom_terms if t not in stop_like and len(t) > 2}
disease_terms = {t for t in disease_terms if t not in stop_like and len(t) > 2}

# ========== 3) PhraseMatcher ==========
symptom_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
disease_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

symptom_patterns = [nlp.make_doc(t) for t in sorted(symptom_terms)]
disease_patterns = [nlp.make_doc(t) for t in sorted(disease_terms)]

#avoid OOM,limit to 5000 patterns
symptom_matcher.add("SYMPTOM", symptom_patterns[:5000])
disease_matcher.add("DISEASE", disease_patterns[:5000])

# ========== 4)  Rules: Denial, Severity, Duration, Body, Vital Signs ==========
NEG_TRIGGERS = {"no","not","without","deny","denies","denied","never","none"}
SEVERITY_WORDS = {
    "mild":"mild","slight":"mild","a little":"mild","bit":"mild",
    "moderate":"moderate","worse":"moderate","getting worse":"moderate",
    "severe":"severe","intense":"severe","extreme":"severe","unbearable":"severe",
    "excruciating":"severe","unable to":"severe"
}
BODY_SITES = {
    "head","throat","chest","abdomen","stomach","back","lower back","shoulder",
    "arm","hand","knee","leg","ankle","foot","eye","ear","nose","jaw","tooth"
}

# Keep only meaningful temporal anchors (no bare 'for'/'since' as tokens)
# TIME_WORDS = {"today","yesterday","tonight","this morning","this afternoon","last night","since","for","ago"}
TIME_WORDS = {"today","yesterday","tonight","this morning","this afternoon","last night","last week","last month"}


RISK_KEYWORDS = {"smoker","pregnant","diabetic","asthma","hypertensive"}

# Vital Signs/Values: Body Temperature, Heart Rate, Blood Pressure, Blood Glucose, Blood Oxygen Saturation
TEMP_RE = re.compile(r"(?:temp(?:erature)?\s*[:=]?\s*)?(\d{2}\.\d|\d{2})(?:\s*°?\s*[cf])", re.I)
HR_RE   = re.compile(r"(?:hr|heart\s*rate)\s*[:=]?\s*(\d{2,3})", re.I)
BP_RE   = re.compile(r"(?:bp|blood\s*pressure)\s*[:=]?\s*(\d{2,3})\s*/\s*(\d{2,3})", re.I)
SPO2_RE = re.compile(r"(?:spo2|o2\s*saturation|oxygen)\s*[:=]?\s*(\d{2,3})\s*%", re.I)
GLU_RE  = re.compile(r"(?:glucose|bgl|blood\s*sugar)\s*[:=]?\s*(\d{2,3})", re.I)

# # Duration
# DUR_RE = rxx.compile(r"(?:(for|since)\s+(?:\d+\s+(?:minute|hour|day|week|month|year)s?|yesterday|today|last\s+night))|(\d+\s*(?:d|w|m|y)\b)", rxx.I)

# Duration: capture phrases like "for 3 days", "since yesterday", "2d", "1 week" Duration logic updated
DUR_RE = rxx.compile(
    r"(?:(for|since)\s+(?:\d+\s+(?:minute|hour|day|week|month|year)s?|yesterday|today|last\s+night))"
    r"|(\b\d+\s*(?:minutes?|hours?|days?|weeks?|months?|years?)\b)"
    r"|(\b\d+\s*(?:d|w|m|y)\b)",
    rxx.I
)

#duplicate function removed
# def normalize_duration(span_text: str):
#     t = span_text.lower().strip()
#     # return both the raw phrase and a numeric approximation in days when possible
#     days = None
#     # map units
#     unit_map = {
#         "minute": 1/1440, "minutes": 1/1440,
#         "hour": 1/24, "hours": 1/24,
#         "day": 1, "days": 1,
#         "week": 7, "weeks": 7,
#         "month": 30, "months": 30,
#         "year": 365, "years": 365
#     }
#     m = re.search(r"(\d+)\s*(minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years|d|w|m|y)\b", t)
#     if m:
#         n = int(m.group(1)); u = m.group(2)
#         if u in unit_map:
#             days = n * unit_map[u]
#         elif u == "d": days = n
#         elif u == "w": days = n * 7
#         elif u == "m": days = n * 30
#         elif u == "y": days = n * 365
#     elif "since yesterday" in t:
#         days = 1
#     elif "since today" in t:
#         days = 0
#     return {"text": span_text, "days": days}

# def window_has_negation(doc, start_i, end_i, win=3):
#     # If a negation trigger word is present within the matching window, it is treated as negation.
#     left = max(0, start_i - win)
#     right = min(len(doc), end_i + win)
#     for i in range(left, right):
#         if doc[i].lemma_.lower() in NEG_TRIGGERS:
#             return True
#     return False

# def window_has_negation(doc, start_i, end_i=None, win=4):
#     # Only scan tokens to the LEFT of the span start
#     left = max(0, start_i - win)
#     for i in range(left, start_i):
#         if doc[i].lemma_.lower() in {"no","not","without","deny","denies","denied","never","none"}:
#             return True
#     return False

NEG_BOUNDARIES = {",",";","but","however","though","yet"}

def window_has_negation(doc, start_i, end_i=None, win=6):
    """
    Left-only negation: Starting from the point of mention, proceed leftward for up to win tokens,
    stopping early upon encountering boundary words (such as but/however).
    """
    for i in range(start_i - 1, max(-1, start_i - win) - 1, -1):
        t = doc[i].text.lower()
        if t in NEG_BOUNDARIES:
            break
        if doc[i].lemma_.lower() in NEG_TRIGGERS:
            return True
    return False


def pick_severity(text):
    t = text.lower()

    # Explicit keywords
    for k, v in SEVERITY_WORDS.items():
        if k in t:
            return v

    # Numeric pain scale
    m = re.search(r"pain\s*(\d|10)\s*/\s*10", t)
    if m:
        val = int(m.group(1))
        if val <= 3: return "mild"
        if val <= 6: return "moderate"
        return "severe"

    # Temp thresholds
    m = TEMP_RE.search(text)
    if m:
        temp = float(m.group(1))
        c = (temp - 32) * 5/9 if "f" in t else temp
        if c >= 39.0: return "severe"
        if c >= 38.0: return "moderate"

    # Red-flag symptom pairs
    red_flag_pairs = [
        ("chest pain", "shortness of breath"),
    ]
    for a, b in red_flag_pairs:
        if a in t and b in t:
            return "severe"

    # High vitals (rough heuristics)
    hr_m = HR_RE.search(text)
    if hr_m and int(hr_m.group(1)) >= 120:
        return "moderate"

    bp_m = BP_RE.search(text)
    if bp_m:
        sys_v = int(bp_m.group(1)); dia_v = int(bp_m.group(2))
        if sys_v >= 180 or dia_v >= 120:
            return "severe"
        if sys_v >= 160 or dia_v >= 100:
            return "moderate"

    return None


# predefine of  5)



def normalize_duration(span_text: str):
    """Return {"text": raw, "days": numeric_or_None}."""
    t = span_text.lower().strip()
    days = None
    unit_map = {
        "minute": 1/1440, "minutes": 1/1440,
        "hour": 1/24, "hours": 1/24,
        "day": 1, "days": 1,
        "week": 7, "weeks": 7,
        "month": 30, "months": 30,
        "year": 365, "years": 365
    }
    m = re.search(r"(\d+)\s*(minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years|d|w|m|y)\b", t)
    if m:
        n = int(m.group(1)); u = m.group(2)
        if u in unit_map: days = n * unit_map[u]
        elif u == "d":    days = n
        elif u == "w":    days = n * 7
        elif u == "m":    days = n * 30
        elif u == "y":    days = n * 365
    elif "since yesterday" in t: days = 1
    elif "since today" in t:     days = 0
    return {"text": span_text, "days": days}

def keep_longest_strings(strings):
    """Remove entries that are substrings of other entries (case-insensitive)."""
    ss = sorted(set(strings), key=lambda s: (-len(s), s))
    kept = []
    for s in ss:
        if not any((s != t and s in t) for t in kept):
            kept.append(s)
    return sorted(kept)


# ========== 5) Main extraction function ==========
def extract_features(sentence: str):
    doc = nlp(sentence)
    low = sentence.lower()

    out = {
        "symptoms": [],
        "diseases": [],
        "negated": [],
        "severity": None,
        "duration": [],
        "onset": None,
        "body_site": [],
        "temporal": [],
        "risk_factors": [],
        "vitals": {},
        "age_sex": {},
        "meta": {"text": sentence}
    }

    # ---- vitals ----
    if m := TEMP_RE.search(sentence): out["vitals"]["temperature"] = m.group(0)
    if m := HR_RE.search(sentence):   out["vitals"]["heart_rate"] = int(m.group(1))
    if m := BP_RE.search(sentence):   out["vitals"]["blood_pressure"] = f"{m.group(1)}/{m.group(2)}"
    if m := SPO2_RE.search(sentence): out["vitals"]["spo2"] = int(m.group(1))
    if m := GLU_RE.search(sentence):  out["vitals"]["glucose"] = int(m.group(1))

    # ---- severity ----
    out["severity"] = pick_severity(sentence)

    # ---- duration (normalized) ----
    out["duration"] = []
    for m in DUR_RE.finditer(sentence):
        span = m.group(0)
        if span:
            out["duration"].append(normalize_duration(span))

    # ---- onset ----
    if "sudden" in low or "suddenly" in low: out["onset"] = "sudden"
    elif "gradual" in low or "slowly" in low: out["onset"] = "gradual"

    # ---- temporal anchors (no 'for'/'since' alone) ----
    out["temporal"] = []
    for tw in TIME_WORDS:
        if re.search(rf"\b{re.escape(tw)}\b", low):
            out["temporal"].append(tw)
    out["temporal"] = sorted(set(out["temporal"]))

    # ---- risk factors ----
    out["risk_factors"] = sorted({rk for rk in RISK_KEYWORDS if rk in low})

    # ---- dictionary matches + one-sided negation ----
    sym_matches = symptom_matcher(doc)
    dis_matches = disease_matcher(doc)

    def spans_to_strings(matches):
        spans = []
        for _id, start, end in matches:
            span = doc[start:end]
            spans.append((span.start, span.end, span.text))
        uniq, seen = [], set()
        for s, e, t in spans:
            key = (s, e, t.lower())
            if key not in seen:
                seen.add(key); uniq.append((s, e, t))
        return uniq

    # symptoms
    for s, e, t in spans_to_strings(sym_matches):
        if window_has_negation(doc, s, e, win=4):
            out["negated"].append(t)
        else:
            out["symptoms"].append(t)

    # diseases
    for s, e, t in spans_to_strings(dis_matches):
        if window_has_negation(doc, s, e, win=4):
            out["negated"].append(t)
        else:
            out["diseases"].append(t)

    # ---- normalize + keep longest ----
    out["symptoms"] = keep_longest_strings([normalize_term(x) for x in out["symptoms"]])
    out["diseases"] = keep_longest_strings([normalize_term(x) for x in out["diseases"]])
    out["negated"]  = sorted(set([normalize_term(x) for x in out["negated"]]))

    # ---- remove duplicates ---- bug fix 2
    # ---- conflict resolution: if a term is in both, prefer symptom ----
    dset = set(out["diseases"])
    sset = set(out["symptoms"])
    out["diseases"] = keep_longest_strings(sorted(dset - sset))


    # ---- body sites from NON-negated mentions (plus cautious scan) ----
    body_sites_found = set()

    def site_from_text(txt):
        tl = txt.lower()
        for site in BODY_SITES:
            if re.search(rf"\b{re.escape(site)}\b", tl):
                body_sites_found.add(site)

    for s_txt in out["symptoms"]:
        site_from_text(s_txt)
    for d_txt in out["diseases"]:
        site_from_text(d_txt)


    
    # ---- body sites from cautious scan ----  removed bug happened in test case "No fever but mild headache since yesterday."
    # cautious sentence-level scan: skip if immediately preceded by negation
    # for i, tok in enumerate(doc):
    #     tlo = tok.text.lower()
    #     if tlo in BODY_SITES:
    #         neg_left = any(doc[j].lemma_.lower() in NEG_TRIGGERS for j in range(max(0, i-3), i))
    #         if not neg_left:
    #             body_sites_found.add(tlo)
    

#old logic:
    # out["body_site"] = sorted(body_sites_found)

#new logic: keep longest only
    out["body_site"] = keep_longest_strings(sorted(body_sites_found))


    # ---- age / sex ----
    if m := re.search(r"\b(\d{1,2})-?year-?old\b", low):
        out["age_sex"]["age"] = int(m.group(1))
    if re.search(r"\b(male|man)\b", low):     out["age_sex"]["sex"] = "male"
    if re.search(r"\b(female|woman)\b", low): out["age_sex"]["sex"] = "female"

    return out


# ======== test result ========
tests = [
    "I have severe chest pain and shortness of breath for 3 days, temp 39C.",
    "No fever but mild headache since yesterday.",
    "Patient denies cough or sore throat. HR 120, BP 160/100.",
    "I am a 38-year-old female, sudden lower back pain tonight.",
    "I think it's just flu, not pneumonia."
]

# for t in tests:
#     print(json.dumps(extract_features(t), indent=2))






# fix logic bugs in test cases 
# fix logic bugs in test cases 
RED_FLAG_PAIRS = [("chest pain", "shortness of breath")]

def _has_pair(text, a, b):
    """Case-insensitive check that two critical terms co-occur in raw text."""
    t = (text or "").lower()
    return a in t and b in t

def _fever_from_temp_text(temp_text: str) -> bool:
    """
    Return True if the temperature mention implies fever.
    - Parse numeric value from strings like 'temp 39C' or 'temperature 102F'.
    - Fever threshold: >= 38.0C (or >= 100.4F).
    """
    if not temp_text:
        return False
    m = re.search(r"(\d{2}\.\d|\d{2})", temp_text)
    if not m:
        return False
    try:
        val = float(m.group(1))
    except Exception:
        return False
    is_f = "f" in temp_text.lower()  # crude unit detection
    c = (val - 32) * 5/9 if is_f else val
    return c >= 38.0

def combine_features(out):
    # """
    # Final minimal JSON:
    #   if symptoms exist:
    #     {
    #       "symptoms": [{"name": str, "duration_days": float|int|None}, ...],
    #       "vitals": {...},          # NOTE: 'temperature' removed; fever handled as a symptom
    #       "triage_level": "mild" | "moderate" | "severe"
    #     }
    #   else:
    #     {
    #       "vitals": {...},
    #       "triage_level": "mild" | "moderate" | "severe"
    #     }

    # Rules:
    # - Merge positive symptoms (exclude negated).
    # - If temperature implies fever (>=38C), add "fever" to symptoms and drop raw temperature from vitals.
    # - Attach a single shared duration (days) to every symptom in this sentence.
    # - Triage by red flags, vitals, explicit severity.
    # """
    # 1) duration (shared across this sentence)
    duration_days = None
    cands = [
        d.get("days") for d in out.get("duration", [])
        if isinstance(d, dict) and d.get("days") is not None
    ]
    if cands:
        # conservative choice: the maximum duration mentioned
        duration_days = max(cands)

    # 2) positive symptoms (already normalized by your extractor)
    negated = set(out.get("negated", []))
    positive = [s for s in set(out.get("symptoms", [])) if s and s not in negated]

    # 3) vitals pass-through, but remove raw temperature; convert to 'fever' if needed
    vitals = dict(out.get("vitals", {}))  # shallow copy
    temp_text = vitals.pop("temperature", None)  # always drop raw temperature from output
    if _fever_from_temp_text(temp_text):
        if "fever" not in positive:
            positive.append("fever")

    # 4) red flags and vitals flags
    text = out.get("meta", {}).get("text", "")
    red_flags = []
    if any(_has_pair(text, a, b) for a, b in RED_FLAG_PAIRS):
        red_flags.append("chest pain + shortness of breath")

    vitals_flags = []
    hr = vitals.get("heart_rate")
    if isinstance(hr, int) and hr >= 120:
        vitals_flags.append("tachycardia>=120")

    bp = vitals.get("blood_pressure")
    if isinstance(bp, str):
        try:
            sys_v, dia_v = map(int, bp.split("/"))
            if sys_v >= 180 or dia_v >= 120:
                vitals_flags.append("hypertensive crisis")
            elif sys_v >= 160 or dia_v >= 100:
                vitals_flags.append("marked hypertension")
        except Exception:
            pass

    # 5) triage level
    triage = "mild"
    if red_flags or ("hypertensive crisis" in vitals_flags):
        triage = "severe"
    elif ("marked hypertension" in vitals_flags) or (duration_days is not None and duration_days >= 3) or ("fever" in positive):
        triage = "moderate"

    # explicit severity can upgrade
    if out.get("severity") == "severe":
        triage = "severe"
    elif out.get("severity") == "moderate" and triage == "mild":
        triage = "moderate"

    # 6) build final JSON
    if positive:
        symptoms_json = [{"name": s, "duration_days": duration_days} for s in sorted(set(positive))]
        return {
            "symptoms": symptoms_json,
            "vitals": vitals,          # without 'temperature'
            "triage_level": triage
        }
    else:
        # no positive symptoms → omit symptoms section entirely
        return {
            "vitals": vitals,
            "triage_level": triage
        }

# ===========================
# Public helper functions
# ===========================

def extract_and_combine(text: str) -> dict:
    """
    Process a single sentence:
    1) run rule-based NLP extraction (extract_features)
    2) post-process to the final minimal JSON (combine_features)
    Returns the final JSON dict.
    """
    feats = extract_features(text)
    final = combine_features(feats)
    return final

# Process multiple texts and
def extract_symptom_names(data):
    names = []
    for entry in data:
        symptoms = entry.get('out', {}).get('symptoms', [])
        for symptom in symptoms:
            name = symptom.get('name')
            if name:
                names.append(name)
    return names
def process_texts(texts):
    """
    Process a list of sentences and return list of results:
    [
      {"input_text": <str>, "output": <final_json>},
      ...
    ]
    """
    results = []
    for t in texts:
        if not t or not str(t).strip():
            continue
        out = extract_and_combine(t)
        results.append({"out":out})
        symptoms = extract_symptom_names(results)
    return symptoms



def process_file(input_path: str, encoding: str = "utf-8"):
    """
    Read a plain text file (one sentence per line),
    run processing, and return list of results (same format as process_texts).
    """
    with open(input_path, "r", encoding=encoding) as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    return process_texts(lines)


def save_json(obj, output_path: str, ensure_ascii: bool = False):
    """
    Save any Python object as a pretty JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=ensure_ascii)


def save_ndjson(items, output_path: str, ensure_ascii: bool = False):
    """
    Save a list of dicts as NDJSON (one JSON per line).
    Useful for streaming / large outputs.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=ensure_ascii) + "\n")


# ======== demo / tests ========


# ===========================
# Entry point for file input
# ===========================
if __name__ == "__main__":

    tests = [
        "I have severe chest pain and shortness of breath for 3 days, temp 39C.",
        "No fever but mild headache since yesterday.",
        "Patient denies cough or sore throat. HR 120, BP 160/100.",
        "I am a 38-year-old female, sudden lower back pain tonight.",
        "I think it's just flu, not pneumonia."
    ]
    print("\n=== Test cases ===")
    print(process_texts(tests))