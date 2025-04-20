# -*- coding: utf-8 -*-
#
# Copyright (c) [2025] [Adam Lérondel]
#
# Licensed under the Fair Source License, Version 0.9.6 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.fair.io/license
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Created on Thu Dec 12 18:00:00 2024

@author: Adam Lérondel
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtSql
import sqlite3


def load_solutions(file_path='solutions.json'):
    with open(file_path, 'r', encoding='utf-8') as file:
        solutions = json.load(file)
    return solutions


def load_building_types(file_path='building_types.json'):
    with open(file_path, 'r', encoding='utf-8') as file:
        building_types = json.load(file)
    return building_types


def load_constants(file_path='constants.json'):
    with open(file_path, 'r', encoding='utf-8') as file:
        constants = json.load(file)
    return constants


def load_norms(file_path='normes.json'):
    with open(file_path, 'r', encoding='utf-8') as file:
        norms = json.load(file)
    return norms


def calculate_resources(input_data, building_type):
    """
    Calcule les ressources en eau exploitables (eaux récupérées ou récupérables) en fonction
    des données d'entrée et du type de bâtiment.

    Par exemple :
      - Pour un appartement : eau récupérable sur toit, eau grise récupérable des douches et de la laverie.
      - Pour un bureau ou une école, on utilisera uniquement les champs pertinents.

    Le calcul s'appuie également sur des constantes et éventuellement sur des normes (extraites de normes.json)
    pour définir quels usages peuvent être considérés comme ressources.
    """
    constants = load_constants()
    # On suppose que building_types est utilisé ailleurs pour contrôler le formulaire.
    building_types = load_building_types()
    if building_type not in building_types:
        raise ValueError("Type de bâtiment inconnu")

    # Récupérer les normes pour pouvoir décider des usages "ressources" (ici à titre d'information)
    norms = load_norms()

    # Récupération de la pluie depuis la localisation (si renseignée)
    location = input_data.get('location', '')
    rainfall_mm = get_rainfall_for_location(location)
    if rainfall_mm is None:
        rainfall_mm = constants.get("default_rainfall", 600)

    resources = {}

    resources["household"] = False
    resources["has_pool"] = False

    # Ressource commune : eau récupérable via le toit (si surface_toit renseignée)
    roof_area = input_data.get('surface_toit', 0)
    catch_efficiency = constants.get("catch_efficiency", 0.15)
    resources["roof_water"] = roof_area * rainfall_mm * 10e-3 * catch_efficiency * 10e3  # en litres/an

    if building_type == "appartement":
        resources["household"] = True
        # Eau grise récupérable des douches
        num_residents = input_data.get("nb_habitants", 0)
        daily_shower_usage = constants.get("daily_shower_usage", 50)
        days_per_year = constants.get("days_per_year", 365)
        total_shower = num_residents * daily_shower_usage * days_per_year/1.5
        resources["grey_water_shower"] = total_shower

        # Eau grise récupérable des machines à laver dans les parties communes (si renseigné)
        parties_communes = input_data.get("parties_communes", {})
        nb_machines = parties_communes.get("nb_machine_a_laver", 0)
        laundry_usage = constants.get("weekly_laundry_utilisation", 1)
        conso_machine_a_laver = constants.get("laundry_water_consumption", 60)
        total_laundry = laundry_usage * days_per_year/7 * num_residents * conso_machine_a_laver
        gray_recovery_machine = constants.get("gray_recovery_machine", 0.5)
        resources["grey_water_laundry"] = total_laundry * gray_recovery_machine

    elif building_type == "bureaux":
        # Pour un bureau, si la donnée "usage_eau_specifique" existe et comprend une quantité,
        # on considère que cette quantité représente un potentiel réutilisable (e.g. pour nettoyage non alimentaire).
        usage_specifique = input_data.get("usage_eau_specifique", {})
        if usage_specifique and isinstance(usage_specifique, dict):
            nb_unit = usage_specifique.get("nb_unites_specifiques", 0)
            quantity = usage_specifique.get("quantity", 0)
            resources["grey_water_specifique"] = nb_unit * quantity
        else:
            resources["grey_water_specifique"] = 0

    elif building_type == "maisons":
        resources["household"] = True
        num_habitants = input_data.get("nb_habitants", 4)
        num_maisons = input_data.get("nb_maisons", 1)
        daily_usage_hab = constants.get("daily_shower_usage", 50)
        days_per_year = constants.get("days_per_year", 365)
        nb_shower = input_data.get("nb_salles_de_bain", 1)
        total_domestic = num_habitants * daily_usage_hab * days_per_year/1.5 * constants.get("gray_recovery_shower", 0.7) * nb_shower
        resources["grey_water_domestic"] = total_domestic

        # Si la parcelle dispose d'une réserve d'eau de pluie collective (champ dans equipements_communs)
        equip_communs = input_data.get("equipements_communs", {})
        if equip_communs.get("has_reserve_eau_pluie", False):
            # On peut considérer une capacité fixe de récupération (en litres/an) selon norme
            resources["reserve_eau_pluie"] = constants.get("reserve_capacity", 2000)
        else:
            resources["reserve_eau_pluie"] = 0

        carac_maisons = input_data.get("caracteristiques_maisons", {})
        nb_maisons_type = carac_maisons.get("nb_maisons_concernees", 1)
        if carac_maisons.get("has_baignoire", False):
            resources["grey_water_domestic"] += num_habitants/num_maisons * daily_usage_hab * days_per_year/3 * constants.get("gray_recovery_shower", 0.7) * nb_shower

        nb_machines = carac_maisons.get("nb_machine_a_laver", 0)
        laundry_usage = constants.get("weekly_laundry_utilisation", 1)
        conso_machine_a_laver = constants.get("laundry_water_consumption", 60)
        total_laundry = laundry_usage * days_per_year/7 * num_habitants * conso_machine_a_laver
        gray_recovery_machine = constants.get("gray_recovery_machine", 0.5)
        resources["grey_water_laundry"] = total_laundry * gray_recovery_machine

        if carac_maisons.get("has_cuisine_exterieure", False):
            resources["water_cuisine_ext"] = constants.get("kitchen_water_consumption", 35) * days_per_year/4 * nb_maisons_type

        esp_ext = input_data.get("espaces_extérieurs", {})
        resources["has_pool"] = esp_ext.get("nb_piscines", 0) > 0

    elif building_type == "ecole":
        # Pour une école, on peut récupérer l'eau grise issue des douches installées dans les bâtiments,
        # ainsi qu'une partie de l'eau utilisée dans les cuisines si autorisée.
        batiments = input_data.get("batiment", [])
        total_surface = 0
        for bat in batiments if isinstance(batiments, list) else []:
            total_surface += bat.get("surface_totale", 0)
        # On estime un potentiel de récupération sur la base de la surface des toits des bâtiments scolaires.
        resources["roof_water"] = roof_area * rainfall_mm * catch_efficiency if roof_area else total_surface * 0.05  # hypothèse

        # Eau grise : on part du principe que le total des élèves et personnel se lavent les mains et remplissent leur gourde
        nb_eleves = input_data.get("nb_eleves", 0)
        nb_personnel = input_data.get("nb_personnel", 0)
        nb_internes = input_data.get("nb_internes", 0)
        total_users = nb_eleves + nb_personnel + nb_internes  # Les internes sont comptés une fois dans la journée et une autre fois dans la soirée
        total_shower = total_users * constants.get("daily_lavabo_usage", 2) * constants.get("days_per_year", 365)
        resources["grey_water_shower"] = total_shower * constants.get("gray_recovery_shower", 0.7)

    elif building_type == "espace_public":
        # Pour un espace public, la ressource exploitable peut être l'eau de pluie récupérable pour le nettoyage
        # des sols ou l'irrigation de certains espaces, par exemple.
        # Ici, on se limite à l'eau récupérable via une surface aménagée (si renseignée).
        resources["roof_water"] = roof_area * rainfall_mm * catch_efficiency
        # Si le système d'arrosage automatique est présent et que des systèmes de récupération existent,
        # on peut en déduire une capacité (valeur fixe par exemple).
        entretien = input_data.get("entretien", {})
        if entretien.get("source_eau", "") != "Réseau potable":
            resources["rainwater_system"] = 1000  # valeur indicative
        else:
            resources["rainwater_system"] = 0

    else:
        # Pour tout autre type (ou par défaut), on ne considère que la récupération sur toit.
        resources["default_resource"] = resources.get("roof_water", 0)

    resources["rainfall"] = True
    resources["gray_water"] = resources.get("gray_water_shower", 0) + resources.get("gray_water_laundry", 0) + resources.get("gray_water_domestic", 0) + resources.get("gray_water_specific", 0) > 0
    resources["garden"] = input_data.get("jardin", False)
    resources["space_available"] = True
    resources["construction_heavy"] = True

    return resources


