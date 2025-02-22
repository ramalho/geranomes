from collections.abc import Iterable

"""
Gerador de nomes brasileiros

>>> extrair_partes('Jane Dias')
['Jane', 'Dias']
>>> extrair_partes('Jane da Silva')
['Jane', 'da Silva']
>>> extrair_partes('Jane Von Zuben')
['Jane', 'Von Zuben']
>>> extrair_partes('Ana Paula da Silva H18')
['Ana', 'Paula', 'da Silva']
"""

prefixos = "da das de di do dos du del von van"
prefixos += prefixos.title()
prefixos = prefixos.split()

prefixos_duplos = [
    "van de",
    "van den",
    "van der",
    "van des",
    "von der",
    "von den",
    "von des",
]
prefixos_duplos.extend([p.title() for p in prefixos_duplos])


def extrair_juniores(nomes: Iterable[str]) -> set[str]:
    juniores = []
    for nome in nomes:
        nome, *_, ultimo = nome.split()
        if ultimo == "Jr":
            juniores.append(nome)
    return set(juniores)


def extrair_partes(nome: str) -> list[str]:
    for prefixo in prefixos:
        de = f" {prefixo} "
        para = f" {prefixo}_"
        nome = nome.replace(de, para)
    partes = nome.split()
    if partes[-1].startswith("H0") or partes[-1].startswith("H1"):
        del partes[-1]
    partes = [parte.replace("_", " ") for parte in partes]
    return partes
