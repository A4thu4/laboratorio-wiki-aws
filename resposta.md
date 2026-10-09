# 📝 Resposta do Laboratório: A Wiki Perdida dos Arquivos Corporativos

> Proposta de solução para transformar os documentos brutos da pasta `raw/` em uma Wiki Corporativa Inteligente, pesquisável e segura, usando apenas serviços da AWS.
>
> Esta entrega é uma **proposta de arquitetura**. Nada foi implantado na AWS. Os números citados sobre os arquivos (contagens, somas, datas) foram conferidos localmente abrindo os três arquivos da `raw/`.

---

## 👤 Identificação

**Nome:**
Arthur Mamedes Borges

**Data:**
07/10/2026

**Link do repositório:**
https://github.com/A4thu4/laboratorio-wiki-aws

---

# ✅ Quest 1: O Mapa dos Arquivos Perdidos

## 1.1 Formatos encontrados na pasta `raw/`

**Sua resposta:**

São três arquivos, todos soltos na raiz de `raw/`, e cada um pede um caminho diferente.

| Arquivo | Formato real | Nasce digital ou precisa de OCR? | O que dá para extrair |
|---|---|---|---|
| `ata_reuniao_vendas_sa.pdf` (150 KB) | PDF 1.7, 5 páginas, gerado pelo LibreOffice, com fontes embutidas e camada de texto em todas as páginas | **Nasce digital, sem OCR.** O texto já está dentro do arquivo e sai íntegro, com acentos | Ata de 08/07/2026 (código `VSA-COM-2026-07`): 6 participantes, pauta, painel com 6 indicadores, 5 decisões (D-001 a D-005), 6 ações com responsável e prazo (A-001 a A-006), 4 riscos (R-01 a R-04) e a próxima reunião (03/08/2026) |
| `ata_resultados_vendas_novos_dados.png` (3,5 MB) | PNG de 1900×2700 px, uma folha digitalizada | **Só pixels, exige OCR.** Não existe nenhum caractere pesquisável no arquivo | Ata de 15/01/2026 sobre os resultados do 2º semestre: 5 participantes nomeados, resumo executivo, tabela com 6 indicadores, desempenho de 5 regiões, 4 observações e 4 deliberações com responsável e prazo. Há ainda duas anotações à mão e um carimbo |
| `vendas_sa_dados_ficticios_laboratorio.csv` (53 KB) | CSV em UTF-8 com BOM, separado por vírgula, 240 linhas e 19 colunas | **Nasce digital, mas não é texto corrido.** É tabela | 240 oportunidades do CRM criadas entre 01/07 e 30/09/2026, com cliente, segmento, região, vendedor, origem, produto, campanha, status, valores, ciclo, motivo de perda e próxima atividade |

O ponto central da leitura: **dois arquivos são atas e o terceiro é uma base de dados**. Atas respondem a "o que foi decidido e por quem". O CSV responde a "quantas, quanto e onde". Tratar os três como texto para busca semântica quebraria justamente as perguntas sobre o CSV.

---

## 1.2 Principais desafios encontrados

**Sua resposta:**

**No PDF**
- Quase todo o conteúdo importante está em tabelas (identificação, participantes, indicadores, decisões, ações, riscos). Extrair como texto corrido embaralha as colunas.
- A tabela do plano de ação quebra entre as páginas 3 e 4: A-001 a A-003 ficam em uma página, A-004 a A-006 na outra, com o cabeçalho repetido.
- Cabeçalho ("VENDAS S.A. | ATA DE REUNIÃO SIMULADA") e rodapé ("Material fictício…", "Página N") se repetem nas 5 páginas e viram ruído em todo trecho indexado.
- A seção 11 repete dados já ditos (data, totais de decisões e ações). Se for indexada, duplica resultados na busca.
- Os metadados do arquivo não são confiáveis: o PDF foi criado em 10/07/2026, mas a reunião foi em 08/07/2026. A data tem que vir do conteúdo.
- Acentuação inconsistente dentro do próprio documento: algumas palavras aparecem sem acento ("Media", "revisao", "porem", "generica") enquanto outras o mantêm ("médio", "revisão").

**No PNG**
- A folha está levemente inclinada, com sombra e fundo cinza em volta.
- O texto impresso não tem acentos ("REUNIAO", "conversao"), então não casa letra por letra com o vocabulário do PDF.
- A anotação manuscrita "ação prioritária" e o círculo vermelho em volta dela atingem **dois prazos**: o círculo envolve 28/02/2026 (deliberação 1), e a escrita, junto com a borda inferior do círculo, passa por cima de 12/02/2026 (deliberação 2). São os dados mais sensíveis do documento e os mais sujeitos a erro de OCR.
- A anotação "conferir CRM" está encostada na borda da tabela de indicadores, e o carimbo "DOCUMENTO FICTICIO" está inclinado.
- O Amazon Textract lê texto impresso em português, mas o suporte oficial a manuscrito cobre o alfabeto inglês e símbolos ASCII. Palavras manuscritas com "ç" e "ã" podem sair erradas.
- A lista de participantes termina em "e supervisores regionais", ou seja, é incompleta por natureza.
- A reunião é de 15/01/2026, mas trata do 2º semestre (do ano anterior, pelo contexto). Data da reunião e período de referência são coisas diferentes.

**No CSV**
- As perguntas naturais são de agregação ("quanto de pipeline tem a campanha Rota 120?"). Busca semântica devolve alguns trechos parecidos e não soma 240 linhas.
- Não há data de extração no arquivo. Sem ela, não dá para dizer de quando é o retrato.
- `motivo_perda` só vem preenchido nas 46 oportunidades perdidas, e `data_fechamento` só nas fechadas. Vazio aqui significa "não se aplica", e não "dado faltando".
- 98 das 122 oportunidades abertas têm `proxima_atividade` anterior a 30/09/2026 (a data de criação mais recente do arquivo). O campo está preenchido, mas vencido.
- Acentuação inconsistente: só "Prospecção ativa" tem acento; todo o resto está sem ("Logistica", "Servicos").
- O BOM no início do arquivo corrompe o nome da primeira coluna se o leitor não tratar.

**Entre os arquivos**
- Nenhum padrão de nome: nenhum arquivo traz a data no nome, e "novos_dados" não diz nada.
- Nomes parecidos de pessoas diferentes: "Mariana Costa" (Diretora Comercial, no PDF) e "Marina Lopes" (Diretoria Comercial, no PNG).
- As pessoas das atas (gestores) não são as do CSV (12 vendedores). Nenhum nome se repete.
- A campanha "Rota 120" é aprovada no PDF e aparece em 96 linhas do CSV. É a única ligação explícita entre os arquivos, e ela só funciona se "campanha" virar metadado.
- Períodos diferentes dão números que parecem contraditórios: a ata de julho diz que 31% das oportunidades estavam sem próxima atividade, e no CSV de setembro todas as abertas têm o campo preenchido.

---

## 1.3 Informações importantes a serem extraídas

**Sua resposta:**

