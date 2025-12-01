# Atelier : Extraction de données d'un problème d'optimisation avec LangChain

## Description

Cet atelier vous guide dans la création d'un système d'extraction et de structuration de données pour un problème d'optimisation d'emploi du temps. Vous utiliserez LangChain et Pydantic pour extraire automatiquement les **variables de décision**, les **contraintes** et la **fonction objectif** d'un énoncé en langage naturel, puis les structurer au format JSON.

**Note** : Cet exercice se concentre uniquement sur l'**extraction et la structuration** des données. La résolution du problème d'optimisation sera traitée dans un atelier dédié avec OR-Tools.

## Objectifs

- Charger et analyser un énoncé de problème d'optimisation en langage naturel
- Utiliser un LLM pour extraire les variables de décision, contraintes et objectif
- Valider la structure des données extraites avec Pydantic
- Générer un fichier JSON exploitable pour un solveur d'optimisation

---

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation des dépendances

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur macOS/Linux :
source venv/bin/activate

# Installer les packages nécessaires
pip install langchain langchain_community langchain-openai pydantic python-dotenv
```

### Configuration de l'API OpenAI

1. Créez un fichier `.env` à la racine du projet :

```bash
OPENAI_API_KEY=votre_clé_api_ici
```

2. Obtenez votre clé API sur [platform.openai.com](https://platform.openai.com/api-keys)

---

## Données de l'exercice

### Énoncé du problème

Créez un fichier `problem_description.txt` avec l'énoncé suivant :

```text
Problème de planification d'emploi du temps pour l'école "Le Campus"

ENSEIGNANTS ET MATIÈRES:
- Alice Martin enseigne Mathématiques, 6 heures par semaine, disponible Lundi, Mercredi, Vendredi
- Bob Dupont enseigne Physique, 4 heures par semaine, disponible Mardi, Jeudi
- Claire Leroy enseigne Français, 5 heures par semaine, disponible Lundi, Mardi, Jeudi
- David Petit enseigne Histoire, 3 heures par semaine, disponible Mercredi, Vendredi
- Emma Dubois enseigne Anglais, 5 heures par semaine, disponible Lundi, Mercredi, Jeudi

CONTRAINTES:
1. Chaque enseignant ne peut donner qu'une seule matière par jour
2. Chaque matière doit atteindre le nombre total d'heures assigné sur la semaine
3. Les créneaux horaires sont divisés en demi-journées (matin / après-midi)
4. Un enseignant ne peut enseigner que les jours où il est disponible
5. Chaque créneau (matin ou après-midi) dure 2 heures

OBJECTIF:
Créer un emploi du temps qui respecte toutes les contraintes et répartit équitablement les heures de cours sur les jours disponibles.
```

---

## Étapes de réalisation

### Étape 1 : Création du schéma Pydantic

Créez un fichier `models.py` pour définir la structure des données extraites :

```python
from pydantic import BaseModel, Field
from typing import List

class Teacher(BaseModel):
    """Représente un enseignant et ses caractéristiques"""
    name: str = Field(description="Nom complet de l'enseignant")
    subject: str = Field(description="Matière enseignée")
    hours_per_week: int = Field(description="Nombre d'heures à enseigner par semaine")
    available_days: List[str] = Field(description="Liste des jours de disponibilité")

class Constraint(BaseModel):
    """Représente une contrainte du problème d'optimisation"""
    id: int = Field(description="Identifiant unique de la contrainte")
    description: str = Field(description="Description textuelle de la contrainte")
    type: str = Field(description="Type de contrainte: 'hard' (obligatoire) ou 'soft' (préférence)")

class Variable(BaseModel):
    """Représente une variable de décision"""
    name: str = Field(description="Nom de la variable")
    description: str = Field(description="Description de ce que représente la variable")
    type: str = Field(description="Type de variable: 'binary', 'integer', 'continuous'")

class Objective(BaseModel):
    """Représente la fonction objectif du problème"""
    description: str = Field(description="Description de l'objectif à optimiser")
    type: str = Field(description="Type d'optimisation: 'minimize' ou 'maximize'")

class OptimizationProblem(BaseModel):
    """Structure complète du problème d'optimisation extrait"""
    problem_name: str = Field(description="Nom du problème")
    teachers: List[Teacher] = Field(description="Liste des enseignants")
    variables: List[Variable] = Field(description="Variables de décision du problème")
    constraints: List[Constraint] = Field(description="Liste des contraintes")
    objective: Objective = Field(description="Fonction objectif")
```

### Étape 2 : Chargement de l'énoncé du problème

Créez un fichier `load_data.py` :

```python
from langchain_community.document_loaders import TextLoader

def load_problem_description(file_path: str) -> str:
    """
    Charge l'énoncé du problème depuis un fichier texte

    Args:
        file_path: Chemin vers le fichier contenant l'énoncé

    Returns:
        Contenu du fichier sous forme de texte
    """
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()

    return documents[0].page_content

