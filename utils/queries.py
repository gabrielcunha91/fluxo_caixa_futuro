

GET_CASAS = """
WITH empresas_normalizadas AS (
  SELECT
    CASE 
      WHEN ID IN (161, 162) THEN 149
      ELSE ID
    END AS ID_Casa_Normalizada,
    NOME_FANTASIA,
    FK_GRUPO_EMPRESA,
    BIT_SOCIOS_EXTERNOS
  FROM T_EMPRESAS
)
SELECT
  te.ID_Casa_Normalizada AS ID_Casa,
  te2.NOME_FANTASIA AS Casa,
  te.BIT_SOCIOS_EXTERNOS as Bit_Socios_Externos
FROM empresas_normalizadas te
LEFT JOIN T_EMPRESAS te2 ON te.ID_Casa_Normalizada = te2.ID
WHERE te.FK_GRUPO_EMPRESA = 100
GROUP BY te.ID_Casa_Normalizada, te2.NOME_FANTASIA
ORDER BY te2.NOME_FANTASIA
"""

GET_EXTRATO_ZIG = """
WITH extrato_normalizado AS (
  SELECT
    ID AS ID_Extrato,
    CASE 
      WHEN ID_LOJA_ZIG IN ('95a1ebd7-3da4-4121-a4eb-f9add8caa749', '544ef5bf-18b2-4081-977c-7733f0d6a8b8') THEN 149
      ELSE ID_LOJA_ZIG
    END AS ID_Loja_Normalizada,
    DESCRICAO,
    DATA_LIQUIDACAO,
    DATA_TRANSACAO,
    VALOR
  FROM T_EXTRATO_FINANCEIRO_ZIG
)
SELECT 
  en.ID_Extrato,
  te.ID AS ID_Casa,
  te.NOME_FANTASIA AS Casa,
  en.DESCRICAO AS Descricao,
  en.DATA_LIQUIDACAO AS Data_Liquidacao,
  en.DATA_TRANSACAO AS Data_Transacao,
  en.VALOR AS Valor
FROM extrato_normalizado en
INNER JOIN T_EMPRESAS te ON en.ID_Loja_Normalizada = te.ID_ZIGPAY
ORDER BY te.NOME_FANTASIA ASC, en.DATA_LIQUIDACAO DESC
"""

GET_ZIG_FATURAMENTO = """
WITH faturamento_normalizado AS (
  SELECT
    CASE 
      WHEN FK_LOJA IN (161, 162) THEN 149
      ELSE FK_LOJA
    END AS ID_Casa,
    DATA,
    VALOR,
    TIPO_PAGAMENTO
  FROM T_ZIG_FATURAMENTO
  WHERE DATA >= '2024-06-01'
)
SELECT
  fn.ID_Casa,
  te.NOME_FANTASIA AS Casa,
  fn.DATA AS Data_Venda,
  fn.VALOR AS Valor,
  fn.TIPO_PAGAMENTO AS Tipo_Pagamento
FROM faturamento_normalizado fn
LEFT JOIN T_EMPRESAS te ON fn.ID_Casa = te.ID
"""

