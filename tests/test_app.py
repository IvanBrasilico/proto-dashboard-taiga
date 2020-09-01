import unittest
import pandas as pd
from flask import Flask

from sqlalchemy import create_engine

from taigadash.db import create_test_base, SQL_ISSUES
from testes.teste_base import RESULT, RESULT_JSON


class AppTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.engine = create_engine('sqlite:///testes.db')
        create_test_base(self.engine)
        df = pd.read_sql(SQL_ISSUES, con=self.engine)
        app = Flask(__name__)
        app.config['df'] = df
        self.app = app.test_client()

    def test_taigadash_json(self):
        rv = self.app.get('/taigadash/json')
        assert rv.status_code == 200
        assert rv.json == RESULT_JSON
