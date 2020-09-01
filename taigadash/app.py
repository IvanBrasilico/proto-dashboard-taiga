import os
import sqlite3

import pandas as pd
import psycopg2
from flask import Flask, request, render_template

from taigadash.forms.filtro_form import FiltroForm

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


def filter_df(status):
    filtered_df = df.copy()
    if status:
        filtered_df = filtered_df[filtered_df['name'] == status]


@app.route('/')
@app.route('/taigadash/')
def home():
    status = request.args.get('status')
    filtered_df = filter_df(status)
    return filtered_df.to_html()


@app.route('/')
@app.route('/taigadash/html')
def html():
    status = request.args.get('status')
    oform = FiltroForm()
    filtered_df = filter_df(status)

    return render_template('home.html',
                           oform=oform,
                           dados=filtered_df.to_dict())


@app.route('/taigadash/json')
def json():
    status = request.json.get('status')
    filtered_df = filter_df(status)
    return filtered_df.to_json()


if __name__ == '__main__':
    app.run(port=5010)
