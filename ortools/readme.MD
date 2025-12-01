# Atelier : Résolution d'un problème d'optimisation avec OR-Tools

## Description

Cet atelier vous guide dans la résolution d'un problème d'optimisation de planification d'emploi du temps en utilisant Google OR-Tools. Vous utiliserez le fichier JSON structuré généré par l'exercice LangChain (exo-2) contenant les variables, contraintes et objectif du problème.

**Prérequis** : Avoir complété l'exercice `langchain/exos/exo-2` pour générer le fichier `problem_structure.json`.

## Objectifs

- Charger et parser le fichier JSON généré par LangChain
- Modéliser le problème d'optimisation avec OR-Tools CP-SAT Solver
- Implémenter les variables de décision et les contraintes
- Résoudre le problème et générer l'emploi du temps optimal
- Exporter la solution au format JSON et visualiser le planning

---

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Fichier `problem_structure.json` généré par l'exercice LangChain

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
pip install ortools pandas tabulate
```

---

## Architecture du projet

```
ortools/
├── readme.MD                      # Ce fichier
├── problem_structure.json         # Fichier généré par LangChain (exo-2)
├── load_problem.py               # Chargement du JSON
├── model.py                      # Modélisation avec OR-Tools
├── solver.py                     # Résolution du problème
├── visualize.py                  # Visualisation du planning
└── solution.json                 # Solution générée
```

---

## Étapes de réalisation

### Étape 1 : Préparation des données

Copiez le fichier `problem_structure.json` généré par l'exercice LangChain dans ce dossier :

```bash
# Depuis la racine du projet
cp langchain/exos/exo-2/problem_structure.json ortools/
```

### Étape 2 : Chargement des données JSON

Créez un fichier `load_problem.py` :

```python
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
```

### Étape 3 : Modélisation avec OR-Tools

Créez un fichier `model.py` :

```python
from ortools.sat.python import cp_model
from load_problem import load_problem_data, extract_teachers_info
from typing import Dict, List

