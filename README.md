# GID-Project 🗂
Este projeto é um desafio de configuração de um ambiente adequado para desenvolvimento com os frameworks Apache Airflow e DBT, além de criar DAGs e modelos DBT para executar um pipeline de transformação de dados.


# Visão Geral
O dbt (data build tool) é uma ferramenta de linha de comando que permite que equipes de dados transformem dados em seu warehouse mais eficientemente. O Airflow é uma plataforma para programar e monitorar fluxos de trabalho, permitindo que você orquestre suas tarefas de transformação de dados (dbt) e outras tarefas relacionadas.

# Pré-requisitos
- Conta na Google Cloud Platform (GCP) com acesso ao BigQuery
- Instalação do dbt configurada para uso com o BigQuery
- Instalação do Apache Airflow
- Configuração Inicial
Antes de começar, é necessário ter um projeto dbt configurado e pronto para ser executado. Além disso, seu ambiente Airflow deve estar configurado e operacional.

# Integração do dbt com o Airflow
Passo 1: Configurar o Projeto dbt
Certifique-se de que o seu projeto dbt esteja configurado corretamente, com um arquivo profiles.yml que define como o dbt se conecta ao seu data warehouse.

# Passo 2: Criar Modelos dbt
Os modelos dbt definem as transformações SQL que você deseja aplicar aos seus dados. Crie modelos dbt no diretório models do seu projeto.

# Passo 3: Testar Modelos dbt
Execute o dbt run localmente para garantir que seus modelos sejam compilados e executados corretamente.

# Passo 4: Criar um DAG do Airflow
No Airflow, crie um novo DAG (Directed Acyclic Graph) que definirá a sequência e o agendamento das suas tarefas de transformação de dados.

# Passo 5: Adicionar Tarefas dbt a DAG
Adicione tarefas ao seu DAG para executar os comandos dbt, como dbt run e dbt test. Você pode usar o BashOperator do Airflow para chamar esses comandos.

# Passo 6: Configurar Dependências
Defina as dependências entre as tarefas do dbt e outras tarefas no Airflow para garantir que sejam executadas na ordem correta.

# Passo 7: Executar a DAG
Ative e execute o seu DAG no Airflow para testar a automação completa do seu pipeline de dados.
