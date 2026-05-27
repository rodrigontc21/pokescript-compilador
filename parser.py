# =============================================================================
#  PokeScript - Analisador Sintatico (Parser LL(1) Descendente Recursivo)
#  Disciplina: Compiladores - AED Projeto Final
#  Autor: Rodrigo Vieira
# =============================================================================
#
#  Gramatica BNF (resumo):
#
#  programa       -> declaracao* EOF
#  declaracao     -> decl_pokemon | decl_batalha | comando
#
#  decl_pokemon   -> POKEMON ID atrib_pokemon* FIM
#  atrib_pokemon  -> ID ATRIB expressao
#
#  decl_batalha   -> BATALHA ID VS ID FACA bloco FIM
#
#  bloco          -> comando*
#  comando        -> cmd_mostrar | cmd_capturar | cmd_se
#                  | cmd_enquanto | cmd_decl_var | cmd_id
#
#  cmd_mostrar    -> MOSTRAR expressao
#  cmd_capturar   -> CAPTURAR ID
#  cmd_se         -> SE expressao ENTAO bloco (SENAO bloco)? FIM
#  cmd_enquanto   -> ENQUANTO expressao FACA bloco FIM
#  cmd_decl_var   -> (INTEIRO | TEXTO) ID ATRIB expressao
#  cmd_id         -> ID (ATRIB expressao | PONTO ID ATRIB expressao)
#
#  expressao      -> expr_ou
#  expr_ou        -> expr_e (OU expr_e)*
#  expr_e         -> expr_nao (E expr_nao)*
#  expr_nao       -> NAO expr_nao | expr_comp
#  expr_comp      -> expr_soma ((== | != | > | < | >= | <=) expr_soma)?
#  expr_soma      -> expr_mult ((+ | -) expr_mult)*
#  expr_mult      -> expr_unario ((* | /) expr_unario)*
#  expr_unario    -> - expr_unario | fator
#  fator          -> NUM_INT | NUM_FLOAT | STRING | VERDADEIRO | FALSO
#                  | ( expressao ) | ID | ID . ID
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from lexer      import Token, TipoToken
from ast_nodes  import (
    NodoPrograma, NodoPokemon, NodoAtribPokemon, NodoBatalha,
    NodoDeclVar, NodoAtrib, NodoMostrar, NodoCapturar,
    NodoSe, NodoEnquanto,
    NodoBinario, NodoUnario, NodoNumero, NodoString,
    NodoBooleano, NodoIdentificador, NodoAcesso,
)


# ---------------------------------------------------------------------------
# Erro Sintatico
# ---------------------------------------------------------------------------

