import ollama

# ---
# 1. Installation de la bibliothèque Python
# Si ce n'est pas déjà fait, installez la bibliothèque Python d'Ollama :
# pip install ollama
#
# Assurez-vous également qu'Ollama est en cours d'exécution en arrière-plan et
# que le modèle 'llama3' est bien installé (ollama run llama3).
# ---

class RecoFlixChatbot:
    """
    Classe pour gérer la conversation avec le modèle Ollama.
    Elle garde en mémoire l'historique de la discussion.
    """
    def __init__(self):
        # Initialise l'historique de la discussion avec un message système.
        self.chat_history = [
            {"role": "system", "content": "Vous êtes RecoFlix, un assistant utile et amical spécialisé dans les recommandations de films. Répondez aux questions sur le cinéma ou donnez des suggestions de films. Votre but est d'aider les utilisateurs à trouver leur prochain film à regarder."}
        ]

    def get_response(self, prompt):
        """
        Envoie un message au modèle Ollama et retourne sa réponse.
        """
        # Ajoute le message de l'utilisateur à l'historique de discussion.
        self.chat_history.append({"role": "user", "content": prompt})

        try:
            # Envoie l'historique complet au modèle Ollama local.
            response = ollama.chat(
                model="llama3",  # Le nom du modèle que vous avez téléchargé.
                messages=self.chat_history
            )
            
            # Extrait la réponse du modèle et l'ajoute à l'historique.
            model_response = response['message']['content'].strip()
            self.chat_history.append({"role": "assistant", "content": model_response})
            
            return model_response
        except Exception as e:
            print(f"Une erreur s'est produite lors de la connexion à Ollama : {e}")
            print("Veuillez vérifier qu'Ollama est en cours d'exécution et que le modèle 'llama3' est bien installé.")
            return "Désolé, je n'ai pas pu contacter mon serveur de chatbot. Assurez-vous qu'Ollama est en cours d'exécution."

# Instance du chatbot pour l'utiliser dans l'application Flask
# C'est cette ligne qui rend 'reco_flix_chatbot' importable depuis d'autres modules.
reco_flix_chatbot = RecoFlixChatbot()

