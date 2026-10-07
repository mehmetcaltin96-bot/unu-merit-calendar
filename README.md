# UNU-MERIT Year 1 schedule 2026–27

Weekly schedule, reading lists, deadlines and exams for the full-time first year of the UNU-MERIT PhD programme.

- **Website:** `index.html`, published with GitHub Pages.
- **Calendar:** `calendar.ics`. In Google Calendar choose *Other calendars → From URL* and paste the address of `calendar.ics` on the website; later changes then appear in your calendar automatically. Apple Calendar and Outlook offer the same option as a subscription.

## Data

`program.json` is the single source of truth. It has four parts:

| Part | Content |
|---|---|
| `courses` | The four mandatory courses, lecturers and assessment |
| `sessions` | Every class: date, time, room, lecturer, readings, questions for the final essay, notes |
| `deadlines` | Assignments, presentations and exams |
| `events` | Programme events, public holidays, course registration deadlines |

Every item has a `confidence` field. `HIGH` means the source documents agree. `MEDIUM` and `LOW` items are shown as “not confirmed” on the website and explained under *Source notes*.

## Which source wins

When documents disagree, the most recent document in that course's folder prevails (judged by the file's own creation date, not the download date). A date stated for a specific session overrides a general rule such as “Thursdays 13:30–15:30”.

## When the schedule changes

1. Edit the item in `program.json` and update `meta.updated`.
2. Optionally rebuild the calendar locally: `python tools/make_ics.py`
3. Commit and push to `main`. GitHub Actions rebuilds `calendar.ics` and republishes the website.

Source: the cohort OneDrive folder “FT First-year ’26-27” (version of 7 October 2026). Zoom links and e-mail addresses are deliberately not published.
