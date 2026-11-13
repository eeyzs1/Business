#!/usr/bin/env python3
"""Browser regressions. Install tools/requirements-dev.txt and Playwright Chromium first.

Run: python tools/test_browser.py
Set BUSINESS_BROWSER_CHANNEL=chrome to use an installed Chrome instead.
The course itself has no third-party dependencies; these are development checks only.
"""
import json
import math
import os
import re
import sys
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ECON = "01-economics/lessons/0001-supply-and-demand.html"
NPV = "03-finance/lessons/0003-npv-and-irr.html"
STATS = "10-business-analytics/lessons/0002-descriptive-stats.html"


class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            channel=os.environ.get("BUSINESS_BROWSER_CHANNEL") or None, headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("console", lambda message: self.errors.append(message.text) if message.type == "error" else None)

    def tearDown(self):
        self.assertEqual(self.errors, [], "Browser errors")

    def go(self, relative):
        self.page.goto((ROOT / relative).as_uri())

    def answer_quiz(self, relative, correct=True):
        source = (ROOT / relative).read_text(encoding="utf-8")
        questions = json.loads(re.search(r'<script type="application/json">(.*?)</script>', source, re.S)[1])
        for question in questions:
            answer = question["answer"] if correct else (question["answer"] + 1) % len(question["options"])
            self.page.locator(".quiz-opt").nth(answer).click()
            self.page.locator(".quiz-next").click()
        return len(questions)

    def test_all_pages_offline_and_mobile_controls(self):
        self.page.set_viewport_size({"width": 320, "height": 900})
        pages = [ROOT / "index.html", ROOT / "en/index.html"]
        for base in (ROOT, ROOT / "en"):
            pages += sorted(base.glob("[0-9][0-9]-*/**/*.html"))
        self.assertEqual(len(pages), 122)
        for path in pages:
            with self.subTest(page=path.relative_to(ROOT).as_posix()):
                self.page.goto(path.as_uri())
                if "lessons" in path.parts:
                    self.assertEqual(self.page.locator(".quiz-opt").count(), 4)
                    if self.page.locator("html").get_attribute("lang") == "en":
                        self.assertNotRegex(self.page.locator(".quiz").inner_text(), r"[\u4e00-\u9fff]")
                for edge in ("min", "max"):
                    self.page.locator('input[type="range"]').evaluate_all(
                        "(els,edge) => els.forEach(el => {el.value=el[edge];el.dispatchEvent(new Event('input',{bubbles:true}));})", edge)
                    self.page.evaluate("() => new Promise(requestAnimationFrame)")
                    self.assertNotRegex(self.page.locator("main").inner_text(), r"\b(?:NaN|Infinity)\b")
                    invalid = self.page.locator("svg").evaluate_all(
                        "els => els.some(svg => [...svg.querySelectorAll('*')].some(el => [...el.attributes].some(a => /NaN|Infinity/.test(a.value))))")
                    self.assertFalse(invalid, "Invalid SVG geometry")
                    overflow = self.page.evaluate("document.documentElement.scrollWidth - innerWidth")
                    self.assertLessEqual(overflow, 1, "Horizontal overflow on mobile")

    def test_quiz_language_shared_history_and_retry(self):
        for prefix in ("", "en/"):
            relative = prefix + ECON
            self.go(relative)
            total = self.answer_quiz(relative)
            self.assertIn("{0} / {0}".format(total), self.page.locator(".quiz-score").inner_text())
            self.page.locator(".quiz-next").click()
            self.answer_quiz(relative, correct=False)
            self.assertIn("{0} / {0}".format(total), self.page.locator(".quiz-history").inner_text())
            self.assertNotIn("长期记忆库", self.page.locator(".quiz").inner_text())
            if prefix:
                self.assertNotRegex(self.page.locator(".quiz").inner_text(), r"[\u4e00-\u9fff]")
            self.go(prefix + "01-economics/index.html")
            self.assertEqual(self.page.locator(".ll-done").count(), 1)
            if prefix:
                self.assertIn("Lesson", self.page.locator(".lesson-list a").first.evaluate(
                    "el => getComputedStyle(el,'::before').content"))
            self.go(prefix + "index.html")
            self.assertEqual(self.page.locator(".bc-progress").count(), 1)
            self.assertIn("1/4", self.page.locator(".bc-progress").inner_text())

    def test_stored_scores_are_validated_and_refreshed(self):
        self.go(ECON)
        key = "biz-quiz:" + ECON
        self.page.evaluate("key => localStorage.setItem(key, JSON.stringify({best:99,total:4}))", key)
        self.page.reload()
        self.assertEqual(self.page.locator(".quiz-history").inner_text(), "")
        # Another tab completes a better attempt after this tab loaded.
        self.page.evaluate("key => localStorage.setItem(key, JSON.stringify({best:4,total:4}))", key)
        self.answer_quiz(ECON, correct=False)
        self.assertEqual(self.page.evaluate("key => JSON.parse(localStorage.getItem(key)).best", key), 4)
        self.go("index.html")
        self.assertEqual(self.page.locator(".bc-progress").count(), 1)
        self.page.evaluate("key => {localStorage.removeItem(key);window.dispatchEvent(new StorageEvent('storage',{key}));}", key)
        self.assertEqual(self.page.locator(".bc-progress").count(), 0)
        self.page.evaluate("key => {localStorage.setItem(key,JSON.stringify({best:2,total:4}));window.dispatchEvent(new Event('pageshow'));window.dispatchEvent(new Event('pageshow'));}", key)
        self.assertEqual(self.page.locator(".bc-progress").count(), 1)
        # A course edit changes the denominator; a previous 5/5 must not become 5/4.
        self.page.evaluate("key => localStorage.setItem(key,JSON.stringify({best:5,total:5}))", key)
        self.go(ECON)
        self.assertEqual(self.page.locator(".quiz-history").inner_text(), "")
        self.answer_quiz(ECON, correct=False)
        self.assertEqual(self.page.evaluate("key => JSON.parse(localStorage.getItem(key)).best", key), 0)

    def test_storage_unavailable_does_not_break_quiz(self):
        self.page.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage disabled');}})")
        self.go("en/" + ECON)
        self.answer_quiz("en/" + ECON)
        self.assertIn("could not be saved", self.page.locator(".quiz-history").inner_text())
        self.go("en/index.html")
        self.assertEqual(self.page.locator(".bc-progress").count(), 0)

    def test_invalid_quiz_displays_an_error(self):
        self.page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{document.querySelector('.quiz script').textContent='{}';});")
        self.go("en/" + ECON)
        self.assertIn("could not be loaded", self.page.locator(".quiz [role=alert]").inner_text())

    def test_drag_lessons_have_keyboard_controls(self):
        cases = ((ECON, "#sd-controls input", "#sd-readout"),
                 (STATS, "#bar-controls input", "#barReadout"),
                 ("04-marketing/lessons/0002-stp.html", "#positionCtrl input", "#pmReadout"))
        for prefix in ("", "en/"):
            for relative, control, readout in cases:
                self.go(prefix + relative)
                slider = self.page.locator(control).first
                before = self.page.locator(readout).inner_text()
                value = float(slider.input_value())
                slider.focus()
                slider.press("ArrowRight")
                self.page.evaluate("() => new Promise(requestAnimationFrame)")
                self.assertGreater(float(slider.input_value()), value)
                self.assertNotEqual(self.page.locator(readout).inner_text(), before)

    def test_ab_without_conversions_is_inconclusive(self):
        self.page.add_init_script("Math.random=()=>1;")
        for prefix in ("", "en/"):
            self.go(prefix + "10-business-analytics/lessons/0003-correlation-vs-causation.html")
            self.page.locator("#abGo").click()
            self.assertNotRegex(self.page.locator("#abDelta").inner_text(), r"NaN|Infinity")
            self.assertIn("does not prove" if prefix else "不等于", self.page.locator("#abVerdict").inner_text())

    def test_wrong_chart_match_recovers_after_timeout(self):
        for prefix in ("", "en/"):
            self.go(prefix + STATS)
            self.page.locator("#mgLeft button").nth(0).click()
            self.page.locator("#mgRight button").nth(1).click()
            self.page.locator("#mgLeft button").nth(1).click()
            self.page.wait_for_timeout(750)
            self.assertEqual(self.page.locator(".mg-item.bad").count(), 0)
            for i, chart_index in enumerate((2, 0, 1, 3)):
                self.page.locator("#mgLeft button").nth(i).click()
                self.page.locator("#mgRight button").nth(chart_index).click()
            self.assertEqual(self.page.locator(".mg-item.ok").count(), 8)

    def test_irr_includes_negative_and_zero_returns(self):
        for prefix in ("", "en/"):
            self.go(prefix + NPV)
            for investment, cash, years in ((60, 14, 8), (100, 3, 3), (60, 20, 3)):
                self.page.locator("#npv-controls input").evaluate_all(
                    "(els,vals)=>els.forEach((el,i)=>{el.value=vals[i];el.dispatchEvent(new Event('input',{bubbles:true}));})",
                    [investment, cash, years, 8])
                self.page.evaluate("() => new Promise(requestAnimationFrame)")
                text = self.page.locator("#npv-irr").inner_text()
                rate = float(re.search(r"-?\d+\.\d+", text)[0]) / 100
                residual = sum(cash / math.pow(1 + rate, year) for year in range(1, years + 1)) - investment
                self.assertAlmostEqual(residual, 0, delta=0.3)
                if investment > cash * years:
                    self.assertLess(rate, 0)
                    self.assertIn("within" if prefix else "期限内", self.page.locator("#npv-pay").inner_text())
                elif investment == cash * years:
                    self.assertEqual(rate, 0)

    def test_viz_handles_zero_values_and_pending_updates(self):
        self.go(ECON)
        result = self.page.evaluate("""async () => {
          const host=document.createElement('div');document.body.append(host);
          const bars=Viz.bars(host,[{label:'zero',value:0}],{animate:false});
          const calls=[];const slider=Viz.slider(host,{min:0,max:10,value:2});slider.onChange(v=>calls.push(v));
          slider.el.querySelector('input').dispatchEvent(new Event('input'));slider.set(6);
          await new Promise(requestAnimationFrame);
          return {calls,bars:bars.outerHTML,scale:Viz.scale(1,1,0,10)(1),inverse:Viz.scale(0,10,1,1).invert(1)};
        }""")
        self.assertEqual(result["calls"], [6])
        self.assertNotRegex(result["bars"], r"NaN|Infinity")
        self.assertEqual(result["scale"], 5)
        self.assertEqual(result["inverse"], 5)
        self.page.emulate_media(reduced_motion="no-preference")
        self.page.evaluate("""() => {
          const out=document.createElement('output');out.id='counter-test';document.body.append(out);
          Viz.countUp(out,100,{dur:120});Viz.countUp(out,200,{dur:20});
        }""")
        self.page.wait_for_timeout(180)
        self.assertEqual(self.page.locator("#counter-test").inner_text(), "200")

    def test_print_and_no_script_keep_content_visible(self):
        self.page.emulate_media(reduced_motion="no-preference")
        self.go(ECON)
        self.page.emulate_media(media="print")
        self.assertTrue(self.page.locator("[data-reveal]").evaluate_all(
            "els => els.length > 0 && els.every(el => getComputedStyle(el).opacity === '1')"))
        context = self.browser.new_context(java_script_enabled=False)
        try:
            page = context.new_page()
            page.goto((ROOT / ECON).as_uri())
            self.assertTrue(page.locator("[data-reveal]").evaluate_all(
                "els => els.every(el => getComputedStyle(el).opacity === '1')"))
        finally:
            context.close()

    def test_drag_uses_svg_coordinates_and_pointer_capture(self):
        self.go(ECON)
        self.page.evaluate("""() => {
          const svg=Viz.svgEl('svg',{id:'drag-test',viewBox:'10 20 200 100',style:'width:300px;height:300px;display:block'});
          const target=Viz.svgEl('rect',{x:90,y:60,width:20,height:20,fill:'red'});svg.append(target);document.body.prepend(svg);
          Viz.draggable(svg,target,p=>window.dragPoint={x:p.x,y:p.y});
        }""")
        box = self.page.locator("#drag-test rect").bounding_box()
        self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        self.page.mouse.down()
        self.page.mouse.move(500, 350)
        expected = self.page.locator("#drag-test").evaluate(
            "svg => {const p=svg.createSVGPoint();p.x=500;p.y=350;const q=p.matrixTransform(svg.getScreenCTM().inverse());return{x:q.x,y:q.y};}")
        self.assertEqual(self.page.evaluate("window.dragPoint"), expected)
        self.page.mouse.up()
        self.page.mouse.move(600, 400)
        self.assertEqual(self.page.evaluate("window.dragPoint"), expected)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
