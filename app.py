
import streamlit as st
import pandas as pd
import plotly.express as px

from dotenv import load_dotenv

from src.database import (
    init_db,
    save_dataset,
    list_datasets,
    get_dataset
)

from src.auth import (
    authenticate,
    ensure_default_user,
    change_password
)

from src.analyzer import (
    analyze_dataframe,
    read_csv_safely,
    detect_identifier_columns
)


# --------------------------------------------------
# CONFIGURAÇÕES INICIAIS
# --------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="SAIP | Análise Pedagógica",
    page_icon="📊",
    layout="wide"
)

init_db()
ensure_default_user()


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

def login_screen():

    st.title("SAIP")

    st.subheader(
        "Sistema de Análise Estatística e Inteligência Pedagógica"
    )

    with st.form("login_form"):

        username = st.text_input("Usuário")
        password = st.text_input(
            "Senha",
            type="password"
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


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


if not st.session_state.authenticated:

    login_screen()
    st.stop()


# --------------------------------------------------
# MENU LATERAL
# --------------------------------------------------

with st.sidebar:

    st.title("SAIP")

    st.write(
        f"Usuário: **{st.session_state.username}**"
    )

    page = st.radio(
        "Navegação",
        [
            "Dashboard",
            "Histórico de importações",
            "Alterar senha"
        ]
    )

    if st.button("Sair", use_container_width=True):

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()


# Exige troca da senha inicial

if (
    st.session_state.get("must_change_password")
    and page != "Alterar senha"
):

    st.warning(
        "Altere sua senha inicial antes de continuar."
    )

    st.stop()


# --------------------------------------------------
# ALTERAÇÃO DE SENHA
# --------------------------------------------------

if page == "Alterar senha":

    st.header("Alterar senha")

    with st.form("change_password"):

        current = st.text_input(
            "Senha atual",
            type="password"
        )

        new = st.text_input(
            "Nova senha",
            type="password"
        )

        confirm = st.text_input(
            "Confirme a nova senha",
            type="password"
        )

        submit = st.form_submit_button("Salvar nova senha")

    if submit:

        if new != confirm:

            st.error("A confirmação da senha está incorreta.")

        elif len(new) < 10:

            st.error(
                "A nova senha deve possuir pelo menos 10 caracteres."
            )

        elif change_password(
            st.session_state.username,
            current,
            new
        ):

            st.session_state.must_change_password = False

            st.success("Senha alterada com sucesso!")

        else:

            st.error("A senha atual está incorreta.")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

elif page == "Dashboard":

    st.title("Dashboard de análise")

    st.write(
        "Importe um arquivo CSV para realizar a análise "
        "estatística dos dados."
    )

    uploaded = st.file_uploader(
        "Selecione o arquivo CSV",
        type=["csv"]
    )

    if uploaded is not None:

        try:

            df = read_csv_safely(uploaded)

            st.success(
                f"Arquivo lido: {len(df):,} registros "
                f"e {len(df.columns)} colunas."
            )

            st.subheader("Pré-visualização dos dados")

            st.dataframe(
                df.head(20),
                use_container_width=True
            )

            # Identificação preliminar de campos pessoais

            suggested = detect_identifier_columns(
                df.columns
            )

            excluded = st.multiselect(
                "Colunas que não devem participar da análise "
                "nem ser armazenadas",
                options=list(df.columns),
                default=suggested
            )

            persist = st.checkbox(
                "Importar os dados processados para a base local"
            )

            dataset_name = st.text_input(
                "Nome da importação",
                value=uploaded.name.rsplit(".", 1)[0]
            )

            if st.button(
                "Processar CSV",
                type="primary",
                use_container_width=True
            ):

                analysis_df = df.drop(
                    columns=excluded,
                    errors="ignore"
                )

                if analysis_df.empty:

                    st.error(
                        "Não existem colunas disponíveis para análise."
                    )

                else:

                    metrics = analyze_dataframe(analysis_df)

                    # Mantém os resultados disponíveis na sessão

                    st.session_state.current_df = analysis_df
                    st.session_state.current_metrics = metrics
                    st.session_state.current_name = dataset_name

                    # Persistência opcional

                    if persist:

                        records = (
                            analysis_df
                            .astype(object)
                            .where(pd.notna(analysis_df), None)
                            .to_dict(orient="records")
                        )

                        save_dataset(
                            name=dataset_name,
                            original_filename=uploaded.name,
                            row_count=len(analysis_df),
                            column_names=list(analysis_df.columns),
                            records=records,
                            metrics=metrics,
                            username=st.session_state.username
                        )

                        st.success(
                            "Dados processados e importados "
                            "para o banco local."
                        )

                    else:

                        st.success(
                            "Análise concluída. Os dados não "
                            "foram persistidos no banco."
                        )

        except Exception as exc:

            st.error(
                f"Erro ao processar o arquivo: {exc}"
            )


    # --------------------------------------------------
    # RESULTADOS DA ANÁLISE
    # --------------------------------------------------

    if (
        "current_df" in st.session_state
        and "current_metrics" in st.session_state
    ):

        df = st.session_state.current_df
        metrics = st.session_state.current_metrics

        st.divider()

        st.header(
            f"Resultados: {st.session_state.current_name}"
        )

        overview = metrics["overview"]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Registros",
            f"{overview['rows']:,}"
        )

        c2.metric(
            "Variáveis",
            overview["columns"]
        )

        c3.metric(
            "Valores ausentes",
            f"{overview['missing_values']:,}"
        )

        c4.metric(
            "Registros duplicados",
            f"{overview['duplicate_rows']:,}"
        )

        # Estatísticas numéricas

        st.subheader("Estatísticas descritivas")

        numeric = metrics["numeric"]

        if numeric:

            numeric_table = pd.DataFrame(numeric).T

            st.dataframe(
                numeric_table,
                use_container_width=True
            )

            selected_numeric = st.selectbox(
                "Selecione uma variável numérica",
                list(numeric.keys())
            )

            fig = px.histogram(
                df,
                x=selected_numeric,
                title=f"Distribuição de {selected_numeric}",
                marginal="box"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Não foram encontradas variáveis numéricas."
            )

        # Estatísticas categóricas

        st.subheader("Análise das variáveis categóricas")

        categorical = metrics["categorical"]

        if categorical:

            selected_cat = st.selectbox(
                "Selecione uma variável categórica",
                list(categorical.keys())
            )

            frequency = (
                df[selected_cat]
                .fillna("(Ausente)")
                .astype(str)
                .value_counts()
                .head(15)
                .rename_axis("Categoria")
                .reset_index(name="Frequência")
            )

            st.dataframe(
                frequency,
                use_container_width=True
            )

            fig = px.bar(
                frequency,
                x="Categoria",
                y="Frequência",
                title=f"Frequência de {selected_cat}"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Não foram encontradas variáveis categóricas."
            )

        # Qualidade dos dados

        st.subheader("Qualidade dos dados")

        quality = pd.DataFrame({
            "Coluna": list(df.columns),

            "Tipo": [
                str(df[column].dtype)
                for column in df.columns
            ],

            "Valores ausentes": [
                int(df[column].isna().sum())
                for column in df.columns
            ],

            "Valores distintos": [
                int(df[column].nunique(dropna=True))
                for column in df.columns
            ]
        })

        st.dataframe(
            quality,
            use_container_width=True
        )


# --------------------------------------------------
# HISTÓRICO DE IMPORTAÇÕES
# --------------------------------------------------

elif page == "Histórico de importações":

    st.title("Histórico de importações")

    items = list_datasets()

    if not items:

        st.info(
            "Ainda não existem conjuntos de dados importados."
        )

    else:

        history = pd.DataFrame(items)

        st.dataframe(
            history[
                [
                    "id",
                    "name",
                    "original_filename",
                    "row_count",
                    "created_at",
                    "created_by"
                ]
            ],
            use_container_width=True
        )

        selected_id = st.selectbox(
            "Selecione uma importação",
            options=[item["id"] for item in items],
            format_func=lambda value: next(
                f"#{item['id']} — {item['name']}"
                for item in items
                if item["id"] == value
            )
        )

        if st.button("Carregar análise salva"):

            item = get_dataset(selected_id)

            if item:

                st.session_state.current_df = pd.DataFrame(
                    item["records"]
                )

                st.session_state.current_metrics = item["metrics"]

                st.session_state.current_name = item["name"]

                st.success(
                    "Dados carregados. Acesse o Dashboard "
                    "para visualizar os resultados."
                )
