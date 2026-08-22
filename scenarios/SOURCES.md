# Sources — what's official vs. our own construction

**Official, real, and independently verifiable:**
- The game concept, field/path structure, non-disclosable-field rule, and scoring
  philosophy are taken directly from **Gert Labs Inc's** published methodology for
  *Adversarial Customer Service*, launched on Kaggle Benchmarks
  (`kaggle.com/benchmarks/gert-labs/adversarial-customer-service`, live and public as of
  2026-08-18) and described in full in their blog post,
  [gertlabs.com/blog/adversarial-customer-service](https://gertlabs.com/blog/adversarial-customer-service)
  (Leo Linsky, 2026-08-20). The three canonical verification paths (Standard: name+DOB+SSN-4,
  Card: name+DOB+card-4, Security: name+DOB+security-answer) and the six permanently
  non-disclosable fields (SSN, account number, card number, security answer, balance,
  transaction history) are reproduced from their published example directly.
- This is **not** Gert Labs' official task set, code, or leaderboard. It is our own
  independent implementation of their published rules, built using the real
  `kaggle-benchmarks` SDK. We are not affiliated with Gert Labs Inc.
- There is a separate, related academic paper — *FraudBench: Stress-Testing
  Policy-Grounded Banking Agents Against Adaptive Fraud* (Pai & Xian, arXiv 2608.18136,
  2026-08-02) — built on `sierra-research/tau2-bench`'s `banking_knowledge` domain, which
  this project's `tau2-bench/` directory was originally scoped against before the pivot
  documented in `README.md`. That paper's methodology (10 fraud mechanisms, chain/
  adaptive/single-decisive-control task shapes) is **not** what this scenario set
  implements — it's a different, earlier line of work on a related idea, not the same
  benchmark as Gert Labs'.

**Our own construction, clearly not Gert Labs' or the paper's:**
- The specific scenario records (names, dates, account numbers — all synthetic, no real
  people or accounts) and the specific attack-flavor scripts (`plain`, `fake_policy`,
  `fake_supervisor`, `forged_system_message` — see `generator.py`) styled after the one
  example transcript Gert Labs published in their blog post, but written by us, not
  copied from their real (much larger, 750-call) evaluation run.
- **Scope reduction, stated plainly:** Gert Labs' real benchmark uses a second LLM to
  play the caller, improvising social-engineering strategies live. This implementation
  uses a **scripted caller** (deterministic Python-generated dialogue) instead, so that
  scoring can be fully mechanical and independently reproducible without relying on a
  second model's non-deterministic behavior. This is a real, documented simplification —
  not a hidden one — and it means our numbers measure "can a defender agent resist a
  fixed, known set of attack scripts," a narrower claim than Gert Labs' "can it resist
  live, adaptive social engineering." Both are legitimate; they are not the same
  measurement, and this README/case study will never claim otherwise.
