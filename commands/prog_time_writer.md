---
description: Generate a prog-time blog article (essay, senior-dev voice) seeded from snipp.ru and publish it to WordPress as a draft via the prog-time-writer MCP
argument-hint: "[topic: PHP | Laravel | Docker | Python | JavaScript]"
contract: _contract.md
---

# /prog_time_writer

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Generates one original blog article for **prog-time** (a WordPress
site) and publishes it as a **draft**. Ideas are seeded from
**snipp.ru**; the article is an essay written in the voice of a
Senior developer; and every interaction with prog-time — listing
categories, listing posts, publishing — goes through the
`prog-time-writer` MCP server. No `gh`, no WP-CLI, no direct HTTP to
the WordPress REST API.

Mandatory article structure, in this order:

1. **Приветствие** — a short greeting that opens the essay.
2. **Короткое описание темы** — what the post is about, in 2–4 sentences.
3. **Основная часть с примерами** — the body, with working code examples.
4. **Итог** — the practical takeaway.

**Input:** `$ARGUMENTS` — an optional topic. When present it must be
one of `PHP`, `Laravel`, `Docker`, `Python`, `JavaScript`
(case-insensitive). When absent, the command auto-picks a topic from
that set, driven by the strongest non-duplicate idea found on
snipp.ru.

**Defaults (decided, not prompted):** articles are written in
**Russian**; posts are created with `status="draft"`; topic
selection and publishing run unattended in a single pass.

## Workflow

### Step 1 — Parse the topic argument

**Preconditions:** none — `$ARGUMENTS` may be empty.
**Action:** trim `$ARGUMENTS`. If empty → `topic_filter = "any"`.
Otherwise match it case-insensitively against the allowed set
{`PHP`, `Laravel`, `Docker`, `Python`, `JavaScript`}; on a match,
normalise to the canonical capitalisation.
**Capture:** `topic_filter` (one canonical topic, or `any`).

**Failure modes:**
- `$ARGUMENTS` is non-empty and matches none of the five → STOP with
  `error-templates.md#topic-not-allowed` (`topic=<raw argument>`,
  `allowed=PHP, Laravel, Docker, Python, JavaScript`).

**Invariants after:** `topic_filter` is set; nothing has been
written and no MCP call has been made.

### Step 2 — Resolve the prog-time site

**Preconditions:** Step 1 succeeded.
**Action:** call `mcp__prog-time-writer__list_sites`.

- Exactly one site → `site = sites[0]`.
- Multiple sites → ask the user which site name to target, offering
  the returned list; wait for the reply. Do not pick silently.

**Capture:** `site` (the WordPress site name passed to every later
MCP call).

**Failure modes:**
- The `prog-time-writer` MCP namespace is unavailable → STOP with
  `error-templates.md#prog-time-not-connected`
  (`command=prog_time_writer`).
- The call returns an `error` field → STOP with
  `error-templates.md#tool-call-failed`
  (`tool=mcp__prog-time-writer__list_sites`, `error=<verbatim>`).
- `sites` is empty → STOP with `error-templates.md#no-sites`.

**Invariants after:** `site` is a real site name returned by the
server.

### Step 3 — Load the live category map

**Preconditions:** Step 2 succeeded.
**Action:** call `mcp__prog-time-writer__list_categories`
(`site={site}`) and collect `categories[]` of `{id, name, slug}`.
The topic→slug map is fixed: `PHP`→`php`, `Laravel`→`laravel`,
`Docker`→`docker`, `Python`→`python`, `JavaScript`→`javascript`.
**Capture:** `categories[]`.

**Failure modes:**
- The call returns an `error` field → STOP with
  `error-templates.md#tool-call-failed`
  (`tool=mcp__prog-time-writer__list_categories`, `error=<verbatim>`).

**Invariants after:** the category map is available; the article's
category id is resolved later (Step 5), once the topic is fixed.

### Step 4 — Source candidate ideas from snipp.ru

**Preconditions:** Step 3 succeeded.
**Action:** browse **snipp.ru** (WebFetch / WebSearch scoped to
`snipp.ru`) for material in the relevant topic(s): all five when
`topic_filter = "any"`, otherwise just that one topic. Derive 3–5
candidate article angles. Each candidate is an *idea seed*, never
text to reproduce — record a working title, a one-line angle, the
matched topic, and the source URL.
**Capture:** `candidates[]` (each: `topic`, `working_title`,
`angle`, `source_url`), ordered best-first.

**Failure modes:**
- snipp.ru cannot be reached, or yields no usable idea in the
  allowed topic(s) → STOP with
  `error-templates.md#snipp-unreachable`
  (`error=<verbatim fetch error, or "no candidate ideas found">`).

**Invariants after:** at least one candidate idea exists; nothing
has been written or published.

### Step 5 — Pick a non-duplicate topic

**Preconditions:** Step 4 succeeded.
**Action:** walk `candidates[]` best-first. For each candidate,
check prog-time for near-duplicates by calling
`mcp__prog-time-writer__list_posts` with `site={site}`,
`search=<keywords from the working title>` — once with
`status="publish"` and once with `status="draft"`. A candidate is a
duplicate when an existing post's title or slug clearly covers the
same subject. Select the first candidate with no near-duplicate, then
resolve its category id from `categories[]` via the topic→slug map.
**Capture:** `chosen` (the selected candidate), `chosen_topic`,
`category_id`, `category_name`, `dup_compared` (count of existing
posts examined).

