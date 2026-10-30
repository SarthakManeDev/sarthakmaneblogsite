# sarthakmane.in

Personal site of Sarthak Mane: a minimal, white, abstract blog built with Django.

| Section | URL | What it shows |
|---|---|---|
| Home | `/` | One-line life headlines, books in progress (with progress bars), photos & videos, latest writing |
| Blogs | `/blogs/` | All posts, filterable by subject, language, length, plus search |
| Tea with AI | `/tea-with-ai/` | Questions asked to AI and the answers, as equal-size cards ending with “…” |
| About | `/about/` | Photos, a short bio, Instagram, email, phone |
| Studio (private) | `/<STUDIO_PATH>/` | Owner-only dashboard to publish everything above |

Also included: RSS feed (`/feed/`), `sitemap.xml`, `robots.txt`, health check (`/healthz`).

## Run it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo        # optional sample content
python manage.py runserver
```

Open http://localhost:8000 and the Studio at http://localhost:8000/studio/.

Run the tests with `python manage.py test tests`.

## Using the Studio

- **New blog**: write in Markdown. *Insert image* uploads a photo and puts it where your cursor is. Save as *Draft* to preview privately, or *Published* to go live. A future publish date schedules the post. Reading time and the short/medium/long length filter are calculated automatically.
- **Books**: add each book once with its page count. Then just type the page you're on and press *Update*. Reaching the last page marks it finished. Several books can be in progress at once.
- **Headlines**, **Photos & videos**, **Tea with AI**, **About**: each one is a simple form.

## Project layout

```
config/            settings, URLs, sitemaps
apps/core/         Home, About, headlines, media, site profile
apps/blog/         posts, subjects, filters, RSS
apps/tea/          Tea with AI
apps/reading/      books & progress
apps/studio/       private owner dashboard
templates/         HTML templates (one per page; partials start with _)
static/css/tokens.css   design tokens: colours, fonts, spacing (from Figma)
static/css/site.css     public site styles (uses tokens only)
static/css/studio.css   Studio styles
infra/provision.sh      creates the Azure resources
.github/workflows/      test + deploy on every push to main
```

## Docs

- [docs/AZURE.md](docs/AZURE.md): Azure resources, monthly cost, deployment
- [docs/DOMAIN.md](docs/DOMAIN.md): pointing the GoDaddy domain at Azure
- [docs/DESIGN_HANDOFF.md](docs/DESIGN_HANDOFF.md): bringing the Figma design into the code
