from model import SchedulingModel
from solver import SchedulingSolver
from visualize import (
    load_solution,
    create_weekly_grid,
    display_grid_table,
    display_teacher_schedules,
    validate_solution,
    export_to_csv
)

def main():
    """Script principal pour résoudre le problème de planification"""

    print("="*80)
    print("SOLVEUR DE PLANIFICATION D'EMPLOI DU TEMPS")
    print("Utilisation de Google OR-Tools CP-SAT Solver")
    print("="*80)

    # Étape 1: Créer le modèle
    print("\n[1/4] Création du modèle...")
    model = SchedulingModel("problem_structure.json")

    # Étape 2: Résoudre
    print("\n[2/4] Résolution du problème...")
    solver = SchedulingSolver(model)

    success = solver.solve(time_limit_seconds=30)

    if not success:
        print("\n[ÉCHEC] Impossible de trouver une solution.")
        print("Vérifiez que les contraintes ne sont pas incompatibles.")
        return

    # Étape 3: Extraire et sauvegarder
    print("\n[3/4] Extraction de la solution...")
    solution = solver.extract_solution()
    solver.save_solution("solution.json")
    solver.print_statistics()

    # Étape 4: Visualiser
    print("\n[4/4] Visualisation de la solution...")

    # Valider
    is_valid = validate_solution(solution)

    if is_valid:
        # Afficher
        grid = create_weekly_grid(solution)
        display_grid_table(grid)
        display_teacher_schedules(solution)

        # Exporter
        export_to_csv(solution, "planning.csv")

        print("\n" + "="*80)
        print("[SUCCÈS] Planification terminée!")
        print("Fichiers générés :")
        print("  - solution.json : Solution complète au format JSON")
        print("  - planning.csv : Planning au format CSV")
        print("="*80)
    else:
        print("\n[ATTENTION] La solution contient des erreurs.")

if __name__ == "__main__":
    main()