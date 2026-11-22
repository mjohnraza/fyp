# Cold-Start Retrieval Corpus & Data Collection Audit
## Agentic Entrepreneur OS (FYP-I)

## 1. Corpus Overview
In accordance with Section 6.c of the FYP proposal, market-grounded opportunity discovery requires authentic buyer friction data rather than LLM hallucinations. The cold-start retrieval corpus contains curated, verified evidence across five high-leverage target outcome categories.

---

## 2. Target Outcome Categories
1. **WORKFLOW_AUTOMATION**: Fragile iPaaS connectors, webhook schema mutations, and multi-tenant observability debt.
2. **DATA_ETL_ANALYTICS**: Layout chaos in invoice/document parsing, unhandled rate limits, and legacy ERP reconciliation overhead.
3. **KNOWLEDGE_ONBOARDING**: Engineering onboarding latency, stale wikis, and mid-market price exclusions from enterprise AI search.
4. **COMPLIANCE_SECURITY**: Startup engineering paralysis during SOC2/ISO 27001 audits and continuous compliance drift.
5. **DEVELOPER_TOOLING**: Runaway LLM API bills, token quotas, and self-hosted proxy router complexity.

---

## 3. Multi-Source Triangulation Audit Matrix

To eliminate single-source bias, every target outcome category must be corroborated by at least two distinct source types:
- **FORUM (F):** Reddit (r/devops, r/automation, r/ExperiencedDevs), Hacker News.
- **REVIEW (R):** G2, Capterra, ProductHunt verified buyer reviews.
- **JOB_POSTING (J):** Upwork, Indeed commercial job listings demonstrating monetary willingness to pay.
- **INDUSTRY_REPORT (I):** Gartner, McKinsey, PwC benchmark and digital trust reports.

### Table: Triangulation Audit
| Category | Source Types Represented | Triangulation Passed? | Diversity Count | Sample Citation |
| :--- | :--- | :---: | :---: | :--- |
| **Workflow Automation** | `FORUM`, `REVIEW`, `JOB_POSTING` | **YES** | 3 / 4 | `SNIP-AUTO-01`, `SNIP-AUTO-02`, `SNIP-AUTO-03` |
| **Data ETL & Analytics** | `FORUM`, `INDUSTRY_REPORT`, `REVIEW` | **YES** | 3 / 4 | `SNIP-ETL-01`, `SNIP-ETL-02`, `SNIP-ETL-03` |
| **Knowledge Onboarding** | `FORUM`, `REVIEW`, `INDUSTRY_REPORT` | **YES** | 3 / 4 | `SNIP-KNOW-01`, `SNIP-KNOW-02`, `SNIP-KNOW-03` |
| **Compliance & Security** | `FORUM`, `JOB_POSTING`, `INDUSTRY_REPORT`| **YES** | 3 / 4 | `SNIP-SEC-01`, `SNIP-SEC-02`, `SNIP-SEC-03` |
| **Developer Tooling** | `FORUM`, `REVIEW` | **YES** | 2 / 4 | `SNIP-DEV-01`, `SNIP-DEV-02` |

---

## 4. Citation Coverage at Obstacle Level
Every extracted obstacle in the buyer obstacle chain must link directly to an existing snippet ID. In the current corpus implementation:
- **Total Obstacles:** 15
- **Obstacles with Verified Evidence Link:** 15
- **Obstacle Citation Coverage Ratio:** $100\%$ (Target threshold: $\ge 65\%$).
