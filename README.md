# SAIP — Sistema de Análise Estatística e Inteligência Pedagógica

O **SAIP** é um sistema desenvolvido em Python para importação, processamento e análise estatística de dados, com foco na interpretação de indicadores educacionais e pedagógicos.

A aplicação utiliza Streamlit para disponibilizar uma interface web interativa, Pandas para manipulação dos dados, Plotly para visualizações gráficas e SQLite para armazenamento local das informações.

## 1. Objetivos do projeto

O sistema tem como objetivos:

- Permitir a importação de conjuntos de dados no formato CSV.
- Realizar análises estatísticas descritivas.
- Identificar valores ausentes e registros duplicados.
- Analisar variáveis numéricas e categóricas.
- Apresentar indicadores e visualizações gráficas.
- Permitir o armazenamento opcional dos dados processados.
- Manter um histórico das importações realizadas.
- Disponibilizar autenticação e gerenciamento de senhas.

## 2. Tecnologias utilizadas

| Tecnologia     | Finalidade                             |
| -------------- | -------------------------------------- |
| Python         | Linguagem principal                    |
| Streamlit      | Interface web                          |
| Pandas         | Manipulação e análise de dados         |
| Plotly Express | Visualização de dados                  |
| SQLite         | Banco de dados local                   |
| python-dotenv  | Gerenciamento de variáveis de ambiente |

## 3. Estrutura do projeto

```text
SAIP/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
├── .env.example
│
├── src/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   └── analyzer.py
│
└── database/
    └── saip_local.db
```

### Descrição dos principais arquivos

**app.py**

Arquivo principal da aplicação. Responsável por:

- Inicializar a interface Streamlit.
- Controlar a autenticação dos usuários.
- Gerenciar a navegação entre as páginas.
- Receber arquivos CSV.
- Apresentar os resultados das análises.
- Disponibilizar o histórico de importações.

**src/auth.py**

Módulo responsável pelas funcionalidades de autenticação:

- Autenticação de usuários.
- Criação do usuário inicial.
- Verificação de credenciais.
- Alteração de senha.

**src/database.py**

Módulo responsável pela comunicação com o SQLite:

- Inicialização do banco de dados.
- Armazenamento dos conjuntos de dados.
- Listagem das importações.
- Recuperação de conjuntos previamente armazenados.

**src/analyzer.py**

Módulo responsável pelo processamento estatístico:

- Leitura de arquivos CSV.
- Identificação preliminar de colunas identificadoras.
- Cálculo de estatísticas descritivas.
- Análise de variáveis numéricas.
- Análise de variáveis categóricas.
- Cálculo de indicadores de qualidade dos dados.

**database/**

Diretório destinado ao armazenamento do banco de dados SQLite utilizado localmente pela aplicação.

## 4. Funcionalidades disponíveis

### Autenticação

O sistema possui uma tela inicial de autenticação, permitindo o acesso por usuário e senha.

Também disponibiliza a funcionalidade de alteração de senha, incluindo a exigência de substituição da senha inicial quando configurada pelo módulo de autenticação.

### Importação de dados

O usuário pode selecionar um arquivo CSV para processamento.

Durante a importação, o sistema permite:

- Visualizar uma prévia dos registros.
- Identificar preliminarmente possíveis colunas identificadoras.
- Selecionar colunas que devem ser excluídas.
- Definir um nome para a importação.
- Escolher se os dados processados serão armazenados localmente.

### Análise estatística

Após o processamento, o sistema apresenta:

- Quantidade de registros.
- Quantidade de variáveis.
- Valores ausentes.
- Registros duplicados.
- Estatísticas descritivas das variáveis numéricas.
- Frequências das variáveis categóricas.
- Distribuição de valores por meio de gráficos.
- Indicadores de qualidade dos dados.

### Histórico de importações

As importações armazenadas no banco local podem ser consultadas posteriormente e carregadas novamente para visualização dos resultados.

## 5. Requisitos para execução

Recomenda-se utilizar Python 3.10 ou superior.

Também é necessário possuir o Git instalado, caso deseje clonar o repositório.

## 6. Instalação

### 6.1. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
```

Entre no diretório:

```bash
cd SAIP
```

### 6.2. Criar ambiente virtual

Windows:

```bash
python -m venv .venv
```

Ativar o ambiente:

```bash
.venv\Scripts\activate
```

Linux ou macOS:

```bash
python3 -m venv .venv
```

Ativar:

```bash
source .venv/bin/activate
```

### 6.3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 6.4. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto, utilizando `.env.example` como referência.

As variáveis devem corresponder aos nomes efetivamente utilizados pelo módulo `src/auth.py`.

Não compartilhe o arquivo `.env`, pois ele pode conter credenciais e informações sensíveis.

### 6.5. Executar a aplicação

```bash
streamlit run app.py
```

Após a inicialização, o Streamlit disponibilizará o endereço local da aplicação, normalmente:

```text
http://localhost:8501
```

## 7. Banco de dados

O SAIP utiliza SQLite para armazenar informações localmente.

A persistência dos conjuntos de dados é opcional e depende da seleção realizada durante a importação do CSV.

O banco é inicializado pela aplicação por meio da função `init_db()`.

**Atenção:** o banco SQLite local não possui criptografia nativa. A utilização de dados pessoais ou sensíveis exige controles adicionais de segurança, acesso, proteção das chaves, retenção e auditoria.

## 8. Privacidade e proteção de dados

O projeto considera a importância da proteção dos dados utilizados nas análises.

A identificação automática de possíveis colunas pessoais é uma funcionalidade auxiliar, que permite sugerir campos para exclusão.

Entretanto:

- A identificação automática não garante a remoção de todos os dados pessoais.
- A exclusão de nomes e documentos não garante anonimização.
- Dados pseudonimizados continuam sujeitos à LGPD.
- A persistência de dados reais exige medidas adicionais de segurança e governança.

Recomenda-se utilizar dados fictícios durante os testes e validar os procedimentos de proteção antes de utilizar bases reais, especialmente dados educacionais de crianças e adolescentes.

## 9. Desenvolvimento futuro

O projeto poderá evoluir com a implementação de:

- Dashboard responsivo com identidade visual própria.
- Abas de análises estatísticas avançadas.
- Comparação de desempenho entre turmas e períodos.
- Análise de habilidades e indicadores pedagógicos.
- Relatórios exportáveis em PDF e Excel.
- Identificação de tendências e padrões de aprendizagem.
- Indicadores de inteligência pedagógica.
- Aprimoramento dos mecanismos de privacidade e segurança.
- Controle de acesso por perfil de usuário.

## 10. Licença

Projeto em desenvolvimento. A definição de licença de distribuição deverá ser realizada pelos responsáveis pelo projeto.
