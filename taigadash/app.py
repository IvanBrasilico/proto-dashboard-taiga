import os
import sqlite3
from datetime import date

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


# con.close()


def filter_df(df, status):
    filtered_df = df.copy()
    if status:
        filtered_df = filtered_df[filtered_df['name'] == status]
    return filtered_df


def create_app(con):
    app = Flask(__name__)
    csrf = CSRFProtect(app)
    Bootstrap(app)
    df = pd.read_sql(SQL_ISSUES, con=con)
    app.config['df'] = df
    app.config['SECRET_KEY'] = os.urandom(32)


    @app.route('/')
    @app.route('/taigadash/', methods=['GET', 'POST'])
    def home():
        session = app.config.get('dbsession')
        lista_relatorios = get_relatorios_choice(session)
        linhas = []
        linhas_formatadas = []
        sql = ''
        plot = ''
        today = date.today()
        inicio = date(year=today.year, month=today.month, day=1)
        filtro_form = FiltroForm(
            datainicio=inicio,
            datafim=date.today(),
            relatorios=lista_relatorios,
        )
        try:
            if request.method == 'POST':
                filtro_form = FiltroForm(request.form,
                                                  relatorios=lista_relatorios)
                filtro_form.validate()
                relatorio = get_relatorio(session, int(filtro_form.relatorio.data))
                if relatorio is None:
                    raise ValueError('Relatório %s não encontrado' %
                                     filtro_form.relatorio.data)
                sql = relatorio.sql
                linhas = executa_relatorio(session, current_user.name,
                                           relatorio,
                                           filtro_form.datainicio.data,
                                           filtro_form.datafim.data,
                                           filtrar_setor=True)
                plot = bar_plotly(linhas, relatorio.nome)
                linhas_formatadas = formata_linhas_relatorio(linhas)
        except Exception as err:
            logger.error(err, exc_info=True)
            flash('Erro! Detalhes no log da aplicação.')
            flash(str(type(err)))
            flash(str(err))
        return render_template('relatorios.html',
                               oform=filtro_form,
                               linhas=linhas_formatadas,
                               sql=sql,
                               plot=plot)

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


if __name__ == '__main__':
    app = create_app(con)
    app.run(port=5010, debug=True)
