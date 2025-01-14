# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 18:00:00 2024

@author: adaml
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtSql


def load_solutions(file_path='solutions.json'):
    """


    Parameters
    ----------
    file_path : str, optional
        Chemin relatif du fichier contenant les solutions disponibles. The default is 'solutions.json'.

    Returns
    -------
    solutions : list
        Liste de dicos imbriqués (suivant la logique inscrite dans le fichier json) contenant les paramètres de chaque solutions.

    """
    with open(file_path, 'r', encoding='utf-8') as file:
        solutions = json.load(file)
    return solutions


def calculate_resources(input_data):
    """
    Calcule les ressources à disposition selon les données brutes fournies. Exple : on fourni le nombre de douches et on retourne la quantité dispo correspondante.

    Parameters
    ----------
    input_data : dict
        Données brutes d'entrée.

    Returns
    -------
    dict
        Données traitables. Exple : la quantité d'eau de douche dispo (plutôt que le nombre de douches qui ne sert 'à rien').

    """
    roof_area, num_residents, conso_hyg, location, is_garden = input_data['roof_area'], input_data['nb_habitants'], input_data['conso_hyg'], input_data['location'], input_data['surf_veg'] > 0

    # Définition de la quantité de pluie en allant chercher dans la base de données
    query = QtSql.QSqlQuery()
    query.prepare("SELECT Precipitation_Moyenne FROM Prec_Anuelles WHERE Ville = :location")
    query.bindValue(":location", location)
    rainfall = None
    if query.exec_():
        if query.next():
            rainfall = query.value(0)
    else:
        print("Erreur lors de l'exécution de la requête.")

    # Calcul des ressources en fonction des variables récupérées
    # TODO mais plus tard c'est pas pressant : laisser la possibilité à l'utilisateur de modifier les constantes
    # TODO mais plus tard : définir des constantes types daily_shower_usage, éventuellement fonction du pourcentage d'hygiène, etc.
    roof_water = roof_area * rainfall * 0.8 / 1000  # L'eau de pluie récupérée en litres
    shower_water = num_residents * conso_hyg*100 * 50 * 365  # Exemple de calcul, par exemple 100% d'hygiène correspond à une douche par jour de 50L d'eau
    gray_water_available = shower_water > 0

    # ATTENTION : le nom des clés du dico doit être harmonisé avec le nom des conditions des solutions existantes (cf fonction de tri des solutions)
    return {
        "roof_water": roof_water,
        "rainfall": rainfall > 500,  # Simplification pour une zone avec suffisamment de pluie
        "shower_water": shower_water,
        "gray_water": gray_water_available,
        "garden": is_garden
    }


def calculate_needs(input_data):
    """
    Calcule les besoins en eau selon les données brutes fournies. Exple : on fourni la surface de jardin et on retourne la quantité dont on a besoin pour arroser correspondante.

    Parameters
    ----------
    input_data : dict
        Dico contenant les données brutes.

    Returns
    -------
    dict
        Données traitables. Exple : l'eau qu'il faut pour arroser le jardin (plutôt que sa surface qui ne sert 'à rien')..

    """
    daily_garden_watering, daily_toilet_usage = 3, input_data["conso_hyg"]*100*15  # Exemple
    num_toilets, num_residents, garden = input_data['num_toilets'], input_data['nb_habitants'], input_data['surf_veg'] > 0

    # TODO mais plus tard il y a le tps : pouvoir modifier les constantes multipicatives
    toilet_water = num_toilets * num_residents * daily_toilet_usage * 365  # L'eau pour les toilettes en litres
    garden_water = daily_garden_watering * 365 if garden is True else 0  # L'eau pour le jardin en litres

    # ATTENTION : le nom des clés du dico doit être harmonisé avec le nom des conditions des solutions existantes (cf fonction de tri des solutions)
    return {"toilet_water": toilet_water, "garden_water": garden_water}


