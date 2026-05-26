import os
import sqlite3
from datetime import datetime

# Configurações de arquivos
BANCO_DADOS = "estoque_obra.db"

# ==========================================
# INICIALIZAÇÃO E LOG DO BANCO
# ==========================================
def inicializar_banco():
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    
    # Tabela de Estoque
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL, 
            quantidade INTEGER DEFAULT 0,
            unidade TEXT,       
            status TEXT,        
            responsavel TEXT    
        )
    """)
    
    # Tabela de Logs Blindada (SQLite define a data/hora do servidor)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            acao TEXT NOT NULL,
            data_hora DATETIME DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conexao.commit()
    conexao.close()

def registrar_log(usuario, acao):
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO logs_auditoria (usuario, acao) VALUES (?, ?)", (usuario, acao))
    conexao.commit()
    conexao.close()

# ==========================================
# CONTROLE DE ACESSO (QUATRO USUÁRIOS E PERFIS)
# ==========================================
USUARIOS = {
    "marcos": {"senha": "123", "perfil": "admin"},
    "compras": {"senha": "456", "perfil": "operario_entrada"},
    "joao": {"senha": "abc", "perfil": "operario_saida"},
    "fiscal": {"senha": "789", "perfil": "operario_devolucao"}  # Novo perfil focado em recebimento
}

def fazer_login():
    print("\n--- LOGIN DO SISTEMA ---")
    username = input("Usuário: ")
    senha = input("Senha: ")
    
    if username in USUARIOS and USUARIOS[username]["senha"] == senha:
        print(f"\nBem-vindo, {username}! Perfil: {USUARIOS[username]['perfil']}")
        registrar_log(username, "Fez login no sistema.")
        return {"nome": username, "perfil": USUARIOS[username]["perfil"]}
    print("❌ Usuário ou senha incorretos!")
    return None

# ==========================================
# FUNÇÕES DE NEGÓCIO
# ==========================================
def consultar_estoque(usuario_atual):
    print("\n=======================================================")
    print("                ESTOQUE ATUAL DA OBRA                  ")
    print("=======================================================")
    print(f"{'ID':<4} | {'Item':<25} | {'Tipo':<12} | {'Status/Qtd':<15}")
    print("-" * 65)
    
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, tipo, quantidade, unidade, status, responsavel FROM estoque")
    linhas = cursor.fetchall()
    
    if not linhas:
        print("O estoque está completamente vazio. Cadastre itens primeiro!")
    else:
        for linha in linhas:
            id_prod, nome, tipo, qtd, unidade, status, resp = linha
            if tipo == 'consumivel':
                info_status = f"{qtd} {unidade}"
            else:
                info_status = "Disponível" if status == "disponivel" else f"C/ {resp}"
                
            print(f"{id_prod:<4} | {nome:<25} | {tipo.capitalize():<12} | {info_status:<15}")
        
    print("=======================================================")
    conexao.close()
    registrar_log(usuario_atual, "Consultou o estoque atual.")

def cadastrar_novo_item(usuario_atual):
    print("\n--- CADASTRAR NOVO ITEM NO ESTOQUE ---")
    nome = input("Nome do material/ferramenta: ")
    tipo = input("Tipo (1 - Consumível / 2 - Ferramenta): ")
    
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    
    if tipo == "1":
        unidade = input("Unidade de medida (ex: sacos, un, metros): ")
        qtd_inicial = int(input("Quantidade inicial que está entrando: "))
        cursor.execute("""
            INSERT INTO estoque (nome, tipo, quantidade, unidade) 
            VALUES (?, 'consumivel', ?, ?)
        """, (nome, qtd_inicial, unidade))
        acao_log = f"Cadastrou o consumível '{nome}' com {qtd_inicial} {unidade}."
    else:
        cursor.execute("""
            INSERT INTO estoque (nome, tipo, status) 
            VALUES (?, 'ferramenta', 'disponivel')
        """, (nome,))
        acao_log = f"Cadastrou a ferramenta '{nome}' como disponível."
        
    conexao.commit()
    conexao.close()
    registrar_log(usuario_atual, acao_log)
    print(f"✔ '{nome}' cadastrado com sucesso!")

def dar_entrada_estoque(usuario_atual):
    print("\n--- DAR ENTRADA EM ITEM EXISTENTE (REABASTECIMENTO) ---")
    id_produto = input("Digite o ID do produto que deseja reabastecer: ")
    
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    
    cursor.execute("SELECT nome, tipo, quantidade, unidade FROM estoque WHERE id = ?", (id_produto,))
    produto = cursor.fetchone()
    
    if not produto:
        print("❌ Produto não encontrado!")
        conexao.close()
        return
        
    nome_prod, tipo_prod, qtd_atual, unidade = produto
    
    if tipo_prod == "ferramenta":
        print(f"ℹ O item '{nome_prod}' é uma ferramenta. Para novas unidades físicas, use a opção 'Cadastrar Novo Item'.")
        conexao.close()
        return
        
    qtd_entrada = int(input(f"Quantos {unidade} de '{nome_prod}' estão entrando? (Atual: {qtd_atual}): "))
    nova_qtd = qtd_atual + qtd_entrada
    
    cursor.execute("UPDATE estoque SET quantidade = ? WHERE id = ?", (nova_qtd, id_produto))
    conexao.commit()
    conexao.close()
    
    mensagem_log = f"Deu entrada em {qtd_entrada} {unidade} de '{nome_prod}' (ID {id_produto}). Novo saldo: {nova_qtd}."
    registrar_log(usuario_atual, mensagem_log)
    print(f"✔ Estoque reabastecido! Novo saldo de {nome_prod}: {nova_qtd} {unidade}.")

def dar_saida_material(usuario_atual):
    print("\n--- DAR SAÍDA / EMPRESTAR ITEM (por ID) ---")
    id_produto = input("Digite o ID do produto: ")
    
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, tipo, quantidade, status FROM estoque WHERE id = ?", (id_produto,))
    produto = cursor.fetchone()
    
    if not produto:
        print("❌ Produto não encontrado!")
        conexao.close()
        return

    nome_prod, tipo_prod, qtd_atual, status_atual = produto
    
    if tipo_prod == "consumivel":
        quantidade_retirada = int(input(f"Quantidade de '{nome_prod}' a retirar (Disponível: {qtd_atual}): "))
        if quantidade_retirada > qtd_atual:
            print("❌ Quantidade insuficiente em estoque!")
        else:
            nova_qtd = qtd_atual - quantidade_retirada
            cursor.execute("UPDATE estoque SET quantidade = ? WHERE id = ?", (nova_qtd, id_produto))
            conexao.commit()
            destino = input("Setor/Frente de obra de destino: ")
            mensagem_log = f"Retirou {quantidade_retirada} un de '{nome_prod}' (ID {id_produto}) para: {destino}."
            registrar_log(usuario_atual, mensagem_log)
            print("✔ Saída registrada com sucesso!")
            
    elif tipo_prod == "ferramenta":
        if status_atual == "emprestado":
            print("❌ Esta ferramenta já está emprestada!")
        else:
            operario = input("Nome do operário que está retirando a ferramenta: ")
            cursor.execute("UPDATE estoque SET status = 'emprestado', responsavel = ? WHERE id = ?", (operario, id_produto))
            conexao.commit()
            mensagem_log = f"Emprestou a ferramenta '{nome_prod}' (ID {id_produto}) para {operario}."
            registrar_log(usuario_atual, mensagem_log)
            print(f"✔ Ferramenta entregue para {operario}!")

    conexao.close()

def devolver_ferramenta(usuario_atual):
    print("\n--- DEVOLUÇÃO DE FERRAMENTA ---")
    id_produto = input("Digite o ID da ferramenta que está sendo devolvida: ")
    
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, tipo, status, responsavel FROM estoque WHERE id = ?", (id_produto,))
    produto = cursor.fetchone()
    
    if not produto or produto[1] != "ferramenta":
        print("❌ ID inválido ou o item não é uma ferramenta!")
        conexao.close()
        return
        
    nome_prod, _, status_atual, antigo_responsavel = produto
    
    if status_atual == "disponivel":
        print("ℹ Esta ferramenta já consta como disponível no estoque.")
    else:
        cursor.execute("UPDATE estoque SET status = 'disponivel', responsavel = NULL WHERE id = ?", (id_produto,))
        conexao.commit()
        mensagem_log = f"Recebeu a devolução da ferramenta '{nome_prod}' (ID {id_produto}) que estava com {antigo_responsavel}."
        registrar_log(usuario_atual, mensagem_log)
        print(f"✔ Ferramenta '{nome_prod}' devolvida com sucesso ao almoxarifado!")
        
    conexao.close()

def editar_nome_item(usuario_atual):
    print("\n--- EDITAR NOME DE UM ITEM (por ID) ---")
    id_produto = input("Digite o ID do item que deseja editar: ")
    
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    
    cursor.execute("SELECT nome FROM estoque WHERE id = ?", (id_produto,))
    produto = cursor.fetchone()
    
    if not produto:
        print("❌ Produto não encontrado!")
        conexao.close()
        return
        
    nome_antigo = produto[0]
    print(f"Nome atual: '{nome_antigo}'")
    
    novo_nome = input("Digite o NOVO nome para este item: ").strip()
    
    if not novo_nome:
        print("❌ O nome não pode ficar em branco!")
        conexao.close()
        return
        
    cursor.execute("UPDATE estoque SET nome = ? WHERE id = ?", (novo_nome, id_produto))
    conexao.commit()
    conexao.close()
    
    mensagem_log = f"Alterou o nome do item ID {id_produto} de '{nome_antigo}' para '{novo_nome}'."
    registrar_log(usuario_atual, mensagem_log)
    print(f"✔ Nome updated com sucesso para: '{novo_nome}'!")

def ver_historico_log(usuario_atual):
    print("\n--- HISTÓRICO DE LOGS (AUDITORIA NO BANCO) ---")
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()
    cursor.execute("SELECT data_hora, usuario, acao FROM logs_auditoria ORDER BY id ASC")
    linhas = cursor.fetchall()
    
    if not linhas:
        print("Nenhum histórico registrado.")
    else:
        for linha in linhas:
            data_hora, user, acao = linha
            print(f"[{data_hora}] Usuário: {user} | {acao}")
            
    conexao.close()
    registrar_log(usuario_atual, "Visualizou o histórico de logs de auditoria.")

# ==========================================
# MENUS INTERFACES (SEGREGAÇÃO DE FUNÇÕES COMPLETA)
# ==========================================
def menu_admin():
    print("\n--- MENU AUDITORIA (ADMINISTRADOR) ---")
    print("1. Consultar Estoque Atual")
    print("2. Editar Nome de um Item (Correção Cadastral)")
    print("3. Ver Histórico de Logs (Auditoria)")
    print("4. Sair")

def menu_operario_entrada():
    print("\n--- MENU ENTRADA DE MATERIAIS (COMPRAS) ---")
    print("1. Consultar Estoque Atual")
    print("2. Cadastrar Novo Item (Material ou Ferramenta)")
    print("3. Dar Entrada / Reabastecer Estoque (por ID)")
    print("4. Sair")

def menu_operario_saida():
    print("\n--- MENU SAÍDA DE MATERIAIS (ALMOXARIFADO) ---")
    print("1. Consultar Estoque Atual")
    print("2. Dar Saída de Material / Emprestar Ferramenta (por ID)")
    print("3. Sair")

def menu_operario_devolucao():
    print("\n--- MENU RECEBIMENTO / FISCALIZAÇÃO DE DEVOLUÇÕES ---")
    print("1. Consultar Estoque Atual")
    print("2. Registrar Devolução de Ferramenta (por ID)")
    print("3. Sair")

# ==========================================
# FLUXO PRINCIPAL DO SISTEMA
# ==========================================
def fluxo_principal():
    inicializar_banco()
    dados_usuario = None
    
    while not dados_usuario:
        dados_usuario = fazer_login()
        
    nome_usuario = dados_usuario["nome"]
    perfil = dados_usuario["perfil"]
    
    while True:
        if perfil == "admin":
            menu_admin()
            opcao = input("Escolha uma opção: ")
            if opcao == "1": consultar_estoque(nome_usuario)
            elif opcao == "2": editar_nome_item(nome_usuario)
            elif opcao == "3": ver_historico_log(nome_usuario)
            elif opcao == "4": break
            
        elif perfil == "operario_entrada":
            menu_operario_entrada()
            opcao = input("Escolha uma opção: ")
            if opcao == "1": consultar_estoque(nome_usuario)
            elif opcao == "2": cadastrar_novo_item(nome_usuario)
            elif opcao == "3": dar_entrada_estoque(nome_usuario)
            elif opcao == "4": break
            
        elif perfil == "operario_saida":
            menu_operario_saida()
            opcao = input("Escolha uma opção: ")
            if opcao == "1": consultar_estoque(nome_usuario)
            elif opcao == "2": dar_saida_material(nome_usuario)
            elif opcao == "3": break
            
        elif perfil == "operario_devolucao":
            menu_operario_devolucao()
            opcao = input("Escolha uma opção: ")
            if opcao == "1": consultar_estoque(nome_usuario)
            elif opcao == "2": devolver_ferramenta(nome_usuario)
            elif opcao == "3": break

if __name__ == "__main__":
    fluxo_principal()