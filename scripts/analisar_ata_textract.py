"""
Evidência da rota de OCR: analisa a ata digitalizada com o Amazon Textract.

Chama AnalyzeDocument com TABLES e LAYOUT, como proposto na Quest 2.3, e mostra
o que a proposta afirma sobre o arquivo: a tabela de indicadores, as anotações
manuscritas, os prazos das deliberações e as linhas de baixa confiança.

Uso (na raiz do repositório, com credenciais da AWS, por exemplo no CloudShell):
    python3 scripts/analisar_ata_textract.py

Saídas (pasta evidencias/, criada na execução):
    textract-resposta.json   -> resposta completa do Textract
    textract-relatorio.md    -> resumo legível

O arquivo em raw/ é apenas lido. Nada é gravado nessa pasta.
"""

import json
import re
import sys
from pathlib import Path

REGIAO = "us-east-1"
IMAGEM_PADRAO = Path("raw/ata_resultados_vendas_novos_dados.png")
PASTA_SAIDA = Path("evidencias")
LIMITE_CONFIANCA = 85.0  # mesmo ponto de partida citado no resposta.md
PADRAO_DATA = re.compile(r"\d{2}/\d{2}/\d{4}")


def chamar_textract(caminho: Path) -> dict:
    import boto3  # importado aqui para o restante do script rodar sem a AWS

    cliente = boto3.client("textract", region_name=REGIAO)
    return cliente.analyze_document(
        Document={"Bytes": caminho.read_bytes()},
        FeatureTypes=["TABLES", "LAYOUT"],
    )


def filhos(bloco: dict, por_id: dict) -> list[dict]:
    """Devolve os blocos filhos (relação CHILD) de um bloco."""
    ids = [
        i
        for rel in bloco.get("Relationships", [])
        if rel["Type"] == "CHILD"
        for i in rel["Ids"]
    ]
    return [por_id[i] for i in ids if i in por_id]


def texto_do_bloco(bloco: dict, por_id: dict) -> str:
    return " ".join(
        f["Text"] for f in filhos(bloco, por_id) if f["BlockType"] == "WORD"
    )


def montar_tabelas(blocos: list[dict], por_id: dict) -> list[list[list[str]]]:
    """Reconstrói cada tabela como uma matriz de textos."""
    tabelas = []
    for tabela in (b for b in blocos if b["BlockType"] == "TABLE"):
        celulas = [f for f in filhos(tabela, por_id) if f["BlockType"] == "CELL"]
        if not celulas:
            continue
        linhas = max(c["RowIndex"] for c in celulas)
        colunas = max(c["ColumnIndex"] for c in celulas)
        matriz = [["" for _ in range(colunas)] for _ in range(linhas)]
        for c in celulas:
            matriz[c["RowIndex"] - 1][c["ColumnIndex"] - 1] = texto_do_bloco(c, por_id)
        tabelas.append(matriz)
    return tabelas


def analisar(resposta: dict) -> dict:
    blocos = resposta["Blocks"]
    por_id = {b["Id"]: b for b in blocos}
    linhas = [b for b in blocos if b["BlockType"] == "LINE"]
    palavras = [b for b in blocos if b["BlockType"] == "WORD"]

    contagem_layout = {}
    for b in blocos:
        if b["BlockType"].startswith("LAYOUT_"):
            contagem_layout[b["BlockType"]] = contagem_layout.get(b["BlockType"], 0) + 1

    prazos = []
    for linha in linhas:
        if "prazo" not in linha["Text"].lower():
            continue
        datas = [
            {"texto": p["Text"], "confianca": round(p["Confidence"], 2)}
            for p in filhos(linha, por_id)
            if p["BlockType"] == "WORD" and PADRAO_DATA.search(p["Text"])
        ]
        prazos.append(
            {
                "linha": linha["Text"],
                "confianca_linha": round(linha["Confidence"], 2),
                "datas": datas,
            }
        )

    return {
        "total_linhas": len(linhas),
        "total_palavras": len(palavras),
        "confianca_media_linhas": round(
            sum(l["Confidence"] for l in linhas) / len(linhas), 2
        )
        if linhas
        else None,
        "layout": dict(sorted(contagem_layout.items())),
        "tabelas": montar_tabelas(blocos, por_id),
        "manuscrito": [
            {"texto": p["Text"], "confianca": round(p["Confidence"], 2)}
            for p in palavras
            if p.get("TextType") == "HANDWRITING"
        ],
        "prazos": prazos,
        "baixa_confianca": [
            {"texto": l["Text"], "confianca": round(l["Confidence"], 2)}
            for l in linhas
            if l["Confidence"] < LIMITE_CONFIANCA
        ],
        "texto": [l["Text"] for l in linhas],
    }


