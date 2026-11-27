"""
Módulo de Exportação Executiva em PDF do SAIP.

Gera dois tipos de relatórios PDF:
  1. Relatório Individual Segmentado por Simulado (generate_segmented_pdf_report)
  2. Relatório Geral Consolidado da Evolução Temporal (generate_temporal_general_pdf_report)
"""

from datetime import datetime
from pathlib import Path
import tempfile

from fpdf import FPDF
import pandas as pd
import plotly.express as px
import plotly.io as pio

from src.skills_catalog import DTYPE_LABELS_PT, METRIC_LABELS_PT
from src.ui.components import (
    get_categorical_columns,
    get_numeric_columns,
    sanitize_dataframe_columns,
)

MACRO_EIXOS_GLOSSARY_DF = pd.DataFrame([
    {
        "Macro-Eixo Cognitivo": "1. Compreensao e Localizacao Textual",
        "Prefixos / Codigos SAEB": "5L1.1, 5L1.2, 9L1.2.I, 9L1.2.D, 9L1.3.G, 9L1.3.I",
        "Dominios Cognitivos e Generos Aglomerados": (
            "Localizacao de informacoes explicitas, identificacao da ideia central, tema global "
            "e situacao comunicativa em textos jornalisticos, normativos, legais e reivindicatorios "
            "(carta de reclamacao, noticia, reportagem e estatutos)."
        ),
    },
    {
        "Macro-Eixo Cognitivo": "2. Generos e Estrutura Composicional",
        "Prefixos / Codigos SAEB": "Demais codigos 5L* e 9L* (ex.: 9L1.5.*, 9L2.1.*, 9L2.10.A)",
        "Dominios Cognitivos e Generos Aglomerados": (
            "Analise da organizacao estrutural, suporte e recursos grafico-espaciais ou sonoros "
            "de diferentes generos: narrativo literario (enredo, foco narrativo, conflito, desfecho), "
            "poemas, divulgacao cientifica, texto dramatico e midiatico."
        ),
    },
    {
        "Macro-Eixo Cognitivo": "3. Inferencia, Semantica e Senso Critico",
        "Prefixos / Codigos SAEB": "5L2.6-5L2.8, 5L3.1, 9L2.3, 9L2.6, 9L2.7, 9L2.9, 9L1.1.C, 9L1.4",
        "Dominios Cognitivos e Generos Aglomerados": (
            "Deducao de informacoes implicitas, sentido de palavras/expressoes, distincao entre "
            "fato e opiniao, reconhecimento de ironia/humor, estrategias argumentativas e persuasivas, "
            "e comparacao de confiabilidade entre diferentes midias."
        ),
    },
    {
        "Macro-Eixo Cognitivo": "4. Analise Linguistica e Coesao",
        "Prefixos / Codigos SAEB": "Todos os codigos 5AL* e 9AL* (ex.: 5AL1.5, 9AL1.1.*, 9AL2.*)",
        "Dominios Cognitivos e Generos Aglomerados": (
            "Mecanismos de referenciacao lexical e pronominal, conectivos e conjuncoes de progressao "
            "textual, efeitos de sentido da pontuacao/modalizacao, figuras de linguagem (metafora/comparacao) "
            "e variacao linguistica."
        ),
    },
])


