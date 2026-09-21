# MiniLang - Analisador Léxico

Analisador léxico manual da MiniLang. O reconhecimento é feito símbolo a símbolo,
sem `re`, `split`, geradores de lexer ou `isalpha()`/`isdigit()` (requisitos do projeto).

## Integrantes

| Nome | Matrícula |
| --- | --- |
| _a preencher_ | _a preencher_ |

## Execução

```
python main.py examples/programa.min
```

Imprime a lista de tokens e, depois, a lista de diagnósticos.

## Testes

```
pip install -r requirements.txt
python -m pytest tests
```

## Organização

```
main.py                     Lê o arquivo-fonte e imprime tokens e diagnósticos
examples/                   Programas de exemplo
minilang/
├── analysis/lexer.py       A varredura: cursor, posição e as operações do lexer
└── spec/
    ├── alphabet.py         Conjuntos do alfabeto e os predicados sobre um símbolo
    ├── tokens.py           TokenType, Token e Diagnostic
    ├── lexical_class.py    O tipo LexicalClass e a ação de cada classe
    ├── recognizers.py      Os pares claims/consume que as classes usam
    ├── table.py            As 11 classes léxicas
    ├── cases.py            Casos de teste por classe
    └── interactions.py     Interações entre classes
tests/
├── test_lexer.py           Os gabaritos das seções 4 e 6 do enunciado
├── test_invariants.py      EOF único, CRLF, progresso da varredura
└── test_catalog.py         Os casos e interações de spec/ contra a varredura
```

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