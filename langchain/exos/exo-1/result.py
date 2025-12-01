PROMPT_TEMPLATE = """
═══════════════════════════════════════════════════════════════════
CONTEXTE
═══════════════════════════════════════════════════════════════════

Vous êtes un assistant intelligent spécialisé dans l'extraction d'informations 
à partir de documents officiels d'entreprises. Votre expertise porte sur 
l'analyse de documents financiers, réglementaires et de gouvernance d'entreprise 
(tels que les formulaires DEF 14A déposés auprès de la SEC).


═══════════════════════════════════════════════════════════════════
OBJECTIF
═══════════════════════════════════════════════════════════════════

Votre tâche est d'extraire la liste complète des membres du comité exécutif 
d'Apple Inc. à partir du document "Apple DEF 14A Statement" fourni.

Pour chaque membre du comité exécutif, vous devez récupérer les informations 
suivantes :
- Nom de famille
- Prénom(s)
- Âge
- Genre (Homme/Femme/Autre)
- Rôle occupé dans l'entreprise
- Nationalité
- Adresse professionnelle

Le résultat doit être fourni au format JSON structuré.


═══════════════════════════════════════════════════════════════════
INSTRUCTIONS
═══════════════════════════════════════════════════════════════════

Instructions importantes :

1. Identifier tous les membres du comité exécutif mentionnés dans le document
2. Pour chaque membre identifié, extraire systématiquement toutes les 
   informations demandées (nom, prénom, âge, genre, rôle, nationalité, adresse)
3. Si une information est manquante ou non mentionnée dans le document, 
   mettre la valeur null dans le JSON
4. Générer UNIQUEMENT le JSON final, sans explications, commentaires ou 
   texte additionnel avant ou après
5. Suivre exactement le schéma JSON fourni dans l'exemple ci-dessous
6. Raisonner étape par étape :
   a) D'abord, identifier la section du document listant les membres du 
      comité exécutif
   b) Ensuite, pour chaque membre, extraire toutes les informations requises
   c) Enfin, construire le JSON final conformément au schéma
7. S'assurer que le JSON est valide et correctement formaté (accolades, 
   virgules, guillemets)


═══════════════════════════════════════════════════════════════════
SCHÉMA DE SORTIE
═══════════════════════════════════════════════════════════════════

La sortie doit être un tableau JSON d'objets, où chaque objet représente
un membre du comité exécutif avec la structure suivante :

[
  {
    "nom": "string | null",                     # Nom de famille
    "prenom": "string | null",                  # Prénom(s)
    "age": "number | null",                     # Âge en années
    "genre": "string | null",                   # 'Homme', 'Femme' ou 'Autre'
    "role": "string | null",                    # Rôle occupé dans l'entreprise
    "nationalite": "string | null",             # Nationalité
    "adresse_professionnelle": "string | null"  # Adresse professionnelle complète
  }
]

Règles :
- Si une information est absente du document, utiliser la valeur null.
- Ne générer AUCUN autre texte que ce tableau JSON final.


═══════════════════════════════════════════════════════════════════
EXEMPLE (Few-Shot Learning)
═══════════════════════════════════════════════════════════════════

Exemple de sortie attendue :

Texte extrait du document :
"Tim Cook, né en 1960, est le Chief Executive Officer (CEO) d'Apple Inc. 
Il est de nationalité américaine et travaille au siège social d'Apple, 
situé à 1 Apple Park Way, Cupertino, Californie 95014."

Sortie JSON attendue :
[
  {
    "nom": "Cook",
    "prenom": "Tim",
    "age": 65,
    "genre": "Homme",
    "role": "Chief Executive Officer (CEO)",
    "nationalite": "Américain",
    "adresse_professionnelle": "1 Apple Park Way, Cupertino, CA 95014"
  }
]


═══════════════════════════════════════════════════════════════════
DOCUMENT À ANALYSER
═══════════════════════════════════════════════════════════════════

[COLLEZ ICI LE CONTENU DU PDF APPLE DEF 14A STATEMENT]


═══════════════════════════════════════════════════════════════════
GÉNÉRATION
═══════════════════════════════════════════════════════════════════

Générez maintenant le JSON contenant tous les membres du comité exécutif 
selon les instructions ci-dessus :

"""

def generate_prompt_template():
    return PROMPT_TEMPLATE