GET_PARCELAS_RECEITAS_EXTRAORDINARIAS = """
SELECT 
vpa.ID as 'ID_Receita',
te.ID as 'ID_Casa',
te.NOME_FANTASIA as 'Casa',
trec.NOME as 'Cliente',
tre.DATA_OCORRENCIA as 'Data_Ocorrencia',
vpa.DATA_VENCIMENTO as 'Vencimento_Parcela',
vpa.DATA_RECEBIMENTO as 'Recebimento_Parcela',
vpa.VALOR_PARCELA as 'Valor_Parcela',
tre.NUM_DOCUMENTACAO as 'Doc_NF',
trec2.CLASSIFICACAO as 'Classif_Receita',
tfdp.DESCRICAO as 'Forma_Pagamento',
tsp.DESCRICAO as 'Status_Pgto',
tcb.NOME_DA_CONTA as 'Conta_Bancaria',
tre.OBSERVACOES as 'Observacoes'
FROM View_Parcelas_Agrupadas vpa
INNER JOIN T_EMPRESAS te ON (vpa.FK_EMPRESA = te.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS tre ON (vpa.ID = tre.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLIENTE trec ON (vpa.FK_CLIENTE = trec.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLASSIFICACAO trec2 ON (tre.FK_CLASSIFICACAO = trec2.ID)
LEFT JOIN T_FORMAS_DE_PAGAMENTO tfdp ON (tre.FK_FORMA_PAGAMENTO = tfdp.ID)
LEFT JOIN T_STATUS_PAGAMENTO tsp ON (tre.FK_STATUS_PGTO = tsp.ID)
LEFT JOIN T_CONTAS_BANCARIAS tcb ON (tre.FK_CONTA_BANCARIA = tcb.ID)
WHERE vpa.DATA_VENCIMENTO IS NOT NULL
ORDER BY vpa.DATA_RECEBIMENTO DESC
"""


GET_CUSTOS_BLUEME_SEM_PARCELAMENTO = """
SELECT 
tdr.ID as 'ID_Despesa',
te.ID as 'ID_Casa',
te.NOME_FANTASIA as 'Casa',
tf.CORPORATE_NAME as 'Fornecedor',
tdr.VALOR_LIQUIDO as 'Valor',
tdr.VENCIMENTO as 'Data_Vencimento',
tc.`DATA` as 'Previsao_Pgto',
tc2.`DATA` as 'Realizacao_Pgto',    
tdr.COMPETENCIA as 'Data_Competencia',
tdr.LANCAMENTO as 'Data_Lancamento',
tfdp.DESCRICAO as 'Forma_Pagamento',
tccg.DESCRICAO as 'Class_Cont_1',
tccg2.DESCRICAO as 'Class_Cont_2',
tdr.NF as 'Doc_NF',
tscd.DESCRICAO as 'Status_Conf_Document',
tsad.DESCRICAO as 'Status_Aprov_Diret',
tsac.DESCRICAO as 'Status_Aprov_Caixa',
CASE
	WHEN tsp.DESCRICAO IS NULL THEN "Pendente"
	ELSE tsp.DESCRICAO 
END as 'Status_Pgto',
tcb.NOME_DA_CONTA as 'Conta_Bancaria',
tdr.FK_LOJA_CNPJ as 'CNPJ_Loja'
FROM T_DESPESA_RAPIDA tdr
INNER JOIN T_EMPRESAS te ON (tdr.FK_LOJA = te.ID)
LEFT JOIN T_CONTAS_BANCARIAS tcb ON (tdr.FK_CONTA_BANCARIA = tcb.ID)
LEFT JOIN T_FORMAS_DE_PAGAMENTO tfdp ON (tdr.FK_FORMA_PAGAMENTO = tfdp.ID)
LEFT JOIN T_FORNECEDOR tf ON (tdr.FK_FORNECEDOR = tf.ID)
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON (tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = tccg.ID)
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON (tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID)
LEFT JOIN T_STATUS_CONFERENCIA_DOCUMENTACAO tscd ON (tdr.FK_CONFERENCIA_DOCUMENTACAO = tscd.ID)
LEFT JOIN T_STATUS_APROVACAO_DIRETORIA tsad ON (tdr.FK_APROVACAO_DIRETORIA = tsad.ID)
LEFT JOIN T_STATUS_APROVACAO_CAIXA tsac ON (tdr.FK_APROVACAO_CAIXA = tsac.ID)
LEFT JOIN T_STATUS_PAGAMENTO tsp ON (tdr.FK_STATUS_PGTO = tsp.ID)
LEFT JOIN T_CALENDARIO tc ON (tdr.PREVISAO_PAGAMENTO = tc.ID)	
LEFT JOIN T_CALENDARIO tc2 ON (tdr.FK_DATA_REALIZACAO_PGTO = tc2.ID)
LEFT JOIN T_DEPESA_PARCELAS tdp ON (tdp.FK_DESPESA = tdr.ID)
WHERE 
    te.ID IS NOT NULL
    AND tdp.FK_DESPESA IS NULL
    AND (tdr.FK_DESPESA_TEKNISA IS NULL OR tdr.BIT_DESPESA_TEKNISA_PENDENTE = 1)
    AND (tdr.FK_FORMA_PAGAMENTO != 109 OR tdr.FK_FORMA_PAGAMENTO IS NULL)
ORDER BY 
    tc2.`DATA` DESC
"""