def gerar_relatorio(analise: dict, nome_arquivo: str) -> str:
    r = [
        "# Evidência: Amazon Textract na ata digitalizada",
        "",
        f"- Arquivo: `{nome_arquivo}`",
        "- Operação: `AnalyzeDocument` com `TABLES` e `LAYOUT`",
        f"- Região: `{REGIAO}`",
        f"- Linhas detectadas: {analise['total_linhas']}",
        f"- Palavras detectadas: {analise['total_palavras']}",
        f"- Confiança média das linhas: {analise['confianca_media_linhas']}%",
        "",
        "## Blocos de layout",
        "",
    ]
    r += [f"- `{tipo}`: {qtd}" for tipo, qtd in analise["layout"].items()] or ["- nenhum"]

    r += ["", "## Tabelas reconstruídas", ""]
    if not analise["tabelas"]:
        r.append("Nenhuma tabela detectada.")
    for n, matriz in enumerate(analise["tabelas"], start=1):
        r.append(f"**Tabela {n}** ({len(matriz)} linhas x {len(matriz[0])} colunas)")
        r.append("")
        r.append("| " + " | ".join(matriz[0]) + " |")
        r.append("|" + "---|" * len(matriz[0]))
        r += ["| " + " | ".join(linha) + " |" for linha in matriz[1:]]
        r.append("")

    r += ["## Palavras classificadas como manuscritas", ""]
    r += [
        f"- `{m['texto']}` ({m['confianca']}%)" for m in analise["manuscrito"]
    ] or ["Nenhuma palavra marcada como `HANDWRITING`."]

    r += ["", "## Prazos das deliberações", ""]
    for p in analise["prazos"]:
        datas = ", ".join(f"`{d['texto']}` ({d['confianca']}%)" for d in p["datas"])
        r.append(f"- {p['linha']}")
        r.append(f"  - confiança da linha: {p['confianca_linha']}%")
        r.append(f"  - datas lidas: {datas or 'nenhuma data reconhecida'}")
    if not analise["prazos"]:
        r.append("Nenhuma linha com a palavra \"Prazo\" foi reconhecida.")

    r += ["", f"## Linhas abaixo de {LIMITE_CONFIANCA:.0f}% de confiança", ""]
    r += [
        f"- `{b['texto']}` ({b['confianca']}%)" for b in analise["baixa_confianca"]
    ] or ["Nenhuma."]

    r += ["", "## Texto completo, linha a linha", "", "```text"]
    r += analise["texto"]
    r += ["```", ""]
    return "\n".join(r)


def main() -> None:
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else IMAGEM_PADRAO
    if not caminho.is_file():
        sys.exit(f"Arquivo não encontrado: {caminho} (rode na raiz do repositório)")

    resposta = chamar_textract(caminho)
    analise = analisar(resposta)
    relatorio = gerar_relatorio(analise, caminho.name)

    PASTA_SAIDA.mkdir(exist_ok=True)
    (PASTA_SAIDA / "textract-resposta.json").write_text(
        json.dumps(resposta, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    (PASTA_SAIDA / "textract-relatorio.md").write_text(relatorio, encoding="utf-8")

    print(relatorio)
    print(f"Arquivos salvos em {PASTA_SAIDA}/")


if __name__ == "__main__":
    main()
