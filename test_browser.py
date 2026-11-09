"""Browser proof: font decoding, controls, responsive layout and visual artifacts."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8765/proof.html')
    page.evaluate('document.fonts.ready')
    assert page.evaluate('document.fonts.check("100px Bathys")')
    assert page.evaluate('[...document.fonts].find(f=>f.family==="Bathys").status')=='loaded'
    page.screenshot(path=str(ROOT/'svg/Bathys-browser-proof.png'),full_page=True)
    page.locator('#smallcaps').check()
    settings=page.locator('#type').evaluate('(e)=>getComputedStyle(e).fontFeatureSettings')
    assert '"smcp"' in settings and '"smcp" 0' not in settings
    page.locator('#liga').uncheck()
    assert '"liga" 0' in page.locator('#type').evaluate('(e)=>getComputedStyle(e).fontFeatureSettings')
    page.locator('#dlig').check()
    page.locator('#type').fill('CORONA / WE ORBIT')
    assert page.locator('#type').inner_text()=='CORONA / WE ORBIT'
    page.locator('#size').fill('80');page.locator('#size').dispatch_event('input')
    assert page.locator('#type').evaluate('(e)=>getComputedStyle(e).fontSize')=='80px'
    page.locator('#theme').click()
    assert page.locator('body').evaluate('(e)=>e.classList.contains("dark")')
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'Mobile horizontal overflow'
    page.screenshot(path=str(ROOT/'svg/Bathys-mobile-proof.png'),full_page=True)
    assert not errors,errors
    browser.close()
print('PASS: webfont loads; editable proof, feature toggles, size, theme and mobile layout work.')
