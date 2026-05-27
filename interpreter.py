# =============================================================================
#  PokeScript - Interpretador (Tree-Walker)
#  Disciplina: Compiladores - AED Projeto Final
#  Autor: Rodrigo Vieira
# =============================================================================

from ast_nodes import *


# ---------------------------------------------------------------------------
# Erro de Execucao
# ---------------------------------------------------------------------------

class ErroExecucao(Exception):
    def __init__(self, mensagem, linha=None):
        self.mensagem = mensagem
        self.linha    = linha
        super().__init__(mensagem)

    def __repr__(self):
        loc = f" (linha {self.linha})" if self.linha else ""
        return f"[ERRO EXECUCAO]{loc}: {self.mensagem}"


# ---------------------------------------------------------------------------
# Interpretador
# ---------------------------------------------------------------------------

class Interpretador:
    """
    Interpretador tree-walker para a linguagem PokeScript.

    Percorre a AST gerada pelo parser e executa cada no diretamente,
    mantendo um ambiente (tabela de simbolos) e um registro de Pokemon.
    """

    def __init__(self):
        self.ambiente: dict = {}   # variaveis: nome -> valor
        self.pokemons: dict = {}   # pokemon: nome -> {atrib: valor}
        self.erros:    list = []

    # ---------------------------------------------------------------- util

    def _truthy(self, val) -> bool:
        """Converte qualquer valor para booleano no estilo PokeScript."""
        if isinstance(val, bool):   return val
        if isinstance(val, (int, float)): return val != 0
        if isinstance(val, str):    return len(val) > 0
        return bool(val)

    def _para_texto(self, val) -> str:
        """Converte valor para representacao textual legivel."""
        if isinstance(val, bool):
            return "verdadeiro" if val else "falso"
        if isinstance(val, float) and val == int(val):
            return str(int(val))
        if isinstance(val, dict):
            # Pokemon como valor
            pares = ", ".join(f"{k}: {self._para_texto(v)}" for k, v in val.items())
            return f"{{ {pares} }}"
        return str(val)

    def _obter_var(self, nome, linha=None):
        if nome in self.ambiente:
            return self.ambiente[nome]
        if nome in self.pokemons:
            return self.pokemons[nome]
        raise ErroExecucao(f"variavel '{nome}' nao foi declarada", linha)

    # ---------------------------------------------------------------- execucao

    def executar(self, programa: NodoPrograma):
        """Ponto de entrada: executa o programa completo."""
        for decl in programa.declaracoes:
            self._exec(decl)

    def _exec(self, nodo):
        """Despacha a execucao para o metodo correto pelo tipo do no."""
        metodo = {
            NodoPokemon:     self._exec_pokemon,
            NodoBatalha:     self._exec_batalha,
            NodoDeclVar:     self._exec_decl_var,
            NodoAtrib:       self._exec_atrib,
            NodoMostrar:     self._exec_mostrar,
            NodoCapturar:    self._exec_capturar,
            NodoSe:          self._exec_se,
            NodoEnquanto:    self._exec_enquanto,
        }.get(type(nodo))

        if metodo:
            metodo(nodo)
        elif nodo is not None:
            raise ErroExecucao(f"no desconhecido: {type(nodo).__name__}")

    # ---- declaracoes

    def _exec_pokemon(self, nodo: NodoPokemon):
        """Registra um Pokemon e seus atributos no ambiente."""
        attrs = {}
        for atrib in nodo.atributos:
            attrs[atrib.nome] = self._avaliar(atrib.valor)
        self.pokemons[nodo.nome]    = attrs
        self.ambiente[nodo.nome]    = attrs   # acessivel como variavel tambem

    def _exec_batalha(self, nodo: NodoBatalha):
        """Executa um bloco de batalha entre dois Pokemon."""
        sep = "-" * 45
        print(f"\n  {sep}")
        print(f"  >> BATALHA: {nodo.nome1} vs {nodo.nome2} <<")
        print(f"  {sep}")

        # Verifica se ambos os Pokemon existem
        for nome in (nodo.nome1, nodo.nome2):
            if nome not in self.pokemons:
                raise ErroExecucao(
                    f"Pokemon '{nome}' nao declarado para a batalha",
                    nodo.linha
                )

        for cmd in nodo.corpo:
            self._exec(cmd)

        print(f"  {sep}\n")

    # ---- comandos

    def _exec_decl_var(self, nodo: NodoDeclVar):
        """Declara e inicializa uma variavel tipada."""
        valor = self._avaliar(nodo.valor)
        # Coercao de tipo
        if nodo.tipo == "inteiro":
            try:
                valor = int(valor)
            except (TypeError, ValueError):
                raise ErroExecucao(
                    f"nao e possivel converter '{valor}' para inteiro",
                    nodo.linha
                )
        elif nodo.tipo == "texto":
            valor = self._para_texto(valor)
        self.ambiente[nodo.nome] = valor

    def _exec_atrib(self, nodo: NodoAtrib):
        """Executa uma atribuicao: variavel = expr  ou  pokemon.attr = expr."""
        valor = self._avaliar(nodo.valor)

        if isinstance(nodo.alvo, NodoIdentificador):
            self.ambiente[nodo.alvo.nome] = valor

        elif isinstance(nodo.alvo, NodoAcesso):
            obj  = nodo.alvo.objeto
            attr = nodo.alvo.atributo
            if obj not in self.pokemons:
                raise ErroExecucao(
                    f"Pokemon '{obj}' nao declarado",
                    nodo.linha
                )
            self.pokemons[obj][attr] = valor
            # Sincroniza com o ambiente
            if obj in self.ambiente:
                self.ambiente[obj][attr] = valor

    def _exec_mostrar(self, nodo: NodoMostrar):
        """Exibe o resultado de uma expressao no terminal."""
        valor = self._avaliar(nodo.expressao)
        print(f"  {self._para_texto(valor)}")

    def _exec_capturar(self, nodo: NodoCapturar):
        """Le uma entrada do usuario e armazena na variavel indicada."""
        try:
            entrada = input(f"  Entrada ({nodo.variavel}): ").strip()
        except EOFError:
            entrada = ""

        # Tenta inferir o tipo automaticamente
        try:
            if "." in entrada:
                self.ambiente[nodo.variavel] = float(entrada)
            else:
                self.ambiente[nodo.variavel] = int(entrada)
        except ValueError:
            self.ambiente[nodo.variavel] = entrada

    def _exec_se(self, nodo: NodoSe):
        """Executa condicional se/entao/senao."""
        cond = self._avaliar(nodo.condicao)
        if self._truthy(cond):
            for cmd in nodo.corpo_entao:
                self._exec(cmd)
        else:
            for cmd in nodo.corpo_senao:
                self._exec(cmd)

    def _exec_enquanto(self, nodo: NodoEnquanto):
        """Executa laco de repeticao enquanto/faca."""
        limite = 10_000   # protecao contra loop infinito
        passos = 0
        while self._truthy(self._avaliar(nodo.condicao)):
            for cmd in nodo.corpo:
                self._exec(cmd)
            passos += 1
            if passos >= limite:
                raise ErroExecucao(
                    "limite de iteracoes atingido (possivel loop infinito)",
                    nodo.linha
                )

    # ---------------------------------------------------------------- avaliacao de expressoes

    def _avaliar(self, nodo):
        """Avalia uma expressao e retorna seu valor."""

        if isinstance(nodo, NodoNumero):
            return nodo.valor

        if isinstance(nodo, NodoString):
            return nodo.valor

        if isinstance(nodo, NodoBooleano):
            return nodo.valor

        if isinstance(nodo, NodoIdentificador):
            return self._obter_var(nodo.nome, nodo.linha)

        if isinstance(nodo, NodoAcesso):
            if nodo.objeto not in self.pokemons:
                raise ErroExecucao(
                    f"Pokemon '{nodo.objeto}' nao declarado",
                    nodo.linha
                )
            attrs = self.pokemons[nodo.objeto]
            if nodo.atributo not in attrs:
                raise ErroExecucao(
                    f"atributo '{nodo.atributo}' nao encontrado em '{nodo.objeto}'",
                    nodo.linha
                )
            return attrs[nodo.atributo]

        if isinstance(nodo, NodoBinario):
            return self._eval_binario(nodo)

        if isinstance(nodo, NodoUnario):
            return self._eval_unario(nodo)

        raise ErroExecucao(f"expressao desconhecida: {type(nodo).__name__}")

    def _eval_binario(self, nodo: NodoBinario):
        op  = nodo.operador

        # Operadores logicos com curto-circuito
        if op == "e":
            esq = self._avaliar(nodo.esquerda)
            return esq if not self._truthy(esq) else self._avaliar(nodo.direita)
        if op == "ou":
            esq = self._avaliar(nodo.esquerda)
            return esq if self._truthy(esq) else self._avaliar(nodo.direita)

        esq = self._avaliar(nodo.esquerda)
        dir = self._avaliar(nodo.direita)

        if op == "+":
            # Concatenacao se qualquer operando for texto
            if isinstance(esq, str) or isinstance(dir, str):
                return self._para_texto(esq) + self._para_texto(dir)
            return esq + dir
        if op == "-":  return esq - dir
        if op == "*":  return esq * dir
        if op == "/":
            if dir == 0:
                raise ErroExecucao("divisao por zero", nodo.linha)
            resultado = esq / dir
            # Retorna inteiro se divisao exata
            return int(resultado) if resultado == int(resultado) else resultado
        if op == "==": return esq == dir
        if op == "!=": return esq != dir
        if op == ">":  return esq > dir
        if op == "<":  return esq < dir
        if op == ">=": return esq >= dir
        if op == "<=": return esq <= dir

        raise ErroExecucao(f"operador desconhecido: '{op}'", nodo.linha)

    def _eval_unario(self, nodo: NodoUnario):
        val = self._avaliar(nodo.operando)
        if nodo.operador == "-":   return -val
        if nodo.operador == "nao": return not self._truthy(val)
        raise ErroExecucao(f"operador unario desconhecido: '{nodo.operador}'")
