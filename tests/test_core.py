import unittest
from invoice_extractor.core import normalize, validate

class InvoiceTests(unittest.TestCase):
    def setUp(self):
        self.raw = {'invoice_number':'RT-2024-1052','invoice_date':'2024-10-14','supplier_name':'RIVERTECH SUPPLIES LTD.', 'currency':'NPR',
            'items':[{'description':'HDPE Pipe 110mm (6m length)','quantity':50,'unit':'pcs','unit_price':1250,'line_total':62500},
                     {'description':'HDPE Elbow 90° 110mm','quantity':20,'unit':'pcs','unit_price':450,'line_total':9000},
                     {'description':'HDPE Coupling 110mm','quantity':30,'unit':'pcs','unit_price':300,'line_total':9000},
                     {'description':'Welding Service','quantity':10,'unit':'hrs','unit_price':1500,'line_total':15000},
                     {'description':'Delivery Charge','quantity':1,'unit':'lot','unit_price':5000,'line_total':5000}],
            'subtotal':100500,'tax_rate_percent':13,'tax_amount':13065,'total_amount':113565}
    def test_sample_passes(self):
        self.assertEqual(validate(normalize(self.raw))['status'], 'passed')
    def test_wrong_total_flagged(self):
        self.raw['total_amount'] = 999
        result = validate(normalize(self.raw))
        self.assertEqual(result['status'], 'review_required')
        self.assertFalse(result['checks']['total_matches_subtotal_plus_tax'])
    def test_missing_fields_flagged(self):
        self.raw['invoice_number'] = None
        self.assertEqual(validate(normalize(self.raw))['status'], 'review_required')
    def test_wrong_line_total_flagged(self):
        self.raw['items'][0]['line_total'] = 62000
        self.assertEqual(validate(normalize(self.raw))['status'], 'review_required')
    def test_bad_numeric_does_not_crash(self):
        self.raw['items'][0]['unit_price'] = 'unreadable'
        self.assertEqual(validate(normalize(self.raw))['status'], 'review_required')

    def test_missing_line_total_requires_review(self):
        self.raw['items'][0]['line_total'] = None
        result = validate(normalize(self.raw))
        self.assertEqual(result['status'], 'review_required')
        self.assertTrue(any('line total' in warning for warning in result['warnings']))

    def test_invalid_items_type_is_reported(self):
        from invoice_extractor.core import ExtractionError
        self.raw['items'] = 'not a list'
        with self.assertRaises(ExtractionError):
            normalize(self.raw)

    def test_invalid_item_is_reported(self):
        from invoice_extractor.core import ExtractionError
        self.raw['items'] = [None]
        with self.assertRaises(ExtractionError):
            normalize(self.raw)

if __name__ == '__main__':
    unittest.main()
