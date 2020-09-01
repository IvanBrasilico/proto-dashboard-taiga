from sqlalchemy import BigInteger, Column, VARCHAR, Integer, Date
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQL_ISSUES = '''
select p.id, s.name, i.subject, i.created_date, i.modified_date from issues_issue i 
inner join projects_project p on p.id = i.project_id
inner join projects_taskstatus s on s.id = i.status_id
limit 1000;
'''

Base = declarative_base()


class Issue(Base):
    __tablename__ = 'issues_issue'
    id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                primary_key=True)
    subject = Column(VARCHAR(100), index=True)
    created_date = Column(Date, index=True)
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
    session.commit()


if __name__ == '__main__':
    import pandas as pd

    engine = create_engine('sqlite:///testes.db')
    create_test_base(engine)
    df = pd.read_sql(SQL_ISSUES, con=engine)
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