**Das atas (PDF e PNG)**
- Identificação: empresa, tipo de documento, código da ata, data, horário, local ou formato, quem presidiu e quem registrou.
- Período de referência (o mês ou semestre analisado), separado da data da reunião.
- Participantes, com função e papel na reunião.
- Pauta e temas discutidos.
- Indicadores: nome, meta, realizado, variação, e a leitura ("abaixo da meta").
- Decisões: identificador, texto e status.
- Ações: identificador, descrição, responsável, prazo, prioridade e status.
- Riscos: identificador, descrição, probabilidade, impacto e resposta planejada.
- Projetos e campanhas citados (por exemplo, "Rota 120") e áreas envolvidas.
- Próxima reunião: data, pauta e entregas esperadas.
- Anotações manuscritas e carimbos, guardados à parte do texto impresso.
- Classificação de confidencialidade declarada no documento.

**Do CSV**
- O esquema: nome, tipo e significado de cada uma das 19 colunas.
- Os valores possíveis das colunas categóricas (5 segmentos, 4 regiões, 12 vendedores, 5 origens, 5 produtos, 5 campanhas, 5 status, 6 motivos de perda).
- O período coberto (01/07 a 30/09/2026) e a data em que o arquivo entrou na base.
- As linhas em si, tipadas, para consulta por SQL.

**De todos**
- Rastreabilidade: nome original, caminho no S3, versão do objeto, hash do conteúdo, página e seção de onde cada informação saiu, e a confiança da extração.

---

## 1.4 Estratégia de classificação inicial

**Sua resposta:**

Como não há subpastas, a classificação é feita **pelo conteúdo do arquivo e gravada como metadado**, nunca pelo lugar onde ele está nem pelo nome.

1. **Classificação técnica (o que o arquivo é).** Uma função Lambda lê os primeiros bytes de cada objeto e ignora a extensão: `%PDF` indica PDF, `\x89PNG` indica PNG, texto com delimitador consistente e mesma quantidade de colunas por linha indica CSV. Um arquivo renomeado errado continua sendo classificado certo.
2. **Classificação de rota (como extrair).** Para PDF, a função conta os caracteres extraíveis de cada página. Página com texto segue como digital; página sem texto vai para OCR. A decisão é por página, então um PDF misto é tratado corretamente. Imagem sempre vai para OCR. CSV vai para a rota tabular.
3. **Classificação de negócio (do que o documento trata).** Depois da extração, um modelo no Amazon Bedrock recebe o início do texto e devolve, dentro de uma lista fechada de valores, o tipo de documento (ata de reunião, exportação de CRM, outro), a área (comercial) e a confidencialidade sugerida. Para o CSV, o tipo é definido pelo cabeçalho.
4. **Onde a classificação fica.** No registro do documento no Amazon DynamoDB e em tags do objeto no S3. A pasta `raw/` continua plana e intocada.

Resultado esperado para o acervo atual:

| Arquivo | Técnica | Rota | Negócio |
|---|---|---|---|
| `ata_reuniao_vendas_sa.pdf` | PDF, 5/5 páginas com texto | Texto digital | Ata de reunião, comercial |
| `ata_resultados_vendas_novos_dados.png` | PNG | OCR | Ata de reunião, comercial |
| `vendas_sa_dados_ficticios_laboratorio.csv` | CSV, 19 colunas | Tabular | Exportação de CRM, comercial |

Arquivo que não se encaixa em nenhuma rota (um `.zip`, por exemplo) é marcado como `NAO_SUPORTADO` e fica visível no painel de falhas, em vez de sumir.

---

# ✅ Quest 2: O Portal de Entrada na AWS

## 2.1 Armazenamento dos arquivos brutos

**Sua resposta:**

**Região.** `us-east-1` (Norte da Virgínia). O Amazon Textract não tem endpoint em São Paulo (`sa-east-1`), e manter tudo em uma região evita tráfego entre regiões. Em um projeto real, a saída dos dados do Brasil precisa passar pelo jurídico (LGPD) antes dessa escolha.

**Dois buckets, com papéis separados.**
- `wiki-vendas-raw`: só os originais, no prefixo `raw/`, plano como na pasta local.
- `wiki-vendas-processed`: tudo o que a solução gera (`textract/`, `texto/`, `kb/`, `crm/`).

Separar em dois buckets permite uma regra simples de permissão: **nenhuma função de processamento tem permissão de escrita no bucket de originais**.

**Envio.** Para o laboratório, um único comando sobe a pasta como está:

```bash
aws s3 sync raw/ s3://wiki-vendas-raw/raw/
```

Em produção, quem envia é um papel do IAM dedicado à ingestão, com permissão apenas de `s3:PutObject` nesse prefixo.

**Configuração do bucket de originais.**
- **Block Public Access** ligado e política que recusa qualquer requisição sem TLS.
- **Criptografia SSE-KMS** com uma chave gerenciada pelo cliente no AWS KMS. Quem não tem permissão de uso da chave não lê o arquivo, mesmo que tenha acesso ao bucket.
- **S3 Versioning** ligado: reenviar um arquivo com o mesmo nome cria uma nova versão e não apaga a anterior.
- **S3 Lifecycle**: originais passam para S3 Standard-IA após 90 dias, porque são lidos uma vez no processamento e depois só em auditoria. No bucket de processados, as saídas brutas do Textract expiram após 180 dias, já que podem ser geradas de novo.
- **Notificações para o Amazon EventBridge**: cada objeto criado em `raw/` dispara o fluxo de processamento. É isso que automatiza a ingestão: um arquivo novo entra na base sem ninguém rodar nada.

---

## 2.2 Preservação dos arquivos originais

**Sua resposta:**

- **Ninguém escreve por cima.** As funções de processamento têm apenas `s3:GetObject` no bucket de originais. Todo resultado vai para o outro bucket.
- **Versioning + Object Lock em modo governança** no bucket de originais: uma versão gravada não pode ser apagada nem sobrescrita dentro do prazo de retenção, nem por engano.
- **Identidade pelo conteúdo.** Na chegada, uma Lambda calcula o SHA-256 do arquivo e usa esse hash como `document_id`. O mesmo arquivo enviado duas vezes é reconhecido e não é reprocessado. Um arquivo com o mesmo nome e conteúdo diferente vira um novo documento, e o anterior é marcado como substituído.
- **Registro de entrada no DynamoDB**: nome original, caminho no S3, `versionId`, hash, tamanho, data de chegada e quem enviou.
- **Trilha de acesso.** O AWS CloudTrail registra os eventos de dados do bucket (quem leu, quem gravou, quando).

Com isso, toda resposta da Wiki consegue apontar para a versão exata do arquivo de onde a informação saiu, e é possível provar que essa versão não foi alterada.

---

## 2.3 Extração de texto dos documentos

**Sua resposta:**

O AWS Step Functions orquestra o fluxo. Ele foi escolhido porque o processamento tem ramificações (três rotas), esperas (OCR assíncrono) e precisa de novas tentativas e de um histórico visual de cada execução. Encadear Lambdas chamando umas às outras esconderia tudo isso.

```
S3 (raw/) → EventBridge → Step Functions
   1. Registrar  (hash, DynamoDB, duplicado?)
   2. Triar      (bytes iniciais + texto por página)
   3. Escolher rota:
        PDF com texto   → Lambda extrai a camada de texto
        Imagem ou scan  → Amazon Textract
        CSV             → Lambda valida e converte para Parquet
        Outro           → marca NAO_SUPORTADO
   4. Normalizar → 5. Enriquecer → 6. Validar → 7. Publicar
```

