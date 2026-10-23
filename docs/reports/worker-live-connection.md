# Published assistant connected — 2026-10-23

Site: https://nbbttdhnybnnb-crypto.github.io/Mdaar21/
Service: https://mdaar21-service.nbbttdhnybnnb.workers.dev
Pages deployment: `76fe16d17731d01b30afa95aa7acf6c0c5390546`, built successfully on GitHub at `2026-10-23T20:05:24Z`.

The owner’s screenshot revealed the actual public Worker origin. No provider or platform secret was read, added to code or committed. `config/github-pages.json` persists that public origin; the Pages builder reads it by default and applies the matching meta configuration, exact connect-src policy and Cloudflare-specific Arabic/English privacy text. An explicit --service-origin still overrides it; an explicit empty value creates an unconfigured build.

## Live results

The actual Worker returned HTTP 200 and configured=true. Preflight from the GitHub origin returned 204 and the correct allowed origin. POST /api/session with start:true returned 200 and a signed session automatically; a real, generic Arabic question to /api/ai returned 200 with the expected answer/suggestions shape. Evidence: worker-live-connection.json. Tokens and generated contents are omitted.

The final mobile browser test loaded the actual published site and its real assets, then sent a generic question through the live service to the real provider. It verified the configured public origin, all 500 meals, absence of the removed daily generator and separate consent controls, zero service requests on page load, one successful automatic session and one successful answer. The returned answer was Arabic, the token was absent from localStorage, and there were no runtime errors or mobile width overflow. Evidence: worker-live-ui.json. Screenshot remains local at /workspace/mdaar-local/worker-live-ui/assistant-connected.png; no personal data or credentials appear in it.

The test used a trusted browser HTTP relay to fetch actual network responses, with no mocks or TLS verification bypass. A plain Python client received Cloudflare error 1010; the normal browser client succeeded. One initial UI check exercised the supported single 401/session-refresh path and then received an answer; its overly strict test assumption that every run must create exactly one session was corrected. The final run needed one session. No authentication rule, IP binding or quota was weakened.

## Local verification

All 86 unit/integration tests passed after configuring the origin. Project checks passed for 27 JavaScript files, referenced assets, document IDs and credential-pattern screening. The actual default Pages build includes the service URL and exact CSP, removes the unavailable banner and preserves removed controls. Existing 18 targeted browser regressions and four cross-origin fixture browser checks cover their previously recorded preparation scope; the final live browser checks verify the production connection directly.

The secret stays exclusively in the owner’s Cloudflare configuration. No billing changes, old-host deployments or purchases were made. Replies remain general estimates; this check does not establish medical precision, unlimited availability or immunity to provider quotas.
