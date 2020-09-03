from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.fields.html5 import DateField


class FiltroForm(FlaskForm):
    status = StringField(u'Status da Tarefa',
                             default='')
    projeto = StringField(u'Nome do Projeto',
                             default='')
    datainicio = DateField(u'Data inicial da pesquisa')
    datafim = DateField(u'Data final da pesquisa')
    relatorio = SelectField('Relatórios disponiveis', default=-1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.relatorio.choices = [(None, 'Selecione')]
        if kwargs.get('relatorios'):
            self.relatorio.choices = [(None, 'Selecione'),
                                      *kwargs.get('relatorios')]
