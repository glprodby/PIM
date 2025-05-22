# ===== IMPORTAÇÃO DE BIBLIOTECAS =====
import os
import hashlib
import datetime
import json
import statistics
import shutil

# ===== CONFIGURAÇÃO DE ARQUIVOS =====
ARQUIVO_USUARIOS = 'usuarios.json'
LOG_TENTATIVAS = 'log_tentativas.txt'
LOG_ACESSOS = 'log_acessos.txt'

# ===== LOGS DE SEGURANÇA =====
# Registra tentativas de login (sucesso ou falha)
def registrar_tentativa(email, sucesso):
    with open(LOG_TENTATIVAS, 'a') as log:
        horario = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'SUCESSO' if sucesso else 'FALHA'
        log.write(f'[{horario}] Tentativa de login - Email: {email} - Resultado: {status}\n')

# Registra quando o admin acessa a lista de usuários
def registrar_acesso(email_admin):
    with open(LOG_ACESSOS, 'a') as log:
        horario = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(f'[{horario}] Acesso à lista de usuários por: {email_admin}\n')

# ===== FUNÇÕES DE ARQUIVO =====
# Carrega os dados dos usuários
def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, 'r') as arquivo:
            return json.load(arquivo)
    return {}

# Salva os dados dos usuários e faz backup automático
def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, 'w') as arquivo:
        json.dump(usuarios, arquivo, indent=4)
    backup_usuarios()

# Cria uma cópia de segurança com data/hora
def backup_usuarios():
    data = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy(ARQUIVO_USUARIOS, f'backup_usuarios_{data}.json')

# Salva novo usuário com senha criptografada
def salvar_usuario(email, nome, idade, senha, tipo):
    usuarios = carregar_usuarios()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    usuarios[email] = {'nome': nome, 'idade': idade, 'senha': senha_hash, 'tipo': tipo, 'respostas': []}
    salvar_usuarios(usuarios)

# ===== VALIDAÇÃO DE SENHA =====
# Confere se a senha tem letra maiúscula, número e 6+ caracteres
def senha_forte(senha):
    return len(senha) >= 6 and any(c.isupper() for c in senha) and any(c.isdigit() for c in senha)

# ===== ESTATÍSTICAS =====
# Mostra média, moda e mediana de idades e acertos
def calcular_estatisticas():
    usuarios = carregar_usuarios()
    if not usuarios:
        print('\nNenhum usuário cadastrado para análise.\n')
        return

    idades = [dados['idade'] for dados in usuarios.values()]
    idade_media = round(statistics.mean(idades))
    idade_moda = statistics.mode(idades)
    idade_mediana = statistics.median(idades)

    print('\n=== Estatísticas de Idade dos Usuários ===')
    print(f'Idade média: {idade_media} anos')
    print(f'Moda das idades: {idade_moda} anos')
    print(f'Mediana das idades: {idade_mediana} anos')

    print('\n=== Estatísticas de Acertos no Questionário ===')
    gabarito = ['C', 'B', 'B', 'C', 'B']
    acertos_gerais = []
    for dados in usuarios.values():
        respostas = dados.get('respostas', [])
        if len(respostas) == len(gabarito):
            acertos = sum([1 for i, r in enumerate(respostas) if r.upper() == gabarito[i]])
            acertos_gerais.append(acertos)

    if acertos_gerais:
        media = round(statistics.mean(acertos_gerais), 2)
        moda = statistics.mode(acertos_gerais)
        mediana = statistics.median(acertos_gerais)
        print(f'Média de acertos: {media}')
        print(f'Moda dos acertos: {moda}')
        print(f'Mediana dos acertos: {mediana}')
    else:
        print('Nenhum questionário respondido até o momento.')

# ===== LGPD - ANONIMIZAÇÃO DE EMAIL =====
def anonimizar_email(email):
    nome, dominio = email.split('@')
    return nome[:2] + '***@' + dominio

# ===== SOBRE O SISTEMA =====
# Mostra texto sobre objetivo e segurança
def sobre():
    print('''
=== Sobre o Sistema ===
Este sistema promove a inclusão digital e ensina programação básica e
cibersegurança, respeitando a LGPD. Os dados são criptografados, acessos
são registrados, e backups automáticos são feitos para proteger as informações.
''')

# ===== CADASTRO DE USUÁRIO =====
# Valida nome, idade, email e senha, depois salva
def cadastrar():
    usuarios = carregar_usuarios()
    nome = input('\nDigite seu nome: ')
    if any(c in nome for c in '<>"\''):
        print('Nome inválido.')
        return
    try:
        idade = int(input('Digite sua idade: '))
    except ValueError:
        print('Idade inválida.')
        return
    if idade <= 17:
        print('\nVocê não tem idade suficiente.\n')
        return
    while True:
        email = input('Digite seu email: ').strip()
        if '@' in email and '.' in email:
            if email in usuarios:
                print('Esse e-mail já está cadastrado. Tente outro.')
            else:
                break
        else:
            print('Email inválido. Tente novamente.')
    while True:
        senha = input('Digite sua senha (mínimo 6 caracteres, 1 letra maiúscula e 1 número): ')
        if senha_forte(senha):
            break
        else:
            print('Senha fraca. Tente novamente.')
    tipo = input('Digite o tipo de usuário (admin/aluno): ').strip().lower()
    if tipo not in ['admin', 'aluno']:
        print('Tipo inválido! Padrão definido como "aluno".')
        tipo = 'aluno'
    salvar_usuario(email, nome, idade, senha, tipo)
    print('\nCadastro realizado com sucesso!')

