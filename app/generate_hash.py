from werkzeug.security import generate_password_hash

# Remplacez 'votrenouveaumotdepasse' par le mot de passe que vous voulez utiliser
new_password = 'yomna2002'
hashed_password = generate_password_hash(new_password)

print("Utilisez cette chaîne pour mettre à jour votre base de données :")
print(hashed_password)