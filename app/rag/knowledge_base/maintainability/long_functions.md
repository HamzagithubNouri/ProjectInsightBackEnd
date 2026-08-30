Issue Type: Long Functions
Category: Maintainability
Severity: Medium

Description:
Une fonction qui depasse ~40-50 lignes ou qui gere plusieurs responsabilites
distinctes (validation, logique metier, acces donnees, formatage) dans le meme bloc.

Why is it a problem:
Difficile a tester unitairement (trop de chemins d'execution a couvrir), difficile
a comprendre d'un seul coup d'oeil, et un changement dans une partie risque de casser
une autre partie non liee.

Bad Example:
def process_order(order_data):
    if not order_data.get("items"):
        raise ValueError("empty order")
    total = 0
    for item in order_data["items"]:
        total += item["price"] * item["qty"]
    if order_data.get("coupon"):
        total = total * 0.9
    db.execute("INSERT INTO orders ...")
    send_email(order_data["email"], f"Order confirmed: {total}")
    log.info(f"Order processed: {total}")
    return total

Good Example:
def process_order(order_data):
    validate_order(order_data)
    total = calculate_total(order_data)
    save_order(order_data, total)
    notify_customer(order_data, total)
    return total

How to Fix:
Extraire chaque responsabilite distincte (validation, calcul, persistance,
notification) dans sa propre fonction nommee explicitement.

Common Student Mistakes:
- Ajouter du code a une fonction existante plutot que d'en creer une nouvelle
- Melanger logique metier et effets de bord (DB, email, logs) dans le meme bloc

Educational Explanation:
Une fonction devrait faire une seule chose et le faire bien (principe de
responsabilite unique). Si tu dois utiliser "et" pour decrire ce que fait ta
fonction ("elle valide ET calcule ET sauvegarde"), c'est un signal qu'il faut
la decouper.

Related Concepts: Single Responsibility Principle, Separation of Concerns, Refactoring