# ===== LOGIN =====
# Confirma usuário e senha, registra sucesso/falha
def login():
    usuarios = carregar_usuarios()
    email = input('\nDigite seu email: ').strip()
    senha = input('Digite sua senha: ')
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    if email in usuarios and usuarios[email]['senha'] == senha_hash:
        registrar_tentativa(email, True)
        print(f'\nBem-vindo(a), {usuarios[email]["nome"]}!')
        return email, usuarios[email]['tipo']
    else:
        registrar_tentativa(email, False)
        print('\nEmail ou senha incorretos.')
        return None, None

# ===== LISTAGEM DE USUÁRIOS (APENAS ADMIN) =====
def listar_usuarios(admin_email):
    registrar_acesso(admin_email)
    usuarios = carregar_usuarios()
    print('\n=== Lista de Usuários (uso interno apenas) ===')
    for email, dados in usuarios.items():
        print(f'Nome: {dados["nome"]}, Email: {anonimizar_email(email)}, Idade: {dados["idade"]}, Tipo: {dados["tipo"]}')

# ===== QUESTIONÁRIO =====
def responder_questionario(email):
    usuarios = carregar_usuarios()
    print('\n=== Questionário ===')
    print('Digite 1 para começar ou 2 para voltar.')
    escolha = input('Escolha: ')
    if escolha != '1':
        return
    perguntas = [
        {"pergunta": "1. Qual das opções é um exemplo de boa prática de segurança digital?",
         "opcoes": {"A": "Compartilhar senhas com colegas", "B": "Usar a mesma senha em todos os sites",
                    "C": "Criar senhas fortes e únicas", "D": "Deixar senhas anotadas no computador"}, "correta": "C"},
        {"pergunta": "2. O que significa LGPD?",
         "opcoes": {"A": "Lei Geral de Programação Digital", "B": "Lei Geral de Proteção de Dados",
                    "C": "Lista Geral de Propriedade de Dados", "D": "Lei de Garantia da Privacidade Digital"},
         "correta": "B"},
        {"pergunta": "3. Qual dos itens abaixo é um exemplo de phishing?",
         "opcoes": {"A": "Atualização do antivírus", "B": "E-mail falso pedindo dados pessoais",
                    "C": "Uso de autenticação em dois fatores", "D": "Download de software oficial"},
         "correta": "B"},
        {"pergunta": "4. Qual extensão é mais comum para arquivos executáveis no Windows?",
         "opcoes": {"A": ".docx", "B": ".jpg", "C": ".exe", "D": ".mp3"}, "correta": "C"},
        {"pergunta": "5. Qual comando Python é usado para repetir algo várias vezes?",
         "opcoes": {"A": "if", "B": "while", "C": "print", "D": "def"}, "correta": "B"}
    ]
    respostas = []
    acertos = 0
    for item in perguntas:
        print("\n" + item["pergunta"])
        for letra, texto in item["opcoes"].items():
            print(f'{letra}) {texto}')
        while True:
            resp = input('Sua resposta: ').strip().upper()
            if resp in item["opcoes"]:
                respostas.append(resp)
                if resp == item["correta"]:
                    acertos += 1
                break
            else:
                print('Opção inválida. Digite apenas A, B, C ou D.')

    usuarios[email]['respostas'] = respostas
    salvar_usuarios(usuarios)
    print('\nObrigado por responder ao questionário!')
    print(f'Você acertou {acertos} de {len(perguntas)} perguntas.')

# ===== MENU PRINCIPAL =====
def menu():
    while True:
        print('\n=== Bem-vindo(a)! ===')
        print('1 - Cadastrar')
        print('2 - Login')
        print('3 - Sobre o Sistema')
        print('4 - Sair')
        opcao = input('\nEscolha uma opção: ')
        if opcao == '1':
            cadastrar()
        elif opcao == '2':
            email_logado, tipo_logado = login()
            if email_logado:
                if tipo_logado == 'admin':
                    while True:
                        print('\n===== Menu do Administrador =====')
                        print('1 - Listar usuários')
                        print('2 - Estatísticas')
                        print('3 - Questionário')
                        print('4 - Sair do Admin')
                        escolha = input('Escolha uma opção: ')
                        if escolha == '1':
                            listar_usuarios(email_logado)
                        elif escolha == '2':
                            calcular_estatisticas()
                        elif escolha == '3':
                            responder_questionario(email_logado)
                        elif escolha == '4':
                            break
                        else:
                            print('Opção inválida.')
                elif tipo_logado == 'aluno':
                    while True:
                        print('\n===== Menu do Aluno =====')
                        print('1 - Estatísticas')
                        print('2 - Questionário')
                        print('3 - Sair do Aluno')
                        escolha = input('Escolha uma opção: ')
                        if escolha == '1':
                            calcular_estatisticas()
                        elif escolha == '2':
                            responder_questionario(email_logado)
                        elif escolha == '3':
                            break
                        else:
                            print('Opção inválida.')
        elif opcao == '3':
            sobre()
        elif opcao == '4':
            print('\nAté mais...')
            break
        else:
            print('Opção inválida.')

menu()

# FIM