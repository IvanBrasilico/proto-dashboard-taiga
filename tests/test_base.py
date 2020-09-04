import unittest
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine

from taigadash.db import create_test_base, SQL_ISSUES

RESULT = {'id': {0: 1, 1: 1, 2: 2},
          'projeto': {0: 'Teste1', 1: 'Teste1', 2: 'Teste2'},
          'status': {0: 'In Progress', 1: 'Ready for Test', 2: 'In Progress'},
          'descricao': {0: 'Teste base de teste (p1 s1)',
                        1: 'Teste base de teste (p1 s2)',
                        2: 'Teste base de teste (p2 s1)'},
          'modified_date': {0: None, 1: None, 2: None}}

RESULT_JSON = ''.join([
    '{"id":{"0":1,"1":1,"2":2},',
    '"projeto":{"0":"Teste1","1":"Teste1","2":"Teste2"},',
    '"status":{"0":"In Progress","1":"Ready for Test","2":"In Progress"},',
    '"descricao":{"0":"Teste base de teste (p1 s1)","1":"Teste base de teste (p1 s2)",',
    '"2":"Teste base de teste (p2 s1)"},',
    '"modified_date":{"0":null,"1":null,"2":null}}'
])


class ModelTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.engine = create_engine('sqlite://')
        create_test_base(self.engine)
        hoje = datetime.strftime(datetime.today(), '%Y-%m-%d')
        amanha = datetime.strftime(datetime.today() + timedelta(days=1), '%Y-%m-%d')
        self.sql = SQL_ISSUES.format(hoje, amanha)

    def test_taigasqlissues_dict(self):
        df = pd.read_sql(self.sql, con=self.engine)
        df = df.drop(columns=['created_date'])
        assert df.to_dict() == RESULT

    def test_taigasqlissues_json(self):
        df = pd.read_sql(self.sql, con=self.engine)
        df = df.drop(columns=['created_date'])
        print(RESULT_JSON)
        assert df.to_json() == RESULT_JSON
