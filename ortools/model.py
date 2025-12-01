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

        Variables entières x[teacher, day, period]:
        - 0 si l'enseignant n'enseigne pas
        - 1 si l'enseignant enseigne 1 heure
        - 2 si l'enseignant enseigne 2 heures
        """
        print("\nCréation des variables de décision...")

        for teacher in self.teachers:
            for day in self.days:
                for period in self.periods:
                    var_name = f"{teacher}_{day}_{period}"
                    # Variable entière entre 0 et 2 (0h, 1h, ou 2h)
                    self.slots[(teacher, day, period)] = self.model.NewIntVar(0, 2, var_name)

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
            hours_needed = self.hours_required[teacher]

            # Somme de toutes les heures pour cet enseignant
            # Maintenant chaque slot vaut 0, 1 ou 2 heures directement
            hours_assigned = []
            for day in self.days:
                for period in self.periods:
                    hours_assigned.append(self.slots[(teacher, day, period)])

            # Contrainte d'égalité : total des heures doit être exactement celui requis
            self.model.Add(sum(hours_assigned) == hours_needed)

        print(f"      {len(self.teachers)} contraintes d'heures")

    def constraint_one_slot_per_day(self):
        """
        Contrainte: Chaque enseignant ne peut donner qu'une seule période par jour
        (soit matin, soit après-midi, pas les deux)
        """
        print("  [3] Contrainte une période maximum par jour...")

        count = 0
        for teacher in self.teachers:
            for day in self.days:
                # Au maximum 1 période par jour (matin OU après-midi)
                # On utilise des variables booléennes pour indiquer si une période est utilisée
                morning_used = self.model.NewBoolVar(f"{teacher}_{day}_morning_used")
                afternoon_used = self.model.NewBoolVar(f"{teacher}_{day}_afternoon_used")
                
                # morning_used = 1 si le créneau du matin > 0
                self.model.Add(self.slots[(teacher, day, "matin")] > 0).OnlyEnforceIf(morning_used)
                self.model.Add(self.slots[(teacher, day, "matin")] == 0).OnlyEnforceIf(morning_used.Not())
                
                # afternoon_used = 1 si le créneau de l'après-midi > 0
                self.model.Add(self.slots[(teacher, day, "après-midi")] > 0).OnlyEnforceIf(afternoon_used)
                self.model.Add(self.slots[(teacher, day, "après-midi")] == 0).OnlyEnforceIf(afternoon_used.Not())
                
                # Au plus une période utilisée par jour
                self.model.Add(morning_used + afternoon_used <= 1)
                count += 1

        print(f"      {count} contraintes jour/enseignant")

    def add_objective(self):
        """
        Fonction objectif: Maximiser l'utilisation des heures d'enseignement
        
        On cherche à assigner le maximum d'heures possible aux enseignants
        tout en respectant leurs disponibilités et les contraintes.
        """
        print("\nDéfinition de l'objectif...")
        
        objective_type = self.data['objective']['type']
        
        # Maximiser le nombre total d'heures assignées
        total_hours_assigned = []
        
        for teacher in self.teachers:
            available_days = self.availability[teacher]
            
            for day in available_days:
                for period in self.periods:
                    # Ajouter les heures de chaque slot (0, 1 ou 2 heures)
                    slot_var = self.slots[(teacher, day, period)]
                    total_hours_assigned.append(slot_var)
        
        # Maximiser le nombre total d'heures utilisées
        if objective_type == "maximize":
            self.model.Maximize(sum(total_hours_assigned))
            print("  Objectif défini: maximiser le nombre d'heures d'enseignement assignées")
        elif objective_type == "minimize":
            # Optionnel: garder l'ancienne logique de compacité si besoin
            self.model.Minimize(sum(total_hours_assigned))
            print("  Objectif défini: minimiser le nombre d'heures utilisées")

if __name__ == "__main__":
    # Test de création du modèle
    scheduling_model = SchedulingModel()
    print("\nModèle créé avec succès!")
    print(f"  Variables : {len(scheduling_model.slots)}")