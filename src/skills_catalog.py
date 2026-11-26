"""
Módulo de Catálogo de Habilidades e Regras Pedagógicas (SAEB / BNCC).

Contém as matrizes oficiais de Língua Portuguesa — 8º Ano (SEMEC Teresina)
do 1º ao 7º Simulado SAEB/2026 (Blocos 1 a 4, Questões 1 a 52), normalização
de códigos SAEB, classificação por Macro-Eixos Cognitivos e faixas de proficiência.
"""

import re
import pandas as pd


# ==============================================================================
# MATRIZ DE HABILIDADES - LÍNGUA PORTUGUESA (8º ANO)
# Fonte: SEMEC Teresina / GEFOR - 1º ao 7º Simulado SAEB/2026
# ==============================================================================

SAEB_LP_SKILLS = [
    # --------------------------------------------------------------------------
    # 1º SIMULADO SAEB/2026 (Blocos 1 e 2 | Q1–Q26)
    # --------------------------------------------------------------------------
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.G",
        "codigo_bncc": "EF69LP14",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Identificar, em textos narrativos, o enredo, os personagens, espaços, tempos e foco narrativo.",
        "blocos": {1: [{"questao": 12, "gabarito": "C"}], 2: [{"questao": 7, "gabarito": "C"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.K",
        "codigo_bncc": "EF69LP18",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Reconhecer os mecanismos de representação das diferentes vozes no texto.",
        "blocos": {1: [{"questao": 9, "gabarito": "C"}, {"questao": 10, "gabarito": "C"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.H",
        "codigo_bncc": "EF69LP15",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Identificar, em textos narrativos, a situação inicial, o conflito gerador, o clímax e o desfecho.",
        "blocos": {1: [{"questao": 11, "gabarito": "D"}], 2: [{"questao": 9, "gabarito": "D"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.F",
        "codigo_bncc": "EF69LP13",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar, em textos narrativos ficcionais, as diferentes formas de composição próprias de cada gênero.",
        "blocos": {1: [{"questao": 13, "gabarito": "B"}], 2: [{"questao": 8, "gabarito": "C"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9L1.3.I",
        "codigo_bncc": "EF06LP05",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": "Ler e compreender carta de reclamação, considerando a situação comunicativa e o tema.",
        "blocos": {1: [{"questao": 4, "gabarito": "D"}, {"questao": 5, "gabarito": "B"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9L1.3.C",
        "codigo_bncc": "EF06LP03",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": "Analisar a forma de organização da carta de reclamação.",
        "blocos": {1: [{"questao": 2, "gabarito": "D"}, {"questao": 3, "gabarito": "A"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9L1.3.D",
        "codigo_bncc": "EF06LP04",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": "Identificar o objeto da reclamação e/ou solicitação e sua sustentação.",
        "blocos": {1: [{"questao": 1, "gabarito": "B"}, {"questao": 6, "gabarito": "A"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9AL1.1.C",
        "codigo_bncc": "EF06LP31",
        "eixo_saeb": "Identificar os recursos de modalização em textos diversos.",
        "descricao_bncc": "Identificar os efeitos de sentido provocados pelo uso do ponto de exclamação e interrogação.",
        "blocos": {1: [{"questao": 7, "gabarito": "A"}, {"questao": 8, "gabarito": "B"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.J",
        "codigo_bncc": "EF69LP17",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Reconhecer, em poemas visuais e concretos, efeitos de sentido de recursos gráfico-espaciais.",
        "blocos": {2: [{"questao": 1, "gabarito": "B"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.I",
        "codigo_bncc": "EF69LP16",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Interpretar, em poemas, efeitos produzidos por recursos expressivos sonoros e semânticos.",
        "blocos": {2: [{"questao": 2, "gabarito": "A"}, {"questao": 3, "gabarito": "D"}, {"questao": 10, "gabarito": "A"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.N",
        "codigo_bncc": "EF06LP01",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Ler e compreender poemas, crônicas, cordéis, letras de música, HQs e tirinhas.",
        "blocos": {2: [{"questao": 6, "gabarito": "A"}, {"questao": 13, "gabarito": "C"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9AL2.1.B",
        "codigo_bncc": "EF06LP20",
        "eixo_saeb": "Analisar o uso de figuras de linguagem como estratégia argumentativa.",
        "descricao_bncc": "Analisar os efeitos de sentido do uso das figuras de linguagem comparação e metáfora.",
        "blocos": {2: [{"questao": 4, "gabarito": "B"}, {"questao": 5, "gabarito": "B"}]},
    },
    {
        "simulado_num": 1,
        "simulado": "1º Simulado SAEB/2026",
        "codigo_saeb": "9AL2.5.A",
        "codigo_bncc": "EF69LP40",
        "eixo_saeb": "Analisar as variedades linguísticas em textos.",
        "descricao_bncc": "Analisar efeitos de sentido decorrentes dos tipos de discurso e variedades linguísticas.",
        "blocos": {2: [{"questao": 11, "gabarito": "A"}, {"questao": 12, "gabarito": "D"}]},
    },

    # --------------------------------------------------------------------------
    # 2º SIMULADO SAEB/2026 (Blocos 1 e 2 | Q1–Q26 | Matriz 5º Ano)
    # --------------------------------------------------------------------------
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L1.2",
        "codigo_bncc": "—",
        "eixo_saeb": "Localizar informação explícita.",
        "descricao_bncc": "Localizar informação explícita.",
        "blocos": {1: [{"questao": 1, "gabarito": "B"}], 2: [{"questao": 1, "gabarito": "C"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L2.7",
        "codigo_bncc": "—",
        "eixo_saeb": "Inferir o sentido de palavras ou expressões em textos.",
        "descricao_bncc": "Inferir o sentido de palavras ou expressões em textos.",
        "blocos": {1: [{"questao": 2, "gabarito": "C"}], 2: [{"questao": 11, "gabarito": "B"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L2.6",
        "codigo_bncc": "—",
        "eixo_saeb": "Inferir informações implícitas em textos.",
        "descricao_bncc": "Inferir informações implícitas em textos.",
        "blocos": {1: [{"questao": 3, "gabarito": "D"}], 2: [{"questao": 3, "gabarito": "C"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L1.1",
        "codigo_bncc": "—",
        "eixo_saeb": "Identificar a ideia central do texto.",
        "descricao_bncc": "Identificar a ideia central do texto.",
        "blocos": {1: [{"questao": 4, "gabarito": "D"}], 2: [{"questao": 8, "gabarito": "C"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L2.8",
        "codigo_bncc": "—",
        "eixo_saeb": "Analisar os efeitos de sentido de recursos multissemióticos.",
        "descricao_bncc": "Analisar os efeitos de sentido de recursos multissemióticos em textos.",
        "blocos": {1: [{"questao": 12, "gabarito": "A"}], 2: [{"questao": 4, "gabarito": "A"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L1.3",
        "codigo_bncc": "—",
        "eixo_saeb": "Reconhecer diferentes gêneros textuais.",
        "descricao_bncc": "Reconhecer diferentes gêneros textuais.",
        "blocos": {1: [{"questao": 9, "gabarito": "D"}], 2: [{"questao": 9, "gabarito": "B"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L2.1.A",
        "codigo_bncc": "—",
        "eixo_saeb": "Analisar elementos constitutivos de gêneros (Conto / Anedota; Tirinha).",
        "descricao_bncc": "Analisar elementos constitutivos de conto, anedota e tirinha.",
        "blocos": {2: [{"questao": 5, "gabarito": "D"}, {"questao": 13, "gabarito": "B"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L2.1.B",
        "codigo_bncc": "—",
        "eixo_saeb": "Analisar elementos constitutivos de gêneros (Verbete).",
        "descricao_bncc": "Analisar elementos constitutivos do gênero verbete.",
        "blocos": {1: [{"questao": 8, "gabarito": "A"}, {"questao": 10, "gabarito": "C"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L2.1.C",
        "codigo_bncc": "—",
        "eixo_saeb": "Analisar elementos constitutivos de gêneros (Tirinha).",
        "descricao_bncc": "Analisar elementos constitutivos do gênero tirinha.",
        "blocos": {1: [{"questao": 5, "gabarito": "B"}, {"questao": 13, "gabarito": "B"}], 2: [{"questao": 2, "gabarito": "A"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L2.1.D",
        "codigo_bncc": "—",
        "eixo_saeb": "Analisar elementos constitutivos de gêneros (Notícia / Reportagem).",
        "descricao_bncc": "Analisar elementos constitutivos de notícia e reportagem.",
        "blocos": {2: [{"questao": 10, "gabarito": "D"}, {"questao": 12, "gabarito": "A"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L1.4",
        "codigo_bncc": "—",
        "eixo_saeb": "Identificar elementos constitutivos de textos narrativos.",
        "descricao_bncc": "Identificar elementos constitutivos de textos narrativos.",
        "blocos": {1: [{"questao": 7, "gabarito": "A"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5AL1.5",
        "codigo_bncc": "—",
        "eixo_saeb": "Identificar os mecanismos de referenciação lexical e pronominal.",
        "descricao_bncc": "Identificar os mecanismos de referenciação lexical e pronominal.",
        "blocos": {1: [{"questao": 6, "gabarito": "C"}, {"questao": 11, "gabarito": "A"}]},
    },
    {
        "simulado_num": 2,
        "simulado": "2º Simulado SAEB/2026",
        "codigo_saeb": "5L3.1",
        "codigo_bncc": "—",
        "eixo_saeb": "Avaliar a fidedignidade de informações sobre um mesmo fato em diferentes mídias.",
        "descricao_bncc": "Avaliar a fidedignidade de informações sobre um mesmo fato veiculadas em diferentes mídias.",
        "blocos": {2: [{"questao": 6, "gabarito": "A"}, {"questao": 7, "gabarito": "D"}]},
    },

    # --------------------------------------------------------------------------
    # 3º SIMULADO SAEB/2026 (Blocos 1 e 2 | Q1–Q26)
    # --------------------------------------------------------------------------
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L2.3",
        "codigo_bncc": "EF69LP10",
        "eixo_saeb": "Inferir a presença de valores sociais, culturais e humanos em textos literários.",
        "descricao_bncc": "Inferir a presença de valores sociais, culturais e humanos e de diferentes visões de mundo.",
        "blocos": {1: [{"questao": 4, "gabarito": "B"}], 2: [{"questao": 12, "gabarito": "D"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.B",
        "codigo_bncc": "EF69LP41",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar efeitos de sentido de palavras e expressões com sentido denotativo e conotativo.",
        "blocos": {1: [{"questao": 5, "gabarito": "C"}], 2: [{"questao": 13, "gabarito": "B"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.J",
        "codigo_bncc": "EF69LP17",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Reconhecer, em poemas visuais e concretos, efeitos de sentido de recursos gráfico-espaciais.",
        "blocos": {1: [{"questao": 6, "gabarito": "A"}, {"questao": 7, "gabarito": "B"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.L",
        "codigo_bncc": "EF07LP02",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Identificar, em texto dramático, personagem, ato, cena, fala e indicações cênicas.",
        "blocos": {1: [{"questao": 1, "gabarito": "C"}, {"questao": 2, "gabarito": "B"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L1.5.B",
        "codigo_bncc": "EF69LP34",
        "eixo_saeb": "Identificar elementos constitutivos de gêneros de divulgação científica.",
        "descricao_bncc": "Articular a linguagem verbal e não verbal (esquemas, infográficos) na divulgação científica.",
        "blocos": {1: [{"questao": 8, "gabarito": "A"}, {"questao": 9, "gabarito": "C"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L1.5.C",
        "codigo_bncc": "EF69LP49",
        "eixo_saeb": "Identificar elementos constitutivos de gêneros de divulgação científica.",
        "descricao_bncc": "Analisar a construção composicional de textos de divulgação científica.",
        "blocos": {1: [{"questao": 10, "gabarito": "D"}, {"questao": 11, "gabarito": "A"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L1.5.D",
        "codigo_bncc": "EF69LP50",
        "eixo_saeb": "Identificar elementos constitutivos de gêneros de divulgação científica.",
        "descricao_bncc": "Reconhecer traços da linguagem de divulgação científica (impessoalização, citações, termos técnicos).",
        "blocos": {1: [{"questao": 12, "gabarito": "B"}, {"questao": 13, "gabarito": "D"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9AL2.3.A",
        "codigo_bncc": "EF07LP32",
        "eixo_saeb": "Analisar os mecanismos que contribuem para a progressão textual.",
        "descricao_bncc": "Identificar períodos compostos conectados por vírgula ou conjunções de soma e oposição.",
        "blocos": {1: [{"questao": 3, "gabarito": "D"}], 2: [{"questao": 9, "gabarito": "C"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L1.2.C",
        "codigo_bncc": "EF07LP07",
        "eixo_saeb": "Identificar elementos constitutivos de textos do domínio jornalístico/midiático.",
        "descricao_bncc": "Identificar, em reportagens, notícias e artigos de opinião, o fato ou temática retratada.",
        "blocos": {2: [{"questao": 1, "gabarito": "A"}, {"questao": 2, "gabarito": "D"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L2.6",
        "codigo_bncc": "EF69LP28",
        "eixo_saeb": "Distinguir fatos de opiniões em textos.",
        "descricao_bncc": "Distinguir, em textos jornalísticos, um fato da opinião relativa a esse fato.",
        "blocos": {2: [{"questao": 5, "gabarito": "C"}, {"questao": 6, "gabarito": "B"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L2.10.A",
        "codigo_bncc": "EF07LP43",
        "eixo_saeb": "Analisar os efeitos de sentido dos mecanismos de construção de textos jornalísticos.",
        "descricao_bncc": "Analisar e utilizar as formas de composição de diferentes gêneros jornalísticos.",
        "blocos": {2: [{"questao": 3, "gabarito": "A"}, {"questao": 4, "gabarito": "D"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L1.4.C",
        "codigo_bncc": "EF07LP08",
        "eixo_saeb": "Identificar teses/opiniões/posicionamentos explícitos e argumentos em textos.",
        "descricao_bncc": "Identificar, em artigos de opinião e cartas do leitor, teses, opiniões e argumentos.",
        "blocos": {2: [{"questao": 7, "gabarito": "C"}, {"questao": 8, "gabarito": "B"}]},
    },
    {
        "simulado_num": 3,
        "simulado": "3º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.D",
        "codigo_bncc": "EF69LP43",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar, em textos versificados, efeitos de recursos rítmicos, sonoros e figuras de linguagem.",
        "blocos": {2: [{"questao": 10, "gabarito": "A"}, {"questao": 11, "gabarito": "B"}]},
    },

    # --------------------------------------------------------------------------
    # 4º SIMULADO SAEB/2026 (Blocos 1 e 2 | Q1–Q26 | Pareado com o 1º Simulado)
    # --------------------------------------------------------------------------
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.G",
        "codigo_bncc": "EF69LP14",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar elementos da narrativa (enredo, personagens, espaço, tempo e foco narrativo).",
        "blocos": {1: [{"questao": 10, "gabarito": "D"}], 2: [{"questao": 21, "gabarito": "D"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.K",
        "codigo_bncc": "EF69LP18",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar vozes no texto narrativo.",
        "blocos": {1: [{"questao": 8, "gabarito": "D"}, {"questao": 12, "gabarito": "B"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.H",
        "codigo_bncc": "EF69LP15",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Identificar momentos da narrativa (situação inicial, conflito, clímax e desfecho).",
        "blocos": {1: [{"questao": 9, "gabarito": "C"}], 2: [{"questao": 23, "gabarito": "C"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.F",
        "codigo_bncc": "EF69LP13",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar características do gênero literário narrativo.",
        "blocos": {1: [{"questao": 11, "gabarito": "D"}], 2: [{"questao": 22, "gabarito": "B"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9L1.3.I",
        "codigo_bncc": "EF06LP05",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": "Identificar situação comunicativa e tema de textos reivindicatórios.",
        "blocos": {1: [{"questao": 4, "gabarito": "B"}, {"questao": 5, "gabarito": "C"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9L1.3.C",
        "codigo_bncc": "EF06LP03",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": "Analisar características da carta de reclamação.",
        "blocos": {1: [{"questao": 2, "gabarito": "C"}, {"questao": 3, "gabarito": "B"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9L1.3.D",
        "codigo_bncc": "EF06LP04",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": "Identificar o objeto da reclamação e/ou da solicitação.",
        "blocos": {1: [{"questao": 1, "gabarito": "B"}, {"questao": 6, "gabarito": "A"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9AL2.1.B",
        "codigo_bncc": "EF06LP20",
        "eixo_saeb": "Analisar o uso de figuras de linguagem como estratégia argumentativa.",
        "descricao_bncc": "Analisar o uso de comparação e metáfora como estratégia argumentativa.",
        "blocos": {1: [{"questao": 13, "gabarito": "A"}], 2: [{"questao": 18, "gabarito": "D"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9AL1.1.C",
        "codigo_bncc": "EF06LP31",
        "eixo_saeb": "Identificar os recursos de modalização em textos diversos.",
        "descricao_bncc": "Identificar os efeitos de sentido dos sinais de pontuação.",
        "blocos": {1: [{"questao": 7, "gabarito": "A"}], 2: [{"questao": 19, "gabarito": "B"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.J",
        "codigo_bncc": "EF69LP17",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar recursos gráficos em textos pertencentes ao domínio literário.",
        "blocos": {2: [{"questao": 14, "gabarito": "C"}, {"questao": 25, "gabarito": "B"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.I",
        "codigo_bncc": "EF69LP16",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar recursos sonoros e semânticos em textos pertencentes ao domínio literário.",
        "blocos": {2: [{"questao": 16, "gabarito": "C"}, {"questao": 17, "gabarito": "D"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.N",
        "codigo_bncc": "EF06LP01",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar situação comunicativa e tema de textos pertencentes ao domínio literário.",
        "blocos": {2: [{"questao": 20, "gabarito": "A"}, {"questao": 26, "gabarito": "D"}]},
    },
    {
        "simulado_num": 4,
        "simulado": "4º Simulado SAEB/2026",
        "codigo_saeb": "9AL2.5.A",
        "codigo_bncc": "EF69LP40",
        "eixo_saeb": "Analisar as variedades linguísticas em textos.",
        "descricao_bncc": "Analisar tipos de discurso, verbos de enunciação e variedades linguísticas.",
        "blocos": {2: [{"questao": 15, "gabarito": "A"}, {"questao": 24, "gabarito": "A"}]},
    },

    # --------------------------------------------------------------------------
    # 5º SIMULADO SAEB/2026 (Blocos 3 e 4 | Q27–Q52)
    # --------------------------------------------------------------------------
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L2.6",
        "codigo_bncc": "EF69LP28",
        "eixo_saeb": "Distinguir fatos de opiniões em textos.",
        "descricao_bncc": "Distinguir, em textos jornalísticos, um fato da opinião relativa a esse fato.",
        "blocos": {3: [{"questao": 27, "gabarito": "A"}], 4: [{"questao": 40, "gabarito": "B"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L1.4.E",
        "codigo_bncc": "EF09LP08",
        "eixo_saeb": "Identificar teses/opiniões/posicionamentos explícitos e argumentos em textos.",
        "descricao_bncc": "Identificar teses, opiniões, argumentos e contra-argumentos em gêneros argumentativos.",
        "blocos": {3: [{"questao": 34, "gabarito": "D"}, {"questao": 36, "gabarito": "D"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L1.4.B",
        "codigo_bncc": "EF69LP30",
        "eixo_saeb": "Identificar teses/opiniões/posicionamentos explícitos e argumentos em textos.",
        "descricao_bncc": "Estabelecer relação entre a tese e os argumentos oferecidos para sustentá-la.",
        "blocos": {3: [{"questao": 35, "gabarito": "A"}, {"questao": 37, "gabarito": "C"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L1.2.D",
        "codigo_bncc": "EF07LP07",
        "eixo_saeb": "Identificar elementos constitutivos de textos do domínio jornalístico/midiático.",
        "descricao_bncc": "Identificar o fato ou a temática retratada e a perspectiva de abordagem.",
        "blocos": {3: [{"questao": 28, "gabarito": "B"}], 4: [{"questao": 41, "gabarito": "D"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L1.2.C",
        "codigo_bncc": "EF67LP03",
        "eixo_saeb": "Identificar elementos constitutivos de textos do domínio jornalístico/midiático.",
        "descricao_bncc": "Interpretar efeitos produzidos por recursos gráfico-visuais e imagens em textos multissemióticos.",
        "blocos": {3: [{"questao": 32, "gabarito": "A"}], 4: [{"questao": 45, "gabarito": "D"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L2.10.A",
        "codigo_bncc": "EF07LP43",
        "eixo_saeb": "Analisar os efeitos de sentido dos mecanismos de construção de textos jornalísticos.",
        "descricao_bncc": "Analisar formas de composição de diferentes gêneros jornalísticos.",
        "blocos": {3: [{"questao": 29, "gabarito": "B"}], 4: [{"questao": 42, "gabarito": "A"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L2.7.A",
        "codigo_bncc": "EF69LP08",
        "eixo_saeb": "Inferir, em textos multissemióticos, efeitos de humor, ironia e/ou crítica.",
        "descricao_bncc": "Identificar efeitos de ironia ou humor em textos variados.",
        "blocos": {3: [{"questao": 33, "gabarito": "C"}], 4: [{"questao": 46, "gabarito": "C"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L1.2.I",
        "codigo_bncc": "EF09LP12",
        "eixo_saeb": "Identificar elementos constitutivos de textos do domínio jornalístico/midiático.",
        "descricao_bncc": "Ler e compreender artigos de opinião, reportagens, notícias, cartas e editoriais.",
        "blocos": {3: [{"questao": 30, "gabarito": "C"}], 4: [{"questao": 43, "gabarito": "B"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L2.9.C",
        "codigo_bncc": "EF67LP06",
        "eixo_saeb": "Analisar a relação temática entre diferentes gêneros jornalísticos.",
        "descricao_bncc": "Comparar informações sobre um mesmo fato divulgadas em diferentes veículos e mídias.",
        "blocos": {3: [{"questao": 38, "gabarito": "D"}, {"questao": 39, "gabarito": "C"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9AL2.3.B",
        "codigo_bncc": "EF08LP45",
        "eixo_saeb": "Analisar os mecanismos que contribuem para a progressão textual.",
        "descricao_bncc": "Identificar, em textos, a função e os sentidos das conjunções coordenativas.",
        "blocos": {3: [{"questao": 31, "gabarito": "A"}], 4: [{"questao": 44, "gabarito": "C"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L1.3.A",
        "codigo_bncc": "EF69LP23",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": "Identificar a forma de organização e hierarquização de textos normativos e legais.",
        "blocos": {4: [{"questao": 47, "gabarito": "D"}, {"questao": 50, "gabarito": "B"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9L1.3.G",
        "codigo_bncc": "EF07LP06",
        "eixo_saeb": "Identificar formas de organização de textos normativos, legais e/ou reivindicatórios.",
        "descricao_bncc": "Ler e compreender propaganda, regimento escolar, ECA, folheto e charge.",
        "blocos": {4: [{"questao": 48, "gabarito": "A"}, {"questao": 51, "gabarito": "C"}]},
    },
    {
        "simulado_num": 5,
        "simulado": "5º Simulado SAEB/2026",
        "codigo_saeb": "9AL1.1.A",
        "codigo_bncc": "EF69LP47",
        "eixo_saeb": "Identificar os recursos de modalização em textos diversos.",
        "descricao_bncc": "Identificar modalidades deônticas (obrigatoriedade/permissibilidade) em textos jurídicos.",
        "blocos": {4: [{"questao": 49, "gabarito": "C"}, {"questao": 52, "gabarito": "A"}]},
    },

    # --------------------------------------------------------------------------
    # 6º SIMULADO SAEB/2026 (Blocos 1 e 2 | Q1–Q26 | Pareado com o 3º Simulado)
    # --------------------------------------------------------------------------
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L2.3",
        "codigo_bncc": "EF69LP10",
        "eixo_saeb": "Inferir a presença de valores sociais, culturais e humanos em textos literários.",
        "descricao_bncc": "Inferir a presença de valores sociais, culturais e humanos em textos literários.",
        "blocos": {1: [{"questao": 7, "gabarito": "D"}], 2: [{"questao": 26, "gabarito": "D"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.B",
        "codigo_bncc": "EF69LP41",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar efeitos de sentido de palavras com sentido denotativo e conotativo.",
        "blocos": {1: [{"questao": 8, "gabarito": "D"}, {"questao": 11, "gabarito": "C"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.J",
        "codigo_bncc": "EF69LP17",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Reconhecer efeitos de sentido de recursos gráfico-espaciais em poemas visuais.",
        "blocos": {1: [{"questao": 9, "gabarito": "B"}, {"questao": 10, "gabarito": "A"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L1.5.B",
        "codigo_bncc": "EF69LP34",
        "eixo_saeb": "Identificar elementos constitutivos de gêneros de divulgação científica.",
        "descricao_bncc": "Articular linguagem verbal e não verbal em textos de divulgação científica.",
        "blocos": {1: [{"questao": 1, "gabarito": "C"}, {"questao": 2, "gabarito": "B"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L1.5.C",
        "codigo_bncc": "EF69LP49",
        "eixo_saeb": "Identificar elementos constitutivos de gêneros de divulgação científica.",
        "descricao_bncc": "Analisar a construção composicional de textos de divulgação científica.",
        "blocos": {1: [{"questao": 3, "gabarito": "B"}, {"questao": 4, "gabarito": "A"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L1.5.D",
        "codigo_bncc": "EF69LP50",
        "eixo_saeb": "Identificar elementos constitutivos de gêneros de divulgação científica.",
        "descricao_bncc": "Reconhecer traços da linguagem de textos de divulgação científica.",
        "blocos": {1: [{"questao": 5, "gabarito": "C"}, {"questao": 6, "gabarito": "B"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L2.1.D",
        "codigo_bncc": "EF69LP43",
        "eixo_saeb": "Analisar elementos constitutivos de textos pertencentes ao domínio literário.",
        "descricao_bncc": "Analisar, em textos versificados, recursos rítmicos, sonoros e figuras de linguagem.",
        "blocos": {1: [{"questao": 13, "gabarito": "D"}], 2: [{"questao": 25, "gabarito": "D"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9AL2.3.A",
        "codigo_bncc": "EF07LP32",
        "eixo_saeb": "Analisar os mecanismos que contribuem para a progressão textual.",
        "descricao_bncc": "Identificar períodos compostos conectados por vírgula ou conjunções de soma/oposição.",
        "blocos": {1: [{"questao": 12, "gabarito": "A"}], 2: [{"questao": 16, "gabarito": "A"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L1.1.C",
        "codigo_bncc": "EF08LP11",
        "eixo_saeb": "Identificar o uso de recursos persuasivos em textos verbais e não verbais.",
        "descricao_bncc": "Identificar e analisar efeitos de sentido de estratégias de persuasão.",
        "blocos": {2: [{"questao": 14, "gabarito": "B"}, {"questao": 15, "gabarito": "D"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L1.2.C",
        "codigo_bncc": "EF07LP07",
        "eixo_saeb": "Identificar elementos constitutivos de textos do domínio jornalístico/midiático.",
        "descricao_bncc": "Identificar, em reportagens, notícias e artigos de opinião, o fato ou temática.",
        "blocos": {2: [{"questao": 17, "gabarito": "B"}, {"questao": 18, "gabarito": "C"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L2.6",
        "codigo_bncc": "EF69LP28",
        "eixo_saeb": "Distinguir fatos de opiniões em textos.",
        "descricao_bncc": "Distinguir, em textos jornalísticos, um fato da opinião relativa a esse fato.",
        "blocos": {2: [{"questao": 19, "gabarito": "A"}, {"questao": 20, "gabarito": "A"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L2.10.A",
        "codigo_bncc": "EF07LP43",
        "eixo_saeb": "Analisar os efeitos de sentido dos mecanismos de construção de textos jornalísticos.",
        "descricao_bncc": "Analisar formas de composição de diferentes gêneros jornalísticos.",
        "blocos": {2: [{"questao": 21, "gabarito": "C"}, {"questao": 22, "gabarito": "B"}]},
    },
    {
        "simulado_num": 6,
        "simulado": "6º Simulado SAEB/2026",
        "codigo_saeb": "9L1.4.C",
        "codigo_bncc": "EF07LP08",
        "eixo_saeb": "Identificar teses/opiniões/posicionamentos explícitos e argumentos em textos.",
        "descricao_bncc": "Identificar, em artigos de opinião e cartas do leitor, teses, opiniões e argumentos.",
        "blocos": {2: [{"questao": 23, "gabarito": "C"}, {"questao": 24, "gabarito": "D"}]},
    },

    # --------------------------------------------------------------------------
    # 7º SIMULADO SAEB/2026 (Blocos 3 e 4 | Q27–Q52)
    # --------------------------------------------------------------------------
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9L2.6",
        "codigo_bncc": "EF69LP28",
        "eixo_saeb": "Distinguir fatos de opiniões em textos.",
        "descricao_bncc": "Distinguir, em textos jornalísticos, um fato da opinião relativa a esse fato.",
        "blocos": {3: [{"questao": 27, "gabarito": "D"}, {"questao": 37, "gabarito": "D"}], 4: [{"questao": 47, "gabarito": "B"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9L1.5.C",
        "codigo_bncc": "EF69LP49",
        "eixo_saeb": "Identificar elementos constitutivos de gêneros de divulgação científica.",
        "descricao_bncc": "Analisar a construção composicional de textos de divulgação científica.",
        "blocos": {3: [{"questao": 30, "gabarito": "C"}], 4: [{"questao": 43, "gabarito": "D"}, {"questao": 44, "gabarito": "D"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9AL1.1.G",
        "codigo_bncc": "EF08LP26",
        "eixo_saeb": "Identificar os recursos de modalização em textos diversos.",
        "descricao_bncc": "Interpretar efeitos de sentido de modificadores do verbo (adjuntos adverbiais).",
        "blocos": {3: [{"questao": 39, "gabarito": "B"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9L2.10.A",
        "codigo_bncc": "EF07LP43",
        "eixo_saeb": "Analisar os efeitos de sentido dos mecanismos de construção de textos jornalísticos.",
        "descricao_bncc": "Analisar formas de composição de diferentes gêneros jornalísticos.",
        "blocos": {3: [{"questao": 29, "gabarito": "B"}], 4: [{"questao": 46, "gabarito": "C"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9L2.7.A",
        "codigo_bncc": "EF69LP08",
        "eixo_saeb": "Inferir, em textos multissemióticos, efeitos de humor, ironia e/ou crítica.",
        "descricao_bncc": "Identificar efeitos de ironia ou humor em textos variados.",
        "blocos": {3: [{"questao": 38, "gabarito": "D"}], 4: [{"questao": 45, "gabarito": "B"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9L1.2.I",
        "codigo_bncc": "EF09LP12",
        "eixo_saeb": "Identificar elementos constitutivos de textos do domínio jornalístico/midiático.",
        "descricao_bncc": "Ler e compreender artigos de opinião, reportagens, notícias, cartas e editoriais.",
        "blocos": {3: [{"questao": 28, "gabarito": "A"}], 4: [{"questao": 48, "gabarito": "D"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9AL2.3.D",
        "codigo_bncc": "EF08LP44",
        "eixo_saeb": "Analisar os mecanismos que contribuem para a progressão textual.",
        "descricao_bncc": "Identificar a função e os sentidos das conjunções subordinativas adverbiais.",
        "blocos": {3: [{"questao": 31, "gabarito": "A"}], 4: [{"questao": 52, "gabarito": "C"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9L2.9.C",
        "codigo_bncc": "EF67LP06",
        "eixo_saeb": "Analisar a relação temática entre diferentes gêneros jornalísticos.",
        "descricao_bncc": "Comparar informações sobre um mesmo fato divulgadas em diferentes veículos e mídias.",
        "blocos": {3: [{"questao": 35, "gabarito": "B"}, {"questao": 36, "gabarito": "C"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9L1.2.H",
        "codigo_bncc": "EF07LP04",
        "eixo_saeb": "Identificar elementos constitutivos de textos do domínio jornalístico/midiático.",
        "descricao_bncc": "Analisar a forma de organização de propagandas de campanhas institucionais.",
        "blocos": {3: [{"questao": 33, "gabarito": "C"}, {"questao": 34, "gabarito": "A"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9AL2.3.B",
        "codigo_bncc": "EF08LP45",
        "eixo_saeb": "Analisar os mecanismos que contribuem para a progressão textual.",
        "descricao_bncc": "Identificar a função e os sentidos das conjunções coordenativas.",
        "blocos": {3: [{"questao": 32, "gabarito": "B"}], 4: [{"questao": 49, "gabarito": "A"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9L1.5.B",
        "codigo_bncc": "EF69LP34",
        "eixo_saeb": "Identificar elementos constitutivos de gêneros de divulgação científica.",
        "descricao_bncc": "Articular linguagem verbal e não verbal na divulgação científica.",
        "blocos": {4: [{"questao": 42, "gabarito": "A"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9L1.5.D",
        "codigo_bncc": "EF69LP50",
        "eixo_saeb": "Identificar elementos constitutivos de gêneros de divulgação científica.",
        "descricao_bncc": "Reconhecer traços da linguagem dos textos de divulgação científica.",
        "blocos": {4: [{"questao": 40, "gabarito": "A"}, {"questao": 41, "gabarito": "C"}]},
    },
    {
        "simulado_num": 7,
        "simulado": "7º Simulado SAEB/2026",
        "codigo_saeb": "9L1.1.C",
        "codigo_bncc": "EF08LP11",
        "eixo_saeb": "Identificar o uso de recursos persuasivos em textos verbais e não verbais.",
        "descricao_bncc": "Identificar e analisar efeitos de sentido de estratégias de persuasão.",
        "blocos": {4: [{"questao": 50, "gabarito": "A"}, {"questao": 51, "gabarito": "B"}]},
    },
]


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


def normalize_saeb_code(text: str) -> str:
    """Corrige falhas comuns de OCR nas tabelas oficiais (ex.: 9L1.2.1 -> 9L1.2.I)."""
    normalized = str(text).strip().upper()
    normalized = re.sub(r"\b9L1\.2\.1\b", "9L1.2.I", normalized)
    normalized = re.sub(r"\b9L1\.3\.1\b", "9L1.3.I", normalized)
    normalized = re.sub(r"\b9L2\.1\.1\b", "9L2.1.I", normalized)
    return normalized


def get_skills_catalog_df() -> pd.DataFrame:
    """Retorna um DataFrame formatado com todas as habilidades do 1º ao 7º Simulado."""
    rows = []
    for item in SAEB_LP_SKILLS:
        blocos_dict = item.get("blocos", {})
        questoes_fmt = []
        blocos_nomes = []

        for b_num in sorted(blocos_dict.keys()):
            q_list = blocos_dict[b_num]
            if q_list:
                blocos_nomes.append(f"Bloco {b_num}")
                q_str = ", ".join(f"Q{q['questao']} ({q['gabarito']})" for q in q_list)
                questoes_fmt.append(f"B{b_num}: {q_str}")

        rows.append({
            "Simulado": item["simulado"],
            "Código SAEB": item["codigo_saeb"],
            "Código BNCC": item["codigo_bncc"],
            "Bloco": " e ".join(blocos_nomes) if blocos_nomes else "—",
            "Questões e Gabaritos": " | ".join(questoes_fmt) if questoes_fmt else "—",
            "Habilidade SAEB": item["eixo_saeb"],
            "Descrição BNCC": item["descricao_bncc"],
        })
    return pd.DataFrame(rows)


def match_column_to_skill(
    col_name: str,
    preferred_simulado_num: int | None = None,
) -> dict | None:
    """
    Identifica a habilidade SAEB/BNCC correspondente a uma coluna do CSV:
      - Código SAEB direto (ex.: 9L2.1.G, 5L1.2, 9L1.2.I / 9L1.2.1)
      - Código BNCC direto (ex.: EF69LP14)
      - Bloco + Questão (ex.: B1_Q12, B3_Q27, BLOCO4_Q40, Q27)
    """
    clean = normalize_saeb_code(col_name)

    # 1. Busca direta por código SAEB ou BNCC (priorizando o simulado atual se houver)
    ordered_skills = sorted(
        SAEB_LP_SKILLS,
        key=lambda s: 0 if s["simulado_num"] == preferred_simulado_num else 1,
    )
    for item in ordered_skills:
        saeb = item["codigo_saeb"].upper()
        bncc = item["codigo_bncc"].upper()
        if re.search(rf"(?:^|[^A-Z0-9]){re.escape(saeb)}(?:[^A-Z0-9]|$)", clean):
            return item
        if bncc != "—" and bncc in clean:
            return item

    # 2. Detecta se o nome da coluna especifica o simulado (ex.: S5_B3_Q27)
    target_sim_num = preferred_simulado_num
    match_sim = re.search(r"(?:S|SIM|SIMULADO)[\s_-]*([1-8])\b", clean)
    if match_sim:
        target_sim_num = int(match_sim.group(1))

    # 3. Busca por Bloco (1 a 4) e Questão (1 a 52)
    match_bq = re.search(
        r"(?:B|BLOCO)[\s_-]*([1-4])[\s_-]*(?:Q|QUESTAO|QUESTÃO)?[\s_-]*(\d{1,2})\b",
        clean,
    )
    if match_bq:
        bloco = int(match_bq.group(1))
        questao = int(match_bq.group(2))
        candidates = (
            [s for s in SAEB_LP_SKILLS if s["simulado_num"] == target_sim_num]
            if target_sim_num
            else SAEB_LP_SKILLS
        )
        for item in candidates:
            for q in item.get("blocos", {}).get(bloco, []):
                if q["questao"] == questao:
                    return item

    # 4. Busca apenas pelo número da questão (ex.: Q27, QUESTAO_40) quando o simulado é conhecido
    match_q = re.search(r"(?:^|[\s_-])(?:Q|QUESTAO|QUESTÃO)[\s_-]*(\d{1,2})\b", clean)
    if match_q and target_sim_num:
        questao = int(match_q.group(1))
        for item in SAEB_LP_SKILLS:
            if item["simulado_num"] == target_sim_num:
                for q_list in item.get("blocos", {}).values():
                    for q in q_list:
                        if q["questao"] == questao:
                            return item

    return None


def classify_proficiency(score_pct: float) -> str:
    """Classifica o percentual de acerto / média pedagógica."""
    if pd.isna(score_pct):
        return "Sem dados"
    if score_pct >= 70:
        return "Adequado (≥ 70%)"
    if score_pct >= 50:
        return "Intermediário (50% - 69%)"
    return "Crítico / Recomposição (< 50%)"


def translate_metrics_dict(metrics: dict) -> dict:
    """Traduz recursivamente as chaves estatísticas de inglês para português."""
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