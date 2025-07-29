import sqlite3
import logging
import json
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = "compras.db"

def criar_tabelas_lixeira_apk():
    """Cria tabelas para o sistema de lixeira se não existirem"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Tabela principal da lixeira
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lixeira (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    tipo_item TEXT NOT NULL,
                    dados_json TEXT NOT NULL,
                    data_exclusao TEXT NOT NULL,
                    data_expiracao TEXT NOT NULL
                )
            ''')
            
            # Índices para melhor performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_lixeira_item_id ON lixeira(item_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_lixeira_tipo_item ON lixeira(tipo_item)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_lixeira_data_expiracao ON lixeira(data_expiracao)')
            
            conn.commit()
            logger.info("Tabelas de lixeira criadas/verificadas com sucesso")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Erro ao criar tabelas de lixeira: {e}")
        return False

def inserir_item_lixeira_apk(item_id, tipo_item, dados_json, data_exclusao=None):
    """Insere item na lixeira com data de expiração"""
    try:
        agora = datetime.now()
        if not data_exclusao:
            data_exclusao = agora.strftime("%Y-%m-%d %H:%M:%S")
        
        # Define data de expiração (30 dias a partir da exclusão)
        data_expiracao = (agora + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO lixeira (item_id, tipo_item, dados_json, data_exclusao, data_expiracao)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_id, tipo_item, dados_json, data_exclusao, data_expiracao))
            
            conn.commit()
            logger.info(f"Item {tipo_item} {item_id} inserido na lixeira")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Erro ao inserir item na lixeira: {e}")
        return False

def listar_itens_lixeira_apk(tipo_filtro=None):
    """Lista todos os itens na lixeira (não expirados) com filtro opcional por tipo"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Remove itens expirados primeiro
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('DELETE FROM lixeira WHERE data_expiracao < ?', (data_atual,))
            itens_expirados_removidos = cursor.rowcount
            
            if itens_expirados_removidos > 0:
                logger.info(f"Limpeza automática: {itens_expirados_removidos} itens expirados removidos")
            
            # Lista itens válidos com filtro opcional
            if tipo_filtro:
                cursor.execute('''
                    SELECT item_id, tipo_item, dados_json, data_exclusao
                    FROM lixeira
                    WHERE data_expiracao >= ? AND tipo_item = ?
                    ORDER BY data_exclusao DESC
                ''', (data_atual, tipo_filtro))
            else:
                cursor.execute('''
                    SELECT item_id, tipo_item, dados_json, data_exclusao
                    FROM lixeira
                    WHERE data_expiracao >= ?
                    ORDER BY data_exclusao DESC
                ''', (data_atual,))
            
            return cursor.fetchall()
            
    except sqlite3.Error as e:
        logger.error(f"Erro ao listar itens da lixeira: {e}")
        return []

