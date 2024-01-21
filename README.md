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
  
## Comandos iniciais
    sudo apt update
    sudo apt install python3-pip   

![image](https://github.com/PedroDPV/GID-Project/assets/103441250/3841b5da-be15-4b26-bf77-93a7f1d91270)


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
- **Conn Type**: Selecione “Google BigQuery”.
- **Login**: Insira o e-mail da sua conta de serviço do Google Cloud.
- **Senha**: Insira a chave da sua conta de serviço do Google Cloud (formato JSON).
  ![image](https://github.com/PedroDPV/GID-Project/assets/103441250/5aa0dfa9-ef1b-4524-a075-7bfe43714dae)

  # Passo 1: Configurar o Projeto dbt
  Certifique-se de que o projeto dbt esteja configurado corretamente, com um arquivo profiles.yml que define como o dbt se conecta ao data warehouse (no caso deste projeto, será o bigquery).
  ##  Execute o comando:
      dbt init projeto_dbt
  ##  Navegue até a Pasta do Projeto DBT:
      cd projeto_dbt
  ## Configure o profiles.yml:
  O arquivo profiles.yml é onde é feita a definição da conexão com o seu banco de dados. Normalmente, ele fica localizado em ~/.dbt/.
É necessário configurar este arquivo com as informações da sua Service Account do Google Cloud e outras configurações de conexão com o BigQuery.
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
  Deverá aparecer uma imagem, como a mostrada abaixo:
  
  ![image](https://github.com/PedroDPV/GID-Project/assets/103441250/ab00f79e-d764-4b33-9423-1d89f3c42bc9)

  # Passo 2: Criar Modelos dbt
  - Os modelos dbt definem as transformações SQL que se deseja aplicar aos dados.
  - Crie modelos dbt no diretório models do  projeto.

  ## a. Instalar o dbt (se ainda não estiver instalado, com o adaptador para BigQuery):
        pip install dbt-bigquery
  ## b. Configurar o Projeto dbt:
  - Navegue até a pasta onde deseja criar ou já tem o seu projeto dbt:
      ```cd /caminho/para/seu/projeto_dbt```
  - Se ainda não tem um projeto dbt, crie um executando:
      ```dbt init seu_nome_de_projeto_dbt```

Isso criará uma nova estrutura de projeto dbt com as configurações iniciais.

![image](https://github.com/PedroDPV/GID-Project/assets/103441250/a2a8bdbc-0600-4feb-a65b-2932db133144)

## c. Criar o Modelo dbt:
   - No diretório do seu projeto dbt, navegue até a pasta models:
        ```cd models```
   - Crie um novo arquivo .sql para o modelo dbt usando um editor de texto como o nano ou vim:
        ```nano cleaned_fakenames.sql```
- Escreva o SQL para o modelo.

```
SELECT
  -- Substituindo strings vazias por valores nulos e capitalizando as palavras
  IF(TRIM(GivenName) = '', NULL, INITCAP(GivenName)) AS GivenName,
  IF(TRIM(Surname) = '', NULL, INITCAP(Surname)) AS Surname,
  -- Traduzindo o gênero de inglês para português
  CASE Gender
    WHEN 'male' THEN 'masculino'
    WHEN 'female' THEN 'feminino'
    ELSE NULL
  END AS Gender,
  -- Capitalizando as cidades e removendo as aspas
  INITCAP(REGEXP_REPLACE(TRIM(City), r'^"|"$', '')) AS City,
  -- Capitalizando os estados e removendo as aspas
  INITCAP(REGEXP_REPLACE(TRIM(StateFull), r'^"|"$', '')) AS StateFull,
  ZipCode,
  EmailAddress,
  Username,
  CCType,
  CCNumber
FROM
  `terraform-366517.dataset_project.tbl_fakenames`
```

## d. Compile e Execute o dbt:

- Compile o código
      ```dbt compile```
- Para rodar o modelo dbt use ```dbt run --models  cleaned_fakenames``` para executar apenas o modelo específico no WSL.

![image](https://github.com/PedroDPV/GID-Project/assets/103441250/f97d4d82-526e-4c29-aaaf-9bd592fbcf6d)

  # Passo 4: Criar um DAG do Airflow
  No Airflow, crie uma nova DAG (Directed Acyclic Graph) que definirá a sequência e o agendamento das suas tarefas de transformação de dados.
  Aqui deverão ser adicionadas também tarefas para executar os comandos dbt, como dbt run.

  ```
  from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
import pandas as pd
import os
import logging
from google.cloud import storage
from google.cloud import bigquery


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

credential_path = '/home/pedrodpv/terraform-366517-733b2d955a83.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

with DAG('data_transformation_dag', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:

    
    @task
    def extract_data():
        csv_file_path = '~/fakenamgenerator.com_aa22a33f9.csv'
        df = pd.read_csv(csv_file_path)
        df_cleaned = df.dropna()
        df_cleaned = df_cleaned.applymap(lambda s: s.lower() if type(s) == str else s)
        cleaned_csv_file_path = '/home/pedrodpv/cleaned_data.csv'
        df_cleaned.to_csv(cleaned_csv_file_path, index=False)
        return cleaned_csv_file_path

    
    @task
    def load_data(cleaned_csv_file_path):
        logger = logging.getLogger("airflow.task")
        bucket_name = 'gid_bucket_project'
        destination_blob_name = 'cleaned_data.csv'
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(cleaned_csv_file_path)
        logger.info(f"File {cleaned_csv_file_path} uploaded to {bucket_name}/{destination_blob_name}.")
        return cleaned_csv_file_path

    # Tarefa Python para carregar dados do GCS para o BigQuery
    def load_csv_to_bigquery(bucket_name, source_blob_name, destination_table_id, project_id):
        bigquery_client = bigquery.Client(project=project_id)
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        uri = f"gs://{bucket_name}/{source_blob_name}"
        load_job = bigquery_client.load_table_from_uri(
            uri, destination_table_id, job_config=job_config
        )
        load_job.result()
        if load_job.errors is not None:
            raise Exception(f"Erro na job de carregamento: {load_job.errors}")
        print(f"Dados do {uri} carregados para {destination_table_id} com sucesso.")

    load_csv_to_bq_task = PythonOperator(
        task_id='load_csv_to_bq',
        python_callable=load_csv_to_bigquery,
        op_kwargs={
            'bucket_name': 'gid_bucket_project',
            'source_blob_name': 'cleaned_data.csv',
            'destination_table_id': 'terraform-366517.dataset_project.tbl_fakenames',
            'project_id': 'terraform-366517',
        },
        dag=dag,
    )

    
     # Tarefa para executar o modelo 'cleaned_fakenames' no dbt
    dbt_run_task = BashOperator(
    	task_id='dbt_run_cleaned_fakenames',
    	bash_command='cd ~/projeto_dbt && dbt run --models cleaned_fakenames',
    	dag=dag,
   
   )

    cleaned_csv_file_path = extract_data()
    loaded_csv_file_path = load_data(cleaned_csv_file_path)
    loaded_csv_file_path >> load_csv_to_bq_task >> dbt_run_task
  ```
  ## Inseririndo a dag na pasta do Airflow
  Certifíque-se de que a pasta do airflow contem uma outra pasta chamada "dag" para que passamos enviar nosso arquivo .py para la.
  lembre-se de que se a pasta não existir, voce precisará cria-la.
  
  ![image](https://github.com/PedroDPV/GID-Project/assets/103441250/869842aa-0449-4a04-9640-fe3e23e1c77b)
  

  
  # Passo 6: Configurar Dependências
  Defina as dependências entre as tarefas do dbt e outras tarefas no Airflow para garantir que sejam executadas na ordem correta.

  # Passo 7: Executar a DAG
  Ative e execute a sua DAG no Airflow para testar a automação completa do seu pipeline de dados.

  ![image](https://github.com/PedroDPV/GID-Project/assets/103441250/56208b15-0eb0-4a73-80b6-65d162e9d95e)

# Resultado Final do Processo de Orquestração de Dados

Como consequência do sucesso na execução da DAG, um processo no Airflow criará um pipeline onde primeiro haverá a extração do arquivo  com as informações que popularão a nossa tabela no bigquery e uma limpeza prévia dos dados.
A segunda etapa será de carregamento no nosso ambiente coud (Load), onde haverá um upload do dataframe no GCS (Google cloud storage) e posteriormente exportado para o nosso Data Wharehouse, que no caso será o BigQuery.
Por último devo explicar a fase de transformação e análise dos dados que serão representados nas imagens a seguir :


![image](https://github.com/PedroDPV/GID-Project/assets/103441250/4633aa9a-f566-4539-9cfd-ad5a4f5c61b1)

![image](https://github.com/PedroDPV/GID-Project/assets/103441250/28134594-fd5b-40a4-9176-714e0615bac3)
![image](https://github.com/PedroDPV/GID-Project/assets/103441250/af0902f1-5439-4e35-83d9-d21728ca05cb)

# Conclusão
Como conclusão desse pipeline deveríamos atingir os seguintes objetivos:

## Obter os valores agrupados de vendas por UF.
este objetivo foi facílmente alcançado após a execução da query logo ácima, onde evidenciamos a quantidade de venda por bandeira de cartão em cada UF, bem como o seu número total.
    
## Valores de vendas médias por dia.
já este, não será possível se levarmos em consideração a massa de dados aplicada para este exercício, pois não contem as informações que seriam obrigatórias como o valor das vendas propriamente dito e algum     formato de timestamp que seria utilizado para agrupar por data e chegar na conclusão das vendas médias por dia.
    




