import sqlite3
import os
from datetime import datetime, timedelta
from random import uniform, randint, random
import random

DB_NAME = "compras.db"

if not os.path.exists(DB_NAME):
    print("Arquivo compras.db não encontrado. Será criado automaticamente.")

def conectar():
    return sqlite3.connect(DB_NAME)

# Categorias
categorias_exemplo = [
    (1, "Alimentação"),
    (2, "Limpeza"),
    (3, "Higiene"),
    (4, "Bebidas"),
    (5, "Padaria"),
    (6, "Frios e Laticínios"),
    (7, "Hortifruti"),
    (8, "Mercearia"),
    (9, "Pet Shop"),
    (10, "Utilidades Domésticas"),
]

# Subcategorias (pre-estabelecidas, associadas à categoria)
subcategorias_exemplo = [
    (1, "Almoço", 1),
    (2, "Café da manhã", 1),
    (3, "Jantar", 1),
    (4, "Lavanderia", 2),
    (5, "Banheiro", 2),
    (6, "Cozinha", 2),
    (7, "Corpo", 3),
    (8, "Cabelos", 3),
    (9, "Refrigerante", 4),
    (10, "Sucos", 4),
    (11, "Pães", 5),
    (12, "Bolos", 5),
    (13, "Queijos", 6),
    (14, "Iogurtes", 6),
    (15, "Verduras", 7),
    (16, "Frutas", 7),
    (17, "Enlatados", 8),
    (18, "Massas", 8),
    (19, "Ração", 9),
    (20, "Acessórios", 10),
]

# Tipos de produto (nome, categoria_id, subcategoria_id)
tipos_produto_exemplo = [
    ("Arroz", 1, 1),                # 0  -> tipo_id 1
    ("Feijão", 1, 1),               # 1  -> tipo_id 2
    ("Macarrão", 1, 3),             # 2  -> tipo_id 3
    ("Açúcar", 1, 2),               # 3  -> tipo_id 4
    ("Sal", 1, 1),                  # 4  -> tipo_id 5
    ("Óleo", 1, 1),                 # 5  -> tipo_id 6
    ("Farinha de Trigo", 1, 2),     # 6  -> tipo_id 7
    ("Café", 1, 2),                 # 7  -> tipo_id 8
    ("Leite", 6, 14),               # 8  -> tipo_id 9
    ("Queijo Mussarela", 6, 13),    # 9  -> tipo_id 10
    ("Presunto", 6, 13),            #10  -> tipo_id 11
    ("Iogurte Natural", 6, 14),     #11  -> tipo_id 12
    ("Alface", 7, 15),              #12  -> tipo_id 13
    ("Tomate", 7, 15),              #13  -> tipo_id 14
    ("Banana", 7, 16),              #14  -> tipo_id 15
    ("Maçã", 7, 16),                #15  -> tipo_id 16
    ("Refrigerante", 4, 9),         #16  -> tipo_id 17
    ("Suco", 4, 10),                #17  -> tipo_id 18
    ("Sabão em Pó", 2, 4),          #18  -> tipo_id 19
    ("Amaciante", 2, 4),            #19  -> tipo_id 20
    ("Desinfetante", 2, 5),         #20  -> tipo_id 21
    ("Detergente", 2, 6),           #21  -> tipo_id 22
    ("Esponja de Aço", 2, 6),       #22  -> tipo_id 23
    ("Shampoo", 3, 8),              #23  -> tipo_id 24
    ("Condicionador", 3, 8),        #24  -> tipo_id 25
    ("Sabonete", 3, 7),             #25  -> tipo_id 26
    ("Creme Dental", 3, 7),         #26  -> tipo_id 27
    ("Desodorante", 3, 7),          #27  -> tipo_id 28
    ("Pão", 5, 11),                 #28  -> tipo_id 29
    ("Bolo", 5, 12),                #29  -> tipo_id 30
    ("Atum em Lata", 8, 17),        #30  -> tipo_id 31
    ("Milho em Conserva", 8, 17),   #31  -> tipo_id 32
    ("Ração para Cães", 9, 19),     #32  -> tipo_id 33
    ("Ração para Gatos", 9, 19),    #33  -> tipo_id 34
    ("Areia Sanitária", 9, 19),     #34  -> tipo_id 35
    ("Vassoura", 10, 20),           #35  -> tipo_id 36
    ("Pano de Prato", 10, 20),      #36  -> tipo_id 37
    ("Balde", 10, 20),              #37  -> tipo_id 38
    ("Escova de Dente", 3, 7),      #38  -> tipo_id 39
    ("Margarina", 6, 14),           #39  -> tipo_id 40
    ("Requeijão", 6, 14),           #40  -> tipo_id 41
    ("Cenoura", 7, 15),             #41  -> tipo_id 42
    ("Laranja", 7, 16),             #42  -> tipo_id 43
]