class SchedulingModel:
    """Modèle de planification d'emploi du temps avec OR-Tools"""

    def __init__(self, problem_file: str = "problem_structure.json"):
        """
        Initialise le modèle

        Args:
            problem_file: Chemin vers le fichier JSON du problème
        """
        # Charger les données
        self.data = load_problem_data(problem_file)
        self.teachers, self.subjects, self.hours_required, self.availability = \
            extract_teachers_info(self.data)

        # Définir les paramètres du problème
        self.days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        self.periods = ["matin", "après-midi"]
        self.hours_per_slot = 2  # Chaque créneau dure 2 heures

        # Créer le modèle CP-SAT
        self.model = cp_model.CpModel()

        # Variables de décision
        self.slots = {}
        self.create_variables()

        # Contraintes
        self.add_constraints()

        # Objectif
        self.add_objective()

    def create_variables(self):
        """
        Crée les variables de décision du modèle

        Variables booléennes x[teacher, day, period]:
        - 1 si l'enseignant enseigne ce jour à cette période
        - 0 sinon
        """
        print("\nCréation des variables de décision...")

        for teacher in self.teachers:
            for day in self.days:
                for period in self.periods:
                    var_name = f"{teacher}_{day}_{period}"
                    self.slots[(teacher, day, period)] = self.model.NewBoolVar(var_name)

        print(f"  {len(self.slots)} variables créées")

    def add_constraints(self):
        """Ajoute toutes les contraintes au modèle"""
        print("\nAjout des contraintes...")

        # Contrainte 1: Respecter les disponibilités
        self.constraint_availability()

        # Contrainte 2: Atteindre le nombre d'heures requis
        self.constraint_hours_required()

        # Contrainte 3: Maximum 1 créneau par jour par enseignant
        self.constraint_one_slot_per_day()

    def constraint_availability(self):
        """
        Contrainte: Un enseignant ne peut enseigner que les jours où il est disponible
        """
        print("  [1] Contrainte de disponibilité...")

        count = 0
        for teacher in self.teachers:
            available_days = self.availability[teacher]
            for day in self.days:
                if day not in available_days:
                    # Interdire tous les créneaux de ce jour
                    for period in self.periods:
                        self.model.Add(self.slots[(teacher, day, period)] == 0)
                        count += 1

        print(f"      {count} créneaux interdits")

    def constraint_hours_required(self):
        """
        Contrainte: Chaque enseignant doit atteindre exactement son nombre d'heures requis
        """
        print("  [2] Contrainte d'heures requises...")

        for teacher in self.teachers:
            total_slots_needed = self.hours_required[teacher] // self.hours_per_slot

            # Somme de tous les créneaux pour cet enseignant
            slots_assigned = []
            for day in self.days:
                for period in self.periods:
                    slots_assigned.append(self.slots[(teacher, day, period)])

            # Contrainte d'égalité
            self.model.Add(sum(slots_assigned) == total_slots_needed)

        print(f"      {len(self.teachers)} contraintes d'heures")

    def constraint_one_slot_per_day(self):
        """
        Contrainte: Chaque enseignant ne peut donner qu'un seul créneau par jour
        (soit matin, soit après-midi, pas les deux)
        """
        print("  [3] Contrainte un créneau maximum par jour...")

        count = 0
        for teacher in self.teachers:
            for day in self.days:
                # Au maximum 1 créneau par jour
                slots_in_day = [
                    self.slots[(teacher, day, period)]
                    for period in self.periods
                ]
                self.model.Add(sum(slots_in_day) <= 1)
                count += 1

        print(f"      {count} contraintes jour/enseignant")

    def add_objective(self):
        """
        Fonction objectif: Minimiser les écarts de répartition

        On cherche à répartir équitablement les créneaux sur les jours disponibles
        """
        print("\nDéfinition de l'objectif...")

        objective_type = self.data['objective']['type']
        print(f"  Type : {objective_type}")
        print(f"  Description : {self.data['objective']['description']}")

        # Pour cet exemple, on minimise le nombre de jours utilisés
        # (objectif de compacité)
        deviation_vars = []

        for teacher in self.teachers:
            available_days = self.availability[teacher]

            for day in available_days:
                # Variable binaire: 1 si le jour est utilisé pour cet enseignant
                day_used = self.model.NewBoolVar(f"used_{teacher}_{day}")

                # day_used = 1 si au moins un créneau est utilisé ce jour
                slots_in_day = [
                    self.slots[(teacher, day, period)]
                    for period in self.periods
                ]

                # Si sum(slots_in_day) > 0, alors day_used = 1
                self.model.Add(sum(slots_in_day) >= 1).OnlyEnforceIf(day_used)
                self.model.Add(sum(slots_in_day) == 0).OnlyEnforceIf(day_used.Not())

                deviation_vars.append(day_used)

        # Minimiser le nombre total de jours utilisés (compacité)
        if objective_type == "minimize":
            self.model.Minimize(sum(deviation_vars))

        print("  Objectif défini: minimiser le nombre de jours utilisés")

if __name__ == "__main__":
    # Test de création du modèle
    scheduling_model = SchedulingModel()
    print("\nModèle créé avec succès!")
    print(f"  Variables : {len(scheduling_model.slots)}")
```

### Étape 4 : Résolution du problème

Créez un fichier `solver.py` :

```python
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

                    if self.solver.Value(var) == 1:
                        teacher_schedule["time_slots"].append({
                            "day": day,
                            "period": period,
                            "hours": self.model_instance.hours_per_slot
                        })
                        total_hours += self.model_instance.hours_per_slot

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
```

### Étape 5 : Visualisation du planning

Créez un fichier `visualize.py` :

```python
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
        Dictionnaire {jour: {période: enseignant-matière}}
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
            grid[day][period] = f"{teacher_name}\n{subject}"

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

    headers = ["Jour", "Matin (2h)", "Après-midi (2h)"]

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
```

### Étape 6 : Script principal

Créez un fichier `main.py` qui orchestre tout :

```python
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
```

---

## Exécution du projet

### 1. Préparer les données

Assurez-vous d'avoir le fichier `problem_structure.json` :

```bash
# Copier depuis l'exercice LangChain
cp ../langchain/exos/exo-2/problem_structure.json .
```

### 2. Lancer le solver

```bash
python main.py
```

### 3. Fichiers générés

- `solution.json` : Solution complète avec tous les créneaux
- `planning.csv` : Export CSV pour Excel/Google Sheets

---

## Exemple de sortie

```
================================================================================
SOLVEUR DE PLANIFICATION D'EMPLOI DU TEMPS
Utilisation de Google OR-Tools CP-SAT Solver
================================================================================