def restaurar_item_lixeira_apk(item_id, tipo_item):
    """Restaura item da lixeira para a tabela original"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Busca dados do item na lixeira
            cursor.execute('''
                SELECT dados_json FROM lixeira 
                WHERE item_id = ? AND tipo_item = ?
            ''', (item_id, tipo_item))
            
            resultado = cursor.fetchone()
            if not resultado:
                logger.warning(f"Item {tipo_item} {item_id} não encontrado na lixeira")
                return False
            
            dados = json.loads(resultado[0])
            
            # Restaura baseado no tipo
            sucesso = False
            if tipo_item == 'produto':
                sucesso = restaurar_produto_lixeira(cursor, dados)
            elif tipo_item == 'carrinho':
                sucesso = restaurar_carrinho_lixeira(cursor, dados)
            elif tipo_item == 'supermercado':
                sucesso = restaurar_supermercado_lixeira(cursor, dados)
            elif tipo_item == 'lista':
                sucesso = restaurar_lista_lixeira(cursor, dados)
            elif tipo_item == 'tipo_produto':
                sucesso = restaurar_tipo_produto_lixeira(cursor, dados)
            
            if sucesso:
                # Remove da lixeira
                cursor.execute('DELETE FROM lixeira WHERE item_id = ? AND tipo_item = ?', 
                             (item_id, tipo_item))
                conn.commit()
                logger.info(f"Item {tipo_item} {item_id} restaurado com sucesso")
                return True
            
            return False
            
    except sqlite3.Error as e:
        logger.error(f"Erro ao restaurar item da lixeira: {e}")
        return False

def restaurar_produto_lixeira(cursor, dados):
    """Restaura produto específico"""
    try:
        cursor.execute('''
            INSERT INTO produtos (id, tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (dados['id'], dados['tipo_produto_id'], dados['nome'], dados['marca'], 
              dados['quantidade'], dados['codigo_barras'], dados['categoria_id'], dados['subcategoria_id']))
        return True
    except Exception as e:
        logger.error(f"Erro ao restaurar produto: {e}")
        return False

def restaurar_carrinho_lixeira(cursor, dados):
    """Restaura carrinho específico"""
    try:
        cursor.execute('''
            INSERT INTO carrinhos (id, nome, supermercado_id, lista_id, data_criacao, finalizado, data_finalizacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (dados['id'], dados['nome'], dados['supermercado_id'], 
              dados['lista_id'], dados['data_criacao'], dados.get('finalizado', 0), dados.get('data_finalizacao')))
        return True
    except Exception as e:
        logger.error(f"Erro ao restaurar carrinho: {e}")
        return False

def restaurar_supermercado_lixeira(cursor, dados):
    """Restaura supermercado específico"""
    try:
        cursor.execute('''
            INSERT INTO supermercados (id, nome, bairro)
            VALUES (?, ?, ?)
        ''', (dados['id'], dados['nome'], dados['bairro']))
        return True
    except Exception as e:
        logger.error(f"Erro ao restaurar supermercado: {e}")
        return False

def restaurar_lista_lixeira(cursor, dados):
    """Restaura lista específica"""
    try:
        cursor.execute('''
            INSERT INTO listas (id, nome, data_criacao)
            VALUES (?, ?, ?)
        ''', (dados['id'], dados['nome'], dados['data_criacao']))
        return True
    except Exception as e:
        logger.error(f"Erro ao restaurar lista: {e}")
        return False

def restaurar_tipo_produto_lixeira(cursor, dados):
    """Restaura tipo de produto específico"""
    try:
        cursor.execute('''
            INSERT INTO tipos_produto (id, nome, categoria_id, subcategoria_id)
            VALUES (?, ?, ?, ?)
        ''', (dados['id'], dados['nome'], dados.get('categoria_id'), 
              dados.get('subcategoria_id')))
        return True
    except Exception as e:
        logger.error(f"Erro ao restaurar tipo de produto: {e}")
        return False

def excluir_definitivamente_lixeira_apk(item_id, tipo_item):
    """Exclui item definitivamente da lixeira"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM lixeira WHERE item_id = ? AND tipo_item = ?', 
                         (item_id, tipo_item))
            
            conn.commit()
            logger.info(f"Item {tipo_item} {item_id} excluído definitivamente da lixeira")
            return cursor.rowcount > 0
            
    except sqlite3.Error as e:
        logger.error(f"Erro ao excluir definitivamente item da lixeira: {e}")
        return False

def limpar_lixeira_completa_apk():
    """Limpa toda a lixeira"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM lixeira')
            itens_excluidos = cursor.rowcount
            conn.commit()
            
            logger.info(f"Lixeira limpa completamente - {itens_excluidos} itens removidos")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Erro ao limpar lixeira: {e}")
        return False

def limpar_lixeira_expirados_apk():
    """Remove itens expirados da lixeira automaticamente"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('DELETE FROM lixeira WHERE data_expiracao < ?', (data_atual,))
            
            excluidos = cursor.rowcount
            conn.commit()
            
            if excluidos > 0:
                logger.info(f"{excluidos} itens expirados removidos da lixeira")
            
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Erro ao limpar itens expirados da lixeira: {e}")
        return False

# Função para ser chamada periodicamente para limpeza automática
def manutencao_lixeira_apk():
    """Executa manutenção automática da lixeira"""
    try:
        sucesso = limpar_lixeira_expirados_apk()
        if sucesso:
            logger.info("Manutenção da lixeira executada com sucesso")
        return sucesso
    except Exception as e:
        logger.error(f"Erro na manutenção da lixeira: {e}")
        return False
