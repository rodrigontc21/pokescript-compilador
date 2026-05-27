# =============================================================================
#  PokeScript - Analisador Lexico (Lexer)
#  Disciplina: Compiladores - AED Projeto Final
#  Autor: Rodrigo Vieira
# =============================================================================

from enum import Enum, auto


# ---------------------------------------------------------------------------
# Tipos de Token
# ---------------------------------------------------------------------------

class TipoToken(Enum):
    # Palavras reservadas
    POKEMON    = auto()
    FIM        = auto()
    BATALHA    = auto()
    VS         = auto()
    SE         = auto()
    ENTAO      = auto()
    SENAO      = auto()
    ENQUANTO   = auto()
    FACA       = auto()
    MOSTRAR    = auto()
    CAPTURAR   = auto()
    INTEIRO    = auto()
    TEXTO      = auto()
    E          = auto()
    OU         = auto()
    NAO        = auto()
    VERDADEIRO = auto()
    FALSO      = auto()
    # Literais e identificadores
    ID         = auto()
    NUM_INT    = auto()
    NUM_FLOAT  = auto()
    STRING     = auto()
    # Operadores
    ATRIB      = auto()   # =
    IGUAL      = auto()   # ==
    DIFER      = auto()   # !=
    MAIOR      = auto()   # >
    MENOR      = auto()   # <
    MAIOR_IG   = auto()   # >=
    MENOR_IG   = auto()   # <=
    SOMA       = auto()   # +
    SUB        = auto()   # -
    MULT       = auto()   # *
    DIV        = auto()   # /
    PONTO      = auto()   # .
    # Delimitadores
    ABRE_PAR   = auto()   # (
    FECHA_PAR  = auto()   # )
    # Especial
    EOF        = auto()


# Mapa de palavras reservadas
PALAVRAS_RESERVADAS = {
    'pokemon':    TipoToken.POKEMON,
    'fim':        TipoToken.FIM,
    'batalha':    TipoToken.BATALHA,
    'vs':         TipoToken.VS,
    'se':         TipoToken.SE,
    'entao':      TipoToken.ENTAO,
    'senao':      TipoToken.SENAO,
    'enquanto':   TipoToken.ENQUANTO,
    'faca':       TipoToken.FACA,
    'mostrar':    TipoToken.MOSTRAR,
    'capturar':   TipoToken.CAPTURAR,
    'inteiro':    TipoToken.INTEIRO,
    'texto':      TipoToken.TEXTO,
    'e':          TipoToken.E,
    'ou':         TipoToken.OU,
    'nao':        TipoToken.NAO,
    'verdadeiro': TipoToken.VERDADEIRO,
    'falso':      TipoToken.FALSO,
}

# Operadores de um unico caractere
OP_SIMPLES = {
    '+': TipoToken.SOMA,
    '-': TipoToken.SUB,
    '*': TipoToken.MULT,
    '/': TipoToken.DIV,
    '.': TipoToken.PONTO,
    '(': TipoToken.ABRE_PAR,
    ')': TipoToken.FECHA_PAR,
}


# ---------------------------------------------------------------------------
# Classe Token
# ---------------------------------------------------------------------------

class Token:
    def __init__(self, tipo, valor, linha, coluna):
        self.tipo   = tipo
        self.valor  = valor
        self.linha  = linha
        self.coluna = coluna

    def __repr__(self):
        return (f'Token({self.tipo.name:<12} "{self.valor}"'
                f'  linha {self.linha}, col {self.coluna})')


# ---------------------------------------------------------------------------
# Classe ErroLexico
# ---------------------------------------------------------------------------

class ErroLexico:
    def __init__(self, mensagem, linha, coluna):
        self.mensagem = mensagem
        self.linha    = linha
        self.coluna   = coluna

    def __repr__(self):
        return (f'[ERRO LEXICO] Linha {self.linha}, '
                f'Coluna {self.coluna}: {self.mensagem}')


# ---------------------------------------------------------------------------
# Analisador Lexico
# ---------------------------------------------------------------------------