# Produtos exemplo (tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem)
produtos_exemplo = [
    # Arroz (tipo_id=1)
    (1, "Arroz Comum", "Tio João", "5kg", "789123456001", 1, 1, ""),
    (1, "Arroz Integral", "Camil", "1kg", "789123456002", 1, 1, ""),
    (1, "Arroz Parboilizado", "Urbano", "1kg", "789123456054", 1, 1, ""),
    (1, "Arroz Premium", "Blue Ville", "2kg", "789123456055", 1, 1, ""),
    (1, "Arroz Cateto", "Namorado", "1kg", "789123456074", 1, 1, ""),
    (1, "Arroz Parboilizado Premium", "Camil", "1kg", "789123456075", 1, 1, ""),
    # Feijão (tipo_id=2)
    (2, "Feijão Preto", "Kicaldo", "1kg", "789123456003", 1, 1, ""),
    (2, "Feijão Carioca", "Camil", "1kg", "789123456004", 1, 1, ""),
    (2, "Feijão Fradinho", "Yoki", "500g", "789123456056", 1, 1, ""),
    (2, "Feijão Branco", "Caldo Bom", "1kg", "789123456076", 1, 1, ""),
    (2, "Feijão Vermelho", "Kicaldo", "1kg", "789123456077", 1, 1, ""),
    # Macarrão (tipo_id=3)
    (3, "Macarrão Espaguete", "Renata", "500g", "789123456005", 1, 3, ""),
    (3, "Macarrão Penne", "Barilla", "500g", "789123456006", 1, 3, ""),
    (3, "Macarrão Fusilli", "Adria", "500g", "789123456057", 1, 3, ""),
    (3, "Macarrão Talharim", "Adria", "500g", "789123456078", 1, 3, ""),
    (3, "Macarrão Parafuso", "Renata", "500g", "789123456079", 1, 3, ""),
    # Açúcar (tipo_id=4)
    (4, "Açúcar Refinado", "União", "1kg", "789123456007", 1, 2, ""),
    (4, "Açúcar Cristal", "Caravelas", "1kg", "789123456058", 1, 2, ""),
    (4, "Açúcar Mascavo", "União", "1kg", "789123456080", 1, 2, ""),
    (4, "Açúcar Orgânico", "Native", "1kg", "789123456081", 1, 2, ""),
    # Óleo (tipo_id=6)
    (6, "Óleo de Soja", "Liza", "900ml", "789123456009", 1, 1, ""),
    (6, "Óleo de Milho", "Soya", "900ml", "789123456059", 1, 1, ""),
    (6, "Óleo de Girassol", "Liza", "900ml", "789123456060", 1, 1, ""),
    (6, "Óleo de Canola", "Liza", "900ml", "789123456082", 1, 1, ""),
    (6, "Óleo de Coco", "Copra", "200ml", "789123456083", 1, 1, ""),
    # Café (tipo_id=8)
    (8, "Café Torrado", "Pilão", "500g", "789123456011", 1, 2, ""),
    (8, "Café Extra Forte", "Melitta", "500g", "789123456061", 1, 2, ""),
    (8, "Café Tradicional", "3 Corações", "500g", "789123456062", 1, 2, ""),
    (8, "Café Gourmet", "Santa Clara", "250g", "789123456084", 1, 2, ""),
    (8, "Café Solúvel", "Nescafé", "200g", "789123456085", 1, 2, ""),
    # Leite (tipo_id=9)
    (9, "Leite Integral", "Itambé", "1L", "789123456012", 6, 14, ""),
    (9, "Leite Desnatado", "Parmalat", "1L", "789123456063", 6, 14, ""),
    (9, "Leite Semidesnatado", "Piracanjuba", "1L", "789123456064", 6, 14, ""),
    (9, "Leite Zero Lactose", "Piracanjuba", "1L", "789123456086", 6, 14, ""),
    (9, "Leite em Pó", "Ninho", "400g", "789123456087", 6, 14, ""),
    # Queijo Mussarela (tipo_id=10)
    (10, "Queijo Mussarela Fatiado", "Italac", "150g", "789123456013", 6, 13, ""),
    (10, "Queijo Mussarela Peça", "Scala", "500g", "789123456065", 6, 13, ""),
    (10, "Queijo Mussarela Ralado", "Scala", "100g", "789123456088", 6, 13, ""),
    # Presunto (tipo_id=11)
    (11, "Presunto Cozido", "Sadia", "200g", "789123456089", 6, 13, ""),
    (11, "Presunto Defumado", "Perdigão", "200g", "789123456090", 6, 13, ""),
    # Iogurte Natural (tipo_id=12)
    (12, "Iogurte Natural Desnatado", "Vigor", "170g", "789123456091", 6, 14, ""),
    # Alface (tipo_id=13)
    (13, "Alface Crespa", "Hortifruti", "1un", "789123456140", 7, 15, ""),
    (13, "Alface Americana", "Hortifruti", "1un", "789123456092", 7, 15, ""),
    # Tomate (tipo_id=14)
    (14, "Tomate Cereja", "Hortifruti", "250g", "789123456093", 7, 15, ""),
    # Banana (tipo_id=15)
    (15, "Banana Nanica", "Hortifruti", "1kg", "789123456094", 7, 16, ""),
    (15, "Banana Prata", "Hortifruti", "1kg", "789123456141", 7, 16, ""),
    # Maçã (tipo_id=16)
    (16, "Maçã Gala", "Hortifruti", "1kg", "789123456129", 7, 16, ""),
    (16, "Maçã Verde", "Hortifruti", "1kg", "789123456095", 7, 16, ""),
    # Refrigerante (tipo_id=17)
    (17, "Coca-Cola", "Coca-Cola", "2L", "789123456020", 4, 9, ""),
    (17, "Pepsi", "PepsiCo", "2L", "789123456071", 4, 9, ""),
    (17, "Fanta Laranja", "Coca-Cola", "2L", "789123456021", 4, 9, ""),
    (17, "Guaraná Antarctica", "Ambev", "2L", "789123456073", 4, 9, ""),
    (17, "Sprite", "Coca-Cola", "2L", "789123456096", 4, 9, ""),
    (17, "Soda Limonada", "Schin", "2L", "789123456097", 4, 9, ""),
    # Suco (tipo_id=18, por exemplo)
    (18, "Suco de Uva Integral", "Aurora", "1L", "789123456098", 4, 10, ""),
    (18, "Suco de Laranja Natural", "Do Bem", "1L", "789123456099", 4, 10, ""),
    (18, "Suco de Maçã", "Del Valle", "1L", "789123456130", 4, 10, ""),
    # Sabão em Pó (tipo_id=19)
    (19, "Sabão em Pó Tixan", "Ypê", "1kg", "789123456100", 2, 4, ""),
    # Amaciante (tipo_id=20)
    (20, "Amaciante Fofo", "Fofo", "2L", "789123456101", 2, 4, ""),
    # Desinfetante (tipo_id=21)
    (21, "Desinfetante Pinho Sol", "Pinho Sol", "500ml", "789123456102", 2, 5, ""),
    # Detergente (tipo_id=22)
    (22, "Detergente Limão", "Ypê", "500ml", "789123456103", 2, 6, ""),
    # Esponja de Aço (tipo_id=23)
    (23, "Esponja de Aço Bombril", "Bombril", "8un", "789123456104", 2, 6, ""),
    # Shampoo (tipo_id=24)
    (24, "Shampoo Anticaspa", "Clear", "200ml", "789123456029", 3, 8, ""),
    (24, "Shampoo Nutritivo", "Pantene", "400ml", "789123456066", 3, 8, ""),
    (24, "Shampoo Infantil", "Johnson's", "200ml", "789123456067", 3, 8, ""),
    (24, "Shampoo Suave", "Johnson's", "200ml", "789123456105", 3, 8, ""),
    # Condicionador (tipo_id=25)
    (25, "Condicionador Suave", "Johnson's", "200ml", "789123456106", 3, 8, ""),
    # Sabonete (tipo_id=26)
    (26, "Sabonete Neutro", "Dove", "90g", "789123456031", 3, 7, ""),
    (26, "Sabonete Hidratante", "Nivea", "85g", "789123456068", 3, 7, ""),
    (26, "Sabonete Antibacteriano", "Protex", "85g", "789123456069", 3, 7, ""),
    (26, "Sabonete Infantil", "Granado", "90g", "789123456107", 3, 7, ""),
    # Creme Dental (tipo_id=27)
    (27, "Creme Dental Sorriso", "Colgate", "90g", "789123456108", 3, 7, ""),
    # Desodorante (tipo_id=28)
    (28, "Desodorante Roll-on", "Nivea", "50ml", "789123456109", 3, 7, ""),
    # Pão (tipo_id=29)
    (29, "Pão Francês", "Padaria do Zé", "10un", "789123456034", 5, 11, ""),
    (29, "Pão Francês Integral", "Padaria do Zé", "10un", "789123456110", 5, 11, ""),
    (29, "Pão de Forma", "Pullman", "500g", "789123456035", 5, 11, ""),
    # Bolo (tipo_id=30)
    (30, "Bolo de Chocolate com Recheio", "Bauducco", "400g", "789123456112", 5, 12, ""),
    (30, "Bolo de Cenoura com Cobertura", "Casa Suíça", "400g", "789123456113", 5, 12, ""),
    (30, "Bolo de Laranja", "Wickbold", "400g", "789123456131", 5, 12, ""),
    # Atum em Lata (tipo_id=31)
    (31, "Atum Sólido", "Gomes da Costa", "170g", "789123456114", 8, 17, ""),
    # Milho em Conserva (tipo_id=32)
    (32, "Milho Verde", "Quero", "200g", "789123456115", 8, 17, ""),
    # Ração para Cães (tipo_id=33)
    (33, "Ração para Cães Adultos", "Pedigree", "10kg", "789123456042", 9, 19, ""),
    (33, "Ração para Cães Filhotes", "Golden", "3kg", "789123456072", 9, 19, ""),
    (33, "Ração para Cães Sênior", "Premier", "10kg", "789123456118", 9, 19, ""),
    # Ração para Gatos (tipo_id=34)
    (34, "Ração para Gatos Castrados", "Whiskas", "10kg", "789123456119", 9, 19, ""),
    # Areia Sanitária (tipo_id=35)
    (35, "Areia Sanitária Sílica", "Pipicat", "4kg", "789123456120", 9, 19, ""),
    # Vassoura (tipo_id=36)
    (36, "Vassoura Multiuso", "Bettanin", "1un", "789123456121", 10, 20, ""),
    # Pano de Prato (tipo_id=37)
    (37, "Pano de Prato Decorado", "Santa Margarida", "3un", "789123456122", 10, 20, ""),
    # Balde (tipo_id=38)
    (38, "Balde Dobrável", "Plasútil", "10L", "789123456123", 10, 20, ""),
    # Escova de Dente (tipo_id=39)
    (39, "Escova de Dente Infantil", "Oral-B", "1un", "789123456124", 3, 7, ""),
    # Margarina (tipo_id=40)
    (40, "Margarina Light", "Qualy", "500g", "789123456125", 6, 14, ""),
    # Requeijão (tipo_id=41)
    (41, "Requeijão Cremoso", "Polenghi", "200g", "789123456126", 6, 14, ""),
    # Cenoura (tipo_id=42)
    (42, "Cenoura Orgânica", "Hortifruti", "1kg", "789123456127", 7, 15, ""),
    # Laranja (tipo_id=43)
    (43, "Laranja Lima", "Hortifruti", "1kg", "789123456128", 7, 16, ""),
    # Maçã (tipo_id=16) -- já incluída acima
]

