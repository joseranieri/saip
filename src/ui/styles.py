"""
Módulo de Identidade Visual e Estilos (CSS) do SAIP.

Centraliza toda a estilização customizada para manter o layout claro,
padronizar os componentes do BaseWeb/Streamlit (inputs, botões, abas,
cards, uploaders) e exibir a identidade visual do sistema.
"""

from pathlib import Path
import streamlit as st


def apply_custom_styles() -> None:
    """
    Injeta o CSS customizado na página do Streamlit, forçando o esquema de
    cores claro (light mode) e aplicando a paleta institucional do SAIP.
    """
    st.markdown("""
    <style>
        /* =====================================
           CORES GERAIS E FORÇAR MODO CLARO
        ===================================== */

        :root {
            color-scheme: light !important;
            --saip-primary: #123B66;
            --saip-primary-hover: #1D568C;
            --saip-text: #172B4D;
            --saip-muted: #52657D;
            --saip-border: #CBD7E5;
            --saip-background: #FFFFFF;
            --saip-surface: #F5F8FC;
            --saip-input-background: #FFFFFF;
        }

        html, body, .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stHeader"] {
            background-color: var(--saip-background) !important;
            color: var(--saip-text) !important;
            color-scheme: light !important;
        }

        [data-testid="stHeader"] button,
        [data-testid="stHeader"] svg {
            color: var(--saip-text) !important;
            fill: var(--saip-text) !important;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        /* =====================================
           TÍTULOS E TEXTOS
        ===================================== */

        h1, h2, h3, h4, h5, h6 {
            color: var(--saip-primary) !important;
            font-weight: 700 !important;
        }

        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] span {
            color: var(--saip-text) !important;
        }

        [data-testid="stCaptionContainer"] p,
        [data-testid="stCaptionContainer"] {
            color: var(--saip-muted) !important;
        }

        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] span {
            color: var(--saip-text) !important;
            font-weight: 600 !important;
        }

        /* =====================================
           INPUTS DE TEXTO, SENHA E TEXTAREA
        ===================================== */

        [data-baseweb="input"],
        [data-baseweb="base-input"],
        [data-baseweb="textarea"],
        div[data-testid="stTextInput"] > div > div,
        div[data-testid="stNumberInput"] > div > div,
        div[data-testid="stTextArea"] > div > div {
            background-color: var(--saip-input-background) !important;
            border-color: var(--saip-border) !important;
            color: var(--saip-text) !important;
        }

        [data-baseweb="input"],
        [data-baseweb="textarea"] {
            border: 1px solid var(--saip-border) !important;
            border-radius: 8px !important;
            overflow: hidden;
        }

        [data-baseweb="input"]:focus-within,
        [data-baseweb="textarea"]:focus-within {
            border-color: var(--saip-primary) !important;
            box-shadow: 0 0 0 1px var(--saip-primary) !important;
        }

        input,
        textarea,
        [data-baseweb="input"] input,
        [data-baseweb="base-input"] input,
        [data-baseweb="textarea"] textarea {
            color: #172B4D !important;
            background-color: #FFFFFF !important;
            -webkit-text-fill-color: #172B4D !important;
            caret-color: #123B66 !important;
            font-weight: 500 !important;
        }

        input:-webkit-autofill,
        input:-webkit-autofill:hover,
        input:-webkit-autofill:focus {
            -webkit-box-shadow: 0 0 0px 1000px #FFFFFF inset !important;
            -webkit-text-fill-color: #172B4D !important;
            transition: background-color 5000s ease-in-out 0s;
        }

        input::placeholder,
        textarea::placeholder,
        [data-baseweb="input"] input::placeholder,
        [data-baseweb="textarea"] textarea::placeholder {
            color: #718096 !important;
            -webkit-text-fill-color: #718096 !important;
            opacity: 1 !important;
        }

        [data-baseweb="input"] button,
        [data-baseweb="base-input"] button {
            background-color: transparent !important;
            color: #52657D !important;
        }

        [data-baseweb="input"] svg,
        [data-baseweb="base-input"] svg,
        [data-baseweb="select"] svg {
            fill: #52657D !important;
            color: #52657D !important;
        }

        /* =====================================
           SELECT E MULTISELECT
        ===================================== */

        [data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            border: 1px solid var(--saip-border) !important;
            border-radius: 8px !important;
            color: #172B4D !important;
        }

        [data-baseweb="select"] > div:focus-within {
            border-color: var(--saip-primary) !important;
            box-shadow: 0 0 0 1px var(--saip-primary) !important;
        }

        [data-baseweb="select"] span,
        [data-baseweb="select"] div,
        [data-baseweb="select"] input {
            color: #172B4D !important;
            -webkit-text-fill-color: #172B4D !important;
        }

        [data-baseweb="tag"] {
            background-color: #EAF1F8 !important;
            border: 1px solid #B8CCE0 !important;
            border-radius: 6px !important;
        }

        [data-baseweb="tag"] span {
            color: #123B66 !important;
            -webkit-text-fill-color: #123B66 !important;
            font-weight: 600 !important;
        }

        [data-baseweb="tag"] svg {
            fill: #123B66 !important;
            color: #123B66 !important;
        }

        [data-baseweb="popover"],
        [data-baseweb="popover"] > div,
        ul[role="listbox"],
        [role="listbox"] {
            background-color: #FFFFFF !important;
            border: 1px solid var(--saip-border) !important;
            color: #172B4D !important;
        }

        [role="option"],
        li[role="option"] {
            background-color: #FFFFFF !important;
            color: #172B4D !important;
        }

        [role="option"]:hover,
        [role="option"][aria-selected="true"] {
            background-color: #EAF1F8 !important;
            color: #123B66 !important;
        }

        /* =====================================
           FORMULÁRIOS E EXPANDERS
        ===================================== */

        [data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E1E8F0 !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
        }

        [data-testid="stExpander"] {
            background-color: #FFFFFF !important;
            border: 1px solid #DCE6F1 !important;
            border-radius: 10px !important;
        }

        [data-testid="stExpander"] summary {
            background-color: #F5F8FC !important;
            color: #123B66 !important;
            font-weight: 600 !important;
            border-radius: 9px !important;
        }

        [data-testid="stExpander"] summary span,
        [data-testid="stExpander"] summary p,
        [data-testid="stExpander"] summary svg {
            color: #123B66 !important;
            fill: #123B66 !important;
        }

        /* =====================================
           BOTÕES
        ===================================== */

        .stButton > button,
        .stFormSubmitButton > button,
        .stDownloadButton > button {
            background-color: #123B66 !important;
            color: #FFFFFF !important;
            border: 1px solid #123B66 !important;
            border-radius: 8px !important;
            min-height: 42px;
            font-weight: 600 !important;
        }

        .stButton > button *,
        .stFormSubmitButton > button *,
        .stDownloadButton > button * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover,
        .stDownloadButton > button:hover {
            background-color: #1D568C !important;
            border-color: #1D568C !important;
        }

        .stButton > button:focus,
        .stFormSubmitButton > button:focus,
        .stDownloadButton > button:focus {
            box-shadow: 0 0 0 3px rgba(18, 59, 102, 0.25) !important;
        }

        /* =====================================
           CHECKBOX E RADIO
        ===================================== */

        [data-testid="stCheckbox"] label,
        [data-testid="stRadio"] label,
        [data-testid="stCheckbox"] p,
        [data-testid="stRadio"] p,
        [data-testid="stCheckbox"] span,
        [data-testid="stRadio"] span {
            color: #172B4D !important;
        }

        /* =====================================
           SIDEBAR
        ===================================== */

        [data-testid="stSidebar"] {
            background-color: #F5F8FC !important;
            border-right: 1px solid #E1E8F0 !important;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div {
            color: #172B4D;
        }

        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] .stButton > button * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }

        /* =====================================
           MÉTRICAS
        ===================================== */

        [data-testid="stMetric"] {
            background-color: #F5F8FC !important;
            border: 1px solid #DCE6F1 !important;
            border-radius: 12px;
            padding: 16px;
        }

        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] * {
            color: #52657D !important;
        }

        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] * {
            color: #123B66 !important;
            font-weight: 700 !important;
        }

        /* =====================================
           ABAS
        ===================================== */

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid #DCE6F1;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            color: #34445B !important;
            font-weight: 600 !important;
        }

        .stTabs [data-baseweb="tab"] p {
            color: inherit !important;
        }

        .stTabs [aria-selected="true"] {
            color: #123B66 !important;
            border-bottom-color: #123B66 !important;
        }

        /* =====================================
           UPLOAD DE ARQUIVOS
        ===================================== */

        [data-testid="stFileUploader"] section {
            background-color: #F8FAFD !important;
            border: 1px dashed #A9BDD2 !important;
            border-radius: 10px !important;
            padding: 12px !important;
        }

        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] p {
            color: #172B4D !important;
        }

        [data-testid="stFileUploader"] button {
            background-color: #FFFFFF !important;
            color: #123B66 !important;
            border: 1px solid #123B66 !important;
            font-weight: 600 !important;
        }

        [data-testid="stFileUploader"] button * {
            color: #123B66 !important;
            -webkit-text-fill-color: #123B66 !important;
        }

        /* =====================================
           ALERTAS E CARDS PEDAGÓGICOS
        ===================================== */

        [data-testid="stAlert"] {
            border-radius: 8px !important;
        }

        [data-testid="stAlert"] p {
            color: #172B4D !important;
        }

        .skill-card {
            background-color: #F5F8FC;
            border: 1px solid #DCE6F1;
            border-left: 5px solid #123B66;
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
        }

        .skill-card-warning {
            border-left-color: #C53030;
            background-color: #FFF5F5;
        }

        .skill-card-success {
            border-left-color: #2F855A;
            background-color: #F0FFF4;
        }

        /* =====================================
           TABELAS E DIVISORES
        ===================================== */

        [data-testid="stDataFrame"] {
            border: 1px solid #E1E8F0;
            border-radius: 8px;
        }

        hr {
            border-color: #E1E8F0 !important;
        }

        /* =====================================
           RESPONSIVIDADE
        ===================================== */

        @media (max-width: 768px) {
            .block-container {
                padding: 1rem 0.8rem 2rem 0.8rem;
            }

            h1 {
                font-size: 1.6rem !important;
            }

            h2 {
                font-size: 1.3rem !important;
            }

            [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap;
                gap: 0.7rem;
            }

            [data-testid="stHorizontalBlock"] > [data-testid="column"] {
                min-width: 45% !important;
                flex: 1 1 45% !important;
            }

            [data-testid="stMetric"] {
                padding: 10px;
            }

            .stTabs [data-baseweb="tab-list"] {
                overflow-x: auto;
                flex-wrap: nowrap;
            }

            .stTabs [data-baseweb="tab"] {
                white-space: nowrap;
                padding: 10px;
            }
        }

        @media (max-width: 480px) {
            [data-testid="stHorizontalBlock"] > [data-testid="column"] {
                min-width: 100% !important;
                flex: 1 1 100% !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def show_logo(logo_path: Path, width: int = 220) -> None:
    """
    Exibe a imagem da logo caso o arquivo exista em 'assets/logo.png'
    ou renderiza um cabeçalho textual institucional como alternativa.
    """
    if logo_path.exists():
        st.image(str(logo_path), width=width)
    else:
        st.markdown(
            "<h2 style='color:#123B66; margin-bottom:0;'>SAIP</h2>"
            "<p style='color:#52657D; margin-top:2px;'>Inteligência Pedagógica</p>",
            unsafe_allow_html=True
        )
