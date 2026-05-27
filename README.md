# PokeScript — Mini-Compilador

Linguagem de programacao imperativa com tematica Pokemon, interpretada em Python.
Desenvolvida como Projeto Final da disciplina de Compiladores (AED).

## Requisitos

- Python 3.10 ou superior
- Sem dependencias externas

## Como Executar

```bash
cd pokescript
python main.py <arquivo.pks>
```

## Exemplos Incluidos

| Arquivo | Descricao |
|---------|-----------|
| `examples/valido.pks` | Programa valido: laco, condicional, acesso a atributo |
| `examples/batalha.pks` | Batalha completa entre dois Pokemon com entrada do usuario |
| `examples/erro_lexico.pks` | 3 erros lexicos: simbolos invalidos e string nao fechada |
| `examples/erro_sintatico.pks` | 2 erros sintaticos: bloco sem FIM e SE sem ENTAO |
| `examples/erro_execucao.pks` | Erro de execucao: variavel nao declarada |

## Estrutura do Projeto

```
pokescript/
  lexer.py          # Fase 1 — Analisador Lexico
  ast_nodes.py      # Nos da AST + ImpressorAST
  parser.py         # Fase 2 — Analisador Sintatico (LL(1) descendente recursivo)
  interpreter.py    # Fase 3 — Interpretador tree-walker
  main.py           # Ponto de entrada (orquestra as 3 fases)
  examples/         # Programas .pks de exemplo
  README.md         # Este arquivo
```

## Tokens da Linguagem

| Categoria | Tokens |
|-----------|--------|
| Palavras-chave | `pokemon fim batalha vs se entao senao enquanto faca mostrar capturar inteiro texto e ou nao verdadeiro falso` |
| Identificadores | `[a-zA-Z_][a-zA-Z0-9_]*` |
| Numeros | `[0-9]+` (inteiro) ou `[0-9]+\.[0-9]+` (real) |
| Strings | `"..."` (aspas duplas) |
| Operadores | `= == != > < >= <= + - * /` |
| Delimitadores | `. ( )` |
| Comentarios | `# ate fim da linha` |

## Exemplo de Programa

```
pokemon dragonite
    nivel  = 55
    hp     = 250
    ataque = 134
fim

mostrar "Qual o seu nome?"
capturar treinador

batalha dragonite vs charizard faca
    dano = dragonite.ataque - 80
    mostrar "Dragonite causou " + dano + " de dano!"
fim

mostrar "Fim da batalha, " + treinador + "!"
```

## Tratamento de Erros

O compilador realiza recuperacao de erros em todas as fases:

- **Fase Lexica**: caracteres invalidos sao ignorados e reportados; a analise continua
- **Fase Sintatica**: tokens inesperados sao reportados; o parser tenta se sincronizar
- **Fase de Execucao**: variaveis nao declaradas, divisao por zero e outros erros semanticos sao capturados com mensagem de linha
