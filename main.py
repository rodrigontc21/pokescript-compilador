# =============================================================================
#  PokeScript - Ponto de Entrada  (3 fases: Lexico + Sintatico + Interpretacao)
#  Uso: python main.py <arquivo.pks>
# =============================================================================

import sys
from lexer        import Lexer, TipoToken
from parser       import Parser
from interpreter  import Interpretador, ErroExecucao
from ast_nodes    import ImpressorAST

SEP  = "=" * 57
LINHA = "-" * 57


def executar(caminho: str):
    # ---------------------------------------------------------------- leitura
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            fonte = f.read()
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{caminho}' nao encontrado.")
        sys.exit(1)

    print(f"\n{SEP}")
    print(f"  PokeScript  --  {caminho}")
    print(f"{SEP}\n")

    # ========================================================
    # FASE 1: ANALISE LEXICA
    # ========================================================
    print("[ FASE 1 ]  Analise Lexica")
    print(LINHA)

    lexer = Lexer(fonte)
    tokens, erros_lex = lexer.tokenizar()

    for tok in tokens:
        if tok.tipo != TipoToken.EOF:
            print(f"  {tok}")

    if erros_lex:
        print(f"\n  Erros lexicos encontrados ({len(erros_lex)}):")
        for e in erros_lex: print(f"  {e}")
        print(f"\n{SEP}")
        print("  Analise interrompida por erros lexicos.")
        print(f"{SEP}\n")
        return
    print(f"\n  OK  —  {len(tokens)} tokens gerados")

    # ========================================================
    # FASE 2: ANALISE SINTATICA
    # ========================================================
    print(f"\n[ FASE 2 ]  Analise Sintatica")
    print(LINHA)

    parser = Parser(tokens)
    ast, erros_sin = parser.parsear()

    if erros_sin:
        print(f"  Erros sintaticos encontrados ({len(erros_sin)}):")
        for e in erros_sin: print(f"  {e}")
        print(f"\n{SEP}")
        print("  Analise interrompida por erros sintaticos.")
        print(f"{SEP}\n")
        return

    print("  OK  —  AST construida\n")
    print("  Arvore Sintatica Abstrata:")
    print(LINHA)
    ImpressorAST().imprimir(ast, indent=1)

    # ========================================================
    # FASE 3: INTERPRETACAO
    # ========================================================
    print(f"\n[ FASE 3 ]  Execucao")
    print(LINHA)

    interpretador = Interpretador()
    try:
        interpretador.executar(ast)
    except ErroExecucao as e:
        print(f"\n  {e!r}")

    # ---- Estado final do ambiente
    if interpretador.ambiente or interpretador.pokemons:
        print(f"\n  Estado final das variaveis:")
        print(LINHA)
        for nome, val in interpretador.ambiente.items():
            if not isinstance(val, dict):
                print(f"    {nome:15} = {val}")
        for nome, attrs in interpretador.pokemons.items():
            print(f"    [pokemon] {nome}:")
            for k, v in attrs.items():
                print(f"        {k:12} = {v}")

    # ---- Resumo
    print(f"\n{SEP}")
    print(f"  Tokens    : {len(tokens)}")
    print(f"  Erros lex : {len(erros_lex)}")
    print(f"  Erros sin : {len(erros_sin)}")
    print(f"  Status    : ACEITO E EXECUTADO")
    print(f"{SEP}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.pks>")
        print("Exemplos:")
        print("  python main.py examples/valido.pks")
        print("  python main.py examples/batalha.pks")
        print("  python main.py examples/erro_lexico.pks")
        sys.exit(0)
    executar(sys.argv[1])
