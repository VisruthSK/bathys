# Bathys

Display capitals inspired by the lettering on Corinne Bailey Rae’s _The Sea_ and _The Love EP_. Includes optical small caps, a spiral S, open bowls and automatic interlocks.

**[Open the specimen](index.html)** · [Regular OTF](fonts/Bathys-Regular.otf) · [Variable OTF](fonts/Bathys-Variable.otf)

The specimen starts with a free-writing box and samples at different sizes and widths. Character inspection, the full ligature catalogue and album comparisons open on demand. HTML, CSS and JavaScript are separate files. All assets are local; the page uses no third-party scripts or services. Colours follow `../brand/inst/_brand.yml`.

## Serve and publish

Preview the public export with its response headers:

```powershell
uv run --project extract --locked extract/serve.py
```

Open `http://127.0.0.1:8765/`. The preview exports only public assets to `dist/`, serves `index.html` at the root and applies `_headers`. It does not expose the build tools or directory listings.

For Cloudflare Pages, use these settings:

| Setting                | Value                        |
| ---------------------- | ---------------------------- |
| Framework preset       | None                         |
| Build command          | `python3 extract/publish.py` |
| Build output directory | `dist`                       |

The export uses Python's standard library and the committed fonts; deployment does not need Node or font-building dependencies. You can also run `python3 extract/publish.py` and upload `dist/` to another static host.

[`_headers`](_headers) sets the CSP, frame restrictions, MIME sniffing protection, referrer policy, cross-origin policies, permissions policy and HTTPS HSTS. Files revalidate rather than retaining stale font builds. The HTML retains a fallback CSP. [`_redirects`](_redirects) sends the former `/proof.html` address to `/`.

[Cloudflare Pages applies `_headers` to static responses](https://developers.cloudflare.com/pages/configuration/headers/). Other hosts need equivalent response-header configuration; an ordinary file server does not apply this file automatically.

## Use the font

The variable font has a `wdth` axis from 85 to 115, with the reference width at 100. The static and variable defaults have identical outlines and metrics.

```css
@font-face {
  font-family: Bathys;
  src: url("fonts/Bathys-Variable.woff2") format("woff2");
  font-stretch: 85% 115%;
}

.title {
  font-family: Bathys, sans-serif;
  font-variation-settings: "wdth" 100;
  font-feature-settings:
    "liga" 1,
    "calt" 1,
    "kern" 1;
}
```

`liga` enables the standard pairs. `calt` connects longer runs using reusable forms derived from those pairs. `dlig` enables the denser optional interlocks. `smcp` and `c2sc` select optical small caps. Lowercase input otherwise displays as capitals.

Keep tracking at zero for connected lettering. Disable `calt` for pair-only composition, or both `calt` and `liga` for ordinary spacing.

## Build and check

Sources and build tools stay in [`extract/`](extract/), with dependencies locked by uv. The compiler writes the four font files and `specimen-data.js`; the page uses the compiled font for every sample.

```powershell
uv run --project extract --locked --python 3.13 extract/build.py --check
uv run --project extract --locked extract/audit.py
uv run --project extract --locked ruff check extract
uv run --project extract --locked python -m unittest discover -s extract -p test_publish.py
```

With the preview server running, browser checks use Chromium, Firefox and WebKit:

```powershell
uv run --project extract --locked playwright install chromium firefox webkit
uv run --project extract --locked extract/test_browser.py
```

Checks cover outlines, spacing, small caps, ligatures, contextual chains, variable interpolation, browser controls, the content-security policy and mobile layout. Screenshots and audit output go into the ignored `extract/generated/` directory.
