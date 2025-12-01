import json
from tabulate import tabulate
from typing import Dict, List

def load_solution(solution_file: str = "solution.json") -> Dict:
    """Charge la solution depuis le fichier JSON"""
    with open(solution_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_weekly_grid(solution: Dict) -> Dict[str, Dict[str, str]]:
    """
    Crée une grille hebdomadaire du planning

    Returns:
        Dictionnaire {jour: {période: enseignant-matière-heures}}
    """
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    periods = ["matin", "après-midi"]

    # Initialiser la grille
    grid = {day: {period: "-" for period in periods} for day in days}

    # Remplir avec les créneaux
    for teacher_data in solution['teachers']:
        teacher_name = teacher_data['name'].split()[0]  # Prénom seulement
        subject = teacher_data['subject']

        for slot in teacher_data['time_slots']:
            day = slot['day']
            period = slot['period']
            hours = slot['hours']
            grid[day][period] = f"{teacher_name}\n{subject}\n({hours}h)"

    return grid

def display_grid_table(grid: Dict[str, Dict[str, str]]):
    """Affiche la grille sous forme de tableau"""

    print("\n" + "="*80)
    print("EMPLOI DU TEMPS GÉNÉRÉ")
    print("="*80)

    # Préparer les données pour tabulate
    table_data = []

    for day, periods in grid.items():
        row = [day, periods['matin'], periods['après-midi']]
        table_data.append(row)

    headers = ["Jour", "Matin (1-2h)", "Après-midi (1-2h)"]

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def display_teacher_schedules(solution: Dict):
    """Affiche le planning par enseignant"""

    print("\n" + "="*80)
    print("PLANNING PAR ENSEIGNANT")
    print("="*80)

    for teacher_data in solution['teachers']:
        print(f"\n{teacher_data['name']} - {teacher_data['subject']}")
        print(f"  Heures requises : {teacher_data['hours_required']}h")
        print(f"  Heures assignées : {teacher_data['total_hours_assigned']}h")
        print(f"  Créneaux :")

        for slot in teacher_data['time_slots']:
            print(f"    - {slot['day']} {slot['period']} ({slot['hours']}h)")

def validate_solution(solution: Dict) -> bool:
    """
    Valide que la solution respecte toutes les contraintes

    Returns:
        True si valide, False sinon
    """
    print("\n" + "="*80)
    print("VALIDATION DE LA SOLUTION")
    print("="*80)

    errors = []
    warnings = []

    # Vérifier que chaque enseignant a le bon nombre d'heures
    for teacher_data in solution['teachers']:
        required = teacher_data['hours_required']
        assigned = teacher_data['total_hours_assigned']

        if required != assigned:
            errors.append(
                f"{teacher_data['name']}: {assigned}h assignées au lieu de {required}h"
            )

    # Vérifier qu'il n'y a pas de doublons de jours
    for teacher_data in solution['teachers']:
        days_used = [slot['day'] for slot in teacher_data['time_slots']]
        if len(days_used) != len(set(days_used)):
            errors.append(
                f"{teacher_data['name']}: Plusieurs créneaux le même jour"
            )

    # Afficher les résultats
    if errors:
        print("\n[ERREUR] Contraintes violées :")
        for error in errors:
            print(f"  - {error}")
        return False

    if warnings:
        print("\n[ATTENTION] Avertissements :")
        for warning in warnings:
            print(f"  - {warning}")

    print("\n[OK] Solution valide!")
    return True

def export_to_csv(solution: Dict, output_file: str = "planning.csv"):
    """Exporte le planning au format CSV"""
    import csv

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Enseignant', 'Matière', 'Jour', 'Période', 'Heures'])

        for teacher_data in solution['teachers']:
            for slot in teacher_data['time_slots']:
                writer.writerow([
                    teacher_data['name'],
                    teacher_data['subject'],
                    slot['day'],
                    slot['period'],
                    slot['hours']
                ])

    print(f"\n[OK] Planning exporté dans {output_file}")

if __name__ == "__main__":
    # Charger la solution
    solution = load_solution()

    # Valider
    is_valid = validate_solution(solution)

    if is_valid:
        # Créer la grille
        grid = create_weekly_grid(solution)

        # Afficher
        display_grid_table(grid)
        display_teacher_schedules(solution)

        # Exporter en CSV
        export_to_csv(solution)