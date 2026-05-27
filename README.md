# 🎓 PokeScript - Mini-Compilador | Projeto Final AED

Este projeto implementa um **Mini-Compilador completo** para a linguagem **PokeScript**, uma linguagem imperativa e interpretada com temática do universo Pokémon, desenvolvida como projeto final da disciplina de **AED - Compiladores**.

## 🎯 Objetivo

Desenvolver, de forma incremental, uma **linguagem de programação própria** com regras claras, tokens definidos e um pipeline completo de compilação em **3 fases**: análise léxica, análise sintática e interpretação/execução, implementadas inteiramente em **Python 3** sem uso de bibliotecas externas de geração de parsers.

---

## 📂 Estrutura do Projeto

```text
📁 pokescript/
├── main.py               ← Ponto de entrada — orquestra as 3 fases do pipeline
├── lexer.py              ← Fase 1: Analisador Léxico (tokenização + erros léxicos)
├── parser.py             ← Fase 2: Analisador Sintático LL(1) recursivo descendente
├── ast_nodes.py          ← 17 classes de nós da AST + ImpressorAST
├── interpreter.py        ← Fase 3: Interpretador Tree-Walker (execução da AST)
├── README.md             ← Este arquivo
└── examples/
    ├── valido.pks         ← Entrada válida — loop de batalha (71 tokens)
    ├── batalha.pks        ← Entrada válida — batalha completa com input (198 tokens)
    ├── erro_lexico.pks    ← Entrada inválida — 3 erros léxicos tratados
    ├── erro_sintatico.pks ← Entrada inválida — 2 erros sintáticos tratados
    └── erro_execucao.pks  ← Entrada inválida — 1 erro de execução tratado
```

---

## ⚙️ Tecnologias Utilizadas

- **Python 3.10+** — implementação de todo o compilador
- **Módulo `enum`** — enumeração dos tipos de token (`TipoToken`)
- **Orientação a Objetos** — classes para Token, Lexer, Parser, AST e Interpretador
- **Sem dependências externas** — nenhuma biblioteca de terceiros necessária

---

## 🧪 Funcionalidades

### 🔍 Fase 1 — Analisador Léxico (`lexer.py`)
- **Tokenização manual** caractere a caractere sem uso de regex ou PLY/ANTLR.
- **18 palavras reservadas** reconhecidas com prioridade máxima sobre identificadores.
- **Reconhecimento de:** identificadores, inteiros, floats, strings, operadores simples e duplos, delimitadores e comentários (`#`).
- **Recuperação de erros léxicos:** símbolo inválido é reportado com linha e coluna e a tokenização continua — todos os erros são listados em uma única execução.
- **Erros detectados:** caractere não reconhecido, string não fechada.

### 🌳 Fase 2 — Analisador Sintático (`parser.py` + `ast_nodes.py`)
- **Parser LL(1) recursivo descendente** — cada não-terminal da GLC é um método Python.
- **Gramática Livre de Contexto (BNF)** com conjuntos FIRST e FOLLOW calculados.
- **Construção simultânea da AST** com 17 classes de nós.
- **Hierarquia de precedência** de operadores codificada na estrutura de chamadas.
- **Recuperação de erros sintáticos:** erro registrado com linha e coluna, análise continua.

### ⚡ Fase 3 — Interpretador (`interpreter.py`)
- **Tree-walker interpreter** — percorre a AST diretamente sem geração de bytecode.
- **Tabela de símbolos** com dois dicionários: `ambiente` (variáveis) e `pokemons` (entidades Pokémon).
- **Tipagem dinâmica** com coerção explícita para `inteiro` e `texto`.
- **Curto-circuito lógico** nos operadores `e` e `ou`.
- **Concatenação automática** de strings com o operador `+`.
- **Proteção contra loop infinito:** laços `enquanto` são abortados após 10.000 iterações.

### 🛡️ Tratamento de Erros (3 fases)
- **Erros Léxicos (L1/L2):** caractere inválido, string não fechada.
- **Erros Sintáticos (S1–S5):** token inesperado, comando inválido, expressão inválida, declaração inválida, ID sem operador.
- **Erros de Execução (E1–E7):** variável não declarada, Pokémon não declarado, atributo inexistente, divisão por zero, tipo incompatível, loop infinito, nó desconhecido.

