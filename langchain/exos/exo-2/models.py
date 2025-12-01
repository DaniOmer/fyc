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