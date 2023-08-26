# telegramBotSoccerTeam

### Created by @Azinth

# Telegram Bot for Soccer Matches

This repository contains the code for a Telegram bot designed to manage soccer matches. The bot is capable of handling user registration, maintaining a list of players, and managing the game schedule.

## Features

### User Registration
Users can register themselves using the `/cadastro` command. The bot will then add them to the list of registered users.

### Player List Management
The bot maintains a list of players for each match. Users can add themselves to the list using the `/adicionar` command. If the list of players is full, the user will be added to the list of substitutes.

### Game Schedule
The bot calculates the date of the next match and informs the players.

### Weather Forecast
The bot fetches the weather forecast for the day of the match and informs the players.

### Admin Functions
Admins have the ability to send general announcements, clear the player list, and ban users.

## Usage

To use the bot, you need to have a Telegram account. Once you have an account, you can interact with the bot using various commands. Here are some of the main commands:

- `/start`: Starts the bot.
- `/cadastro`: Registers the user.
- `/adicionar`: Adds the user to the player list.
- `/lista`: Shows the player list.
- `/remover`: Removes the user from the player list.
- `/regras`: Shows the rules of the game.

## Installation

To run the bot, you need to have Python installed on your machine. You also need to install the required Python packages which are listed in the `requirements.txt` file. You can install these packages using pip:

`pip install -r requirements.txt`

Once you have installed the required packages, you can run the bot using the following command:

`python bot.py`

Please note that you need to replace `'token'` in the `TOKEN` and `owm` variables with your actual Telegram bot token and OpenWeatherMap API key respectively.

## Contribution

Contributions are welcome! If you have any ideas or suggestions, feel free to open an issue or submit a pull request.

________________________________________________________________________________________________________________________________________________________________________________

# Bot do Telegram para Partidas de Futebol

Este repositório contém o código para um bot do Telegram projetado para gerenciar partidas de futebol. O bot é capaz de lidar com o registro de usuários, manter uma lista de jogadores e gerenciar a programação dos jogos.

## Recursos

### Registro de Usuários
Os usuários podem se registrar usando o comando `/cadastro`. O bot então os adicionará à lista de usuários registrados.

### Gerenciamento da Lista de Jogadores
O bot mantém uma lista de jogadores para cada partida. Os usuários podem se adicionar à lista usando o comando `/adicionar`. Se a lista de jogadores estiver cheia, o usuário será adicionado à lista de reservas.

### Programação dos Jogos
O bot calcula a data da próxima partida e informa os jogadores.

### Previsão do Tempo
O bot busca a previsão do tempo para o dia da partida e informa os jogadores.

### Funções de Administração
Os administradores têm a capacidade de enviar anúncios gerais, limpar a lista de jogadores e banir usuários.

## Uso

Para usar o bot, você precisa ter uma conta no Telegram. Uma vez que você tenha uma conta, você pode interagir com o bot usando vários comandos. Aqui estão alguns dos principais comandos:

- `/start`: Inicia o bot.
- `/cadastro`: Registra o usuário.
- `/adicionar`: Adiciona o usuário à lista de jogadores.
- `/lista`: Mostra a lista de jogadores.
- `/remover`: Remove o usuário da lista de jogadores.
- `/regras`: Mostra as regras do jogo.

## Instalação

Para executar o bot, você precisa ter Python instalado em sua máquina. Você também precisa instalar os pacotes Python necessários que estão listados no arquivo `requirements.txt`. Você pode instalar esses pacotes usando pip:
`pip install -r requirements.txtc`

luaDepois de instalar os pacotes necessários, você pode executar o bot usando o seguinte comando:
`python bot.py`

rubyPor favor, note que você precisa substituir `'token'` nas variáveis `TOKEN` e `owm` pelo seu token real do bot do Telegram e pela chave da API do OpenWeatherMap, respectivamente.

## Contribuição

Contribuições são bem-vindas! Se você tiver alguma ideia ou sugestão, sinta-se à vontade para abrir uma issue ou enviar um pull request.







