# sehi.li

Lyes Sehili’s personal website. Plain HTML, CSS, and a little vanilla JavaScript,
hosted on GitHub Pages. No packages, tracking, or external font requests.

## Preview and edit

Generated HTML is checked in alongside the sources, so GitHub Pages serves the repository as-is.
`.nojekyll` disables Jekyll. Keep `CNAME` containing `sehi.li`.

```sh
python3 -m http.server 8000
# Open http://localhost:8000
```

Edit content in `_pages/`, shared markup in `_templates/`, and styling in
`assets/css/style.css`. Fonts, colors, spacing, and reading widths are CSS
variables at the top of that file. For a sans-serif design, change
`--font-heading` to `var(--font-body)`.

After changing content, templates, or navigation, regenerate the HTML:

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 scripts/test_media.py
```

Python 3.9+ and its standard library are sufficient. The generator is a local
authoring tool, not a GitHub Pages build requirement. Commit source and generated
files together. It overwrites generated HTML; make prose edits in `_pages/`.
These commands never push or deploy. Publishing remains a separate manual step.

## Add a page or project

Copy a file in `_pages/`. Its small front matter block supplies `path`, `title`,
`description`, `section`, and optional `layout`. Use `layout: project` for the
shared article layout, with `category`, `status`, and `technologies` metadata.
A documented starter lives in `_templates/project-starter.html`.

Use directory URLs, e.g. `/projects/my-project/`. The generator writes
`projects/my-project/index.html`, metadata, and a sitemap entry. Link the new
project in `_pages/projects.html` and optionally the home or CV selection.
For new primary navigation, edit `NAV_PRIMARY` or `NAV_MORE` in `scripts/build.py`.
The header name links home. A custom `404.html` is included.

Project articles support headings, lists, `pre`/`code`, figures, tables,
references, and native MathML, without external libraries. Link only material
cleared for public release. The Apollo paper is related reading; the site does
not claim paper authorship.

## Add photographs

Put your own images in `assets/images/`. Replace the relevant placeholder:

```html
<figure>
  <img src="/assets/images/climb-960.webp"
       srcset="/assets/images/climb-480.webp 480w,
               /assets/images/climb-960.webp 960w"
       sizes="(max-width: 640px) calc(100vw - 40px), 760px"
       width="960" height="640" loading="lazy" decoding="async"
       alt="Describe what is actually visible in the photograph.">
  <figcaption>Your memory, location, and date, when known.</figcaption>
</figure>
```

Export appropriately sized WebP/JPEG files. Use meaningful alt text (empty for
decorative images), explicit dimensions, and lazy loading below the fold. For
the home portrait, use `class="portrait-image"`, a square crop, and omit lazy
loading. Existing placeholders use typography and CSS, not artificial photos.

## Add gaming clips

Add an object to `_data/clips.json` and run `python3 scripts/build.py`.
The gallery has no fixed limit and works without client-side data loading.
Empty entries render as placeholders. Fill in a real video ID or HTTPS URL:

```json
{
  "game": "Game name",
  "title": "Clip title",
  "youtube_id": "",
  "url": "",
  "thumbnail": "",
  "thumbnail_alt": "",
  "date": "",
  "caption": ""
}
```

Use `youtube_id` for the 11-character video ID; the generator creates the link.
For another host, leave the ID empty and supply `url`. Dates are optional, using
`YYYY-MM-DD`. Thumbnails are optional local paths under `/assets/images/`;
add descriptive `thumbnail_alt` text. Titles and captions are plain text.

YouTube players load only after a click, with a normal link as the no-JavaScript
fallback. Other hosts remain external links. No external thumbnails or players
load on a normal visit. Use only media you may publish.

## Add music

Append objects to `_data/music.json`, then regenerate:

```json
{"title": "Song or piece", "artist": "Artist / composer", "url": "", "note": ""}
```

Use a real HTTPS listening link for `url`; the artist and personal note are
optional. The current empty entry is a placeholder. No audio is embedded or
played automatically, and no copyrighted recordings are hosted.

## CV, SEO, and checks

When a real PDF is ready, add `assets/documents/lyes-sehili-cv.pdf` and replace
the marked PDF placeholder in `_pages/cv.html` with a download link. Until then,
the page offers browser printing / Save as PDF. The HTML CV deliberately keeps
the full education history and activities; the downloadable PDF will be the
separate, concise application CV.

Page descriptions live in each source file. Shared metadata, the domain, and
navigation live in `scripts/build.py` and `_templates/base.html`. The generator
updates `sitemap.xml`; `robots.txt` points to it. Favicons include SVG, ICO,
and an Apple touch PNG. `assets/images/social.png` is a typographic social
preview, not a personal photograph.

`scripts/check.py` checks generated output against source, local links,
fragments, images, metadata, headings, navigation, and the custom domain.
It does not fetch external links or private resources. Browser QA should include
mobile widths, the More menu with a keyboard, print preview, and (once a real
clip is supplied) click-to-play. CSS respects reduced motion and printing.

Unconfirmed content stays marked: dates, awards, technologies, exact
contributions, routes, music selections, and media need your real information.
