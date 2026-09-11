import unittest
import csv
import sys

from u_test import perform_mann_whitney_u

def load_data():
    A = []
    B = []

    with open('perf-data.csv') as f:
        for row in csv.DictReader(f):
            A.append(float(row['A']))
            B.append(float(row['B']))

    return A, B

class TestGenAI(unittest.TestCase):
    def test_gemini_u_test(self):
        # Determined via external calculator
        EXPECTED_U = 6149.0
        ALPHA = 0.05
        IS_SIGNIFICANT = False
        # For float comparison
        EPSILON = 1.0e-6

        a, b = load_data()
        u, p = perform_mann_whitney_u(a, b)

        self.assertTrue(abs(u - EXPECTED_U) < EPSILON, 'U value was incorrect')
        self.assertEqual(p < ALPHA, IS_SIGNIFICANT, 'The P value indicated the wrong significance')

if __name__ == '__main__':
    for dep in ['numpy', 'scipy']:
        try:
            __import(dep)
        except:
            sys.exit(f"Missing dependency {dep}")
    unittest.main()
