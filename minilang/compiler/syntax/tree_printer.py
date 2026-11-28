"""Visualizador textual da AST: um nó por linha, com os filhos recuados"""


def format_tree(node) -> str:
    lines = [node.label()]
    add_children(node, "", lines)
    return "\n".join(lines)


def add_children(parent, prefix: str, lines: list) -> None:
    children = parent.children()
    for index, child in enumerate(children):
        last = index == len(children) - 1

        if last:
            lines.append(prefix + "+-- " + child.label())
            add_children(child, prefix + "    ", lines)
        else:
            lines.append(prefix + "|-- " + child.label())
            add_children(child, prefix + "|   ", lines)