# Exemplos de listas de compras
listas_exemplo = [
    (1, "Lista da Semana"),
    (2, "Jantar de Sexta-feira"),
]

# Itens das listas de compras: (lista_id, tipo_id, categoria_id, subcategoria_id, quantidade, data_adicao)
# Supondo que os produtos já foram inseridos e seus IDs são conhecidos
data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
lista_itens_exemplo = [
    # Lista da Semana (diversificada)
    (1, 1, 1, 1, 2, data_hoje),    # Arroz
    (1, 2, 1, 1, 1, data_hoje),    # Feijão
    (1, 3, 1, 3, 2, data_hoje),    # Macarrão
    (1, 4, 1, 2, 1, data_hoje),    # Açúcar
    (1, 6, 1, 1, 1, data_hoje),    # Óleo
    (1, 8, 1, 2, 1, data_hoje),    # Café
    (1, 9, 6, 14, 2, data_hoje),   # Leite
    (1, 10, 6, 13, 1, data_hoje),  # Queijo Mussarela
    (1, 13, 7, 15, 2, data_hoje),  # Alface
    (1, 14, 7, 15, 2, data_hoje),  # Tomate
    (1, 15, 7, 16, 6, data_hoje),  # Banana
    (1, 16, 7, 16, 4, data_hoje),  # Maçã
    (1, 17, 4, 9, 2, data_hoje),   # Refrigerante
    (1, 18, 4, 10, 2, data_hoje),  # Suco
    (1, 21, 2, 4, 1, data_hoje),   # Sabão em Pó
    (1, 22, 2, 4, 1, data_hoje),   # Amaciante
    (1, 24, 2, 6, 1, data_hoje),   # Detergente
    (1, 26, 3, 8, 1, data_hoje),   # Shampoo
    (1, 28, 3, 7, 2, data_hoje),   # Sabonete
    (1, 31, 5, 11, 10, data_hoje), # Pão
    (1, 33, 5, 12, 1, data_hoje),  # Bolo

    # Jantar de Sexta-feira (itens para preparar um jantar)
    (2, 1, 1, 1, 1, data_hoje),    # Arroz
    (2, 2, 1, 1, 1, data_hoje),    # Feijão
    (2, 3, 1, 3, 1, data_hoje),    # Macarrão
    (2, 10, 6, 13, 1, data_hoje),  # Queijo Mussarela
    (2, 11, 6, 13, 1, data_hoje),  # Presunto
    (2, 13, 7, 15, 1, data_hoje),  # Alface
    (2, 14, 7, 15, 1, data_hoje),  # Tomate
    (2, 15, 7, 16, 2, data_hoje),  # Banana
    (2, 16, 7, 16, 2, data_hoje),  # Maçã
    (2, 17, 4, 9, 2, data_hoje),   # Refrigerante
    (2, 18, 4, 10, 1, data_hoje),  # Suco
    (2, 31, 5, 11, 4, data_hoje),  # Pão
    (2, 33, 5, 12, 1, data_hoje),  # Bolo
]

