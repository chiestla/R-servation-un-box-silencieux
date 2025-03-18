# 📚 Réservation de Boxes Silencieux 

## Description du projet  
Ce projet est une application web permettant aux étudiants de réserver des boxes silencieux dans une bibliothèque universitaire. Développé en **Python** avec **Django** et utilisant une base de données **SQLite**, il offre une solution pratique et sécurisée pour la gestion des réservations.

## Fonctionnalités  
✅ **Réservation en ligne** : Créneaux de 15 minutes, gestion des disponibilités en temps réel.  
✅ **Validation sécurisée** : Un code de confirmation est envoyé par email institutionnel.  
✅ **Restrictions de réservation** : Maximum **deux réservations par semaine** et **une réservation toutes les 24 heures**.  
✅ **Interface intuitive** : Affichage des créneaux disponibles sous forme de planning.  
✅ **Espace administrateur** : Gestion des réservations et réinitialisation des codes de confirmation.

## Technologies utilisées  
- **Backend** : Python (Django)  
- **Base de données** : SQLite  
- **Frontend** : HTML / CSS avec Django Templates  
- **Envoi d’emails** : Django EmailBackend  

## Installation 🚀  
1. **Cloner le projet**  
   ```bash
   git clone https://github.com/votre-repo.git
   cd votre-repo
   ```
2. **Créer un environnement virtuel et installer les dépendances**  
   ```bash
   python -m venv env
   source env/bin/activate  # Sur Windows : env\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Lancer le serveur Django**  
   ```bash
   python manage.py runserver
   ```

## Améliorations futures 🔮  
- 📩 **Rappels de réservation** par email  
- 📱 **Version mobile** pour une meilleure accessibilité  
- 📊 **Statistiques d’utilisation** pour optimiser les ressources  

💡 **Projet réalisé par** : *Doan Thi Mai Chi (Université Paris Nanterre - MIAGE 2024-2025)*  
