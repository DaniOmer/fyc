# Tutoriel : Ingénierie de Prompt pour l'Extraction d'Informations

Ce tutoriel se concentre sur **la rédaction d'un prompt efficace** pour extraire des informations structurées à partir de documents.

## Objectif de l'exercice

Apprendre à rédiger un prompt performant pour extraire la liste complète des membres du comité exécutif d'Apple à partir du document "Apple DEF 14A Statement" (PDF) et structurer les données au format JSON.

## Le Contexte de l'Exercice

**Document source** : Apple DEF 14A Statement (disponible sur le site de la SEC)

**Informations à extraire** pour chaque membre du comité exécutif :

- Nom
- Prénom(s)
- Âge
- Genre
- Rôle occupé dans l'entreprise
- Nationalité
- Adresse professionnelle

**Format de sortie attendu** : JSON structuré

```json
[
  {
    "nom": "Nom de famille",
    "prenom": "Prénom",
    "age": 0,
    "genre": "Homme/Femme/Autre",
    "role": "Intitulé du poste",
    "nationalite": "Nationalité",
    "adresse_professionnelle": "Adresse complète"
  }
]
```

---

## Les 5 Piliers d'un Prompt Robuste

Un prompt efficace repose sur cinq piliers fondamentaux. Chacun joue un rôle crucial dans la qualité de la réponse générée par le modèle.

### 1. Contexte (Context)

**Définition** : Le contexte définit le rôle, l'expertise et le domaine d'intervention de l'assistant IA.

**Pourquoi c'est important ?**

- Aide le modèle à adopter le bon "état d'esprit"
- Oriente le style et le ton de la réponse
- Cadre le domaine de connaissance à mobiliser

**Exemple :**

```
Vous êtes un assistant intelligent spécialisé dans l'extraction d'informations
à partir de documents officiels. Votre expertise porte sur l'analyse de
documents financiers et réglementaires d'entreprises cotées en bourse.
```

**Bonnes pratiques :**

- Soyez spécifique sur le domaine d'expertise
- Définissez clairement le rôle de l'assistant
- Utilisez un ton professionnel adapté à la tâche
- Évitez les rôles vagues comme "tu es un assistant utile"

---

### 2. Objectif (Objective)

**Définition** : L'objectif décrit précisément ce que le modèle doit accomplir.

**Pourquoi c'est important ?**

- Évite les ambiguïtés et les interprétations multiples
- Guide le modèle vers le résultat attendu
- Définit le périmètre de la tâche

**Exemple :**

```
Votre tâche est d'extraire la liste complète des membres du comité exécutif d'Apple
à partir du document fourni.

Pour chaque membre, vous devez récupérer :
- Le nom de famille
- Le(s) prénom(s)
- L'âge
- Le genre (Homme/Femme/Autre)
- Le rôle occupé dans l'entreprise
- La nationalité
- L'adresse professionnelle
```

**Bonnes pratiques :**

- Listez explicitement toutes les informations à extraire
- Soyez exhaustif dans la description de la tâche
- Utilisez des listes à puces pour la clarté
- Précisez ce qui doit être inclus ET exclu
- Évitez les objectifs trop larges ou imprécis

---

### 3. Instructions (Instructions)

**Définition** : Les instructions fournissent des directives étape par étape sur la manière de procéder.

**Pourquoi c'est important ?**

- Structure le raisonnement du modèle
- Garantit une approche méthodique
- Gère les cas particuliers et les erreurs
- Améliore la consistance des résultats

**Exemple :**

```
Instructions importantes :

1. Identifier tous les membres du comité exécutif mentionnés dans le document
2. Pour chaque membre identifié, extraire systématiquement toutes les informations demandées
3. Si une information est manquante ou non mentionnée, mettre la valeur null
4. Générer uniquement le JSON final, sans explications ni commentaires additionnels
5. Suivre exactement le schéma JSON fourni
6. Raisonner étape par étape :
   a) D'abord, identifier la section du document listant les membres
   b) Ensuite, pour chaque membre, extraire toutes les informations
   c) Enfin, construire le JSON final conformément au schéma
```

**Bonnes pratiques :**

- Numérotez les étapes pour plus de clarté
- Spécifiez le format de sortie attendu (JSON strict, sans commentaires)
- Guidez le raisonnement étape par étape (Chain of Thought)
- Précisez comment gérer les cas particuliers (données manquantes, ambiguïtés)
- Demandez au modèle de raisonner avant d'agir
- Évitez les instructions contradictoires
- Ne laissez pas de zones d'ombre

---

### 4. Schéma de sortie (Output Schema)

**Définition** : Le schéma de sortie explicite la structure exacte attendue pour la réponse (types, ordre des champs, valeurs par défaut).

**Pourquoi c'est important ?**

