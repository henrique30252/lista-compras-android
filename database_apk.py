import sqlite3

# Importa funções da lixeira
from database_lixeira import (
    criar_tabelas_lixeira_apk, inserir_item_lixeira_apk, listar_itens_lixeira_apk,
    restaurar_item_lixeira_apk, excluir_definitivamente_lixeira_apk,
    limpar_lixeira_completa_apk, manutencao_lixeira_apk
)

DB_NAME = "compras.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def migrar_tabela_carrinhos_status():
    """Adiciona colunas de status de finalização à tabela carrinhos se não existirem"""
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Verifica se as colunas já existem
        cursor.execute("PRAGMA table_info(carrinhos)")
        colunas = [coluna[1] for coluna in cursor.fetchall()]
        
        if 'finalizado' not in colunas:
            cursor.execute("ALTER TABLE carrinhos ADD COLUMN finalizado INTEGER DEFAULT 0")
            print("Coluna 'finalizado' adicionada à tabela carrinhos")
        
        if 'data_finalizacao' not in colunas:
            cursor.execute("ALTER TABLE carrinhos ADD COLUMN data_finalizacao TEXT")
            print("Coluna 'data_finalizacao' adicionada à tabela carrinhos")
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro na migração da tabela carrinhos: {e}")
        return False

