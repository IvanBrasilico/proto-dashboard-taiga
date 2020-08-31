import pandas as pd
import psycopg2
from flask import Flask, request, render_template

from taigadash.forms.filtro_form import FiltroForm

SQL_ISSUES = '''
select p.id, s.name, i.subject, i.created_date, i.modified_date from issues_issue i 
inner join projects_project p on p.id = i.project_id
inner join projects_taskstatus s on s.id = i.status_id;
'''

con = psycopg2.connect(database='taiga', user='taiga_consulta')
df = pd.read_sql(SQL_ISSUES, con=con)
# con.close()
print(df.head())

app = Flask(__name__)


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
