# 💰 MELHORIA: Sistema de Preços e Orçamento

## 🎯 Funcionalidades a Implementar:

### 1. **Histórico de Preços por Produto/Supermercado**
- Rastrear preços por produto em cada supermercado
- Gráficos de evolução de preços
- Alertas de variação de preço
- Comparativo entre supermercados

### 2. **Orçamento de Lista**
- Definir orçamento máximo para lista
- Acompanhar gasto em tempo real
- Alertas quando ultrapassar orçamento
- Sugestões de produtos mais baratos

### 3. **Calculadora de Carrinho**
- Total automático do carrinho
- Desconto/cupons
- Comparativo de preços entre supermercados
- Economia estimada

### 4. **Relatórios de Compras**
- Gastos mensais por categoria
- Produtos mais comprados
- Supermercados mais econômicos
- Tendências de preços

## 🔧 Implementação Técnica:

### Tabelas Necessárias:
```sql
-- Histórico de preços
CREATE TABLE historico_precos (
    id INTEGER PRIMARY KEY,
    produto_id INTEGER,
    supermercado_id INTEGER,
    preco REAL,
    data_preco DATE,
    usuario_id INTEGER
);

-- Orçamentos de listas
CREATE TABLE orcamentos_lista (
    id INTEGER PRIMARY KEY,
    lista_id INTEGER,
    valor_orcamento REAL,
    valor_gasto REAL,
    data_criacao DATE
);
```

### Funcionalidades na Interface:
- Campo de preço ao adicionar item ao carrinho
- Tela de comparativo de preços
- Dashboard com estatísticas
- Notificações de orçamento
