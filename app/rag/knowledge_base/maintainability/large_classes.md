Issue Type: Large Classes (God Object)
Category: Maintainability
Severity: Medium

Description:
Une classe accumule un grand nombre de responsabilites et de methodes non liees
(souvent appelee "God Object"), devenant un point central que presque tout le
code doit connaitre et modifier.

Why is it a problem:
Toute modification, meme mineure, risque d'affecter des fonctionnalites sans
rapport apparent. La classe devient difficile a tester isolement et un point
de conflit frequent quand plusieurs developpeurs y travaillent en meme temps.

Bad Example:
class UserManager:
    def create_user(self): ...
    def send_email(self): ...
    def generate_pdf_report(self): ...
    def calculate_statistics(self): ...
    def connect_to_github(self): ...
    def validate_payment(self): ...

Good Example:
class UserService:
    def create_user(self): ...

class EmailService:
    def send_email(self): ...

class ReportService:
    def generate_pdf_report(self): ...
    def calculate_statistics(self): ...

How to Fix:
Identifier les groupes de methodes qui changent ensemble pour les memes raisons
(coherence forte) et les extraire dans des classes separees, chacune avec une
responsabilite claire et nommee explicitement.

Common Student Mistakes:
- Ajouter des methodes a une classe existante par facilite, sans se demander si elles y ont leur place
- Craindre de "casser" le code en decoupant une grosse classe, et repousser indefiniment le refactoring

Educational Explanation:
Le principe de responsabilite unique s'applique aux classes comme aux fonctions :
une classe devrait avoir une seule raison de changer. Si tu peux imaginer deux
personnes differentes (l'une responsable des emails, l'autre des utilisateurs)
qui auraient chacune une bonne raison de modifier la meme classe pour des motifs
totalement independants, c'est le signal qu'il faut la separer.

Related Concepts: Single Responsibility Principle, Cohesion, Coupling, God Object Anti-pattern