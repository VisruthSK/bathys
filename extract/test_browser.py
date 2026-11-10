"""Exercise the live specimen in Chromium, Firefox and WebKit."""

from contextlib import closing
from http.client import HTTPConnection
from pathlib import Path

from playwright.sync_api import sync_playwright

from outlines import DLIGS, LIGS

ROOT = Path(__file__).resolve().parent.parent
MEASURE = """() => {
  const editor = document.getElementById('type');
  const style = getComputedStyle(editor);
  const probe = document.createElement('span');
  probe.textContent = editor.value;
  for (const property of ['fontFamily', 'fontSize', 'fontFeatureSettings',
    'fontVariationSettings', 'fontStretch', 'letterSpacing']) probe.style[property] = style[property];
  probe.style.whiteSpace = 'pre';
  probe.style.position = 'fixed';
  probe.style.left = '-10000px';
  document.body.append(probe);
  const width = probe.getBoundingClientRect().width;
  probe.remove();
  return width;
}"""


def check_http():
    for path, expected in [
        ("/", 200),
        ("/index.html", 200),
        ("/specimen.css", 200),
        ("/specimen.js", 200),
        ("/fonts/Bathys-Variable.woff2", 200),
        ("/assets/icon.png", 200),
        ("/proof.html", 301),
        ("/extract/build.py", 404),
        ("/README.md", 404),
        ("/_headers", 404),
        ("/%5fheaders", 404),
        ("/fonts/", 404),
    ]:
        for method in ["GET", "HEAD"]:
            with closing(HTTPConnection("127.0.0.1", 8765)) as connection:
                connection.request(method, path)
                response = connection.getresponse()
                assert response.status == expected, (method, path, response.status)
                assert response.getheader("X-Content-Type-Options") == "nosniff"
                assert "frame-ancestors 'none'" in response.getheader(
                    "Content-Security-Policy"
                )
                assert response.getheader("Cache-Control") == "no-cache"
                if path == "/proof.html":
                    assert response.getheader("Location") == "/"
                body = response.read()
                if expected == 404 and method == "GET":
                    assert body == (ROOT / "404.html").read_bytes()
    print(
        "PASS HTTP: index, response headers, legacy redirect, private files and directory listings."
    )