- Verrouille le format de sortie et réduit les divergences
- Facilite la validation automatique du résultat
- Aide le modèle à comprendre les contraintes de structure
- Rend l'évaluation des réponses plus objective

**Exemple :**

```
Le JSON doit suivre STRICTEMENT le schéma suivant :

[
  {
    "nom": "Nom de famille",
    "prenom": "Prénom",
    "age": 0,
    "genre": "Homme/Femme/Autre",
    "role": "Intitulé du poste",
    "nationalite": "Nationalité",
    "adresse_professionnelle": "Adresse complète"
  }
]
```

**Bonnes pratiques :**

- Représentez le schéma sous forme de JSON concret
- Précisez les types attendus (string, integer, null)
- Mentionnez les valeurs par défaut (ex. `null` si absent)
- Rappelez que le JSON doit être strict, sans texte additionnel
- Optionnel : ajouter une version compacte ET une version détaillée du schéma

---

### 5. Exemples (Few-Shot Learning)

**Définition** : Le few-shot learning consiste à fournir un ou plusieurs exemples concrets du résultat attendu.

**Pourquoi c'est important ?**

- Les exemples sont extrêmement puissants pour montrer le format exact
- Clarifient les attentes mieux que de longues explications
- Montrent comment gérer les cas particuliers
- Réduisent drastiquement les erreurs de format

**Exemple :**

```
Exemple de sortie attendue :

Texte extrait du document :
"Tim Cook, né en 1960, est le CEO d'Apple. Il est de nationalité américaine
et travaille au siège d'Apple, situé à 1 Apple Park Way, Cupertino, CA 95014."

Sortie JSON correspondante :
[
  {
    "nom": "Cook",
    "prenom": "Tim",
    "age": 65,
    "genre": "Homme",
    "role": "CEO",
    "nationalite": "Américain",
    "adresse_professionnelle": "1 Apple Park Way, Cupertino, CA 95014"
  }
]
```

**Bonnes pratiques :**

- Fournissez au moins 1 exemple complet et réaliste
- Montrez comment gérer les données manquantes (avec null)
- L'exemple doit être proche du cas d'usage réel
- Montrez le format exact attendu (indentation, structure)
- Si possible, donnez 2-3 exemples pour couvrir différents cas
- Évitez les exemples trop simplistes ou irréalistes

---

## Structure du Prompt à Compléter

Voici la structure que vous devez compléter dans le fichier `main.py` :

```
═══════════════════════════════════════════
CONTEXTE
═══════════════════════════════════════════
[À COMPLÉTER]
Définissez le rôle et l'expertise de l'assistant


═══════════════════════════════════════════
OBJECTIF
═══════════════════════════════════════════
[À COMPLÉTER]
Décrivez précisément la tâche à accomplir et les informations à extraire


═══════════════════════════════════════════
INSTRUCTIONS
═══════════════════════════════════════════
[À COMPLÉTER]
1. Première instruction...
2. Deuxième instruction...
3. ...


═══════════════════════════════════════════
SCHÉMA DE SORTIE
═══════════════════════════════════════════
[À COMPLÉTER]
Indiquez le JSON exact attendu (ordre des champs, types, valeurs null)


═══════════════════════════════════════════
EXEMPLE (Few-Shot Learning)
═══════════════════════════════════════════
[À COMPLÉTER]
Texte extrait du document :
"..."

Sortie JSON attendue :
[...]


═══════════════════════════════════════════
DOCUMENT À ANALYSER
═══════════════════════════════════════════
[ICI SERA INSÉRÉ LE CONTENU DU PDF]


═══════════════════════════════════════════
GÉNÉRATION
═══════════════════════════════════════════
Générez maintenant le JSON selon les instructions ci-dessus :
```

---

## Exercice Pratique : À Vous de Jouer !

### Étape 1 : Rédiger le Contexte

**Questions à vous poser :**

- Quel est le domaine d'expertise de l'assistant ?
- Quel type de documents va-t-il analyser ?
- Quelle est sa mission principale ?

**Conseils :**

- Soyez précis sur le domaine (documents financiers, réglementaires)
- Mentionnez l'expertise en extraction d'informations structurées

---

### Étape 2 : Définir l'Objectif

**Questions à vous poser :**

- Qu'est-ce qui doit être extrait exactement ?
- Quelles sont TOUTES les informations requises ?
- Quel format de sortie est attendu ?

**Conseils :**

- Listez exhaustivement les 7 champs à extraire
- Précisez qu'il s'agit des membres du comité exécutif
- Mentionnez le format JSON attendu

---

### Étape 3 : Rédiger les Instructions

**Questions à vous poser :**

- Comment le modèle doit-il procéder étape par étape ?
- Que faire si une information est manquante ?
- Quel format exact de sortie ?
- Comment gérer les ambiguïtés ?

