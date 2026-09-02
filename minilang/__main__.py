from .analise.erros import ErroLexico
from .analise.lexer import tokenizar


def main() -> None:
    fonte = input("MiniLang> ")

    try:
        for token in tokenizar(fonte):
            print(f"{token.pos:>4}  {token.tipo.value:<13} {token.lexema!r}")
    except ErroLexico as erro:
        print(erro)


if __name__ == "__main__":
    main()
