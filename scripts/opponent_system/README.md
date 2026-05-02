# Self-Sustaining Opponent System
## Adversarial Research Architecture for Steve's Gematria

This implements a robust, adversarial research system that automatically tests hypotheses against counter-evidence, avoids confirmation bias, and maintains scientific integrity through enforced Domain Law axioms.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 2 (Domain)                          │
│   Specific Symbol/Hypothesis Claims                          │
│   ┌──────────────────┬──────────────────┬──────────────────┐ │
│   │   Advocate      │   Advocate       │    Advocate      │ │
│   │   (124)         │   (666)          │    (963)         │ │
│   └──────────────────┴──────────────────┴──────────────────┘ │
│                                                                │
└─────────────────────────────────────────────────────────────┘
                           ⬇ DEBATE
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 3 (Meta)                            │
│   Opponent Tests Framework Integrity                          │
│   ┌──────────────────────────────────────────────────────┐  │
│   │   Falsification Engine                              │  │
│   │   - Tests hypotheses against Domain Law axioms       │  │
│   │   - Generates counter-evidence and challenges        │  │
│   │   - Never attacks specific claims directly (meta)    │  │
│   └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ⬇ ARBITRATION
┌─────────────────────────────────────────────────────────────┐
│                  LAYER 4 (Arbitration)                       │
│      Judge Evaluates & Updates Hypothesis Strength           │
│   ┌──────────────────────────────────────────────────────┐  │
│   │   Arbitrator / Judge                                 │  │
│   │   - Receives arguments from advocates                │  │
│   │   - Receives challenges from opponent                │  │
│   │   - Applies Domain Law axioms as constraints         │  │
│   │   - Makes Bayesian-updated judgments                  │  │
│   └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ⬇ DEBATE LOOP
┌─────────────────────────────────────────────────────────────┐
│              Orchestrator (opponent_system.py)               │
│   - Coordinates all layers in automated debate loop          │
│   - Runs continuously until interrupted                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📜 Domain Law Axioms

These formal axioms govern all arbitration decisions:

### 1. Conservation Hypothesis
> *"Every claim about a symbol/value must have an explainable origin and transformation rules."*

**Transformation Rules:**
- No creation from nothing or disappearance into void
- Value chains must be reversible where natural
- Every manifestation connects to causal context
- Reduction/construction operations follow defined patterns

### 2. Simplicity Hypothesis (Occam's Razor)
> *"Prefer explanations with fewer assumptions and simpler operations."*

**Preference Principles:**
- Each domain should resolve to core primitives when decomposed
- Avoid unnecessary complexity in transformation rules
- Multi-step explanations require multiple pieces of evidence
- Special cases must be clearly marked as exceptions

### 3. Consistency Hypothesis
> *"The same symbols must behave consistently across contexts."*

**Consistency Requirements:**
- Identical symbols should produce predictable results
- Domain-specific exceptions must be clearly marked and bounded
- No contradictory claims within the same scope or level
- Boundary conditions explicitly stated when rules change

---

## 📁 File Structure

```
/scripts/
├── opponent_system.py          # Main orchestrator (entry point)
├── opponents/
│   └── falsification_engine.py # Layer 3: Meta-level adversary
├── advocates/
│   ├── symbol_124.py           # Universal Threshold / Bridge
│   ├── symbol_666.py           # Completion / Wholeness
│   ├── symbol_963.py           # Cycle Turning Variants (Harmony)
│   ├── symbol_55.py            # Vessel / Holds The Fire
│   ├── symbol_17.py            # Harmony Integration
│   └── symbol_279.py           # Cycle Turning Variants (Resolution)
└── arbitrator/
    └── judge.py                 # Layer 4: Decision arbiter

# Runtime state
/scripts/state.json             # Saved hypothesis states and results
```

---

## 🚀 Quick Start

### Interactive Mode (Development & Exploration)

```bash
cd /home/avalonas/.hermes/gematria/scripts
python3 opponent_system.py
# Select "1" for interactive mode
```

### Continuous Loop (Overnight Research)

```bash
cd /home/avalonas/.hermes/gematria/scripts  
python3 opponent_system.py
# Select "2" for continuous automatic loop
```

---

## 🔧 Usage Examples

### Single Component Testing

```bash
# Test falsification engine directly
python3 opponents/falsification_engine.py --self-test

# Test a specific advocate
python3 advocates/symbol_124.py
```

### Programmatic Access

