"""
Módulo de Catálogo de Habilidades e Regras Pedagógicas (SAEB / BNCC).

Responsável por armazenar a matriz curricular de referência (Língua Portuguesa - 8º Ano,
1º Simulado SAEB/2026 - SEMEC Teresina), realizar o cruzamento automático entre colunas
de arquivos CSV e códigos de habilidades/questões, classificar os níveis de proficiência
e padronizar termos estatísticos em português.
"""

import re
import pandas as pd


# ==============================================================================
# MATRIZ DE HABILIDADES - LÍNGUA PORTUGUESA (8º ANO)
# Fonte: SEMEC Teresina / GEFOR - 1º Simulado SAEB/2026
# ==============================================================================

SAEB_LP_SKILLS = [
    {
        "codigo_saeb": "9L2.1.G",
        "codigo_bncc": "EF69LP14",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": (
            "Identificar, em textos narrativos, o enredo, os personagens e suas características "
            "físicas e psicológicas, a caracterização dos espaços, os tempos cronológico e psicológico, "
            "o foco narrativo e/ou opinião do narrador sobre os acontecimentos e personagens."
        ),
        "bloco_1": [{"questao": 12, "gabarito": "C"}],
        "bloco_2": [{"questao": 7, "gabarito": "C"}],
    },
    {
        "codigo_saeb": "9L2.1.K",
        "codigo_bncc": "EF69LP18",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": (
            "Reconhecer os mecanismos de representação das diferentes vozes no texto "
            "(do narrador, de personagens em discurso direto e indireto)."
        ),
        "bloco_1": [
            {"questao": 9, "gabarito": "C"},
            {"questao": 10, "gabarito": "C"},
        ],
        "bloco_2": [],
    },
    {
        "codigo_saeb": "9L2.1.H",
        "codigo_bncc": "EF69LP15",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": (
            "Identificar, em textos narrativos, a situação inicial, o conflito gerador, "
            "o clímax e o desfecho."
        ),
        "bloco_1": [{"questao": 11, "gabarito": "D"}],
        "bloco_2": [{"questao": 9, "gabarito": "D"}],
    },
    {
        "codigo_saeb": "9L2.1.F",
        "codigo_bncc": "EF69LP13",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": (
            "Analisar, em textos narrativos ficcionais, as diferentes formas de composição "
            "próprias de cada gênero."
        ),
        "bloco_1": [{"questao": 13, "gabarito": "B"}],
        "bloco_2": [{"questao": 8, "gabarito": "C"}],
    },
    {
        "codigo_saeb": "9L1.3.I",
        "codigo_bncc": "EF06LP05",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": (
            "Ler e compreender carta de reclamação, carta pessoal, diário, Código de Defesa do "
            "Consumidor, post e comentário, considerando a situação comunicativa e o tema do texto."
        ),
        "bloco_1": [
            {"questao": 4, "gabarito": "D"},
            {"questao": 5, "gabarito": "B"},
        ],
        "bloco_2": [],
    },
    {
        "codigo_saeb": "9L1.3.C",
        "codigo_bncc": "EF06LP03",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": (
            "Analisar, a partir do contexto de produção, a forma de organização da carta de reclamação "
            "(datação, forma de início, apresentação contextualizada do pedido ou da reclamação, "
            "em geral, acompanhada de explicações, argumentos e/ou relatos do problema)."
        ),
        "bloco_1": [
            {"questao": 2, "gabarito": "D"},
            {"questao": 3, "gabarito": "A"},
        ],
        "bloco_2": [],
    },
    {
        "codigo_saeb": "9L1.3.D",
        "codigo_bncc": "EF06LP04",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": (
            "Identificar o objeto da reclamação e/ou da solicitação e sua sustentação, explicação "
            "ou justificativa, de forma a poder analisar a pertinência da solicitação ou justificação."
        ),
        "bloco_1": [
            {"questao": 1, "gabarito": "B"},
            {"questao": 6, "gabarito": "A"},
        ],
        "bloco_2": [],
    },
    {
        "codigo_saeb": "9AL1.1.C",
        "codigo_bncc": "EF06LP31",
        "eixo_saeb": "Identificar os recursos de modalização em textos diversos.",
        "descricao_bncc": (
            "Identificar os efeitos de sentido provocados pelo uso do ponto de exclamação "
            "e ponto de interrogação."
        ),
        "bloco_1": [
            {"questao": 7, "gabarito": "A"},
            {"questao": 8, "gabarito": "B"},
        ],
        "bloco_2": [],
    },
    {
        "codigo_saeb": "9L2.1.J",
        "codigo_bncc": "EF69LP17",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": (
            "Reconhecer, em poemas visuais e concretos, efeitos de sentido decorrentes do uso de "
            "recursos gráfico-espacial, imagens e sua relação com o texto verbal."
        ),
        "bloco_1": [],
        "bloco_2": [{"questao": 1, "gabarito": "B"}],
    },
    {
        "codigo_saeb": "9L2.1.I",
        "codigo_bncc": "EF69LP16",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": (
            "Interpretar, em poemas, efeitos produzidos pelo uso de recursos expressivos sonoros "
            "(estrofação, rimas, aliterações etc.) e semânticos (figuras de linguagem, por exemplo)."
        ),
        "bloco_1": [],
        "bloco_2": [
            {"questao": 2, "gabarito": "A"},
            {"questao": 3, "gabarito": "D"},
            {"questao": 10, "gabarito": "A"},
        ],
    },
    {
        "codigo_saeb": "9L2.1.N",
        "codigo_bncc": "EF06LP01",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": (
            "Ler e compreender poemas, crônicas, cordéis, letras de música, HQs, mangás e tirinhas, "
            "considerando a situação comunicativa e o tema do texto."
        ),
        "bloco_1": [],
        "bloco_2": [
            {"questao": 6, "gabarito": "A"},
            {"questao": 13, "gabarito": "C"},
        ],
    },
    {
        "codigo_saeb": "9AL2.1.B",
        "codigo_bncc": "EF06LP20",
        "eixo_saeb": "Analisar o uso de figuras de linguagem como estratégia argumentativa.",
        "descricao_bncc": (
            "Analisar os efeitos de sentido do uso das figuras de linguagem comparação e metáfora."
        ),
        "bloco_1": [],
        "bloco_2": [
            {"questao": 4, "gabarito": "B"},
            {"questao": 5, "gabarito": "B"},
        ],
    },
    {
        "codigo_saeb": "9AL2.5.A",
        "codigo_bncc": "EF69LP40",
        "eixo_saeb": "Analisar as variedades linguísticas em textos.",
        "descricao_bncc": (
            "Analisar, em textos narrativos, os efeitos de sentido decorrentes dos tipos de discurso, "
            "dos verbos de enunciação e das variedades linguísticas empregados nos discursos."
        ),
        "bloco_1": [],
        "bloco_2": [
            {"questao": 11, "gabarito": "A"},
            {"questao": 12, "gabarito": "D"},
        ],
    },
]