# Supermercados de exemplo
supermercados_exemplo = [
    (1, "Carrefour", "Ouro Preto"),
    (2, "Supernosso", "Ouro Preto"),
]

# Carrinhos de compras: (id, nome, supermercado_id, lista_id, data_criacao)
from datetime import datetime
data_carrinho = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
carrinhos_exemplo = [
    (1, "Carrinho Jantar Sexta", 1, 2, data_carrinho),  # Carrinho para o jantar de sexta-feira, no Supermercado Central
]

# Itens do carrinho: (carrinho_id, produto_id, quantidade, preco_unit)
# Utilize os IDs reais dos produtos cadastrados na tabela produtos
carrinho_itens_exemplo = [
    # Exemplo: (1, produto_id, quantidade, preco_unit)
    (1, 1, 1, 22.90),   # Arroz Comum
    (1, 7, 1, 8.50),    # Feijão Preto
    (1, 13, 1, 5.99),   # Macarrão Espaguete
    (1, 25, 1, 12.00),  # Queijo Mussarela Fatiado
    (1, 29, 1, 10.00),  # Presunto Cozido
    (1, 37, 1, 3.50),   # Alface Crespa
    (1, 39, 1, 6.00),   # Tomate Cereja
    (1, 41, 2, 4.00),   # Banana Nanica
    (1, 43, 2, 7.00),   # Maçã Gala
    (1, 45, 2, 8.99),   # Coca-Cola
    (1, 49, 1, 9.50),   # Suco de Uva Integral
    (1, 53, 4, 2.00),   # Pão Francês
    (1, 57, 1, 15.00),  # Bolo de Chocolate com Recheio
]

