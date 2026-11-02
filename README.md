# MiniLang - Analisadores Léxico e Sintático

Analisador léxico manual da MiniLang. O reconhecimento é feito símbolo a símbolo,
sem `re`, `split`, geradores de lexer ou `isalpha()`/`isdigit()` (requisitos do projeto).

Analisador sintático descendente recursivo (Trabalho 02): recebe os tokens do
lexer, reconhece programas da MiniLang e constrói a árvore sintática abstrata
(AST). Não executa as expressões nem verifica declarações de variáveis.

## Integrantes

| Nome | Matrícula |
| --- | --- |
| _a preencher_ | _a preencher_ |

## Execução

Requer Python 3.10 ou superior.

```
python main.py examples/testes-slide2-sucesso.min
python main.py examples/testes-slide2-erro.min
```

Imprime a lista de tokens, os diagnósticos léxicos, o diagnóstico sintático e,
se não houver erro, a AST.

**Exemplo de AST** - `examples/testes-slide2-sucesso.min` (o programa do slide 2
mais os casos de precedência e associatividade do slide 6), trecho final da saída:

```
Programa
├── Declaracao(x)
├── Atribuicao(x)
│   └── Binaria(+)
│       ├── Inteiro(2)
│       └── Binaria(*)
│           ├── Inteiro(3)
│           └── Inteiro(4)
├── Saida
│   └── Variavel(x)
├── Saida
│   └── Binaria(*)
│       ├── Binaria(+)
│       │   ├── Inteiro(2)
│       │   └── Inteiro(3)
│       └── Inteiro(4)
├── Saida
│   └── Binaria(-)
│       ├── Binaria(-)
│       │   ├── Inteiro(10)
│       │   └── Inteiro(3)
│       └── Inteiro(2)
└── Saida
    └── Variavel(y)
```

**Exemplo de diagnóstico sintático** - `examples/testes-slide2-erro.min`. A
análise para no primeiro erro (linha 3) e a linha 4, também inválida, não chega a
ser examinada:

```
Diagnóstico sintatico:
  3:11: esperado numero, identificador ou '(', encontrado ')'
```

O diagnóstico traz `linha:coluna` do token encontrado e o que se esperava no lugar.

Os outros exemplos mostram os dois limites da análise:

- `examples/programa.min` usa `if`, fora do escopo do trabalho:
  `3:1: esperado comando ('int', 'print' ou identificador), encontrado 'if'`.
- `examples/diagnosticos.min` tem três erros léxicos (`2:6`, `4:1`, `4:3`), então
  o parser não roda. Sem os símbolos inválidos a lista de tokens não representa
  mais o arquivo, e o parser acusaria erros que não existem no texto.

## Testes

```
pip install -r requirements.txt
python -m pytest tests
```

Resultado: **441 passed** - 72 do lexer e 369 do analisador sintático.

| Arquivo | O que cobre |
| --- | --- |
| `test_parser.py` | Cursor (`peek`/`advance`/`match`/`expect`), Etapa 1 (expressões), Etapa 2 (programas) e Etapa 3 (diagnósticos com posição e mensagem) |
| `test_parser_invariants.py` | `parse()` nunca levanta; sucesso consome todos os tokens; um diagnóstico só, na posição do token encontrado; parênteses redundantes, espaços e comentários não mudam a AST |
| `test_syntax_tree.py` | Forma compacta dos nós e o visualizador textual |
| `test_grammar.py` | O catálogo da gramática: FIRST, condição LL(1) e cada exemplo reconhecido pelo método do `Parser` correspondente |

## Gramática

É a gramática G₂ das aulas 06-08: a gramática da MiniLang com os níveis de
precedência separados e sem recursão à esquerda. Declaração com inicialização
(`int x = 10;`) não tem produção (Aula 06) e é erro sintático.

