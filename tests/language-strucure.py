from ..minilang.analise.lexer import tokenizar

def __init__():
    print("menor palavra válida")
    print(tokenizar("t"))
    print("palavra vazia")
    print(tokenizar(""))
    print("uma repetição, quando aplicável")
    print(tokenizar("repetido2"))
    print(tokenizar("repetido2"))
    print("várias repetições, quando aplicável")
    for _ in range(10):
        print(tokenizar("repetido_varias"))
    print("símbolo fora do alfabeto")
    print(tokenizar("á"))