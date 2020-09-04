from datetime import datetime, timedelta
from typing import List, Tuple

import pandas as pd
from sqlalchemy import BigInteger, Column, VARCHAR, Integer, Date, Text, func, TIMESTAMP
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQL_ISSUES = '''
select p.id, p.name as projeto, s.name as status, i.subject as descricao,
 i.created_date, i.modified_date from issues_issue i 
inner join projects_project p on p.id = i.project_id
inner join projects_taskstatus s on s.id = i.status_id
WHERE i.created_date between '{}' and '{}'
limit 1000;
'''
TASK_ISSUES = '''
select p.id, p.name as projeto, s.name as status, t.subject as descricao,
 t.created_date, t.modified_date from tasks_task t 
inner join projects_project p on p.id = t.project_id
inner join projects_taskstatus s on s.id = t.status_id
WHERE t.created_date between '{}' and '{}'
limit 1000;
'''

relatorios = (
    (1, 'Issues', SQL_ISSUES),
    (2, 'Tarefas', TASK_ISSUES)
)

Base = declarative_base()


class Issue(Base):
    __tablename__ = 'issues_issue'
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    subject = Column(VARCHAR(100), index=True)
    created_date = Column(TIMESTAMP, index=True,
                          server_default=func.current_timestamp())
    modified_date = Column(Date, index=True)
    project_id = Column(BigInteger().with_variant(Integer, 'sqlite'))
    status_id = Column(BigInteger().with_variant(Integer, 'sqlite'))


class Task(Base):
    __tablename__ = 'tasks_task'
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    subject = Column(VARCHAR(100), index=True)
    created_date = Column(TIMESTAMP, index=True,
                          server_default=func.current_timestamp())
    modified_date = Column(Date, index=True)
    project_id = Column(BigInteger().with_variant(Integer, 'sqlite'))
    status_id = Column(BigInteger().with_variant(Integer, 'sqlite'))


class Project(Base):
    __tablename__ = 'projects_project'
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    name = Column(VARCHAR(100), index=True)


class TaskStatus(Base):
    __tablename__ = 'projects_taskstatus'
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    name = Column(VARCHAR(100), index=True)


class Relatorio(Base):
    __tablename__ = 'taiga_relatorios'
    id = Column(BigInteger().with_variant(Integer, 'sqlite'), primary_key=True)
    nome = Column(VARCHAR(200), index=True, nullable=False)
    sql = Column(Text())


def get_relatorios_choice() -> List[Tuple[int, str]]:
    return [(relatorio[0], relatorio[1]) for relatorio in relatorios]


def get_sql_relatorio(relatorio_id: int) -> str:
    for relatorio in relatorios:
        if relatorio[0] == relatorio_id:
            return relatorio[2]
    return ''


def executa_relatorio(con, relatorio_id: int,
                      data_inicial: datetime, data_final: datetime):
    sql = get_sql_relatorio(relatorio_id)
    if not sql:
        raise ValueError('Relatório %s não encontrado' % relatorio_id)
    if not data_inicial:
        data_inicial = datetime.today() - timedelta(days=1)
    inicio = datetime.strftime(data_inicial, '%Y-%m-%d')
    if not data_final:
        data_final = datetime.today()
    fim = datetime.strftime(data_final + timedelta(days=1), '%Y-%m-%d')
    sql = sql.format(inicio, fim)
    df = pd.read_sql(sql, con)
    return df, sql


def create_test_base(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    project = Project()
    project.name = 'Teste1'
    session.add(project)
    project2 = Project()
    project2.name = 'Teste2'
    session.add(project2)
    status = TaskStatus()
    status.name = 'In Progress'
    session.add(status)
    status2 = TaskStatus()
    status2.name = 'Ready for Test'
    session.add(status2)
    session.commit()
    session.refresh(project)
    session.refresh(project2)
    session.refresh(status)
    session.refresh(status2)
    issue = Issue()
    issue.subject = 'Teste base de teste (p1 s1)'
    issue.project_id = project.id
    issue.status_id = status.id
    session.add(issue)
    issue2 = Issue()
    issue2.subject = 'Teste base de teste (p1 s2)'
    issue2.project_id = project.id
    issue2.status_id = status2.id
    session.add(issue2)
    issue3 = Issue()
    issue3.subject = 'Teste base de teste (p2 s1)'
    issue3.project_id = project2.id
    issue3.status_id = status.id
    session.add(issue3)
    task = Task()
    task.subject = 'Teste tarefa base de teste (p1 s1)'
    task.project_id = project.id
    task.status_id = status.id
    session.add(task)
    task2 = Task()
    task2.subject = 'Teste tarefa base de teste (p2 s2)'
    task2.project_id = project2.id
    task2.status_id = status2.id
    session.add(task2)
    task3 = Task()
    task3.subject = 'Teste tarefa base de teste (p2 s1)'
    task3.project_id = project2.id
    task3.status_id = status.id
    session.add(task3)
    session.commit()
    relatorio = Relatorio()
    relatorio.nome = 'Issues com Status e Projeto'
    relatorio.sql = SQL_ISSUES
    session.add(relatorio)
    relatorio = Relatorio()
    relatorio.nome = 'Tarefas com Status e Projeto'
    relatorio.sql = TASK_ISSUES
    session.add(relatorio)


if __name__ == '__main__':  # pragma: no cover

    engine = create_engine('sqlite:///testes.db')
    create_test_base(engine)
    hoje = datetime.strftime(datetime.today() - timedelta(days=1), '%Y-%m-%d')
    amanha = datetime.strftime(datetime.today() + timedelta(days=1), '%Y-%m-%d')
    df = pd.read_sql(SQL_ISSUES.format(hoje, amanha), con=engine)
    print(df.head())
    print(df.to_dict())
    print(df.to_json())
    print(list(df.columns))
    print([list(row) for row in df.values])
    """
    {'id': {0: 1, 1: 1, 2: 2}, 'name': {0: 'In Progress', 1: 'Ready for Test', 2: 'In Progress'},
     'subject': {0: 'Teste base de teste (p1 s1)', 1: 'Teste base de teste (p1 s2)', 2: 'Teste base de teste (p2 s1)'},
     'created_date': {0: None, 1: None, 2: None}, 'modified_date': {0: None, 1: None, 2: None}}
    """