class Lexer:
    """
    Scanner da linguagem PokeScript.
    Percorre o codigo-fonte caractere a caractere, agrupa sequencias
    em tokens e reporta erros lexicos sem interromper a analise.
    """

    def __init__(self, fonte: str):
        self.fonte  = fonte
        self.pos    = 0
        self.linha  = 1
        self.coluna = 1
        self.tokens : list[Token]     = []
        self.erros  : list[ErroLexico] = []

    # ------------------------------------------------------------------ util

    def _atual(self):
        """Retorna o caractere atual sem consumir."""
        return self.fonte[self.pos] if self.pos < len(self.fonte) else None

    def _proximo(self, offset=1):
        """Espia o caractere seguinte sem consumir."""
        idx = self.pos + offset
        return self.fonte[idx] if idx < len(self.fonte) else None

    def _avancar(self):
        """Consome e retorna o caractere atual, atualizando linha/coluna."""
        ch = self.fonte[self.pos]
        self.pos += 1
        if ch == '\n':
            self.linha  += 1
            self.coluna  = 1
        else:
            self.coluna += 1
        return ch

    # ---------------------------------------------------------------- lexemas

    def _pular_espacos(self):
        while self._atual() in (' ', '\t', '\r', '\n'):
            self._avancar()

    def _pular_comentario(self):
        """Descarta tudo apos '#' ate o fim da linha."""
        while self._atual() and self._atual() != '\n':
            self._avancar()

    def _ler_string(self, linha, coluna):
        self._avancar()          # consome a aspas de abertura "
        valor = ''
        while self._atual() and self._atual() not in ('"', '\n'):
            valor += self._avancar()

        if self._atual() == '"':
            self._avancar()      # consome a aspas de fechamento "
            return Token(TipoToken.STRING, valor, linha, coluna)

        # String nao fechada = erro lexico (recupera e continua)
        self.erros.append(ErroLexico(
            f'string nao fechada — falta \'"\' de fechamento',
            linha, coluna
        ))
        return None

    def _ler_numero(self, linha, coluna):
        valor = ''
        while self._atual() and self._atual().isdigit():
            valor += self._avancar()

        # Verifica ponto flutuante
        if self._atual() == '.' and self._proximo() and self._proximo().isdigit():
            valor += self._avancar()   # consome '.'
            while self._atual() and self._atual().isdigit():
                valor += self._avancar()
            return Token(TipoToken.NUM_FLOAT, valor, linha, coluna)

        return Token(TipoToken.NUM_INT, valor, linha, coluna)

    def _ler_identificador(self, linha, coluna):
        valor = ''
        while self._atual() and (self._atual().isalnum() or self._atual() == '_'):
            valor += self._avancar()
        tipo = PALAVRAS_RESERVADAS.get(valor, TipoToken.ID)
        return Token(tipo, valor, linha, coluna)

    # ---------------------------------------------------------------- main

    def tokenizar(self):
        """
        Executa a analise lexica completa.
        Retorna (lista_de_tokens, lista_de_erros).
        """
        while self._atual():
            self._pular_espacos()
            if not self._atual():
                break

            ch     = self._atual()
            linha  = self.linha
            coluna = self.coluna

            # Comentario
            if ch == '#':
                self._pular_comentario()
                continue

            # String literal
            if ch == '"':
                tok = self._ler_string(linha, coluna)
                if tok:
                    self.tokens.append(tok)
                continue

            # Numero
            if ch.isdigit():
                self.tokens.append(self._ler_numero(linha, coluna))
                continue

            # Identificador ou palavra reservada
            if ch.isalpha() or ch == '_':
                self.tokens.append(self._ler_identificador(linha, coluna))
                continue

            # Operadores de dois caracteres (verificar antes dos simples)
            dois = self._atual() + (self._proximo() or '')
            if dois == '==':
                self._avancar(); self._avancar()
                self.tokens.append(Token(TipoToken.IGUAL,    '==', linha, coluna))
                continue
            if dois == '!=':
                self._avancar(); self._avancar()
                self.tokens.append(Token(TipoToken.DIFER,    '!=', linha, coluna))
                continue
            if dois == '>=':
                self._avancar(); self._avancar()
                self.tokens.append(Token(TipoToken.MAIOR_IG, '>=', linha, coluna))
                continue
            if dois == '<=':
                self._avancar(); self._avancar()
                self.tokens.append(Token(TipoToken.MENOR_IG, '<=', linha, coluna))
                continue

            # Operadores e delimitadores de um caractere
            if ch == '=':
                self._avancar()
                self.tokens.append(Token(TipoToken.ATRIB, '=', linha, coluna))
                continue
            if ch == '>':
                self._avancar()
                self.tokens.append(Token(TipoToken.MAIOR, '>', linha, coluna))
                continue
            if ch == '<':
                self._avancar()
                self.tokens.append(Token(TipoToken.MENOR, '<', linha, coluna))
                continue
            if ch in OP_SIMPLES:
                self._avancar()
                self.tokens.append(Token(OP_SIMPLES[ch], ch, linha, coluna))
                continue

            # Caractere desconhecido — erro lexico com recuperacao
            self.erros.append(ErroLexico(
                f"simbolo '{ch}' nao reconhecido",
                linha, coluna
            ))
            self._avancar()   # descarta o caractere e continua

        # Token de fim de arquivo
        self.tokens.append(Token(TipoToken.EOF, '', self.linha, self.coluna))
        return self.tokens, self.erros
