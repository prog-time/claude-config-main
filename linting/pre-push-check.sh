#!/bin/bash

FAILED=0

echo "ShellCheck..."
bash linting/check_scripts/check_shellcheck_all.sh || FAILED=1
echo "----------"

echo "Markdown Code Style Checker..."
bash linting/check_scripts/check_markdownlint_all.sh || FAILED=1
echo "----------"

echo "YML/YAML Checker..."
bash linting/check_scripts/check_yamllint_all.sh || FAILED=1
echo "----------"

if [ "$FAILED" -ne 0 ]; then
    echo "pre-push-check: one or more checks failed — push blocked"
    exit 1
fi
