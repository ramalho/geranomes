# Encurtador de nomes para cartão de crédito

Este é um desafio para uso em coding dojos.

A existência de diferentes regras sugere uma solução
com uma função principal que aplica funções auxiliares,
cada uma delas implementando uma regra.

> **Nota**: Uma variante possível e mais simples é
um validador de senhas com diferentes regras.
Nesse caso, é importante considerar a boa prática
de frases-senhas (passphrases), para não impor regras
que dificultem o uso delas.

## Objetivo

Abreviar nomes de acordo com um conjunto de regras
para fazê-los caber em um campo de 26 posições em
um cartão de crédito.

## Comportamento esperado

* Se o nome tem 26 caracteres ou menos, devolver sem alteração.

* Se o nome tem mais de 26 caracteres, aplicar uma ou mais regras para encurtar.
Se não for possível encurtar, gerar uma mensagem de
erro incluindo o nome original completo para que o problema seja resolvido manualmente depois.

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

### Remover preposições

Remover preposições como DA, DAS, DE, DO, DOS.

Exemplo:

```
RODRIGO OLIVEIRA DOS SANTOS (27 caracteres)
RODRIGO OLIVEIRA SANTOS
```

### Abreviar parte do sobrenome

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