**PDF digital (`ata_reuniao_vendas_sa.pdf`): sem OCR.**
A triagem confirma que as 5 páginas têm texto. Uma Lambda extrai a camada de texto com uma biblioteca de leitura de PDF empacotada na própria função (o dado não sai da AWS), preservando o número da página e a posição das linhas. Passar esse arquivo pelo Textract seria pagar por página para receber um texto pior do que o que já está dentro dele: OCR pode errar um acento ou um dígito de valor que o PDF traz exato. A reconstrução das tabelas fica para a etapa de enriquecimento (3.3), que trabalha sobre texto limpo.

**Imagem (`ata_resultados_vendas_novos_dados.png`): Amazon Textract.**
Sem OCR, nada dessa ata entra na base. A chamada é `AnalyzeDocument` com dois recursos:
- `TABLES`, porque os indicadores estão em uma tabela de 4 colunas. Só com detecção de texto, "R$ 9,85 mi", "R$ 9,20 mi" e "+7,1%" sairiam como palavras soltas, sem ligação com "Faturamento".
- `LAYOUT`, porque identifica título, cabeçalhos de seção e listas, o que permite dividir a ata nas seções numeradas.

Três campos da resposta do Textract são aproveitados:
- `TextType` (`PRINTED` ou `HANDWRITING`): separa as anotações à mão do corpo da ata. "conferir CRM" e "ação prioritária" são gravadas em um campo próprio e não se misturam ao texto impresso.
- `Confidence`: toda linha abaixo de um limite (ponto de partida: 85) é marcada para revisão. É o caso esperado dos prazos 28/02/2026 e 12/02/2026, atingidos pelo círculo vermelho e pela anotação.
- `Geometry`: a posição de cada bloco na imagem é guardada para a Wiki mostrar o recorte do original ao lado da resposta.

A resposta completa do Textract é guardada em JSON em `textract/`, para reprocessar sem pagar OCR de novo.

**PDF escaneado (não há no acervo atual, mas a rota existe).**
Usa as operações assíncronas do Textract (`StartDocumentAnalysis`), porque um PDF de várias páginas não cabe na chamada síncrona. O Step Functions aguarda o aviso de conclusão e segue. Em PDF misto, só as páginas sem texto vão para OCR.

**CSV (`vendas_sa_dados_ficticios_laboratorio.csv`): rota tabular.**
Uma Lambda remove o BOM, valida o cabeçalho (19 colunas esperadas), converte os tipos (datas, valores decimais, percentuais inteiros) e grava em Parquet em `crm/`, registrando a tabela no AWS Glue Data Catalog. A consulta é feita por SQL no Amazon Athena. Regras simples de qualidade rodam aqui: identificador único, `valor_liquido = valor_bruto × (1 − desconto)`, status dentro da lista conhecida. Nos 240 registros atuais, todas passam. O original não é alterado; o Parquet é uma cópia tipada.

**Outros formatos (`.txt`, `.md`, `.docx`).**
`.txt` e `.md` já são texto: são lidos como UTF-8 e seguem direto para a normalização. `.docx` é um pacote de XML: a Lambda lê os parágrafos e tabelas, sem OCR.

**Onde o texto extraído fica.**
No bucket de processados, em `texto/<document_id>/`, com um arquivo por página e a origem de cada linha (página, posição, confiança). É uma camada intermediária: fiel ao original, ainda sem limpeza.

---

## 2.4 Tratamento de falhas

**Sua resposta:**

- **Novas tentativas automáticas.** Cada etapa do Step Functions tem `Retry` com espera crescente para erros passageiros (limite de requisições do Textract ou do Bedrock, tempo esgotado).
- **Captura de erro.** Se as tentativas se esgotam, um `Catch` leva o documento para um estado de falha que grava no DynamoDB o status `FALHA`, a etapa, a mensagem de erro e o identificador da execução. O evento também vai para uma fila morta no Amazon SQS, de onde pode ser reprocessado.
- **Falha de qualidade também é falha.** Além de erro técnico, o documento pode parar por: confiança média do OCR abaixo do limite, página sem nenhum texto, CSV com colunas diferentes do esperado, ou totais extraídos que não batem com os declarados no documento. Nesses casos o status é `REVISAO`, e o documento **não é publicado** na base até alguém conferir.
- **Estados visíveis.** Cada documento tem um status único: `RECEBIDO`, `EXTRAINDO`, `ENRIQUECENDO`, `PUBLICADO`, `REVISAO`, `FALHA`, `NAO_SUPORTADO`. Uma consulta responde "o que entrou e ainda não está pesquisável?".
- **Logs e alarmes.** As Lambdas gravam logs estruturados no Amazon CloudWatch com o `document_id`. Alarmes avisam por Amazon SNS quando uma execução falha, quando a fila morta tem mensagens ou quando um documento fica mais de uma hora sem mudar de estado.
- **Reprocessar não duplica.** Como a identidade é o hash do conteúdo e cada etapa grava em um caminho fixo, rodar o mesmo documento de novo sobrescreve o resultado anterior.

---

# ✅ Quest 3: A Relíquia dos Metadados

## 3.1 Padronização dos textos processados

**Sua resposta:**

Todo documento, venha de PDF, de OCR ou de CSV, termina no mesmo formato: **um JSON canônico** com os campos estruturados e **um Markdown por seção** com o texto limpo.

**Limpeza**
- **Cabeçalho e rodapé repetidos.** No PDF, linhas idênticas que aparecem em quase todas as páginas são removidas ("VENDAS S.A. | ATA DE REUNIÃO SIMULADA", "Material fictício…", "Página N"). No PNG, o Textract já marca esses blocos como cabeçalho, rodapé e número de página.
- **Quebras de linha.** Linhas quebradas no meio de uma frase ou de uma célula são reunidas ("Mariana Costa - Diretora" + "Comercial").
- **Tabelas cortadas entre páginas.** Quando uma tabela termina no fim de uma página e a seguinte começa com o mesmo cabeçalho, as duas são unidas. É o caso do plano de ação, nas páginas 3 e 4.
- **Conteúdo duplicado.** A seção 11 do PDF repete dados já ditos. Ela não vira trecho indexado, mas é usada como conferência (ver 3.3).
- **Formatos.** Datas viram ISO 8601 ("15 de janeiro de 2026" e "08/07/2026" viram `2026-01-15` e `2026-07-08`). Valores viram número ("R$ 9,85 mi" vira `9850000.00`), guardando também o texto original.
- **Acentos.** O texto é mantido como está no documento. Para filtros e comparação de nomes, é gravada uma segunda forma em minúsculas e sem acento, de modo que "Logística" (PDF) e "Logistica" (CSV) caiam no mesmo valor.
- **Vocabulário controlado.** Valores de status, prioridade e região são mapeados para uma lista única ("Media", como está no PDF, e a forma acentuada "Média" viram `media`).

**Formato canônico (resumo)**

