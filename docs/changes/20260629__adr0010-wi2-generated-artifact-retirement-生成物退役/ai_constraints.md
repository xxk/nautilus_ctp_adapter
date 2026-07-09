# AI Constraints

1. Only modify `.gitignore`, this change bundle, ADR-0010 guard tests, and the git index state for generated runtime outputs.
2. Use `git rm --cached` for retirement; do not delete working-tree files.
3. Verify `git ls-files 'output/debug/**' 'var/**' 'pytest_tmp/**'` is zero before completion.
4. Stop if any required fixture or evidence artifact is discovered inside generated runtime output roots.
