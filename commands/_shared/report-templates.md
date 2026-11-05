# Shared — Report Templates

Canonical layouts for each command's final report. Every command
ends with a Report step that emits exactly one of the templates
below. Field order is fixed; no reordering, no extra fields, no
omissions except where the template marks a field optional.

## Formatting rules (apply to all templates)

- **Labels are left-aligned and padded to 15 characters** followed
  by two spaces, matching the examples below. Do not change
  padding.
- **Tag order is `[new | existing]`**, never the reverse.
- **Em dash `—`** separates URL from tag: `Pull Request: <url> — [new]`.
- **`----` (four hyphens on their own line)** separates the
  compact header from any embedded sub-report (e.g. the team-lead
  skill's JSON result).
- **No trailing prose.** After the report, emit nothing.
- Missing-but-expected fields are rendered as `—` (em dash), not
  `N/A` or blank. Truly optional fields are omitted entirely.

## `task_create`

Fields (all required):

```
Task file:     tasks/TASK-YYYYMMDD-{slug}.md
GitHub Issue:  #{N} — {url}
Type:          {feature | bug | refactor | spike}
Estimate:      {S | M | L}
```

## `task_branch`

Fields (all required):

```
Task source:   {GitHub URL | local file path}
GitHub Issue:  #{N}
Branch:        issues-{N}   [new | existing]
Next:          /task_complete {same input}   (or /task_submit if no pipeline)
```

## `task_complete`

Header (always emitted):

```
Task source:   {GitHub URL | local file path}
GitHub Issue:  #{N}
Branch:        issues-{N}   [new | existing]
Pull Request:  {pr_url} — [new | existing]
----
<team-lead skill JSON result, verbatim>
```

**Blocked variant** (team-lead outcome `blocked` / `partial`, delivery
skipped):

```
Task source:   {GitHub URL | local file path}
GitHub Issue:  #{N}
Branch:        issues-{N}   [new | existing]
Delivery:      skipped — team-lead outcome `{outcome}`
----
<team-lead skill JSON result, verbatim>
```

## `task_submit`

Fields:

```
Branch:        issues-{N}
GitHub Issue:  #{N}
Commits:       {count} pushed
Pull Request:  {pr_url} — [new | existing]
```

When invoked by `/task_complete`, `/task_submit` still emits this
same report shape; the caller re-wraps it into the `task_complete`
template.

## `task_abort`

Fields:

```
Branch:        issues-{N} — deleted
GitHub Issue:  #{N} — commented
Reason:        {one-line reason supplied by the user}
JSON record:   {updated | absent}
```

## `task_example`

Fields (all required):

```
Input:         {validated_input}
Status:        ok
```

Replace `Input` / `Status` with the fields that make sense for
your derived command. Keep labels left-aligned and padded to
15 characters.

## `prog_time_writer`

Fields (all required):

```
Topic:         {chosen_topic}
Source idea:   {snipp_source_url}
Article file:  {article_path}
Title:         {article_title}
Category:      {category_name} — #{category_id}
Dup check:     {count} compared — no near-match
Post:          {post_url} — [new]
Status:        draft
```

`Post` always carries the `[new]` tag — the command only ever
creates a fresh draft, never reuses one. `Status` is always `draft`;
this command never publishes publicly. `Source idea` is the snipp.ru
URL that seeded the article.

## `task_sync`

Multi-section report (the only free-form template). The sections
below are all required; their bullet sub-lists are omitted when
empty:

```
/task_sync — done

Project: {owner/repo}

From GitHub: {count} open issues fetched
Added to github-tasks.json: {count}

Comments posted: {count}
Comments skipped: {count}
  #{N} — no local file
  #{N} — local file missing
  #{N} — already commented (close: true)

Local files created: {count}
Local files already present: {count}
Local paths updated in JSON: {count}

Notes:
  - Size: M hardcoded on files materialised from GitHub (the Issue
    carries no size metadata).

Errors:
  #{N} — {gh or filesystem error}
```
