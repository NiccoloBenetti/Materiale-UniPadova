import os
from azure.search.documents.indexes.models import (
    SplitSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    EntityRecognitionSkill,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
    SearchIndexerSkillset,
    CognitiveServicesAccountKey,
    CognitiveServicesAccount
)
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.core.credentials import AzureKeyCredential
from create_search_index import index_name, search_connection

credential = DefaultAzureCredential()

# Create a skillset  
skillset_name = os.environ["AISEARCH_SKILLSET_NAME"]

split_skill = SplitSkill(
    description="Split skill to chunk documents",  
    text_split_mode="pages",  
    context="/document",  
    maximum_page_length=2000,  
    page_overlap_length=500,  
    inputs=[  
        InputFieldMappingEntry(name="text", source="/document/content"),  
    ],  
    outputs=[  
        OutputFieldMappingEntry(name="textItems", target_name="pages")  
    ],  
)  

embedding_skill = AzureOpenAIEmbeddingSkill(  
    description="Skill to generate embeddings via Azure OpenAI",  
    context="/document/pages/*",  
    resource_url=os.environ["AZURE_OPENAI_ACCOUNT"],  
    deployment_name= os.environ["EMBEDDINGS_MODEL"],  #usiamo lo stesso nome sia per il deployment che per il modello
    model_name=os.environ["EMBEDDINGS_MODEL"],
    dimensions=1536,
    inputs=[  
        InputFieldMappingEntry(name="text", source="/document/pages/*"),  
    ],  
    outputs=[  
        OutputFieldMappingEntry(name="embedding", target_name="text_vector")  
    ],  
)

index_projections = SearchIndexerIndexProjection(  
    selectors=[  
        SearchIndexerIndexProjectionSelector(  
            target_index_name=index_name,  
            parent_key_field_name="parent_id",  
            source_context="/document/pages/*",  
            mappings=[  
                InputFieldMappingEntry(name="chunk", source="/document/pages/*"),  
                InputFieldMappingEntry(name="text_vector", source="/document/pages/*/text_vector"), 
                InputFieldMappingEntry(name="title", source="/document/metadata_storage_name"),  
            ],  
        ),  
    ],  
    parameters=SearchIndexerIndexProjectionsParameters(  
        projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS  
    ),
) 

# cognitive_services_account = CognitiveServicesAccountKey(key=os.environ["AZURE_AI_MULTISERVICE_KEY"])
# cognitive_services_account = AIServicesAccountKey(
#     key=os.environ["AZURE_AI_MULTISERVICE_KEY"], 
#     subdomain_url=azure_ai_services_endpoint
#     )

skills = [split_skill, embedding_skill]

skillset = SearchIndexerSkillset(  
    name=skillset_name,  
    description="Skillset to chunk documents and generating embeddings",  
    skills=skills,  
    index_projection=index_projections,
    #cognitive_services_account=cognitive_services_account
)
  
client = SearchIndexerClient(endpoint=os.environ["AZURE_SEARCH_SERVICE"], credential=AzureKeyCredential(key=search_connection.key))  
client.create_or_update_skillset(skillset)  
print(f"{skillset.name} created")