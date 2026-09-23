import unittest
from camden_work import catalog
from camden_work.core import Denied

class CatalogOutcomes(unittest.TestCase):
    def test_each_outcome_matches_full_records(self):
        raw=catalog.data()
        for outcome in raw['outcome_tags']:
            expected=[r['id'] for r in raw['entries'] if outcome in r['facets']['primary_outcome_tags']]
            seen=[];offset=0
            while True:
                result=catalog.search(outcome=outcome,offset=offset,limit=25)
                self.assertEqual(result['total'],len(expected))
                seen.extend(r['id'] for r in result['items'])
                if result['next_offset'] is None:break
                offset=result['next_offset']
            self.assertEqual(seen,expected)

    def test_unknown_and_wrong_type_outcomes_rejected(self):
        for value in ['unknown',[],1,True]:
            with self.assertRaises(Denied):catalog.search(outcome=value)

    def test_combined_filters_and_empty_result(self):
        rows=catalog.search(family='TX',basis='R',outcome='EFFECT')['items']
        self.assertTrue(rows)
        self.assertTrue(all(r['family']=='TX' and r['evidence_basis']=='R' for r in rows))
        self.assertEqual(catalog.search(query='no-match-zzzzzz',outcome='EFFECT')['total'],0)
