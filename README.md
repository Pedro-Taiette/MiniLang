# MiniLang
É um projeto de compilador linguagem simples.

Já implementamos o lexer, com os tokens definidos em minilang/spec/tokens.py.

Há opções de ignorar tokens, comparar eles com outros e mais.

Testes estão presentes em minilang/tests/lexer_estrutura_linguagem.py

## Como rodar testes:
Inicie o ambiente virtual com
```
cd .\minilang\

python -m venv .venv

.\.venv\Scripts\activate

pip install -r requirements.txt
```

Depois, rode o teste com:
```bash
pytest .\tests\lexer_estrutura_linguagem.py
```

Ele deve passar todos os testes e nada será printado. Para ver mais dados, use o seguinte comando:
```bash
pytest -rA .\tests\lexer_estrutura_linguagem.py
```