GET_CUSTOS_BLUEME_COM_PARCELAMENTO = """
  SELECT
    tdp.ID as 'ID_Parcela',
    tdr.ID as 'ID_Despesa',
    te.NOME_FANTASIA as 'Casa',
    te.ID as 'ID_Casa',
    tdr.FK_LOJA_CNPJ as 'CNPJ_Loja',
    tf.CORPORATE_NAME as 'Fornecedor',
    CASE
        WHEN tdp.FK_DESPESA IS NOT NULL
            THEN 'True'
        ELSE 'False'
    END AS 'Parcelamento',
    CASE 
        WHEN tdp.FK_DESPESA IS NOT NULL
            THEN COUNT(tdp.ID) OVER (PARTITION BY tdr.ID)
        ELSE NULL 
    END AS 'Qtd_Parcelas',
    tdp.PARCELA as 'Num_Parcela',
    tdp.VALOR as 'Valor_Parcela',
    tdp.`DATA` as 'Vencimento_Parcela',
    tc.`DATA` AS 'Previsao_Parcela',
    tc2.`DATA` AS 'Realiz_Parcela',
    tdr.VALOR_PAGAMENTO as 'Valor_Original',
    tdr.VALOR_LIQUIDO as 'Valor_Liquido',
    STR_TO_DATE(tdr.LANCAMENTO, '%Y-%m-%d') as 'Data_Lancamento',
    tfdp.DESCRICAO as 'Forma_Pagamento',
    tdr.NF as 'Doc_NF',
    tccg.DESCRICAO as 'Class_Cont_1',
    tccg2.DESCRICAO as 'Class_Cont_2',
    tscd.DESCRICAO as 'Status_Conf_Document',
    tsad.DESCRICAO as 'Status_Aprov_Diret',
    tsac.DESCRICAO as 'Status_Aprov_Caixa',
    CASE
        WHEN tdp.PARCELA_PAGA = 1 
            THEN 'Parcela_Paga'
        ELSE 'Parcela_Pendente'
    END as 'Status_Pgto',
    tcb.NOME_DA_CONTA as 'Conta_Bancaria'
  FROM 
    T_DESPESA_RAPIDA tdr
  INNER JOIN T_EMPRESAS te ON (tdr.FK_LOJA = te.ID)
  LEFT JOIN T_FORMAS_DE_PAGAMENTO tfdp ON (tdr.FK_FORMA_PAGAMENTO = tfdp.ID)
  LEFT JOIN T_FORNECEDOR tf ON (tdr.FK_FORNECEDOR = tf.ID)
  LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON (tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = tccg.ID)
  LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON (tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID)
  LEFT JOIN T_STATUS_CONFERENCIA_DOCUMENTACAO tscd ON (tdr.FK_CONFERENCIA_DOCUMENTACAO = tscd.ID)
  LEFT JOIN T_STATUS_APROVACAO_DIRETORIA tsad ON (tdr.FK_APROVACAO_DIRETORIA = tsad.ID)
  LEFT JOIN T_STATUS_APROVACAO_CAIXA tsac ON (tdr.FK_APROVACAO_CAIXA = tsac.ID)
  LEFT JOIN T_STATUS_PAGAMENTO tsp ON (tdr.FK_STATUS_PGTO = tsp.ID)
  LEFT JOIN T_DEPESA_PARCELAS tdp ON (tdp.FK_DESPESA = tdr.ID)
  LEFT JOIN T_CONTAS_BANCARIAS tcb ON (tdp.FK_CONTA_BANCARIA = tcb.ID)
  LEFT JOIN T_CALENDARIO tc ON (tdp.FK_PREVISAO_PGTO = tc.ID)
  LEFT JOIN T_CALENDARIO tc2 ON (tdp.FK_DATA_REALIZACAO_PGTO = tc2.ID)
  WHERE 
    tdp.FK_DESPESA IS NOT NULL
    AND (tdr.FK_DESPESA_TEKNISA IS NULL OR tdr.BIT_DESPESA_TEKNISA_PENDENTE = 1)
  ORDER BY 
    tc2.`DATA` DESC
"""

