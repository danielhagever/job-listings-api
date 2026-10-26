# Job Listings API: search millions of open roles from company career sites, no company list

Search over 2.5 million open jobs from over 50,000 company job boards at once (Greenhouse,
Ashby, Workable, Workday, Oracle, ADP, iCIMS, Phenom, Jibe, Amazon and more) by title, place,
salary, seniority or remote, without knowing a single company name. Or rank companies by
how fast they are hiring, or list the roles that just closed. Rebuilt every night from the
employers' own career-site feeds; no login, no cookies, no LinkedIn or Indeed account.

This repo is the quick start for the hosted
[**Job Listings API**](https://apify.com/glitchbound/ats-jobs-search) on Apify: one HTTP
call from the shell, a standard-library Python script that writes a CSV, and the setup for
using it as a tool in Claude, ChatGPT or Cursor.

- [Quick start: one curl](#quick-start-one-curl)
- [Quick start: Python](#quick-start-python)
- [Use it from an AI agent (MCP)](#use-it-from-an-ai-agent-mcp)
- [Three modes](#three-modes) · [Filters](#filters)
- [A daily feed of new jobs](#a-daily-feed-of-new-jobs)
- [FAQ](#faq)

## Quick start: one curl

Get a free Apify API token at
[console.apify.com/settings/integrations](https://console.apify.com/settings/integrations),
then:

```bash
export APIFY_TOKEN=apify_api_...
curl -s -X POST \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"mode": "jobs", "title": ["data engineer"], "location": ["berlin"], "maxResults": 20}' \
  "https://api.apify.com/v2/acts/glitchbound~ats-jobs-search/run-sync-get-dataset-items"
```

The response is a JSON array, one object per job.

## Quick start: Python

[`example.py`](example.py) uses only the standard library and writes a CSV:

```bash
python3 example.py --title "data engineer" --location berlin --max 5
python3 example.py inputs/companies-surging.json --max 5
python3 example.py --title "product manager" --remote --new-within 24h
```

Real runs of the first two:

```
5 jobs rows written to jobs.csv
  GetYourGuide: Senior Data Engineer, Growth Data Engineering (Berlin)
  Nucs AI: Data Scientist / Data Engineer (Berlin, Berlin, Germany)
  Zeta Global: Data Engineer (Berlin, Germany)
  ANGEHEUERT GmbH: Senior Data Engineer (m/w/d) (Berlin, Berlin, Deutschland)
  Air Apps: Data Engineer (Berlin Metropolitain Area)

5 companies rows written to jobs.csv
  Walgreens: 22830 open, 3623 opened in 7 days
  CVS Health (cvshealth): 19560 open, 4074 opened in 7 days
  Lowe's (lowes): 12635 open, 1129 opened in 7 days
  Kotak Additional: 10832 open, 1239 opened in 7 days
  Marriott: 13325 open, 2788 opened in 7 days
```

## Use it from an AI agent (MCP)

Add this as a connector in Claude or ChatGPT:

```
https://mcp.apify.com?tools=glitchbound/ats-jobs-search
```

In Cursor or VS Code, the same address goes in `mcp.json`:

```json
{ "mcpServers": { "apify": { "url": "https://mcp.apify.com?tools=glitchbound/ats-jobs-search" } } }
```

The first call asks you to sign in to Apify or takes an API token. Then "remote senior
backend roles posted this week that publish a salary" is one tool call.

## Three modes

| `mode` | One row is | Use it for |
|---|---|---|
| `jobs` | one open role: title, company, location, country, city, work arrangement, seniority, posted date, first seen, link | job boards, alerts, research |
| `companies` | one company, ranked by roles opened recently: open roles, opened in 7, 30 and 90 days, closed in 30, net change | finding who is hiring hard right now, sales prospecting |
| `closed` | one role that disappeared: first seen, last seen, closed on, days open | time-to-fill, which roles were filled or pulled |

One real row of each is in [`sample-output.json`](sample-output.json) (the companies row
abridged: its location lists are cut). Staffing agencies are left out of `companies` by
default, because they post on behalf of others and would top every ranking.

## Filters

| Field | What it does |
|---|---|
| `title` | Words the title must contain; several lines are OR-ed, `*` matches a prefix |
| `location`, `countries` | A place in the location text, or a country resolved from it |
| `company`, `department`, `keywords` | Narrow by employer, team, or any field at once |
| `titleExclude`, `companyExclude`, `locationExclude` | Drop what you do not want; dropped rows are not charged |
| `workArrangements` | `remote`, `hybrid`, `onsite` |
| `seniority` | `intern`, `junior`, `senior`, `staff`, `principal`, `lead`, `director`, `executive` |
| `employmentTypes` | `full-time`, `part-time`, `contract`, `temporary`, `internship` |
| `withSalaryOnly`, `minAnnualSalary`, `maxAnnualSalary`, `salaryCurrency` | Roles whose employer published a pay band |
| `postedAfter`, `changedSince`, `newWithin` | Dates, or only what the index first saw in the last `24h`, `3d`, `7d` or `30d` |
| `platforms` | Limit to one career system |
| `includeDescription` | Adds the full posting text, read live from the employer's board |
| `maxResults` | A hard ceiling on rows returned and charged (default 1,000, up to 100,000) |

Ready-made inputs are in [`inputs/`](inputs).

## A daily feed of new jobs

Run it once a day with `"newWithin": "24h"` and your filters, and each run returns only the
roles that appeared since the last nightly rebuild, with `firstSeen` on every row. That is
a job feed without keeping state yourself.

## FAQ

**Do I need a list of companies?**
No. The index already holds every board this project reads; you ask a question. If you do
have a list, [Company Career Page Jobs Scraper](https://apify.com/glitchbound/ats-jobs-scraper)
reads each company's board live.

**Where does the data come from?**
Each employer's own careers feed, the one they publish so aggregators can list their jobs.
The endpoints themselves are documented in
[job-board-apis](https://github.com/danielhagever/job-board-apis).

**How fresh is it?**
Rebuilt every night. `firstSeen` is the date the index first saw a role; `closed` mode
reports the ones that disappeared since.

**What does it cost?**
It is paid per row returned; rows your filters drop are not charged. The current rate for
your plan is on the [Actor page](https://apify.com/glitchbound/ats-jobs-search).

## Related

- [Company Career Page Jobs Scraper](https://apify.com/glitchbound/ats-jobs-scraper): one company's jobs, live, by name or domain; quick start in [company-career-page-scraper](https://github.com/danielhagever/company-career-page-scraper).
- [Workday Jobs Scraper](https://apify.com/glitchbound/workday-jobs-scraper): any Workday careers site by company name; quick start in [workday-jobs-scraper](https://github.com/danielhagever/workday-jobs-scraper).
- [job-board-apis](https://github.com/danielhagever/job-board-apis): the public endpoint of each career system, with a tested `curl`.
- Live counts per system, rebuilt nightly: [glitchbound-jobs.pages.dev](https://glitchbound-jobs.pages.dev/).

Questions or a filter that does not do what it says? Open an issue here or on the Actor page.

## License

MIT
