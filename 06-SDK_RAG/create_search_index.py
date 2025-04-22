from dotenv import load_dotenv
import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.identity import get_bearer_token_provider
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SearchIndex
)

load_dotenv("credentials.env", override=True)

# create a project client using environment variables loaded from the credentials.env file
project = AIProjectClient.from_connection_string(
    conn_str=os.environ["AIPROJECT_CONNECTION_STRING"], credential=DefaultAzureCredential()
)

# use the project client to get the default search connection
search_connection = project.connections.get_default(
    connection_type=ConnectionType.AZURE_AI_SEARCH, include_credentials=True
)

# Create a search index  
index_name = os.environ["AISEARCH_INDEX_NAME"]
index_client = SearchIndexClient(endpoint=search_connection.endpoint_url, credential=AzureKeyCredential(key=search_connection.key))
fields = [
    SearchField(name="parent_id", type=SearchFieldDataType.String),  
    SearchField(name="title", type=SearchFieldDataType.String),
    SearchField(name="chunk_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, analyzer_name="keyword"),  
    SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),  
    SearchField(name="text_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile")
    ]  

# Configure the vector search configuration  
vector_search = VectorSearch(  
    algorithms=[  
        HnswAlgorithmConfiguration(name="myHnsw"),
    ],  
    profiles=[  
        VectorSearchProfile(  
            name="myHnswProfile",  
            algorithm_configuration_name="myHnsw",  
            vectorizer_name="myOpenAI",  
        )
    ],  
    vectorizers=[  
        AzureOpenAIVectorizer(  
            vectorizer_name="myOpenAI",  
            kind="azureOpenAI",  
            parameters=AzureOpenAIVectorizerParameters(  
                resource_url=os.environ["AZURE_OPENAI_ACCOUNT"],  
                deployment_name=os.environ["EMBEDDINGS_MODEL"],
                model_name=os.environ["EMBEDDINGS_MODEL"],
            ),
        ),  
    ], 
)  

# Create the search index
index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)  
result = index_client.create_or_update_index(index)  
print(f"{result.name} created")