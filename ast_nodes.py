# =============================================================================
#  PokeScript - Nos da Arvore Sintatica Abstrata (AST)
#  Disciplina: Compiladores - AED Projeto Final
#  Autor: Rodrigo Vieira
# =============================================================================


# ---------------------------------------------------------------------------
# Nos de Declaracao
# ---------------------------------------------------------------------------

class NodoPrograma:
    def __init__(self, declaracoes):
        self.declaracoes = declaracoes

class NodoPokemon:
    def __init__(self, nome, atributos, linha):
        self.nome = nome
        self.atributos = atributos
        self.linha = linha

class NodoAtribPokemon:
    def __init__(self, nome, valor, linha):
        self.nome = nome
        self.valor = valor
        self.linha = linha

class NodoBatalha:
    def __init__(self, nome1, nome2, corpo, linha):
        self.nome1 = nome1
        self.nome2 = nome2
        self.corpo = corpo
        self.linha = linha


# ---------------------------------------------------------------------------
# Nos de Comando
# ---------------------------------------------------------------------------

class NodoDeclVar:
    def __init__(self, tipo, nome, valor, linha):
        self.tipo  = tipo   # 'inteiro' ou 'texto'
        self.nome  = nome
        self.valor = valor
        self.linha = linha

class NodoAtrib:
    def __init__(self, alvo, valor, linha):
        self.alvo  = alvo   # NodoIdentificador ou NodoAcesso
        self.valor = valor
        self.linha = linha

class NodoMostrar:
    def __init__(self, expressao, linha):
        self.expressao = expressao
        self.linha     = linha

class NodoCapturar:
    def __init__(self, variavel, linha):
        self.variavel = variavel
        self.linha    = linha

class NodoSe:
    def __init__(self, condicao, corpo_entao, corpo_senao, linha):
        self.condicao    = condicao
        self.corpo_entao = corpo_entao
        self.corpo_senao = corpo_senao
        self.linha       = linha

class NodoEnquanto:
    def __init__(self, condicao, corpo, linha):
        self.condicao = condicao
        self.corpo    = corpo
        self.linha    = linha


# ---------------------------------------------------------------------------
# Nos de Expressao
# ---------------------------------------------------------------------------

class NodoBinario:
    def __init__(self, operador, esquerda, direita, linha):
        self.operador = operador
        self.esquerda = esquerda
        self.direita  = direita
        self.linha    = linha

class NodoUnario:
    def __init__(self, operador, operando, linha):
        self.operador = operador
        self.operando = operando
        self.linha    = linha

class NodoNumero:
    def __init__(self, valor, linha):
        self.valor = valor
        self.linha = linha

class NodoString:
    def __init__(self, valor, linha):
        self.valor = valor
        self.linha = linha

class NodoBooleano:
    def __init__(self, valor, linha):
        self.valor = valor
        self.linha = linha

class NodoIdentificador:
    def __init__(self, nome, linha):
        self.nome  = nome
        self.linha = linha

class NodoAcesso:
    """Acesso a atributo de Pokemon: dragonite.hp"""
    def __init__(self, objeto, atributo, linha):
        self.objeto   = objeto
        self.atributo = atributo
        self.linha    = linha


# ---------------------------------------------------------------------------
# Impressao da AST (Pretty Printer)
# ---------------------------------------------------------------------------

class ImpressorAST:
    """
    Percorre a AST e a imprime de forma indentada no terminal,
    mostrando a estrutura hierarquica do programa.
    """

    def imprimir(self, nodo, indent=0):
        p = "  " * indent
        t = "  " * (indent + 1)

        if isinstance(nodo, NodoPrograma):
            print(f"{p}Programa")
            for d in nodo.declaracoes:
                self.imprimir(d, indent + 1)

        elif isinstance(nodo, NodoPokemon):
            print(f"{p}Pokemon: {nodo.nome}  (linha {nodo.linha})")
            for a in nodo.atributos:
                self.imprimir(a, indent + 1)

        elif isinstance(nodo, NodoAtribPokemon):
            print(f"{p}Atributo: {nodo.nome} =")
            self.imprimir(nodo.valor, indent + 2)

        elif isinstance(nodo, NodoBatalha):
            print(f"{p}Batalha: {nodo.nome1} vs {nodo.nome2}  (linha {nodo.linha})")
            for c in nodo.corpo:
                self.imprimir(c, indent + 1)

        elif isinstance(nodo, NodoDeclVar):
            print(f"{p}DeclVar [{nodo.tipo}]: {nodo.nome} =  (linha {nodo.linha})")
            self.imprimir(nodo.valor, indent + 2)

        elif isinstance(nodo, NodoAtrib):
            print(f"{p}Atrib:  (linha {nodo.linha})")
            self.imprimir(nodo.alvo,  indent + 1)
            self.imprimir(nodo.valor, indent + 1)

        elif isinstance(nodo, NodoMostrar):
            print(f"{p}Mostrar:  (linha {nodo.linha})")
            self.imprimir(nodo.expressao, indent + 1)

        elif isinstance(nodo, NodoCapturar):
            print(f"{p}Capturar: {nodo.variavel}  (linha {nodo.linha})")

        elif isinstance(nodo, NodoSe):
            print(f"{p}Se:  (linha {nodo.linha})")
            print(f"{t}Condicao:")
            self.imprimir(nodo.condicao, indent + 2)
            print(f"{t}Entao:")
            for c in nodo.corpo_entao:
                self.imprimir(c, indent + 2)
            if nodo.corpo_senao:
                print(f"{t}Senao:")
                for c in nodo.corpo_senao:
                    self.imprimir(c, indent + 2)

        elif isinstance(nodo, NodoEnquanto):
            print(f"{p}Enquanto:  (linha {nodo.linha})")
            print(f"{t}Condicao:")
            self.imprimir(nodo.condicao, indent + 2)
            print(f"{t}Corpo:")
            for c in nodo.corpo:
                self.imprimir(c, indent + 2)

        elif isinstance(nodo, NodoBinario):
            print(f"{p}BinOp: '{nodo.operador}'")
            self.imprimir(nodo.esquerda, indent + 1)
            self.imprimir(nodo.direita,  indent + 1)

        elif isinstance(nodo, NodoUnario):
            print(f"{p}UnOp: '{nodo.operador}'")
            self.imprimir(nodo.operando, indent + 1)

        elif isinstance(nodo, NodoNumero):
            print(f"{p}Numero: {nodo.valor}")

        elif isinstance(nodo, NodoString):
            print(f'{p}String: "{nodo.valor}"')

        elif isinstance(nodo, NodoBooleano):
            print(f"{p}Booleano: {nodo.valor}")

        elif isinstance(nodo, NodoIdentificador):
            print(f"{p}ID: {nodo.nome}")

        elif isinstance(nodo, NodoAcesso):
            print(f"{p}Acesso: {nodo.objeto}.{nodo.atributo}")

        else:
            print(f"{p}[no desconhecido: {type(nodo).__name__}]")
