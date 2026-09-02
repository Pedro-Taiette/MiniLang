# MiniLang
É um projeto de compilador linguagem simples.

Já implementamos o lexer, com os tokens definidos em minilang/spec/tokens.py.

Há opções de ignorar tokens, comparar eles com outros e mais.

Testes estão presentes em minilang/tests/.

## Como testar o lexer:
A partir da raiz do repositório:
```bash
python -m minilang
```

Digite um trecho de código no input. A saída é uma linha por token, com posição, tipo e lexema:
```
MiniLang> int x = 40 + 2;
   0  KW_INT        'int'
   4  IDENT         'x'
   6  ASSIGN        '='
   8  INT_LITERAL   '40'
  11  PLUS          '+'
  13  INT_LITERAL   '2'
  14  SEMICOLON     ';'
```

Espaços e comentários são reconhecidos e ignorados, então não aparecem na saída. Se houver um caractere inválido, o erro aponta a posição:
```
MiniLang> print(a @ 2);
posicao 8: '@' fora do alfabeto-fonte
```

## Como rodar testes:
A partir da raiz do repositório, inicie o ambiente virtual com
```
python -m venv .venv

.\.venv\Scripts\activate

pip install -r minilang\requirements.txt
```

Depois, rode os testes com:
```bash
pytest
```

O pytest descobre os testes sozinho; se tudo passar, nada além do resumo será printado. Para ver o nome de cada teste, use:
```bash
pytest -rA
```