class ErroSintatico:
    def __init__(self, mensagem: str, linha: int, coluna: int):
        self.mensagem = mensagem
        self.linha    = linha
        self.coluna   = coluna

    def __repr__(self):
        return (f"[ERRO SINTATICO] Linha {self.linha}, "
                f"Coluna {self.coluna}: {self.mensagem}")


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    """
    Parser descendente recursivo LL(1) para PokeScript.

    Consome a lista de tokens produzida pelo Lexer e constroi a AST.
    Erros sintaticos sao registrados sem interromper a analise (recuperacao
    por sincronizacao no inicio de bloco / fim de bloco).
    """

    # tokens que podem iniciar um comando
    _INICIO_COMANDO = {
        TipoToken.MOSTRAR, TipoToken.CAPTURAR,
        TipoToken.SE, TipoToken.ENQUANTO,
        TipoToken.INTEIRO, TipoToken.TEXTO,
        TipoToken.ID,
    }

    # tokens que sinalizam fim de bloco
    _FIM_BLOCO = {TipoToken.FIM, TipoToken.SENAO, TipoToken.EOF}

    # operadores de comparacao
    _OPS_COMP = {
        TipoToken.IGUAL, TipoToken.DIFER,
        TipoToken.MAIOR, TipoToken.MENOR,
        TipoToken.MAIOR_IG, TipoToken.MENOR_IG,
    }

    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos    = 0
        self.erros: list = []

    # ---------------------------------------------------------------- helpers

    def _atual(self) -> Token:
        return self.tokens[self.pos]

    def _avancar(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.tipo != TipoToken.EOF:
            self.pos += 1
        return tok

    def _checar(self, *tipos) -> bool:
        return self._atual().tipo in tipos

    def _consumir(self, tipo: TipoToken) -> Token:
        tok = self._atual()
        if tok.tipo == tipo:
            return self._avancar()
        self.erros.append(ErroSintatico(
            f"esperado '{tipo.name}', encontrado '{tok.valor}' ({tok.tipo.name})",
            tok.linha, tok.coluna
        ))
        return tok   # retorna o token atual sem avancar (recuperacao)

    # ---------------------------------------------------------------- ponto de entrada

    def parsear(self):
        """Analisa o programa completo e retorna (NodoPrograma, lista_de_erros)."""
        prog = self._programa()
        return prog, self.erros

    # programa -> declaracao* EOF
    def _programa(self):
        decls = []
        while not self._checar(TipoToken.EOF):
            # Pula tokens desconhecidos no nivel superior
            if not (self._checar(TipoToken.POKEMON, TipoToken.BATALHA) or
                    self._checar(*self._INICIO_COMANDO)):
                tok = self._atual()
                self.erros.append(ErroSintatico(
                    f"declaracao invalida: '{tok.valor}' ({tok.tipo.name})",
                    tok.linha, tok.coluna
                ))
                self._avancar()
                continue
            d = self._declaracao()
            if d:
                decls.append(d)
        return NodoPrograma(decls)

    # declaracao -> decl_pokemon | decl_batalha | comando
    def _declaracao(self):
        if self._checar(TipoToken.POKEMON):
            return self._decl_pokemon()
        if self._checar(TipoToken.BATALHA):
            return self._decl_batalha()
        return self._comando()

    # decl_pokemon -> POKEMON ID atrib_pokemon* FIM
    def _decl_pokemon(self):
        tok  = self._consumir(TipoToken.POKEMON)
        nome = self._consumir(TipoToken.ID)
        attrs = []
        while self._checar(TipoToken.ID):
            attrs.append(self._atrib_pokemon())
        self._consumir(TipoToken.FIM)
        return NodoPokemon(nome.valor, attrs, tok.linha)

    # atrib_pokemon -> ID ATRIB expressao
    def _atrib_pokemon(self):
        nome = self._consumir(TipoToken.ID)
        self._consumir(TipoToken.ATRIB)
        val  = self._expressao()
        return NodoAtribPokemon(nome.valor, val, nome.linha)

    # decl_batalha -> BATALHA ID VS ID FACA bloco FIM
    def _decl_batalha(self):
        tok   = self._consumir(TipoToken.BATALHA)
        nome1 = self._consumir(TipoToken.ID)
        self._consumir(TipoToken.VS)
        nome2 = self._consumir(TipoToken.ID)
        self._consumir(TipoToken.FACA)
        corpo = self._bloco()
        self._consumir(TipoToken.FIM)
        return NodoBatalha(nome1.valor, nome2.valor, corpo, tok.linha)

    # bloco -> comando*
    def _bloco(self):
        cmds = []
        while self._atual().tipo not in self._FIM_BLOCO:
            cmd = self._comando()
            if cmd:
                cmds.append(cmd)
        return cmds

    # comando -> um dos varios tipos de comando
    def _comando(self):
        tok = self._atual()

        if self._checar(TipoToken.MOSTRAR):
            return self._cmd_mostrar()

        if self._checar(TipoToken.CAPTURAR):
            return self._cmd_capturar()

        if self._checar(TipoToken.SE):
            return self._cmd_se()

        if self._checar(TipoToken.ENQUANTO):
            return self._cmd_enquanto()

        if self._checar(TipoToken.INTEIRO, TipoToken.TEXTO):
            return self._cmd_decl_var()

        if self._checar(TipoToken.ID):
            return self._cmd_id()

        # Erro: token nao esperado — recuperacao por avanco
        self.erros.append(ErroSintatico(
            f"comando invalido: '{tok.valor}' ({tok.tipo.name})",
            tok.linha, tok.coluna
        ))
        self._avancar()
        return None

    # cmd_mostrar -> MOSTRAR expressao
    def _cmd_mostrar(self):
        tok  = self._consumir(TipoToken.MOSTRAR)
        expr = self._expressao()
        return NodoMostrar(expr, tok.linha)

    # cmd_capturar -> CAPTURAR ID
    def _cmd_capturar(self):
        tok = self._consumir(TipoToken.CAPTURAR)
        var = self._consumir(TipoToken.ID)
        return NodoCapturar(var.valor, tok.linha)

    # cmd_se -> SE expressao ENTAO bloco (SENAO bloco)? FIM
    def _cmd_se(self):
        tok  = self._consumir(TipoToken.SE)
        cond = self._expressao()
        self._consumir(TipoToken.ENTAO)
        corpo_entao = self._bloco()
        corpo_senao = []
        if self._checar(TipoToken.SENAO):
            self._avancar()
            corpo_senao = self._bloco()
        self._consumir(TipoToken.FIM)
        return NodoSe(cond, corpo_entao, corpo_senao, tok.linha)

    # cmd_enquanto -> ENQUANTO expressao FACA bloco FIM
    def _cmd_enquanto(self):
        tok   = self._consumir(TipoToken.ENQUANTO)
        cond  = self._expressao()
        self._consumir(TipoToken.FACA)
        corpo = self._bloco()
        self._consumir(TipoToken.FIM)
        return NodoEnquanto(cond, corpo, tok.linha)

    # cmd_decl_var -> (INTEIRO | TEXTO) ID ATRIB expressao
    def _cmd_decl_var(self):
        tipo = self._avancar()
        nome = self._consumir(TipoToken.ID)
        self._consumir(TipoToken.ATRIB)
        val  = self._expressao()
        return NodoDeclVar(tipo.valor, nome.valor, val, tipo.linha)

    # cmd_id -> ID (ATRIB expressao | PONTO ID ATRIB expressao)
    def _cmd_id(self):
        id_tok = self._avancar()   # consome ID

        # Atribuicao de atributo: ID . ID = expr
        if self._checar(TipoToken.PONTO):
            self._avancar()
            attr = self._consumir(TipoToken.ID)
            self._consumir(TipoToken.ATRIB)
            val  = self._expressao()
            alvo = NodoAcesso(id_tok.valor, attr.valor, id_tok.linha)
            return NodoAtrib(alvo, val, id_tok.linha)

        # Atribuicao simples: ID = expr
        if self._checar(TipoToken.ATRIB):
            self._avancar()
            val  = self._expressao()
            alvo = NodoIdentificador(id_tok.valor, id_tok.linha)
            return NodoAtrib(alvo, val, id_tok.linha)

        # Erro
        tok = self._atual()
        self.erros.append(ErroSintatico(
            f"esperado '=' ou '.' apos identificador '{id_tok.valor}'",
            tok.linha, tok.coluna
        ))
        return None

    # ---------------------------------------------------------------- expressoes

    # expressao -> expr_ou
    def _expressao(self):
        return self._expr_ou()

    # expr_ou -> expr_e (OU expr_e)*
    def _expr_ou(self):
        esq = self._expr_e()
        while self._checar(TipoToken.OU):
            op  = self._avancar()
            dir = self._expr_e()
            esq = NodoBinario("ou", esq, dir, op.linha)
        return esq

    # expr_e -> expr_nao (E expr_nao)*
    def _expr_e(self):
        esq = self._expr_nao()
        while self._checar(TipoToken.E):
            op  = self._avancar()
            dir = self._expr_nao()
            esq = NodoBinario("e", esq, dir, op.linha)
        return esq

    # expr_nao -> NAO expr_nao | expr_comp
    def _expr_nao(self):
        if self._checar(TipoToken.NAO):
            op  = self._avancar()
            ope = self._expr_nao()
            return NodoUnario("nao", ope, op.linha)
        return self._expr_comp()

    # expr_comp -> expr_soma ((== | != | > | < | >= | <=) expr_soma)?
    def _expr_comp(self):
        esq = self._expr_soma()
        if self._atual().tipo in self._OPS_COMP:
            op  = self._avancar()
            dir = self._expr_soma()
            return NodoBinario(op.valor, esq, dir, op.linha)
        return esq

    # expr_soma -> expr_mult ((+ | -) expr_mult)*
    def _expr_soma(self):
        esq = self._expr_mult()
        while self._checar(TipoToken.SOMA, TipoToken.SUB):
            op  = self._avancar()
            dir = self._expr_mult()
            esq = NodoBinario(op.valor, esq, dir, op.linha)
        return esq

    # expr_mult -> expr_unario ((* | /) expr_unario)*
    def _expr_mult(self):
        esq = self._expr_unario()
        while self._checar(TipoToken.MULT, TipoToken.DIV):
            op  = self._avancar()
            dir = self._expr_unario()
            esq = NodoBinario(op.valor, esq, dir, op.linha)
        return esq

    # expr_unario -> - expr_unario | fator
    def _expr_unario(self):
        if self._checar(TipoToken.SUB):
            op  = self._avancar()
            ope = self._expr_unario()
            return NodoUnario("-", ope, op.linha)
        return self._fator()

    # fator -> NUM_INT | NUM_FLOAT | STRING | VERDADEIRO | FALSO
    #        | ( expressao ) | ID | ID . ID
    def _fator(self):
        tok = self._atual()

        if self._checar(TipoToken.NUM_INT):
            self._avancar()
            return NodoNumero(int(tok.valor), tok.linha)

        if self._checar(TipoToken.NUM_FLOAT):
            self._avancar()
            return NodoNumero(float(tok.valor), tok.linha)

        if self._checar(TipoToken.STRING):
            self._avancar()
            return NodoString(tok.valor, tok.linha)

        if self._checar(TipoToken.VERDADEIRO):
            self._avancar()
            return NodoBooleano(True, tok.linha)

        if self._checar(TipoToken.FALSO):
            self._avancar()
            return NodoBooleano(False, tok.linha)

        if self._checar(TipoToken.ABRE_PAR):
            self._consumir(TipoToken.ABRE_PAR)
            expr = self._expressao()
            self._consumir(TipoToken.FECHA_PAR)
            return expr

        if self._checar(TipoToken.ID):
            id_tok = self._avancar()
            if self._checar(TipoToken.PONTO):
                self._avancar()
                attr = self._consumir(TipoToken.ID)
                return NodoAcesso(id_tok.valor, attr.valor, id_tok.linha)
            return NodoIdentificador(id_tok.valor, id_tok.linha)

        # Erro: token nao inicia uma expressao valida
        self.erros.append(ErroSintatico(
            f"expressao invalida: '{tok.valor}' ({tok.tipo.name})",
            tok.linha, tok.coluna
        ))
        self._avancar()
        return NodoNumero(0, tok.linha)
