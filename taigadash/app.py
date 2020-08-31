import pandas as pd
import psycopg2
from flask import Flask

SQL_ISSUES = '''
select p.id, s.name, i.subject, i.created_date, i.modified_date from issues_issue i 
inner join projects_project p on p.id = i.project_id
inner join projects_taskstatus s on s.id = i.status_id
limit 1000;
'''

con = psycopg2.connect(database='taiga', user='taiga_consulta')
df = pd.read_sql(SQL_ISSUES, con=con)
# con.close()
print(df.head())

app = Flask(__name__)


@app.route('/')
@app.route('/taigadash/')
def home():
    return df.to_html()


@app.route('/taigadash/json')
def json():
    return df.to_json()


if __name__ == '__main__':
    app.run(port=5010)