---

## 📋 Tokens Reconhecidos

| Categoria | Tokens |
|---|---|
| Palavras reservadas | `pokemon` `fim` `batalha` `vs` `se` `entao` `senao` `enquanto` `faca` `mostrar` `capturar` `inteiro` `texto` `e` `ou` `nao` `verdadeiro` `falso` |
| Literais | `NUM_INT` `NUM_FLOAT` `STRING` |
| Identificadores | `ID` |
| Operadores aritméticos | `+` `-` `*` `/` |
| Operadores relacionais | `==` `!=` `>` `<` `>=` `<=` |
| Operador de atribuição | `=` |
| Delimitadores | `(` `)` `.` |
| Especiais | `COMENTARIO` `EOF` |

---

## 📐 Gramática (resumo BNF)
programa     -> declaracao* EOF
declaracao   -> decl_pokemon | decl_batalha | comando
decl_pokemon -> POKEMON ID atrib_pok* FIM
decl_batalha -> BATALHA ID VS ID bloco FIM
bloco        -> comando*
comando      -> MOSTRAR expressao | CAPTURAR ID
| SE expressao ENTAO bloco (SENAO bloco)? FIM
| ENQUANTO expressao FACA bloco FIM
| INTEIRO ID ATRIB expressao
| TEXTO ID ATRIB expressao
| ID ATRIB expressao
| ID PONTO ID ATRIB expressao
expressao    -> expr_ou -> expr_e -> expr_nao -> expr_comp
-> expr_soma -> expr_mult -> expr_unario -> fator
---

## 📈 Resultados (Resumo)

- Pipeline completo de **3 fases** funcionando de ponta a ponta.
- **1.327 linhas** de código Python distribuídas em 5 módulos.
- **5 arquivos de teste** cobrindo caminho feliz e erros em cada fase.
- Detecção e reporte de erros com **linha e coluna exatos** em todas as fases.
- **Estado final das variáveis** exibido ao término de toda execução.
- Saída do pipeline: tokens, AST indentada, saída do programa e tabela de símbolos.

---

## 📌 Limitações e Próximos Passos

- Não há suporte a funções/procedimentos definidos pelo usuário.
- Tipagem apenas `inteiro`, `texto` e `pokemon` — sem suporte a listas ou dicionários.
- Possibilidade futura de gerar bytecode intermediário em vez de interpretar a AST diretamente.
- Expansão do sistema de tipos com verificação estática em tempo de compilação.
- Possibilidade de adicionar suporte a múltiplos arquivos e importações.

---

## 📃 Como Executar

**1. Clone este repositório**
> git clone https://github.com/rodrigontc21/pokescript-compilador.git

**2. Acesse a pasta do projeto**
> cd pokescript-compilador

**3. Execute com um arquivo `.pks`**

| Opção | Arquivo | Comando |
|---|---|---|
| 1 — Entrada válida simples | `valido.pks` | `python main.py examples/valido.pks` |
| 2 — Batalha completa com input | `batalha.pks` | `python main.py examples/batalha.pks` |
| 3 — Erro léxico | `erro_lexico.pks` | `python main.py examples/erro_lexico.pks` |
| 4 — Erro sintático | `erro_sintatico.pks` | `python main.py examples/erro_sintatico.pks` |
| 5 — Erro de execução | `erro_execucao.pks` | `python main.py examples/erro_execucao.pks` |

*(Dica: Para `batalha.pks` será solicitado um input — digite o nome do treinador e pressione Enter.)*

**Pré-requisito:** Python 3.10 ou superior. Nenhuma dependência externa necessária.

---

## 👤 Autor

**Rodrigo Vieira** — Estudante de Ciência da Computação | PUC Goiás

---

## 📝 Licença

Projeto desenvolvido com fins didáticos e acadêmicos.  
Uso livre para estudos e aprimoramento de portfólio.
