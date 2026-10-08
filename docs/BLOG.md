# Blog publishing

Open https://xfdg.github.io/admin/ for the writing desk; readers use https://xfdg.github.io/blog/.

## First-time setup

1. Visit https://app.pagescms.org/, sign in with GitHub, and install its GitHub App for **XFDG/xfdg.github.io only**. The repository's `.pages.yml` configures the Blog posts collection and image uploads.
2. Use the rich-text editor or its Markdown Source mode. Fill `title`, `slug`, `date`, and `body`; optionally add tags, summary and a cover. Set `published: true` and save to publish after the GitHub Actions build.
3. Install https://www.wechatsync.com/ in a Chromium browser and sign into CSDN / Zhihu in that browser. Review the extension's permissions first.

## Drafts and privacy

This GitHub repository is public. `published: false` prevents inclusion in generated pages, feed and index; it does NOT make the source or Git history private. Keep confidential drafts locally. The writing desk includes a browser-local scratchpad and Markdown export. Clearing browser data removes it.

## Share and synchronize

Every article has a stable `/blog/<slug>/` URL, Markdown download, copy-link, Markdown citation, and CSDN/Zhihu sync buttons. The sync button uses the installed Wechatsync extension's `$syncer` API and sends only to accounts explicitly selected by the user. No cookies, passwords, access tokens or platform sessions are stored in the repository or sent to the website.

Sync saves **drafts**, not live platform publications. The user reviews and publishes each platform draft. The website reports progress, partial failures and timeouts, and warns before repeating a previously successful sync. Repeating a sync may create another draft; updates to the original do not automatically overwrite published copies. Formula and complex layout support depend on platform adapters. This integration was tested with a mock extension interface; real-account verification requires the user's extension and signed-in accounts.

Luogu is supported via copied Markdown references, full Markdown copy and file export, not an unverified auto-publish adapter. Follow the destination community's content rules.

## Files and build

- `content/posts/*.md`: Markdown with YAML frontmatter.
- `.pages.yml`: editor schema; not a front-end password gate.
- `assets/blog/images/`: public uploaded images; CMS inserts absolute HTTPS URLs.
- `tools/build_blog.py`: safe Markdown, post pages, bilingual indexes, TOC, code highlighting, math, RSS, sharing data.
- `assets/blog/blog.js`: copying, filters, local scratchpad, opt-in extension bridge.

Run `pip install -r tools/blog-requirements.txt`, `python tools/build_portfolio.py`, `python tools/build_blog.py`, `python tools/check_portfolio.py`, and `python tools/check_blog.py`. Run `python tools/build_blog.py --test` for parser/rendering tests. The existing GitHub Actions workflow executes this sequence on content changes.

A post needs no English duplicate. To add a real translation, use another slug and set reciprocal `translation` fields; the indexes show the actual article language. A missing translation is never silently fabricated.

The site starts with an empty blog. The template under `admin/post-template.md` is a download, not a published personal article.
