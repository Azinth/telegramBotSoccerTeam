import telegram
import csv
import datetime
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from pyowm import OWM
from datetime import datetime, timedelta, time

TOKEN = 'token'
owm = OWM('token')
mgr = owm.weather_manager()

bot = telegram.Bot(token=TOKEN)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Bem-vindo ao bot do Racha Top da Areninha! Use o comando /cadastro para se cadastrar. Esse bot foi criado por @gsvhasura.')

def usuario_banido(chat_id):
    with open('banidos.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Check if the row is not empty
            if row:
                # Print the row for debugging
                print(f"Row: {row}")
                # Compare the chat_id with the first element of the row
                if row[0].strip() == str(chat_id):
                    print(f"User {chat_id} is banned.")
                    return True
    print(f"User {chat_id} is not banned.")
    return False

def cadastro(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    nome = obter_nome_usuario(chat_id)

    if usuario_banido(chat_id):
        context.bot.send_message(chat_id=chat_id, text=f"{user} você está banido do racha.")
        return
    # Verificar se o usuário já está cadastrado
    if usuario_cadastrado(chat_id):
        context.bot.send_message(chat_id=chat_id, text=f"{nome}, você já está cadastrado!")
        return

    # Verificar se o nome do usuário já existe
    if nome_usuario_existe(nome):
        context.bot.send_message(chat_id=chat_id, text="Esse nome de usuário já existe. Por favor, escolha outro nome.")
        return

    # Perguntar o nome do usuário
    context.bot.send_message(chat_id=chat_id, text="Por favor, digite o nome com o qual você quer ser cadastrado:")
    return 'nome'

def nome(update, context):
    chat_id = update.message.chat_id
    nome = update.message.text

    context.user_data['nome'] = nome

    context.bot.send_message(chat_id=chat_id, text="Olá, {}! você está pronto para adicionar seu nome na lista e rachar com a gente! digite /adicionar para colocar seu nome na lista do próximo domingo 😎🥅⚽️".format(nome))
    registrar_usuario(chat_id, nome)
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Tudo bem! Obrigado por usar o bot. Até a próxima!',reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def registrar_usuario(chat_id, nome):
    with open('usuarios_cadastrados.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([chat_id, nome])
        
    limpar_linhas_em_branco('usuarios_cadastrados.csv')

def limpar_linhas_em_branco(nome_arquivo):
    with open(nome_arquivo, 'r') as file:
        linhas = file.readlines()

    linhas = [linha for linha in linhas if linha.strip()]

    with open(nome_arquivo, 'w') as file:
        file.writelines(linhas)

# def proximo_domingo():
#     hoje = datetime.today()
#     proximo_domingo = hoje + timedelta((6-hoje.weekday()) % 7)
#     return proximo_domingo.strftime("%d/%m/%Y")
def proximo_domingo():
    hoje = datetime.today()
    dias_ate_domingo = (6-hoje.weekday()) % 7
    dias_ate_domingo = 7 if dias_ate_domingo == 0 else dias_ate_domingo
    proximo_domingo = hoje + timedelta(dias_ate_domingo)
    return proximo_domingo.strftime("%d/%m/%y")

def remover_linhas_em_branco(nome_arquivo):
    with open(nome_arquivo, 'r') as file:
        linhas = file.readlines()

    linhas = [linha for linha in linhas if linha.strip()]

    with open(nome_arquivo, 'w') as file:
        file.writelines(linhas)

def mover_suplente_para_titular():
    with open('suplentes.csv', 'r') as file:
        linhas = file.readlines()

    if not linhas:
        return

    primeiro_suplente = linhas[0]
    del linhas[0]

    with open('suplentes.csv', 'w') as file:
        file.writelines(linhas)

    # Abra o arquivo no modo de leitura para verificar a última linha
    with open('titulares.csv', 'r') as file:
        ultima_linha = file.readlines()[-1]

    with open('titulares.csv', 'a') as file:
        # Verifique se a última linha do arquivo termina com uma quebra de linha
        if not ultima_linha.endswith('\n'):
            file.write('\n')
        file.write(primeiro_suplente.strip() + '\n')

    remover_linhas_em_branco('suplentes.csv')
    remover_linhas_em_branco('titulares.csv')

def lista(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user

    if not usuario_cadastrado(chat_id):
        context.bot.send_message(chat_id=chat_id, text="Você precisa se cadastrar primeiro usando o comando /cadastro.")
        return

    titulares = obter_lista_titulares()
    suplentes = obter_lista_suplentes()
    goleiros = obter_lista_goleiros()

    context.bot.send_message(chat_id=chat_id, text=f"Lista de Domingo data: {proximo_domingo()}")

    if titulares:
        context.bot.send_message(chat_id=chat_id, text="Lista de Titulares:")
        context.bot.send_message(chat_id=chat_id, text="\n".join(f"{i+1}. {nome}" for i, nome in enumerate(titulares)))
    else:
        context.bot.send_message(chat_id=chat_id, text="A lista de titulares está vazia.")

    if suplentes:
        context.bot.send_message(chat_id=chat_id, text="Lista de Suplentes:")
        context.bot.send_message(chat_id=chat_id, text="\n".join(f"{i+1}. {nome}" for i, nome in enumerate(suplentes)))
    else:
        context.bot.send_message(chat_id=chat_id, text="A lista de suplentes está vazia.")
    
    if goleiros:
        context.bot.send_message(chat_id=chat_id, text="Lista de Goleiros:")
        context.bot.send_message(chat_id=chat_id, text="\n".join(f"{i+1}. {nome}" for i, nome in enumerate(goleiros)))
    else:
        context.bot.send_message(chat_id=chat_id, text="A lista de goleiros está vazia.")

def remover(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user

    if not usuario_cadastrado(chat_id):
        context.bot.send_message(chat_id=chat_id, text="Você precisa se cadastrar primeiro usando o comando /cadastro.")
        return ConversationHandler.END

    context.bot.send_message(chat_id=chat_id, text="Você deseja remover seu nome da lista? (sim ou não)")
    return 'remover'

def usuario_cadastrado(chat_id):
    with open('usuarios_cadastrados.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Check if the row is not empty
            if row:
                # Print the row for debugging
                print(f"Row: {row}")
                # Compare the chat_id with the first element of the row
                if row[0].strip() == str(chat_id):
                    print(f"User {chat_id} is registered.")
                    return True
    print(f"User {chat_id} is not registered.")
    return False

def usuario_na_lista(chat_id):
    with open('titulares.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(chat_id):
                return True

    with open('suplentes.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(chat_id):
                return True
    with open('goleiros.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(chat_id):
                return True

    return False

def adicionar_jogador_titular(chat_id):
    with open('titulares.csv', 'r') as file:
        if len(file.readlines()) >= 27:
            return False

    nome = obter_nome_usuario(chat_id)  # Buscar o nome do usuário

    with open('titulares.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([chat_id, nome])  # Aqui você escreve o nome no arquivo CSV

    return True

def obter_nome_usuario(chat_id):
    with open('usuarios_cadastrados.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # Check if the row is not empty
                if row[0] == str(chat_id):
                    return row[1]  # Retorna o nome do usuário
    return None

def obter_lista_titulares():
    with open('titulares.csv', 'r') as file:
        reader = csv.reader(file)
        return [f"{row[1]}" for i, row in enumerate(reader) if row]  # Aqui você lê o nome

def obter_lista_titulares_com_chat_id():
    with open('titulares.csv', 'r') as file:
        reader = csv.reader(file)
        return [row for i, row in enumerate(reader) if row]  # Aqui você lê o nome

def obter_lista_suplentes():
    with open('suplentes.csv', 'r') as file:
        reader = csv.reader(file)
        return [f"{row[1]}" for i, row in enumerate(reader) if row]  # Aqui você lê o nome
def obter_lista_goleiros():
    with open('goleiros.csv', 'r') as file:
        reader = csv.reader(file)
        return [f"{row[1]}" for i, row in enumerate(reader) if row]  # Aqui você lê o nome
def obter_lista_goleiros_com_chat_id():
    with open('goleiros.csv', 'r') as file:
        reader = csv.reader(file)
        return [row for i, row in enumerate(reader) if row]  # Aqui você lê o nome

def obter_lista_suplentes_com_chat_id():
    with open('suplentes.csv', 'r') as file:
        reader = csv.reader(file)
        return [row for i, row in enumerate(reader) if row]  # Aqui você lê o nome

def send_list_definitiva(context: telegram.ext.CallbackContext):
    usuarios_cadastrados = obter_usuarios_cadastrados()

    with open('lista_definitiva.txt', 'w') as file:
        file.write(f"Lista Definitiva {proximo_domingo()}:\n\n")
        file.write("Lista de Titulares:\n")
        # Adicione a numeração usando enumerate
        file.write("\n".join(f"{i+1}. {nome}" for i, nome in enumerate(obter_lista_titulares())))
        file.write("\n\nLista de Suplentes:\n")
        # Adicione a numeração usando enumerate
        file.write("\n".join(f"{i+1}. {nome}" for i, nome in enumerate(obter_lista_suplentes())))
        file.write("\n\nLista de Goleiros:\n")
        # Adicione a numeração usando enumerate
        file.write("\n".join(f"{i+1}. {nome}" for i, nome in enumerate(obter_lista_goleiros())))

    for user in usuarios_cadastrados:
        chat_id = user[0]  # Aqui você acessa o chat_id como o primeiro elemento da lista
        file_path = 'lista_definitiva.txt'
        context.bot.send_message(chat_id=chat_id, text=f"Lista Definitiva de Domingo data: {proximo_domingo()}")
        context.bot.send_document(chat_id=chat_id, document=open(file_path, 'rb'))
        
def aviso_geral(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    nome = obter_nome_usuario(chat_id)  # Obter o nome que o usuário quer ser chamado

    if not is_admin(chat_id):
        context.bot.send_message(chat_id=chat_id, text="Você não tem permissão para enviar avisos gerais.")
        return

    usuarios_cadastrados = obter_usuarios_cadastrados()

    for user in usuarios_cadastrados:
        chat_id = user[0]  # Aqui você acessa o chat_id como o primeiro elemento da lista
        context.bot.send_message(chat_id=chat_id, text="⚠ Aviso Geral: \n" + update.message.text[13:])

def regras(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    nome = obter_nome_usuario(chat_id)  # Obter o nome que o usuário quer ser chamado
    context.bot.send_message(chat_id=chat_id, text = ("Regras do racha TOP\n0️⃣1️⃣- A lista do racha será montada a partir da sequência em que os jogadores de linha e os goleiros  digitem o nome após o lançamento da bolinha às 13h00 do domingo.\n0️⃣2️⃣- Os jogadores de linha só receberão o colete após a entrega de uma contribuição no valor de 5,00 para a manutenção do racha. \n0️⃣3️⃣- A chamada para o racha começa às 06h40 e será feita por ordem dos times 01, 02 e 03, sendo que às 06h51 começa a chamada dos suplentes.\n0️⃣4️⃣- O sorteio dos times será realizado no sábado por volta das 22h00, sendo que quem não retirar o nome da lista e não comparecer ao racha no domingo, será punido com um domingo de suspensão. Vale ressaltar que, só será punido no domingo em que botar o nome na lista novamente, caso contrário ficará devendo a punição até conseguir botar o nome na lista.\n0️⃣5️⃣- Será removido do grupo e do racha, quem deixar de botar o nome na lista por mais de 3 meses ou cometer alguma indisciplina grave com qualquer um do grupo. \n0️⃣6️⃣- Quem enganchar a bola nas casas deve tentar recuperar. Caso não consiga deve pagar uma multa de 20,00 para que possamos  pagar uma recompensa a quem conseguir recuperar a bola.\n0️⃣7️⃣- O racha top é filmado, sendo que quem botar o nome na lista estará autorizando a divulgação de sua imagem nas mídias sociais do racha via internet.\n0️⃣8️⃣- Serão utilizadas regras de futebol na medida do possível, devendo os jogadores respeitarem os critérios e decisões dos árbitros que são amadores.\n0️⃣9️⃣- No último racha do ano, teremos uma confraternização com troféus e medalhas além de um momento de descontração com música, bebidas e refrigerantes, gastos com o dinheiro do próprio racha. Vale ressaltar que serão 4 times no formato mata-mata, sorteados em aplicativo.\n1️⃣0️⃣- O sucesso do nosso racha depende da colaboração de todos. Vale ressaltar que os administradores do racha  têm a regalia de não precisar digitar o nome para formar a lista."))
    
    
def aviso_lista(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    nome = obter_nome_usuario(chat_id)  # Obter o nome que o usuário quer ser chamado

    if not is_admin(chat_id):
        context.bot.send_message(chat_id=chat_id, text="Você não tem permissão para enviar avisos para quem está na lista.")
        return

    titulares = obter_lista_titulares()
    suplentes = obter_lista_suplentes()
    goleiros = obter_lista_goleiros()
    
    for user in titulares:
        chat_id = user[0]  # Aqui você acessa o chat_id como o primeiro elemento da lista
        context.bot.send_message(chat_id=chat_id, text="⚠ Aviso para quem está na lista: \n" + update.message.text[13:])
    for user in suplentes:
        chat_id = user[0]
        context.bot.send_message(chat_id=chat_id, text="⚠ Aviso para quem está na lista: \n" + update.message.text[13:])
    for user in goleiros:
        chat_id = user[0]
        context.bot.send_message(chat_id=chat_id, text="⚠ Aviso para quem está na lista: \n" + update.message.text[13:])

def is_admin(chat_id):
    with open('administrador.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Check if the row is not empty
            if row:
                # Print the row for debugging
                print(f"Row: {row}")
                # Compare the chat_id with the first element of the row
                if row[0].strip() == str(chat_id):
                    print(f"User {chat_id} is adm.")
                    return True
    print(f"User {chat_id} is not adm.")
    return False
        
def adicionar(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    nome = obter_nome_usuario(chat_id)  # Obter o nome que o usuário quer ser chamado

    if not usuario_cadastrado(chat_id):
        context.bot.send_message(chat_id=chat_id, text="Você precisa se cadastrar primeiro usando o comando /cadastro.")
        return

    if usuario_na_lista(chat_id):
        context.bot.send_message(chat_id=chat_id, text=f"{nome}, você está já está na lista! \ndigite /lista para conferir.")
        
        return

    if adicionar_jogador_titular(chat_id):
        context.bot.send_message(chat_id=chat_id, text=f"Pronto {nome}! Você foi adicionado na lista de titulares! \ndigite /lista para conferir.")
    else:
        adicionar_jogador_suplente(chat_id)
        context.bot.send_message(chat_id=chat_id, text="A lista de titulares já está completa. Você foi adicionado na lista de suplentes! \ndigite /lista para conferir.")

def obter_usuarios_cadastrados():
    with open('usuarios_cadastrados.csv', 'r') as file:
        reader = csv.reader(file)
        return [row for row in reader]
    
def adicionar_jogador_suplente(chat_id):
    with open('suplentes.csv', 'r') as file:
        if len(file.readlines()) >= 27:
            return False

    nome = obter_nome_usuario(chat_id)  # Buscar o nome do usuário

    with open('suplentes.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([chat_id, nome])  # Aqui você escreve o nome no arquivo CSV

    return True

def adicionar_goleiro_lista(chat_id):
    with open('goleiros.csv', 'r') as file:
        if len(file.readlines()) >= 4:
            return False

    nome = obter_nome_usuario(chat_id)  # Buscar o nome do usuário

    with open('goleiros.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([chat_id, nome])  # Aqui você escreve o nome no arquivo CSV

    return True

def adicionar_goleiro(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    nome = obter_nome_usuario(chat_id)  # Obter o nome que o usuário quer ser chamado

    if not usuario_cadastrado(chat_id):
        context.bot.send_message(chat_id=chat_id, text="Você precisa se cadastrar primeiro usando o comando /cadastro.")
        return

    if usuario_na_lista(chat_id):
        context.bot.send_message(chat_id=chat_id, text=f"{nome}, você está já está na lista! \ndigite /lista para conferir.")
        return

    if adicionar_goleiro_lista(chat_id):
        context.bot.send_message(chat_id=chat_id, text="Você foi adicionado na lista de goleiros! \ndigite /lista para conferir.")
    else:
        context.bot.send_message(chat_id=chat_id, text="A lista de goleiros já está completa! Mas você pode ir para revezar com os goleiros no dia!")


def nome_usuario_existe(nome):
    with open('usuarios_cadastrados.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Ignore empty lines
            if not row:
                continue
            # Check if the user's name exists in the file
            if row[1] == nome:
                return True
    return False

def zerar_listas(context: telegram.ext.CallbackContext):
    open('titulares.csv', 'w').close()
    open('suplentes.csv', 'w').close()
    open('goleiros.csv', 'w').close()

    usuarios_cadastrados = obter_usuarios_cadastrados()
    for user in usuarios_cadastrados:
        chat_id = user[0]
        context.bot.send_message(chat_id=chat_id, text="13h Listas zeradas!")
        context.bot.send_message(chat_id=chat_id, text="⚽")
def remover_resposta(update, context):
    chat_id = update.message.chat_id
    resposta = update.message.text.lower()

    if resposta == 'sim':
        remover_usuario(chat_id)
        context.bot.send_message(chat_id=chat_id, text="Seu nome foi removido da lista! 😉")
        context.bot.send_message(chat_id=chat_id, text="Se mudar de ideia, use o comando /adicionar para adicionar seu nome novamente.")
        return ConversationHandler.END
    elif resposta == 'não':
        context.bot.send_message(chat_id=chat_id, text="Ok, seu nome permanecerá na lista. 👍")
        return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=chat_id, text="Resposta inválida. Por favor, responda com 'sim' ou 'não'.")
        return 'remover'

def remover_usuario(chat_id):
    remover_usuario_da_lista(chat_id, 'titulares.csv')
    mover_suplente_para_titular()
    remover_usuario_da_lista(chat_id, 'suplentes.csv')
    remover_usuario_da_lista(chat_id, 'goleiros.csv')

def remover_usuario_da_lista(chat_id, nome_arquivo):
    with open(nome_arquivo, 'r') as file:
        linhas = file.readlines()

    linhas = [linha for linha in linhas if linha.strip().split(',')[0] != str(chat_id)]

    with open(nome_arquivo, 'w') as file:
        file.writelines(linhas)

    with open(nome_arquivo, 'w') as file:
        for linha in linhas:
            if linha.strip().split(',')[0] != str(chat_id):
                file.write(linha)


def send_weather_forecast(context: telegram.ext.CallbackContext):
    usuarios_cadastrados = obter_usuarios_cadastrados()
    titulares = obter_lista_titulares_com_chat_id()
    suplentes = obter_lista_suplentes_com_chat_id()
    goleiros = obter_lista_goleiros_com_chat_id()

    # Obtenha a previsão do tempo para o próximo domingo
    forecast = mgr.forecast_at_place('Juazeiro do Norte,BR', '3h')
    weather_list = forecast.forecast.weathers

    # Encontre a previsão do tempo para o próximo domingo
    for weather in weather_list:
        # if weather.reference_time('date').date() == proximo_domingo.date():
        
        temperature = weather.temperature('celsius')['temp']
        humidity = weather.humidity
        status = weather.detailed_status
        break
            
    translations = {
        'clear sky': 'céu limpo',
        'few clouds': 'poucas nuvens',
        'scattered clouds': 'nuvens dispersas',
        'broken clouds': 'nuvens quebradas',
        'shower rain': 'chuva de banho',
        'rain': 'chuva',
        'thunderstorm': 'trovão',
        'snow': 'neve',
        'mist': 'névoa'
        }
    status_pt = translations.get(status, status)

    for user in titulares:
        chat_id = user[0]
        nome = user[1]
        context.bot.send_message(chat_id=chat_id, text=f"Bom dia {nome}! O racha começa em 1 hora.\nA previsão do tempo agora é:\nTemperatura: {temperature}°C, Tempo: {status_pt}, {humidity}% de umidade\n \n Cuida! 🏃‍♂️💨 " )
    for user in suplentes:
        chat_id = user[0]
        nome = user[1]
        context.bot.send_message(chat_id=chat_id, text=f"Bom dia {nome}! O racha começa em 1 hora.\nA previsão do tempo agora é:\nTemperatura: {temperature}°C, Tempo: {status_pt}, {humidity}% de umidade\n \n Cuida! 🏃‍♂️💨 " )
    for user in goleiros:
        chat_id = user[0]
        nome = user[1]
        context.bot.send_message(chat_id=chat_id, text=f"Bom dia {nome}! O racha começa em 1 hora.\nA previsão do tempo agora é:\nTemperatura: {temperature}°C, Tempo: {status_pt}, {humidity}% de umidade\n \n Cuida! 🏃‍♂️💨 " )
def remove_user_from_list(name, list_file):
    with open(list_file, 'r') as file:
        lines = file.readlines()

    with open(list_file, 'w') as file:
        for line in lines:
            if line.strip() != name:
                file.write(line)

def admin_remove_user(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    name_to_remove = ' '.join(context.args)

    if is_admin(chat_id):
        remove_user_from_list(name_to_remove, 'titulares.csv')
        remove_user_from_list(name_to_remove, 'suplentes.csv')
        remove_user_from_list(name_to_remove, 'goleiros.csv')
        context.bot.send_message(chat_id=chat_id, text=f"O jogador {name_to_remove} foi removido da lista.")
    else:
        context.bot.send_message(chat_id=chat_id, text="Desculpe! Você não é administrador.")
def adicionar_banido(nome):
    chat_id = obter_id_usuario(nome)  # Buscar o nome do usuário
    
    with open('banidos.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([chat_id, nome])  # Aqui você escreve o nome no arquivo CSV
    
def obter_id_usuario(nome):
    with open('usuarios_cadastrados.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Ignore empty lines
            if not row:
                continue
            # Check if the user's name exists in the file
            if row[1] == nome:
                return row[0]
    return None

def admin_ban_user(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    name_to_remove = ' '.join(context.args)

    if is_admin(chat_id):
        if nome_usuario_existe(name_to_remove):
            remove_user_from_list(name_to_remove, 'usuarios_cadastrados.csv')
            adicionar_banido(name_to_remove)
            context.bot.send_message(chat_id=chat_id, text=f"O jogador {name_to_remove} foi banido do racha.")
    else:
        context.bot.send_message(chat_id=chat_id, text="Desculpe! Você não é administrador.")
        
def admin_ban(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    name_to_ban = ' '.join(context.args)

    if is_admin(chat_id):
        adicionar_banido(name_to_ban)
        context.bot.send_message(chat_id=chat_id, text=f"O usuário {name_to_ban} foi banido.")
    else:
        context.bot.send_message(chat_id=chat_id, text="Desculpe! Você não é administrador.")


# def schedule_tasks():
#     job_queue = updater.job_queue

#     # Altere o horário para 22:25
#     job_queue.run_daily(send_list_definitiva, time(14, 54, 0), days=(1,), context=bot)
#     job_queue.run_daily(zerar_listas, time(14, 56, 0), days=(1,), context=bot)
#     job_queue.run_daily(send_weather_forecast, time(14, 55, 0), days=(1,), context=bot)

def schedule_tasks():
    job_queue = updater.job_queue

    # Sábado às 22h em Brasília é Domingo às 01h em UTC
    job_queue.run_daily(send_list_definitiva, time(1, 0, 0), days=(6,), context=bot)

    # Domingo às 6h em Brasília é Domingo às 9h em UTC
    job_queue.run_daily(send_weather_forecast, time(9, 0, 0), days=(6,), context=bot)

    # Domingo às 13h em Brasília é Domingo às 16h em UTC
    job_queue.run_daily(zerar_listas, time(16, 0, 0), days=(6,), context=bot)

    
    

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
dispatcher.add_handler(ConversationHandler(
    entry_points=[CommandHandler('cadastro', cadastro), CommandHandler('remover', remover)],
    states={
        'nome': [MessageHandler(Filters.text, nome)],
        'remover': [MessageHandler(Filters.text, remover_resposta)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
))
dispatcher.add_handler(CommandHandler("lista", lista))
dispatcher.add_handler(CommandHandler("adicionar", adicionar))
dispatcher.add_handler(CommandHandler("adicionar_goleiro", adicionar_goleiro))
dispatcher.add_handler(CommandHandler("aviso_geral", aviso_geral))
dispatcher.add_handler(CommandHandler("aviso_lista", aviso_lista))
dispatcher.add_handler(CommandHandler("regras", regras))
dispatcher.add_handler(CommandHandler('admin_remove_user', admin_remove_user))


dispatcher.add_handler(start_handler)

schedule_tasks()

updater.start_polling()
updater.idle()