**Conseils :**

- Numérotez les étapes (au moins 5-6 instructions)
- Incluez une instruction sur les données manquantes (→ null)
- Demandez de générer UNIQUEMENT le JSON, sans texte supplémentaire
- Guidez le raisonnement (Chain of Thought)

---

### Étape 4 : Définir le Schéma de Sortie

**Questions à vous poser :**

- Quelle structure JSON exacte exigez-vous ?
- Quel est l'ordre des champs et leurs types ?
- Comment représenter les valeurs manquantes ?

**Conseils :**

- Montrez un JSON complet avec les clés attendues
- Précisez les types (string, integer, null)
- Mentionnez explicitement les règles (JSON strict, pas de texte annexe)

---

### Étape 5 : Créer un Exemple (Few-Shot)

**Questions à vous poser :**

- Quel exemple serait représentatif du cas réel ?
- Comment montrer le format JSON exact ?
- Faut-il montrer un cas avec données manquantes ?

**Conseils :**

- Utilisez un exemple réaliste (peut-être Tim Cook)
- Montrez le texte source ET le JSON résultant
- Assurez-vous que le JSON est parfaitement formaté
- Si possible, ajoutez un 2e exemple avec un champ null

---

## Critères d'Évaluation

Votre prompt sera évalué sur :

| Critère        | Description                                                 | Points |
| -------------- | ----------------------------------------------------------- | ------ |
| **Clarté**     | Les instructions sont-elles claires et sans ambiguïté ?     | /5     |
| **Complétude** | Les 5 piliers sont-ils présents et bien développés ?        | /5     |
| **Structure**  | Le prompt est-il bien organisé et facile à suivre ?         | /5     |
| **Exemples**   | Les exemples sont-ils pertinents et bien formatés ?         | /5     |
| **Résultats**  | Le prompt produit-il un JSON valide avec toutes les infos ? | /5     |

**Score total : /25**

---

## Checklist Finale

Avant de considérer votre prompt comme terminé, vérifiez :

- [ ] Le contexte définit clairement le rôle de l'assistant
- [ ] L'objectif liste les 7 informations à extraire
- [ ] Les instructions sont numérotées et détaillées (min. 5 étapes)
- [ ] Une instruction gère les données manquantes (null)
- [ ] Une instruction demande UNIQUEMENT du JSON en sortie
- [ ] Le schéma de sortie est précisé et facile à suivre
- [ ] Un exemple complet est fourni avec texte source + JSON
- [ ] Le format JSON de l'exemple est correct
- [ ] Le prompt guide le raisonnement étape par étape (CoT)
- [ ] Le ton est professionnel et adapté

---

## Techniques Avancées (Bonus)

Une fois votre prompt de base maîtrisé, explorez ces techniques :

### Chain of Thought (CoT)

Demandez au modèle de raisonner étape par étape avant de répondre :

```
Avant de générer le JSON, raisonnez ainsi :
1. Identifier les sections pertinentes
2. Lister tous les noms trouvés
3. Pour chaque nom, extraire les infos
4. Construire le JSON final
```

### Self-Consistency

Générez plusieurs versions et comparez-les pour détecter les incohérences.

### Validation de Schéma

Demandez au modèle de valider lui-même sa sortie :

```
Après avoir généré le JSON, vérifiez :
- Tous les champs requis sont présents
- Le format JSON est valide
- Aucune information n'a été inventée
```

---

## Ressources Complémentaires

### Guides de Prompt Engineering

- [Prompt Engineering Guide](https://www.promptingguide.ai/) - Guide complet
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)

### Techniques Avancées

- **Chain of Thought (CoT)** : Raisonnement étape par étape
- **Few-Shot Learning** : Apprentissage par exemples
- **Zero-Shot CoT** : "Let's think step by step"
- **ReAct** : Raisonnement + Actions
- **Tree of Thoughts** : Exploration de multiples chemins

---

## Conseils Pro

### À FAIRE

- Être précis et explicite dans chaque section
- Utiliser des listes numérotées pour les instructions
- Fournir au moins 1 exemple réaliste et complet
- Demander un raisonnement étape par étape (CoT)
- Spécifier le format de sortie (JSON strict, sans commentaires)
- Gérer explicitement les cas particuliers (données manquantes)
- Tester et itérer votre prompt

### À ÉVITER

- Instructions vagues ou ambiguës
- Prompts trop courts sans contexte
- Oublier de donner des exemples concrets
- Ne pas spécifier le format de sortie exact
- Mélanger plusieurs tâches dans un seul prompt
- Instructions contradictoires
- Exemples trop simplistes ou irréalistes

---

**Bon courage !**

N'oubliez pas : un bon prompt est un prompt testé et itéré. Votre première version ne sera probablement pas parfaite, et c'est normal !
