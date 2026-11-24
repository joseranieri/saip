"""
Módulo de Visualização: Autenticação e Gestão de Senha.

Contém a tela de login centralizada e o formulário de alteração de senha.
"""

from pathlib import Path
import streamlit as st

from src.auth import authenticate, change_password


def render_login_screen(logo_path: Path) -> None:
    """Renderiza a tela inicial de autenticação do sistema SAIP."""
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Colunas para centralização horizontal do card de login
    _, center, _ = st.columns([1, 1.2, 1])

    with center:
        # Centralização da logo dentro do bloco central
        _, logo_center, _ = st.columns([1, 2, 1])

        with logo_center:
            if logo_path.exists():
                st.image(str(logo_path), use_container_width=True)
            else:
                st.markdown(
                    """
                    <div style="text-align:center;">
                        <h1 style="color:#123B66;">SAIP</h1>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown(
            """
            <div style="text-align:center; margin-bottom:25px;">
                <h2 style="color:#123B66; margin-bottom:5px;">
                    Acesso ao sistema
                </h2>
                <p style="color:#52657D; font-size:14px;">
                    Sistema de Análise Estatística e Inteligência Pedagógica
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form"):
            username = st.text_input(
                "Usuário",
                placeholder="Digite seu usuário"
            )
            password = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite sua senha"
            )
            submitted = st.form_submit_button(
                "Entrar",
                use_container_width=True
            )

        if submitted:
            user = authenticate(username, password)

            if user:
                st.session_state.authenticated = True
                st.session_state.username = user["username"]
                st.session_state.must_change_password = bool(
                    user["must_change_password"]
                )
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")


def render_change_password_page() -> None:
    """Renderiza a página para alteração da senha do usuário autenticado."""
    st.title("Alterar senha")

    with st.form("change_password"):
        current = st.text_input("Senha atual", type="password")
        new = st.text_input("Nova senha", type="password")
        confirm = st.text_input(
            "Confirme a nova senha",
            type="password"
        )
        submit = st.form_submit_button("Salvar nova senha")

    if submit:
        if new != confirm:
            st.error("A confirmação da senha está incorreta.")
        elif len(new) < 10:
            st.error("A nova senha deve possuir pelo menos 10 caracteres.")
        elif change_password(st.session_state.username, current, new):
            st.session_state.must_change_password = False
            st.success("Senha alterada com sucesso!")
        else:
            st.error("A senha atual está incorreta.")
