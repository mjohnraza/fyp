---
name: obstacle-chain-extractor
description: Skill for extracting and sequencing retrieval-grounded buyer obstacle chains across chronological customer journey phases.
---

# Obstacle-Chain Extractor Skill

This skill guides the extraction of verified buyer friction to ensure opportunities are anchored in market reality rather than speculative hallucinations.

## Key Principles
- **Sequence First**: Unordered pain points conceal friction transitions. Always map obstacles into three sequential phases:
  1. `BEFORE_ATTEMPT`: Search cost, vendor lock-in anxiety, fear of compliance penalties, pricing unpredictability.
  2. `DURING_EXECUTION`: Silent webhook failures, OCR hallucinations, schema drift, rate limit errors, setup time.
  3. `AFTER_COMPLETION`: Maintenance debt, lack of continuous auditability, documentation rot, surprise LLM billing.
- **Triangulation Rule**: Every chain must reference snippets corroborated by at least two distinct source types:
  - `FORUM` (Reddit, Hacker News - raw emotion, uncensored complaints)
  - `REVIEW` (G2, Capterra - enterprise purchasing dilemmas)
  - `JOB_POSTING` (Upwork, Indeed - willingness to spend dollars)
  - `INDUSTRY_REPORT` (Gartner, McKinsey, PwC - macro organizational drag)
- **Obstacle Citation Coverage**: The ratio of obstacles with direct backing snippets must meet $\ge 65\%$ to avoid loop-back flags.
