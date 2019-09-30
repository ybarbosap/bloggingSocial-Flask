from flask import Blueprint

# o construtor aceita o nome do blueprint e o módulo ou pacote que ele estará
main = Blueprint('main', __name__)

# Imortação circular: views e erros importarão o obejto blueprint main, a menos que referência circular ocorra a importação falhará 
# a sintaxe '. import' é uma importação relativa que representa o modulo/pacote atual 
from . import forms, views