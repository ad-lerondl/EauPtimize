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
    with open(file_path, 'r', encoding='utf-8') as file:
        solutions = json.load(file)
    return solutions


def calculate_resources(input_data):
    roof_area, num_residents, daily_shower_usage, location, is_garden = input_data['roof_area'], input_data['num_residents'], input_data['daily_shower_usage'], input_data['location'], input_data['garden']

    query = QtSql.QSqlQuery()
    query.prepare("SELECT Precipitation_Moyenne FROM Prec_Anuelles WHERE Ville = :location")
    query.bindValue(":location", location)
    rainfall = None
    if query.exec_():
        if query.next():
            rainfall = query.value(0)
    else:
        print("Erreur lors de l'exécution de la requête.")

    roof_water = roof_area * rainfall * 0.8 / 1000  # L'eau récupérée en litres
    shower_water = num_residents * daily_shower_usage * 365  # L'eau de douche récupérée en litres
    gray_water = shower_water > 0  # Hypothèse que les eaux grises sont disponibles si l'eau de douche est utilisée
    return {
        "roof_water": roof_water,
        "rainfall": rainfall > 500,  # Simplification pour une zone avec suffisamment de pluie
        "shower_water": shower_water,
        "gray_water": gray_water,
        "garden": is_garden
    }


def calculate_needs(input_data):
    num_toilets, num_residents, daily_toilet_usage, garden, daily_garden_watering = input_data['num_toilets'], input_data['num_residents'], input_data['daily_toilet_usage'], input_data['garden'], input_data['daily_garden_watering']

    toilet_water = num_toilets * num_residents * daily_toilet_usage * 365  # L'eau pour les toilettes en litres
    garden_water = daily_garden_watering * 365 if garden is True else 0  # L'eau pour le jardin en litres
    return {"toilet_water": toilet_water, "garden_water": garden_water}


def suggest_solutions(total_water_resources, total_water_needed, resources, needs):
    solutions = load_solutions()
    applicable_solutions = []

    for solution in solutions:
        conditions = solution["conditions"]
        applicable = True

        for key, value in conditions.items():
            if key not in resources or resources[key] != value:
                applicable = False
                break

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
    # Just an example of possible calculations
    water_cost_per_liter = 0.002  # Example cost in currency per liter
    total_cost_savings = total_water_resources * water_cost_per_liter
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