```json
{
  "document_id": "sha256:e785fc07…",
  "arquivo_original": "s3://wiki-vendas-raw/raw/ata_reuniao_vendas_sa.pdf",
  "version_id": "…",
  "tipo_documento": "ata_reuniao",
  "origem_extracao": "pdf_texto",
  "data_documento": "2026-07-08",
  "periodo_referencia": "2026-06",
  "secoes": [
    { "id": "6", "titulo": "Decisões aprovadas", "pagina_inicio": 3, "markdown": "…" }
  ],
  "decisoes": [
    { "id": "D-004", "texto": "Executar a campanha Rota 120 no terceiro trimestre.",
      "status": "Aprovada por consenso", "pagina": 3, "evidencia": "Executar a campanha Rota 120 no terceiro trimestre." }
  ],
  "acoes": [
    { "id": "A-003", "descricao": "Definir lista das 120 contas-alvo da campanha Rota 120.",
      "responsavel": "Camila Rocha", "prazo": "2026-07-20", "prioridade": "alta",
      "status": "Em preparação", "pagina": 3 }
  ],
  "qualidade": { "confianca_media": 100, "revisao_pendente": false }
}
```

Cada seção em Markdown começa com uma linha de contexto, para que o trecho faça sentido sozinho quando for recuperado na busca:

```md
> Ata VSA-COM-2026-07 · Vendas S.A. · reunião de 08/07/2026 · seção 7 · páginas 3–4

## 7. Plano de ação
| ID | Ação | Responsável | Prazo | Prioridade | Status |
```

---

## 3.2 Metadados propostos

| Metadado | Por que ele é importante? |
|---|---|
| Nome do documento | É como as pessoas reconhecem o arquivo e o que aparece na citação da resposta. Sozinho não basta, porque os nomes não seguem padrão |
| Tipo do documento | Decide a rota de consulta (ata vai para busca semântica, CRM vai para SQL) e permite filtrar "só atas" |
| Data identificada | Permite perguntar por período ("último trimestre") e ordenar decisões no tempo. Vem do conteúdo, porque a data do arquivo não coincide com a da reunião |
| Tema principal | Agrupa documentos sobre o mesmo assunto mesmo quando usam palavras diferentes |
| Participantes | Responde "em quais reuniões fulano esteve" e ajuda a distinguir nomes parecidos (Mariana Costa e Marina Lopes) pela função |
| Decisões tomadas | É a pergunta mais comum da liderança. Guardadas uma a uma, com identificador, podem ser listadas sem depender de interpretação do modelo |
| Responsáveis | Liga cada ação a uma pessoa: "o que está com o Rafael Nunes?" |
| Próximos passos | Com prazo e status, permite cobrar pendências e gerar alertas de vencimento |
| Nível de confidencialidade | Controla quem pode ver o documento. É aplicado como filtro obrigatório na busca |
| Caminho do arquivo original | É o que torna a resposta verificável: toda citação leva ao arquivo de origem |

**Metadados adicionais**

| Metadado | Por que ele é importante? |
|---|---|
| `document_id` (SHA-256) | Identidade estável, independente do nome. Evita duplicatas |
| `version_id` do S3 | Aponta para a versão exata usada na extração |
| Período de referência | A ata de 15/01/2026 fala do semestre anterior. Sem esse campo, "resultados de janeiro" traria o documento errado |
| Código da ata | Identificador oficial quando existe (`VSA-COM-2026-07`) |
| Origem da extração | `pdf_texto`, `ocr` ou `crm`. Informa o quanto confiar no texto |
| Confiança e revisão pendente | Marca trechos que o OCR leu com dúvida. A resposta avisa o usuário |
| Seção e página | Levam a citação até o ponto exato do documento |
| Campanhas e projetos citados | Liga a ata ao CRM. "Rota 120" aparece na decisão D-004 e em 96 oportunidades |
| Área | Filtro por departamento e base do controle de acesso por perfil |
| Riscos (probabilidade e impacto) | Responde "quais riscos altos foram apontados" |
| Anotações manuscritas | "conferir CRM" e "ação prioritária" são informação, mas não fazem parte do texto oficial da ata |
| Data de ingestão | Para o CSV, é a única referência de quando o retrato do CRM foi tirado |
| Substituído por | Indica que existe uma versão mais nova do mesmo documento |

---

## 3.3 Uso de IA para enriquecimento dos documentos

**Sua resposta:**

Depois da limpeza, uma Lambda envia o texto de cada ata a um modelo no Amazon Bedrock (um modelo rápido e barato, como o Claude Haiku, é suficiente para extração) e pede a resposta em um esquema JSON fixo.

**O que o modelo faz**
- Identifica tipo de documento, data da reunião, período de referência e tema principal.
- Reconstrói as tabelas a partir do texto e lista participantes, decisões, ações, riscos e próximos passos, cada um com seus campos.
- Gera um resumo curto do documento e um resumo por seção.
- Reconhece campanhas, projetos e áreas citados.
- Sugere um nível de confidencialidade.

Um modelo de linguagem é a ferramenta certa aqui porque as duas atas têm estruturas diferentes: o PDF tem "6. Decisões aprovadas" em tabela com identificadores, e o PNG tem "5. DELIBERACOES E PLANO DE ACAO" em lista numerada com responsável e prazo na mesma frase. Uma regra fixa serviria para uma e falharia na outra.

**Como evitar que o modelo invente**
- **Evidência obrigatória.** Cada item extraído precisa vir com o trecho literal do documento que o sustenta e a página. Uma Lambda confere se esse trecho existe no texto. Item sem evidência encontrada é descartado.
- **Sem preencher lacunas.** O modelo é instruído a devolver `null` quando a informação não está no texto. O PNG não tem prioridade nas ações, e o campo fica vazio.
- **Listas fechadas** para tipo, status, prioridade e confidencialidade, e temperatura zero.
- **Conferência com o próprio documento.** A seção 11 do PDF declara 6 participantes, 5 decisões e 6 ações. Se a extração trouxer outra contagem, o documento vai para `REVISAO`.
- **Confidencialidade conservadora.** O padrão é "Interno". A IA pode sugerir um nível mais restrito, mas tornar um documento público exige uma pessoa.
- **Revisão humana** para o que foi marcado com baixa confiança, em uma fila própria. O Step Functions pausa o documento nesse ponto (integração com `waitForTaskToken`) e publica a tarefa em uma fila do Amazon SQS. Uma tela de revisão no mesmo site da Wiki, restrita ao grupo `revisores` do Cognito, mostra o recorte da imagem ao lado do texto lido. Quando a pessoa confirma ou corrige, a API devolve o token e a execução continua. O Amazon Augmented AI (A2I) faria esse papel, mas entrou em modo de manutenção e não aceita novos clientes desde 30/07/2026.

**O que a IA não faz.** No CSV não há enriquecimento por linha: os dados já são estruturados, e pedir a um modelo que "leia" 240 linhas só acrescenta custo e risco de erro. A IA entra no CSV em outro ponto, ao traduzir a pergunta do usuário em SQL (ver 4.3).

---

## 3.4 Armazenamento dos metadados

**Sua resposta:**

Os metadados ficam em três lugares, cada um servindo a um tipo de pergunta.

**1. Amazon DynamoDB: o catálogo.**
Uma tabela com um registro por documento e um registro por item extraído:

| Chave de partição | Chave de ordenação | Conteúdo |
|---|---|---|
| `DOC#<document_id>` | `META` | Tipo, datas, status do processamento, caminho e versão no S3 |
| `DOC#<document_id>` | `DECISAO#D-004` | Texto, status, página, evidência |
| `DOC#<document_id>` | `ACAO#A-003` | Descrição, responsável, prazo, prioridade, status, página |
| `DOC#<document_id>` | `RISCO#R-03` | Descrição, probabilidade, impacto, resposta |

