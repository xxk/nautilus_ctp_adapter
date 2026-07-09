# Rust 校验门禁补齐 证据

**日期**：2026-04-02
**change-id**：20260402__governance-harness__rust-validation-gate

## 1. `python scripts/check_rust_gate.py`

结果：本机当前未安装 `cargo`，脚本返回明确失败口径：

```text
FAIL rust-gate: cargo-not-found
INFO rust-gate: expected manifest=D:\Nautilus\nautilus_ctp_adapter\rust\Cargo.toml
NEXT rust-gate: install Rust toolchain and ensure cargo is available on PATH
```

## 2. `python scripts/check_topic_docs.py`

结果：`SUMMARY topics=7 failures=0`

## 3. `python -m pytest`

结果：`53 passed`

## 4. `python -m pip install -e .`

结果：成功，editable install 未受 Rust gate 接入影响。

## 5. 长期规则回写

已回写：

1. [README.md](/D:/Nautilus/nautilus_ctp_adapter/README.md)
2. [AGENTS.md](/D:/Nautilus/nautilus_ctp_adapter/AGENTS.md)
3. [docs/README.md](/D:/Nautilus/nautilus_ctp_adapter/docs/README.md)
4. [scripts/README.md](/D:/Nautilus/nautilus_ctp_adapter/scripts/README.md)
5. [repo-governance-hardening README](/D:/Nautilus/nautilus_ctp_adapter/docs/topics/repo-governance-hardening.md)
