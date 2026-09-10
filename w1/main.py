import unittest
import csv

from u_test import mann_whitney_u

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
        EXPECTED_U_VALUES = { 5732.0, 6149.0 }
        EXPECTED_U = min(EXPECTED_U_VALUES)
        EPSILON = 1.0e-6

        a, b = load_data()
        u, u1, u2 = mann_whitney_u(a, b)

        self.assertTrue(abs(u - EXPECTED_U) < EPSILON, 'U value was incorrect')
        self.assertTrue(any(u1 - abs(x) < EPSILON for x in EXPECTED_U_VALUES), 'U1 value was incorrect')
        self.assertTrue(any(u2 - abs(x) < EPSILON for x in EXPECTED_U_VALUES), 'U2 value was incorrect')
        self.assertTrue(abs(u - min(u1, u2)) < EPSILON, 'U should be the minimum of U1 and U2')

if __name__ == '__main__':
    unittest.main()