GET_EXTRATOS_BANCARIOS = """
SELECT
teb.ID as 'ID_Extrato_Bancario',
tcb.ID as 'ID_Conta_Bancaria',
tcb.NOME_DA_CONTA as 'Nome_Conta_Bancaria',
te.ID as 'ID_Casa',
te.NOME_FANTASIA as 'Casa',
teb.DATA_TRANSACAO as 'Data_Transacao',
CASE 
    WHEN teb.FK_TIPO_CREDITO_DEBITO = 100 THEN 'CREDITO'
    ELSE 'DEBITO'
END as 'Tipo_Credito_Debito',
teb.DESCRICAO_TRANSACAO as 'Descricao_Transacao',
teb.VALOR as 'Valor'
FROM T_EXTRATOS_BANCARIOS teb
INNER JOIN T_CONTAS_BANCARIAS tcb ON (teb.FK_CONTA_BANCARIA = tcb.ID)
INNER JOIN T_EMPRESAS te ON (tcb.FK_LOJA = te.ID)
WHERE teb.DESCRICAO_TRANSACAO NOT LIKE '%RESG AUTOMATICO%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%APLICACAO AUTOMATICA%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%APLIC.AUTOM.INVESTFACIL*%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%RESG.AUTOM.INVEST FACIL*%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%RESGATE INVEST FACIL%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%APLICACAO CONTAMAX%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%Pix Enviado-Conta Transacional%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%RESGATE CONTAMAX AUTOMATICO%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%APLIC.INVEST FACIL%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%RENTAB.INVEST FACILCRED*%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%BB RENDE FACIL - RENDE FACIL%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%BB RENDE FCIL - RENDE FACIL%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%BB RENDE FCIL%'
ORDER BY teb.DATA_TRANSACAO DESC
"""

GET_MUTUOS = """
SELECT
tm.ID as 'Mutuo_ID',
tm.`DATA` as 'Data_Mutuo',
te.ID as 'ID_Casa_Saida',
te.NOME_FANTASIA as 'Casa_Saida',
te2.ID as 'ID_Casa_Entrada',
te2.NOME_FANTASIA as 'Casa_Entrada',
tm.VALOR as 'Valor',
tm.TAG_FATURAM_ZIG as 'Tag_Faturam_Zig',
tm.OBSERVACOES as 'Observacoes'
FROM T_MUTUOS tm 
LEFT JOIN T_EMPRESAS te ON (tm.FK_LOJA_SAIDA = te.ID)
LEFT JOIN T_EMPRESAS te2 ON (tm.FK_LOJA_ENTRADA = te2.ID)
ORDER BY tm.`DATA` DESC
"""

GET_TESOURARIA = """
SELECT 
ttt.ID as 'ID_Transacao_Tesouraria',
te2.ID as 'ID_Casa',
te2.NOME_FANTASIA as 'Casa',
ttt.FK_EMPRESA_TESOURARIA as 'ID_Empresa_Tesouraria',
te.NOME_FANTASIA as 'Empresa_Tesouraria',
ttt.DATA_TRANSACAO as 'Data_Transacao',
ttt.VALOR as 'Valor',
ttt.DESCRICAO as 'Descricao'
FROM T_TESOURARIA_TRANSACOES ttt 
LEFT JOIN T_EMPRESAS te ON (ttt.FK_EMPRESA_TESOURARIA = te.ID)
LEFT JOIN T_EMPRESAS te2 ON (ttt.FK_LOJA = te2.ID)
ORDER BY ttt.ID DESC
"""

