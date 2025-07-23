def get_recommendations(film_name):
    # Exemple simple
    if not film_name:
        return []
    return [f"{film_name} - Suggestion 1", f"{film_name} - Suggestion 2", f"{film_name} - Suggestion 3"]
