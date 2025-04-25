from storage import clients

# Utility function to search for clients by name (case-insensitive)
def search_clients(query):
    return [client for client in clients.values() if query.lower() in client.name.lower()]