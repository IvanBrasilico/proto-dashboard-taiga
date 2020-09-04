import os
import pickle
import sqlite3
from datetime import date

import plotly
import plotly.graph_objs as go
import psycopg2
from flask import Flask, request, render_template, jsonify, current_app, flash
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect

from taigadash.db import get_relatorios_choice, executa_relatorio
from taigadash.forms.filtro_form import FiltroForm

if os.environ.get('PRODUCTION'):
    con = psycopg2.connect(database='taiga', user='taiga_consulta')
else:
    con = sqlite3.connect('testes.db', check_same_thread=False)


def filter_df(df, status: str, projeto: str):
    filtered_df = df.copy()
    if status and status != 'None':
        filtered_df = filtered_df[filtered_df['status'] == status]
    if projeto and projeto != 'None':
        filtered_df = filtered_df[filtered_df['projeto'] == projeto]
    return filtered_df


def get_secret():
    try:
        with open('SECRET', 'rb') as secret:
            try:
                SECRET = pickle.load(secret)
            except pickle.PickleError:
                SECRET = None
    except FileNotFoundError:
        SECRET = None

    if SECRET is None:
        SECRET = os.urandom(24)
        with open('SECRET', 'wb') as out:
            pickle.dump(SECRET, out, pickle.HIGHEST_PROTOCOL)
    return SECRET


def bar_plotly(df) -> str:
    """Renderiza gráfico no plotly e serializa via HTTP/HTML."""
    try:
        count_df = df[['status', 'id']].groupby(['status']).count()
        count_df = count_df.reset_index()
        # print(count_df.head())
        x = count_df['status'].tolist()
        y = count_df['id'].tolist()
        colors = count_df.index
        data = go.Bar(x=x, y=y, name='qtde', marker_color=colors)
        plot = plotly.offline.plot({
            'data': data,
            'layout': go.Layout(title='Qtde por status',
                                xaxis=go.layout.XAxis(type='category'))
        },
            show_link=False,
            output_type='div',
            image_width=400)
        return plot
    except Exception as err:
        print(err)
        # logger.error(str(err), exc_info=True)
        return ''


def create_app(con):
    app = Flask(__name__)
    csrf = CSRFProtect(app)
    Bootstrap(app)
    app.config['con'] = con
    app.config['SECRET_KEY'] = get_secret()

    @app.route('/', methods=['POST', 'GET'])
    @app.route('/taigadash/', methods=['POST', 'GET'])
    def home():
        con = app.config['con']
        lista_relatorios = get_relatorios_choice()
        colunas = []
        linhas = []
        linhas_formatadas = []
        sql = ''
        plot = ''
        relatorio_id = 0
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
                try:
                    relatorio_id = int(filtro_form.relatorio.data)
                except ValueError:
                    raise ValueError('Informar o tipo de relatorio')
                df, sql = executa_relatorio(con, relatorio_id,
                                            filtro_form.datainicio.data,
                                            filtro_form.datafim.data)
                projetos_choice = [(nome, nome) for nome in df['projeto'].unique()]
                status_choice = [(nome, nome) for nome in df['status'].unique()]
                filtro_form = FiltroForm(request.form,
                                         projetos=projetos_choice,
                                         status=status_choice,
                                         relatorios=lista_relatorios)
                plot = bar_plotly(df)
                filtered_df = filter_df(df,
                                        filtro_form.status.data,
                                        filtro_form.projeto.data)

                colunas = list(df.columns)[1:]
                linhas = [list(row) for row in filtered_df.values]
                # linhas_formatadas = formata_linhas_relatorio(linhas)
        except Exception as err:
            current_app.logger.error(err, exc_info=True)
            flash('Erro! Detalhes no log da aplicação.')
            flash(str(type(err)))
            flash(str(err))
        return render_template('home.html',
                               oform=filtro_form,
                               colunas=colunas,
                               linhas=linhas,
                               sql=sql,
                               plot=plot)

    @app.route('/taigadash/json', methods=['POST'])
    @csrf.exempt
    def json():
        con = app.config['con']
        try:
            filtro_form = FiltroForm(**dict(request.json))
            filtro_form.validate()
            try:
                relatorio_id = int(filtro_form.relatorio.data)
            except ValueError:
                raise ValueError('Informar o tipo de relatorio')
            df, sql = executa_relatorio(con, relatorio_id,
                                        filtro_form.datainicio.data,
                                        filtro_form.datafim.data)
            filtered_df = filter_df(df, filtro_form.status.data,
                                    filtro_form.projeto.data)
            return jsonify(filtered_df.to_json()), 200
        except Exception as err:
            raise err
            return jsonify({'msg': str(err)}), 500

    return app


app = create_app(con)

if __name__ == '__main__':  # pragma: no cover
    app.run(port=5010, debug=True, threaded=False)
