"""
Exercice 1 : Ingénierie de Prompt pour l'Extraction d'Informations
Voir readme.MD pour le tutoriel complet

═══════════════════════════════════════════════════════════════════
OBJECTIF DE L'EXERCICE
═══════════════════════════════════════════════════════════════════

Rédiger un prompt robuste en suivant les 4 piliers :
1. Contexte       → Définir le rôle de l'assistant
2. Objectif       → Décrire la tâche précisément  
3. Instructions   → Lister les étapes à suivre
4. Few-Shot       → Donner un exemple concret

═══════════════════════════════════════════════════════════════════
"""

PROMPT_TEMPLATE = """
═══════════════════════════════════════════════════════════════════
CONTEXTE
═══════════════════════════════════════════════════════════════════

[À COMPLÉTER]

Définissez le rôle de l'assistant :
- Quel est son domaine d'expertise ?
- Quel type de documents analyse-t-il ?
- Quelle est sa mission principale ?


═══════════════════════════════════════════════════════════════════
OBJECTIF
═══════════════════════════════════════════════════════════════════

[À COMPLÉTER]

Décrivez précisément la tâche :
- Qu'est-ce qui doit être extrait ? (membres du comité exécutif d'Apple)
- Quelles informations pour chaque membre ? (7 champs au total)
  * Nom
  * Prénom(s)
  * Âge
  * Genre
  * Rôle
  * Nationalité
  * Adresse professionnelle
- Quel format de sortie ? (JSON)


═══════════════════════════════════════════════════════════════════
INSTRUCTIONS
═══════════════════════════════════════════════════════════════════

[À COMPLÉTER]

Listez les étapes à suivre (minimum 5-6 instructions) :
1. Comment identifier les membres ?
2. Comment extraire les informations ?
3. Que faire si une information est manquante ? (→ null)
4. Quel format exact de sortie ? (JSON uniquement, sans texte)
5. Comment raisonner ? (étape par étape - Chain of Thought)
6. ...


═══════════════════════════════════════════════════════════════════
SCHÉMA DE SORTIE
═══════════════════════════════════════════════════════════════════

[À COMPLÉTER]

Décrivez précisément le format de la sortie JSON :
1. La sortie doit être un tableau JSON (`[]`) de membres du comité exécutif.
2. Chaque élément du tableau doit être un objet JSON représentant une personne.
3. Chaque objet doit contenir exactement les champs suivants :
   - "nom"
   - "prenom"
   - "age"
   - "genre"
   - "role"
   - "nationalite"
   - "adresse_professionnelle"
4. Les champs dont l’information est absente doivent être renseignés avec `null`.
5. Aucun texte explicatif ne doit être renvoyé, uniquement le JSON valide.
6. Assurez-vous que le JSON final soit bien formé et directement parseable.

═══════════════════════════════════════════════════════════════════
EXEMPLE (Few-Shot Learning)
═══════════════════════════════════════════════════════════════════

Fournissez un exemple complet :

Texte extrait du document :
"[Exemple de texte décrivant un membre du comité exécutif]"

Sortie JSON attendue :
[
  {
    "nom": "...",
    "prenom": "...",
    "age": ...,
    "genre": "...",
    "role": "...",
    "nationalite": "...",
    "adresse_professionnelle": "..."
  }
]
"""


def generate_prompt_template():
    return PROMPT_TEMPLATE