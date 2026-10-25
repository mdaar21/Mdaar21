# Working on Mdaar21

## Start here

Read [MDAAR_HUB.md](MDAAR_HUB.md) before locating or editing any part of Mdaar. It is the shared project map and the reference for current links, source locations and current deliverables. Keep it current when a URL, artifact or source location changes.

Use these names consistently with the owner:

- **المتجر**: the Zid storefront.
- **الواجهة / الموقع التعريفي**: the promotional site under `public/discover/`.
- **التطبيق**: the nutrition and training application under `public/`.
- **صفحة المنتج**: the Zid listing for بروتوكول التحول.
- **الكتاب / ملف المنتج**: the editable book and current PDF.

Resolve “الموقع” from the immediate context. If the target remains ambiguous between the storefront, promotional site and app, clarify the target before changing the wrong surface.

## Current sources

The canonical repository is `https://github.com/mdaar21/Mdaar21.git`: `main` holds sources and `gh-pages` holds the published Pages tree. Use this repository rather than the old account checkouts or temporary video folders outside it.

- App: `public/index.html`, `public/assets/`, `public/data/`.
- Promotional site: `public/discover/`.
- Book: edit `scripts/build-book.py` and `docs/book/book.css`; preserve original vector covers in `docs/book/identity/`. `docs/book/index.html` and the PDF are generated. Current PDF is listed in MDAAR_HUB.md.
- Connected assistant: `cloudflare/worker.mjs`, `public/assets/assistant.mjs`, `public/assets/remote-service.mjs`. The configured service origin is in `config/github-pages.json`; deployment instructions are in `docs/github-ai.md`.
- Zid storefront and product settings live in Zid, not this checkout. A Git commit does not update Zid pricing, product files, checkout or automatic delivery. Verify available authenticated access when actual Zid edits are requested; do not claim an external change without evidence.

This current structure replaces the initial Netlify migration plan. Netlify scripts, functions and historical reports are retained for their existing uses and history; they are not the current GitHub/Cloudflare deployment instructions.

## Editing and publishing

Preserve the black, warm gold and ivory identity, Arabic RTL, original logos/covers and existing user flows. Keep the reference upload unchanged. Keep older deliverables available at their existing URLs; choose the active version from MDAAR_HUB.md rather than from filenames containing “latest”.

Check related surfaces when shared facts change: price on Zid versus the promotional site, recipe count, training programs and book links/QR. Updating one surface does not update the others automatically. The owner has limited the shared hub to the five areas above; keep historical media files outside its navigation unless requested.

For Pages changes, use `scripts/build-github-pages.py` and the existing publication workflow so the /Mdaar21/ prefix, CSP and Cloudflare origin are retained. Do not overwrite the deployed app with unprocessed source HTML. Distinguish source commits from verified live deployment. Respect the owner's requested scope and publishing authorization, including authorization already given in the session; do not ask again for the same authorized step. Do not merge or publish unrelated changes.

## Security and data

- Never commit API keys, passwords, tokens or environment secrets; never repeat exposed credentials from conversation history. Keep service secrets on the service.
- Escape untrusted content; use textContent for plain text.
- Preserve distributed request limits and the assistant's session protections.
- Do not send messages to others or perform purchases as part of routine site work.
- Do not fabricate reviews, medical accuracy or guaranteed fitness results. Nutritional values are estimates.
- Do not expose the full paid book in public marketing navigation. The hub is an owner/developer reference in the repository, not a new storefront download page.
- Do not reintroduce removed food-photo features or the removed “ولّد خطتي” interface without a new request. Keep customer-facing AI wording preferences recorded in existing copy; the assistant is called “اسأل مدار”.

## Verification

For app code changes, use appropriate existing checks (`npm run check`, `npm test`, browser/accessibility checks where affected). For book work, follow its build and visual review instructions. For documentation and source organization alone, verify links, paths and preservation of copied source/assets; a full application regression run is unnecessary unless content or behavior changed.

Main development: Node.js 22+, `npm ci --ignore-scripts`, `npm run dev`. Do not print secret values while investigating configuration. Clearly report external services or behaviors that were not tested.