```
Programa   → ListaItens
ListaItens → Item ListaItens | ε
Item       → Declaracao | Atribuicao | Saida
Declaracao → KW_INT IDENT SEMICOLON
Atribuicao → IDENT ASSIGN Expr SEMICOLON
Saida      → KW_PRINT LPAREN Expr RPAREN SEMICOLON
Expr       → Termo Expr′
Expr′      → PLUS Termo Expr′ | MINUS Termo Expr′ | ε
Termo      → Fator Termo′
Termo′     → STAR Fator Termo′ | SLASH Fator Termo′ | ε
Fator      → LPAREN Expr RPAREN | IDENT | INT_LITERAL
```

| Nível | Não-terminal | Operadores | Associatividade |
| --- | --- | --- | --- |
| 1 (menor) | `Expr` | `+` `-` | esquerda |
| 2 | `Termo` | `*` `/` | esquerda |
| 3 (maior) | `Fator` | literal, identificador, `( Expr )` | - |

| Não-terminal | FIRST | FOLLOW |
| --- | --- | --- |
| `Programa`, `ListaItens` | `KW_INT IDENT KW_PRINT ε` | `EOF` |
| `Item`, `Declaracao`, `Atribuicao`, `Saida` | o próprio comando (`KW_INT`, `IDENT`, `KW_PRINT`) | `KW_INT IDENT KW_PRINT EOF` |
| `Expr` | `LPAREN IDENT INT_LITERAL` | `SEMICOLON RPAREN` |
| `Expr′` | `PLUS MINUS ε` | `SEMICOLON RPAREN` |
| `Termo` | `LPAREN IDENT INT_LITERAL` | `PLUS MINUS SEMICOLON RPAREN` |
| `Termo′` | `STAR SLASH ε` | `PLUS MINUS SEMICOLON RPAREN` |
| `Fator` | `LPAREN IDENT INT_LITERAL` | `STAR SLASH PLUS MINUS SEMICOLON RPAREN` |

As alternativas de cada não-terminal têm FIRST disjuntos, e nos anuláveis FIRST e
FOLLOW também são disjuntos: G₂ é LL(1), e um token de consulta basta para cada
decisão do parser. O catálogo `minilang/spec/grammar.py` guarda esses conjuntos e
`tests/test_grammar.py` confere a condição.

## Correspondência de nomes

O código segue a convenção do projeto (identificadores em inglês). Os rótulos
impressos da AST são os do enunciado.

| Enunciado / slides | Código |
| --- | --- |
| `programa()`, `lista_itens()`, `item()` | `program()`, `item_list()`, `item()` |
| `declaracao()`, `atribuicao()`, `saida()` | `declaration()`, `assignment()`, `output()` |
| `expressao()`, `termo()`, `fator()` | `expression()`, `term()`, `factor()` |
| `peek()`, `advance()`, `expect()`, `match()`, `at_end()` | iguais |
| `Programa`, `Declaracao`, `Atribuicao`, `Saida` | `Program`, `Declaration`, `Assignment`, `Output` |
| `Binaria`, `Variavel`, `Inteiro` | `Binary`, `Variable`, `Integer` |

## Organização

```
main.py                     Lê o arquivo-fonte e imprime tokens, diagnósticos e a AST
examples/                   Programas de exemplo
minilang/
├── analysis/
│   ├── lexer.py            A varredura: cursor, posição e as operações do lexer
│   └── parser.py           O parser descendente recursivo: um método por não-terminal
└── spec/
    ├── alphabet.py         Conjuntos do alfabeto e os predicados sobre um símbolo
    ├── tokens.py           TokenType, Token e Diagnostic
    ├── lexical_class.py    O tipo LexicalClass e a ação de cada classe
    ├── recognizers.py      Os pares claims/consume que as classes usam
    ├── table.py            As 11 classes léxicas
    ├── grammar.py          O catálogo da gramática G₂: produções, FIRST, FOLLOW e operadores
    └── syntax_tree.py      Os nós da AST e o visualizador textual
tests/
├── test_lexer.py           Os gabaritos das seções 4 e 6 do enunciado do lexer
├── test_invariants.py      EOF único, CRLF, progresso da varredura
├── test_catalog.py         Os casos e interações de cases.py e interactions.py contra a varredura
├── cases.py                Casos de teste por classe
├── interactions.py         Interações entre classes
├── test_parser.py          Cursor e as três etapas do Trabalho 02
├── test_parser_invariants.py  Invariantes do parser
├── test_syntax_tree.py     Nós da AST e visualizador
└── test_grammar.py         O catálogo da gramática contra o parser
```