def criar_tabelas():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subcategorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria_id INTEGER NOT NULL,
                FOREIGN KEY (categoria_id) REFERENCES categorias (id),
                UNIQUE(nome, categoria_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tipos_produto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria_id INTEGER NOT NULL,
                subcategoria_id INTEGER NOT NULL,
                FOREIGN KEY (categoria_id) REFERENCES categorias (id),
                FOREIGN KEY (subcategoria_id) REFERENCES subcategorias (id),
                UNIQUE(nome, categoria_id, subcategoria_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                marca TEXT,
                quantidade_embalagem TEXT,
                codigo_barras TEXT,
                categoria_id INTEGER NOT NULL,
                subcategoria_id INTEGER NOT NULL,
                imagem TEXT,
                FOREIGN KEY (tipo_id) REFERENCES tipos_produto (id),
                FOREIGN KEY (categoria_id) REFERENCES categorias (id),
                FOREIGN KEY (subcategoria_id) REFERENCES subcategorias (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_criacao TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lista_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lista_id INTEGER NOT NULL,
                tipo_id INTEGER NOT NULL,
                categoria_id INTEGER NOT NULL,
                subcategoria_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                data_adicao TEXT NOT NULL,
                FOREIGN KEY (lista_id) REFERENCES listas (id),
                FOREIGN KEY (tipo_id) REFERENCES tipos_produto (id),
                FOREIGN KEY (categoria_id) REFERENCES categorias (id),
                FOREIGN KEY (subcategoria_id) REFERENCES subcategorias (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supermercados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                bairro TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carrinhos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                supermercado_id INTEGER NOT NULL,
                lista_id INTEGER NOT NULL,
                data_criacao TEXT NOT NULL,
                finalizado INTEGER DEFAULT 0,
                data_finalizacao TEXT,
                FOREIGN KEY (supermercado_id) REFERENCES supermercados (id),
                FOREIGN KEY (lista_id) REFERENCES listas (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carrinho_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                carrinho_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unit REAL NOT NULL,
                FOREIGN KEY (carrinho_id) REFERENCES carrinhos (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_precos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                supermercado_id INTEGER NOT NULL,
                preco REAL NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos (id),
                FOREIGN KEY (supermercado_id) REFERENCES supermercados (id)
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")

# PRODUTOS
def listar_produtos_apk():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem FROM produtos"
        )
        produtos = cursor.fetchall()
        conn.close()
        return produtos
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        return []

def cadastrar_produto_apk(tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem=None):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO produtos (tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem))
        conn.commit()
        conn.close()
        print("Produto cadastrado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao cadastrar produto: {e}")
        return False

def alterar_produto_apk(produto_id, tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE produtos
            SET tipo_id=?, nome=?, marca=?, quantidade_embalagem=?, codigo_barras=?, categoria_id=?, subcategoria_id=?, imagem=?
            WHERE id=?
            ''',
            (tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem, produto_id)
        )
        conn.commit()
        conn.close()
        print("Produto alterado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao alterar produto: {e}")
        return False

def excluir_produto_apk(produto_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
        conn.commit()
        conn.close()
        print(f"Produto com ID {produto_id} excluído com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao excluir produto: {e}")
        return False

# TIPOS DE PRODUTO
def listar_tipos_produto_apk():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, categoria_id, subcategoria_id FROM tipos_produto")
        tipos = cursor.fetchall()
        conn.close()
        return tipos
    except Exception as e:
        print(f"Erro ao listar tipos de produto: {e}")
        return []

def cadastrar_tipo_produto_apk(nome, categoria_id, subcategoria_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tipos_produto (nome, categoria_id, subcategoria_id) VALUES (?, ?, ?)",
            (nome, categoria_id, subcategoria_id)
        )
        conn.commit()
        conn.close()
        print("Tipo de produto cadastrado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao cadastrar tipo de produto: {e}")
        return False

def alterar_tipo_produto_apk(tipo_id, nome, categoria_id, subcategoria_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE tipos_produto
            SET nome=?, categoria_id=?, subcategoria_id=?
            WHERE id=?
            ''',
            (nome, categoria_id, subcategoria_id, tipo_id)
        )
        conn.commit()
        conn.close()
        print("Tipo de produto alterado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao alterar tipo de produto: {e}")
        return False

def excluir_tipo_produto_apk(tipo_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tipos_produto WHERE id = ?', (tipo_id,))
        conn.commit()
        conn.close()
        print(f"Tipo de produto com ID {tipo_id} excluído com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao excluir tipo de produto: {e}")
        return False

# CATEGORIAS
def listar_categorias_apk():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM categorias")
        categorias = cursor.fetchall()
        conn.close()
        return categorias
    except Exception as e:
        print(f"Erro ao listar categorias: {e}")
        return []

def cadastrar_categoria_apk(nome):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))
        conn.commit()
        conn.close()
        print("Categoria cadastrada com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao cadastrar categoria: {e}")
        return False

def alterar_categoria_apk(categoria_id, novo_nome):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE categorias SET nome=? WHERE id=?",
            (novo_nome, categoria_id)
        )
        conn.commit()
        conn.close()
        print("Categoria alterada com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao alterar categoria: {e}")
        return False

def excluir_categoria_apk(categoria_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM categorias WHERE id = ?', (categoria_id,))
        conn.commit()
        conn.close()
        print(f"Categoria com ID {categoria_id} excluída com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao excluir categoria: {e}")
        return False

# SUBCATEGORIAS
def listar_subcategorias_apk(categoria_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, categoria_id FROM subcategorias WHERE categoria_id = ?", (categoria_id,))
        subcategorias = cursor.fetchall()
        conn.close()
        return subcategorias
    except Exception as e:
        print(f"Erro ao listar subcategorias: {e}")
        return []

def cadastrar_subcategoria_apk(nome, categoria_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subcategorias (nome, categoria_id) VALUES (?, ?)", (nome, categoria_id))
        conn.commit()
        conn.close()
        print("Subcategoria cadastrada com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao cadastrar subcategoria: {e}")
        return False

def alterar_subcategoria_apk(subcategoria_id, novo_nome, nova_categoria_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE subcategorias SET nome=?, categoria_id=? WHERE id=?",
            (novo_nome, nova_categoria_id, subcategoria_id)
        )
        conn.commit()
        conn.close()
        print("Subcategoria alterada com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao alterar subcategoria: {e}")
        return False

def excluir_subcategoria_apk(subcategoria_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM subcategorias WHERE id = ?', (subcategoria_id,))
        conn.commit()
        conn.close()
        print(f"Subcategoria com ID {subcategoria_id} excluída com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao excluir subcategoria: {e}")
        return False

# SUPERMERCADOS
def listar_supermercados_apk():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, bairro FROM supermercados")
        supermercados = cursor.fetchall()
        conn.close()
        return supermercados
    except Exception as e:
        print(f"Erro ao listar supermercados: {e}")
        return []

def cadastrar_supermercado_apk(nome, bairro):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO supermercados (nome, bairro) VALUES (?, ?)", (nome, bairro))
        conn.commit()
        conn.close()
        print("Supermercado cadastrado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao cadastrar supermercado: {e}")
        return False

def alterar_supermercado_apk(supermercado_id, novo_nome, novo_bairro):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE supermercados SET nome=?, bairro=? WHERE id=?",
            (novo_nome, novo_bairro, supermercado_id)
        )
        conn.commit()
        conn.close()
        print("Supermercado alterado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao alterar supermercado: {e}")
        return False
    
def excluir_supermercado_apk(supermercado_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM supermercados WHERE id = ?', (supermercado_id,))
        conn.commit()
        conn.close()
        print(f"Supermercado com ID {supermercado_id} excluído com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao excluir supermercado: {e}")
        return False

# LISTAS
def listar_listas_apk():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, data_criacao FROM listas")
        listas = cursor.fetchall()
        conn.close()
        return listas
    except Exception as e:
        print(f"Erro ao listar listas: {e}")
        return []

def cadastrar_lista_apk(nome, data_criacao):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO listas (nome, data_criacao) VALUES (?, ?)",
            (nome, data_criacao)
        )
        conn.commit()
        conn.close()
        print("Lista cadastrada com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao cadastrar lista: {e}")
        return False

def alterar_lista_apk(lista_id, novo_nome, nova_data_criacao):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE listas SET nome=?, data_criacao=? WHERE id=?",
            (novo_nome, nova_data_criacao, lista_id)
        )
        conn.commit()
        conn.close()
        print("Lista alterada com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao alterar lista: {e}")
        return False

def excluir_lista_apk(lista_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM listas WHERE id=?", (lista_id,))
        conn.commit()
        conn.close()
        print(f"Lista com ID {lista_id} excluída com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao excluir lista: {e}")
        return False

# ITENS DA LISTA
def listar_itens_lista_apk(lista_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT li.id, li.lista_id, li.tipo_id, li.categoria_id, li.subcategoria_id, li.quantidade, li.data_adicao,
                   tp.nome as tipo_nome, c.nome as categoria_nome, s.nome as subcategoria_nome
            FROM lista_itens li
            JOIN tipos_produto tp ON li.tipo_id = tp.id
            JOIN categorias c ON li.categoria_id = c.id
            JOIN subcategorias s ON li.subcategoria_id = s.id
            WHERE li.lista_id = ?
            ''',
            (lista_id,)
        )
        itens = cursor.fetchall()
        conn.close()
        return itens
    except Exception as e:
        print(f"Erro ao listar itens da lista: {e}")
        return []

def adicionar_item_lista_apk(lista_id, tipo_id, categoria_id, subcategoria_id, quantidade, data_adicao):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO lista_itens (lista_id, tipo_id, categoria_id, subcategoria_id, quantidade, data_adicao) VALUES (?, ?, ?, ?, ?, ?)",
            (lista_id, tipo_id, categoria_id, subcategoria_id, quantidade, data_adicao)
        )
        conn.commit()
        conn.close()
        print("Item adicionado à lista com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao adicionar item à lista: {e}")
        return False

def editar_item_lista_apk(item_id, nova_quantidade):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE lista_itens SET quantidade=? WHERE id=?",
            (nova_quantidade, item_id)
        )
        conn.commit()
        conn.close()
        print("Item da lista alterado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao editar item da lista: {e}")
        return False

def excluir_item_lista_apk(item_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lista_itens WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        print(f"Item da lista com ID {item_id} excluído com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao excluir item da lista: {e}")
        return False

# CARRINHOS
def listar_carrinhos_apk():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome, supermercado_id, lista_id, data_criacao, finalizado, data_finalizacao FROM carrinhos"
        )
        carrinhos = cursor.fetchall()
        conn.close()
        return carrinhos
    except Exception as e:
        print(f"Erro ao listar carrinhos: {e}")
        return []

def cadastrar_carrinho_apk(nome, supermercado_id, lista_id, data_criacao):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO carrinhos (nome, supermercado_id, lista_id, data_criacao) VALUES (?, ?, ?, ?)",
            (nome, supermercado_id, lista_id, data_criacao)
        )
        conn.commit()
        conn.close()
        print("Carrinho cadastrado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao cadastrar carrinho: {e}")
        return False
    
def alterar_carrinho_apk(carrinho_id, novo_nome, novo_supermercado_id, nova_lista_id, nova_data_criacao):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE carrinhos
            SET nome=?, supermercado_id=?, lista_id=?, data_criacao=?
            WHERE id=?
            ''',
            (novo_nome, novo_supermercado_id, nova_lista_id, nova_data_criacao, carrinho_id)
        )
        conn.commit()
        conn.close()
        print("Carrinho alterado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao alterar carrinho: {e}")
        return False

def excluir_carrinho_apk(carrinho_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM carrinhos WHERE id=?", (carrinho_id,))
        conn.commit()
        conn.close()
        print(f"Carrinho com ID {carrinho_id} excluído com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao excluir carrinho: {e}")
        return False

def finalizar_carrinho_apk(carrinho_id):
    """Finaliza um carrinho marcando-o como finalizado"""
    try:
        from datetime import datetime
        conn = conectar()
        cursor = conn.cursor()
        
        data_finalizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE carrinhos SET finalizado = 1, data_finalizacao = ? WHERE id = ?",
            (data_finalizacao, carrinho_id)
        )
        conn.commit()
        conn.close()
        print(f"Carrinho com ID {carrinho_id} finalizado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao finalizar carrinho: {e}")
        return False

def reabrir_carrinho_apk(carrinho_id):
    """Reabre um carrinho finalizado"""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE carrinhos SET finalizado = 0, data_finalizacao = NULL WHERE id = ?",
            (carrinho_id,)
        )
        conn.commit()
        conn.close()
        print(f"Carrinho com ID {carrinho_id} reaberto com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao reabrir carrinho: {e}")
        return False

# ITENS DO CARRINHO
def listar_itens_carrinho_apk(carrinho_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT ci.id, ci.carrinho_id, ci.produto_id, ci.quantidade, ci.preco_unit,
                   p.nome, p.marca, p.quantidade_embalagem
            FROM carrinho_itens ci
            JOIN produtos p ON ci.produto_id = p.id
            WHERE ci.carrinho_id = ?
            ''',
            (carrinho_id,)
        )
        itens = cursor.fetchall()
        conn.close()
        return itens
    except Exception as e:
        print(f"Erro ao listar itens do carrinho: {e}")
        return []

def adicionar_item_carrinho_apk(carrinho_id, produto_id, quantidade, preco_unit):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO carrinho_itens (carrinho_id, produto_id, quantidade, preco_unit) VALUES (?, ?, ?, ?)",
            (carrinho_id, produto_id, quantidade, preco_unit)
        )
        conn.commit()
        conn.close()
        print("Item adicionado ao carrinho com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao adicionar item ao carrinho: {e}")
        return False

def editar_item_carrinho_apk(item_id, nova_quantidade, novo_preco_unit):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE carrinho_itens SET quantidade=?, preco_unit=? WHERE id=?",
            (nova_quantidade, novo_preco_unit, item_id)
        )
        conn.commit()
        conn.close()
        print("Item do carrinho alterado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao editar item do carrinho: {e}")
        return False

def excluir_item_carrinho_apk(item_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM carrinho_itens WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        print(f"Item do carrinho com ID {item_id} excluído com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao excluir item do carrinho: {e}")
        return False

# HISTÓRICO DE PREÇOS
def listar_historico_precos_apk(produto_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT id, produto_id, supermercado_id, preco, data
            FROM historico_precos
            WHERE produto_id = ?
            ORDER BY data DESC
            ''',
            (produto_id,)
        )
        historico = cursor.fetchall()
        conn.close()
        return historico
    except Exception as e:
        print(f"Erro ao listar histórico de preços: {e}")
        return []

def incluir_historico_preco_apk(produto_id, supermercado_id, preco, data):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO historico_precos (produto_id, supermercado_id, preco, data) VALUES (?, ?, ?, ?)",
            (produto_id, supermercado_id, preco, data)
        )
        conn.commit()
        conn.close()
        print("Histórico de preço adicionado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao adicionar histórico de preço: {e}")
        return False