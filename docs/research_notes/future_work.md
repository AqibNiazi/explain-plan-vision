# Future Work & Phase 6 — LLM Grounding Layer

---

## What Phase 6 Is Not

Phase 6 is **not** adding more ML models, more endpoints, or more features. The system already has sufficient engineering depth. Adding complexity without research value would weaken the project, not strengthen it.

The specific anti-pattern to avoid:

```
Phase 6
→ Add ChatGPT
→ Add LangChain  
→ Add agents
→ "AI-powered"
```

This produces complexity without a research contribution.

---

## What Phase 6 Is

**Human-Aware Explainable AI Assistant** — a grounded LLM layer that translates verified symbolic reasoning traces into fluent, audience-specific natural language.

The constraint that makes this research-grade:

> **The LLM performs no reasoning. It only explains, teaches, reformulates, and summarises — based on facts already verified by the symbolic engine.**

This design prevents hallucination by construction.

---

## Architecture

```
Image
 ↓
EfficientNet-B0 (Vision)
 ↓
Grad-CAM++ (XAI)
 ↓
Symbolic Fact Extraction
 ↓
Knowledge Graph Inference
 ↓
Adaptive Planning
 ↓
Verified Reasoning Trace (JSON)
 ↓
LLM Layer (explanation only — no reasoning)
 ↓
Audience-Adaptive Natural Language Explanation
```

---

## Module 6.1 — Grounded LLM Explanation

**Input to LLM:**

```json
{
  "disease": "Tomato Late Blight",
  "confidence": 0.97,
  "severity": "high",
  "urgency_level": "critical",
  "treatment_class": "fungicide",
  "rules_fired": 14,
  "requires_isolation": true,
  "gradcam_findings": {
    "infection_spread": "widespread",
    "focus_score": 0.723
  },
  "top_actions": ["Isolate plant", "Apply fungicide", "Remove infected tissue"]
}
```

**System prompt (key excerpt):**

```
You are an agricultural AI assistant. You will be given a structured 
reasoning trace from a plant disease analysis system. Your task is to 
explain these findings in clear natural language.

RULES:
- Only use facts provided in the structured trace.
- Do not infer, assume, or add information not present in the trace.
- Do not make treatment recommendations beyond those in the trace.
- Cite the confidence value when discussing the diagnosis.
- If a fact has low confidence, explicitly flag uncertainty.
```

**Expected output:**

```
The leaf image shows symptoms strongly consistent with Tomato Late Blight 
(confidence: 97%). The disease severity is assessed as high, and the 
infection pattern covers a widespread area of the leaf surface.

The reasoning engine determined that immediate intervention is required 
(urgency: critical). This assessment is based on 14 inference rules 
firing simultaneously, including the widespread spread pattern and high 
severity level.

The recommended treatment class is fungicide. The primary actions are: 
(1) isolate the affected plant from neighbouring crops, (2) apply 
approved fungicide within 24 hours, and (3) remove and destroy infected 
leaf tissue.
```

---

## Module 6.2 — Multi-Persona Explanations (Extension of current system)

Current system produces template-based farmer/agronomist/researcher explanations. Phase 6 replaces templates with LLM-generated text grounded in the same structured trace:

| Persona | Language register | Focus |
|---|---|---|
| Farmer | Plain language, action-first | What to do today |
| Student | Educational, defines terms | What this disease is and why it matters |
| Agronomist | Technical, cites mechanisms | Treatment class rationale, resistance risk |
| Researcher | Full trace, cites rules | Rule IDs, confidence propagation, limitations |

---

## Module 6.3 — Interactive Why / Why Not

User can ask:

```
Why did you recommend fungicide?
Why not irrigation?
What would happen if I waited 3 days?
```

System constructs an answer grounded in the reasoning trace:

```python
def answer_why(question, reasoning_trace, plan):
    relevant_facts = extract_relevant_facts(question, reasoning_trace)
    relevant_rules = extract_triggered_rules(question, reasoning_trace)
    
    prompt = build_grounded_prompt(question, relevant_facts, relevant_rules)
    return llm.generate(prompt, max_tokens=200)
```

The key: `relevant_facts` and `relevant_rules` come from the symbolic engine, not from the LLM's training data. The LLM is used purely for natural language generation.

---

## Module 6.4 — Reasoning Alignment Evaluation (Paper Contribution)

**Hypothesis:** LLM-generated explanations grounded in symbolic facts are more factually accurate than LLM explanations generated without structured context.

**Evaluation design:**

1. Generate symbolic explanations from 100 test images
2. Generate LLM explanations with structured trace (grounded)
3. Generate LLM explanations without structured trace (ungrounded)
4. Human evaluation on three criteria:
   - Factual consistency (does the explanation match the trace?)
   - Hallucination rate (claims not supported by any trace element)
   - Completeness (fraction of key trace elements mentioned)

**Expected result:** Grounded explanations show 30–50% lower hallucination rate. This result, if confirmed, is publishable as a short paper or workshop contribution.

---

## Evaluation Metrics Proposed

| Metric | Measurement Method |
|---|---|
| Factual consistency | NLI entailment between explanation and trace |
| Hallucination rate | Human annotator flags unsupported claims |
| Completeness | Fraction of trace elements mentioned |
| Audience appropriateness | Flesch-Kincaid grade level per persona |

---

## Implementation Notes

- Use Anthropic Claude API (claude-sonnet-4-6) or OpenAI GPT-4o for quality; Mistral-7B for cost
- Structured trace injected as system context, not user message
- Temperature = 0.2 for explanation tasks (low creativity, high reliability)
- Max tokens = 300 per explanation to prevent rambling
- Cache explanations per request_id to avoid repeated LLM calls
- Frontend: add collapsible "AI Explanation" panel below each result card

---

## Timeline Estimate

| Task | Effort |
|---|---|
| LLM API integration + prompt engineering | 3–4 days |
| Multi-persona endpoint | 1–2 days |
| Interactive Q&A endpoint | 2–3 days |
| Evaluation dataset + annotation | 1 week |
| Evaluation analysis + writeup | 1 week |
| **Total** | **~3 weeks** |
