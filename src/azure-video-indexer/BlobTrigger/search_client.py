from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

def create_search_client(index_name):
    search_service_name = "your-search-service-name"
    admin_key = "your-admin-key"

    credential = AzureKeyCredential(admin_key)
    search_client = SearchClient(endpoint=f"https://{search_service_name}.search.windows.net/",
                                 index_name=index_name,
                                 credential=credential)
    return search_client