import json
from typing import Dict, List, Any

def load_problem_data(json_file: str = "problem_structure.json") -> Dict[str, Any]:
    """
    Charge le fichier JSON contenant la structure du problème

    Args:
        json_file: Chemin vers le fichier JSON

    Returns:
        Dictionnaire contenant les données du problème
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Problème chargé : {data['problem_name']}")
    print(f"- {len(data['teachers'])} enseignants")
    print(f"- {len(data['variables'])} types de variables")
    print(f"- {len(data['constraints'])} contraintes")
    print(f"- Objectif : {data['objective']['type']}")

    return data

def extract_teachers_info(data: Dict[str, Any]) -> tuple:
    """
    Extrait les informations des enseignants

    Returns:
        Tuple contenant (teachers_list, subjects, hours_required, availability)
    """
    teachers = data['teachers']

    teachers_list = [t['name'] for t in teachers]
    subjects = [t['subject'] for t in teachers]
    hours_required = {t['name']: t['hours_per_week'] for t in teachers}
    availability = {t['name']: t['available_days'] for t in teachers}

    return teachers_list, subjects, hours_required, availability

def extract_constraints_info(data: Dict[str, Any]) -> tuple:
    """
    Extrait les contraintes hard et soft

    Returns:
        Tuple contenant (hard_constraints, soft_constraints)
    """
    constraints = data['constraints']

    hard_constraints = [c for c in constraints if c['type'] == 'hard']
    soft_constraints = [c for c in constraints if c['type'] == 'soft']

    print(f"\nContraintes HARD ({len(hard_constraints)}) :")
    for c in hard_constraints:
        print(f"  [{c['id']}] {c['description']}")

    print(f"\nContraintes SOFT ({len(soft_constraints)}) :")
    for c in soft_constraints:
        print(f"  [{c['id']}] {c['description']}")

    return hard_constraints, soft_constraints

if __name__ == "__main__":
    # Test du chargement
    data = load_problem_data()
    teachers, subjects, hours, availability = extract_teachers_info(data)
    hard_const, soft_const = extract_constraints_info(data)

    print("\nDonnées extraites avec succès!")