GET_AJUSTES_CONCILIACAO = """
SELECT 
tac.FK_EMPRESA AS 'ID_Casa',
te.NOME_FANTASIA as 'Casa',
tac.DATA_AJUSTE AS 'Data_Ajuste',
tac.VALOR AS 'Valor',
tac.DESCRICAO AS 'Descrição'
FROM T_AJUSTES_CONCILIACAO tac
INNER JOIN T_EMPRESAS te ON (tac.FK_EMPRESA = te.ID)
"""

GET_BLOQUEIOS_JUDICIAIS = """
SELECT
tbj.ID as 'ID_Bloqueio',
te.ID as 'ID_Casa',
te.NOME_FANTASIA as 'Casa',
tbj.DATA_TRANSACAO as 'Data_Transacao',
tbj.VALOR as 'Valor',
tbj.OBSERVACAO as 'Observacao'
FROM T_BLOQUEIOS_JUDICIAIS tbj 
LEFT JOIN T_EMPRESAS te ON (tbj.FK_EMPRESA = te.ID)
"""


GET_TIPO_CLASS_CONT_2 = """
SELECT
tccg2.ID as 'ID_Class_Cont_2',
tccg2.DESCRICAO as 'Class_Cont_2',
tccg.ID as 'ID_Class_Cont_1',
tccg.DESCRICAO as 'Class_Cont_1',
ttcdff.DESCRICAO as 'Tipo_Fluxo_Futuro'
FROM T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON (tccg2.FK_GRUPO_1 = tccg.ID)
LEFT JOIN T_TIPO_CLASSIF_DESPESA_FLUXO_FUTURO ttcdff ON (tccg2.FK_TIPO_FLUXO_FUTURO = ttcdff.ID)
WHERE ttcdff.DESCRICAO IS NOT NULL
"""
    


GET_ORCAMENTOS = """
SELECT 
to2.ID as 'ID_Orcamento',
te.ID as 'ID_Casa',
te.NOME_FANTASIA as 'Casa',
tccg.ID as 'ID_Class_Cont_1',
tccg.DESCRICAO as 'Class_Cont_1',
tccg2.ID as 'ID_Class_Cont_2',
tccg2.DESCRICAO as 'Class_Cont_2',
to2.ANO as 'Ano_Orcamento',
to2.MES as 'Mes_Orcamento',
to2.VALOR as 'Valor_Orcamento',
ttcdff.DESCRICAO as 'Tipo_Fluxo_Futuro'
FROM T_ORCAMENTOS to2 
LEFT JOIN T_EMPRESAS te ON (to2.FK_EMPRESA = te.ID)
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON (to2.FK_CLASSIFICACAO_1 = tccg.ID)
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON (to2.FK_CLASSIFICACAO_2 = tccg2.ID)
LEFT JOIN T_TIPO_CLASSIF_DESPESA_FLUXO_FUTURO ttcdff ON (tccg2.FK_TIPO_FLUXO_FUTURO = ttcdff.ID)
WHERE to2.ANO >= 2025
ORDER BY te.NOME_FANTASIA, to2.ANO, to2.MES, tccg.DESCRICAO, tccg2.DESCRICAO
"""


# GET_FATURAMENTO_AGREGADO = """
# WITH empresas_normalizadas AS (
#   SELECT
#     ID             AS original_id,
#     CASE 
#       WHEN ID IN (161, 162) THEN 149 
#       ELSE ID 
#     END            AS id_casa_normalizada
#   FROM T_EMPRESAS
# )
# SELECT
#   tfa.ID                     AS ID_Faturam_Agregado,
#   en.id_casa_normalizada     AS ID_Casa,
#   te2.NOME_FANTASIA          AS Casa,
#   tivc.DESCRICAO             AS Categoria,
#   tfa.ANO                    AS Ano,
#   tfa.MES                    AS Mes,
#   tfa.VALOR_BRUTO            AS Valor_Bruto,
#   tfa.DESCONTO               AS Desconto,
#   tfa.VALOR_LIQUIDO          AS Valor_Liquido
# FROM T_FATURAMENTO_AGREGADO tfa
# -- primeiro, linka ao CTE para saber a casa “normalizada”
# LEFT JOIN empresas_normalizadas en
#   ON tfa.FK_EMPRESA = en.original_id
# -- depois, puxa o nome da casa já normalizada
# LEFT JOIN T_EMPRESAS te2
#   ON en.id_casa_normalizada = te2.ID
# LEFT JOIN T_ITENS_VENDIDOS_CATEGORIAS tivc
#   ON tfa.FK_CATEGORIA = tivc.ID;
# """


