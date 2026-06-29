# AI Constraints

1. Only modify `.gitignore`, this change bundle, and the git index state for `var/**` and `pytest_tmp/**`.
2. Use `git rm --cached -r -- var pytest_tmp` for retirement; do not delete working-tree files.
3. Verify `git ls-files 'var/**' 'pytest_tmp/**'` is zero before completion.
4. Stop if any required fixture or evidence artifact is discovered inside `var/**` or `pytest_tmp/**`.
