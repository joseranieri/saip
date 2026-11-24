
import csv
import io
import pandas as pd


IDENTIFIER_TERMS = {
    "nome", "nome_completo",
    "cpf", "rg", "matricula", "matrícula",
    "prontuario", "prontuário",
    "cartao_sus", "cartão_sus", "cns",
    "email", "telefone", "celular",
    "endereco", "endereço"
}


def read_csv_safely(uploaded_file):

    raw = uploaded_file.getvalue()

    for encoding in ("utf-8-sig", "utf-8", "latin-1"):

        try:

            text = raw.decode(encoding)

            try:
                dialect = csv.Sniffer().sniff(
                    text[:8192],
                    delimiters=",;\t|"
                )
                separator = dialect.delimiter

            except csv.Error:
                separator = ","

            df = pd.read_csv(
                io.StringIO(text),
                sep=separator
            )

            if df.empty and len(df.columns) == 0:
                raise ValueError("Arquivo sem dados.")

            return df

        except (UnicodeDecodeError, pd.errors.ParserError):
            continue

    raise ValueError(
        "Não foi possível interpretar o arquivo CSV."
    )


def detect_identifier_columns(columns):

    detected = []

    for column in columns:

        name = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        if any(term in name for term in IDENTIFIER_TERMS):
            detected.append(column)

    return detected


def analyze_dataframe(df):

    numeric_df = df.select_dtypes(include="number")

    numeric_metrics = {}

    for column in numeric_df.columns:

        series = numeric_df[column].dropna()

        numeric_metrics[str(column)] = {
            "count": int(series.count()),
            "mean": float(series.mean()) if len(series) else None,
            "median": float(series.median()) if len(series) else None,
            "std": float(series.std()) if len(series) > 1 else None,
            "min": float(series.min()) if len(series) else None,
            "q1": float(series.quantile(0.25)) if len(series) else None,
            "q3": float(series.quantile(0.75)) if len(series) else None,
            "max": float(series.max()) if len(series) else None
        }

    categorical_metrics = {}

    for column in df.columns:

        if column not in numeric_df.columns:

            series = df[column].dropna().astype(str)

            modes = series.mode()

            categorical_metrics[str(column)] = {
                "count": int(series.count()),
                "unique": int(series.nunique()),
                "top": str(modes.iloc[0]) if not modes.empty else None,
                "top_frequency": (
                    int(series.value_counts().iloc[0])
                    if not series.empty else 0
                )
            }

    return {
        "overview": {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "missing_values": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum())
        },
        "numeric": numeric_metrics,
        "categorical": categorical_metrics
    }
