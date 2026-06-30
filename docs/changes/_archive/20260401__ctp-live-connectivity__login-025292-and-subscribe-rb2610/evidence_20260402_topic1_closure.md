# Topic 1 Closure Evidence

**日期**：2026-04-02  
**anchor change-id**：`20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610`

## 一、Topic 1 总结论

`ctp-live-connectivity` 已达到 topic 级出口条件：

1. 账号 `025292` 的 live config 路径已经收敛，敏感值留在 untracked local config。
2. 仓内维护的 `ctp_native` / 本地 `c wrapper` 边界已经冻结。
3. `rb2610` 行情已经通过 Python 主线与正式 Nautilus-facing smoke baseline 留证。
4. `TD` readiness 已通过本仓主线验证，历史 `ErrorID=63` 已被解释为错误的 `TdAuthenticate` 参数顺序。
5. 正式 smoke baseline 已冻结为 `python scripts\ctp_nautilus_live_smoke.py --config <path>`。

## 二、关联证据

1. `rb2610` 主线行情证据：
   `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__python-rust-md-login-path/evidence_20260402_python_md_subscribe_smoke.md`
2. `TD readiness` 证据：
   `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__td-auth-and-login-readiness/evidence_20260402_td_login_readiness.md`
3. `Nautilus live smoke baseline` 证据：
   `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__nautilus-live-smoke-baseline/evidence_20260402_nautilus_live_smoke_baseline.md`

## 三、对后续 Topic 的交接

1. Topic 2 可以直接在已冻结的 live/bootstrap 口径上推进 InstrumentProvider。
2. Topic 3 不需要重新定义 live smoke 入口。
3. Topic 4 不需要重新摸索 TD auth/login 输入顺序。
