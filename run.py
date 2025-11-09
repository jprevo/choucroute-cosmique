from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='gemma3:4b', messages=[
  {
    'role': 'user',
    'content': 'Écrit 8 mots-clés en français décrivant cette image, séparés par une virgule, du plus commun au plus spécifique. N\'écrit que les mots-clés. Exemple : "Personne, Chat, Salon, Tapis". Mots-clés :',
    'images': ['./images/photos/depositphotos_9209115-stock-photo-young-group-of-friends-hanging.jpg'],
  },
])

print(response.message.content)