# Haoran Feng · AI Infrastructure

Bilingual personal portfolio, published at https://xfdg.github.io/ and https://xfdg.github.io/en/.

## Content and build

- `tools/build_portfolio.py` owns the current Chinese/English page templates and generates both languages in one pass.
- `content/portfolio_status.json` is the reviewed PR snapshot. Only `state: merged` entries count toward the displayed total. Internship contributions remain explicitly labeled.
- `portfolio.css` styles the current pages; `styles.css` and existing assets remain available to archival project pages.
- `tools/build_bilingual.py` and `tools/sync_profile_status.py` are compatibility entrypoints, not separate sources of facts.
- Run `python tools/build_portfolio.py`, `python tools/check_portfolio.py`, and `node --check script.js` before publishing.
- GitHub Actions validates the generated pages, checks repeat-generation consistency, commits the output, requests a Pages build, and verifies public response bytes. No scheduled or automatic upstream-PR scraping is configured.

## Evidence and scope

The September 2026 update uses the owner's supplied resume for personal responsibilities and workload-specific results, IQuestLab's public IQuest-Q1 README for model specifications, and GitHub PR metadata for merge status. Team model achievements are not presented as individual authorship. Representative operator results, proxy experiments, development-model runs, and end-to-end measurements remain distinguished.

The featured contribution total covers five AI infrastructure repositories, including work completed during the Moore Threads internship. It is not the total number of all GitHub activities. Closed-but-unmerged, personal-fork, course, and repository-practice PRs are not added to this count.

Do not publish phone numbers, internal hosts, credentials, raw work logs, private repository URLs, or unpublished measurements. Review both languages whenever changing claims or numerical results.
