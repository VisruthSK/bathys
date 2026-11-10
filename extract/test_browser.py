"""Exercise the static specimen at http://127.0.0.1:8765/ in three browsers."""

from pathlib import Path

from playwright.sync_api import sync_playwright

from outlines import DLIGS, LIGS

ROOT = Path(__file__).resolve().parent.parent
PANGRAM = "SPHINX OF BLACK QUARTZ, JUDGE MY VOW."
MEASURE = """() => {
  const editor = document.getElementById('type');
  const style = getComputedStyle(editor);
  const probe = document.createElement('span');
  probe.textContent = editor.value;
  for (const property of ['fontFamily', 'fontSize', 'fontFeatureSettings',
    'fontVariationSettings', 'fontStretch', 'letterSpacing']) probe.style[property] = style[property];
  probe.style.whiteSpace = 'pre'; probe.style.position = 'fixed'; probe.style.left = '-10000px';
  document.body.append(probe);
  const width = probe.getBoundingClientRect().width;
  probe.remove();
  return width;
}"""


def font_size(locator):
    return locator.evaluate("e => parseFloat(getComputedStyle(e).fontSize)")


def check_browser(engine, name):
    browser = engine.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.add_init_script("""window.policyViolations = [];
      document.addEventListener('securitypolicyviolation', e => policyViolations.push(e.violatedDirective));""")
    assert page.goto("http://127.0.0.1:8765/").status == 200
    page.evaluate("document.fonts.ready")
    editor = page.locator("#type")
    assert editor.input_value() == PANGRAM
    assert page.locator("#sizeValue").input_value() == "64"
    assert abs(font_size(editor) - 64 * 4 / 3) < 0.1
    assert (
        page.locator(
            ".unjoined, .pair-only, .joining-comparison, select, .tester-bottom"
        ).count()
        == 0
    )
    assert page.locator(".character-inspector").is_visible()
    assert page.evaluate(
        "document.querySelector('.smallcap-row').nextElementSibling.classList.contains('character-inspector')"
    )
    assert page.locator("#reset").evaluate("e => e.closest('.controls') !== null")
    assert (
        page.locator(".about-writing .writing-placeholder").evaluate(
            "e => getComputedStyle(e).borderBottomStyle"
        )
        == "solid"
    )
    assert "Bathys" in page.locator(".site-title").evaluate(
        "e => getComputedStyle(e).fontFamily"
    )
    assert page.locator("#reference img").count() == 2
    assert page.locator(".writing-placeholder").all_text_contents() == [
        "TODO: WRITE",
        "TODO: WRITE",
    ]
    assert page.locator("#pairs small").all_text_contents() == list(LIGS)
    assert page.locator("#optionalPairs small").all_text_contents() == list(DLIGS)
    sample_copy = page.locator("#samples").inner_text().upper()
    assert (
        "THE SEA" not in sample_copy
        and "CORINNE" not in sample_copy
        and "BAILEY RAE" not in sample_copy
    )
    assert (
        page.locator(
            "svg, script:not([src]), style, [onclick], #zero, #sample, #figures"
        ).count()
        == 0
    )
    assert (
        page.evaluate("getComputedStyle(document.body).backgroundColor")
        == "rgb(246, 239, 225)"
    )
    assert page.evaluate("""() => {
      const header = document.querySelector('.site-header').getBoundingClientRect();
      const nav = document.querySelector('nav').getBoundingClientRect();
      const button = document.getElementById('theme').getBoundingClientRect();
      return Math.abs((nav.left + nav.right - header.left - header.right) / 2) < 1
        && Math.abs((nav.top + nav.bottom - button.top - button.bottom) / 2) < 1;
    }""")
    metrics = page.evaluate("""async () => {
      const ctx = document.createElement('canvas').getContext('2d'); const widths = [];
      for (const [i,file] of ['Bathys-Regular.otf','Bathys-Regular.woff2','Bathys-Variable.otf','Bathys-Variable.woff2'].entries()) {
        const family = 'CheckFont' + i;
        document.fonts.add(await new FontFace(family, `url(fonts/${file})`).load());
        ctx.font = `1000px ${family}`; widths.push(ctx.measureText('BATHYS THEATRE').width);
      }
      return widths;
    }""")
    assert max(metrics) - min(metrics) < 0.05, metrics
    for word in ["ATH", "THEATRE", "WTW", "EVT"]:
        editor.fill(word)
        editor.evaluate(
            'e => e.style.fontFeatureSettings = \'"liga" 1, "calt" 1, "kern" 1\''
        )
        chain = page.evaluate(MEASURE)
        editor.evaluate(
            'e => e.style.fontFeatureSettings = \'"liga" 1, "calt" 0, "kern" 1\''
        )
        assert chain < page.evaluate(MEASURE) - 1
    editor.evaluate("e => e.style.removeProperty('font-feature-settings')")
    editor.fill(PANGRAM)
    page.locator("#sizeValue").fill("240")
    assert abs(font_size(editor) - 320) < 0.1
    assert float(page.locator("#size").get_attribute("max")) >= 240
    page.locator("#size").dblclick()
    assert page.locator("#sizeValue").input_value() == "64"
    assert page.locator("#size").get_attribute("max") == "150"
    page.locator("#sizeValue").fill("64.5")
    assert abs(font_size(editor) - 86) < 0.1
    page.locator("#widthValue").fill("105.25")
    assert "105.25" in editor.evaluate("e => getComputedStyle(e).fontVariationSettings")
    page.locator("#width").dblclick()
    assert page.locator("#widthValue").input_value() == "100"
    page.locator("#trackingValue").fill("-3.5")
    assert editor.evaluate("e => getComputedStyle(e).letterSpacing") == "-3.5px"
    page.locator("#tracking").dblclick()
    assert page.locator("#trackingValue").input_value() == "0"
    page.locator("#glyph").fill("Q")
    assert page.locator("#glyphView").inner_text() == "Q"
    page.locator("#glyphSizeValue").fill("500")
    assert page.locator("#glyphView").evaluate("e => e.style.fontSize") == "500pt"
    # Firefox rounds this large computed point size to a whole CSS pixel.
    assert abs(font_size(page.locator("#glyphView")) - 500 * 4 / 3) < 0.5
    page.locator("#glyphSize").dblclick()
    assert page.locator("#glyphSizeValue").input_value() == "255"
    editor.fill('<img src=x onerror="window.injected=1">')
    assert (
        page.locator("#try img").count() == 0
        and page.evaluate("window.injected") is None
    )
    page.locator("#smallcaps").check()
    assert '"smcp"' in editor.evaluate("e => getComputedStyle(e).fontFeatureSettings")
    page.locator("#reset").click()
    assert editor.input_value() == '<img src=x onerror="window.injected=1">'
    assert page.locator("#sizeValue").input_value() == "64"
    assert not page.locator("#smallcaps").is_checked()
    editor.fill(PANGRAM)
    page.locator("#glyph").fill("S")
    page.locator("#theme").click()
    assert (
        page.evaluate("getComputedStyle(document.body).backgroundColor")
        == "rgb(10, 10, 10)"
    )
    for width in [390, 320]:
        page.set_viewport_size({"width": width, "height": 844})
        page.locator("details").evaluate_all(
            "items => items.forEach(item => item.open = true)"
        )
        page.locator("#glyph").fill("W")
        page.locator("#glyphSizeValue").fill("500")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
            name,
            width,
        )
        assert (
            len(
                page.locator(".covers")
                .evaluate("e => getComputedStyle(e).gridTemplateColumns")
                .split()
            )
            == 2
        )
        page.locator("#glyphSizeValue").fill("255")
        page.locator("#glyph").fill("S")
        page.locator("details").evaluate_all(
            "items => items.forEach(item => item.open = false)"
        )
    assert not errors, errors
    assert page.evaluate("window.policyViolations") == [], page.evaluate(
        "window.policyViolations"
    )
    # Capture after policy checks: WebKit's screenshot harness injects styles.
    page.set_viewport_size({"width": 390, "height": 844})
    page.screenshot(
        path=str(ROOT / f"extract/generated/mobile-{name}.png"),
        full_page=True,
        caret="initial",
    )
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.locator("#theme").click()
    for section in ["try", "samples", "alphabet", "joins", "reference"]:
        page.locator(f"#{section}").screenshot(
            path=str(ROOT / f"extract/generated/{section}-{name}.png"), caret="initial"
        )
    page.screenshot(
        path=str(ROOT / f"extract/generated/site-{name}.png"),
        full_page=True,
        caret="initial",
    )
    browser.close()
    print(
        f"PASS {name}: final specimens, typed values, slider resets, navbar, security and mobile layout."
    )


if __name__ == "__main__":
    with sync_playwright() as playwright:
        for name in ["chromium", "firefox", "webkit"]:
            check_browser(getattr(playwright, name), name)