def suggest_solutions(total_water_resources, total_water_needed, resources, needs):
    """
    Tri des solutions existantes en fonction de si elles sont applicables au problème étudié.

    Parameters
    ----------
    total_water_resources : int
        Quantité d'eau totale à disposition.
    total_water_needed : int
        Quantité d'eau totale dont on a besoin.
    resources : dict
        Dico contenant les ressources (exploitables) à disposition.
    needs : dict
        Dico contenant les besoins en eau (exploitables).

    Returns
    -------
    applicable_solutions : list
        Liste des solutions (solutions au format dico : copie de certaines solutions existantes codées dans solutions.json).

    """
    solutions = load_solutions()
    applicable_solutions = []

    # Idée de la boucle de tri : on parcourt toutes les solutions, puis on regarde si on en a besoin et que c'est une solution qu'on peut mettre en place. Auquel cas on renseigne les parmètres de la solution (comme la taille d'une cuve par exemple : petit si pas beaucoup de pluie, grand sinon)
    # Parcours des solutions
    for solution in solutions:
        conditions = solution["conditions"]
        needs_covered = solution["covered_needs"]
        applicable = True

        # Vérification que la solution est applicable
        for key, value in conditions.items():
            if key not in resources or resources[key] <= value:
                applicable = False
                break
        # Vérification qu'on ait besoin de la solution
        for key, value in needs_covered.items():
            if key not in needs:
                applicable = False
                break

        # Mise à jour des paramètres de la solution, type taille de la cuve
        # TODO : le faire sous forme de boucle pour éviter les tests if ça fait moche
        if applicable:
            if "roof_water" in solution["parameters"] and resources["roof_water"]:
                solution["parameters"]["tank_capacity"] = resources["roof_water"]
            if "gray_water_usage" in solution["parameters"] and resources["gray_water"]:
                solution["parameters"]["gray_water_usage"] = resources["shower_water"]
            if "irrigation_requirement" in solution["parameters"] and needs["garden_water"]:
                solution["parameters"]["irrigation_requirement"] = needs["garden_water"]

            applicable_solutions.append(solution)

    return applicable_solutions


def calculate_savings(input_data, solutions, total_water_resources, total_water_needed, required_storage):
    """
    Calcule les économies réalisées

    Parameters
    ----------
    input_data : dict
        Données brutes d'entrée. (actuellement ça ne sert à rien mais ne pas supprimer car le main.py y est relié)
    solutions : list
        Liste des solutions envisagées (solutions au format dico comme d'hab).
    total_water_resources : int
        Eau à disposition.
    total_water_needed : int
        Eau dont on a besoin.
    required_storage : int
        Quantité d'eau qu'on a besoin de stocker. (assez naïf vu la définition donnée dans le main, mais c'est à titre d'exemple, il faudra juste modifier. Ne pas enlever donc)

    Returns
    -------
    dict
        Coûts économisés et coûts d'implémentation.

    """
    water_cost_per_liter = 0.002  # Valeur d'exemple, à modifier. TODO mais plus tard : permettre la redéfinition de cette constante
    total_cost_savings = total_water_resources * water_cost_per_liter  # Calcul simple et naïf qu'il faudra améliorer
    implementation_cost = sum(solution.get('implementation_cost', 0) for solution in solutions)

    return {
        "total_cost_savings": total_cost_savings,
        "implementation_cost": implementation_cost
    }


def plot_results(total_water_resources, total_water_needed, required_storage, savings):
    labels = ['Resources', 'Needs']
    sizes = [total_water_resources, total_water_needed]
    sizes = [0 if np.isnan(size) else size for size in sizes]
    colors = ['#8bc34a', '#ff9800']

    plt.figure(figsize=(10, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Water Resources vs Needs')
    plt.savefig('water_resources_vs_needs.png')
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.bar(['Cost Savings', 'Implementation Cost'], [savings['total_cost_savings'], savings['implementation_cost']], color=['#2196f3', '#f44336'])
    plt.title('Cost Savings vs Implementation Cost')
    plt.savefig('cost_savings_vs_implementation_cost.png')
    plt.close()