# ==============================================================================
# DICIONÁRIO DE TRADUÇÃO DE MÉTRICAS E TIPOS DE DADOS
# ==============================================================================

METRIC_LABELS_PT = {
    "count": "Registros",
    "mean": "Média",
    "median": "Mediana",
    "std": "Desvio padrão",
    "min": "Mínimo",
    "max": "Máximo",
    "25%": "1º Quartil (25%)",
    "50%": "Mediana (50%)",
    "75%": "3º Quartil (75%)",
    "q25": "1º Quartil (25%)",
    "q50": "Mediana (50%)",
    "q75": "3º Quartil (75%)",
    "missing": "Ausentes",
    "missing_values": "Valores ausentes",
    "unique": "Valores distintos",
    "sum": "Soma",
    "var": "Variância",
}

DTYPE_LABELS_PT = {
    "int64": "Número inteiro",
    "float64": "Número decimal",
    "object": "Texto",
    "string": "Texto",
    "bool": "Booleano (Sim/Não)",
    "category": "Categoria",
    "datetime64[ns]": "Data e hora",
}


# ==============================================================================
# FUNÇÕES DE CONSULTA E CLASSIFICAÇÃO PEDAGÓGICA
# ==============================================================================

def get_skills_catalog_df() -> pd.DataFrame:
    """
    Constrói e retorna um DataFrame estruturado contendo todas as habilidades
    do catálogo oficial (SAEB e BNCC), seus respectivos blocos, questões e gabaritos.
    """
    rows = []
    for item in SAEB_LP_SKILLS:
        q_b1 = ", ".join(
            f"Q{q['questao']} ({q['gabarito']})" for q in item["bloco_1"]
        ) or "—"
        q_b2 = ", ".join(
            f"Q{q['questao']} ({q['gabarito']})" for q in item["bloco_2"]
        ) or "—"

        blocos = []
        if item["bloco_1"]:
            blocos.append("Bloco 1")
        if item["bloco_2"]:
            blocos.append("Bloco 2")

        rows.append({
            "Código SAEB": item["codigo_saeb"],
            "Código BNCC": item["codigo_bncc"],
            "Bloco": " e ".join(blocos),
            "Questões Bloco 1 (Gab.)": q_b1,
            "Questões Bloco 2 (Gab.)": q_b2,
            "Habilidade SAEB": item["eixo_saeb"],
            "Descrição BNCC": item["descricao_bncc"],
        })
    return pd.DataFrame(rows)


