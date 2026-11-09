---
name: expand
description: Grow the Atlas of the Silence by N new wiki articles, written strictly one at a time, each a full write → link → build cycle before the next starts. Use when the user types /expand N (e.g. /expand 11).
argument-hint: "[N articles, default 1]"
---

# /expand N

Add **N** new pages to the atlas. `N` = `$ARGUMENTS` (default 1; if not a positive integer, ask).

## The one rule

**Serial, never batched.** Article *k+1* is not chosen, asked about, drafted or planned until article *k* is written, wired into `world.json`, reverse-linked, and `python3 build.py` passes. No drafting several pages at once, no parallel subagents, no planning the full list up front. Each article is chosen from the world *as it stands after the previous one*, so later articles can build on earlier ones.

## Before the loop (once)

1. Read `CLAUDE.md` and `world.json`.
2. Run `python3 build.py`. If it fails, fix that first (it is not one of the N).
3. Put N steps on the task list: `Article 1/N`, `Article 2/N`, … Mark one in progress at a time.

## Each iteration (k = 1 … N)

1. **Re-read `world.json`** fresh. Gather every *Loose threads* bullet across all pages.
2. **Choose one target**, in this order of preference:
   - a loose thread from an existing page (prefer threads on the oldest or most-linked pages, and threads two pages both point at);
   - an empty spot on the map (place);
   - a gap: someone or something already named on a page that has no page of its own.

   Keep the run balanced: across the N, mix places, people, events and lore; don't make three of the same kind in a row unless the threads demand it. Don't pull the same thread twice.
3. **Read the source pages** the new article will touch. If the topic is covered by the novel, read `~/work/writing/111/Meta.MD` for it (wiki wins on conflict).
4. **Ask the user before writing. Do this for every article, no exceptions.** Use AskUserQuestion with 2–4 questions that let them shape this article. Always include:
   - **Target:** your pick (Recommended) plus 1–2 alternative threads or spots.
   - **The core twist:** 2–3 distinct directions for the article's central secret, conflict or answer.

   Add 1–2 more where they matter: who it serves among the Thirteen or the empires, what it costs, how it ties to the Grimoire or the Last Dawn, tone or scale, what stays *unknown*. Each question stands on its own, and options are concrete and mutually exclusive. Build on the answers; if they pick "Other", follow their text. Never ask them to rule on the Thirteen's origin or their link to the Silence (fixed as unknown).
5. **Write the page** at `<folder>/<id>.html`, copying the structure of an existing page in the same folder (header, `kind` line, `facts` aside, `lede`, sections, `Loose threads` with 2–4 bullets in `ul.threads`, `see-also`). Follow every Fixed decision in `CLAUDE.md`: grim tone, encyclopedia voice, AS dates, no real names, Thirteen's origin stays unsettled.
6. **Register it in `world.json`**: id, name, page, summary, `links` (≥2 existing ids). Place → `type`, `realm`, `x`/`y` on land, off rivers, clear of labels. Event → integer `year` (`approx: true` if circa).
7. **Wire it in.**
   - Link from the new page to ≥2 existing pages.
   - Add a reverse link on ≥1 of them (inline in the text, or in `see-also`).
   - If a loose thread was pulled, edit that bullet on its source page so it links to the new page and reads as answered or narrowed (e.g. *"Answered in part: see [Olegzander]."*). Don't delete it outright.
8. **Build:** `python3 build.py`. Fix until it prints `ok`. Never move on with a failing build.
9. **Log one line** to the user and advance the task list:
   `k/N · <Name> (<kind>) · pulled from <source page / map spot>`

If the build can't be made green, or a choice would contradict canon, stop the run, report where it stopped (k of N), and ask.

## After the loop

- Final `python3 build.py`.
- Short summary: the N articles in order, each with its link, plus which loose threads are now open for the next run.
- **Then ask.** Every run ends with an AskUserQuestion round (up to 4 questions, more rounds if needed) covering:
  - anything you guessed or left vague while writing (names, dates, coordinates, who knew what);
  - tensions with canon or the novel you noticed;
  - bigger shape questions the new pages opened (where a power struggle is heading, which realm to grow next, whether a rumour is true).
  Record the answers in the relevant pages and `world.json`, then rebuild. If an answer is a standing rule, offer to add it to `CLAUDE.md`.
- **Do not commit** unless the user asks.
