"""Cursor sobre uma sequência: a parte que o lexer e o parser têm em comum"""


class Cursor:
    # O que peek devolve quando não há mais item. O lexer troca por "" para comparar com símbolos
    END = None

    def __init__(self, items):
        self.items = items
        self.current = 0        # índice do próximo item a ler

    def at_end(self) -> bool:
        return self.current >= len(self.items)

    def peek(self, offset: int = 0):
        index = self.current + offset
        if index >= len(self.items):
            return self.END
        return self.items[index]

    def check(self, expected) -> bool:
        return self.peek() == expected

    def advance(self):
        item = self.peek()
        if not self.at_end():
            self.current += 1
        return item

    def match(self, expected) -> bool:
        if not self.check(expected):
            return False

        self.advance()
        return True