if __name__ == "__main__":
    # Test du chargement
    description = load_problem_description("problem_description.txt")
    print("Énoncé chargé avec succès:")
    print(description)
```

### Étape 3 : Création du prompt d'extraction

Créez un fichier `prompt_template.py` :

```python
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
```

### Étape 4 : Extraction avec LangChain

Créez un fichier `extract_problem.py` :

```python
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from models import OptimizationProblem
from load_data import load_problem_description
from prompt_template import create_extraction_prompt

# Charger les variables d'environnement
load_dotenv()

def extract_optimization_problem(problem_file: str = "problem_description.txt") -> OptimizationProblem:
    """
    Extrait la structure du problème d'optimisation depuis un énoncé en langage naturel

    Args:
        problem_file: Chemin vers le fichier contenant l'énoncé

    Returns:
        Objet OptimizationProblem contenant toute la structure extraite
    """
    # 1. Charger l'énoncé
    print("Chargement de l'énoncé du problème...")
    problem_description = load_problem_description(problem_file)

    # 2. Créer le prompt d'extraction
    print("Création du prompt d'extraction...")
    prompt = create_extraction_prompt(problem_description)

    # 3. Initialiser le LLM avec structured output
    print("Initialisation du LLM...")
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 4. Créer un LLM structuré avec le schéma Pydantic
    structured_llm = llm.with_structured_output(OptimizationProblem)

    # 5. Extraire la structure du problème
    print("Extraction de la structure du problème...")
    problem = structured_llm.invoke(prompt)

    print("Structure extraite avec succès!")
    return problem