# Gerar datas anteriores para os carrinhos
datas_carrinhos = [
    (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
    (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S"),
    (datetime.now() - timedelta(days=21)).strftime("%Y-%m-%d %H:%M:%S"),
    (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
]

# Novos carrinhos de compras: (id, nome, supermercado_id, lista_id, data_criacao)
carrinhos_exemplo += [
    (2, "Carrinho Semana Passada", 2, 1, datas_carrinhos[0]),
    (3, "Carrinho Quinzena", 1, 1, datas_carrinhos[1]),
    (4, "Carrinho Três Semanas", 2, 2, datas_carrinhos[2]),
    (5, "Carrinho Mês Passado", 1, 2, datas_carrinhos[3]),
]

# Produtos para os novos carrinhos (produto_id, quantidade base, preço base)
produtos_para_carrinhos = [
    (1, 1, 22.90),   # Arroz Comum
    (7, 1, 8.50),    # Feijão Preto
    (13, 1, 5.99),   # Macarrão Espaguete
    (25, 1, 12.00),  # Queijo Mussarela Fatiado
    (29, 1, 10.00),  # Presunto Cozido
    (37, 1, 3.50),   # Alface Crespa
    (39, 1, 6.00),   # Tomate Cereja
    (41, 2, 4.00),   # Banana Nanica
    (43, 2, 7.00),   # Maçã Gala
    (45, 2, 8.99),   # Coca-Cola
    (49, 1, 9.50),   # Suco de Uva Integral
    (53, 4, 2.00),   # Pão Francês
    (57, 1, 15.00),  # Bolo de Chocolate com Recheio
]

# Gerar itens para cada novo carrinho com pequenas variações de preço e quantidade
carrinho_itens_exemplo_extra = []
historico_precos_exemplo = []

for idx, carrinho in enumerate(carrinhos_exemplo[1:], start=2):  # pula o primeiro carrinho já existente
    supermercado_id = carrinho[2]
    data_carrinho = carrinho[4]
    # Seleciona aleatoriamente alguns produtos para cada carrinho
    produtos_escolhidos = produtos_para_carrinhos.copy()
    random.shuffle(produtos_escolhidos)
    produtos_escolhidos = produtos_escolhidos[:randint(6, 10)]
    for produto_id, quantidade_base, preco_base in produtos_escolhidos:
        quantidade = max(1, quantidade_base + randint(-1, 2))
        variacao = uniform(-0.5, 1.5) + (supermercado_id - 1) * 0.2
        preco_unit = round(preco_base + variacao, 2)
        carrinho_itens_exemplo_extra.append((idx, produto_id, quantidade, preco_unit))
        historico_precos_exemplo.append((produto_id, supermercado_id, preco_unit, data_carrinho))

# Adicione ao histórico de preços também os itens do carrinho já existente
for item in carrinho_itens_exemplo:
    produto_id = item[1]
    preco_unit = item[3]
    supermercado_id = 1  # Carrinho 1 é do supermercado 1
    data_carrinho = data_carrinho  # data_carrinho já definida anteriormente
    historico_precos_exemplo.append((produto_id, supermercado_id, preco_unit, data_carrinho))

# Criação das tabelas no banco de dados
def criar_tabelas():
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

def inserir_exemplos():
    conn = conectar()
    cursor = conn.cursor()
    # Categorias
    for cat in categorias_exemplo:
        cursor.execute("INSERT OR IGNORE INTO categorias (id, nome) VALUES (?, ?)", (cat[0], cat[1]))
    # Subcategorias
    for sub in subcategorias_exemplo:
        cursor.execute("INSERT OR IGNORE INTO subcategorias (id, nome, categoria_id) VALUES (?, ?, ?)", sub)
    # Tipos de produto
    for tipo in tipos_produto_exemplo:
        cursor.execute(
            "INSERT OR IGNORE INTO tipos_produto (nome, categoria_id, subcategoria_id) VALUES (?, ?, ?)",
            tipo
        )
    conn.commit()
    conn.close()
    print("Tipos, categorias e subcategorias de exemplo cadastradas com sucesso!")

def inserir_produtos_exemplo():
    conn = conectar()
    cursor = conn.cursor()
    # Produtos (busca o tipo_id correto)
    for p in produtos_exemplo:
        tipo_id = p[0]  # Agora pega o tipo_id diretamente
        cursor.execute(
            "SELECT id FROM tipos_produto WHERE id=?",
            (tipo_id,)
        )
        tipo_id_row = cursor.fetchone()
        if not tipo_id_row:
            print(f"[ERRO] Tipo de produto não encontrado: id={tipo_id}")
            continue
        cursor.execute(
            "INSERT INTO produtos (tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (tipo_id, p[1], p[2], p[3], p[4], p[5], p[6], p[7])
        )
    conn.commit()
    conn.close()
    print("Produtos de exemplo cadastrados com sucesso!")

def inserir_listas_exemplo():
    conn = conectar()
    cursor = conn.cursor()
    # Listas de compras
    for lista in listas_exemplo:
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT OR IGNORE INTO listas (id, nome, data_criacao) VALUES (?, ?, ?)", (lista[0], lista[1], data_criacao))
    # Itens das listas
    for item in lista_itens_exemplo:
        cursor.execute(
            "INSERT INTO lista_itens (lista_id, tipo_id, categoria_id, subcategoria_id, quantidade, data_adicao) VALUES (?, ?, ?, ?, ?, ?)",
            item
        )
    conn.commit()
    conn.close()
    print("Listas de compras de exemplo cadastradas com sucesso!")

def inserir_carrinhos_exemplo():
    conn = conectar()
    cursor = conn.cursor()
    # Supermercados
    for sup in supermercados_exemplo:
        cursor.execute("INSERT OR IGNORE INTO supermercados (id, nome, bairro) VALUES (?, ?, ?)", sup)
    # Carrinhos
    for carrinho in carrinhos_exemplo:
        cursor.execute(
            "INSERT OR IGNORE INTO carrinhos (id, nome, supermercado_id, lista_id, data_criacao) VALUES (?, ?, ?, ?, ?)",
            carrinho
        )
    conn.commit()
    conn.close()
    print("Carrinho de compras de exemplo cadastrado com sucesso!")

def inserir_carrinho_itens_exemplo():
    conn = conectar()
    cursor = conn.cursor()
    # Itens do carrinho principal
    for item in carrinho_itens_exemplo:
        cursor.execute(
            "INSERT INTO carrinho_itens (carrinho_id, produto_id, quantidade, preco_unit) VALUES (?, ?, ?, ?)",
            item
        )
    # Itens dos carrinhos extras
    for item in carrinho_itens_exemplo_extra:
        cursor.execute(
            "INSERT INTO carrinho_itens (carrinho_id, produto_id, quantidade, preco_unit) VALUES (?, ?, ?, ?)",
            item
        )
    conn.commit()
    conn.close()
    print("Itens dos carrinhos cadastrados com sucesso!")

def inserir_historico_precos_exemplo():
    conn = conectar()
    cursor = conn.cursor()
    for item in historico_precos_exemplo:
        cursor.execute(
            "INSERT INTO historico_precos (produto_id, supermercado_id, preco, data) VALUES (?, ?, ?, ?)",
            item
        )
    conn.commit()
    conn.close()
    print("Histórico de preços cadastrado com sucesso!")

# No main, chame também:
if __name__ == "__main__":
    criar_tabelas()
    inserir_exemplos()
    inserir_produtos_exemplo()
    inserir_listas_exemplo()
    inserir_carrinhos_exemplo()
    inserir_carrinho_itens_exemplo()
    inserir_historico_precos_exemplo()