Índices secundários por responsável e por prazo respondem "quais ações estão com Rafael Nunes?" e "o que vence este mês?" com uma consulta exata, sem busca semântica. O DynamoDB foi escolhido por ser sem servidor, cobrar por uso e atender bem a esse acesso por chave.

**2. Arquivo `.metadata.json` ao lado de cada trecho: o filtro da busca.**
O Amazon Bedrock Knowledge Bases lê um arquivo de metadados com o mesmo nome do arquivo de conteúdo e permite filtrar a busca por ele. Aqui vai só o conjunto pequeno e filtrável:

```json
{
  "metadataAttributes": {
    "document_id": "sha256:e785fc07…",
    "nome_documento": "ata_reuniao_vendas_sa.pdf",
    "tipo_documento": "ata_reuniao",
    "data_documento": 20260708,
    "area": "comercial",
    "confidencialidade": "interno",
    "secao": "7",
    "pagina": 3,
    "origem_extracao": "pdf_texto",
    "campanhas": ["rota 120"],
    "revisao_pendente": false
  }
}
```

A base vetorial escolhida (S3 Vectors) limita o tamanho dos metadados por vetor, por isso listas longas de decisões e ações ficam no DynamoDB, e não aqui.

**3. AWS Glue Data Catalog: o esquema do CRM.**
Guarda nomes, tipos e descrição das 19 colunas da tabela de oportunidades. É o que o Athena usa para consultar e o que o modelo recebe para escrever SQL correto.

**Ligação com o original.** Todo registro, nos três lugares, carrega `document_id`, o caminho `s3://wiki-vendas-raw/raw/<arquivo>` e o `version_id`. Itens extraídos carregam também página e seção, e os que vieram de OCR, a posição na imagem. De qualquer metadado se chega ao arquivo original e ao ponto dentro dele.

---

# ✅ Quest 4: O Oráculo da Wiki Inteligente

## 4.1 Estratégia de indexação

**Sua resposta:**

**Atas: um trecho por seção.**
As duas atas já são divididas em seções numeradas e curtas. O corte segue essa estrutura, em vez de um tamanho fixo de caracteres:
- A ata em PDF gera um trecho para cada seção de 1 a 10 (a 5 é dividida em 5.1 a 5.4). A seção 11 não é indexada.
- A ata em PNG gera um trecho para cada bloco: participantes, resumo executivo, indicadores, desempenho por região, observações e deliberações.

Cortar por tamanho fixo separaria, por exemplo, a ação A-003 do seu responsável e do seu prazo, que estão em colunas diferentes da mesma linha. Cortando por seção, uma tabela nunca é partida ao meio.

Na prática, a etapa de publicação grava um arquivo Markdown por seção em `kb/`, com a linha de contexto no topo e o `.metadata.json` ao lado. A base de conhecimento é configurada **sem divisão automática**, de modo que cada arquivo vira exatamente um trecho. As seções são pequenas e cabem com folga no limite do modelo de embeddings.

**CSV: as linhas não são indexadas uma a uma.**
O CSV entra na busca semântica de duas formas leves:
- Uma **ficha do conjunto de dados**: o que o arquivo é, período coberto, significado de cada coluna e valores possíveis. Serve para a Wiki saber que essa fonte existe e quando usá-la.
- **Resumos gerados por SQL** (por campanha, região, vendedor e motivo de perda), em texto, com a data do retrato. Servem para ligar atas e CRM em perguntas gerais.

Os números em si são sempre calculados na hora pelo Athena.

---

## 4.2 Busca semântica e base vetorial

**Sua resposta:**

**Embeddings.** Gerados pelo Amazon Titan Text Embeddings V2, no Amazon Bedrock. É multilíngue, o que importa porque o acervo está em português e parte dele sem acentos, e tem custo por token muito baixo. A busca semântica aproxima "REUNIAO" de "reunião" e "deliberações" de "decisões" sem depender da grafia. Se os testes mostrarem recuperação fraca em português, a alternativa dentro do próprio Bedrock é o Cohere Embed Multilingual.

**Quem gera e sincroniza.** O Amazon Bedrock Knowledge Bases. Ele lê os arquivos de `kb/`, gera os embeddings, grava na base vetorial e mantém tudo sincronizado: arquivo novo, alterado ou removido é refletido na próxima sincronização, que o Step Functions dispara ao fim de cada ingestão. Fazer isso à mão exigiria escrever e manter código de embeddings, lotes e remoção.

**Onde os vetores ficam: Amazon S3 Vectors.**

| Opção | Por que sim ou não |
|---|---|
| **Amazon S3 Vectors (escolhida)** | Cobra por armazenamento e por consulta, sem custo mínimo por hora. Para um acervo de dezenas a milhares de documentos e consultas ocasionais, é a opção mais barata, com latência abaixo de um segundo |
| Amazon OpenSearch Serverless | Oferece busca híbrida (semântica + palavra-chave), mas tem custo mínimo mensal mesmo sem uso. Só compensa com volume e exigência de latência maiores |
| Amazon Aurora PostgreSQL com pgvector | Faz sentido quando já existe um banco Aurora. Aqui seria um banco a mais para administrar |

**Limitações assumidas com o S3 Vectors**
- **Só busca semântica, sem busca por palavra-chave.** Códigos exatos como "D-003" ou "OPP-20260003" são mal atendidos por semântica. Por isso esses identificadores são resolvidos por consulta exata no DynamoDB e no Athena.
- **Metadados filtráveis pequenos por vetor.** Por isso só o conjunto mínimo vai no `.metadata.json`.

Se a busca híbrida passar a ser necessária, a troca é de base vetorial, sem mudar o restante da arquitetura.

**Como a busca encontra a informação.** A pergunta vira um vetor com o mesmo modelo, a base devolve os trechos mais próximos **já filtrados pelos metadados** (confidencialidade permitida ao usuário, tipo de documento, intervalo de datas) e cada trecho volta com sua pontuação e seus metadados.

---

## 4.3 Geração de respostas com IA

**Sua resposta:**

**1. Recebimento.** A pergunta chega pela API com o token do usuário. Uma Lambda orquestradora extrai do token os grupos do usuário e monta, no servidor, o filtro de acesso. O navegador nunca envia o filtro.

**2. Escolha da ferramenta.** A Lambda chama um modelo no Amazon Bedrock (Claude Sonnet, pela qualidade de raciocínio em português) com duas ferramentas disponíveis:

| Ferramenta | Quando é usada | O que faz |
|---|---|---|
| `buscar_documentos` | "O que foi decidido…", "quem ficou responsável…", "quais riscos…" | Consulta a base de conhecimento com o filtro de acesso e devolve trechos com fonte |
| `consultar_crm` | "Quantas…", "qual o valor…", "por região…" | Gera um `SELECT` sobre a tabela de oportunidades e executa no Athena |

O modelo pode usar as duas na mesma pergunta. "A campanha Rota 120 atingiu a meta?" precisa da meta, que está na ata, e do realizado, que está no CRM.

