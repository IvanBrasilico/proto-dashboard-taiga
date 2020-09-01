import os
import sqlite3

import pandas as pd
import psycopg2
from flask import Flask

from taigadash.db import SQL_ISSUES

if os.environ.get('DB'):
    con = psycopg2.connect(database='taiga', user='taiga_consulta')
else:
    con = sqlite3.connect('testes.db')
df = pd.read_sql(SQL_ISSUES, con=con)
# con.close()
print(df.head())
print(df.to_dict())


def create_app(df):
    app = Flask(__name__)
    app.config['df'] = df


app = create_app(df)


@app.route('/')
@app.route('/taigadash/')
def home():
    return df.to_html()


@app.route('/taigadash/json')
def json():
    return df.to_json()


if __name__ == '__main__':
    app.run(port=5010)
