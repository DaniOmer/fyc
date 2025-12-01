def create_extraction_prompt(problem_description: str) -> str:
    """
    Crée un prompt pour extraire les éléments du problème d'optimisation

    Args:
        problem_description: Énoncé du problème en langage naturel

    Returns:
        Prompt formaté pour le LLM
    """
    prompt = f"""
    **CONTEXTE :**
    Tu es un expert en optimisation et en analyse de problèmes mathématiques.
    Ton rôle est d'extraire et structurer les informations d'un problème d'optimisation pour permettre sa résolution par un solveur.

    **ÉNONCÉ DU PROBLÈME :**
    {problem_description}

    **OBJECTIF :**
    Extraire et structurer TOUTES les informations de cet énoncé au format JSON avec les clés suivantes :
    - variables_decision : les variables à déterminer par le solveur
    - contraintes : toutes les contraintes (hard et soft)
    - fonction_objectif : ce qu'on cherche à optimiser
    - donnees : les enseignants et leurs caractéristiques

    **INSTRUCTIONS :**

    1. Pour les VARIABLES DE DÉCISION :
       - Identifie les variables à déterminer
       - Précise le type : binary (0/1), integer (entier), ou continuous (réel)
       - Formule-les de manière mathématique

    2. Pour les CONTRAINTES :
       - Liste TOUTES les contraintes mentionnées
       - Distingue les contraintes HARD (obligatoires, doivent être respectées absolument)
       - Distingue les contraintes SOFT (préférences, souhaitables mais pas obligatoires)
       - Donne un ID unique à chaque contrainte

    3. Pour la FONCTION OBJECTIF :
       - Identifie ce qu'on cherche à minimiser (coût, temps, distance, etc.)
       - Ou ce qu'on cherche à maximiser (profit, satisfaction, utilisation, etc.)

    4. Pour les DONNÉES :
       - Extrais les enseignants avec toutes leurs caractéristiques
       - Structure les données de manière exploitable

    **IMPORTANT :**
    - Sois précis et exhaustif
    - Ne résous PAS le problème, extrais seulement sa structure
    - Respecte strictement le format JSON

    **EXEMPLE DE SORTIE :**
    {{
        "variables_decision": {{
            "nom": "x[i,j,k]",
            "description": "1 si l'enseignant i enseigne le jour j pendant la période k, 0 sinon",
            "type": "binary"
        }},
        "contraintes": [
            {{
                "id": "C1",
                "type": "hard",
                "description": "Chaque enseignant doit enseigner exactement ses heures hebdomadaires"
            }},
            {{
                "id": "C2",
                "type": "soft",
                "description": "Respecter les préférences de jours si possible"
            }}
        ],
        "fonction_objectif": {{
            "type": "maximiser",
            "description": "La satisfaction globale des enseignants"
        }},
        "donnees": {{
            "enseignants": [
                {{
                    "nom": "Alice",
                    "heures_hebdo": 18,
                    "preferences": ["lundi", "mercredi"]
                }}
            ]
        }}
    }}

    Génère maintenant la structure complète du problème au format JSON.
    """
    return prompt