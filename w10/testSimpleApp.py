import unittest
import sys
from simpleApp import create_app

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = create_app()
        app.config.update({ "TESTING": True })
        cls._client = app.test_client()

    def test_ssp(self):
        response = self._client.get("/ssp")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Secure Software Process", response.data.decode())

    def test_vanity(self):
        response = self._client.get("/vanity")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Brandon Buckley", response.data.decode())

    def test_mypython(self):
        response = self._client.get("/mypython")
        self.assertEqual(200, response.status_code)
        self.assertEqual(sys.version, response.data.decode())

    def test_csse(self):
        response = self._client.get("/csse")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Department of Computer Science and Software Engineering", response.data.decode())
