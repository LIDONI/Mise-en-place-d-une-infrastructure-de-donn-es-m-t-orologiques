#  Mise en place d’une infrastructure de données météorologiques – Forecast 2.0

**Forecast 2.0** est un projet de **Data Engineering** réalisé pour **GreenCoop**, une entreprise spécialisée dans la gestion et la production d’énergie renouvelable.  
L’objectif est de fournir **quotidiennement des données météorologiques de qualité** aux Data Scientists afin d’améliorer leurs **modèles de prévision de la demande en électricité**.

En tant que **Data Engineer**, j’ai conçu et déployé un **pipeline complet** permettant d’intégrer, transformer, stocker et sécuriser des données issues de **plusieurs sources météorologiques** (stations officielles et amateurs).

---

##  Objectifs

- Intégrer de nouvelles sources de données météo *(InfoClimat, Weather Underground, etc.)*  
- Mettre en place une **infrastructure cloud scalable** *(AWS + Docker)*  
- Garantir la **qualité et la cohérence** des données stockées  
- Offrir une **connexion directe** pour les Data Scientists via MongoDB *(utilisé par SageMaker)*  

---

## Architecture du pipeline

Le pipeline de données **Forecast 2.0** se compose de plusieurs étapes :

### 1️⃣ Extraction – *Airbyte + S3*
- Connexion aux sources météo *(Excel, JSON)*  
- Chargement automatique dans un bucket **AWS S3**

### 2️⃣ Transformation – *Python*
- Nettoyage, typage et harmonisation des colonnes  
- Contrôles qualité *(valeurs manquantes, cohérence, doublons)*

### 3️⃣ Chargement – *MongoDB*
- Migration des données depuis **S3** vers **MongoDB**  
- Création de collections adaptées aux différents types de stations  
- Vérification automatique de la conformité post-migration

### 4️⃣ Conteneurisation & Déploiement – *Docker + AWS ECS*
- Conteneurisation du script Python et de MongoDB  
- Déploiement sur **Amazon ECS** avec monitoring via **CloudWatch**

---

## ⚙️ Stack technique

| Domaine | Outil / Service |
|----------|-----------------|
| **Extraction** | Airbyte |
| **Stockage intermédiaire** | AWS S3 |
| **Transformation** | Python *(pandas, boto3, pymongo)* |
| **Base de données** | MongoDB |
| **Conteneurisation** | Docker, Docker Compose |
| **Cloud** | AWS *(ECS, S3, CloudWatch)* |
| **Documentation** | Markdown, README, logigramme du pipeline |

---

##  Sécurité et bonnes pratiques

- Variables sensibles stockées dans un fichier **`.env`** *(non versionné)*  
- Authentification MongoDB via un utilisateur restreint **`forecast_writer`**  
- Connexions AWS sécurisées via **clés IAM**  
- Sauvegardes automatiques des données sur AWS  

---

##  Contrôle qualité

- Suppression des lignes incomplètes ou incohérentes  
- Vérification du schéma avant et après migration  
- Rapport automatique sur :
  - le taux de valeurs manquantes  
  - la correspondance des colonnes entre la source et MongoDB  

---

##  Résultats

- Pipeline **automatisé de bout en bout**  
- Temps d’accès moyen aux données : **< 2 secondes** pour une requête standard  
- Intégration fluide avec **SageMaker** pour les modèles de prévision  

---

##  Auteur

👤 **Khalid OURO-ADOYI**  
📧 khalidouroadoyi@gmail.com  

---


