from flask import Blueprint

# o construtor aceita o nome do blueprint e o módulo ou pacote que ele estará
main = Blueprint('main', __name__)

# Imortação circular: views e erros importarão o obejto blueprint main, a menos que referência circular ocorra a importação falhará 
# a sintaxe '. import' é uma importação relativa que representa o modulo/pacote atual 
from . import forms, views
from ..import models

# Processadores de contexto deixam variáveis disponíveis a todos os templates durante a renderização
from ..models import Permission
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

