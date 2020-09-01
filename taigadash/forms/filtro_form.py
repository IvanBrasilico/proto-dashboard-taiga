from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.html5 import DateField


class FiltroForm(FlaskForm):
    status = StringField(u'Status da Tarefa',
                             default='')
    datainicio = DateField(u'Data inicial da pesquisa')
    datafim = DateField(u'Data final da pesquisa')
