# Gerador de nomes brasileiros

Os programas `geranomes.py` e `geranomes.go` geram nomes a partir de um modelo
por [cadeia de Markov](https://pt.wikipedia.org/wiki/Cadeias_de_Markov)
construído a partir de uma amostra de cerca de 300.000 nomes de listas
publicadas pela Fuvest de 2002 a 2008 com nomes de pessoas isentas de taxa
e/ou convocadas para 2ª fase do vestibular.

Exemplo gerando 10 nomes:

```
% ./geranomes.py 10
Ulisses Damaceno dos Santos
Sidinei Fialho Prado Caldas
Danillo Teixeira Camargo Sipionato
Bruna Bueno da Silvestre
Gustavo Henrique de Siqueira
Rodolfo de Oliveira Amancio Pereira Rosa Arai
Amanda de Morais
Dominguez Correa da Silva
Roberto Martins Prado
Sueli Martins dos Reis
```

Observações:

* Cada nome gerado pode ou não existir na amostra.
* A lista gerada pode conter repetições.
* `geranomes.py` pode acrescentar acentos a certas partes do nome.

Nomes repetidos ocorrem em praticamente qualquer lista extensa que não tenha sido filtrada.
Nas diferentes listas da Fuvest, cerca de 1% a 3% dos nomes são repetidos.
Nas listas geradas por estes programas, a porcentagem de homônimos pode ser maior ou menor,
dependendo do número de nomes solicitado.

## Referências

* [Registro Civil](https://transparencia.registrocivil.org.br/inicio): 50 prenomes mais comuns de 2015 a 2024
