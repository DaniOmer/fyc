import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from models import OptimizationProblem
from load_data import load_problem_description
from prompt_template import create_extraction_prompt

# Charger les variables d'environnement
load_dotenv()

def extract_optimization_problem(problem_file: str = "teachers_data.txt") -> OptimizationProblem:
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