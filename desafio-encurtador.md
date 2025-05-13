# Encurtador de nomes para cartão de crédito

Este é um desafio para uso em coding dojos.

## Objetivo

Abreviar nomes de acordo com um conjunto de regras
para fazê-los caber em um campo de 26 posições em
um cartão de crédito.

## Comportamento esperado

* Se o nome tem 26 caracteres ou menos, devolver sem alteração.

* Se o nome tem mais de 26 caracteres, aplicar uma ou mais regras para encurtar.

## Pré-requisitos

O nome será fornecido em MAIÚSCULAS usando apenas caracteres ASCII:
espaços e letras A-Z (sem acentos).

## Regras sugeridas

### Abreviar prenome Maria

Abreviar MARIA para M somente quando MARIA for o primeiro nome.

Exemplo:

```
MARIA BEATRIZ CAMARGO DUARTE (28 caracteres)
M BEATRIZ CAMARGO DUARTE
```

### Abreviar JUNIOR

Abreviar JUNIOR para JR, exceto se JUNIOR for o primeiro nome.

```
VICTOR SIVIERO BOMFIM JUNIOR (28 caracteres)
VICTOR SIVIERO BOMFIM JR
```

### Remover uma preposição

Remover uma preposição como DA, DAS, DE, DO, DOS, VON, VAN.

Exemplo:

```
RODRIGO OLIVEIRA DOS SANTOS (27 caracteres)
RODRIGO OLIVEIRA SANTOS
```

### Abreviar uma parte do sobrenome

Reduzir uma parte do sobrenome para uma letra inicial,
sem abreviar o último sobrenome.
Priorize os sobrenomes: abrevie o penúltima parte do nome primeiro.
A ideia é evitar abreviar partes de um prenome composto, como
JOSELIA CAROLINA.

Exemplo:

```
JOSELIA CAROLINA CASTRO SANTOS (30 caracteres)
JOSELIA CAROLINA C SANTOS
```

## Observações

### Como organizar a solução

A existência de diferentes regras sugere uma solução com uma função principal que aplica funções auxiliares, cada uma delas implementando uma regra.

A função principal decide se o nome precisa ser abreviado.
Caso necessário, ela invoca uma função de cada vez,
até receber um nome com tamanho adequado.
Algumas ações podem ser aplicadas mais de uma vez,
como remover uma preposição ou abreviar parte do sobrenome.

Considere priorizar a aplicação das regras para minimizar as alterações no nome.
Por exemplo, abreviar JUNIOR para JR antes de abreviar MARIA para M.


### Nomes que não podem ser abreviados

Exemplo de nome que não pode ser abreviado pelas regras sugeridas acima:

```BELARMINONDAS FRANCISQUETTO (27 caracteres)
```

Neste caso, há duas opções:

* Levantar uma exceção para forçar uma solução manual.

* Abreviar o primeiro nome para uma letra inicial mas só depois de ter tentado outras regras.

Discuta com o grupo os prós e contras dessas opções.
Escolham uma, implemente os testes, e implemente a regra.


### Variante deste exercício

Uma variante possível e mais simples é um validador de senhas com diferentes regras.
Nesse caso, é importante considerar a boa prática de frases-senhas (passphrases),
para não impor regras que dificultem o uso delas.
