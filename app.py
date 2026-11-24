"""
SAIP — Sistema de Análise Estatística e Inteligência Pedagógica.

Arquivo principal (ponto de entrada) da aplicação Streamlit.
Responsável apenas pela configuração inicial da página, aplicação da identidade
visual, controle de sessão/autenticação e roteamento entre as telas.
"""

from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

from src.auth import ensure_default_user
from src.database import init_db
from src.ui.styles import apply_custom_styles, show_logo
from src.ui.views.dashboard import render_dashboard_page
from src.ui.views.history import render_history_page
from src.ui.views.login import render_change_password_page, render_login_screen


# ==============================================================================
# 1. CONFIGURAÇÕES INICIAIS E BANCO DE DADOS
# ==============================================================================

load_dotenv()

st.set_page_config(
    page_title="SAIP | Inteligência Pedagógica",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

# Inicializa as tabelas do SQLite e garante a existência do usuário padrão
init_db()
ensure_default_user()

# Aplica o CSS customizado da identidade visual do SAIP
apply_custom_styles()


# ==============================================================================
# 2. CONTROLE DE AUTENTICAÇÃO
# ==============================================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    render_login_screen(LOGO_PATH)
    st.stop()


# ==============================================================================
# 3. MENU LATERAL (SIDEBAR) E NAVEGAÇÃO
# ==============================================================================

with st.sidebar:
    show_logo(LOGO_PATH, width=190)
    st.divider()

    st.caption("SESSÃO ATUAL")
    st.write(f"**{st.session_state.username}**")

    page = st.radio(
        "Navegação",
        [
            "Dashboard",
            "Histórico de importações",
            "Alterar senha"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    if st.button("Sair", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Obriga a troca da senha inicial antes de liberar o acesso às demais telas
if (
    st.session_state.get("must_change_password")
    and page != "Alterar senha"
):
    st.warning("Altere sua senha inicial antes de continuar.")
    st.stop()


# ==============================================================================
# 4. ROTEAMENTO DAS PÁGINAS
# ==============================================================================

if page == "Alterar senha":
    render_change_password_page()

elif page == "Dashboard":
    render_dashboard_page(LOGO_PATH)

elif page == "Histórico de importações":
    render_history_page()