[1/4] Création du modèle...
Problème chargé : Planification d'emploi du temps - Le Campus
- 5 enseignants
- 1 types de variables
- 5 contraintes
- Objectif : minimize

Création des variables de décision...
  50 variables créées

Ajout des contraintes...
  [1] Contrainte de disponibilité...
      20 créneaux interdits
  [2] Contrainte d'heures requises...
      5 contraintes d'heures
  [3] Contrainte un créneau maximum par jour...
      25 contraintes jour/enseignant

[2/4] Résolution du problème...

Recherche de solution (max 30s)...

[SUCCÈS] Solution optimale trouvée!

[3/4] Extraction de la solution...

Alice Martin (Mathématiques):
  Heures requises : 6h
  Heures assignées : 6h
  Créneaux : 3

...

[4/4] Visualisation de la solution...

================================================================================
EMPLOI DU TEMPS GÉNÉRÉ
================================================================================
+-----------+------------------+------------------+
| Jour      | Matin (2h)       | Après-midi (2h)  |
+===========+==================+==================+
| Lundi     | Alice            | Claire           |
|           | Mathématiques    | Français         |
+-----------+------------------+------------------+
| Mardi     | Claire           | Bob              |
|           | Français         | Physique         |
+-----------+------------------+------------------+
...
```

---

## Points d'apprentissage

1. **Modélisation avec CP-SAT** : Utilisation du solveur de contraintes de Google OR-Tools
2. **Variables booléennes** : Modélisation de décisions binaires (oui/non)
3. **Contraintes linéaires** : Implémentation de contraintes hard et soft
4. **Fonction objectif** : Optimisation d'un critère (minimisation/maximisation)
5. **Extraction de solution** : Récupération des valeurs des variables
6. **Intégration JSON** : Utilisation de données structurées en entrée/sortie
7. **Validation** : Vérification de la cohérence de la solution

---

## Troubleshooting

**Erreur : Module 'ortools' not found**

```bash
pip install --upgrade ortools
```

**Erreur : Fichier problem_structure.json introuvable**

- Vérifiez que vous avez bien copié le fichier depuis l'exercice LangChain
- Vérifiez le chemin du fichier

**Le solver ne trouve pas de solution (INFEASIBLE)**

- Vérifiez que les contraintes ne sont pas contradictoires
- Augmentez la limite de temps : `solver.solve(time_limit_seconds=60)`
- Vérifiez les heures requises vs disponibilités (par exemple, 6h requises avec seulement 2 jours disponibles)

**La solution ne respecte pas les contraintes**

- Vérifiez l'implémentation des contraintes dans `model.py`
- Utilisez la fonction `validate_solution()` pour identifier les problèmes

---

## Ressources supplémentaires

- [Documentation OR-Tools](https://developers.google.com/optimization)
- [Guide CP-SAT Solver](https://developers.google.com/optimization/cp/cp_solver)
- [Exemples de problèmes](https://github.com/google/or-tools/tree/stable/examples/python)

---

## Extension possible

- Ajouter des contraintes de préférence (soft constraints)
- Gérer plusieurs classes/groupes d'étudiants
- Optimiser l'utilisation des salles
- Ajouter des contraintes de pause entre les cours
- Générer plusieurs solutions alternatives
- Visualisation graphique avec matplotlib
- API REST pour exposer le solver
