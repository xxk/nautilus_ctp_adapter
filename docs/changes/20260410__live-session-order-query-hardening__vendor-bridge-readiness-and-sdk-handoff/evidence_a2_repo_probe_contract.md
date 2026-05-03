# Repo-Only Probe 证据 / Evidence A2

**更新日期**：2026-04-11
**状态**：已执行
**change-id**：20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff
**场景**：A2 Success 2 - repo-only probe 不再被误解为 live-ready

## 执行命令 / Command

```bash
python scripts/ctp_repo_debug_smoke.py
```

## 关键结果 / Key Results

```json
{
  "baseline": "repo-debug-smoke-v1",
  "success": true,
  "probe_scope": "repo_only_debug_bootstrap",
  "td_probe_mode": "public_pyo3_scaffold_before_c3",
  "formal_live_td_entrypoint": "python scripts/ctp_nautilus_live_smoke.py --config <path>",
  "formal_live_td_path": "execution_client.run_live_td_readiness_smoke -> native.td_ctypes -> ctp_native.dll",
  "scaffold_not_implemented": -9000,
  "invalid_handle": -9001,
  "td_init_code": -9000,
  "td_authenticate_code": -9000,
  "td_login_code": -9000
}
```

## 结论 / Verdict

1. repo-only probe 已明确把自己标记为 `repo_only_debug_bootstrap`，不再伪装成 live readiness。
2. 输出同时给出唯一 formal live entrypoint：`python scripts/ctp_nautilus_live_smoke.py --config <path>`。
3. `-9000` / `-9001` 继续被解释为 public scaffold contract，而不是私有 SDK/live DLL 已接好的信号。