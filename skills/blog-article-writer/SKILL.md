---
name: blog-article-writer
description: |
  Writes blog articles, posts, tutorials, guides, technology reviews, and
  deep dives on any IT topic (programming, frameworks, languages, DevOps,
  architecture, databases) from a senior-developer perspective. Output is
  always a `.md` file. Use ALWAYS when the user says "write an article",
  "write a post", "make a blog post", "write a tutorial", "write a
  guide", "write a review", "deep dive", "how-to", "prepare material",
  "напиши статью", "сделай пост", "напиши туториал", "обзор технологии",
  "разбор", "напиши how-to", or describes a technical topic they want
  turned into a readable article. Walks through task clarification,
  outline, drafting, editing, and saving to `.md`. Do NOT use for:
  internal project docs (README, CHANGELOG — use `docs-quality`),
  generating `rules/` (use `rules-generator`), PR descriptions or
  release notes (use `git-agent`), or inline code comments.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# blog-article-writer

Produce useful, honest, well-structured articles that help other
developers solve real problems. Write as a peer — calm, concrete,
respecting the reader's time.

## Workflow

### Step 1 — Clarify the task before writing

Answer four questions before you start. If anything is unclear, ask
the user.

1. **Topic** — what specific problem or technology?
2. **Audience** — junior, middle, senior, manager?
3. **Format** — tutorial, technology review, deep dive, opinion piece?
4. **Length** — if unspecified, aim for 1500–3000 words.

### Step 2 — Load writing principles (mandatory)

Read `references/writing-principles.md` before writing a single
line. It defines the core writing standards — leads, structure, tone,
what to avoid. Apply these principles to every subsequent step. If the
file is missing, stop and report it.

### Step 3 — Build the outline

Pick 3–5 key ideas. Each idea becomes a self-contained module — a
reader should understand it even if they skipped the previous section.

### Step 4 — Write the draft

- One paragraph = one idea
- One sentence = one thought
- Facts over judgments: not "high performance" but "2 ms latency at
  10k RPS"
- Verbs over nominalizations: not "performs optimization" but "speeds
  up"
- Code examples: working, minimal, with a language tag on the fence

Before every code block, explain what it does. After it, unpack the
key points. Use inline comments only for non-obvious details.

### Step 5 — Edit ruthlessly

- Strip filler words and clichés (see principles reference)
- Replace abstractions with concrete facts
- Test every sentence: can it be deleted without loss of meaning? If
  yes, delete it.
- End every section with a takeaway or practical advice

### Step 6 — Save the output

Write the article to a `.md` file. Use a short English slug for the
filename (e.g., `usememo-vs-usecallback.md`). Never print the full
article into chat instead of saving — the artifact is the file.

## Article Structure

### Lead (intro)

The first 2–3 sentences must hook the reader. No clichés like "In
today's fast-paced IT world…".

**Bad:** "Software development is one of the most dynamically evolving
industries…"

**Good:** "Your React component renders in 400 ms instead of 16? The
problem is probably not React — it's how you manage state. Let's look
at three patterns that fix 90% of these cases."

### Context (optional)

If the topic needs prior knowledge, cover it briefly. Don't rehash the
docs — link to them.

### Main sections

Module structure: What → Why → How → Pitfalls.

### Code examples

Always specify the language in the fence.

````
```typescript
const sortedItems = useMemo(() => {
  return items.sort((a, b) => a.price - b.price);
}, [items]);
```
````

### Comparisons

Use a table instead of bullet lists of pros and cons:

| Approach | Good for | Not good for |
|----------|----------|--------------|
| Redux | Complex shared state | Simple local state |
| Context API | Rarely-changing data | Frequently-updated data |

### Conclusion

A practical takeaway. Answer: "What should the reader do after reading
this?"

**Bad:** "In this article, we have reviewed the main aspects of
working with Docker…"

**Good:** "Start simple: take one of your projects and write a
Dockerfile for it. Don't jump straight to multi-stage builds — just
get the app running in a container first."

## Article Formats

### Tutorial (how-to)

Problem → Prerequisites → Step-by-step solution → Result → What's
next.

### Technology review

What it is → Problems it solves → How it works → Pros and cons →
When to use, when not to → Alternatives.

### Deep dive

Problem → Why it happens → How it works under the hood → Solutions →
Trade-offs.

### Opinion piece

Thesis → Arguments with examples → Counterarguments → Conclusion.

## Tone and Style

- Address the reader as "you" or use impersonal constructions
- Humor: fine if natural, not forced
- Jargon: moderate technical slang (deploy, merge, refactor) is fine
- Loanwords: established ones (backend, framework, API) are fine
- Sentence length: alternate short and medium sentences
- Paragraphs: 2–5 sentences
- Don't hesitate to say "this approach has downsides" or "I don't
  know" — honesty builds trust

## Rules (non-negotiable)

- **Read `references/writing-principles.md` before writing.**
  Without it, the article will not meet quality standards.
- **Do NOT use `---` horizontal rule separators** in the article body.
  Use Markdown headings (`##`, `###`) to structure sections. A heading
  already signals a new section; a rule on top is visual noise. This
  applies to article output only, not to SKILL.md.
- **Never restate the same idea with different words** across
  paragraphs.
- **Every sentence must add new information.** Test: delete the
  sentence — does meaning change? If no, cut it.
- **Always specify a language tag** on every code fence.
- **Save to a `.md` file** — the article is the artifact, not the
  chat response.
- **If the user's request is vague**, ask for topic, audience, format,
  and length before writing.

## Examples

### Example 1 — Deep dive request

**User:** напиши статью про useMemo и useCallback — когда они реально
помогают, а когда вредят

**Assistant:** *(confirms audience = React developers, format = deep
dive, length ~2000 words; reads
`references/writing-principles.md`; outlines problem → why →
how → pitfalls; writes article; saves to
`usememo-vs-usecallback.md`)*

### Example 2 — Tutorial request

**User:** write a tutorial on setting up CI/CD with GitHub Actions for
a Node.js project

**Assistant:** *(how-to format: Problem → Prerequisites → Step-by-step
solution → Result → What's next; working YAML examples; saves to
`github-actions-nodejs-tutorial.md`)*

### Example 3 — Vague request

**User:** напиши что-нибудь про Docker

**Assistant:** "To write something useful I need a bit more context:
(1) what specific Docker topic — multi-stage builds, compose,
security, something else? (2) audience — devs new to Docker or people
already using it? (3) format — tutorial, review, or deep dive?"

## Edge Cases

- **User only knows the topic superficially** — flag the limits of
  your knowledge in the article itself; don't fake expertise.
- **No target length specified** — default to 1500–3000 words;
  confirm if much longer or shorter seems appropriate.
- **Principles file missing** — stop and report; do not proceed with
  reduced quality.
- **User wants the output in chat, not a file** — still save the file,
  and include the filename in the reply; the file is the canonical
  output.
- **User wants multiple articles in one request** — write one well
  first; ask before starting the next.
