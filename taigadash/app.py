SQL_ISSUES = '''
select p.id, s.name, i.subject, i.created_date, i.modified_date from issues_issue i 
inner join projects_project p on p.id = i.project_id
inner join projects_taskstatus s on s.id = i.status_id
limit 10;
'''


