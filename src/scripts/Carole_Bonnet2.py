# -*- coding:utf-8 -*-
# Created on 6 mai 2013
# This file is part of OpenFisca.
# OpenFisca is a socio-fiscal microsimulation software
# Copyright © #2013 Clément Schaff, Mahdi Ben Jelloul
# Licensed under the terms of the GVPLv3 or later license
# (see openfisca/__init__.py for details)

from __future__ import division
import os
from src.lib.simulation import Simulation
from src.lib.cohorts.accounting_cohorts import AccountingCohorts
from pandas import read_csv, HDFStore, concat, ExcelFile, DataFrame
from numpy import array, hstack
import matplotlib.pyplot as plt
from src import SRC_PATH




def test():
    
    country = "france"    
    population_filename = os.path.join(SRC_PATH, 'countries', country, 'sources',
                                           'data_fr', 'proj_pop_insee', 'proj_pop.h5')
    profiles_filename = os.path.join(SRC_PATH, 'countries', country, 'sources',
                                         'data_fr','profiles.h5')
    CBonnet_results = os.path.join(SRC_PATH, 'countries', country, 'sources',
                                           'Carole_Bonnet', 'theoretical_results.xls')

    simulation = Simulation()
    population_scenario = "projpop0760_FECbasESPbasMIGbas"
    
    simulation.load_population(population_filename, population_scenario)
    simulation.load_profiles(profiles_filename)
#     uniform = (164.3-157.7-285.4+3.1+15.4-0.7+0.4-15.7-67.6-24.6)*1e+09
#     simulation.profiles['uniform'] = uniform/60e+06
    
    xls = ExcelFile(CBonnet_results)
    """
    Hypothesis set #1 : 
    actualization rate r = 3%
    growth rate g = 1%
    net_gov_wealth = -3217.7e+09 (unit : Franc Français (FF) of 1996)
    
    """

    
    #Setting parameters
    year_length = 250
    r = 0.03
    g = 0.01
    n = 0.00
    net_gov_wealth = -3217.7e+09
    net_gov_spendings = 0
    for t in range(251):
        year_gov_spending = (2.96+2.57+3.59+4.58+3.31+0.61+2.71+41.99+1.53+10.04+11.72+0.56+8.80+
                             0.36+1.02+0.26+25.37+16.82+0.46+0.41+7.65+10.0)*6.55957*0.85*1e+09*(
                            (1+g)/(1+r))**t
        net_gov_spendings += year_gov_spending
    print net_gov_spendings
    simulation.set_population_projection(year_length=year_length, method="stable")
    simulation.set_tax_projection(method="per_capita", rate=g)
    simulation.set_growth_rate(g)
    simulation.set_discount_rate(r) 
    simulation.set_population_growth_rate(n)
    simulation.create_cohorts()
    simulation.set_gov_wealth(net_gov_wealth)
    simulation.set_gov_spendings(net_gov_spendings)

    #Calculating net transfers
    #Net_transfers = tax paid to the state minus money recieved from the state

    
    taxes_list = ['tva', 'tipp', 'cot', 'irpp', 'impot', 'property']
    payments_list = ['chomage', 'retraite', 'revsoc', 'maladie', 'educ']
    
    simulation.cohorts.compute_net_transfers(name = 'net_transfers', taxes_list = taxes_list, payments_list = payments_list)
    
    
    """
    Reproducing the table 2 : Comptes générationnels par âge et sexe (Compte central)
    """
    #Generating generationnal accounts
    simulation.create_present_values(typ = 'net_transfers')
    print "PER CAPITA PV"
    print simulation.percapita_pv.xs(0, level = 'age').head()
    print simulation.percapita_pv.xs((0, 2007), level = ['sex', 'year']).head()


    # Calculating the Intertemporal Public Liability
    ipl = simulation.compute_ipl(typ = 'net_transfers')
    print "------------------------------------"
    print "IPL =", ipl
    print "share of the GDP : ", ipl/8050.6e+09*100, "%"
    print "------------------------------------"
    
    #Calculating the generational imbalance
    gen_imbalance = simulation.compute_gen_imbalance(typ = 'net_transfers')
    print "----------------------------------"
    print "imbalance : [n_1=", gen_imbalance[0], ", n_1-n_0=", gen_imbalance[1], ", n_1/n_0=", gen_imbalance[2],"]"
    print "----------------------------------"    
    
    
    #Creating age classes
    cohorts_age_class = AccountingCohorts(simulation.create_age_class(typ = 'net_transfers', step = 5))
    cohorts_age_class._types = [u'tva', u'tipp', u'cot', u'irpp', u'impot', u'property', u'chomage', u'retraite', u'revsoc', u'maladie', u'educ', u'net_transfers']
    age_class_pv_fe = cohorts_age_class.xs((1, 2007), level = ['sex', 'year'])
    age_class_pv_ma = cohorts_age_class.xs((0, 2007), level = ['sex', 'year'])
    print "AGE CLASS PV"
    print age_class_pv_fe.head()
    print age_class_pv_ma.head()
    
    
    #Plotting
    age_class_pv = cohorts_age_class.xs(2007, level = "year").unstack(level="sex")
    age_class_pv = age_class_pv['net_transfers']
    age_class_pv.columns = ['men' , 'women']
#     age_class_pv['total'] = age_class_pv_ma['net_transfers'] + age_class_pv_fe['net_transfers']
#     age_class_pv['total'] *= 1.0/2.0
    age_class_theory = xls.parse('Feuil1', index_col = 0)
       
    age_class_pv['men_CBonnet'] = age_class_theory['men_Cbonnet']
    age_class_pv['women_CBonnet'] = age_class_theory['women_Cbonnet']
    age_class_pv.plot(style = '--') ; plt.legend()
    plt.axhline(linewidth=2, color='black')
    plt.show()

def show_data():
    
    country = "france"    
    population_filename = os.path.join(SRC_PATH, 'countries', country, 'sources',
                                           'data_fr', 'proj_pop_insee', 'proj_pop.h5')
    profiles_filename = os.path.join(SRC_PATH, 'countries', country, 'sources',
                                         'data_fr','profiles.h5')

    simulation = Simulation()
    population_scenario = "projpop0760_FECbasESPbasMIGbas"
    
    simulation.load_population(population_filename, population_scenario)
    simulation.load_profiles(profiles_filename)
    
    simulation.restricted_pop1 = simulation.population.iloc[:101,:]
    simulation.restricted_pop2 = simulation.population.iloc[5454:5555,:]
    
    
    simulation.restricted_pop = concat([simulation.restricted_pop1, simulation.restricted_pop2])
    simulation.profiles.reset_index(inplace=True); simulation.restricted_pop.reset_index(inplace=True)
    simulation.restricted_pop['year'] = 1996
    print simulation.restricted_pop.head()
    print simulation.profiles.head()
    
    simulation.profiles['pop'] = simulation.restricted_pop['pop'] 
    simulation.profiles.set_index(['age', 'sex', 'year'], inplace=True)
    print simulation.profiles.loc[:, ['pop', 'tva']].tail(10).to_string()

    simulation.profiles['tva'] *= simulation.profiles['pop']
    print simulation.profiles.loc[:, ['pop', 'tva']].tail(10).to_string()
    
    agreg_irpp = simulation.profiles.cumsum().get_value((100,1,1996), 'tva')
    agreg_pop = simulation.profiles.cumsum().get_value((100,1,1996), 'pop')
    print agreg_irpp, agreg_pop
    
     
if __name__ == '__main__':
    test()
#     show_data()
