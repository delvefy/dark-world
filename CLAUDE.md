# Atlas of the Silence

A growing wiki + hand-drawn map of a dark-fantasy world: early-modern European history, twisted with dark magic and nigh-immortal powers. It grew out of the novel *111* (`~/work/writing/111`: `Meta.MD`, `AuthorVoice.MD`, `Chapters/`). The novel is one story inside this world.

## Canon order

1. **`world.json` is the single source of truth.** Read it first, every session. Never contradict it.
2. **This wiki is the master canon.** Where the novel disagrees with the wiki, the wiki wins and the novel gets revised later. The novel is raw material, not a constraint: it will be rewritten to fit, so change its facts freely when the wiki needs it. When adding something the novel already covers, take the novel's facts (Meta.MD world-building section) as the starting point.
3. Real history is the hidden skeleton. **Never name real people, places or events on any page.** Twist them; don't cite them.

## Fixed decisions

- **Tone: grim.** Dark fantasy. Magic always costs something, usually someone else.
- **Voice: neutral reference.** Encyclopedia register, past tense for history, present for standing facts. No in-world narrator. Mark uncertainty plainly: *unconfirmed*, *disputed*, *unknown*.
- **Calendar:** years counted **AS — After the Silence** (year 0 = the kimberstone builders vanish). Write dates as `1487 AS`; `c. 1424 AS` when approximate. No named months yet. The novel's journal runs 1487–1488 AS.
- **Geography:** loosely inspired by the real map (relative layout only). Veleh in the middle; Bloria NW, Mechil NE, Ustrus SE across the Vorn Danu; the Eastern Sea on the east; Strova between the river's last bend and the sea.
- **The Thirteen:** thirteen nigh-immortals. Not all identified. They rule through empires and proxies and fight each other. In 1488 AS one stands behind each of **Ustrus, Bloria, Mechil**. Their origin and their link to the Silence are **unknown even in-world** — keep it that way; record theories, never settle it.
- **The Last Dawn:** the prophesied one who will return and destroy the Thirteen.
- **The Last Dawn returns c. 400 years after 1488 AS** (around 1900 AS). No 1487–88 figure is it. No page states the date; in-world nobody knows when.
- **The Grimoire** (of the Hundred-Eleven) is an **independent** relic with its own will. The Thirteen covet it. It was not made by them.
- Other darkness that exists: bound relics, revenants and bargains (witches who take payment in lives), things left from before the Silence, state mage corps.

## Structure

- `index.html` — the map. Terrain is hand-drawn SVG; markers, place labels and roads are **generated** between `BEGIN:`/`END:` comments. Don't hand-edit inside those blocks.
- `places/`, `people/`, `events/`, `lore/` — one page each. Path is `<folder>/<id>.html`.
- `world.json` — names, coordinates, years, links, roads.
- `style.css` — shared look.
- `build.py` — regenerates the map from `world.json` and validates every page.

## Rules for every session

1. Read `world.json` (and the pages you'll touch) before writing.
2. **Every new page links to at least 2 existing pages.** Add the reverse link on at least one of them.
3. Every page ends with **Loose threads** (2–4 bullets). The next session pulls one.
4. New place → coordinates in `world.json` (map is 1000×700; Veleh core sits roughly x 40–800, y 160–560). Keep it on land, off rivers, and clear of existing labels.
5. New event → `year` in AS. Pages may be `null` for minor events (they'll feed the timeline later).
6. Run `python3 build.py` at the end. It must pass with no errors.
7. Commit only when asked.

## Session menu

- Pick an empty spot on the map and invent what's there.
- Or open an existing page and add a character, a conflict, a rumour.
- Or pull a loose thread.
- Or `/expand N`: add N pages strictly one at a time, each fully built and linked before the next (`.claude/skills/expand/SKILL.md`).

## Later

Timeline page from `events`; random "travel" button; trade routes as dashed lines (`routes` in world.json); seasonal map tint by real-world month.

## Known novel inconsistencies (fix in the novel, not here)

- Day 430 says the breach was "three years ago"; journal time since Day 70 is about one year.
- Seasons drift: Day 291 has the harvest, Day 306 the first snow, yet the journal opens in spring.
- Day 238 puts the whole company on horseback (company is foot-only).
- Meta.MD says Andrej held the Rift with three times Mihail's men and implies a traitor (Olegzander). Wiki: Mihail had the larger army; Andrej's garrison was about three times the company's size; no traitor, the Hundred-Eleven opened the gate from inside.
