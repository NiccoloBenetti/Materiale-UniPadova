import os
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from create_search_index import search_connection

# Create a data source 
indexer_client = SearchIndexerClient(endpoint=os.environ["AZURE_SEARCH_SERVICE"], credential=AzureKeyCredential(key=search_connection.key))
container = SearchIndexerDataContainer(name=os.environ["CONTAINER_NAME"])
data_source_connection = SearchIndexerDataSourceConnection(
    name=os.environ["AISEARCH_DATA_SOURCE_NAME"],
    type="azureblob",
    connection_string=os.environ["AZURE_STORAGE_CONNECTION_STRING"],
    container=container
)
data_source = indexer_client.create_or_update_data_source_connection(data_source_connection)

print(f"Data source '{data_source.name}' created or updated")