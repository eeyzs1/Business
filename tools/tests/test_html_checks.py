import json
import tempfile
import unittest
from pathlib import Path

from tools.html_checks import Markup, check_common, quiz_errors


QUESTION = {"q": "Question?", "options": ["Yes", "No"], "answer": 0, "explain": "Why."}


class QuizSchemaTests(unittest.TestCase):
    def test_valid_question(self):
        self.assertEqual(quiz_errors([QUESTION]), [])

    def test_malformed_data_is_reported_without_crashing(self):
        invalid = [None, {}, [], "text", [None], [42], [dict(QUESTION, q=" ")],
                   [dict(QUESTION, options=[])], [dict(QUESTION, options=["Yes", 2])],
                   [dict(QUESTION, answer=True)], [dict(QUESTION, answer=0.5)],
                   [dict(QUESTION, answer=-1)], [dict(QUESTION, answer=2)],
                   [dict(QUESTION, explain=None)]]
        for data in invalid:
            with self.subTest(data=data):
                self.assertTrue(quiz_errors(data))


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "en").mkdir()
        (self.root / "en/index.html").write_text("<p>English</p>", encoding="utf-8")
        self.page = self.root / "index.html"

    def check(self, body, switch='en/index.html'):
        self.page.write_text(
            '<meta name="viewport" content="width=device-width"><link rel="icon" href="data:,">'
            '<a class="lang-switch" href="{}">EN</a>{}'.format(switch, body), encoding="utf-8")
        errors, warnings = [], []
        check_common(self.page, self.root, errors.append, warnings.append, ("example.org",))
        return errors, warnings

    def test_encoded_cross_page_anchor_and_query(self):
        (self.root / "a b.html").write_text('<p id="target">OK</p>', encoding="utf-8")
        self.assertEqual(self.check('<a href="a%20b.html?v=1#target">Link</a>')[0], [])
        self.assertTrue(any("anchor" in err for err in self.check('<a href="a%20b.html#missing">Link</a>')[0]))

    def test_single_quotes_and_local_anchors(self):
        self.assertEqual(self.check("<p id='here'></p><a href='#here'>Link</a>")[0], [])
        self.assertTrue(self.check("<a href='#absent'>Link</a>")[0])

    def test_script_text_is_not_parsed_as_markup(self):
        markup = Markup('<p id="a"></p><script>var demo = \'<p id="a">\';</script>')
        self.assertEqual(markup.ids, ["a"])

    def test_external_dependencies_and_unsafe_schemes(self):
        for body in ('<script src="//cdn.example.org/x.js"></script>',
                     '<link rel="stylesheet" href="https://example.org/style?v=2">',
                     '<img src="https://example.org/x.png">',
                     '<a href="javascript:alert(1)">Link</a>'):
            with self.subTest(body=body):
                self.assertTrue(self.check(body)[0])

    def test_host_whitelist_uses_hostname(self):
        self.assertEqual(self.check('<a href="https://sub.example.org/page">Link</a>')[1], [])
        self.assertTrue(self.check('<a href="https://example.org.evil.test/page">Link</a>')[1])
        self.assertTrue(self.check('<a href="https://evil.test/?q=example.org">Link</a>')[1])

    def test_duplicate_ids_and_wrong_switch(self):
        self.assertTrue(self.check('<p id="x"></p><p id="x"></p>')[0])
        self.assertTrue(self.check("", switch="index.html")[0])
        self.assertTrue(self.check('<a class="lang-switch" href="en/index.html">EN</a>')[0])

    def test_quiz_json_schema_and_missing_data(self):
        lessons = self.root / "01-economics/lessons"
        lessons.mkdir(parents=True)
        self.page = lessons / "0001-test.html"
        mirror = self.root / "en/01-economics/lessons"
        mirror.mkdir(parents=True)
        (mirror / self.page.name).write_text("", encoding="utf-8")
        switch = "../../en/01-economics/lessons/0001-test.html"
        self.assertTrue(self.check("", switch)[0])
        valid = '<script type="application/json">{}</script>'.format(json.dumps([QUESTION]))
        self.assertEqual(self.check(valid, switch)[0], [])
        self.assertTrue(self.check('<script type="application/json">{}</script>', switch)[0])
        self.assertTrue(self.check('<script type="application/json">[</script>', switch)[0])


if __name__ == "__main__":
    unittest.main()
