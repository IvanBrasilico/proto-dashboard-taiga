import os
import sqlite3

import pandas as pd
import psycopg2
from flask import Flask, request, render_template, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect

from taigadash.db import SQL_ISSUES
from taigadash.forms.filtro_form import FiltroForm

if os.environ.get('PRODUCTION'):
    con = psycopg2.connect(database='taiga', user='taiga_consulta')
else:
    con = sqlite3.connect('testes.db')
df = pd.read_sql(SQL_ISSUES, con=con)
# con.close()
print(df.head())
print(df.to_dict())


def filter_df(df, status):
    filtered_df = df.copy()
    if status:
        filtered_df = filtered_df[filtered_df['name'] == status]
    return filtered_df


def create_app(df):
    app = Flask(__name__)
    csrf = CSRFProtect(app)
    Bootstrap(app)
    app.config['df'] = df
    app.config['SECRET_KEY'] = os.urandom(32)

    @app.route('/')
    @app.route('/taigadash/')
    def home():
        df = app.config['df']
        status = request.args.get('status')
        filtered_df = filter_df(df, status)
        return filtered_df.to_html()

    @app.route('/')
    @app.route('/taigadash/html', methods=['POST', 'GET'])
    def html():
        df = app.config['df']
        status = None
        oform = FiltroForm()
        if request.method == 'POST':
            print(request.form)
            oform = FiltroForm(request.form)
            oform.validate()
            status = oform.status.data
        filtered_df = filter_df(df, status)
        print(status)
        colunas = list(df.columns)[1:]
        linhas = [list(row) for row in filtered_df.values]
        return render_template('home.html',
                               oform=oform,
                               colunas=colunas,
                               linhas=linhas)

    @app.route('/taigadash/json')
    def json():
        df = app.config['df']
        if request.json:
            status = request.json.get('status')
        else:
            status = None
        filtered_df = filter_df(df, status)
        return jsonify(filtered_df.to_json()), 200

    return app


app = create_app(df)

if __name__ == '__main__':  # pragma: no cover
    app.run(port=5010, debug=True)