GET_FATURAMENTO_AGREGADO = """
WITH empresas_normalizadas AS (
  SELECT
    ID             AS original_id,
    CASE 
      WHEN ID IN (161, 162) THEN 149 
      ELSE ID 
    END            AS id_casa_normalizada
  FROM T_EMPRESAS
)
SELECT
  tfa.ID                     AS ID_Faturam_Agregado,
  en.id_casa_normalizada     AS ID_Casa,
  te2.NOME_FANTASIA          AS Casa,
  tivc.DESCRICAO             AS Categoria,
  tfa.ANO                    AS Ano,
  tfa.MES                    AS Mes,
  tfa.VALOR_BRUTO            AS Valor_Bruto,
  tfa.DESCONTO               AS Desconto,
  tfa.VALOR_LIQUIDO          AS Valor_Liquido
FROM T_FATURAMENTO_AGREGADO tfa
-- primeiro, linka ao CTE para saber a casa “normalizada”
LEFT JOIN empresas_normalizadas en
  ON tfa.FK_EMPRESA = en.original_id
-- depois, puxa o nome da casa já normalizada
LEFT JOIN T_EMPRESAS te2
  ON en.id_casa_normalizada = te2.ID
LEFT JOIN T_ITENS_VENDIDOS_CATEGORIAS tivc
  ON tfa.FK_CATEGORIA = tivc.ID
  
UNION ALL

SELECT 
trec2.ID as ID_Faturam_Agregado,
te.ID as ID_Casa,
te.NOME_FANTASIA as Casa,
trec2.CLASSIFICACAO as Categoria,
YEAR(vpa.DATA_RECEBIMENTO) as Ano,
MONTH(vpa.DATA_RECEBIMENTO) as Mes,
SUM(vpa.VALOR_PARCELA) as Valor_Bruto,
0 as Desconto,
vpa.VALOR_PARCELA as Valor_Liquido
FROM View_Parcelas_Agrupadas vpa
INNER JOIN T_EMPRESAS te ON (vpa.FK_EMPRESA = te.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS tre ON (vpa.ID = tre.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLIENTE trec ON (vpa.FK_CLIENTE = trec.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLASSIFICACAO trec2 ON (tre.FK_CLASSIFICACAO = trec2.ID)
LEFT JOIN T_FORMAS_DE_PAGAMENTO tfdp ON (tre.FK_FORMA_PAGAMENTO = tfdp.ID)
LEFT JOIN T_STATUS_PAGAMENTO tsp ON (tre.FK_STATUS_PGTO = tsp.ID)
LEFT JOIN T_CONTAS_BANCARIAS tcb ON (tre.FK_CONTA_BANCARIA = tcb.ID)
WHERE vpa.DATA_RECEBIMENTO IS NOT NULL
AND vpa.DATA_RECEBIMENTO >= '2025-01-01'
AND trec2.ID IN (131,142,124,135,111,153,104,106,116,114,110,137)  # Bilheteria, Bilheteria-Rebate, Coleta de Oleo, Delivery, Eventos, Eventos de Marketing, Lojinha, Plataforma Ifood, Plataforma Rappi, Plataforma Total Acesso, Repasses FabLab, Voucher  
GROUP BY te.ID, trec2.ID, YEAR(vpa.DATA_RECEBIMENTO), MONTH(vpa.DATA_RECEBIMENTO)
"""





