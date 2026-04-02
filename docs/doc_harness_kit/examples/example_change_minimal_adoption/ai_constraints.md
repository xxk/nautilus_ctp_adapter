# 最小接入 5 步 AI 执行约束 / Minimal 5-Step Adoption AI Constraints

**change-id**：20260327__harness-adoption__minimal-5step-adoption
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

> 这是跨项目示例文件。复制到目标项目后，必须替换真实路径、正式入口和验证命令。

## 启动顺序

1. 先读 `acceptance.md`，确认 5 步完成的判定标准。
2. 再读 `plan.md`，确认这 5 步应如何拆分执行。
3. 再开始动手；若正式入口或验证入口不明确，先补文档，不要跳过。

## 执行规则

1. 一次只解决一个最小缺口。
2. 不允许把“目录已复制”直接当作接入完成。
3. 不允许保留示例仓验证命令占位而宣告通过。
4. 必须把当前 change 自身当作第一个真实试点 change 留证。

## 状态回填

1. `AI-STATUS` YAML 是唯一 AI 执行状态源。
2. 只有 A1-A5 全满足，才允许把 `allow_declare_pass` 改成 `true`。
3. 只有真实执行与真实证据满足出口条件时，AI 才能把最终结论改为已验收。

## 收尾动作

1. 确认入口地图已可发现。
2. 确认 change 模板落点已存在。
3. 确认目标项目验证命令已替换为真实口径。
4. 确认当前 change 的证据已完整记录。
