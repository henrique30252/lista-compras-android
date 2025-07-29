from database_app import (
    criar_tabelas,
    cadastrar_produto,
    listar_produtos,
    alterar_produto,
    excluir_produto,
    cadastrar_supermercado,
    listar_supermercados,
    alterar_supermercado,
    excluir_supermercado,
    criar_lista,
    listar_listas,
    visualizar_lista,
    alterar_lista,
    excluir_lista,
    adicionar_item_lista,
    alterar_item_lista,
    excluir_item_lista,
    criar_carrinho,
    listar_carrinhos,
    visualizar_carrinho,
    adicionar_item_carrinho,
    alterar_item_carrinho,
    excluir_item_carrinho,
    alterar_carrinho,
    excluir_carrinho,
    listar_historico_precos,
    cadastrar_categoria,
    cadastrar_subcategoria,
    listar_categorias_e_subcategorias,
    alterar_categoria,
    excluir_categoria,
    alterar_subcategoria,
    excluir_subcategoria
)

def menu_principal():
    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1 - Produtos")
        print("2 - Supermercados")
        print("3 - Listas de Compras")
        print("4 - Carrinhos")
        print("5 - Categorias e Subcategorias")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            menu_produtos()
        elif opcao == "2":
            menu_supermercados()
        elif opcao == "3":
            menu_listas_compras()
        elif opcao == "4":
            menu_carrinhos()
        elif opcao == "5":
            menu_categorias()
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

def menu_produtos():
    while True:
        print("\n=== PRODUTOS ===")
        print("1 - Cadastrar produto")
        print("2 - Listar produtos")
        print("3 - Alterar produto")
        print("4 - Excluir produto")
        print("5 - Histórico de Preços")  # Adiciona opção aqui
        print("0 - Voltar")

        opcao = input("Escolha uma opção: ")
        try:
            if opcao == "1":
                cadastrar_produto()
            elif opcao == "2":
                listar_produtos()
            elif opcao == "3":
                alterar_produto()
            elif opcao == "4":
                excluir_produto()
                print("Produto excluído com sucesso!")
            elif opcao == "5":
                menu_historico_precos()  # Chama o menu de histórico de preços aqui
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
        except Exception as e:
            print(f"Erro: {e}")

def menu_supermercados():
    while True:
        print("\n=== SUPERMERCADOS ===")
        print("1 - Cadastrar supermercado")
        print("2 - Listar supermercados")
        print("3 - Alterar supermercado")
        print("4 - Excluir supermercado")
        print("0 - Voltar")

        opcao = input("Escolha uma opção: ")
        try:
            if opcao == "1":
                cadastrar_supermercado()
            elif opcao == "2":
                listar_supermercados()
            elif opcao == "3":
                alterar_supermercado()  # Não passa supermercado_id
            elif opcao == "4":
                excluir_supermercado()  # Não passa supermercado_id
                print("Supermercado excluído com sucesso!")
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
        except Exception as e:
            print(f"Erro: {e}")

def menu_listas_compras():
    while True:
        print("\n=== LISTAS DE COMPRAS ===")
        print("1 - Criar lista")
        print("2 - Listar listas")
        print("3 - Alterar lista")
        print("4 - Excluir lista")
        print("5 - Adicionar item na lista")
        print("6 - Visualizar itens da lista")
        print("7 - Alterar item da lista")
        print("8 - Excluir item da lista")
        print("0 - Voltar")

        opcao = input("Escolha uma opção: ")
        try:
            if opcao == "1":
                criar_lista()
            elif opcao == "2":
                listar_listas()
            elif opcao == "3":
                alterar_lista()  # Não passa lista_id
            elif opcao == "4":
                excluir_lista()  # Não passa lista_id
            elif opcao == "5":
                adicionar_item_lista()  # Não passa argumentos
                print("Item adicionado à lista com sucesso!")
            elif opcao == "6":
                visualizar_lista()  # Não passa lista_id
            elif opcao == "7":
                alterar_item_lista()  # Não passa argumentos
                print("Item alterado com sucesso!")
            elif opcao == "8":
                excluir_item_lista()  # Não passa argumentos
                print("Item excluído da lista com sucesso!")
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
        except Exception as e:
            print(f"Erro: {e}")

def menu_carrinhos():
    while True:
        print("\n=== CARRINHOS ===")
        print("1 - Criar carrinho")
        print("2 - Listar carrinhos")
        print("3 - Alterar carrinho")
        print("4 - Excluir carrinho")
        print("5 - Adicionar item ao carrinho")
        print("6 - Visualizar carrinho")
        print("7 - Alterar item do carrinho")
        print("8 - Excluir item do carrinho")
        print("0 - Voltar")

        opcao = input("Escolha uma opção: ")
        try:
            if opcao == "1":
                criar_carrinho()
            elif opcao == "2":
                listar_carrinhos()
            elif opcao == "3":
                alterar_carrinho()
            elif opcao == "4":
                excluir_carrinho()
                print("Carrinho excluído com sucesso!")
            elif opcao == "5":
                adicionar_item_carrinho()
                print("Item adicionado ao carrinho com sucesso!")
            elif opcao == "6":
                visualizar_carrinho()
            elif opcao == "7":
                alterar_item_carrinho()
                print("Item do carrinho alterado com sucesso!")
            elif opcao == "8":
                excluir_item_carrinho()
                print("Item excluído do carrinho com sucesso!")
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
        except Exception as e:
            print(f"Erro: {e}")

def menu_historico_precos():
    while True:
        print("\n=== HISTÓRICO DE PREÇOS ===")
        print("1 - Listar histórico de preços")
        print("0 - Voltar")
        opcao = input("Escolha uma opção: ")
        try:
            if opcao == "1":
                listar_historico_precos()
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
        except Exception as e:
            print(f"Erro: {e}")

def menu_categorias():
    while True:
        print("\n=== CATEGORIAS E SUBCATEGORIAS ===")
        print("1 - Listar categorias e subcategorias")
        print("2 - Cadastrar categoria")
        print("3 - Alterar categoria")
        print("4 - Excluir categoria")
        print("5 - Cadastrar subcategoria")
        print("6 - Alterar subcategoria")
        print("7 - Excluir subcategoria")
        print("0 - Voltar")

        opcao = input("Escolha uma opção: ")
        try:
            if opcao == "1":
                listar_categorias_e_subcategorias()
            elif opcao == "2":
                cadastrar_categoria()
            elif opcao == "3":
                alterar_categoria()
            elif opcao == "4":
                excluir_categoria()
            elif opcao == "5":
                cadastrar_subcategoria()
            elif opcao == "6":
                alterar_subcategoria()
            elif opcao == "7":
                excluir_subcategoria()
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    criar_tabelas()
    menu_principal()