def get_rainfall_for_location(location):
    try:
        conn = sqlite3.connect("pluviometrie_france.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Annuelles FROM pluviometrie_villes_France WHERE Villes = ?", (location,))
        pluvios = cursor.fetchall()
        conn.close()

        return pluvios[0][0]

    except Exception:
        return None


def calculate_needs(input_data, building_type):
    """
    Calcule les besoins en eau (consommation non récupérable) en fonction
    des données d'entrée et du type de bâtiment.

    Ces besoins concernent par exemple :
      - L'eau potable nécessaire pour l'hygiène (toilettes, cuisine, douches),
      - L'arrosage des espaces verts (jardins, terrains, etc.),
      - Le nettoyage (sols, surfaces intérieures ou extérieures).

    Les calculs s'appuient sur des constantes et sur les champs pertinents pour chaque type
    de bâtiment, sans tenter d'utiliser des données non applicables.
    """
    constants = load_constants()
    building_types = load_building_types()
    if building_type not in building_types:
        raise ValueError("Type de bâtiment inconnu")

    needs = {}
    days_per_year = constants.get("days_per_year", 365)

    if building_type == "appartement":
        # Eau grise pour les toilettes individuels
        num_residents = input_data.get("nb_habitants", 0)
        daily_toilet_usage = constants.get("daily_toilet_usage", 16)
        days_per_year = constants.get("days_per_year", 365)
        total_toilet = num_residents * daily_toilet_usage * days_per_year
        needs["toilet_water"] = total_toilet

        # Besoin en eau pour toilettes en parties communes
        parties_communes = input_data.get("parties_communes", {})
        nb_toilettes_communes = parties_communes.get("nb_toilettes_communes", 0)
        toilet_usage = constants.get("toilet_usage", 5)
        toilet_uses = constants.get("toilet_uses_per_day", 3)
        needs["toilet_water"] += nb_toilettes_communes * toilet_usage * toilet_uses * days_per_year

        # Besoin pour l'arrosage du jardin (si renseigné)
        jardin_area = input_data.get("jardin", 0)
        # On considère ici une consommation (par exemple en L/an par are), de 10L d'eau par m^2 sous 25° (moyenne entre un potager et un champ de fleurs)
        usage_jardin = constants.get("usage_jardin", 10) * days_per_year/3/2 * 100
        needs["garden_water"] = jardin_area * usage_jardin

    elif building_type == "bureaux":
        # Besoins en eau pour hygiène dans les parties communes (toilettes, kitchenettes)
        parties_communes = input_data.get("parties_communes", {})
        nb_toilettes = parties_communes.get("nb_toilettes", 0)
        toilet_usage = constants.get("toilet_usage", 3)
        toilet_uses = constants.get("toilet_uses_per_day", 5)
        needs["toilet_water"] = nb_toilettes * toilet_usage * toilet_uses * days_per_year

        kitchenettes = parties_communes.get("nb_cuisinettes", 0)
        # Consommation journalière estimée pour une kitchenette (pour boire, laver la vaisselle, etc.)
        usage_kitchenette = constants.get("usage_kitchenette_needs", 20)
        needs["kitchenettes_water"] = kitchenettes * usage_kitchenette * days_per_year

        # Besoin éventuel lié aux espaces extérieurs (par exemple, nettoyage ou arrosage d'espaces verts)
        espaces_ext = input_data.get("espaces_exterieurs", {})
        surface_ext = espaces_ext.get("surface_espace_vert", 0)
        usage_ext = constants.get("usage_ext_needs_per_are", 15)
        needs["garden_water"] = surface_ext
        needs["external_water"] = usage_ext

    elif building_type == "maisons":
        # Pour les maisons, le besoin en eau porte sur la consommation domestique (toilettes, cuisine, douches)
        num_habitants = input_data.get("nb_habitants", 0)
        # Consommation potable moyenne par personne (L/jour)
        potable_usage = constants.get("potable_usage", 250)
        needs["domestic_water"] = num_habitants * potable_usage * days_per_year
        needs["toilet_water"] = needs["domestic_water"] * 0.05

        # Besoin pour les espaces extérieurs (jardins, piscines)
        ext = input_data.get("espaces_extérieurs", {})
        jardin_area = ext.get("surface_jardin_moyen", 0)
        usage_jardin = constants.get("usage_jardin", 100)
        needs["garden_water"] = jardin_area * usage_jardin

        # Pour les équipements collectifs, on considère la consommation fixe
        equip_communs = input_data.get("equipements_communs", {})
        if equip_communs.get("has_laverie", False):
            needs["laundry_water"] = constants.get("laverie_needs", 5000)
        else:
            needs["laundry_water"] = 0

    elif building_type == "ecole":
        # Besoin en eau pour les établissements scolaires
        nb_eleves = input_data.get("nb_eleves", 0)
        nb_personnel = input_data.get("nb_personnel", 0)
        total_users = nb_eleves + nb_personnel
        potable_usage_ecole = constants.get("potable_usage_ecole", 40)
        needs["domestic_water"] = total_users * potable_usage_ecole * days_per_year
        needs["toilet_water"] = needs["domestic_water"] / 2

        # Besoin pour la restauration scolaire (cantine)
        batiments = input_data.get("batiment", [])
        cantine_usage = 0
        for bat in batiments if isinstance(batiments, list) else []:
            if bat.get("sanitaires", {}) and bat.get("cuisine_restauration", {}):
                nb_repas = bat.get("cuisine_restauration", {}).get("nb_repas_jour", 0)
                cantine_usage += nb_repas * constants.get("usage_cantine", 200) * days_per_year
        needs["cantine"] = cantine_usage

    elif building_type == "espace_public":
        # Pour un espace public, les besoins concernent principalement l'arrosage et le nettoyage.
        surface_totale = input_data.get("surface_totale", 0)
        # Consommation moyenne pour l'entretien (L/an par m² ou valeur fixée)
        usage_maintenance = constants.get("usage_entretien", 5)
        needs["maintenance"] = surface_totale * usage_maintenance

        # Besoin d'arrosage, calculé à partir des espaces verts
        espaces_verts = input_data.get("espaces_verts", {})
        surface_gazon = espaces_verts.get("surface_gazon", 0)
        surface_massifs = espaces_verts.get("surface_massifs_fleuris", 0)
        usage_arrosage = constants.get("usage_arrosage", 0.1)
        needs["garden_water"] = (surface_gazon + surface_massifs) * usage_arrosage

    else:
        # Valeur par défaut, si le type n'est pas géré, on ne calcule que le besoin pour l'eau de base.
        needs["default_needs"] = 0

    return needs


