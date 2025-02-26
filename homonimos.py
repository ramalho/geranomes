#!/usr/bin/env python3

import sys
from collections import Counter

def contar(stream):
    contador = Counter()
    for nome in stream:
        if nome.strip():
            contador[nome] += 1
    return contador

def relatorio(contador):
    qtd_homonimos = 0
    for nome, qtd in contador.most_common():
        if qtd < 2:
            break
        qtd_homonimos += qtd
        print(f'{qtd:2d}\t{nome.strip()}')
    total = contador.total()
    pct = 100 * qtd_homonimos / total
    stats = f'# nomes: {total:_d}; homônimos: {qtd_homonimos:_d} ({pct:.1f}%)'
    print(stats)


def main():
    if len(sys.argv) == 1:  # nenhum argumento
        contador = contar(sys.stdin)
    else:
        with open(sys.argv[1], 'r') as f:
            contador = contar(f)

    relatorio(contador)

if __name__ == '__main__':
    main()