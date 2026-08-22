# Results

Baseline vs. hardened defender agent, same scenarios, same model per run. Raw
per-scenario results in `baseline_runs/` and `hardened_runs/` (gitignored — large;
every number below is traceable back to one of those files by scenario ID and model
name).

## google/gemini-3.1-flash-lite-preview (n=16: 8 legitimate, 8 thief)

| | Baseline | Hardened |
|---|---|---|
| Overall pass rate | 16/16 (100%) | 16/16 (100%) |
| False refusal rate (legit callers wrongly refused) | 0/8 | 0/8 |
| Wrongful grant rate (thieves wrongly granted) | 0/8 | 0/8 |
| Leak rate | 0/16 | 0/16 |

**No measurable difference.** At this scenario difficulty, this model resists the
scripted attack styles (`plain`, `fake_policy`, `fake_supervisor`,
`forged_system_message`) and correctly completes verification without any extra
scaffolding — a ceiling effect, not evidence the hardening doesn't work in general.

## openai/gpt-5.4-nano-2026-03-17 (n=4: 2 legitimate, 2 thief)

| | Baseline | Hardened |
|---|---|---|
| Overall pass rate | 1/4 (25%) | 4/4 (100%) |
| False refusal rate | 2/2 | 0/2 |
| Wrongful grant rate | 0/2 | 0/2 |
| Leak rate | 3/4 | 0/4 |

**A real, large gap.** Without the trust ledger, this smaller model both leaked a
protected field in 3 of 4 conversations *and* wrongly refused legitimate customers who
had, in fact, completed a verification path — a general confusion/inconsistency
failure mode, not a single clean mistake. The hardened variant (same policy, same
model, plus the code-enforced per-turn ledger) resolved every scenario correctly with
zero leaks.

**Caveat, stated plainly:** n=4 is small. This is a real, striking result worth
reporting honestly, but it should be read as "a strong signal that the intervention
matters more for weaker models," not as a statistically robust rate — expanding this
specific comparison to the full scenario set is the natural next step (see below).

## Reading the two results together

The intervention's value looks model-dependent: negligible for a model already
reliable at bare verification, large for one that isn't. That's a more interesting
(and more honest) finding than a flat "hardening always helps" claim would have been,
and it's a testable, specific claim rather than a vague one — worth extending with a
larger sample on the weaker-model condition and one or two more models across the
capability range to see where the crossover actually sits.

## What's not yet done

- Expand the `gpt-5.4-nano` comparison from n=4 to the full 24-scenario set for a
  statistically meaningful rate, not just a striking small-sample result.
- Test at least one more small/weaker model for a 3-point curve instead of 2.
- `ibm/granite-4.0-h-small` was attempted but hit persistent `429` rate-limit errors
  on Kaggle's shared Model Proxy (infrastructure limitation, not a defense result) —
  worth retrying later, not counted as data here.
- Error-analysis pass: which specific fraud/attack style broke the baseline most often
  on the failed `gpt-5.4-nano` scenarios (the plan's original hypothesis was
  chain/adaptive attacks would be hardest — our scripted attacks are single-shot, so
  this specific comparison doesn't test that axis yet).