```python
from opponent_system import DebateLoopOrchestrator

orchestrator = DebateLoopOrchestrator(state_file="state.json")
await orchestrator.initialize_advocates()
await orchestrator.run_all_hypotheses()
```

---

## 📊 Heat Scale Visualization

The system uses ASCII heat scale encoding for status:

| Symbol | Visual    | Status              | Net Strength   |
|--------|-----------|---------------------|----------------|
| ██     | ████████  | Strong Support      | > +70%         |
| ▓█     | ████░░░░  | Partially Supported | +40 to +70%    |
| ░▓     | ██░░░░░░  | Neutral-Biased      | +20 to +40%    |
| ░░     | ░░░░░░░░  | Indeterminate       | -30 to +20%    |
| .O     | ░░░░░░░░  | Suspicious          | < -30%         |

---

## 🔬 Scientific Rigor Features

### 1. No Absolute Certainty
- All confidence estimates are probabilistic (never 100%)
- Confidence expressed as probability, not certainty
- Bayesian-style updating of hypothesis strength

### 2. Meta-Level Separation
- Opponent operates at Layer 3 (meta/framework level)
- Specific claims live at Layer 2 (domain/hypothesis level)
- Avoids self-reference paradoxes through hierarchical separation

### 3. Domain Law Enforcement
- All hypotheses must respect Conservation, Simplicity, Consistency axioms
- Violations tracked and reported with heat scales
- Systematically flags patterns of suspicious behavior

### 4. Cumulative Evidence Tracking
- Never accepts/rejects based on single instance
- Tracks evidence strength across multiple observations
- Reports "support ratio" as proxy for likelihood ratios

---

## 🔄 Debate Loop Mechanics

Each round proceeds through 3 phases:

### Phase 1: Advocate Argument
- Presents hypothesis with key supporting points
- Estimates current evidence confidence
- Demonstrates domain law compliance
- Identifies known vulnerabilities

### Phase 2: Opponent Challenge  
- Tests against Domain Law axioms
- Generates counter-hypotheses where applicable
- Reports violations with confidence estimates
- Suggests alternative frameworks

### Phase 3: Arbitration Decision
- Computes advocacy vs opposition scores
- Checks domain law compliance status
- Calculates evidence quality rating
- Makes Bayesian-updated judgment
- Outputs recommendation (accept/tentatively_accept/reject/needs_more_evidence)

---

## ⚙️ Configuration Options

### State Persistence
```python
state_file = "/home/avalonas/.hermes/gematria/scripts/state.json"
```

### Custom Domain Laws
Edit `opponents/falsification_engine.py` to add/remove laws or modify transformation rules.

### Heat Scale Thresholds
Edit `arbitrator/judge.py` `_get_status_class()` method to adjust visualization thresholds.

---

## 📈 Output Format

Example arbitration result:

```json
{
  "hypothesis_name": "Universal Threshold",
  "advocacy_score": 0.81,
  "opposition_score": 0.65,
  "net_strength": 0.24,
  "domain_law_status": "full_compliance",
  "evidence_quality": "well_tested",
  "confidence_estimate": 0.85,
  "recommendation": "tentatively_accept"
}
```

---

## 🧪 Testing

### Run Self-Test
```bash
python3 opponents/falsification_engine.py --self-test
```

### View Current Status
```bash
python3 opponent_system.py  # Select option "2" to view status
```

---

## ⚠️ Important Notes

1. **Confidence ≠ Certainty**: All confidence values are probabilistic estimates, never absolute truths.

2. **Domain Laws Are Immutable**: The three axioms (Conservation, Simplicity, Consistency) cannot be disabled - they're foundational to scientific integrity.

3. **Opponent Meta-Level**: The falsification engine operates at meta-level, testing framework integrity, not making specific claims about the symbols themselves.

4. **Self-Reference Avoidance**: By separating Layer 2 (hypothesis claims) from Layer 3 (framework testing), the system avoids self-reference paradoxes.

---

## 🔮 Future Enhancements

- Integration with Firecrawl for automated evidence gathering
- Database-backed state persistence  
- Web dashboard visualization
- Export to Obsidian wikilink format
- Multi-region observer synchronization

---

## 📞 For Questions

See individual component documentation:
- `opponents/falsification_engine.py` - Opponent module
- `advocates/symbol_*.py` - Individual advocate docs  
- `arbitrator/judge.py` - Arbitration logic

---

*System ready for overnight adversarial research deployment.* 🚀