def _safe_text(value: object) -> str:
    """Normaliza texto para compatibilidade segura com fontes padrão Latin-1 do PDF."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "-"
    txt = str(value).strip()
    if txt.lower() in {"", "none", "nan", "nat", "null", "<na>"}:
        return "-"
    replacements = {
        "—": "-",
        "–": "-",
        "≥": ">=",
        "≤": "<=",
        "Δ": "Delta",
        "→": "->",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
    }
    for old, new in replacements.items():
        txt = txt.replace(old, new)
    return txt.encode("latin-1", errors="replace").decode("latin-1")


def _fig_to_png_bytes(fig, width: int = 960, height: int = 440) -> bytes | None:
    """Converte uma figura Plotly em bytes PNG usando Kaleido."""
    try:
        fig.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#172B4D", size=12),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.22,
                xanchor="center",
                x=0.5,
                title_text="",
            ),
            margin=dict(l=35, r=25, t=55, b=105),
        )
        return pio.to_image(fig, format="png", width=width, height=height, scale=2)
    except Exception:
        return None


class SAIPReportPDF(FPDF):
    """Template institucional do relatório pedagógico em PDF do SAIP."""

    def add_macro_eixos_glossary(self, section_number: str) -> None:
        """Renderiza ao final do PDF a tabela metodológica dos 4 Macro-Eixos Cognitivos."""
        self.add_page()
        self.add_section_banner(
            section_number,
            "Nota Metodologica: Aglomeracao dos Macro-Eixos Cognitivos",
            "Correspondencia entre os dominios cognitivos, generos textuais e codigos SAEB (5o e 9o Ano).",
        )

        col_widths = [46.0, 44.0, 96.0]
        headers = list(MACRO_EIXOS_GLOSSARY_DF.columns)

        self.set_fill_color(43, 108, 176)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(203, 215, 229)
        self.set_font("Helvetica", "B", 8)

        self.set_x(12)
        for header_txt, w in zip(headers, col_widths):
            self.cell(w, 7, _safe_text(header_txt), border=1, align="L", fill=True)
        self.ln()

        line_h = 4.6
        for row_idx, (_, row) in enumerate(MACRO_EIXOS_GLOSSARY_DF.iterrows()):
            texts = [_safe_text(row[col]) for col in headers]

            # Calcula a altura necessária da linha conforme a coluna com mais quebras de texto
            max_lines = 1
            for col_i, (txt, w) in enumerate(zip(texts, col_widths)):
                self.set_font("Helvetica", "B" if col_i == 0 else "", 7.5)
                lines = self.multi_cell(w, line_h, txt, dry_run=True, output="LINES")
                max_lines = max(max_lines, len(lines))

            row_h = max_lines * line_h + 3.0
            y_start = self.get_y()

            if row_idx % 2 == 1:
                self.set_fill_color(248, 250, 253)
            else:
                self.set_fill_color(255, 255, 255)

            x_cursor = 12.0
            for col_i, (txt, w) in enumerate(zip(texts, col_widths)):
                self.rect(x_cursor, y_start, w, row_h, style="DF")
                self.set_xy(x_cursor + 1.5, y_start + 1.5)
                if col_i == 0:
                    self.set_font("Helvetica", "B", 7.5)
                    self.set_text_color(18, 59, 102)
                else:
                    self.set_font("Helvetica", "", 7.5)
                    self.set_text_color(23, 43, 77)
                self.multi_cell(w - 3.0, line_h, txt, border=0, align="L")
                x_cursor += w

            self.set_y(y_start + row_h)

        self.ln(4)

    def __init__(self, dataset_name: str, logo_path: Path | None = None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.dataset_name = _safe_text(dataset_name)
        self.logo_path = logo_path
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        # Barra superior em azul institucional mais claro (#2B6CB0)
        self.set_fill_color(43, 108, 176)
        self.rect(0, 0, 210, 20, style="F")

        has_logo = False
        if self.logo_path and self.logo_path.exists():
            try:
                self.image(str(self.logo_path), x=10, y=3.5, h=13)
                has_logo = True
            except Exception:
                has_logo = False

        # Deslocamento horizontal de +40 px (~11 mm) após a área da logo para evitar sobreposição
        text_x = 34 if has_logo else 23

        self.set_xy(text_x, 4.5)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(255, 255, 255)
        self.cell(
            0,
            5.5,
            "SAIP | Sistema de Analise Estatistica e Inteligencia Pedagogica",
            ln=True,
        )
        self.set_x(text_x)
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(235, 244, 255)
        self.cell(0, 4.5, f"Base analisada: {self.dataset_name}", ln=True)
        self.ln(9)

    def footer(self):
        self.set_y(-13)
        self.set_draw_color(203, 215, 229)
        self.line(12, self.get_y(), 198, self.get_y())
        self.set_font("Helvetica", "", 8)
        self.set_text_color(82, 101, 125)
        gerado_em = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(95, 8, f"Relatorio gerado em {gerado_em}", align="L")
        self.cell(91, 8, f"Pagina {self.page_no()}/{{nb}}", align="R")

    def add_section_banner(self, number: str, title: str, subtitle: str = "") -> None:
        if self.get_y() > 235:
            self.add_page()
        self.ln(3)
        self.set_fill_color(245, 248, 252)
        self.set_draw_color(43, 108, 176)
        y_start = self.get_y()
        box_h = 15 if subtitle else 10
        self.rect(12, y_start, 186, box_h, style="F")
        self.set_fill_color(43, 108, 176)
        self.rect(12, y_start, 2.5, box_h, style="F")

        self.set_xy(17, y_start + 2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(18, 59, 102)
        self.cell(0, 5, _safe_text(f"{number}. {title}"), ln=True)

        if subtitle:
            self.set_x(17)
            self.set_font("Helvetica", "", 8.5)
            self.set_text_color(82, 101, 125)
            self.cell(0, 4.5, _safe_text(subtitle), ln=True)

        self.set_y(y_start + box_h + 4)

    def add_kpi_cards(self, kpis: list[tuple[str, str]]) -> None:
        if not kpis:
            return
        if self.get_y() > 250:
            self.add_page()

        cols = min(len(kpis), 4)
        gap = 4
        total_w = 186
        card_w = (total_w - gap * (cols - 1)) / cols
        card_h = 18
        y0 = self.get_y()

        for idx, (label, value) in enumerate(kpis[:4]):
            x0 = 12 + idx * (card_w + gap)
            self.set_fill_color(245, 248, 252)
            self.set_draw_color(220, 230, 241)
            self.rect(x0, y0, card_w, card_h, style="DF")

            self.set_xy(x0 + 3, y0 + 2.5)
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(82, 101, 125)
            self.cell(card_w - 6, 4, _safe_text(label), ln=True)

            self.set_x(x0 + 3)
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(18, 59, 102)
            self.cell(card_w - 6, 7, _safe_text(value), ln=True)

        self.set_y(y0 + card_h + 5)

    def add_styled_table(
        self,
        df: pd.DataFrame,
        col_widths: list[float] | None = None,
        max_rows: int = 40,
    ) -> None:
        if df.empty:
            return

        clean_df = sanitize_dataframe_columns(df).head(max_rows).copy()
        num_cols = len(clean_df.columns)
        if col_widths is None:
            col_widths = [186.0 / num_cols] * num_cols

        if self.get_y() > 255:
            self.add_page()

        self.set_fill_color(43, 108, 176)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(203, 215, 229)
        self.set_font("Helvetica", "B", 8)

        self.set_x(12)
        for col, w in zip(clean_df.columns, col_widths):
            max_chars = max(6, int(w / 2.0))
            header_txt = _safe_text(col)[:max_chars]
            self.cell(w, 7, header_txt, border=1, align="L", fill=True)
        self.ln()

        self.set_font("Helvetica", "", 7.5)
        for row_idx, (_, row) in enumerate(clean_df.iterrows()):
            if self.get_y() > 268:
                self.add_page()
                self.set_fill_color(43, 108, 176)
                self.set_text_color(255, 255, 255)
                self.set_font("Helvetica", "B", 8)
                self.set_x(12)
                for col, w in zip(clean_df.columns, col_widths):
                    max_chars = max(6, int(w / 2.0))
                    self.cell(w, 7, _safe_text(col)[:max_chars], border=1, align="L", fill=True)
                self.ln()
                self.set_font("Helvetica", "", 7.5)

            if row_idx % 2 == 1:
                self.set_fill_color(248, 250, 253)
            else:
                self.set_fill_color(255, 255, 255)

            self.set_text_color(23, 43, 77)
            self.set_x(12)
            for col, w in zip(clean_df.columns, col_widths):
                val = row[col]
                if isinstance(val, float) and pd.notna(val):
                    txt = f"{val:.2f}"
                else:
                    txt = _safe_text(val)
                max_chars = max(6, int(w / 1.9))
                if len(txt) > max_chars:
                    txt = txt[: max_chars - 3] + "..."
                self.cell(w, 6.2, txt, border=1, align="L", fill=True)
            self.ln()

        self.ln(4)

    def add_chart_image(self, png_bytes: bytes | None, img_width: float = 182) -> None:
        if not png_bytes:
            return
        if self.get_y() > 175:
            self.add_page()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(png_bytes)
            tmp_path = Path(tmp.name)

        try:
            x_pos = 12 + (186 - img_width) / 2
            self.image(str(tmp_path), x=x_pos, w=img_width)
            self.ln(4)
        finally:
            tmp_path.unlink(missing_ok=True)


def generate_temporal_general_pdf_report(
    selected_year: int,
    timeline_df: pd.DataFrame,
    macro_df: pd.DataFrame | None = None,
    skills_temp_df: pd.DataFrame | None = None,
    per_simulado_summaries: list[dict] | None = None,
    logo_path: Path | None = None,
) -> bytes:
    """
    Gera o Relatório Geral Consolidado do Ciclo Anual (1º ao 8º Simulado):
      1. Síntese Longitudinal do Ano Letivo (KPIs, Curva Geral e Tabela de Evolução)
      2. Evolução Contínua por Macro-Eixo Cognitivo
      3. Matriz de Pareamento Longitudinal por Código SAEB
      4. Detalhamento Individual por Simulado Importado
    """
    pdf = SAIPReportPDF(
        dataset_name=f"Relatorio Geral Consolidado - Ciclo Anual {selected_year}",
        logo_path=logo_path,
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    # ==========================================================================
    # SEÇÃO 1: SÍNTESE LONGITUDINAL DO CICLO ANUAL
    # ==========================================================================
    pdf.add_section_banner(
        "1",
        f"Sintese Longitudinal dos Simulados ({selected_year})",
        "Consolidacao geral de todas as edicoes aplicadas e importadas no ciclo anual.",
    )

    first_sim = timeline_df.iloc[0]
    last_sim = timeline_df.iloc[-1]
    net_gain = round(
        float(last_sim["Aproveitamento Médio (%)"])
        - float(first_sim["Aproveitamento Médio (%)"]),
        2,
    )

    pdf.add_kpi_cards([
        ("Simulados na Serie", f"{len(timeline_df)} de 8"),
        (f"Base ({first_sim['Simulado']})", f"{first_sim['Aproveitamento Médio (%)']:.1f}%"),
        (f"Ultimo ({last_sim['Simulado']})", f"{last_sim['Aproveitamento Médio (%)']:.1f}%"),
        ("Variacao Acumulada", f"{net_gain:+.1f} p.p."),
    ])

    fig_geral = px.line(
        timeline_df,
        x="Simulado",
        y="Aproveitamento Médio (%)",
        markers=True,
        text="Aproveitamento Médio (%)",
        title=f"Evolucao do Aproveitamento Medio Geral - {selected_year}",
        template="plotly_white",
        color_discrete_sequence=["#2B6CB0"],
        range_y=[0, 100],
    )
    fig_geral.update_traces(textposition="top center", line=dict(width=3))
    pdf.add_chart_image(_fig_to_png_bytes(fig_geral, height=390))

    cols_tl = [
        c
        for c in [
            "Simulado",
            "Registros",
            "Aproveitamento Médio (%)",
            "Variação (Δ p.p.)",
            "Dispersão entre Habilidades (DP)",
        ]
        if c in timeline_df.columns
    ]
    pdf.add_styled_table(timeline_df[cols_tl], col_widths=[36, 30, 42, 36, 42])

    # ==========================================================================
    # SEÇÃO 2: EVOLUÇÃO POR MACRO-EIXO COGNITIVO
    # ==========================================================================
    if macro_df is not None and not macro_df.empty:
        pdf.add_page()
        pdf.add_section_banner(
            "2",
            "Evolucao Continua por Macro-Eixo Cognitivo",
            "Comparabilidade longitudinal nos 4 dominios cognitivos da matriz SAEB/BNCC.",
        )

        simulados_ord = [f"{n}º Simulado" for n in sorted(macro_df["Ordem"].unique())]
        eixos_ord = sorted(macro_df["Macro-Eixo"].unique())
        grade = pd.MultiIndex.from_product(
            [simulados_ord, eixos_ord],
            names=["Simulado", "Macro-Eixo"],
        ).to_frame(index=False)

        macro_plot = grade.merge(
            macro_df[["Simulado", "Macro-Eixo", "Aproveitamento (%)"]],
            on=["Simulado", "Macro-Eixo"],
            how="left",
        )

        fig_macro = px.line(
            macro_plot,
            x="Simulado",
            y="Aproveitamento (%)",
            color="Macro-Eixo",
            markers=True,
            title="Desempenho por Macro-Eixo ao Longo dos Simulados",
            template="plotly_white",
            range_y=[0, 100],
            category_orders={"Simulado": simulados_ord, "Macro-Eixo": eixos_ord},
        )
        fig_macro.update_traces(line=dict(width=2.5), connectgaps=False)
        fig_macro.update_xaxes(type="category")
        pdf.add_chart_image(_fig_to_png_bytes(fig_macro, height=430))

        pivot_macro = (
            macro_df.pivot_table(
                index="Macro-Eixo",
                columns="Simulado",
                values="Aproveitamento (%)",
                aggfunc="mean",
            )
            .reset_index()
        )
        ordered_cols = ["Macro-Eixo"] + [s for s in simulados_ord if s in pivot_macro.columns]
        pdf.add_styled_table(pivot_macro[ordered_cols])

    # ==========================================================================
    # SEÇÃO 3: PAREAMENTO DE HABILIDADES SAEB AO LONGO DO CICLO
    # ==========================================================================
    if skills_temp_df is not None and not skills_temp_df.empty:
        pdf.add_page()
        pdf.add_section_banner(
            "3",
            "Pareamento Longitudinal de Habilidades SAEB",
            "Evolucao do aproveitamento por descritor ao longo das edicoes do ano.",
        )

        simulados_ord = [f"{n}º Simulado" for n in sorted(skills_temp_df["Ordem"].unique())]
        pivot_saeb = (
            skills_temp_df.pivot_table(
                index=["Código SAEB", "Descrição"],
                columns="Simulado",
                values="Aproveitamento (%)",
                aggfunc="mean",
            )
            .reset_index()
        )
        sim_cols = [s for s in simulados_ord if s in pivot_saeb.columns]
        pivot_saeb = pivot_saeb[["Código SAEB", "Descrição"] + sim_cols]

        n_sims = len(sim_cols)
        rem_w = max(84.0, 186.0 - 20.0 - 66.0)
        sim_w = rem_w / max(1, n_sims)
        widths = [20.0, 66.0] + [sim_w] * n_sims
        pdf.add_styled_table(pivot_saeb, col_widths=widths, max_rows=60)

    # ==========================================================================
    # SEÇÃO 4: SÍNTESE INDIVIDUAL POR SIMULADO IMPORTADO
    # ==========================================================================
    if per_simulado_summaries:
        for sim_info in per_simulado_summaries:
            sim_label = sim_info["simulado_label"]
            sim_name = sim_info["name"]
            sum_df = sim_info["summary_df"]
            if sum_df.empty:
                continue

            pdf.add_page()
            pdf.add_section_banner(
                "4",
                f"Detalhamento por Edicao: {sim_label}",
                f"Identificacao: {sim_name} | Registros avaliados: {sim_info['row_count']}",
            )

            best_r = sum_df.loc[sum_df["Aproveitamento (%)"].idxmax()]
            worst_r = sum_df.loc[sum_df["Aproveitamento (%)"].idxmin()]
            pdf.add_kpi_cards([
                ("Indicadores", str(len(sum_df))),
                ("Media da Edicao", f"{sum_df['Aproveitamento (%)'].mean():.1f}%"),
                ("Maior Dominio", f"{best_r['Código SAEB']} ({best_r['Aproveitamento (%)']:.1f}%)"),
                ("Foco Recomposicao", f"{worst_r['Código SAEB']} ({worst_r['Aproveitamento (%)']:.1f}%)"),
            ])

            skill_cols = [
                c
                for c in [
                    "Código SAEB",
                    "Código BNCC",
                    "Descrição da Habilidade",
                    "Aproveitamento (%)",
                    "Mediana",
                    "Nível Pedagógico",
                ]
                if c in sum_df.columns
            ]
            pdf.add_styled_table(
                sum_df[skill_cols],
                col_widths=[22, 22, 68, 24, 18, 32],
                max_rows=55,
            )

    pdf.add_macro_eixos_glossary("5")
    return bytes(pdf.output())


def generate_segmented_pdf_report(
    df: pd.DataFrame,
    metrics: dict,
    dataset_name: str,
    skill_summary_df: pd.DataFrame | None = None,
    temporal_timeline_df: pd.DataFrame | None = None,
    temporal_macro_df: pd.DataFrame | None = None,
    logo_path: Path | None = None,
) -> bytes:
    """
    Constrói o relatório PDF segmentado do simulado ativo na sessão.
    """
    clean_df = sanitize_dataframe_columns(df)
    pdf = SAIPReportPDF(dataset_name=dataset_name, logo_path=logo_path)
    pdf.alias_nb_pages()
    pdf.add_page()

    overview = metrics.get("overview", {})
    total_rows = overview.get("rows", len(clean_df))
    total_cols = overview.get("columns", len(clean_df.columns))
    missing = overview.get("missing_values", int(clean_df.isna().sum().sum()))
    duplicated = overview.get("duplicate_rows", int(clean_df.duplicated().sum()))

    pdf.add_section_banner(
        "1",
        "Visao Geral da Base Analisada",
        "Resumo estrutural, volumetria de registros e integridade inicial.",
    )
    pdf.add_kpi_cards([
        ("Registros Avaliados", f"{total_rows:,}"),
        ("Variaveis Ativas", str(total_cols)),
        ("Valores Ausentes", f"{missing:,}"),
        ("Duplicidades", f"{duplicated:,}"),
    ])

    if temporal_timeline_df is not None and not temporal_timeline_df.empty:
        pdf.add_section_banner(
            "2",
            "Evolucao Temporal dos Simulados (Ciclo Anual)",
            "Progressao longitudinal do aproveitamento medio geral e por Macro-Eixo Cognitivo.",
        )

        first_sim = temporal_timeline_df.iloc[0]
        last_sim = temporal_timeline_df.iloc[-1]
        net_gain = round(
            float(last_sim["Aproveitamento Médio (%)"])
            - float(first_sim["Aproveitamento Médio (%)"]),
            2,
        )
        pdf.add_kpi_cards([
            ("Simulados na Serie", f"{len(temporal_timeline_df)} de 8"),
            ("Base (" + str(first_sim["Simulado"]) + ")", f"{first_sim['Aproveitamento Médio (%)']:.1f}%"),
            ("Ultimo (" + str(last_sim["Simulado"]) + ")", f"{last_sim['Aproveitamento Médio (%)']:.1f}%"),
            ("Variacao Acumulada", f"{net_gain:+.1f} p.p."),
        ])

        fig_geral = px.line(
            temporal_timeline_df,
            x="Simulado",
            y="Aproveitamento Médio (%)",
            markers=True,
            text="Aproveitamento Médio (%)",
            title="Evolucao do Aproveitamento Medio Geral (%)",
            template="plotly_white",
            color_discrete_sequence=["#2B6CB0"],
            range_y=[0, 100],
        )
        fig_geral.update_traces(textposition="top center", line=dict(width=3))
        pdf.add_chart_image(_fig_to_png_bytes(fig_geral, height=390))

        cols_tl = [
            c
            for c in [
                "Simulado",
                "Registros",
                "Aproveitamento Médio (%)",
                "Variação (Δ p.p.)",
                "Dispersão entre Habilidades (DP)",
            ]
            if c in temporal_timeline_df.columns
        ]
        pdf.add_styled_table(temporal_timeline_df[cols_tl])

        if temporal_macro_df is not None and not temporal_macro_df.empty:
            fig_macro = px.line(
                temporal_macro_df,
                x="Simulado",
                y="Aproveitamento (%)",
                color="Macro-Eixo",
                markers=True,
                title="Desempenho por Macro-Eixo Cognitivo ao Longo dos Simulados",
                template="plotly_white",
                range_y=[0, 100],
            )
            fig_macro.update_traces(line=dict(width=2.5))
            pdf.add_chart_image(_fig_to_png_bytes(fig_macro, height=430))

    if skill_summary_df is not None and not skill_summary_df.empty:
        pdf.add_page()
        pdf.add_section_banner(
            "3",
            "Analise Pedagogica por Habilidades (SAEB / BNCC)",
            "Aproveitamento por descritor, classificacao de proficiencia e focos de recomposicao.",
        )

        mapped_count = int((skill_summary_df["Código SAEB"] != "Não mapeado").sum())
        worst_row = skill_summary_df.loc[skill_summary_df["Aproveitamento (%)"].idxmin()]

        pdf.add_kpi_cards([
            ("Indicadores Avaliados", str(len(skill_summary_df))),
            ("Habilidades SAEB", str(mapped_count)),
            ("Media Geral", f"{skill_summary_df['Aproveitamento (%)'].mean():.1f}%"),
            ("Menor Aproveitamento", f"{worst_row['Código SAEB']} ({worst_row['Aproveitamento (%)']:.1f}%)"),
        ])

        plot_skills = skill_summary_df.sort_values("Aproveitamento (%)", ascending=True).copy()
        plot_skills["Rotulo"] = plot_skills.apply(
            lambda r: (
                f"{r['Código SAEB']} ({r['Coluna no Arquivo']})"
                if r["Código SAEB"] != "Não mapeado"
                else str(r["Coluna no Arquivo"])
            ),
            axis=1,
        )
        color_map = {
            "Adequado (≥ 70%)": "#2F855A",
            "Intermediário (50% - 69%)": "#D69E2E",
            "Crítico / Recomposição (< 50%)": "#C53030",
            "Sem dados": "#718096",
        }
        fig_skills = px.bar(
            plot_skills,
            x="Aproveitamento (%)",
            y="Rotulo",
            color="Nível Pedagógico",
            orientation="h",
            title="Desempenho por Habilidade / Indicador (%)",
            template="plotly_white",
            color_discrete_map=color_map,
            range_x=[0, 100],
        )
        fig_skills.update_layout(yaxis_title="", xaxis_title="Aproveitamento (%)")
        chart_h = max(400, min(680, len(plot_skills) * 32))
        pdf.add_chart_image(_fig_to_png_bytes(fig_skills, height=chart_h))

        skill_cols = [
            c
            for c in [
                "Código SAEB",
                "Código BNCC",
                "Descrição da Habilidade",
                "Aproveitamento (%)",
                "Mediana",
                "Nível Pedagógico",
            ]
            if c in skill_summary_df.columns
        ]
        pdf.add_styled_table(
            skill_summary_df[skill_cols],
            col_widths=[22, 22, 68, 24, 18, 32],
            max_rows=50,
        )

    numeric_metrics = metrics.get("numeric", {})
    if numeric_metrics:
        pdf.add_page()
        pdf.add_section_banner(
            "4",
            "Estatisticas Descritivas das Variaveis Numericas",
            "Medidas de tendencia central, dispersao e distribuicao dos escores.",
        )

        num_table = pd.DataFrame(numeric_metrics).T.rename(
            columns=lambda col: METRIC_LABELS_PT.get(str(col).strip().lower(), col)
        ).reset_index(names="Variável")
        pdf.add_styled_table(num_table, max_rows=40)

        first_num_col = list(numeric_metrics.keys())[0]
        if first_num_col in clean_df.columns:
            fig_hist = px.histogram(
                clean_df,
                x=first_num_col,
                marginal="box",
                title=f"Distribuicao de Frequencia: {first_num_col}",
                template="plotly_white",
                color_discrete_sequence=["#2B6CB0"],
            )
            pdf.add_chart_image(_fig_to_png_bytes(fig_hist, height=380))

    cat_cols = [
        c for c in get_categorical_columns(clean_df)
        if c not in {"Simulado", "Ano_Letivo"}
    ]
    if cat_cols:
        pdf.add_section_banner(
            "5",
            "Distribuicao de Variaveis Categoricas",
            "Frequencia absoluta das principais categorias identificadas na base.",
        )
        target_cat = cat_cols[0]
        freq_df = (
            clean_df[target_cat]
            .fillna("(Ausente)")
            .astype(str)
            .value_counts()
            .head(15)
            .rename_axis("Categoria")
            .reset_index(name="Frequência")
        )
        pdf.add_styled_table(freq_df, col_widths=[130, 56], max_rows=15)

        fig_cat = px.bar(
            freq_df,
            x="Categoria",
            y="Frequência",
            title=f"Frequencia por Categoria: {target_cat}",
            template="plotly_white",
            color_discrete_sequence=["#2B6CB0"],
        )
        pdf.add_chart_image(_fig_to_png_bytes(fig_cat, height=370))

    num_cols = [
        c for c in get_numeric_columns(clean_df)
        if c not in {"Ordem_Simulado", "Ano_Letivo"}
    ]
    if cat_cols and num_cols:
        pdf.add_page()
        group_col = cat_cols[0]
        val_col = num_cols[0]
        pdf.add_section_banner(
            "6",
            f"Analise Comparativa por Grupos ({group_col})",
            f"Desempenho medio e dispersao do indicador '{val_col}' por agrupamento.",
        )

        grouped = (
            clean_df.groupby(group_col, dropna=False)[val_col]
            .agg(
                Quantidade="count",
                Média="mean",
                Mediana="median",
                **{"Desvio padrão": "std"},
                Mínimo="min",
                Máximo="max",
            )
            .reset_index()
            .rename(columns={group_col: "Grupo"})
        )
        pdf.add_styled_table(grouped, max_rows=25)

        fig_grp = px.bar(
            grouped.head(20),
            x="Grupo",
            y="Média",
            title=f"Media de {val_col} por {group_col}",
            template="plotly_white",
            color_discrete_sequence=["#2B6CB0"],
        )
        pdf.add_chart_image(_fig_to_png_bytes(fig_grp, height=380))

    pdf.add_section_banner(
        "7",
        "Diagnostico de Qualidade e Completude dos Dados",
        "Tipagem de variaveis, valores distintos e percentual de preenchimento.",
    )
    quality_df = pd.DataFrame({
        "Coluna": list(clean_df.columns),
        "Tipo de dado": [
            DTYPE_LABELS_PT.get(str(clean_df[col].dtype), str(clean_df[col].dtype))
            for col in clean_df.columns
        ],
        "Valores ausentes": [int(clean_df[col].isna().sum()) for col in clean_df.columns],
        "Valores distintos": [int(clean_df[col].nunique(dropna=True)) for col in clean_df.columns],
        "Completude (%)": [round(clean_df[col].notna().mean() * 100, 2) for col in clean_df.columns],
    })
    pdf.add_styled_table(quality_df, col_widths=[56, 36, 32, 32, 30], max_rows=45)

    fig_qual = px.bar(
        quality_df.head(25),
        x="Coluna",
        y="Completude (%)",
        title="Completude por Variavel (%)",
        range_y=[0, 100],
        template="plotly_white",
        color_discrete_sequence=["#2B6CB0"],
    )
    pdf.add_chart_image(_fig_to_png_bytes(fig_qual, height=360))

    pdf.add_macro_eixos_glossary("8")
    return bytes(pdf.output())