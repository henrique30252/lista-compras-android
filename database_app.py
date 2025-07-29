import sqlite3
from datetime import datetime

DB_NAME = "compras.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def input_esc(prompt):
    valor = input(prompt)
    return valor.upper()

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
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                marca TEXT,
                quantidade_embalagem TEXT,
                codigo_barras TEXT,
                categoria_id INTEGER,
                subcategoria_id INTEGER,
                imagem TEXT,
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
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                FOREIGN KEY (lista_id) REFERENCES listas (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
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
                lista_id INTEGER,
                data_criacao TEXT NOT NULL,
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
    except KeyboardInterrupt:
        print("Criação de tabelas cancelada.")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")

# PRODUTOS
def cadastrar_produto():
    try:
        conn = conectar()
        cursor = conn.cursor()
        print("\nCategorias disponíveis:")
        cursor.execute("SELECT id, nome FROM categorias")
        categorias = cursor.fetchall()
        for cat in categorias:
            print(f"{cat[0]} - {cat[1]}")
        categoria_id = input_esc("ID da categoria (ou Enter para nenhum): ")
        categoria_id = int(categoria_id) if categoria_id.strip() else None

        print("\nSubcategorias disponíveis:")
        cursor.execute("SELECT id, nome, categoria_id FROM subcategorias")
        subcategorias = cursor.fetchall()
        for sub in subcategorias:
            print(f"{sub[0]} - {sub[1]} (Categoria {sub[2]})")
        subcategoria_id = input_esc("ID da subcategoria (ou Enter para nenhum): ")
        subcategoria_id = int(subcategoria_id) if subcategoria_id.strip() else None

        while True:
            nome = input_esc("Nome do produto (obrigatório): ").strip()
            if nome:
                break
            print("O nome do produto é obrigatório.")

        marca = input_esc("Marca: ")
        quantidade_embalagem = input_esc("Quantidade/Embalagem: ")
        codigo_barras = input_esc("Código de barras: ")
        imagem = input_esc("Imagem (caminho ou URL): ")

        cursor.execute('''
            INSERT INTO produtos (nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem))
        conn.commit()
        conn.close()
        print("Produto cadastrado com sucesso!")
    except KeyboardInterrupt:
        print("Cadastro de produto cancelado.")
    except Exception as e:
        print(f"Erro ao cadastrar produto: {e}")

def listar_produtos():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.nome, p.marca, p.quantidade_embalagem, p.codigo_barras, c.nome, s.nome
            FROM produtos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN subcategorias s ON p.subcategoria_id = s.id
        ''')
        produtos = cursor.fetchall()
        conn.close()
        print("\n--- Produtos ---")
        for prod in produtos:
            print(
                f"ID: {prod[0]}, Nome: {prod[1]}, Marca: {prod[2]}, Embalagem: {prod[3]}, "
                f"Código de Barras: {prod[4]}, Categoria: {prod[5]}, Subcategoria: {prod[6]}"
            )
        return produtos
    except KeyboardInterrupt:
        print("Listagem de produtos cancelada.")

def alterar_produto():
    try:
        listar_produtos()
        produto_id = input_esc("ID do produto a alterar: ")
        produto_id = int(produto_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem FROM produtos WHERE id=?", (produto_id,))
        produto = cursor.fetchone()
        if not produto:
            print("Produto não encontrado.")
            conn.close()
            return

        print("\nCategorias disponíveis:")
        cursor.execute("SELECT id, nome FROM categorias")
        categorias = cursor.fetchall()
        for cat in categorias:
            print(f"{cat[0]} - {cat[1]}")

        print("\nSubcategorias disponíveis:")
        cursor.execute("SELECT id, nome, categoria_id FROM subcategorias")
        subcategorias = cursor.fetchall()
        for sub in subcategorias:
            print(f"{sub[0]} - {sub[1]} (Categoria {sub[2]})")

        print("Pressione Enter para manter o valor atual. ESC para cancelar.")
        nome = input_esc(f"Novo nome [{produto[0]}]: ") or produto[0]
        marca = input_esc(f"Nova marca [{produto[1]}]: ") or produto[1]
        quantidade_embalagem = input_esc(f"Nova quantidade/embalagem [{produto[2]}]: ") or produto[2]
        codigo_barras = input_esc(f"Novo código de barras [{produto[3]}]: ") or produto[3]
        categoria_id = input_esc(f"Novo ID da categoria [{produto[4]}]: ")
        categoria_id = int(categoria_id) if categoria_id.strip() else produto[4]
        subcategoria_id = input_esc(f"Novo ID da subcategoria [{produto[5]}]: ")
        subcategoria_id = int(subcategoria_id) if subcategoria_id.strip() else produto[5]
        imagem = input_esc(f"Nova imagem [{produto[6]}]: ") or produto[6]

        cursor.execute('''
            UPDATE produtos
            SET nome=?, marca=?, quantidade_embalagem=?, codigo_barras=?, categoria_id=?, subcategoria_id=?, imagem=?
            WHERE id=?
        ''', (nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem, produto_id))
        conn.commit()
        conn.close()
        print("Produto alterado com sucesso!")
    except KeyboardInterrupt:
        print("Alteração de produto cancelada.")
    except Exception as e:
        print(f"Erro ao alterar produto: {e}")

def excluir_produto():
    try:
        listar_produtos()
        produto_id = input_esc("ID do produto a excluir: ")
        produto_id = int(produto_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id FROM produtos WHERE id=?",
            (produto_id,)
        )
        produto = cursor.fetchone()
        if not produto:
            print("Produto não encontrado.")
            conn.close()
            return

        print("\nVocê selecionou para excluir o produto:")
        print(
            f"Nome: {produto[0]}, Marca: {produto[1]}, Embalagem: {produto[2]}, "
            f"Código de Barras: {produto[3]}, Categoria ID: {produto[4]}, Subcategoria ID: {produto[5]}"
        )
        confirmacao = input_esc("Confirma a exclusão deste produto? (S/N): ")
        if confirmacao != "S":
            print("Exclusão cancelada.")
            conn.close()
            return

        cursor.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
        conn.commit()
        conn.close()
        print("Produto excluído com sucesso!")
    except KeyboardInterrupt:
        print("Exclusão de produto cancelada.")
    except Exception as e:
        print(f"Erro ao excluir produto: {e}")

# SUPERMERCADOS
def cadastrar_supermercado():
    try:
        nome = input_esc("Nome do supermercado: ")
        bairro = input_esc("Bairro: ")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO supermercados (nome, bairro) VALUES (?, ?)", (nome, bairro))
        conn.commit()
        conn.close()
        print("Supermercado cadastrado com sucesso!")
    except KeyboardInterrupt:
        print("Cadastro de supermercado cancelado.")
    except Exception as e:
        print(f"Erro ao cadastrar supermercado: {e}")

def listar_supermercados():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, bairro FROM supermercados")
        supermercados = cursor.fetchall()
        conn.close()
        print("\n--- Supermercados ---")
        for sup in supermercados:
            print(f"ID: {sup[0]}, Nome: {sup[1]}, Bairro: {sup[2]}")
        return supermercados
    except KeyboardInterrupt:
        print("Listagem de supermercados cancelada.")

def alterar_supermercado():
    try:
        listar_supermercados()
        supermercado_id = input_esc("ID do supermercado a alterar: ")
        supermercado_id = int(supermercado_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, bairro FROM supermercados WHERE id=?", (supermercado_id,))
        supermercado = cursor.fetchone()
        if not supermercado:
            print("Supermercado não encontrado.")
            conn.close()
            return
        print("Pressione Enter para manter o valor atual. ESC para cancelar.")
        nome = input_esc(f"Novo nome [{supermercado[0]}]: ") or supermercado[0]
        bairro = input_esc(f"Novo bairro [{supermercado[1]}]: ") or supermercado[1]
        cursor.execute("UPDATE supermercados SET nome=?, bairro=? WHERE id=?", (nome, bairro, supermercado_id))
        conn.commit()
        conn.close()
        print("Supermercado alterado com sucesso!")
    except KeyboardInterrupt:
        print("Alteração de supermercado cancelada.")
    except Exception as e:
        print(f"Erro ao alterar supermercado: {e}")

def excluir_supermercado():
    try:
        listar_supermercados()
        supermercado_id = input_esc("ID do supermercado a excluir: ")
        supermercado_id = int(supermercado_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM supermercados WHERE id=?", (supermercado_id,))
        if not cursor.fetchone():
            print("Supermercado não encontrado.")
            conn.close()
            return
        cursor.execute("DELETE FROM supermercados WHERE id=?", (supermercado_id,))
        conn.commit()
        conn.close()
        print("Supermercado excluído com sucesso!")
    except KeyboardInterrupt:
        print("Exclusão de supermercado cancelada.")
    except Exception as e:
        print(f"Erro ao excluir supermercado: {e}")

# LISTAS DE COMPRAS
def criar_lista():
    try:
        nome = input_esc("Nome da lista: ")
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO listas (nome, data_criacao) VALUES (?, ?)", (nome, data_criacao))
        conn.commit()
        conn.close()
        print("Lista criada com sucesso!")
    except KeyboardInterrupt:
        print("Criação de lista cancelada.")
    except Exception as e:
        print(f"Erro ao criar lista: {e}")

def listar_listas():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM listas")
        listas = cursor.fetchall()
        conn.close()
        print("\n--- Listas de Compras ---")
        for lista in listas:
            print(f"ID: {lista[0]}, Nome: {lista[1]}")
        return listas
    except KeyboardInterrupt:
        print("Listagem de listas cancelada.")

def visualizar_lista(lista_id=None):
    try:
        if lista_id is None:
            listar_listas()
            lista_id = input_esc("ID da lista: ")
            lista_id = int(lista_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.nome as categoria, p.nome, p.marca, li.quantidade
            FROM lista_itens li
            JOIN produtos p ON li.produto_id = p.id
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE li.lista_id = ?
            ORDER BY c.nome, p.nome
        ''', (lista_id,))
        itens = cursor.fetchall()
        conn.close()
        print(f"\n--- Itens da Lista (ID {lista_id}) ---")
        categorias_dict = {}
        for categoria, nome, marca, quantidade in itens:
            if categoria not in categorias_dict:
                categorias_dict[categoria] = []
            categorias_dict[categoria].append((quantidade, nome, marca))
        for categoria in categorias_dict:
            print(f"{categoria}")
            for quantidade, nome, marca in categorias_dict[categoria]:
                print(f"    [{quantidade}] {nome}, {marca}")
        return itens
    except KeyboardInterrupt:
        print("Visualização de lista cancelada.")
    except Exception as e:
        print(f"Erro ao visualizar lista: {e}")

def alterar_lista():
    try:
        listar_listas()
        lista_id = input_esc("ID da lista a alterar: ")
        lista_id = int(lista_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM listas WHERE id=?", (lista_id,))
        lista = cursor.fetchone()
        if not lista:
            print("Lista não encontrada.")
            conn.close()
            return
        novo_nome = input_esc(f"Novo nome da lista [{lista[0]}]: ") or lista[0]
        cursor.execute("UPDATE listas SET nome=? WHERE id=?", (novo_nome, lista_id))
        conn.commit()
        conn.close()
        print("Lista alterada com sucesso!")
    except KeyboardInterrupt:
        print("Alteração de lista cancelada.")
    except Exception as e:
        print(f"Erro ao alterar lista: {e}")

def excluir_lista():
    try:
        listar_listas()
        lista_id = input_esc("ID da lista a excluir: ")
        lista_id = int(lista_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM listas WHERE id=?", (lista_id,))
        if not cursor.fetchone():
            print("Lista não encontrada.")
            conn.close()
            return
        cursor.execute("DELETE FROM lista_itens WHERE lista_id=?", (lista_id,))
        cursor.execute("DELETE FROM listas WHERE id=?", (lista_id,))
        conn.commit()
        conn.close()
        print("Lista excluída com sucesso!")
    except KeyboardInterrupt:
        print("Exclusão de lista cancelada.")
    except Exception as e:
        print(f"Erro ao excluir lista: {e}")

def adicionar_item_lista():
    try:
        listar_listas()
        lista_id = input_esc("ID da lista: ")
        lista_id = int(lista_id)
        visualizar_lista(lista_id)
        while True:
            listar_produtos()
            produto_id = input_esc("ID do produto (ou 0 para finalizar): ")
            if produto_id == "0":
                print("Finalizando inserção de itens na lista.")
                break
            produto_id = int(produto_id)
            quantidade = input_esc("Quantidade: ")
            quantidade = int(quantidade)
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT quantidade FROM lista_itens WHERE lista_id=? AND produto_id=?",
                (lista_id, produto_id)
            )
            item_existente = cursor.fetchone()
            if item_existente:
                nova_quantidade = item_existente[0] + quantidade
                cursor.execute(
                    "UPDATE lista_itens SET quantidade=? WHERE lista_id=? AND produto_id=?",
                    (nova_quantidade, lista_id, produto_id)
                )
                print("Quantidade somada ao item já existente na lista!")
            else:
                cursor.execute(
                    "INSERT INTO lista_itens (lista_id, produto_id, quantidade) VALUES (?, ?, ?)",
                    (lista_id, produto_id, quantidade)
                )
                print("Item adicionado à lista com sucesso!")
            conn.commit()
            conn.close()
    except KeyboardInterrupt:
        print("Adição de item à lista cancelada.")
    except Exception as e:
        print(f"Erro ao adicionar item à lista: {e}")

def alterar_item_lista(item_id=None, quantidade=None):
    try:
        listar_listas()
        lista_id = input_esc("ID da lista do item a alterar: ")
        lista_id = int(lista_id)
        visualizar_lista(lista_id)
        if item_id is None:
            item_id = input_esc("ID do item da lista: ")
            item_id = int(item_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT quantidade FROM lista_itens WHERE id=?", (item_id,))
        item = cursor.fetchone()
        if not item:
            print("Item da lista não encontrado.")
            conn.close()
            return
        quantidade_atual = item[0]
        nova_quantidade = input_esc(f"Nova quantidade [{quantidade_atual}]: ")
        if not nova_quantidade.strip():
            nova_quantidade = quantidade_atual
        else:
            nova_quantidade = int(nova_quantidade)
        if nova_quantidade == 0:
            cursor.execute("DELETE FROM lista_itens WHERE id=?", (item_id,))
            print("Item excluído da lista por quantidade zero!")
        else:
            cursor.execute("UPDATE lista_itens SET quantidade=? WHERE id=?", (nova_quantidade, item_id))
            print("Item alterado com sucesso!")
        conn.commit()
        conn.close()
    except KeyboardInterrupt:
        print("Alteração de item da lista cancelada.")
    except Exception as e:
        print(f"Erro ao alterar item da lista: {e}")

def excluir_item_lista(item_id=None):
    try:
        listar_listas()
        lista_id = input_esc("ID da lista do item a excluir: ")
        lista_id = int(lista_id)
        visualizar_lista(lista_id)
        if item_id is None:
            item_id = input_esc("ID do item da lista: ")
            item_id = int(item_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM lista_itens WHERE id=?", (item_id,))
        if not cursor.fetchone():
            print("Item da lista não encontrado.")
            conn.close()
            return
        cursor.execute("DELETE FROM lista_itens WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        print("Item excluído da lista com sucesso!")
    except KeyboardInterrupt:
        print("Exclusão de item da lista cancelada.")
    except Exception as e:
        print(f"Erro ao excluir item da lista: {e}")

# CARRINHOS
def criar_carrinho():
    try:
        nome = input_esc("Nome do carrinho: ")
        listar_supermercados()
        supermercado_id = input_esc("ID do supermercado: ")
        supermercado_id = int(supermercado_id)
        listar_listas()
        lista_id = input_esc("ID da lista de compras para associar ao carrinho: ")
        lista_id = int(lista_id)
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO carrinhos (nome, supermercado_id, lista_id, data_criacao) VALUES (?, ?, ?, ?)",
            (nome, supermercado_id, lista_id, data_criacao)
        )
        conn.commit()
        conn.close()
        print("Carrinho criado com sucesso e associado à lista de compras!")
    except KeyboardInterrupt:
        print("Criação de carrinho cancelada.")
    except Exception as e:
        print(f"Erro ao criar carrinho: {e}")

def listar_carrinhos():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.nome, s.nome
            FROM carrinhos c
            JOIN supermercados s ON c.supermercado_id = s.id
        ''')
        carrinhos = cursor.fetchall()
        conn.close()
        print("\n--- Carrinhos ---")
        for carrinho in carrinhos:
            print(f"ID: {carrinho[0]}, Nome: {carrinho[1]}, Supermercado: {carrinho[2]}")
        return carrinhos
    except KeyboardInterrupt:
        print("Listagem de carrinhos cancelada.")

def visualizar_carrinho(carrinho_id=None):
    try:
        listar_carrinhos()
        if carrinho_id is None:
            carrinho_id = input_esc("ID do carrinho: ")
            carrinho_id = int(carrinho_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ci.id, p.nome, ci.quantidade, ci.preco_unit, (ci.quantidade * ci.preco_unit) as total
            FROM carrinho_itens ci
            JOIN produtos p ON ci.produto_id = p.id
            WHERE ci.carrinho_id = ?
        ''', (carrinho_id,))
        itens = cursor.fetchall()
        total_geral = sum(item[4] for item in itens)
        conn.close()
        print(f"\n--- Itens do Carrinho (ID {carrinho_id}) ---")
        for item in itens:
            print(f"Item ID: {item[0]}, Produto: {item[1]}, Quantidade: {item[2]}, Preço Unitário: R${item[3]:.2f}, Subtotal: R${item[4]:.2f}")
        print(f"TOTAL: R${total_geral:.2f}")
        return [(item[1], item[2], item[3], item[4]) for item in itens], total_geral
    except KeyboardInterrupt:
        print("Visualização de carrinho cancelada.")
    except Exception as e:
        print(f"Erro ao visualizar carrinho: {e}")

def adicionar_item_carrinho(carrinho_id=None, produto_id=None, quantidade=None, preco_unit=None):
    try:
        listar_carrinhos()
        if carrinho_id is None:
            carrinho_id = input_esc("ID do carrinho: ")
            carrinho_id = int(carrinho_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT lista_id, supermercado_id FROM carrinhos WHERE id=?", (carrinho_id,))
        lista_assoc = cursor.fetchone()
        if not lista_assoc or not lista_assoc[0]:
            print("Nenhuma lista associada a este carrinho.")
            conn.close()
            return
        lista_id = lista_assoc[0]
        supermercado_id = lista_assoc[1]
        while True:
            print("\nItens da lista associada:")
            cursor.execute('''
                SELECT p.id, p.nome, li.quantidade
                FROM lista_itens li
                JOIN produtos p ON li.produto_id = p.id
                WHERE li.lista_id = ?
            ''', (lista_id,))
            itens_lista = cursor.fetchall()
            for item in itens_lista:
                print(f"Produto ID: {item[0]}, Nome: {item[1]}, Quantidade na lista: {item[2]}")
            produto_id = input_esc("ID do produto para adicionar ao carrinho (ou 0 para finalizar): ")
            if produto_id == "0":
                print("Finalizando inserção de itens no carrinho.")
                break
            produto_id = int(produto_id)
            quantidade_lista = None
            for item in itens_lista:
                if item[0] == produto_id:
                    quantidade_lista = item[2]
                    break
            quantidade = input_esc(f"Quantidade (Enter para usar a quantidade da lista: {quantidade_lista}): ")
            if not quantidade.strip() and quantidade_lista is not None:
                quantidade = quantidade_lista
            else:
                quantidade = int(quantidade)
            preco_unit = input_esc("Preço unitário: ")
            preco_unit = float(preco_unit)
            cursor.execute('''
                INSERT INTO carrinho_itens (carrinho_id, produto_id, quantidade, preco_unit)
                VALUES (?, ?, ?, ?)
            ''', (carrinho_id, produto_id, quantidade, preco_unit))
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO historico_precos (produto_id, supermercado_id, preco, data)
                VALUES (?, ?, ?, ?)
            ''', (produto_id, supermercado_id, preco_unit, data_atual))
            if quantidade_lista is not None:
                nova_quantidade_lista = quantidade_lista - quantidade
                if nova_quantidade_lista <= 0:
                    cursor.execute(
                        "DELETE FROM lista_itens WHERE lista_id=? AND produto_id=?",
                        (lista_id, produto_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE lista_itens SET quantidade=? WHERE lista_id=? AND produto_id=?",
                        (nova_quantidade_lista, lista_id, produto_id)
                    )
            conn.commit()
            print("Item adicionado ao carrinho com sucesso!")
        conn.close()
    except KeyboardInterrupt:
        print("Adição de item ao carrinho cancelada.")
    except Exception as e:
        print(f"Erro ao adicionar item ao carrinho: {e}")

def alterar_item_carrinho(item_id=None, quantidade=None, preco_unit=None):
    try:
        listar_carrinhos()
        carrinho_id = input_esc("ID do carrinho do item a alterar: ")
        carrinho_id = int(carrinho_id)
        visualizar_carrinho(carrinho_id)
        if item_id is None:
            item_id = input_esc("ID do item do carrinho: ")
            item_id = int(item_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT lista_id FROM carrinhos WHERE id=?", (carrinho_id,))
        lista_assoc = cursor.fetchone()
        lista_id = lista_assoc[0] if lista_assoc else None
        print("\nItens da lista associada:")
        cursor.execute('''
            SELECT p.id, p.nome, li.quantidade
            FROM lista_itens li
            JOIN produtos p ON li.produto_id = p.id
            WHERE li.lista_id = ?
        ''', (lista_id,))
        itens_lista = cursor.fetchall()
        for item in itens_lista:
            print(f"Produto ID: {item[0]}, Nome: {item[1]}, Quantidade na lista: {item[2]}")
        cursor.execute("SELECT produto_id, quantidade, preco_unit FROM carrinho_itens WHERE id=?", (item_id,))
        item = cursor.fetchone()
        if not item:
            print("Item do carrinho não encontrado.")
            conn.close()
            return
        produto_id = item[0]
        quantidade_atual = item[1]
        preco_unit_atual = item[2]
        nova_quantidade = input_esc(f"Nova quantidade [{quantidade_atual}]: ")
        if not nova_quantidade.strip():
            nova_quantidade = quantidade_atual
        else:
            nova_quantidade = int(nova_quantidade)
        novo_preco_unit = input_esc(f"Novo preço unitário [{preco_unit_atual}]: ")
        if not novo_preco_unit.strip():
            novo_preco_unit = preco_unit_atual
        else:
            novo_preco_unit = float(novo_preco_unit)
        cursor.execute("SELECT quantidade FROM lista_itens WHERE lista_id=? AND produto_id=?", (lista_id, produto_id))
        item_lista = cursor.fetchone()
        quantidade_lista = item_lista[0] if item_lista else 0
        diferenca = nova_quantidade - quantidade_atual
        if diferenca > 0:
            nova_quantidade_lista = quantidade_lista - diferenca
            if nova_quantidade_lista < 0:
                print("Erro: quantidade insuficiente na lista associada para realizar a operação.")
                conn.close()
                return
            elif nova_quantidade_lista == 0:
                cursor.execute("DELETE FROM lista_itens WHERE lista_id=? AND produto_id=?", (lista_id, produto_id))
            else:
                cursor.execute("UPDATE lista_itens SET quantidade=? WHERE lista_id=? AND produto_id=?", (nova_quantidade_lista, lista_id, produto_id))
        elif diferenca < 0:
            nova_quantidade_lista = quantidade_lista + abs(diferenca)
            if item_lista:
                cursor.execute("UPDATE lista_itens SET quantidade=? WHERE lista_id=? AND produto_id=?", (nova_quantidade_lista, lista_id, produto_id))
            else:
                cursor.execute("INSERT INTO lista_itens (lista_id, produto_id, quantidade) VALUES (?, ?, ?)", (lista_id, produto_id, abs(diferenca)))
        if nova_quantidade == 0:
            cursor.execute("DELETE FROM carrinho_itens WHERE id=?", (item_id,))
            print("Item excluído do carrinho por quantidade zero!")
        else:
            cursor.execute(
                "UPDATE carrinho_itens SET quantidade=?, preco_unit=? WHERE id=?",
                (nova_quantidade, novo_preco_unit, item_id)
            )
            print("Item do carrinho alterado com sucesso!")
        conn.commit()
        conn.close()
    except KeyboardInterrupt:
        print("Alteração de item do carrinho cancelada.")
    except Exception as e:
        print(f"Erro ao alterar item do carrinho: {e}")

def excluir_item_carrinho(item_id=None):
    try:
        listar_carrinhos()
        carrinho_id = input_esc("ID do carrinho do item a excluir: ")
        carrinho_id = int(carrinho_id)
        visualizar_carrinho(carrinho_id)
        if item_id is None:
            item_id = input_esc("ID do item do carrinho: ")
            item_id = int(item_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT lista_id FROM carrinhos WHERE id=?", (carrinho_id,))
        lista_assoc = cursor.fetchone()
        lista_id = lista_assoc[0] if lista_assoc else None
        cursor.execute("SELECT produto_id, quantidade FROM carrinho_itens WHERE id=?", (item_id,))
        item = cursor.fetchone()
        if not item:
            print("Item do carrinho não encontrado.")
            conn.close()
            return
        produto_id = item[0]
        quantidade_excluida = item[1]
        cursor.execute("SELECT quantidade FROM lista_itens WHERE lista_id=? AND produto_id=?", (lista_id, produto_id))
        item_lista = cursor.fetchone()
        if item_lista:
            nova_quantidade_lista = item_lista[0] + quantidade_excluida
            cursor.execute("UPDATE lista_itens SET quantidade=? WHERE lista_id=? AND produto_id=?", (nova_quantidade_lista, lista_id, produto_id))
        else:
            cursor.execute("INSERT INTO lista_itens (lista_id, produto_id, quantidade) VALUES (?, ?, ?)", (lista_id, produto_id, quantidade_excluida))
        cursor.execute("DELETE FROM carrinho_itens WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        print("Item excluído do carrinho e quantidade devolvida à lista associada!")
    except KeyboardInterrupt:
        print("Exclusão de item do carrinho cancelada.")
    except Exception as e:
        print(f"Erro ao excluir item do carrinho: {e}")

def alterar_carrinho():
    try:
        listar_carrinhos()
        carrinho_id = input_esc("ID do carrinho a alterar: ")
        carrinho_id = int(carrinho_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, supermercado_id, lista_id FROM carrinhos WHERE id=?", (carrinho_id,))
        carrinho = cursor.fetchone()
        if not carrinho:
            print("Carrinho não encontrado.")
            conn.close()
            return
        print("Pressione Enter para manter o valor atual.")
        novo_nome = input_esc(f"Novo nome [{carrinho[0]}]: ") or carrinho[0]
        listar_supermercados()
        novo_supermercado_id = input_esc(f"Novo ID do supermercado [{carrinho[1]}]: ")
        novo_supermercado_id = int(novo_supermercado_id) if novo_supermercado_id.strip() else carrinho[1]
        listar_listas()
        novo_lista_id = input_esc(f"Novo ID da lista associada [{carrinho[2]}]: ")
        novo_lista_id = int(novo_lista_id) if novo_lista_id.strip() else carrinho[2]
        cursor.execute(
            "UPDATE carrinhos SET nome=?, supermercado_id=?, lista_id=? WHERE id=?",
            (novo_nome, novo_supermercado_id, novo_lista_id, carrinho_id)
        )
        conn.commit()
        conn.close()
        print("Carrinho alterado com sucesso!")
    except KeyboardInterrupt:
        print("Alteração de carrinho cancelada.")
    except Exception as e:
        print(f"Erro ao alterar carrinho: {e}")

def excluir_carrinho():
    try:
        listar_carrinhos()
        carrinho_id = input_esc("ID do carrinho a excluir: ")
        carrinho_id = int(carrinho_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM carrinhos WHERE id=?", (carrinho_id,))
        if not cursor.fetchone():
            print("Carrinho não encontrado.")
            conn.close()
            return
        cursor.execute("DELETE FROM carrinho_itens WHERE carrinho_id=?", (carrinho_id,))
        cursor.execute("DELETE FROM carrinhos WHERE id=?", (carrinho_id,))
        conn.commit()
        conn.close()
        print("Carrinho excluído com sucesso!")
    except KeyboardInterrupt:
        print("Exclusão de carrinho cancelada.")
    except Exception as e:
        print(f"Erro ao excluir carrinho: {e}")

# HISTÓRICO DE PREÇOS
def listar_historico_precos(produto_id=None):
    try:
        conn = conectar()
        cursor = conn.cursor()
        if produto_id:
            cursor.execute('''
                SELECT h.id, p.nome, c.nome, s.nome, h.preco, h.data
                FROM historico_precos h
                JOIN produtos p ON h.produto_id = p.id
                LEFT JOIN categorias c ON p.categoria_id = c.id
                JOIN supermercados s ON h.supermercado_id = s.id
                WHERE p.id = ?
                ORDER BY h.data DESC, s.nome
            ''', (produto_id,))
        else:
            cursor.execute('''
                SELECT h.id, p.nome, c.nome, s.nome, h.preco, h.data
                FROM historico_precos h
                JOIN produtos p ON h.produto_id = p.id
                LEFT JOIN categorias c ON p.categoria_id = c.id
                JOIN supermercados s ON h.supermercado_id = s.id
                ORDER BY c.nome, p.nome, h.data DESC, s.nome
            ''')
        historico = cursor.fetchall()
        conn.close()
        print("\n--- Histórico de Preços ---")
        categorias_dict = {}
        for h in historico:
            categoria = h[2] if h[2] else "Sem Categoria"
            produto = h[1]
            supermercado = h[3]
            if categoria not in categorias_dict:
                categorias_dict[categoria] = {}
            if produto not in categorias_dict[categoria]:
                categorias_dict[categoria][produto] = {}
            if supermercado not in categorias_dict[categoria][produto]:
                categorias_dict[categoria][produto][supermercado] = []
            categorias_dict[categoria][produto][supermercado].append(h)
        for categoria in categorias_dict:
            print(f"\n{categoria}")
            for produto in categorias_dict[categoria]:
                print(f"  {produto}")
                for supermercado in categorias_dict[categoria][produto]:
                    print(f"    Supermercado: {supermercado}")
                    for h in categorias_dict[categoria][produto][supermercado]:
                        print(f"      Preço: R${h[4]:.2f}, Data: {h[5]}")
        return historico
    except KeyboardInterrupt:
        print("Listagem de histórico de preços cancelada.")
    except Exception as e:
        print(f"Erro ao listar histórico de preços: {e}")

# CATEGORIAS E SUBCATEGORIAS
def cadastrar_categoria():
    try:
        nome = input_esc("Nome da categoria: ")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))
        conn.commit()
        conn.close()
        print("Categoria cadastrada com sucesso!")
    except KeyboardInterrupt:
        print("Cadastro de categoria cancelado.")
    except Exception as e:
        print(f"Erro ao cadastrar categoria: {e}")

def listar_categorias():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM categorias")
        categorias = cursor.fetchall()
        conn.close()
        print("\n--- Categorias ---")
        for cat in categorias:
            print(f"ID: {cat[0]}, Nome: {cat[1]}")
        return categorias
    except KeyboardInterrupt:
        print("Listagem de categorias cancelada.")

def cadastrar_subcategoria():
    try:
        nome = input_esc("Nome da subcategoria: ")
        categoria_id = input_esc("ID da categoria: ")
        categoria_id = int(categoria_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO subcategorias (nome, categoria_id) VALUES (?, ?)",
            (nome, categoria_id)
        )
        conn.commit()
        conn.close()
        print("Subcategoria cadastrada com sucesso!")
    except KeyboardInterrupt:
        print("Cadastro de subcategoria cancelado.")
    except Exception as e:
        print(f"Erro ao cadastrar subcategoria: {e}")

def listar_subcategorias():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id, s.nome, c.nome,
                (SELECT COUNT(*) FROM produtos p WHERE p.subcategoria_id = s.id) as qtd_produtos
            FROM subcategorias s
            JOIN categorias c ON s.categoria_id = c.id
        ''')
        subcategorias = cursor.fetchall()
        conn.close()
        print("\n--- Subcategorias ---")
        for sub in subcategorias:
            print(f"ID: {sub[0]}, Subcategoria: {sub[1]}, Categoria: {sub[2]}, Produtos cadastrados: {sub[3]}")
        return subcategorias
    except KeyboardInterrupt:
        print("Listagem de subcategorias cancelada.")

def alterar_subcategoria():
    try:
        listar_subcategorias()
        subcategoria_id = input_esc("ID da subcategoria a alterar: ")
        subcategoria_id = int(subcategoria_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, categoria_id FROM subcategorias WHERE id=?", (subcategoria_id,))
        subcategoria = cursor.fetchone()
        if not subcategoria:
            print("Subcategoria não encontrada.")
            conn.close()
            return
        print("Pressione Enter para manter o valor atual.")
        novo_nome = input_esc(f"Novo nome [{subcategoria[0]}]: ") or subcategoria[0]
        listar_categorias()
        novo_categoria_id = input_esc(f"Novo ID da categoria [{subcategoria[1]}]: ")
        novo_categoria_id = int(novo_categoria_id) if novo_categoria_id.strip() else subcategoria[1]
        cursor.execute(
            "UPDATE subcategorias SET nome=?, categoria_id=? WHERE id=?",
            (novo_nome, novo_categoria_id, subcategoria_id)
        )
        conn.commit()
        conn.close()
        print("Subcategoria alterada com sucesso!")
    except KeyboardInterrupt:
        print("Alteração de subcategoria cancelada.")
    except Exception as e:
        print(f"Erro ao alterar subcategoria: {e}")

def excluir_subcategoria():
    try:
        listar_subcategorias()
        subcategoria_id = input_esc("ID da subcategoria a excluir: ")
        subcategoria_id = int(subcategoria_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM subcategorias WHERE id=?", (subcategoria_id,))
        if not cursor.fetchone():
            print("Subcategoria não encontrada.")
            conn.close()
            return
        cursor.execute("DELETE FROM subcategorias WHERE id=?", (subcategoria_id,))
        conn.commit()
        conn.close()
        print("Subcategoria excluída com sucesso!")
    except KeyboardInterrupt:
        print("Exclusão de subcategoria cancelada.")
    except Exception as e:
        print(f"Erro ao excluir subcategoria: {e}")

def listar_categorias_e_subcategorias():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.nome,
                (SELECT COUNT(*) FROM produtos p WHERE p.categoria_id = c.id) as qtd_produtos
            FROM categorias c
        ''')
        categorias = cursor.fetchall()
        cursor.execute('''
            SELECT s.id, s.nome, s.categoria_id,
                (SELECT COUNT(*) FROM produtos p WHERE p.subcategoria_id = s.id) as qtd_produtos
            FROM subcategorias s
        ''')
        subcategorias = cursor.fetchall()
        conn.close()
        print("\n--- Categorias e Subcategorias ---")
        for cat in categorias:
            print(f"Categoria: {cat[1]} (ID: {cat[0]}) - Produtos cadastrados: {cat[2]}")
            subs = [sub for sub in subcategorias if sub[2] == cat[0]]
            if subs:
                for sub in subs:
                    print(f"    Subcategoria: {sub[1]} (ID: {sub[0]}) - Produtos cadastrados: {sub[3]}")
            else:
                print("    Nenhuma subcategoria cadastrada.")
        return categorias, subcategorias
    except KeyboardInterrupt:
        print("Listagem de categorias e subcategorias cancelada.")
    except Exception as e:
        print(f"Erro ao listar categorias e subcategorias: {e}")

def alterar_categoria():
    try:
        listar_categorias()
        categoria_id = input_esc("ID da categoria a alterar: ")
        categoria_id = int(categoria_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM categorias WHERE id=?", (categoria_id,))
        categoria = cursor.fetchone()
        if not categoria:
            print("Categoria não encontrada.")
            conn.close()
            return
        print("Pressione Enter para manter o valor atual.")
        novo_nome = input_esc(f"Novo nome [{categoria[0]}]: ") or categoria[0]
        cursor.execute("UPDATE categorias SET nome=? WHERE id=?", (novo_nome, categoria_id))
        conn.commit()
        conn.close()
        print("Categoria alterada com sucesso!")
    except KeyboardInterrupt:
        print("Alteração de categoria cancelada.")
    except Exception as e:
        print(f"Erro ao alterar categoria: {e}")

def excluir_categoria():
    try:
        listar_categorias()
        categoria_id = input_esc("ID da categoria a excluir: ")
        categoria_id = int(categoria_id)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categorias WHERE id=?", (categoria_id,))
        if not cursor.fetchone():
            print("Categoria não encontrada.")
            conn.close()
            return
        cursor.execute("DELETE FROM subcategorias WHERE categoria_id=?", (categoria_id,))
        cursor.execute("DELETE FROM categorias WHERE id=?", (categoria_id,))
        conn.commit()
        conn.close()
        print("Categoria e subcategorias vinculadas excluídas com sucesso!")
    except KeyboardInterrupt:
        print("Exclusão de categoria cancelada.")
    except Exception as e:
        print(f"Erro ao excluir categoria: {e}")