def match_column_to_skill(col_name: str) -> dict | None:
    """
    Verifica se o nome de uma coluna do arquivo CSV corresponde a:
      1. Um código SAEB (ex.: '9L2.1.G')
      2. Um código BNCC (ex.: 'EF69LP14')
      3. Uma identificação de bloco e questão do simulado (ex.: 'B1_Q12', 'BLOCO2_Q7')

    Retorna o dicionário da habilidade encontrada ou None caso não haja vínculo.
    """
    clean = str(col_name).strip().upper()

    # Busca direta por código SAEB ou BNCC no nome da coluna
    for item in SAEB_LP_SKILLS:
        saeb = item["codigo_saeb"].upper()
        bncc = item["codigo_bncc"].upper()
        if saeb in clean or bncc in clean:
            return item

    # Busca por padrão de Bloco e Questão (ex.: B1_Q12, BLOCO 2 Q7)
    match_bq = re.search(
        r"(?:B|BLOCO)[\s_-]*([12])[\s_-]*(?:Q|QUESTAO|QUESTÃO)?[\s_-]*(\d{1,2})\b",
        clean
    )
    if match_bq:
        bloco = int(match_bq.group(1))
        questao = int(match_bq.group(2))
        chave_bloco = "bloco_1" if bloco == 1 else "bloco_2"
        for item in SAEB_LP_SKILLS:
            for q in item[chave_bloco]:
                if q["questao"] == questao:
                    return item

    return None


def classify_proficiency(score_pct: float) -> str:
    """
    Classifica o percentual médio de aproveitamento em faixas pedagógicas:
      - >= 70%: Adequado
      - 50% a 69.9%: Intermediário
      - < 50%: Crítico / Recomposição
    """
    if pd.isna(score_pct):
        return "Sem dados"
    if score_pct >= 70:
        return "Adequado (≥ 70%)"
    if score_pct >= 50:
        return "Intermediário (50% - 69%)"
    return "Crítico / Recomposição (< 50%)"


def translate_metrics_dict(metrics: dict) -> dict:
    """
    Traduz recursivamente as chaves estatísticas de inglês para português
    antes da exportação em JSON.
    """
    translated_metrics = {}
    for section, content in metrics.items():
        if isinstance(content, dict):
            translated_section = {}
            for key, value in content.items():
                if isinstance(value, dict):
                    translated_section[key] = {
                        METRIC_LABELS_PT.get(str(k).lower(), k): v
                        for k, v in value.items()
                    }
                else:
                    translated_section[METRIC_LABELS_PT.get(str(key).lower(), key)] = value
            translated_metrics[section] = translated_section
        else:
            translated_metrics[section] = content
    return translated_metrics
