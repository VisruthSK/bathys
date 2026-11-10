# /// script
# requires-python = ">=3.13"
# dependencies = ["playwright==1.64.1"]
# ///
"""Browser proof: font decoding, controls, responsive layout and visual artifacts."""

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def check_browser(browser_type, engine_name):
    browser = browser_type.launch(headless=True)
    page = browser.new_page(
        viewport={"width": 1440, "height": 1000}, device_scale_factor=1
    )
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto("http://127.0.0.1:8765/proof.html")
    page.evaluate("document.fonts.ready")
    metrics = page.evaluate("""async () => {
      const variants=[['staticOTF','Bathys-Regular.otf'],['staticWOFF','Bathys-Regular.woff2'],['variableOTF','Bathys-Variable.otf'],['variableWOFF','Bathys-Variable.woff2']];
      const canvas=document.createElement('canvas');const ctx=canvas.getContext('2d');const result={};
      for(const [name,file] of variants){
        const face=await new FontFace(name,`url(fonts/${file})`).load();document.fonts.add(face);
        // At 1000 px, one design unit is one device pixel. This compares
        // font data without CFF/CFF2 rasterizer rounding at smaller sizes.
        ctx.font=`1000px ${name}`;result[name]=ctx.measureText('CORINNE BAILEY RAE').width;
      }
      return result;
    }""")
    assert max(metrics.values()) - min(metrics.values()) < 0.05, metrics
    assert page.evaluate('document.fonts.check("100px Bathys")')
    assert (
        page.evaluate('[...document.fonts].find(f=>f.family==="Bathys").status')
        == "loaded"
    )
    labels = page.locator(".pair small").all_text_contents()
    assert len(labels) == 28
    for removed in ["RO", "ON", "OL", "LO", "OE", "ORA", "CORO", "OOR", "TI"]:
        assert not any(label.startswith(removed + " /") for label in labels)
    page.screenshot(
        path=str(ROOT / f"extract/generated/browser-proof-{engine_name}.png"),
        full_page=True,
    )
    measure = """() => {const r=document.createRange();r.selectNodeContents(document.getElementById('type'));return r.getBoundingClientRect().width;}"""
    original = page.locator("#type").inner_text()
    page.locator("#type").fill("TU")
    page.locator("#liga").uncheck()
    plain_tu = page.evaluate(measure)
    page.locator("#liga").check()
    assert page.evaluate(measure) < plain_tu * 0.95, (
        "TU must actually form its ligature"
    )
    page.locator("#dlig").uncheck()
    page.locator("#type").fill(original)
    page.locator("#smallcaps").check()
    settings = page.locator("#type").evaluate(
        "(e)=>getComputedStyle(e).fontFeatureSettings"
    )
    assert '"smcp"' in settings and '"smcp" 0' not in settings
    page.locator("#liga").uncheck()
    assert '"liga" 0' in page.locator("#type").evaluate(
        "(e)=>getComputedStyle(e).fontFeatureSettings"
    )
    page.locator("#dlig").check()
    page.locator("#type").fill("CORONA / WE ORBIT")
    assert page.locator("#type").inner_text() == "CORONA / WE ORBIT"
    page.locator("#size").fill("80")
    page.locator("#size").dispatch_event("input")
    assert page.locator("#type").evaluate("(e)=>getComputedStyle(e).fontSize") == "80px"
    page.locator("#smallcaps").uncheck()
    page.locator("#type").fill("CORINNE")
    measure = """() => {const r=document.createRange();r.selectNodeContents(document.getElementById('type'));return r.getBoundingClientRect().width;}"""
    normal = page.evaluate(measure)
    page.locator("#width").fill("115")
    page.locator("#width").dispatch_event("input")
    assert page.evaluate(measure) > normal * 1.12, (
        "Variable width must change actual glyph layout"
    )
    page.locator("#type").fill("THE SEA\nAFTER THE STARS")
    assert page.locator("#type").inner_text() == "THE SEA\nAFTER THE STARS"
    page.locator("#theme").click()
    assert page.locator("body").evaluate('(e)=>e.classList.contains("dark")')
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
        "Mobile horizontal overflow"
    )
    page.screenshot(
        path=str(ROOT / f"extract/generated/mobile-proof-{engine_name}.png"),
        full_page=True,
    )
    assert not errors, errors
    page.set_viewport_size({"width": 1600, "height": 1640})
    for name in ["glyph-proof", "reference-study", "ligatures", "spacing-proof"]:
        page.set_content(
            f'<img style="width:1580px" src="http://127.0.0.1:8765/svg/Bathys-{name}.svg">'
        )
        page.locator("img").evaluate("(image)=>image.decode()")
        page.locator("img").screenshot(
            path=str(ROOT / f"extract/generated/{name}-{engine_name}.png")
        )
    browser.close()
    print(
        f"PASS {engine_name}: font decoding, controls, variable width and mobile layout."
    )


with sync_playwright() as p:
    for engine in ["chromium", "firefox", "webkit"]:
        check_browser(getattr(p, engine), engine)
