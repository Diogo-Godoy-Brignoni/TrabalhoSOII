# TrabalhoSOII

Integrantes do grupo:
 - Guilherme Witte Rambo, 203162
 - Diogo Godoy Brignoni, 201027

Esse é o nosso trabalho sobre Gerenciamento de Memória.
Implementamos os modelos de: "Alocação Contígua Dinâmica" e "Paginação Pura".

Escolhemos a linguagem python por questão de experiência com tal.
Decidimos representar os estados de alocação, com visualização ASCII tendo em mente simplicidade e legibilidade.

Como usar:
 - Rode o arquivo SO2.py
 - Ele irá simular 256KB de memória (262144 bytes)
 - Escolha um modelo dentre "Alocação Contígua Dinâmica" e "Paginação Pura"
 - Crie um novo processo e informe quantas bytes ele deve ter
 - Visualize no retorno como ficou a visualização do sistema após tal
 - Você também pode alterar o algoritmo para "first fit", "best fit", "worst fit" e "circular fit"
 - Os retornos no terminal contém as opções de preenchimento dentro de parênteses para fácil compreensão e uso simplificado
 - O terminal também irá informar uma legenda juntamente a visualização, facilitando a interpretação

Bibliotecas utilizadas:
 - dataclasses
 - typing
 - math
 - sys

Decisões de projetos:
 - Como pode observar no resto da descrição desse projeto, ele foi feito prezando a simplicidade e usabilidade
 - Sua interface é simples, minimalista e autoexplicativa
 - O código foi feito conforme preferência e costume dos programadores
 - A interface foi escolhida de acordo com a opção mais direta e rápida

Exemplo de uso:
 - rodar SO2.py
 - Selecionar "Alocação Contígua Dinâmica" inserindo "1" no terminal
 - Criando um processo inserindo "1" no terminal
 - Definindo o tamanho do processo inserindo "9999" no terminal
 - Entrando no modo de mudança de algoritmo inserindo "3" no terminal
 - Selecionando o algoritmo "circular" inserindo "circular" no terminal
 - Observar a alocação da memória de acordo com o espaço ocupado por "#" e por "." nesse exemplo
 - Durante o processo prestar atenção nas instruções e legendas do terminal para fácil interpretação do processo
