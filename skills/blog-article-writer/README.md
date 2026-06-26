# blog-article-writer

Writes technical blog articles from a senior-developer perspective:
tutorials, technology reviews, deep dives, and opinion pieces.
Triggered by natural-language requests ("напиши статью", "write a
tutorial", etc.) and produces a `.md` file as output.

## Triggers

- "write an article", "make a blog post", "write a tutorial"
- "write a review", "deep dive", "how-to", "prepare material"
- "напиши статью", "сделай пост", "напиши туториал",
  "обзор технологии", "разбор", "напиши how-to"

## Does not trigger for

- Internal project docs (README, CHANGELOG — use `docs-quality`)
- Generating `rules/` (use `rules-generator`)
- PR descriptions (use `git-pr`) or release notes (use `git-release`)
- Inline code comments

## Structure

- `SKILL.md` — workflow, tone, format rules
- `references/writing-principles.md` — core writing principles
  (leads, structure, what to avoid, edit ruthlessly) — loaded before
  every article

## Article formats supported

| Format | Structure |
|---|---|
| Tutorial | Problem → Prerequisites → Steps → Result → What's next |
| Technology review | What → Problems solved → How → Pros/Cons → When to use → Alternatives |
| Deep dive | Problem → Why it happens → Under the hood → Solutions → Trade-offs |
| Opinion piece | Thesis → Arguments → Counterarguments → Conclusion |

## Installation

Picked up automatically after `make install` at the repository root.