**3. Proteções da consulta ao CRM.** O SQL gerado é validado antes de rodar: apenas `SELECT`, apenas a tabela de oportunidades, com limite de linhas. O papel do IAM usado pelo Athena é somente leitura, e o grupo de trabalho do Athena tem limite de dados lidos por consulta.

**4. Geração.** O modelo recebe os trechos e os resultados e redige a resposta sob três regras: usar **apenas** o material recuperado, citar a fonte de cada afirmação, e dizer quando a informação não foi encontrada.

**5. Fontes.** Cada citação traz nome do arquivo, seção, página e data do documento, com um link temporário para o original no S3. Em respostas do CRM, a fonte é o arquivo, a data do retrato, o filtro aplicado e a quantidade de linhas consideradas. Quando o trecho veio de OCR com baixa confiança, a resposta avisa.

**Formato da resposta**

```
Resumo
Decisões encontradas
Pessoas envolvidas
Datas e prazos
Próximos passos
Fontes: [1] ata_reuniao_vendas_sa.pdf, seção 6, p. 3 (08/07/2026)
```

**Quando a base não tem a informação.**
- Se nenhum trecho passa da pontuação mínima, a Lambda **não chama o modelo para responder**. Devolve um texto fixo: "Não encontrei essa informação nos documentos indexados", seguido dos temas mais próximos que existem.
- Se houve recuperação, o Amazon Bedrock Guardrails verifica se a resposta está sustentada pelos trechos. Se não estiver, a resposta é bloqueada e substituída pela mesma mensagem.
- A mensagem é igual para "não existe" e "existe, mas você não tem acesso", para não revelar a existência de documentos restritos.
- Toda pergunta sem resposta é registrada. Essa lista mostra o que as pessoas procuram e a base ainda não tem.

**Períodos diferentes não são misturados.** Quando as fontes são de datas distintas, a resposta apresenta cada número com sua data, em vez de fundi-los. Exemplo: "31% sem próxima atividade" é da ata de julho sobre junho, e o CSV retrata o fim de setembro.

---

## 4.4 Interface de consulta

**Sua resposta:**

Uma aplicação web simples, com uma caixa de pergunta, a resposta e um painel de fontes ao lado.

| Camada | Serviço | Por quê |
|---|---|---|
| Hospedagem | AWS Amplify Hosting | Publica o site estático com HTTPS e CDN, sem servidor para administrar |
| Login | Amazon Cognito | Autenticação com MFA e grupos de usuários (por exemplo, `comercial`, `diretoria`). O grupo vai dentro do token |
| API | Amazon API Gateway | Valida o token do Cognito antes de qualquer código rodar e aplica limite de requisições por usuário |
| Lógica | AWS Lambda | Orquestra busca, consulta ao CRM e geração. Paga só quando alguém pergunta |

**Na tela**
- Resposta com as fontes numeradas. Clicar em uma fonte abre o original na página citada. Para a ata digitalizada, mostra o recorte da imagem.
- Filtros opcionais: período, tipo de documento, área.
- Aviso visível quando a resposta usa trecho pendente de revisão.
- Botões de "útil" e "não útil" em cada resposta.

**Por que não o Amazon Q Business.** Ele entrega uma interface pronta com conectores e controle de acesso, e já foi o caminho mais rápido para um piloto. Não foi escolhido por três motivos. O principal: entrou em modo de manutenção e não aceita novos clientes desde 30/07/2026, então uma conta nova não consegue adotá-lo. Além disso, cobra por usuário, o que pesa em um acervo pequeno, e dá menos controle sobre dois pontos centrais desta proposta: a consulta ao CRM por SQL e o formato das citações.

---

## 4.5 Segurança, auditoria e monitoramento

**Sua resposta:**

**Controle de acesso**
- **AWS IAM com privilégio mínimo.** Cada Lambda tem seu próprio papel. A de triagem só lê o bucket de originais, a de OCR só chama o Textract e grava em `textract/`, e assim por diante. Nenhuma tem permissão de escrita nos originais.
- **Acesso por perfil na busca.** O grupo do usuário no Cognito determina os níveis de confidencialidade e as áreas que ele pode consultar. O filtro é montado no servidor e aplicado **na recuperação**: o trecho restrito nem chega ao modelo, então não pode vazar na resposta.
- **Links temporários** para os originais, gerados só depois da checagem de permissão.

**Proteção dos dados**
- **AWS KMS**: criptografia em repouso com chave gerenciada pelo cliente em S3, DynamoDB, logs e base vetorial. TLS em todo o tráfego.
- **Amazon Macie** varre os buckets em busca de dados pessoais (nomes, CPFs, e-mails) e avisa quando encontra algo fora do esperado. O CSV traz nomes de clientes e vendedores, e em um cenário real seriam dados pessoais.
- **Amazon Bedrock Guardrails** mascara dados pessoais nas respostas e bloqueia respostas sem sustentação nas fontes.
- Os dados enviados ao Bedrock não são usados para treinar os modelos.

**Auditoria**
- **AWS CloudTrail** registra as chamadas de API da conta e os eventos de dados dos buckets: quem leu ou gravou cada arquivo.
- **Registro de consultas** em tabela própria: usuário, pergunta, ferramentas usadas, documentos citados, SQL executado e data. Responde "quem consultou o quê".
- **Log de invocações do Bedrock**, com acesso restrito, para investigar respostas contestadas.

**Monitoramento**

| O que | Como |
|---|---|
| Erros de processamento | Alarmes do CloudWatch sobre execuções com falha, fila morta e documentos parados |
| Uso | Perguntas por dia, usuários ativos, tempo de resposta, tokens por pergunta |
| Qualidade das respostas | Taxa de "não encontrei", taxa de bloqueio pelo Guardrails, avaliações dos usuários, e um conjunto fixo de perguntas com resposta conhecida rodado a cada mudança (por exemplo, "quem é responsável pela A-003?" deve devolver Camila Rocha) |
| Qualidade da extração | Confiança média do OCR por documento e quantidade de itens em revisão |
| Custos | Tags de custo em todos os recursos, AWS Cost Explorer por serviço e AWS Budgets com alerta ao atingir 80% do orçamento mensal |

**Estimativa de custo mensal.** Cenário hipotético: 500 documentos por mês (2.500 páginas, 750 delas digitalizadas), 50 usuários e 3.000 perguntas por mês. Valores aproximados em dólar, a partir de preços de tabela de `us-east-1`. São ordem de grandeza e devem ser refeitos na AWS Pricing Calculator antes de qualquer decisão.

| Item | Estimativa | Observação |
|---|---|---|
| Textract (tabelas + layout) | ~US$ 15 | Só as 750 páginas sem texto. Mandar as 2.500 custaria mais que o triplo |
| Bedrock, enriquecimento | ~US$ 7 | Modelo pequeno, uma chamada por documento |
| Bedrock, respostas | ~US$ 70 a 90 | **Maior item.** Depende do tamanho do contexto enviado por pergunta |
| Bedrock, embeddings | < US$ 1 | |
| S3 e S3 Vectors | < US$ 5 | |
| Lambda, Step Functions, DynamoDB, Athena, API Gateway | < US$ 10 | Tudo cobrado por uso |
| KMS, CloudWatch, CloudTrail, Macie | ~US$ 10 a 15 | |
| Cognito | US$ 0 | Dentro da faixa gratuita para 50 usuários |
| **Total** | **~US$ 110 a 140** | |