def check_browser(engine, name):
    browser = engine.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.add_init_script("""window.policyViolations = [];
      document.addEventListener('securitypolicyviolation', e =>
        window.policyViolations.push(e.violatedDirective + ': ' + e.blockedURI));""")
    response = page.goto("http://127.0.0.1:8765/")
    assert response.status == 200
    headers = response.headers
    assert "frame-ancestors 'none'" in headers["content-security-policy"]
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["referrer-policy"] == "no-referrer"
    assert headers["cross-origin-opener-policy"] == "same-origin"
    page.evaluate("document.fonts.ready")
    initial_policy_reports = page.evaluate("window.policyViolations")
    # WebKit 27.2 reports its own <select> shadow-tree styles against CSP:
    # https://bugs.webkit.org/show_bug.cgi?id=327212. Keep the page's strict
    # policy, allow only the initial native-control reports (one per select
    # and policy), and reject
    # any additional report produced by application controls or screenshots.
    policy_count = (
        1 + page.locator('meta[http-equiv="Content-Security-Policy"]').count()
    )
    native_reports = page.locator("select").count() * policy_count
    assert not initial_policy_reports or (
        name == "webkit"
        and initial_policy_reports == ["style-src-attr: inline"] * native_reports
    ), initial_policy_reports
    assert page.locator("#type").input_value().startswith("SPHINX OF BLACK QUARTZ")
    text_width = "e => {const r = document.createRange(); r.selectNodeContents(e); return r.getBoundingClientRect().width;}"
    narrow = page.locator(".width-narrow").evaluate(text_width)
    wide = page.locator(".width-wide").evaluate(text_width)
    assert wide > narrow * 1.3, "Width examples must use real font variations"
    assert page.locator("#pairs small").all_text_contents() == [
        f"{p} / STANDARD" for p in LIGS
    ]
    assert page.locator("#optionalPairs small").all_text_contents() == [
        f"{p} / OPTIONAL" for p in DLIGS
    ]
    assert page.locator("svg, script:not([src]), style, [onclick], #zero").count() == 0
    assert (
        page.evaluate("getComputedStyle(document.body).backgroundColor")
        == "rgb(246, 239, 225)"
    )
    metrics = page.evaluate("""async () => {
      const ctx = document.createElement('canvas').getContext('2d');
      const result = [];
      for (const [i, file] of ['Bathys-Regular.otf', 'Bathys-Regular.woff2',
        'Bathys-Variable.otf', 'Bathys-Variable.woff2'].entries()) {
        const family = 'CheckFont' + i;
        const face = await new FontFace(family, `url(fonts/${file})`).load();
        document.fonts.add(face);
        ctx.font = `1000px ${family}`;
        result.push(ctx.measureText('CORINNE BAILEY RAE').width);
      }
      return result;
    }""")
    assert max(metrics) - min(metrics) < 0.05, metrics
    for word in ["ATH", "THEATRE", "WTW", "VTH", "EVT", "AVT", "EWT"]:
        page.locator("#type").fill(word)
        page.locator("#type").evaluate(
            'e => e.style.fontFeatureSettings = \'"liga" 1, "calt" 1, "kern" 1\''
        )
        chain = page.evaluate(MEASURE)
        page.locator("#type").evaluate(
            'e => e.style.fontFeatureSettings = \'"liga" 1, "calt" 0, "kern" 1\''
        )
        pair = page.evaluate(MEASURE)
        assert chain < pair - 1, (name, word, chain, pair)
    page.locator("#type").evaluate(
        "e => e.style.removeProperty('font-feature-settings')"
    )
    page.locator("#type").fill("CORINNE")
    normal = page.evaluate(MEASURE)
    page.locator("#width").fill("115")
    page.locator("#width").dispatch_event("input")
    assert page.evaluate(MEASURE) > normal * 1.12
    page.locator("#size").fill("80")
    page.locator("#size").dispatch_event("input")
    assert page.locator("#type").evaluate("e => getComputedStyle(e).fontSize") == "80px"
    page.locator("#smallcaps").check()
    settings = page.locator("#type").evaluate(
        "e => getComputedStyle(e).fontFeatureSettings"
    )
    assert '"smcp"' in settings and '"smcp" 0' not in settings
    page.locator("#liga").uncheck()
    assert '"calt" 0' in page.locator("#type").evaluate(
        "e => getComputedStyle(e).fontFeatureSettings"
    )
    page.locator("#type").fill('<img src=x onerror="window.injected=1">')
    assert page.locator("#try img").count() == 0
    assert page.evaluate("window.injected") is None
    page.locator("#reset").click()
    page.locator("#sample").select_option("0")
    assert (
        page.locator("#type").input_value() == "SPHINX OF BLACK QUARTZ,\nJUDGE MY VOW."
    )
    page.locator(".glyph-details").evaluate("element => element.open = true")
    page.locator("#glyph").select_option("6")
    assert page.locator("#glyphView").inner_text() == "6"
    page.locator("#glyph").select_option("S")
    page.locator(".glyph-details").evaluate("element => element.open = false")
    assert page.evaluate("window.policyViolations") == initial_policy_reports
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.locator("#theme").click()
    assert (
        page.evaluate("getComputedStyle(document.body).backgroundColor")
        == "rgb(10, 10, 10)"
    )
    assert page.locator("#theme").get_attribute("aria-pressed") == "true"
    for width in [390, 320]:
        page.set_viewport_size({"width": width, "height": 844})
        page.locator("details").evaluate_all(
            "items => items.forEach(item => item.open = true)"
        )
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
            "Mobile overflow",
            width,
        )
        page.locator("details").evaluate_all(
            "items => items.forEach(item => item.open = false)"
        )
    assert not errors, errors
    assert page.evaluate("window.policyViolations") == initial_policy_reports
    # Screenshot capture injects a Playwright stylesheet in WebKit. Check the
    # application's CSP above, before the capture harness adds its own reports.
    page.set_viewport_size({"width": 390, "height": 844})
    page.screenshot(
        caret="initial",
        path=str(ROOT / f"extract/generated/mobile-{name}.png"),
        full_page=True,
    )
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.locator("#theme").click()
    for section in ["try", "alphabet", "joins", "figures", "origins"]:
        page.locator(f"#{section}").screenshot(
            caret="initial", path=str(ROOT / f"extract/generated/{section}-{name}.png")
        )
    page.screenshot(
        caret="initial",
        path=str(ROOT / f"extract/generated/site-{name}.png"),
        full_page=True,
    )
    browser.close()
    print(
        f"PASS {name}: fonts, joins, controls, content security, brand colours and mobile layout."
    )


if __name__ == "__main__":
    check_http()
    with sync_playwright() as playwright:
        for name in ["chromium", "firefox", "webkit"]:
            check_browser(getattr(playwright, name), name)
