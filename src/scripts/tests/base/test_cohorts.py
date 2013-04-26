# -*- coding:utf-8 -*-
# Created on 22 mars 2013
# Copyright © 2013 Clément Schaff, Mahdi Ben Jelloul
# Acknowlegement  

# Good docs about nosetest
# http://ivory.idyll.org/articles/nose-intro.html
# https://nose.readthedocs.org/en/latest/testing.html

import nose
from src.lib.cohorte import Cohorts
from src.scripts.tests.utils import (create_testing_population_dataframe,
                                     create_empty_population_dataframe,
                                     create_constant_profiles_dataframe)
                                     
 


def test_empty_frame_generation():

    year_start = 2001
    year_end = 2061
    population_dataframe = create_empty_population_dataframe(year_start, year_end)
    test_value = population_dataframe.get_value((0,0,2043), "pop")
    assert test_value == 1
         
#===============================================================================
# Some tests of the object Cohorts
#===============================================================================

def test_population_projection():
    # Create cohorts
    population = create_empty_population_dataframe(2001, 2061)
    cohorts = Cohorts(data = population, columns = ['pop'])

    # Complete population projection
    year_length = 200
    method = 'stable'   
    cohorts.population_project(year_length, method = method)
    test_value = cohorts.get_value((0,0,2161), "pop")
#    print test_value
    assert test_value == 1

#     print population_dataframe.head()
#     
#     population_dataframe.reset_index(inplace=True)
#     population_dataframe_restricted = population_dataframe[population_dataframe.year==2007 ]
#     population_dataframe_restricted["tax"] = 1 
# 
#     profiles_dataframe = population_dataframe_restricted.set_index(['age', 'sex','year'])
#     
#     population_dataframe.set_index(['age', 'sex','year'], inplace=True)
#     simulation = Simulation()
#     simulation.set_population(population_dataframe)
#     simulation.set_profiles(profiles_dataframe)
#     simulation.set_population_projection(year_length=200, method="constant")
# 
#     r = 0.00
#     g = 0.00
#     simulation.set_growth_rate(g)
#     simulation.set_discount_rate(r)       
# 
#     simulation.create_cohorts()
#     
#     
#     test_value = simulation.cohorts.get_value((0,0,2100),"tax")
#     assert test_value == 1    
#     pass

def test_column_combination():
    year_start = 2001
    pop_dataframe = create_empty_population_dataframe(year_start, 2061)
#     print pop_dataframe
    profiles_dataframe = create_constant_profiles_dataframe(pop_dataframe, tax=-1.0, sub=0.5)
#     print profiles_dataframe
    profiles_dataframe['net'] = profiles_dataframe.sum(axis=1) 
#     print profiles_dataframe['net']
    test_value = profiles_dataframe.get_value((0,0,2001), 'net')
#     print test_value
    assert test_value == -0.5


def test_fill_cohort():   
    population = create_empty_population_dataframe(2001, 2061)
    profiles = create_constant_profiles_dataframe(population, tax = -1, subsidies = 0.5)
    cohorts_test = Cohorts(data = population, columns = ['pop'])
    cohorts_test.fill(profiles, year = None)
    test_value = cohorts_test.get_value((0,0,2060), 'tax')
    print test_value
    assert test_value == -1


def test_dsct():
    population = create_empty_population_dataframe(2001, 2061)
    cohorts = Cohorts(data = population, columns = ['pop']) 
    cohorts.gen_dsct(0.05)
    test_value = cohorts.get_value((0,0,2060), 'dsct')
#    print test_value
    assert test_value <= 1
    
def test_tax_projection():

    population = create_empty_population_dataframe(2001, 2061)
    profile = create_constant_profiles_dataframe(population, tax = -1, sub=0.5) 
    g = 0.05
    r = 0
    cohort = Cohorts(population)
    cohort.fill(profile)
    typ = None
    cohort.proj_tax(g, r, typ,  method = 'per_capita')
#    print cohort
    test_value = cohort.get_value((0,1,2002), 'tax')
    test_value2 = cohort.get_value((0,1,2002), 'sub')
#    print test_value, test_value2
    # TODO: I don't understand the following <- Just wanted to check if the for loop works by changing the value of typ in the test
    assert test_value2 > 0.5 and test_value < -1

    
def test_tax_projection_aggregated():
    n = 1
    population = create_testing_population_dataframe(year_start=2001, year_end=2061, rate=n)
    print population.get_value((0,0,2011), 'pop')
    profile = create_constant_profiles_dataframe(population, tax=-1, sub=0.5)
    g = 0.5
    r = 0.0 
    cohort = Cohorts(population)
    cohort.fill(profile)
    typ = None
    cohort.proj_tax(g, r, typ,  method = 'aggregate')
    test_value = cohort.get_value((0,1,2002), 'tax')
    test_value2 = cohort.get_value((0,1,2002), 'sub')
    assert test_value2 < 0.5 and test_value > -1




def test_pv_ga():
    pass



if __name__ == '__main__':

#     test_population_projection() 
#     test_tax_projection() #Now working flawlessly
#     test_tax_projection_aggregated() #Good to go
#     test_fill_cohort() #Working
#     test_dsct() #Working
#     test_empty_frame_generation()
#     test_population_projection()
#     test_column_combination() #Working
    nose.core.runmodule(argv=[__file__, '-v', '-i test_*.py'])
#     nose.core.runmodule(argv=[__file__, '-vvs', '-x', '--pdb', '--pdb-failure'], exit=False)
