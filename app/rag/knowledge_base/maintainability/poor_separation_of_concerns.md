Issue Type: Poor Separation of Concerns
Category: Maintainability
Severity: Medium

Description:
Plusieurs preoccupations distinctes (acces base de donnees, logique metier,
presentation/formatage, validation) sont melangees dans la meme fonction ou le
meme fichier, sans separation claire des couches.

Why is it a problem:
Il devient impossible de tester la logique metier sans une vraie base de donnees,
de reutiliser la logique dans un autre contexte (API vs script CLI), ou de
changer une couche (par exemple la base de donnees) sans risquer de casser
la logique metier melangee avec elle.

Bad Example:
@router.post("/orders")
def create_order(data: dict):
    if data["quantity"] <= 0:
        raise HTTPException(400, "quantite invalide")
    total = data["price"] * data["quantity"]
    db.execute("INSERT INTO orders (total) VALUES (%s)", (total,))
    return {"html": f"<p>Commande de {total} EUR creee</p>"}

Good Example:
def validate_order(data): ...
def calculate_total(data): ...

def save_order(db, total): ...

@router.post("/orders")
def create_order(data: OrderCreate, db=Depends(get_db)):
    validate_order(data)
    total = calculate_total(data)
    save_order(db, total)
    return OrderOut(total=total)

How to Fix:
Separer explicitement les couches : validation (schemas Pydantic), logique
metier (services), acces donnees (repositories), presentation (routes/schemas
de sortie) — exactement le pattern que ton propre projet applique deja au
niveau architecture globale.

Common Student Mistakes:
- Ecrire toute la logique directement dans la fonction de route pour "aller vite"
- Retourner du HTML ou du texte formate directement depuis la couche d'acces aux donnees

Educational Explanation:
Separer les preoccupations rend chaque couche testable independamment (tester la
logique de calcul sans base de donnees reelle, par exemple), et rend le systeme
plus resilient au changement : remplacer PostgreSQL par une autre base ne devrait
toucher que la couche d'acces aux donnees, jamais la logique metier.

Related Concepts: Layered Architecture, Separation of Concerns, Dependency Injection, Testability