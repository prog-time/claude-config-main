#!/bin/bash

echo "ShellCheck..."
bash linting/check_scripts/check_shellcheck_all.sh
echo "----------"

echo "Markdown Code Style Checker..."
bash linting/check_scripts/check_markdownlint_all.sh
echo "----------"

echo "YML/YAML Checker..."
bash linting/check_scripts/check_yamllint_all.sh
echo "----------"
