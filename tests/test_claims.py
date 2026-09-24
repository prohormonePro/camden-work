import json,unittest
from tools.check_claims import R,validate
class ClaimsTests(unittest.TestCase):
    def test_register_references_and_source_identities(self):self.assertEqual(validate(json.loads((R/'docs/claims.json').read_text())),[])
    def test_tested_claim_without_test_is_rejected(self):
        d=json.loads((R/'docs/claims.json').read_text());d['claims'][0]['named_tests']=[]
        self.assertTrue(any('EVIDENCE_REQUIRED' in e for e in validate(d)))
    def test_missing_run_wrong_test_and_changed_source_are_rejected(self):
        d=json.loads((R/'docs/claims.json').read_text());r=d['claims'][0];r['evidence_status']='PUBLIC_RUN_OBSERVED';r['named_tests']=['tests/test_core.py::not_a_test'];r['source_sha256']['camden_work/core.py']='0'*64
        errors=validate(d)
        for code in ['RUN_REQUIRED','TEST_NOT_FOUND','SOURCE_CHANGED']:self.assertTrue(any(code in e for e in errors))
