import chromadb

# Replace the placeholder with the actual IP address you got from the output command
CHROMA_HOST_IP = "172.176.208.168"

chroma_client = chromadb.HttpClient(host=CHROMA_HOST_IP, port=8000)

# This command sends a simple request to the server to check if it's alive.
# It should return a timestamp if the server is running correctly.
print(chroma_client.heartbeat())
