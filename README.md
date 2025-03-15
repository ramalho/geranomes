# Gerador de nomes brasileiros

Os programas `namegen.py` e `namegen.go` geram nomes a partir de um modelo
por [cadeia de Markov](https://pt.wikipedia.org/wiki/Cadeias_de_Markov)
construído a partir de uma amostra de cerca de 300.000 nomes de listas
publicadas pela Fuvest de 2002 a 2008 com nomes de pessoas isentas de taxa
e/ou convocadas para 2ª fase do vestibular.

Exemplo gerando 10 nomes:

```
% ./namegen.py 10
Catia Alameddine Butilhao
Raphael Mesquita Santos Junior
Mariana Luisa Battistini
Diego Carvalho dos Santos
Tiago Fadel Mondeki dos Santos
Marcelo Oliva Vieira
Eleonora Barbosa de Camargo Guerra
Tarcicleide Eugenio Borges
Nubia de Andrade Costa
Carla da Silva
```

Observações:

* Cada nome gerado pode ou não existir na amostra.
* A lista gerada pode conter repetições.
* `namegen.py` pode acrescentar acentos a certas partes do nome.

Nomes repetidos ocorrem em praticamente qualquer lista extensa que não tenha sido filtrada.
Nas diferentes listas da Fuvest, cerca de 1% a 3% dos nomes são repetidos.
Nas listas geradas por estes programas, a porcentagem de homônimos pode ser maior ou menor,
dependendo do número de nomes solicitado.
