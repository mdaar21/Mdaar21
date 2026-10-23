# GitHub account rename verification

Verified 24 October 2026 for the renamed account `mdaar21`.

## Published addresses

- Marketing site: https://mdaar21.github.io/Mdaar21/discover/
- Fitness application: https://mdaar21.github.io/Mdaar21/
- Repository: https://github.com/mdaar21/Mdaar21
- Service: https://mdaar21-service.nbbttdhnybnnb.workers.dev
- Updated book: [original identity v5](../artifacts/mdaar-protocol-original-identity-v5.pdf)

The service hostname belongs to the existing Cloudflare account and remains valid. Changing the GitHub username does not rename the Cloudflare account namespace. No domain was purchased and no payment was made.

## Changes and deployment

Source commit `5ce36be12b769385f28b4d38b3abcf00e3689c41` updates active GitHub URLs, canonical metadata, the book link and QR code, setup instructions and portable website/ad archives. Historical editions and reports retain their original addresses.

GitHub Pages published commit `3faef9fb6944bc7e5da283ca2ff5e059a64d9840` successfully. Service repository `mdaar21/mdaar21-service` deployed commit `0d58908c1f99b697dc29686113ff44e3b46a42fb` through its Cloudflare Git integration, changing the allowed origin to `https://mdaar21.github.io`. Existing service secrets were not read or copied.

## Verification

- 86 unit/integration tests passed; JavaScript syntax, asset and secret-pattern checks passed. After adding the retired-origin assertion, all 17 targeted Cloudflare and remote-adapter tests passed.
- Live marketing page returned HTTP 200 at mobile (390 px) and desktop (1440 px) widths with no horizontal overflow, runtime errors or failed requests. Mobile navigation, program switching and the book preview worked. Clicking the purchase button reached the direct Zid product page with HTTP 200.
- From the new live application, sending a question through “اسأل مدار” returned an Arabic answer and HTTP 200 from `/api/ai`. One expired/invalid session response (401) was renewed automatically by the existing adapter before the successful response. The final check recorded no runtime errors or failed requests.
- A session request from the retired GitHub origin returned HTTP 403. The new origin was accepted.
- The new PDF downloaded publicly with HTTP 200 and matched the local SHA-256. It has 34 pages and 226 exercise-video links. Exercise URIs match the preceding edition page by page; all 11 original cover rasters are unchanged. The QR code decoded from the final PDF opens the new fitness application URL. Video availability and exercise technique were not reviewed.

Machine-readable evidence: [account-rename.json](account-rename.json). No credentials or answer contents are included.
