import os
from dotenv import load_dotenv
from azure.search.documents.indexes.models import (
    SearchIndexer,
    FieldMapping
)
from azure.search.documents.indexes import SearchIndexerClient
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from create_search_index import index_name, search_connection
from create_skillset import skillset_name
from create_datasource_connection import data_source

load_dotenv("credentials.env", override=True)

# Create an indexer  
indexer_name = os.environ["AISEARCH_INDEXER_NAME"] 

indexer_parameters = None

indexer = SearchIndexer(  
    name=indexer_name,  
    description="Indexer to index documents and generate embeddings",  
    skillset_name=skillset_name,  
    target_index_name=index_name,  
    data_source_name=data_source.name,
    # Map the metadata_storage_name field to the title field in the index to display the PDF title in the search results  
    field_mappings=[FieldMapping(source_field_name="metadata_storage_name", target_field_name="title")],
    parameters=indexer_parameters
)  

# Create and run the indexer  
indexer_client = SearchIndexerClient(endpoint=os.environ["AZURE_SEARCH_SERVICE"], credential=AzureKeyCredential(key=search_connection.key))  
indexer_result = indexer_client.create_or_update_indexer(indexer)  

print(f' {indexer_name} is created and running. Give the indexer a few minutes before running a query.')