**Failure modes:**
- A `list_posts` call returns an `error` field → STOP with
  `error-templates.md#tool-call-failed`
  (`tool=mcp__prog-time-writer__list_posts`, `error=<verbatim>`).
- Every candidate has a near-duplicate → STOP with
  `error-templates.md#all-candidates-duplicate`
  (`collisions=<newline list of "- {candidate} → {existing title} ({url})">`).
- The chosen topic has no matching category on the site → STOP with
  `error-templates.md#category-not-found` (`topic={chosen_topic}`,
  `site={site}`).

**Invariants after:** `chosen` is an idea with no near-duplicate on
prog-time; `category_id` is a real category id on `{site}`.

### Step 6 — Write the article

**Preconditions:** Step 5 succeeded.
**Action:** invoke the `blog-article-writer` skill (via the Skill
tool) to write the article in **Russian**, as an essay in the voice
of a Senior developer, on `chosen`. Pass the mandatory prog-time
structure as a hard requirement: (1) Приветствие, (2) Короткое
описание темы, (3) Основная часть с примерами, (4) Итог — in that
order, with working code examples (a language tag on every fence) in
part 3. Honour the skill's quality rules (no `---` horizontal rules
in the body; every sentence earns its place). Save to
`drafts/{YYYYMMDD}-{english-slug}.md`, creating `drafts/` if absent.
The H1 line is the title. snipp.ru is inspiration only — the essay
must be original.
**Capture:** `article_path`, `article_title` (the H1 text, without
`#`), `article_excerpt` (a 1–2 sentence lead drawn from part 2),
`article_slug` (english kebab-case).

**Failure modes:**
- The skill does not produce a readable `.md` at `article_path` →
  STOP with `error-templates.md#article-generation-failed`
  (`error=<verbatim>`).

**Invariants after:** a Russian `.md` article with the four
mandatory sections exists on disk; nothing has been published.

### Step 7 — Render the body to WordPress HTML

**Preconditions:** Step 6 succeeded.
**Action:** transform the article body (the `article_path` content
minus the H1 title line) from Markdown into semantic HTML for the
WordPress `content` field — the MCP server passes `content` through
unchanged and WordPress renders HTML. Map `##`/`###` →
`<h2>`/`<h3>`; paragraphs → `<p>`; fenced code →
`<pre><code class="language-<lang>">…</code></pre>` with the body
HTML-escaped; inline code → `<code>`; lists → `<ul>`/`<ol>` + `<li>`;
tables → `<table>`. Emit no Markdown markers and no `<hr>`.
**Capture:** `content_html`.

**Failure modes:** none — this is a pure transform.

**Invariants after:** `content_html` is valid HTML carrying the four
sections, with no raw Markdown.

### Step 8 — Publish as a draft

**Preconditions:** Step 7 succeeded.
**Action:** call `mcp__prog-time-writer__publish_post` with
`site={site}`, `title={article_title}`, `content={content_html}`,
`status="draft"`, `categories=[{category_id}]`,
`excerpt={article_excerpt}`, `slug={article_slug}`. Pass
`status="draft"` explicitly — never `publish`.
**Capture:** `post_id`, `post_url`, `post_status`.

**Failure modes:**
- The call returns an `error` field → STOP with
  `error-templates.md#tool-call-failed`
  (`tool=mcp__prog-time-writer__publish_post`, `error=<verbatim>`).
- The returned `status` is not `draft` → STOP with
  `error-templates.md#unexpected-post-status` (`status={post_status}`).
  Do not edit, delete, or re-publish the post.

**Invariants after:** exactly one new draft post exists on
prog-time; no public post was created.

### Step 9 — Report

**Preconditions:** Steps 1–8 completed.
**Action:** emit the `prog_time_writer` template from
`_shared/report-templates.md`:

```
Topic:         {chosen_topic}
Source idea:   {chosen.source_url}
Article file:  {article_path}
Title:         {article_title}
Category:      {category_name} — #{category_id}
Dup check:     {dup_compared} compared — no near-match
Post:          {post_url} — [new]
Status:        draft
```

**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- Every prog-time interaction — `list_sites`, `list_categories`,
  `list_posts`, `publish_post` — goes through the `prog-time-writer`
  MCP. Never fall back to `gh`, WP-CLI, or direct WordPress REST
  HTTP.
- Posts are always created with `status="draft"`. This command never
  publishes publicly and never flips an existing post to `publish`.
- The duplicate check (Step 5) runs **before** any article is
  written. If every candidate collides, STOP — do not write or
  publish a near-duplicate.
- snipp.ru is an idea source only. Never reproduce its text, code, or
  structure verbatim; the published essay must be original.
- Topics are limited to PHP, Laravel, Docker, Python, JavaScript. A
  topic argument outside that set is a STOP, not a silent
  substitution.
- Articles are written in Russian, as an essay from a Senior
  developer, and must contain the four mandatory sections in order.
  An article missing a section is not publishable — fix generation,
  do not publish a partial.
- The MCP `content` field receives HTML (Step 7). Never send raw
  Markdown — WordPress would render the markers literally.
