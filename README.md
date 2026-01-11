# 🧠 Retention AI API

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Available-2496ED.svg)
![Machine Learning](https://img.shields.io/badge/AI-Scikit--Learn-orange.svg)

> **Moteur intelligent d'aide à la décision RH combinant prédiction et prescription.**

## 🔗 Interface Utilisateur
Ce backend alimente le tableau de bord RH disponible ici :
👉 **[Retention-Decision-Dashboard](https://github.com/moubarak1ezzyani/Retention-Decision-Dashboard.git)**

**Retention AI API** est une application fullstack d’aide à la décision pour les départements Ressources Humaines. Elle combine l'apprentissage supervisé (Machine Learning) pour prédire le risque de démission d'un employé et l'IA générative pour proposer des plans de rétention personnalisés.

---

## 📋 Contexte du Projet

Les directions RH font face à un coût élevé lié au turnover. Ce projet vise à passer d'une analyse *a posteriori* à une approche **prédictive** et **prescriptive**.

**Objectifs principaux :**
1.  **Prédire** : Estimer la probabilité de départ d'un collaborateur (Churn Prediction).
2.  **Agir** : Générer automatiquement un plan d'action personnalisé via une IA Générative (LLM).
3.  **Industrialiser** : Exposer ces modèles via une API sécurisée et conteneurisée.

---

## 🛠️ Architecture & Technologies

### Backend & API
* **Langage** : Python
* **Framework** : FastAPI (Asynchrone, Rapide)
* **Sécurité** : Authentification JWT (JSON Web Tokens)
* **Base de données** : PostgreSQL (Stockage utilisateurs & historique des prédictions)
* **ORM** : SQLAlchemy (Interaction DB)

### Data Science & ML
* **Exploration** : Pandas, Seaborn
* **Preprocessing** : Scikit-learn (StandardScaler, OneHotEncoder)
* **Modélisation** : RandomForestClassifier & LogisticRegression
* **IA Générative** : Intégration API (Gemini / HuggingFace) pour la génération de texte.

### DevOps
* **Conteneurisation** : Docker & Docker Compose
* **Tests** : Pytest (Unitaires & Mocks)

---

## 📂 Structure du Projet

Voici l'arborescence du dépôt backend :

```text
RetentionAI-Backend/
├── app/                        # Cœur de l'application API
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── models.py               # Modèles de base de données (SQLAlchemy)
│   ├── schemas.py              # Schémas Pydantic (Validation des données)
│   ├── crud.py                 # Opérations Create, Read, Update, Delete
│   ├── database.py             # Configuration de la connexion PostgreSQL
│   ├── security.py             # Gestion des tokens JWT et Hashage
│   └── services.py             # Logique métier (appel ML, appel LLM)
│
├── ml_dev/                     # Environnement de développement ML
│   ├── data/                   # Dataset brut (RetentionAI.csv)
│   ├── src/                    # Scripts d'exploration
│   └── lab.ipynb               # Notebook Jupyter (EDA, Entraînement)
│
├── models/                     # Artefacts ML sérialisés (Production)
│   ├── attrition_model.pkl     # Le modèle prédictif final
│   ├── scaler_attrition.pkl    # Pour la normalisation
│   └── colonnes_modele.pkl     # Liste des features attendues
│
├── tests/                      # Tests automatisés
│   └── test_main.py            # Tests des endpoints API
│
├── Dockerfile                  # Instructions de build image
├── docker-compose.yml          # Orchestration (API + DB)
├── requirements.txt            # Dépendances Python
└── README.md                   # Documentation

```

---

## 🚀 Installation et Démarrage

### Pré-requis

* Docker & Docker Compose (Recommandé)
* **OU** Python 3.9+ et PostgreSQL installé localement.

### Option 1 : Démarrage rapide avec Docker (Recommandé)

1. **Cloner le dépôt**
```bash
git clone [https://github.com/votre-username/RetentionAI.git](https://github.com/votre-username/RetentionAI.git)
cd RetentionAI

```


2. **Configurer les variables d'environnement**
Créez un fichier `.env` à la racine :
```env
DATABASE_URL=postgresql://user:password@db:5432/retention_db
SECRET_KEY=votre_cle_secrete_jwt
ALGORITHM=HS256
GENAI_API_KEY=votre_api_key_gemini_ou_hf

```


3. **Lancer les services**
```bash
docker-compose up --build

```


L'API sera accessible sur `http://localhost:8000`.

### Option 2 : Installation Manuelle (Local)

1. Créer un environnement virtuel :
```bash
python -m venv RHvenv
source RHvenv/bin/activate  # ou RHvenv\Scripts\activate sur Windows

```


2. Installer les dépendances :
```bash
pip install -r requirements.txt

```


3. Lancer le serveur :
```bash
uvicorn app.main:app --reload

```



---

## 🔌 Documentation de l'API

Une fois l'application lancée, la documentation interactive Swagger est disponible sur :
👉 **http://localhost:8000/docs**

### Endpoints Clés

#### 1. Authentification

* `POST /register` : Créer un compte Manager RH.
* `POST /login` : Obtenir un **Access Token**.

#### 2. Prédiction (Machine Learning)

* `POST /predict` (Protégé JWT)
* **Input** : Données de l'employé (Age, Dept, JobRole, Satisfaction...)
* **Output** : `{"churn_probability": 0.78}`



#### 3. Rétention (IA Générative)

* `POST /generate-retention-plan` (Protégé JWT)
* **Logique** : Si la probabilité > 50%, génère un plan.
* **Output** : Suggestions concrètes (Télétravail, Formation, Augmentation...).



---

## 📊 Pipeline Machine Learning

Le modèle a été développé dans le dossier `ml_dev/` suivant ces étapes :

1. **Cleaning** : Suppression des variables à variance nulle (ex: Over18).
2. **Encoding** : `OneHotEncoding` pour les variables catégorielles (Department, JobRole) et `LabelEncoding` pour la cible.
3. **Scaling** : `StandardScaler` pour les variables numériques.
4. **Training** : Comparaison entre **Logistic Regression** et **Random Forest**.
* *Le modèle Random Forest a été retenu pour ses meilleures performances.*


5. **Export** : Sauvegarde via `joblib` dans le dossier `models/`.

---

## 🎯 Exemple de Résultat Attendu

Voici le flux typique d'une détection de risque de départ (Churn) :

### 1. Entrée (Données Employé)
Le manager RH envoie les données d'un employé via l'endpoint `/predict`.

```json
POST /predict
{
  "Age": 35,
  "Department": "Sales",
  "JobRole": "Sales Executive",
  "OverTime": "Yes",
  "MonthlyIncome": 4500,
  "EnvironmentSatisfaction": 1
  // ... autres champs
}

```

### 2. Sortie (Prédiction + Plan d'Action)

L'API détecte une probabilité élevée (**78%**) et déclenche automatiquement l'IA générative car le risque dépasse le seuil d'alerte (50%).

**Réponse JSON :**

```json
{
  "employee_id": "EMP-1024",
  "churn_probability": 0.78,
  "risk_level": "High",
  "suggested_retention_plan": [
    "✅ Proposer un aménagement hybride (2 jours de télétravail) pour compenser les heures supplémentaires.",
    "✅ Revoir la partie variable du salaire pour l'aligner sur la performance commerciale actuelle.",
    "✅ Organiser un point RH pour discuter des causes de l'insatisfaction environnementale."
  ]
}

```

> **Note :** Si la probabilité est inférieure à 50%, le champ `suggested_retention_plan` renverra `null` ou un message indiquant qu'aucune action immédiate n'est requise.


