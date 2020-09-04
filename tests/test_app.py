import unittest

import pandas as pd
from sqlalchemy import create_engine

from taigadash.app import create_app
from taigadash.db import create_test_base, SQL_ISSUES
from test_base import RESULT_JSON


class AppTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.engine = create_engine('sqlite://')
        create_test_base(self.engine)
        # df = pd.read_sql(SQL_ISSUES, con=self.engine)
        app = create_app(self.engine)
        self.app = app.test_client()

    def test_taigadash_json(self):
        rv = self.app.get('/taigadash/json', json={'relatorio': 1})
        print(rv.data)
        assert rv.status_code == 200
        assert rv.json == RESULT_JSON
