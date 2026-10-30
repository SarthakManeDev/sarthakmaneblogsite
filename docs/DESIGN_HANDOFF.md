# From Figma to the site

A Figma file can't be "applied" to a codebase automatically. Someone translates it into HTML/CSS. This project is set up so that translation is small and safe:

- **All visual decisions live in `static/css/tokens.css`**: colours, fonts, sizes, spacing, radii. Nothing else hardcodes them.
- **Each page is one template** and each repeated element is one CSS block, so a Figma frame maps cleanly to a file.
- The Python/Django logic never needs to change for a visual redesign.

## What to ask your friend for

1. **Figma Variables** (or Styles) for colours, type scale, spacing and corner radii. Ideally named like the tokens in `tokens.css` (`color/bg`, `color/text-muted`, `space/4`, `radius/md` …).
2. **Frames for each page at desktop (1280 px) and mobile (390 px):**
   Home · Blogs list (with filters) · Blog post · Tea with AI list · Tea with AI answer · About. Studio screens are optional; they inherit the same tokens.
3. **Components** with their states (default/hover/focus): header & nav, footer, blog card, Tea with AI card (fixed height, text ending in “…”), book progress bar, headline row, gallery item, button, input/select, tag, pagination.
4. **Empty states**: what Home or Blogs looks like with no content yet.
5. **Assets**: logos, icons, abstract shapes exported as **SVG**; photos as WebP/JPG.
6. A **view link with Dev Mode** access to the file.

## How it gets into the code

| Figma | Code |
|---|---|
| Variables / Styles | `static/css/tokens.css` |
| Header, footer | `templates/base.html` + "Header / footer" section of `site.css` |
| Home frame | `templates/core/home.html` |
| Blogs list / post | `templates/blog/list.html`, `templates/blog/detail.html`, card: `templates/blog/_card.html` |
| Tea with AI | `templates/tea/list.html`, `detail.html`, card: `_card.html` |
| About | `templates/core/about.html` |
| SVG / images | `static/img/` |

Steps:
1. **Tokens first**: copy values into `tokens.css`. The site restyles immediately; check every page.
2. **Fonts**: swap the Google Fonts `<link>` in `templates/base.html` and the `--font-*` tokens.
3. **Layouts and components**: adjust templates and `site.css` page by page, comparing against the frames at both widths.
4. Open a pull request per page so changes are easy to review.

Fastest route: share the Figma link in a Claude Code session. With the Figma connector enabled, Claude can read the frames and variables directly and do steps 1–3. Plugins such as *Tokens Studio* or *Variables to CSS* can also export Variables straight to CSS custom properties.
