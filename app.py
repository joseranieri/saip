"""
SAIP — Sistema de Análise Estatística e Inteligência Pedagógica.

Ponto de entrada da aplicação Streamlit com menu lateral segmentado:
Dashboard, Carga de Dados, Histórico de Importações, Alterar Senha,
Resetar Senha e Sair.
"""

from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

from src.auth import ensure_default_user
from src.database import init_db
from src.ui.styles import apply_custom_styles, show_logo
from src.ui.views.dashboard import (
    render_dashboard_page,
    render_upload_page,
)
from src.ui.views.history import render_history_page
from src.ui.views.login import (
    render_change_password_page,
    render_login_screen,
    render_reset_password_page,
)


# ==============================================================================
# 1. CONFIGURAÇÕES INICIAIS E BANCO DE DADOS
# ==============================================================================

load_dotenv()

st.set_page_config(
    page_title="SAIP | Inteligência Pedagógica",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"
LOGOW_PATH = BASE_DIR / "assets" / "logoBranca.png"

init_db()
ensure_default_user()
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
            "Carga de Dados",
            "Histórico de Importações",
            "Alterar Senha",
            "Resetar Senha",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    if st.button("Sair", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Obriga a troca da senha inicial antes de liberar o acesso às demais telas
if (
    st.session_state.get("must_change_password")
    and page not in ("Alterar Senha", "Resetar Senha")
):
    st.warning("Altere sua senha inicial antes de continuar.")
    st.stop()


# ==============================================================================
# 4. ROTEAMENTO DAS PÁGINAS
# ==============================================================================

if page == "Dashboard":
    render_dashboard_page(LOGO_PATH)

elif page == "Carga de Dados":
    render_upload_page(LOGO_PATH)

elif page == "Histórico de Importações":
    render_history_page()

elif page == "Alterar Senha":
    render_change_password_page()

elif page == "Resetar Senha":
    render_reset_password_page()