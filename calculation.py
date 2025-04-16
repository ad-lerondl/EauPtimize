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

    # Ressource commune : eau récupérable via le toit (si surface_toit renseignée)
    roof_area = input_data.get('surface_toit', 0)
    catch_efficiency = constants.get("catch_efficiency", 0.8)
    resources["roof_water"] = roof_area * rainfall_mm * catch_efficiency  # en litres/an

    if building_type == "appartement":
        # Eau grise récupérable des douches
        num_residents = input_data.get("nb_habitants", 0)
        daily_shower_usage = constants.get("daily_shower_usage", 50)
        days_per_year = constants.get("days_per_year", 365)
        total_shower = num_residents * daily_shower_usage * days_per_year
        gray_recovery_shower = constants.get("gray_recovery_shower", 0.7)
        resources["grey_water_shower"] = total_shower * gray_recovery_shower

        # Eau grise récupérable des machines à laver dans les parties communes (si renseigné)
        parties_communes = input_data.get("parties_communes", {})
        nb_machines = parties_communes.get("nb_machine_a_laver", 0)
        laundry_usage = constants.get("laundry_water_usage", 50)
        total_laundry = nb_machines * laundry_usage * days_per_year
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
        # On peut également proposer l'eau récupérable sur toiture si le bâtiment possède une surface dédiée.
        # Dans certains bureaux, une "surface_toit" peut être renseignée.

    elif building_type == "maisons":
        # Pour une parcelle de maisons, on peut récupérer l'eau de pluie sur les toitures communes (si renseigné)
        # et l'eau grise issue de l'usage domestique.
        num_habitants = input_data.get("nb_habitants", 0)
        daily_usage_hab = constants.get("daily_shower_usage", 50)  # on réutilise la donnée en l'absence d'autre info
        days_per_year = constants.get("days_per_year", 365)
        total_domestic = num_habitants * daily_usage_hab * days_per_year
        resources["grey_water_domestic"] = total_domestic * constants.get("gray_recovery_shower", 0.7)

        # Si la parcelle dispose d'une réserve d'eau de pluie collective (champ dans equipements_communs)
        equip_communs = input_data.get("equipements_communs", {})
        if equip_communs.get("has_reserve_eau_pluie", False):
            # On peut considérer une capacité fixe de récupération (en litres/an) selon norme
            resources["reserve_eau_pluie"] = constants.get("reserve_capacity", 2000)
        else:
            resources["reserve_eau_pluie"] = 0

    elif building_type == "ecole":
        # Pour une école, on peut récupérer l'eau grise issue des douches installées dans les bâtiments,
        # ainsi qu'une partie de l'eau utilisée dans les cuisines si autorisée.
        batiments = input_data.get("batiment", [])
        total_surface = 0
        for bat in batiments if isinstance(batiments, list) else []:
            total_surface += bat.get("surface_totale", 0)
        # On estime un potentiel de récupération sur la base de la surface des toits des bâtiments scolaires.
        resources["roof_water"] = roof_area * rainfall_mm * catch_efficiency if roof_area else total_surface * 0.05  # hypothèse

        # Eau grise : on part du principe que le total des élèves et personnel passe sous douche dans certains bâtiments
        nb_eleves = input_data.get("nb_eleves", 0)
        nb_personnel = input_data.get("nb_personnel", 0)
        total_users = nb_eleves + nb_personnel
        total_shower = total_users * constants.get("daily_shower_usage", 50) * constants.get("days_per_year", 365)
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

    return resources


def get_rainfall_for_location(location):
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
        # Besoin en eau pour toilettes en parties communes et usages individuels.
        parties_communes = input_data.get("parties_communes", {})
        nb_toilettes_communes = parties_communes.get("nb_toilettes_communes", 0)
        toilet_usage = constants.get("toilet_usage", 3)
        toilet_uses = constants.get("toilet_uses_per_day", 5)
        needs["toilets"] = nb_toilettes_communes * toilet_usage * toilet_uses * days_per_year

        # Besoin pour l'arrosage du jardin (si renseigné)
        jardin_area = input_data.get("jardin", 0)
        # On considère ici une consommation (par exemple en L/an par are)
        usage_jardin = constants.get("usage_jardin", 100)
        needs["garden_irrigation"] = jardin_area * usage_jardin

    elif building_type == "bureaux":
        # Besoins en eau pour hygiène dans les parties communes (toilettes, kitchenettes)
        parties_communes = input_data.get("parties_communes", {})
        nb_toilettes = parties_communes.get("nb_toilettes", 0)
        toilet_usage = constants.get("toilet_usage", 3)
        toilet_uses = constants.get("toilet_uses_per_day", 5)
        needs["toilets"] = nb_toilettes * toilet_usage * toilet_uses * days_per_year

        kitchenettes = parties_communes.get("nb_cuisinettes", 0)
        # Consommation journalière estimée pour une kitchenette (pour boire, laver la vaisselle, etc.)
        usage_kitchenette = constants.get("usage_kitchenette_needs", 20)
        needs["kitchenettes"] = kitchenettes * usage_kitchenette * days_per_year

        # Besoin éventuel lié aux espaces extérieurs (par exemple, nettoyage ou arrosage d'espaces verts)
        espaces_ext = input_data.get("espaces_exterieurs", {})
        surface_ext = espaces_ext.get("surface_espace_vert", 0)
        usage_ext = constants.get("usage_ext_needs_per_are", 15)
        needs["external"] = surface_ext * usage_ext

    elif building_type == "maisons":
        # Pour les maisons, le besoin en eau porte sur la consommation domestique (toilettes, cuisine, douches)
        num_habitants = input_data.get("nb_habitants", 0)
        # Consommation potable moyenne par personne (L/jour)
        potable_usage = constants.get("potable_usage", 150)
        needs["domestic"] = num_habitants * potable_usage * days_per_year

        # Besoin pour les espaces extérieurs (jardins, piscines)
        ext = input_data.get("espaces_extérieurs", {})
        jardin_area = ext.get("surface_jardin_moyen", 0)
        usage_jardin = constants.get("usage_jardin", 100)
        needs["garden_irrigation"] = jardin_area * usage_jardin

        # Pour les équipements collectifs, on considère la consommation fixe
        equip_communs = input_data.get("equipements_communs", {})
        if equip_communs.get("has_laverie", False):
            needs["laverie"] = constants.get("laverie_needs", 5000)
        else:
            needs["laverie"] = 0

    elif building_type == "ecole":
        # Besoin en eau pour les établissements scolaires
        nb_eleves = input_data.get("nb_eleves", 0)
        nb_personnel = input_data.get("nb_personnel", 0)
        total_users = nb_eleves + nb_personnel
        potable_usage_ecole = constants.get("potable_usage_ecole", 40)
        needs["domestic"] = total_users * potable_usage_ecole * days_per_year

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
        needs["irrigation"] = (surface_gazon + surface_massifs) * usage_arrosage

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
            if key not in resources or resources[key] <= value:
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