def suggest_solutions(total_water_resources, total_water_needed, resources, needs, building_type):
    solutions = load_solutions()
    applicable_solutions = []

    for solution in solutions:
        conditions = solution["conditions"]
        needs_covered = solution["covered_needs"]
        applicable = True

        for key, value in conditions.items():
            if key not in resources:
                applicable = False
                break

        for key, value in needs_covered.items():
            if key not in needs:
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
    constants = load_constants()
    total_cost_savings = total_water_resources * constants["water_cost_per_liter"]
    implementation_cost = sum(solution.get('implementation_cost', 0) for solution in solutions)

    return {
        "total_cost_savings": total_cost_savings,
        "implementation_cost": implementation_cost
    }


def viable_economic_solutions(solutions, savings):
    solu_viables = []
    cout_total = 0
    solutions = sorted(solutions, key=lambda x: x.get("implementation_cost", 0))
    for sol in solutions:
        cout_total += sol.get("implementation_cost", 0)
        if cout_total < savings["total_cost_savings"]*2:
            solu_viables.append(sol)
    return solu_viables


def plot_results(resources, needs, required_storage, savings):
    """
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
    """

    plt.figure(figsize=(10, 6))
    plt.bar(['Cost Savings', 'Implementation Cost'], [savings['total_cost_savings'], savings['implementation_cost']], color=['#2196f3', '#f44336'])
    plt.ylabel('Coût en €')
    plt.title('Cost Savings vs Implementation Cost')
    plt.savefig('cost_savings_vs_implementation_cost.png')
    plt.close()

    # Fusionner les deux dictionnaires pour avoir les mêmes clés
    all_keys = [nom for (nom, valeur) in resources.items() if type(valeur) is not bool] + [nom for (nom, valeur) in needs.items() if type(valeur) is not bool]
    all_keys = list(dict.fromkeys(all_keys))  # Supprimer les doublons tout en gardant l’ordre

    values_resources = [resources.get(k, 0) for k in all_keys]
    values_needs = [needs.get(k, 0) for k in all_keys]

    # Création de l'histogramme
    x = np.arange(len(all_keys))
    width = 0.35

    plt.figure(figsize=(12, 6))
    plt.bar(x - width / 2, values_resources, width, label='Ressources', color='#4db6ac')
    plt.bar(x + width / 2, values_needs, width, label='Besoins', color='#ff8a65')

    plt.ylabel('Volume (m^3)')
    plt.title('Ressources et besoins en eau')
    plt.xticks(x, [k.replace('_', ' ').capitalize() for k in all_keys], rotation=30, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Sauvegarde du graphique
    plt.savefig('water_resources_vs_needs.png')
    plt.close()
