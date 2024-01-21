# GID-Project 🗂
Este projeto é um desafio de configuração de um ambiente adequado para desenvolvimento com os frameworks Apache Airflow e DBT, além de criar DAGs e modelos DBT para executar um pipeline de transformação de dados.


# Visão Geral
O dbt (data build tool) é uma ferramenta de linha de comando que permite que equipes de dados transformem dados em seu warehouse mais eficientemente. O Airflow é uma plataforma para programar e monitorar fluxos de trabalho, permitindo que você orquestre suas tarefas de transformação de dados (dbt) e outras tarefas relacionadas.

# Pré-requisitos
- Conta na Google Cloud Platform (GCP) com acesso ao BigQuery
- Instalação do dbt configurada para uso com o BigQuery
- Instalação do Apache Airflow
- Configuração Inicial
- OBS.: Antes de começar, é necessário ter um projeto dbt configurado em ambiente Linux, no caso deste projeto específico foi utilizado o ambiente WSL dentro do Windows.

## Integração do dbt com o Airflow
    pip install dbt
    pip install apache-airflow
    
## Inicializar o Airflow databse
    airflow db init
  
  ## Inicializar o Airflow webserver e o scheduler
    airflow webserver --port 8080
    airflow scheduler

## Abra a Interface Web do Airflow

Acesse http://localhost:8080 no navegador.

## Acesse as Conexões

Clique em “Admin” no menu superior e selecione “Conexões”.

## Adicione uma Nova Conexão (SE NÃO HOUVER)

Clique no botão “Criar” para adicionar uma nova conexão.

## Preencha os Detalhes da Conexão

- **Conn Id**: Insira um ID único para a conexão (por exemplo, “bigquery_conn”).
- **Conn Type**: Selecione “Google Cloud Platform”.
- **Login**: Insira o e-mail da sua conta de serviço do Google Cloud.
- **Senha**: Insira a chave da sua conta de serviço do Google Cloud (formato JSON).
  ![image](https://github.com/PedroDPV/GID-Project/assets/103441250/5aa0dfa9-ef1b-4524-a075-7bfe43714dae)

  # Passo 1: Configurar o Projeto dbt
  Certifique-se de que projeto dbt esteja configurado corretamente, com um arquivo profiles.yml que define como o dbt se conecta ao seu data warehouse (que no caso será o bigquery).
  ##  Execute o comando:
      dbt init projeto_dbt
  ##  Navegue até a Pasta do Projeto DBT:
      cd projeto_dbt
  ## Configure o profiles.yml:
  O arquivo profiles.yml é onde você define a conexão com o seu banco de dados. Normalmente, ele fica localizado em ~/.dbt/.
Você precisa configurar este arquivo com as informações da sua Service Account do Google Cloud e outras configurações de conexão com o BigQuery.
Exemplo de configuração para o BigQuery.
  ## yaml:
      projeto_dbt:
       target: dev
       outputs:
        dev:
          type: bigquery
          method: service-account
          project: [SEU_PROJECT_ID]
          dataset: [SEU_DATASET]
          threads: [NUMERO_DE_THREADS]
          keyfile: [CAMINHO_PARA_SUA_SERVICE_ACCOUNT_JSON]
          timeout_seconds: 300
          location: [LOCALIZACAO_DO_DATASET] # ex: US
  ## Teste a conexão (verificando se o dbt consegue se conectar ao Bigquery):
      dbt debug
  deve aparecer algo como o print a seguir
  ![image](https://github.com/PedroDPV/GID-Project/assets/103441250/ab00f79e-d764-4b33-9423-1d89f3c42bc9)


  
![image](https://github.com/PedroDPV/GID-Project/assets/103441250/d1993ad5-07fb-497b-bd5d-a500e4f7a3e6)

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
