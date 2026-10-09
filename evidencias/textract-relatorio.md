# Evidência: Amazon Textract na ata digitalizada

- Arquivo: `ata_resultados_vendas_novos_dados.png`
- Operação: `AnalyzeDocument` com `TABLES` e `LAYOUT`
- Região: `us-east-1`
- Linhas detectadas: 70
- Palavras detectadas: 340
- Confiança média das linhas: 97.2%

## Blocos de layout

- `LAYOUT_FOOTER`: 3
- `LAYOUT_LIST`: 2
- `LAYOUT_SECTION_HEADER`: 5
- `LAYOUT_TABLE`: 1
- `LAYOUT_TEXT`: 20
- `LAYOUT_TITLE`: 1

## Tabelas reconstruídas

**Tabela 1** (4 linhas x 2 colunas)

| Data: | 15 de janeiro de 2026 |
|---|---|
| Horario: | 09h00 as 11h10 |
| Local: | Sala Comercial 3 Matriz |
| Objetivo: | Revisao dos resultados do segundo semestre e definicao de metas. |

**Tabela 2** (7 linhas x 4 colunas)

| Indicador | Realizado | Meta | Variacao |
|---|---|---|---|
| Faturamento | R$ 9,85 mi | R$ 9,20 mi | +7,1% |
| Pedidos faturados | 41.320 | 38.000 | +8,7% |
| Ticket medio | R$ 238,40 | R$ 247,00 | -3,5% |
| Taxa de conversao | 21,8% | 20,0% | +1,8 p.p. |
| Novos clientes | 1.460 | 1.250 | +16,8% |
| Churn de clientes | 6,9% | ate 7,5% | melhor que meta |

## Palavras classificadas como manuscritas

Nenhuma palavra marcada como `HANDWRITING`.

## Prazos das deliberações

- 1. Expandir equipe de vendas do Norte. Responsavel: Paulo Mendes. Prazo: 28/02/2026
  - confiança da linha: 97.9%
  - datas lidas: `28/02/2026` (98.36%)
- 2. Revisar politica de desconto por margem. Responsavel: Renata Souza. Prazo: 12/02/2026.
  - confiança da linha: 98.39%
  - datas lidas: `12/02/2026.` (92.45%)
- 3. Criar campanha para elevar ticket medio. Responsavel: Diego Alves. Prazo: 20/02/2026.
  - confiança da linha: 98.43%
  - datas lidas: `20/02/2026.` (96.3%)
- 4. Implantar painel semanal de conversao. Responsavel: Carla Ribeiro. Prazo: 05/02/2026.
  - confiança da linha: 98.09%
  - datas lidas: `05/02/2026.` (97.49%)

## Linhas abaixo de 85% de confiança

- `prioritaria` (76.63%)

## Texto completo, linha a linha

```text
VENDAS S.A.
ATA DE REUNIAO COMERCIAL
RESULTADOS DO 2o SEMESTRE DADOS SIMULADOS
Data:
15 de janeiro de 2026
Horario:
09h00 as 11h10
Local:
Sala Comercial 3 Matriz
Objetivo:
Revisao dos resultados do segundo semestre e definicao de metas.
PARTICIPANTES
Marina Lopes (Diretoria Comercial), Paulo Mendes (Gerencia Nacional), Carla Ribeiro (Operacoes),
Diego Alves (Marketing), Renata Souza (Controladoria) e supervisores regionais.
1. RESUMO EXECUTIVO
0 faturamento consolidado do semestre atingiu R$ 9,85 milhoes, superando a meta em 7,1%. 0
crescimento foi sustentado por novos contratos corporativos, maior volume no canal digital e
recuperacao das vendas nas regioes Sul e Nordeste.
2. INDICADORES COMERCIAIS
conferir CRM
Indicador
Realizado
Meta
Variacao
Faturamento
R$ 9,85 mi
R$ 9,20 mi
+7,1%
Pedidos faturados
41.320
38.000
+8,7%
Ticket medio
R$ 238,40
R$ 247,00
-3,5%
Taxa de conversao
21,8%
20,0%
+1,8 p.p.
Novos clientes
1.460
1.250
+16,8%
Churn de clientes
6,9%
ate 7,5%
melhor que meta
3. DESEMPENHO POR REGIAO
Sudeste: R$ 4,05 mi 41,1% do faturamento crescimento de 5,4%.
Sul: R$ 2,10 mi 21,3% do faturamento crescimento de 12,8%.
Nordeste: R$ 1,75 mi 17,8% do faturamento crescimento de 15,2%.
Centro-Oeste: R$ 1,15 mi 11,7% do faturamento crescimento de 3,6%.
Norte: R$ 0,80 mi 8,1% do faturamento queda de 2,1%.
4. PRINCIPAIS OBSERVACOES
1. A campanha de reativacao recuperou 286 clientes inativos.
2. 0 canal digital respondeu por 34% dos novos pedidos.
3. A linha de servicos premium cresceu 19%, mas apresentou maior ciclo de fechamento.
4. A regiao Norte ficou abaixo da meta devido a atrasos logisticos e menor cobertura comercial.
5. DELIBERACOES E PLANO DE ACAO
1. Expandir equipe de vendas do Norte. Responsavel: Paulo Mendes. Prazo: 28/02/2026
prioritaria
2. Revisar politica de desconto por margem. Responsavel: Renata Souza. Prazo: 12/02/2026.
3. Criar campanha para elevar ticket medio. Responsavel: Diego Alves. Prazo: 20/02/2026.
4. Implantar painel semanal de conversao. Responsavel: Carla Ribeiro. Prazo: 05/02/2026.
Nada mais havendo a tratar, a reuniao foi encerrada as 11h10. Esta ata foi redigida para fins de
treinamento e validacao de rotinas de leitura documental.
Marina Lopes
Paulo Mendes
DOCUMENTO FICTICIO
```