Para os três arquivos do laboratório, o custo de processamento é de centavos: uma página de OCR e três chamadas ao modelo.

**Alternativas mais baratas e mais caras**
- Usar um modelo menor nas respostas a perguntas simples reduz o maior item da conta.
- Enviar menos trechos por pergunta (os 4 melhores, e não 10) reduz tokens sem perder qualidade em um acervo pequeno.
- Trocar o S3 Vectors pelo OpenSearch Serverless acrescentaria um custo fixo mensal da ordem de centenas de dólares.
- O Amazon Q Business não é alternativa para uma conta nova, por estar em modo de manutenção. Para quem já o utiliza, cobra assinatura por usuário e um índice por hora, e para 50 usuários ficaria acima do total estimado aqui.

---

# 🧩 Arquitetura Final da Solução

## 1. Visão geral

**Sua resposta:**

A arquitetura separa o acervo por natureza do dado e dá a cada tipo o caminho que preserva sua informação. Documentos narrativos (atas) viram texto limpo, dividido por seção e pesquisado por significado. Dados tabulares (CRM) viram uma tabela consultada por SQL. Um modelo de linguagem escolhe o caminho certo para cada pergunta, responde apenas com o que foi recuperado e cita a origem. Os originais nunca são alterados, e todo dado extraído aponta de volta para o arquivo, a versão e a página de onde saiu.

---

## 2. Serviços AWS utilizados

| Serviço AWS | Papel na solução |
|---|---|
| Amazon S3 | Guarda os originais (bucket imutável, versionado) e os dados processados (texto, saída de OCR, trechos da base, Parquet do CRM) |
| Amazon S3 Vectors | Base vetorial dos trechos das atas, sem custo mínimo por hora |
| Amazon EventBridge | Dispara o processamento quando um arquivo chega em `raw/` |
| AWS Step Functions | Orquestra o fluxo: triagem, escolha de rota, novas tentativas, espera do OCR, pausa para revisão humana e tratamento de falhas |
| AWS Lambda | Executa cada etapa (registro, triagem, extração de PDF, conversão do CSV, normalização, validação, publicação) e a orquestração das perguntas |
| Amazon Textract | OCR com tabelas e layout para imagens e PDFs digitalizados. Distingue texto impresso de manuscrito e informa a confiança |
| Amazon Bedrock | Modelos para enriquecer as atas (extração estruturada), gerar embeddings, traduzir perguntas em SQL e redigir respostas |
| Amazon Bedrock Knowledge Bases | Gera e sincroniza os embeddings a partir do S3 e executa a busca semântica com filtro por metadados |
| Amazon Bedrock Guardrails | Bloqueia respostas sem sustentação nas fontes e mascara dados pessoais |
| Amazon DynamoDB | Catálogo de documentos, itens extraídos (decisões, ações, riscos), status do processamento e registro de consultas |
| AWS Glue Data Catalog | Esquema da tabela de oportunidades do CRM |
| Amazon Athena | Consultas SQL sobre o CRM em Parquet |
| Amazon Cognito | Login, MFA e grupos de usuários usados no controle de acesso |
| Amazon API Gateway | Porta de entrada da API, valida o token e limita requisições |
| AWS Amplify Hosting | Hospeda a interface web de consulta e a tela de revisão |
| AWS IAM | Papéis de privilégio mínimo para cada componente |
| AWS KMS | Chave de criptografia dos dados em repouso |
| Amazon SQS e Amazon SNS | Fila de revisão humana, fila morta para reprocessar falhas e avisos de alarme |
| Amazon CloudWatch | Logs, métricas, alarmes e painel de operação |
| AWS CloudTrail | Auditoria de chamadas de API e de acesso aos arquivos |
| Amazon Macie | Detecção de dados pessoais nos buckets |
| AWS Budgets e Cost Explorer | Alerta e acompanhamento de custos |

---

## 3. Fluxo de dados de ponta a ponta

**Sua resposta:**

**Ingestão**
1. Os três arquivos são enviados de `raw/` para `s3://wiki-vendas-raw/raw/`, sem alteração e sem subpastas.
2. O S3 notifica o EventBridge, que inicia uma execução do Step Functions por arquivo.
3. A Lambda de registro calcula o SHA-256, grava o documento no DynamoDB como `RECEBIDO` e encerra se o arquivo for duplicado.
4. A Lambda de triagem identifica o tipo real pelos bytes iniciais e, no PDF, verifica se cada página tem texto.
5. O fluxo se divide:
   - **PDF com texto:** a Lambda extrai a camada de texto, página por página.
   - **PNG:** o Textract devolve texto, tabela, layout, tipo de escrita e confiança.
   - **CSV:** a Lambda valida, converte para Parquet e registra no Glue.
6. A normalização remove cabeçalhos e rodapés repetidos, une tabelas cortadas, padroniza datas e valores.
7. O Bedrock extrai participantes, decisões, ações, riscos e resumo das atas, com evidência literal para cada item.
8. A validação confere evidências e totais. Com problema, o documento vai para `REVISAO`; sem problema, segue.
9. A publicação grava o JSON canônico, os itens no DynamoDB e um Markdown por seção com seu `.metadata.json` em `kb/`.
10. A base de conhecimento sincroniza: gera embeddings e grava no S3 Vectors. O documento passa a `PUBLICADO`.

**Consulta**
11. O usuário faz login pelo Cognito e pergunta pela interface web.
12. O API Gateway valida o token e chama a Lambda orquestradora, que monta o filtro de acesso pelo grupo do usuário.
13. O modelo decide entre buscar nas atas, consultar o CRM por SQL, ou ambos.
14. Com os trechos e resultados, o modelo redige a resposta, e o Guardrails confere se ela está sustentada.
15. A resposta volta com resumo, decisões, pessoas, datas, próximos passos e fontes com link para o original.
16. A consulta é registrada para auditoria e medição de qualidade.

---

## 4. Diagrama textual da arquitetura

**Sua resposta:**

```
INGESTÃO
────────
raw/ (3 arquivos, sem subpastas)
  │  aws s3 sync
  ▼
S3 wiki-vendas-raw  [Versioning · Object Lock · SSE-KMS]
  │  evento "objeto criado"
  ▼
EventBridge ──► Step Functions
                  │
                  ├─ Lambda Registrar (SHA-256, duplicado?) ──► DynamoDB
                  ├─ Lambda Triar (bytes iniciais, texto por página)
                  │
                  ├──[PDF com texto]──► Lambda extrai camada de texto ─┐
                  ├──[PNG / scan]─────► Textract (TABLES + LAYOUT) ────┤
                  │                       └─ baixa confiança ► revisão │
                  │                                                    ▼
                  │                                   Lambda Normalizar
                  │                                                    ▼
                  │                                   Bedrock (extração com evidência)
                  │                                                    ▼
                  │                                   Lambda Validar ──► REVISAO
                  │                                                    ▼
                  │                                   Lambda Publicar
                  │                                     ├─► DynamoDB (decisões, ações, riscos)
                  │                                     └─► S3 processed/kb/ (.md + .metadata.json)
                  │                                                    ▼
                  │                                   Bedrock Knowledge Bases
                  │                                     (Titan Embeddings) ──► S3 Vectors
                  │
                  ├──[CSV]──► Lambda valida e converte ──► S3 processed/crm/ (Parquet)
                  │                                          └─► Glue Data Catalog ◄── Athena
                  │
                  └──[falha]──► SQS (fila morta) + CloudWatch Alarm ──► SNS


CONSULTA
────────
Usuário ──► Amplify (web) ──► Cognito (login, grupos)
                │
                ▼
          API Gateway (valida token)
                │
                ▼
          Lambda Orquestradora ── filtro de acesso pelo grupo
                │
                ▼
          Bedrock (modelo com ferramentas)
                ├─ buscar_documentos ──► Knowledge Bases ──► S3 Vectors
                ├─ consultar_crm ──────► Athena (somente SELECT)
                └─ itens exatos ───────► DynamoDB
                │
                ▼
          Bedrock Guardrails (resposta sustentada? dados pessoais?)
                │
                ▼
          Resposta + fontes (arquivo, seção, página, link para o original)


TRANSVERSAL:  IAM · KMS · CloudTrail · CloudWatch · Macie · Budgets
```

