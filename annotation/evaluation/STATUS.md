# Evaluation status

Requested first-stage models:

- **Qwen3.8-27B**: account catalog confirms `Qwen/Qwen3.8-27B`.
  Full run directory: `runs/qwen38-27b-4096/`.
- **Llama 3.3 70B**: unavailable in the authenticated catalog returned by
  `https://api.tokenfactory.nebius.com/v1/models` on October 28, 2026.
  No Llama model IDs were returned. No substitute model was run.

Gemma-3-27b-it was subsequently authorized and completed; GPT OSS remains deferred.

The initial five-document Qwen pilot in `runs/qwen38-27b/` used 512 output tokens;
reasoning exhausted that budget for two documents. It is a failed-budget pilot,
not the evaluation result. All five succeeded with the full run's 4,096-token
budget. The prompt and source remain unchanged. The full-run manifest records
this configuration and both file hashes. The saved model catalog is included in
the full run directory.

Full Qwen evaluation completed: **1,557/1,557** labeled, zero failures.
Two truncated records succeeded with a recorded 16,384-token retry budget.
One reason exceeds 100 words; its valid explicit label is retained and flagged.
See [RESULTS.md](RESULTS.md) for final metrics.

## Direct Llama inference check

On October 28, 2026, direct chat-completion requests confirmed:

- `meta-llama/Llama-3.3-70B-Instruct`: **HTTP 403**, account/key does not have access.
- `Llama-3.3-70B-Instruct`: **HTTP 404**, unqualified model ID does not exist.

See [saved API responses](llama_availability_probe.json). Llama evaluation requires
access to the qualified model ID or a Nebius endpoint/key that serves it.

## Gemma 3 evaluation completed

`google/gemma-3-27b-it` labeled **1,557/1,557** documents with the unchanged prompt.
One context-limit failure succeeded using a recorded 512-token response allowance
with the full original text. Both models are compared on the same 1,554 primary
documents in [comparison.md](comparison.md). No Gemma format violations remain.
