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
    roof_area, num_residents, daily_shower_usage, precip, is_garden = input_data['roof_area'], input_data['num_residents'], input_data['daily_shower_usage'], input_data['precip'], input_data['surf_veg']

    
    nb_travail=input_data["nb_travail"]
    conso_travail=input_data["conso_travail"]
    roof_water = roof_area * precip * 0.8 / 1000  # L'eau récupérée en litres
    shower_water = num_residents * daily_shower_usage * 365  # L'eau de douche récupérée en litres
    gray_water = shower_water > 0  # Hypothèse que les eaux grises sont disponibles si l'eau de douche est utilisée
    return {
        "roof_water": roof_water,
        "rainfall": precip > 500,  # Simplification pour une zone avec suffisamment de pluie
        "shower_water": shower_water,
        "gray_water": gray_water,
        "garden": is_garden,
        
        
        
        "hab":num_residents*input_data['conso_hab']*365*(input_data["conso_hyg"]+input_data["conso_vet"]+input_data["conso_vai"])/100,
        "trav":conso_travail*nb_travail*365*input_data["conso_hyg_travail"]/100,
        "pluie":precip*input_data["surfpl"]
    }


def calculate_needs(input_data):
    conso_exc, num_residents, conso_hab,  surf_veg = input_data['conso_exc'], input_data['num_residents'], input_data['conso_hab'], input_data['surf_veg']
    conso_veg=input_data['conso_veg']
    conso_net_com=input_data['conso_net_com']
    surf_net=input_data['surf_net']
    nb_travail=input_data["nb_travail"]
    conso_travail=input_data["conso_travail"]
    toilet_water = conso_exc * num_residents * conso_hab* 365  # L'eau pour les toilettes en litres par an
    garden_water = surf_veg * conso_veg*365   # L'eau pour le jardin en litres
    return {"toilet_water": toilet_water, 'conso_tot_trav':conso_travail*nb_travail*365,"garden_water": garden_water,'conso_tot_hab':num_residents*conso_hab*365,'conso_tot_net':surf_net*conso_net_com*52}


def plot_results(water_resources,water_needed):
    labels = ['Consommation habitants', 'Consommation travailleurs','Nettoyage espaces communs','Arrosage surface végétalisée']
    sizes = water_needed
    # colors = ['#8bc34a', '#ff9800']
    plt.figure(figsize=(15, 9))
    plt.bar(["Total de la consommation d'eau [l/an]", 'Total des ressources en eaux grises disponibles [l/an]'], [sum(water_needed), sum(water_resources)], color=['#2196f3', '#f44336'])
    plt.title("Consommation total d'eau et ressources en eaux grises disponibles à la réutilisation")
    plt.savefig('Conso_eaux_grises.png')
    plt.close()

    plt.figure(figsize=(15, 9))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title("Détail des consommation d'eau")
    plt.savefig('Conso_eau.png')
    plt.close()
    
    plt.figure(figsize=(15, 9))
    plt.pie(water_resources, labels=["Eaux grises des habitants","Eaux grises des travailleurs","Eaux de pluie"], autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title("Détail des ressources en eaux grises disponibles")
    plt.savefig('Eau_grises.png')
    plt.close()



def suggest_solutions(input_data):
    solutions = load_solutions()
    applicable_solutions = []
    
    
    pluie=input_data["precip"]*input_data["surfpl"]
    recup_hyg=input_data['num_residents']*input_data['conso_hab']*365*input_data["conso_hyg"]/100+input_data['conso_travail']*input_data['nb_travail']*365*input_data["conso_hyg_travail"]/100
    recup_vet=input_data['num_residents']*input_data['conso_vet']*365*input_data["conso_hyg"]/100
    recup_vai=input_data['num_residents']*input_data['conso_vai']*365*input_data["conso_hyg"]/100
    pest=input_data["pest"]
    mic=input_data["mic"]
    
    
    
    cles={"pluie":pluie>0,
         "recup_hyg":recup_hyg>0,
         "recup_vet":recup_vet>0,
         "recup_vai":recup_vai>0,
         "pest":pest,
         "mic":mic
         }

    for solution in solutions:
        conditions = solution["conditions"]
        for cle in cles:
            if cles[cle] and cle in conditions:
                applicable_solutions.append(solution)
        

    return applicable_solutions


def calculate_savings(input_data):
    # Just an example of possible calculations
    
    
    pluie=input_data["precip"]*input_data["surfpl"]
    recup_hyg=input_data['num_residents']*input_data['conso_hab']*365*input_data["conso_hyg"]/100+input_data['conso_travail']*input_data['nb_travail']*365*input_data["conso_hyg_travail"]/100
    recup_vet=input_data['num_residents']*input_data['conso_vet']*365*input_data["conso_hyg"]/100
    recup_vai=input_data['num_residents']*input_data['conso_vai']*365*input_data["conso_hyg"]/100
    
    
    
    cles={"pluie":pluie>0,
         "recup_hyg":recup_hyg>0,
         "recup_vet":recup_vet>0,
         "recup_vai":recup_vai>0,
         }
    
    water_save={"pluie":0,
                "recup_hyg":0,
                "recup_vet":0,
                "recup_vai":0
                }
    if cles["pluie"]:
        water_save["pluie"]=input_data["precip"]*input_data["surfpl"]
    if cles["recup_hyg"]:
        water_save["recup_hyg"]=(input_data["num_residents"]*input_data["conso_hab"]*input_data["conso_hyg"]+input_data["nb_travail"]*input_data["conso_travail"]*input_data["conso_hyg_travail"])*3.65
    if cles["recup_vet"]:
        water_save["recup_vet"]=(input_data["num_residents"]*input_data["conso_hab"]*input_data["conso_vet"])*3.65
    if cles["recup_vai"]:
        water_save["recup_vai"]=(input_data["num_residents"]*input_data["conso_hab"]*input_data["conso_vai"])*3.65
    
    return water_save


    