---

## 5. Riscos e limitações

**Sua resposta:**

- **Manuscrito em português.** O suporte oficial do Textract a escrita à mão cobre o alfabeto inglês. Anotações como "ação prioritária" podem sair erradas, e por isso ficam em campo separado e sinalizado.
- **Texto sobreposto.** Os prazos 28/02/2026 e 12/02/2026 estão parcialmente cobertos por uma anotação e pelo círculo em volta dela. Mesmo com revisão humana, a origem do erro é a qualidade do original.
- **Extração por IA pode errar.** A exigência de evidência literal reduz invenção, mas não impede atribuição errada (ligar um prazo à ação vizinha). A conferência de totais só existe quando o documento declara totais, como no PDF.
- **Sem busca por palavra-chave.** O S3 Vectors só faz busca semântica. Termos exatos fora dos identificadores tratados (um número de contrato no meio de um parágrafo, por exemplo) podem não ser encontrados.
- **SQL gerado por modelo.** Uma pergunta ambígua pode gerar uma consulta que roda sem erro e responde outra coisa. A resposta mostra o filtro aplicado para o usuário conferir.
- **Retrato sem data.** O CSV não informa quando foi extraído. A solução usa a data de ingestão, que pode não coincidir.
- **Definições de negócio ausentes.** A ata fala em "pipeline qualificado" e o CSV não tem essa marcação. Comparações entre os dois dependem de uma premissa, que a resposta precisa declarar.
- **Resolução de pessoas.** Nomes parecidos (Mariana Costa, Marina Lopes) e listas incompletas ("e supervisores regionais") limitam a busca por participante.
- **Região fora do Brasil.** O Textract não está disponível em São Paulo. Processar em `us-east-1` exige avaliação de LGPD.
- **Custo cresce com o uso.** O maior item são as respostas geradas. Muitos usuários fazendo perguntas longas mudam a conta.
- **Proposta não validada em execução.** Limites de confiança, pontuação mínima da busca e estratégia de corte são pontos de partida e precisam de ajuste com dados reais.

---

## 6. Melhorias futuras

**Sua resposta:**

- **Painel de pendências.** Com as ações já estruturadas no DynamoDB, exibir o que está aberto por responsável e por prazo.
- **Alertas de vencimento.** Uma regra agendada no EventBridge avisa o responsável quando o prazo de uma ação está próximo ou vencido.
- **Acompanhamento de decisões.** Cruzar decisões das atas com os dados do CRM ao longo do tempo: a decisão D-002 (sinalizar oportunidades paradas há sete dias) pode ser verificada diretamente no CSV.
- **Controle de acesso mais fino.** Além de área e confidencialidade, restringir por região (um gerente regional vê apenas as oportunidades da sua região).
- **Busca híbrida.** Migrar a base vetorial para o OpenSearch Serverless quando o volume justificar o custo fixo.
- **Novas fontes.** Receber exportações periódicas do CRM com data no nome, e-mails e gravações de reunião (com o Amazon Transcribe).
- **Histórico do CRM.** Guardar cada exportação como uma partição por data, para responder "como o pipeline evoluiu".
- **Avaliação contínua.** Ampliar o conjunto de perguntas de referência e usar as avaliações de RAG do Bedrock para medir a qualidade a cada mudança.
- **Infraestrutura como código.** Descrever tudo em AWS CDK ou CloudFormation, para recriar o ambiente de forma idêntica.
- **Prova de conceito.** Implantar o fluxo mínimo (S3, Textract, Knowledge Bases, S3 Vectors) com os três arquivos e registrar as evidências.

---

# 🧠 Checklist Final

- [x] Como transformar documentos escaneados em texto? (2.3: Textract com tabelas e layout)
- [x] Como lidar com diferentes formatos dentro da mesma pasta `raw/`? (1.4 e 2.3: triagem pelo conteúdo e três rotas)
- [x] Como armazenar os documentos originais? (2.1 e 2.2: bucket dedicado, versionado e imutável)
- [x] Como preservar a rastreabilidade entre resposta e documento fonte? (3.4 e 4.3: hash, versão, página e seção em todo dado)
- [x] Como organizar metadados? (3.2 e 3.4: DynamoDB, `.metadata.json` e Glue)
- [x] Como criar busca semântica? (4.1 e 4.2: trechos por seção, Titan Embeddings, S3 Vectors)
- [x] Como usar Amazon Bedrock na solução? (3.3, 4.2 e 4.3: extração, embeddings, SQL e resposta)
- [x] Como proteger documentos sensíveis? (4.5: IAM, KMS, filtro por perfil, Macie, Guardrails)
- [x] Como monitorar falhas? (2.4 e 4.5: status por documento, fila morta, alarmes)
- [x] Como a empresa usaria essa Wiki no dia a dia? (4.4: interface web com login, filtros e fontes)

---

# 🏁 Conclusão

**Sua resposta:**

O problema da empresa não é falta de informação. As decisões, os responsáveis e os números já existem, em três arquivos que ninguém consegue consultar juntos. A proposta resolve isso sem mexer nos originais e sem tratar tudo como se fosse a mesma coisa.

Três escolhas sustentam a solução. A primeira é **dar a cada formato o caminho certo**: o PDF já tem texto e não paga OCR; a folha digitalizada passa pelo Textract, que entrega a tabela e separa o que é impresso do que foi escrito à mão; o CSV vira tabela consultável, porque somar 240 oportunidades é trabalho para SQL, e não para busca por semelhança. A segunda é **não confiar na IA sem conferência**: cada item extraído precisa da frase que o sustenta, cada resposta cita arquivo e página, e quando a base não tem a informação a Wiki diz isso. A terceira é **pagar pelo que se usa**: todos os componentes são sem servidor e a base vetorial não tem custo mínimo, o que mantém a conta proporcional ao uso e permite começar pequeno.

O resultado esperado é que uma pergunta como "a campanha Rota 120 atingiu a meta?" receba, em segundos, a meta aprovada na ata de julho, o valor calculado no CRM e o link para os dois documentos. A liderança deixa de depender da memória de quem estava na reunião.

O próximo passo recomendado é uma prova de conceito com os três arquivos deste laboratório, para ajustar os limites de confiança e medir o custo real antes de ampliar o acervo.
