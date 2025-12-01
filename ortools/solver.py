from ortools.sat.python import cp_model
from model import SchedulingModel
import json
from typing import Dict, List

class SchedulingSolver:
    """Résout le problème de planification et génère la solution"""

    def __init__(self, model: SchedulingModel):
        """
        Initialise le solver

        Args:
            model: Instance du modèle de planification
        """
        self.model_instance = model
        self.solver = cp_model.CpSolver()
        self.solution = None

    def solve(self, time_limit_seconds: int = 30) -> bool:
        """
        Résout le problème

        Args:
            time_limit_seconds: Limite de temps pour la résolution

        Returns:
            True si une solution a été trouvée, False sinon
        """
        print("\n" + "="*60)
        print("RÉSOLUTION DU PROBLÈME")
        print("="*60)

        # Configuration du solver
        self.solver.parameters.max_time_in_seconds = time_limit_seconds

        print(f"\nRecherche de solution (max {time_limit_seconds}s)...")

        # Résolution
        status = self.solver.Solve(self.model_instance.model)

        # Analyse du statut
        if status == cp_model.OPTIMAL:
            print("\n[SUCCÈS] Solution optimale trouvée!")
            return True
        elif status == cp_model.FEASIBLE:
            print("\n[SUCCÈS] Solution réalisable trouvée!")
            return True
        elif status == cp_model.INFEASIBLE:
            print("\n[ÉCHEC] Problème impossible à résoudre (contraintes incompatibles)")
            return False
        elif status == cp_model.MODEL_INVALID:
            print("\n[ERREUR] Modèle invalide")
            return False
        else:
            print("\n[ÉCHEC] Aucune solution trouvée dans le temps imparti")
            return False

    def extract_solution(self) -> Dict:
        """
        Extrait la solution du solver

        Returns:
            Dictionnaire contenant le planning pour chaque enseignant
        """
        if self.solver.StatusName() not in ['OPTIMAL', 'FEASIBLE']:
            return None

        print("\n" + "="*60)
        print("EXTRACTION DE LA SOLUTION")
        print("="*60)

        solution = {
            "problem_name": self.model_instance.data['problem_name'],
            "status": self.solver.StatusName(),
            "objective_value": self.solver.ObjectiveValue(),
            "solve_time_seconds": self.solver.WallTime(),
            "teachers": []
        }

        # Extraire les créneaux pour chaque enseignant
        for teacher in self.model_instance.teachers:
            teacher_schedule = {
                "name": teacher,
                "subject": self.model_instance.subjects[self.model_instance.teachers.index(teacher)],
                "hours_required": self.model_instance.hours_required[teacher],
                "time_slots": []
            }

            total_hours = 0

            for day in self.model_instance.days:
                for period in self.model_instance.periods:
                    var = self.model_instance.slots[(teacher, day, period)]
                    hours = self.solver.Value(var)

                    # Si des heures sont assignées à ce créneau (1h ou 2h)
                    if hours > 0:
                        teacher_schedule["time_slots"].append({
                            "day": day,
                            "period": period,
                            "hours": hours
                        })
                        total_hours += hours

            teacher_schedule["total_hours_assigned"] = total_hours
            solution["teachers"].append(teacher_schedule)

            print(f"\n{teacher} ({teacher_schedule['subject']}):")
            print(f"  Heures requises : {teacher_schedule['hours_required']}h")
            print(f"  Heures assignées : {total_hours}h")
            print(f"  Créneaux : {len(teacher_schedule['time_slots'])}")

        self.solution = solution
        return solution

    def save_solution(self, output_file: str = "solution.json"):
        """
        Sauvegarde la solution dans un fichier JSON

        Args:
            output_file: Nom du fichier de sortie
        """
        if self.solution is None:
            print("\n[ERREUR] Aucune solution à sauvegarder")
            return

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.solution, f, ensure_ascii=False, indent=2)

        print(f"\n[OK] Solution sauvegardée dans {output_file}")

    def print_statistics(self):
        """Affiche les statistiques de résolution"""
        print("\n" + "="*60)
        print("STATISTIQUES")
        print("="*60)
        print(f"Statut : {self.solver.StatusName()}")
        print(f"Valeur objectif : {self.solver.ObjectiveValue()}")
        print(f"Temps de résolution : {self.solver.WallTime():.3f}s")
        print(f"Branches explorées : {self.solver.NumBranches()}")
        print(f"Conflits : {self.solver.NumConflicts()}")
        print("="*60)

if __name__ == "__main__":
    # Créer le modèle
    model = SchedulingModel()

    # Créer le solver et résoudre
    solver = SchedulingSolver(model)

    if solver.solve(time_limit_seconds=30):
        # Extraire la solution
        solution = solver.extract_solution()

        # Sauvegarder
        solver.save_solution()

        # Statistiques
        solver.print_statistics()
    else:
        print("\nImpossible de trouver une solution.")