def save_problem_to_json(problem: OptimizationProblem, output_file: str = "problem_structure.json"):
    """
    Sauvegarde la structure du problème dans un fichier JSON

    Args:
        problem: Objet OptimizationProblem à sauvegarder
        output_file: Nom du fichier de sortie
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(problem.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"Structure sauvegardée dans {output_file}")

if __name__ == "__main__":
    # Extraire la structure du problème
    problem = extract_optimization_problem()

    # Afficher le résultat
    print("\n" + "="*60)
    print("STRUCTURE DU PROBLÈME D'OPTIMISATION EXTRAITE")
    print("="*60)

    print(f"\nProblème : {problem.problem_name}")

    print(f"\nEnseignants ({len(problem.teachers)}) :")
    for teacher in problem.teachers:
        print(f"  - {teacher.name} : {teacher.subject}, {teacher.hours_per_week}h/semaine")
        print(f"    Disponibilités : {', '.join(teacher.available_days)}")

    print(f"\nVariables de décision ({len(problem.variables)}) :")
    for var in problem.variables:
        print(f"  - {var.name} ({var.type})")
        print(f"    {var.description}")

    print(f"\nContraintes ({len(problem.constraints)}) :")
    for constraint in problem.constraints:
        print(f"  [{constraint.id}] ({constraint.type}) {constraint.description}")

    print(f"\nObjectif ({problem.objective.type}) :")
    print(f"  {problem.objective.description}")

    # Sauvegarder dans un fichier JSON
    save_problem_to_json(problem)

    print("\n" + "="*60)
    print("Le fichier JSON peut maintenant être utilisé avec un solveur d'optimisation (OR-Tools, Gurobi, etc.)")
    print("="*60)
```

### Étape 5 : Exécution du projet

```bash
# Exécuter le script d'extraction
python extract_problem.py
```

---

## Exemple de sortie attendue

Le fichier `problem_structure.json` généré devrait ressembler à :

```json
{
  "problem_name": "Planification d'emploi du temps - Le Campus",
  "teachers": [
    {
      "name": "Alice Martin",
      "subject": "Mathématiques",
      "hours_per_week": 6,
      "available_days": ["Lundi", "Mercredi", "Vendredi"]
    },
    {
      "name": "Bob Dupont",
      "subject": "Physique",
      "hours_per_week": 4,
      "available_days": ["Mardi", "Jeudi"]
    }
  ],
  "variables": [
    {
      "name": "x[teacher, day, period]",
      "description": "Variable binaire: 1 si l'enseignant 'teacher' enseigne le jour 'day' pendant la période 'period' (matin/après-midi), 0 sinon",
      "type": "binary"
    }
  ],
  "constraints": [
    {
      "id": 1,
      "description": "Chaque enseignant ne peut donner qu'une seule matière par jour",
      "type": "hard"
    },
    {
      "id": 2,
      "description": "Chaque matière doit atteindre le nombre total d'heures assigné sur la semaine",
      "type": "hard"
    },
    {
      "id": 3,
      "description": "Un enseignant ne peut enseigner que les jours où il est disponible",
      "type": "hard"
    },
    {
      "id": 4,
      "description": "Répartir équitablement les heures sur les jours disponibles",
      "type": "soft"
    }
  ],
  "objective": {
    "description": "Minimiser les écarts de répartition des heures entre les jours pour chaque enseignant",
    "type": "minimize"
  }
}
```

---

## Validation de l'extraction

Créez un fichier `validate_extraction.py` pour vérifier la qualité de l'extraction :

```python
import json
from models import OptimizationProblem

def validate_problem_structure(problem: OptimizationProblem):
    """
    Valide que la structure extraite est complète et cohérente
    """
    print("\nValidation de la structure extraite...\n")

    errors = []
    warnings = []

    # Vérifier qu'il y a au moins un enseignant
    if len(problem.teachers) == 0:
        errors.append("Aucun enseignant extrait")
    else:
        print(f"[OK] {len(problem.teachers)} enseignants extraits")

    # Vérifier qu'il y a au moins une variable de décision
    if len(problem.variables) == 0:
        errors.append("Aucune variable de décision définie")
    else:
        print(f"[OK] {len(problem.variables)} variables de décision définies")

    # Vérifier qu'il y a des contraintes
    if len(problem.constraints) == 0:
        warnings.append("Aucune contrainte définie")
    else:
        hard_constraints = [c for c in problem.constraints if c.type == "hard"]
        soft_constraints = [c for c in problem.constraints if c.type == "soft"]
        print(f"[OK] {len(problem.constraints)} contraintes ({len(hard_constraints)} hard, {len(soft_constraints)} soft)")

    # Vérifier l'objectif
    if problem.objective.type not in ["minimize", "maximize"]:
        errors.append(f"Type d'objectif invalide: {problem.objective.type}")
    else:
        print(f"[OK] Objectif : {problem.objective.type}")

    # Vérifier les types de variables
    valid_var_types = ["binary", "integer", "continuous"]
    for var in problem.variables:
        if var.type not in valid_var_types:
            errors.append(f"Type de variable invalide pour {var.name}: {var.type}")

    # Afficher le résumé
    print("\n" + "="*60)
    if errors:
        print("ERREURS DÉTECTÉES:")
        for error in errors:
            print(f"  [ERREUR] {error}")

    if warnings:
        print("\nAVERTISSEMENTS:")
        for warning in warnings:
            print(f"  [ATTENTION] {warning}")

    if not errors and not warnings:
        print("[OK] Structure valide et complète!")
    elif not errors:
        print("[OK] Structure valide (avec avertissements)")
    else:
        print("[ERREUR] Structure invalide")
    print("="*60)

if __name__ == "__main__":
    with open("problem_structure.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    problem = OptimizationProblem(**data)
    validate_problem_structure(problem)
```

---

## Points d'apprentissage

1. **Document Loaders** : Chargement et traitement de texte non structuré
2. **Prompt Engineering** : Conception de prompts pour l'extraction d'informations structurées
3. **Pydantic** : Validation et typage de données complexes
4. **Structured Output** : Utilisation de `with_structured_output` pour garantir un format JSON valide
5. **Modélisation de problèmes d'optimisation** : Distinction variables/contraintes/objectif
6. **Préparation de données** : Structuration pour utilisation par un solveur

---

## Utilisation future

Le fichier JSON généré pourra être utilisé dans un prochain atelier pour :

- Implémenter le modèle d'optimisation avec OR-Tools
- Résoudre le problème avec un solveur
- Comparer différentes approches de résolution
- Visualiser les solutions obtenues

---

## Troubleshooting

**Erreur : Module not found**

```bash
pip install --upgrade langchain langchain-openai pydantic python-dotenv
```

**Erreur : OpenAI API Key**

- Vérifiez que votre fichier `.env` contient `OPENAI_API_KEY=...`
- Assurez-vous que la clé est valide

**L'extraction est incomplète**

- Améliorez le prompt en étant plus explicite sur les informations à extraire
- Ajoutez des exemples dans le prompt
- Utilisez un modèle plus performant (gpt-4 au lieu de gpt-4o-mini)

**Les contraintes ne sont pas bien catégorisées (hard/soft)**

- Précisez mieux dans l'énoncé quelles contraintes sont obligatoires
- Ajoutez des mots-clés dans le prompt ("obligatoire", "souhaitable", etc.)

---

## Ressources supplémentaires

- [Documentation LangChain](https://python.langchain.com/)
- [Documentation Pydantic](https://docs.pydantic.dev/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [OR-Tools Documentation](https://developers.google.com/optimization) (pour la suite)

---

## Critères de réussite

- [ ] L'énoncé du problème est correctement chargé
- [ ] Le schéma Pydantic valide la structure extraite
- [ ] Toutes les variables de décision sont identifiées
- [ ] Toutes les contraintes sont extraites et catégorisées (hard/soft)
- [ ] La fonction objectif est clairement définie
- [ ] Le fichier JSON est bien formé et exploitable
- [ ] La validation ne retourne aucune erreur

Bon courage !
