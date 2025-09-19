from ortools.sat.python import cp_model

# 1. Modèle
model = cp_model.CpModel()

# 2. Variables
# Chaque cours est affecté à un créneau ∈ {0,1,2}
html   = model.NewIntVar(0, 2, "html")
javascript = model.NewIntVar(0, 2, "javascript")
python = model.NewIntVar(0, 2, "python")

# 3. Contraintes
# - Tous les cours doivent être à des créneaux différents
model.AddAllDifferent([html, javascript, python])

# - Javascript n'est pas le matin et après-midi (≠ 0 ≠ 1)
model.Add(javascript != 0)
# model.Add(javascript != 1)
# model.Add(javascript != 2)

# - Python n'est pas le matin et après-midi (≠ 0 && ≠ 1)
model.Add(python != 0)
model.Add(python != 1)

# 4. Solveur
solver = cp_model.CpSolver()
status = solver.Solve(model)

# 5. Affichage de la solution
if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
    print(f"La solution est {solver.status_name(status)}")
    print("HTML         -> créneau", solver.Value(html))
    print("Javascript   -> créneau", solver.Value(javascript))
    print("Python       -> créneau", solver.Value(python))
else:
    print(f"La solution n'est pas faisable. Le status est {solver.status_name(status)}")