### Analisador léxico

O `Lexer` mantém um cursor sobre o código-fonte e não divide a entrada
previamente. A cada volta do laço, `scan_token` percorre a tabela léxica e
pergunta a cada classe se ela é dona da posição atual (`claims`, que consulta no
máximo dois símbolos e não consome nada). A primeira que reclamar consome o
lexema (`consume`) e emite o token.

Nenhuma classe indexa o código-fonte diretamente: tudo passa pelas operações do
lexer (`advance`, `peek`, `peek_next`, `match`), e é em `advance` que linha e
coluna são atualizadas. A ordem das classes na tabela só desempata quem reclama
a **mesma** posição - `LINE_COMMENT` antes de `ARITH_OP` por causa de `/`, e
`REL_OP` antes de `ASSIGN` por causa de `=`.

Palavras reservadas não participam da varredura. `identifier()` consome o
identificador inteiro e só então consulta a tabela de reservadas, que é o que faz
`intx`, `ifx` e `while1` continuarem `IDENT`.

Quando nenhuma classe reclama a posição, o lexer consome o símbolo, registra um
diagnóstico e segue. Consumir antes de relatar é o que garante progresso e evita
laço infinito.

### Analisador sintático

O `Parser` mantém um cursor sobre a lista de tokens, e toda leitura passa por
`peek`, `advance`, `match` e `expect`; `advance` nunca passa do `EOF`. Cada
não-terminal de G₂ é um método, e cada escolha entre alternativas olha só o token
atual, sem consumir. As continuações `Expr′` e `Termo′` viram laços em
`expression()` e `term()`: o resultado acumulado vira o filho esquerdo do próximo
`Binary`, e é isso que faz `10 - 3 - 2` virar `(10 - 3) - 2`. Parênteses não
viram nó, porque o agrupamento já está na forma da árvore.

`program()` só termina quando chega ao `EOF`, então a entrada inteira precisa ser
reconhecida, não apenas um prefixo. No primeiro erro, `expect` levanta um
`ParseError` interno que desenrola a pilha até `parse()`. `parse()` nunca levanta:
devolve `(programa, [])` ou `(None, [diagnóstico])`, o mesmo contrato de
`scan_tokens()`.

## Limitações conhecidas

- O lexer não julga se a sequência de tokens forma um programa válido. `2total`
  produz `INT_LITERAL("2")` e `IDENT("total")` sem erro; é o analisador
  sintático que decide se isso é aceitável.
- Cada símbolo inválido gera um diagnóstico próprio. `@@@` produz três
  diagnósticos, não um só para o trecho.
- Não há limite de magnitude para `INT_LITERAL`. O lexema é reconhecido como
  está, e um valor grande demais só seria problema em fases posteriores.
- Acentos não pertencem ao alfabeto. `vãlor` vira `IDENT("v")`, um diagnóstico
  para `ã` e `IDENT("lor")`.
- Um `CR` sozinho, sem `LF`, conta como quebra de linha.
- O arquivo-fonte é lido inteiro na memória antes da varredura.
- O parser para no primeiro erro sintático: um arquivo com três erros mostra só
  o primeiro.
- Com erro léxico, o parser não roda.
- `if`, `else`, `while`, blocos, operadores relacionais e `-` unário estão fora
  do escopo e são rejeitados como erro sintático.
- Não há verificação semântica: `print(y);` sem declarar `y` e `int x; int x;`
  são aceitos.
- Literais não são avaliados: `007` aparece na AST como `Inteiro(007)`.
- Aninhamento muito profundo de parênteses (perto de 330 níveis) estoura a pilha
  do Python; o parser devolve o diagnóstico `expressao aninhada demais` em vez de
  um traceback.
