# Template — `rules/_meta/how-to-write-rules.md`

Produce EXACTLY this content. This file is self-referential and must comply
with the rules it defines.

```markdown
# Rules for Writing Rules

> Purpose: This file defines the standard every rules file in this project must meet. It is self-referential — it must itself comply with the rules it defines.
> Context: Read this file before creating or updating any rules in the `rules/` directory.
> Version: 1.0

## 1. Purpose

- Explain why this documentation system exists
- Describe what problem it solves
- Ensure consistency across all rules files
- Make onboarding for AI agents and developers deterministic

## 2. Mandatory structure of every rules file

Every .md file in rules/ must contain:

1. A `# Title` matching the file's subject
2. A `> Context:` blockquote explaining when an AI agent should read this file
3. Numbered sections with clear, imperative headings
4. At least one Correct and one Incorrect example per major rule
5. A `## Checklist` section at the end

## 3. Writing style rules

**Language:**
- Write all rules in English
- Write in short, imperative sentences: "Use X", "Never do Y", "Always Z"
- Avoid vague qualifiers: "try to", "consider", "might want to" — state rules definitively
- Use second person: "the agent must", "you must"

**Code example formatting:**

\`\`\`php
// Correct
public function findById(int $id): ?User
{
    return $this->users->find($id);
}

// Incorrect — missing return type, untyped parameter
public function findById($id)
{
    return $this->users->find($id);
}
\`\`\`

**Decomposition rules:**
- One rule per bullet point — never combine two rules in one sentence
- If a section grows beyond 10 bullets, split into subsections
- If a topic covers more than 3 distinct concerns, create a separate file

## 4. Versioning and changelog rules

\`\`\`markdown
// Correct
> Version: 1.1
## Changelog
- BR-005 updated to include edge case validation
\`\`\`

## 5. Forbidden content

- Opinions without justification — every rule must have a reason
- Duplicate rules that already exist in another file — link instead
- Broken or hypothetical code examples
- Vague rules that cannot be verified (e.g., "write clean code")
- Rules that contradict another file without explicitly noting the override

## Checklist

- [ ] Title matches the file subject
- [ ] `> Context:` blockquote included
- [ ] Numbered sections present
- [ ] At least one Correct and one Incorrect example per major rule
- [ ] Examples are syntactically correct and runnable
- [ ] Decomposition rules followed
- [ ] Version included and maintained
- [ ] Forbidden content avoided
```
