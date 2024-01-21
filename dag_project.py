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