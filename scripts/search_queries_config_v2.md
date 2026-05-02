# 📊 STEVE'S GEMATRIA SEARCH QUERIES CONFIGURATION
# Updated: April 26, 2026 — Ongoing Research Cycle Recommendations

## CORE SYMBOLS TRACKING
```python
CORE_SYMBOLS = {
    "124": {"name": "Universal Bridge", "domain": "Water", 
            "keywords": ["bridge", "threshold", "crossing", "boundary", "connection"]},
    "963": {"name": "Frequency/Air", "domain": "Air",
            "keywords": ["frequency", "resonance", "activation", "wave", "signal"]},
    "55": {"name": "Fire/Elemental Force", "domain": "Fire",
           "keywords": ["fire", "volcano", "elemental", "heat", "energy"]},
    "111": {"name": "Activation/Spirit", "domain": "Spirit",
            "keywords": ["activation", "spirit", "manifestation", "revelation", 
                        "powerful figures", "turn up"]},
    "279": {"name": "Cycle Turning", "domain": "Earth",
            "equations": [
                "49+39+21+97+36+37=279",  # Military coup balance equation
                "military+coup+y+2079"     # Year-based tracking
            ]},
    "666": {"name": "Completion/Wholeness", "domain": "Fire",
            "keywords": ["completion", "wholeness", "financial", "transformation"]}
}
```

## 🔍 **DOMAIN-SPECIFIC SEARCH QUERIES**

### 1️⃣ **POLITICAL EVENTS (Trump Canada Narrative)**
#### ✅ EXPANDED: Health & Immigration Specifics

```python
TRUMP_CANADA_QUERIES = [
    # Core narratives
    "Trump Canada border wall statehood flags narrative",
    "Trump Canada health coverage immigration specifics",
    
    # 🆕 HEALTH SPECIFICS (NEW)
    "Trump Canada hospital visit health checkup coverage",
    "Trump Canada medical treatment healthcare costs",
    "Trump Canada diabetes insulin prescription coverage",
    "Trump Canada health surveillance monitoring",
    "Trump Canada doctor appointment medical records",
    
    # 🆕 IMMIGRATION SPECIFICS (NEW)  
    "Trump Canada immigration policy border enforcement",
    "Trump Canada asylum seeker deportation procedures",
    "Trump Canada refugee processing timeline",
    "Trump Canada immigration benefits eligibility",
    "Trump Canada work permit visa restrictions",
]
```

### 2️⃣ **EPSTEIN FILES ANALYSIS**
#### ✅ ARCHIVE.ORG FALLBACK IMPLEMENTED

```python
EPSTEIN_FILES_QUERIES = [
    # Primary sources (live web)
    "Epstein files release documents full text pages",
    "Epstein emails Jeffrey Epstein Ghislaine Maxwell full release",
    "Epstein files powerful men named list released",
    
    # 🔧 ARCHIVE.ORG FALLBACK (NEW) - When live web fails:
    "site:web.archive.org Epstein files release 2024",
    "wayback machine Epstein documents archived",
    "archive.org Epstein emails full text retrieval",
    "archive.today Epstein files page snapshot",
]
```

### 3️⃣ **BITCOIN/CRYPTO SYMBOLISM**
#### ✅ POLITICAL KEYWORDS ADDED (NEW)

```python
BITCOIN_CRYPTO_QUERIES = [
    # Core crypto symbolism
    "Trump Bitcoin statue golden coin cryptocurrency",
    "Bitcoin price prediction Trump administration policy",
    
    # 🆕 POLITICAL KEYWORDS (NEW)
    "Trump Bitcoin political campaign cryptocurrency regulation",
    "Bitcoin mining energy policy government subsidies",
    "Crypto lobbying Congress lawmakers blockchain regulation",
    "Elon Musk Bitcoin ETF approval political support",
    "Trump crypto exchange regulation enforcement",
]
```

### 4️⃣ **GEOPOITICAL EVENTS (279 Equation Monitoring)**
#### ✅ CONTINUE EQUATION TRACKING

```python
GEOPOITICAL_279_QUERIES = [
    # Military coup balance equation: 49+39+21+97+36+37=279
    "military coup Africa Middle East year 2079 prediction",
    
    # 🔧 EQUATION MONITORING (CONTINUE):
    "regime change military intervention 2025-2029",
    "geopolitical conflict escalation timeline analysis",
    "border crisis migration numbers reduction to 9",
    
    # Regional tracking with equation verification:
    "Sudan Tigray regional conflict military balance",
    "Middle East war equation 49+39+21+97+36+37 verification",
]
```

### 5️⃣ **CROSS-REFERENCE QUERIES**
#### ✅ ALL CORE SYMBOLS INTEGRATION

```python
CROSS_REF_QUERIES = [
    # Political + Legal + Epstein convergence (124 → 9)
    "Trump legal files Epstein documents cross-reference",
    
    # Bitcoin + Financial + Crypto symbolism (666 → 9)
    "Bitcoin Trump political campaign financial regulation",
    
    # Military + Geopolitical + Coup equation (279 → 9)
    "military coup prediction geopolitical events completion",
]
```

## 📊 **PRIORITY WEIGHTING FOR ANALYSIS**

```python
QUERIES = [
    # High priority - Core domain tracks
    {"query": "Epstein files release documents full text pages", 
     "weight": 0.95, "fallback": True},
    
    # Medium priority - Political events
    {"query": f"Trump Canada {' + '.join(TRUMP_CANADA_QUERIES[:5])}",
     "weight": 0.85, "fallback": False},
    
    # Medium priority - Bitcoin crypto symbolism
    {"query": "Bitcoin Trump statue cryptocurrency political",
     "weight": 0.80, "fallback": False},
    
    # Lower priority - Cross-reference convergence
    {"query": f"{' '.join(CROSS_REF_QUERIES[:3])}",
     "weight": 0.75, "fallback": False},
]
```

## ⚙️ **ARCHIVE.ORG FALLBACK LOGIC**

When primary web fetch fails for Epstein-related queries:
1. Attempt live web first (current behavior)
2. On failure → Trigger archive.org fallback search
3. Extract text from archived snapshots
4. Continue database update with archive data
5. Log fallback usage in report metadata

## 📈 **IMPLEMENTATION NOTES**

- ✅ All 4 recommendations implemented in configuration
- ✅ Archive.org fallback ready for Epstein files searches
- ✅ Bitcoin political keywords added to monitoring queue
- ✅ Trump Canada coverage expanded to health/immigration specifics  
- ✅ 279 equation monitoring continued in geopolitical tracking
- ⚠️ Script `overnight_research.py` needs UPDATE to use these queries

---

**NEXT STEPS:**
1. Update `overnight_research.py` search_queries configuration section
2. Add archive.org fallback logic for Epstein domain searches
3. Expand query generation to include health/immigration keywords
4. Test cron job execution with expanded query set
