# -*- coding: utf-8 -*-
"""

This code retrieves an example on the application of the trade-offs and 
synergies framework proposed in the paper 
'How to measure Circularity Trade-offs and Synergies?'.

It includes:
    - An scenario analysis based on Donati et al. (2020)
    - Harmonization process
    - A function to analyze geographical trade-offs and synergies
    - A function to analyze impact trade-offs and synergies
    - A function to analyze sectoral trade-offs and synergies
    - 3 save functions for each dimension assessments

    * Note 1: Before running the code, dowload EXIOBASE v3.9.5 
            from https://zenodo.org/records/14869924
    * Note 2: From step-2, it can be analyzed any dataset following 
            the proposed structure on the 

Python version: v3.12.7

EXIOBASE version: v3.9.5 ixi_2020 

Data access: https://zenodo.org/records/14869924

Author: aguilarga (https://github.com/aguilarga)

Latest update: March 15, 2025
"""

# Import packages
import mario
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Import data
    
path_exio = 'IOT_2020_ixi_v3.9.5' # Add/Change directory for database folder
exiobase = mario.parse_exiobase(
    table = 'IOT',
    unit = 'Monetary',
    path = path_exio)

# Adding GHG emissions extension
path_extensions = 'MARIO_Extensions&Aggregations/new_E_extension.xlsx'
#exiobase.get_extensions_excel(matrix='E',path=path_extensions) ##Only use for adding new extensions in E
units = pd.read_excel(path_extensions, sheet_name='units',index_col=[0],header=[0])
exiobase.add_extensions(
    io=path_extensions,
    units=units,
    matrix='E')

# Aggregation
path_aggr = 'MARIO_Extensions&Aggregations/exiobase_aggregated.xlsx'
# exiobase.get_aggregation_excel(path = path_aggr,) # Use only when it's a new aggregation
exiobase.aggregate(
    io= path_aggr,
    levels = ["Factor of production",
        "Satellite account",
        "Consumption category",
        "Region",
        "Sector"]) # CoreModel.aggreate retrieves the aggregated database based on the Aggregation Excel file
    
# Step 1: Scenario analysis

""" 
Description:
    
This example scenario assumes CE implementation in the LAC agriculture sector,
having changes in:
    - LAC's agriculture sector increases composting by 30%
    - LAC's agriculture sector reduces domestic consumption and imports of
    N & P fertilisers by 1.6%
    - All final demand from LAC's agriculture and food products
    replaces 30% of consumption with organic products that cost 2 times more
    - In agriculture: 20% increase in composting, biogasification, 
    
"""
ce_scenario = "MARIO_ce_scenario.xlsx" 
# exiobase.get_shock_excel(path = ce_scenario) ## Use only to create new scenario files
exiobase.shock_calc(
    io= ce_scenario,
    Y = True,
    z= True,
    scenario='CE scenario',
    force_rewrite=True,
    notes=['CE scenarios in LAC']) # df.shock_cal calculates the scenarios based on the Shock file data

ce_scenario = exiobase.query(
    matrices='F',
    scenarios='CE scenario',) # df.query is used to explore every element of the scenarios

bau_scenario = exiobase.query(
    matrices='F',
    scenarios='baseline',) # df.query is used to explore every element of the scenarios

    # Footprint calculation setting

Y_bau = exiobase.Y
L_bau = exiobase.w
Y_ce = exiobase.matrices['CE scenario']['Y']
L_ce = exiobase.matrices['CE scenario']['w']

va = exiobase.v.loc['Value Added',:]
emp = exiobase.e.loc['Employment (people)',:]
ghg = exiobase.e.loc['GHG emissions',:]

va_ind = 'Value Added'
emp_ind = 'Employment (people)'
ghg_ind = 'GHG emissions'

va_bau = np.diag(va) @ L_bau
emp_bau = np.diag(emp) @ L_bau
ghg_bau = np.diag(ghg) @ L_bau

va_ce = np.diag(va) @ L_ce
emp_ce = np.diag(emp) @ L_ce
ghg_ce = np.diag(ghg) @ L_ce

    # EU's footprints
    
va_bau_eu = va_bau @ Y_bau.loc[:, 'EU']
emp_bau_eu = emp_bau @ Y_bau.loc[:, 'EU']
ghg_bau_eu = ghg_bau @ Y_bau.loc[:, 'EU']

va_ce_eu = va_ce @ Y_ce.loc[:, 'EU']
emp_ce_eu = emp_ce @ Y_ce.loc[:, 'EU']
ghg_ce_eu = ghg_ce @ Y_ce.loc[:, 'EU']

    # LAC footprints
    
va_bau_lac = va_bau @ Y_bau.loc[:, 'LAC']
emp_bau_lac = emp_bau @ Y_bau.loc[:, 'LAC']
ghg_bau_lac = ghg_bau @ Y_bau.loc[:, 'LAC']

va_ce_lac = va_ce @ Y_ce.loc[:, 'LAC']
emp_ce_lac = emp_ce @ Y_ce.loc[:, 'LAC']
ghg_ce_lac = ghg_ce @ Y_ce.loc[:, 'LAC']

# Step 2: Harmonization

    # EU's harmonization
column_labels = ['Value added', 'Employment', 'GHG']
bau_eu = pd.DataFrame({
    'Value Added': va_bau_eu.values.ravel(),  # Ensures 1D
    'Employment': emp_bau_eu.values.ravel(),
    'GHG': ghg_bau_eu.values.ravel()})
ce_eu = pd.DataFrame({
    'Value Added': va_ce_eu.values.ravel(),
    'Employment': emp_ce_eu.values.ravel(),
    'GHG': ghg_ce_eu.values.ravel()})
norm_eu = ((ce_eu - bau_eu) / bau_eu.sum()) * 100
norm_eu = norm_eu.fillna(0) # Replace resulting NaN values with zeros in Norm
norm_eu.index = Y_bau.index
    # Changes in sign for environmental impacts
norm_eu.loc[:,'GHG']*= -1    

    # LAC's harmonization
bau_lac = pd.DataFrame({
    'Value Added': va_bau_lac.values.ravel(),  # Ensures 1D
    'Employment': emp_bau_lac.values.ravel(),
    'GHG': ghg_bau_lac.values.ravel()})
ce_lac = pd.DataFrame({
    'Value Added': va_ce_lac.values.ravel(),
    'Employment': emp_ce_lac.values.ravel(),
    'GHG': ghg_ce_lac.values.ravel()})
norm_lac = ((ce_lac - bau_lac) / bau_lac.sum()) * 100
norm_lac = norm_lac.fillna(0) # Replace resulting NaN values with zeros in Norm
norm_lac.index = Y_bau.index
    # Changes in sign for environmental impacts
norm_lac.loc[:,'GHG']*= -1

    # Aggregation EU countries
norm_eu_agg= norm_eu.groupby(level='Item').sum()
norm_eu_agg['Region'] = 'EU footprint'  # Add as a column
norm_eu_agg = norm_eu_agg.set_index('Region', append=True)  # Move to MultiIndex
norm_eu_agg = norm_eu_agg.reorder_levels(['Region', 'Item'])  # Optional: reorder levels

    # Aggregation LAC countries
norm_lac_agg= norm_lac.groupby(level='Item').sum()
norm_lac_agg['Region'] = 'LAC footprint'  # Add as a column
norm_lac_agg = norm_lac_agg.set_index('Region', append=True)  # Move to MultiIndex
norm_lac_agg = norm_lac_agg.reorder_levels(['Region', 'Item'])  # Optional: reorder levels

    # EU + LAC matrix
norm_new = pd.concat([norm_eu_agg, norm_lac_agg])

# Step 3 & 4: Concatenating dimensions, and Trade-offs and Synergies analysis

    # Functions
def ts_geo(data, country_list, impact):
    df_ = data.copy()
    df_geo = df_.loc[pd.IndexSlice[country_list,:],impact]
    # Group by country and sector, then unstack for plotting
    grouped = df_geo.unstack(level='Region')
    df_ts = grouped.copy()
    # Function to apply win/lose/tie situation
    def ts_result(value1, value2):
        if value1 > 0 and value2 > 0:
            return 'win-win'
        elif value1 > 0 and value2 < 0:
            return 'win-lose'
        elif value1 < 0 and value2 > 0:
            return 'lose-win'
        elif value1 < 0 and value2 < 0:
            return 'lose-lose'
        elif value1 == 0 and value2 == 0:
            return 'tie-tie'
        elif value1 == 0 and value2 < 0:
            return 'tie-lose'
        elif value1 == 0 and value2 > 0:
            return 'tie-win'
        elif value1 < 0 and value2 == 0:
            return 'lose-tie'
        elif value1 > 0 and value2 == 0:
            return 'win-tie'
        else:
            return

    # Apply the function to create a new TS column
    df_ts['TS'] = df_ts.apply(lambda row: ts_result(row[df_ts.columns[0]], 
                                                        row[df_ts.columns[1]]), 
                                                    axis=1)
    # Create TS-results dataframe
    ## Function to calculate Euclidean sum
    def euclidean_sum(row):
        return np.sqrt(row[df_ts.columns[0]] ** 2 + row[df_ts.columns[1]] ** 2)
    ## Calculate Euclidean sum for each row
    df_ts['Euclidean'] = df_ts.apply(euclidean_sum, axis=1)
    ## New dataframe
    categories = df_ts['TS'].unique() # Extract unique categories
    results = df_ts['TS'].value_counts().reindex(categories, fill_value=0).tolist() # Count occurrences of each category
    ### Calculate magnitude for each category
    magnitude = []
    for category in categories:
        # Filter DataFrame for the current category and sum the Euclidean distances
        magnitude.append(df_ts[df_ts['TS'] == category]['Euclidean'].sum())

    ts_results = pd.DataFrame({'Categories': categories, 
                               'Results': results, 
                               'Magnitude': magnitude}) # Create DataFrame with correct values for each category
    # Plotting
    labels = ts_results['Categories']
    sizes = ts_results['Magnitude']
    
    # Create the pie chart
    plt.figure(figsize=(8, 8))  # Set the size of the figure
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)  # Plot the pie chart
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Geographical trade-off and synergies distribution by categories for ' +str(impact))  # Add title
    plt.show()
    
    # Create scatter plot
    fig, ax = plt.subplots()
    grouped.plot(kind='scatter', x=grouped.columns[0], y=grouped.columns[1],
                 ax=ax)
    # Set axis limits
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    # Hide the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Set the position of the remaining spines to cross at (0,0)
    ax.spines['bottom'].set_position(('data', 0))
    ax.spines['left'].set_position(('data', 0))
        
    # Set labels and legend
    # Add a title to the figure
    ax.set_title('Geographical trade-off and synergies for ' + str(impact) +
                 ' (in relative changes, %)'
                 , fontsize=14, pad=20, loc='center', va='top')
    plt.show()
    
    # Calculate the total of all sectors for each country
    total = df_geo.groupby('Region').sum()
 
    # Plotting the total figure
    fig_total, ax_total = plt.subplots()
    total.plot(kind='barh', stacked=True, ax=ax_total, linewidth=50,
               color=['C0', 'C1'])
    
    # Set labels and legend
    ax_total.set_title('Geographical trade-off and synergies for ' +str(impact)
                 , fontsize=14, pad=20, loc='center', va='top')
    ax_total.set_xlabel('Relative change (%)')
    ax_total.set_xlim(-10.0, 10.0)
    # Add text annotations
    ax_total.text(8.75,1.3, 'Win', fontsize=24, ha='center', va='center', color='blue')
    ax_total.text(-8.75,1.3, 'Lose', fontsize=24, ha='center', va='center', color='red')
    plt.show()
    return ts_results, grouped, total

def ts_imp(data, impact_list, country):
    df_ = data.copy()
    df_imp = df_.loc[pd.IndexSlice[country,:],impact_list]
    df_ts = df_imp.copy()
    
    # Function to apply win/lose/tie situation
    def ts_result(value1, value2, value3):
        if value1 > 0 and value2 > 0 and value3 > 0:
            return 'win-win-win'
        elif value1 < 0 and value2 < 0 and value3 < 0:
            return 'lose-lose-lose'
        elif value1 == 0 and value2 == 0 and value3 == 0:
            return 'tie-tie-tie'
        ###
        elif value1 > 0 and value2 > 0 and value3 < 0:
            return 'win-win-lose'
        elif value1 > 0 and value2 < 0 and value3 < 0:
            return 'win-lose-lose'
        elif value1 > 0 and value2 < 0 and value3 > 0:
            return 'win-lose-win'
        elif value1 > 0 and value2 == 0 and value3 == 0:
            return 'win-tie-tie'
        elif value1 > 0 and value2 < 0 and value3 < 0:
            return 'win-lose-lose'
        elif value1 > 0 and value2 == 0 and value3 < 0:
            return 'win-tie-lose'
        elif value1 > 0 and value2 == 0 and value3 > 0:
            return 'win-tie-win'
        elif value1 > 0 and value2 > 0 and value3 == 0:
            return 'win-win-tie'
        elif value1 > 0 and value2 < 0 and value3 == 0:
            return 'win-lose-tie'
        ###
        elif value1 < 0 and value2 > 0 and value3 > 0:
            return 'lose-win-win'
        elif value1 < 0 and value2 > 0 and value3 < 0:
            return 'lose-win-lose'
        elif value1 < 0 and value2 < 0 and value3 > 0:
            return 'lose-lose-win'
        elif value1 < 0 and value2 == 0 and value3 < 0:
            return 'lose-tie-lose'
        elif value1 < 0 and value2 == 0 and value3 < 0:
            return 'lose-tie-lose'
        elif value1 < 0 and value2 == 0 and value3 > 0:
            return 'lose-tie-win'       
        elif value1 < 0 and value2 > 0 and value3 == 0:
            return 'lose-win-tie'
        elif value1 < 0 and value2 < 0 and value3 == 0:
            return 'lose-lose-tie'
        ###
        elif value1 == 0 and value2 > 0 and value3 == 0:
            return 'tie-win-tie'
        elif value1 == 0 and value2 > 0 and value3 < 0:
            return 'tie-win-lose'
        elif value1 == 0 and value2 > 0 and value3 > 0:
            return 'tie-win-win'
        elif value1 > 0 and value2 > 0 and value3 == 0:
            return 'win-win-tie'
        elif value1 < 0 and value2 > 0 and value3 < 0:
            return 'lose-win-lose'
        ###
        elif value1 == 0 and value2 < 0 and value3 == 0:
            return 'tie-lose-tie'
        elif value1 == 0 and value2 < 0 and value3 < 0:
            return 'tie-lose-lose'
        elif value1 == 0 and value2 < 0 and value3 > 0:
            return 'tie-lose-win'
        ###
        elif value1 == 0 and value2 == 0 and value3 > 0:
            return 'tie-tie-win'
        elif value1 == 0 and value2 == 0 and value3 < 0:
            return 'tie-tie-lose'
        else:
            return

    # Apply the function to create a new TS column
    df_ts['TS'] = df_ts.apply(lambda row: ts_result(row[df_ts.columns[0]], 
                                                    row[df_ts.columns[1]],
                                                    row[df_ts.columns[2]]),
                                                        axis=1)
    # Create TS-results dataframe
    ## Function to calculate Euclidean sum
    def euclidean_sum(row):
        return np.sqrt(row[df_ts.columns[0]] ** 2 + row[df_ts.columns[1]] ** 2 + row[df_ts.columns[2]] ** 2)
    
    ## Calculate Euclidean sum for each row
    df_ts['Euclidean'] = df_ts.apply(euclidean_sum, axis=1)
    
    ## New dataframe
    categories = df_ts['TS'].unique() # Extract unique categories
    results = df_ts['TS'].value_counts().reindex(categories, fill_value=0).tolist() # Count occurrences of each category
    
    ### Calculate magnitude for each category
    magnitude = []
    for category in categories:
        # Filter DataFrame for the current category and sum the Euclidean distances
        magnitude.append(df_ts[df_ts['TS'] == category]['Euclidean'].sum())

    ts_results = pd.DataFrame({'Categories': categories, 
                               'Results': results, 
                               'Magnitude': magnitude}) # Create DataFrame with correct values for each category
    # Plotting
    labels = ts_results['Categories']
    sizes = ts_results['Magnitude']
    
    # Create the pie chart
    plt.figure(figsize=(8, 8))  # Set the size of the figure
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)  # Plot the pie chart
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Impact trade-off and synergies distribution by categories for '+str(country))  # Add title
    plt.show()
    
    # Create scatter plot
    # Create 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(df_imp['Value Added'], df_imp['Employment'], df_imp['GHG'])
    
    # Set axis limits
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)

    # Hide the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Set the position of the remaining spines to cross at (0,0,0)
    ax.spines['bottom'].set_position(('data', 0))
    ax.spines['left'].set_position(('data', 0))
    ax.spines['bottom'].set_position(('data', 0))
    ax.spines['top'].set_position(('data', 0))

    # Add lines representing each axis intersecting at (0,0,0)
    ax.plot([-1, 1], [0, 0], [0, 0], color='k', linestyle='-', linewidth=1, zorder=1)  # X-axis
    ax.plot([0, 0], [-1, 1], [0, 0], color='k', linestyle='-', linewidth=1, zorder=1)  # Y-axis
    ax.plot([0, 0], [0, 0], [-1, 1], color='k', linestyle='-', linewidth=1, zorder=1)  # Z-axis
    
    # Set labels and legend
    ax.set_title('Impacts trade-off and synergies in ' + str(country), 
                 fontsize=14, pad=20, loc='center', va='top')

    ax.set_xlabel(df_imp.columns[0])
    ax.set_ylabel(df_imp.columns[1])
    ax.set_zlabel(df_imp.columns[2])
    plt.show()
    
    # Calculate the total of all sectors for each country
    total = df_imp.sum()
 
    # Plotting the total figure
    fig_total, ax_total = plt.subplots()
    total.plot(kind='barh', stacked=True, ax=ax_total, linewidth=50,
               color=['C0', 'C1', 'C2'])
    #Set Labels and legend
    ax_total.set_title('Impacts trade-off and synergies in ' +str(country)
                 , fontsize=14, pad=20, loc='center', va='top')
    ax_total.set_xlabel('Relative change (%)')
    ax_total.set_xlim(-10, 10)  # Set x-axis limits
    # Add text annotations
    ax_total.text(8.75,3.0, 'Win', fontsize=24, ha='center', va='center', color='blue')
    ax_total.text(-8.75,3.0, 'Lose', fontsize=24, ha='center', va='center', color='red')
    plt.show()
    return ts_results, df_imp, total

def ts_sec(data, sector_list, impact):
    df_ = data.copy()
    df_sec = df_.loc[pd.IndexSlice[:, sector_list],impact]
    
    # Group by country and sector, then unstack for plotting
    grouped = df_sec.unstack(level='Item')
    df_ts = grouped.copy()
    
    # Function to apply win/lose/tie situation
    def ts_result(value1, value2):
        if value1 > 0 and value2 > 0:
            return 'win-win'
        elif value1 > 0 and value2 < 0:
            return 'win-lose'
        elif value1 < 0 and value2 > 0:
            return 'lose-win'
        elif value1 < 0 and value2 < 0:
            return 'lose-lose'
        elif value1 == 0 and value2 == 0:
            return 'tie-tie'
        elif value1 == 0 and value2 < 0:
            return 'tie-lose'
        elif value1 == 0 and value2 > 0:
            return 'tie-win'
        elif value1 < 0 and value2 == 0:
            return 'lose-tie'
        elif value1 > 0 and value2 == 0:
            return 'win-tie'
        else:
            return 'tie-tie'

    # Apply the function to create a new TS column
    df_ts['TS'] = df_ts.apply(lambda row: ts_result(row[df_ts.columns[0]], 
                                                        row[df_ts.columns[1]]), 
                                                    axis=1)
    # Create TS-results dataframe
    ## Function to calculate Euclidean sum
    def euclidean_sum(row):
        return np.sqrt(row[df_ts.columns[0]] ** 2 + row[df_ts.columns[1]] ** 2)
    
    ## Calculate Euclidean sum for each row
    df_ts['Euclidean'] = df_ts.apply(euclidean_sum, axis=1)
    
    ## New dataframe
    categories = df_ts['TS'].unique() # Extract unique categories
    results = df_ts['TS'].value_counts().reindex(categories, fill_value=0).tolist() # Count occurrences of each category
    
    ### Calculate magnitude for each category
    magnitude = []
    for category in categories:
        # Filter DataFrame for the current category and sum the Euclidean distances
        magnitude.append(df_ts[df_ts['TS'] == category]['Euclidean'].sum())

    ts_results = pd.DataFrame({'Categories': categories, 
                               'Results': results, 
                               'Magnitude': magnitude}) # Create DataFrame with correct values for each category
    
    # Plotting
    labels = ts_results['Categories']
    sizes = ts_results['Magnitude']
    
    # Create the pie chart
    plt.figure(figsize=(8, 8))  # Set the size of the figure
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)  # Plot the pie chart
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Sectoral trade-off and synergies distribution by categories for ' +str(impact))  # Add title
    plt.show()
        
    # Create scatter plot
    fig, ax = plt.subplots()
    grouped.plot(kind='scatter', x=grouped.columns[0], y=grouped.columns[1],
                 ax=ax)
    # Set axis limits
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    # Hide the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Set the position of the remaining spines to cross at (0,0)
    ax.spines['bottom'].set_position(('data', 0))
    ax.spines['left'].set_position(('data', 0))
        
    # Set labels and legend
    # Add a title to the figure
    ax.set_title('Sectoral trade-off and synergies for ' + str(impact) +
                 ' (in relative changes, %)'
                 , fontsize=14, pad=20, loc='center', va='top')
    plt.show()
    
    # Calculate the total of all sectors for each country
    total = df_sec.groupby('Item').sum()
 
    # Plotting the total figure
    fig_total, ax_total = plt.subplots()
    total.plot(kind='barh', stacked=True, ax=ax_total, linewidth=50,
               color=['C0', 'C1'])
    
    # Set labels and legend
    ax_total.set_title('Sectoral trade-off and synergies for ' +str(impact)
                 , fontsize=14, pad=20, loc='center', va='top')
    ax_total.set_xlabel('Relative change (%)')
    ax_total.set_xlim(-1.0, 1.0)  # Set x-axis limits
    
    # Add text annotations
    ax_total.text(0.75,1.3, 'Win', fontsize=24, ha='center', va='center', color='blue')
    ax_total.text(-0.75,1.3, 'Lose', fontsize=24, ha='center', va='center', color='red')
    plt.show()
    return ts_results, grouped, total

    # Analysis per dimension 
        # Geographical trade-offs and synergies analysis
country_list =['EU footprint', 'LAC footprint']
ts_geo(norm_new, country_list, 'Value Added')
ts_geo(norm_new, country_list, 'Employment')
ts_geo(norm_new, country_list, 'GHG')

        # Impact trade-offs and synergies analysis
impact_list = ['Value Added','Employment', 'GHG']
ts_imp(norm_new, impact_list, 'EU footprint')
ts_imp(norm_new, impact_list, 'LAC footprint')

        # Sectoral trade-offs and synergies analysis
sector_list = ['P&N Fertilisers','Agriculture']
ts_sec(norm_new, sector_list, 'Value Added')
ts_sec(norm_new, sector_list, 'Employment')
ts_sec(norm_new, sector_list, 'GHG')

# Save results functions 
def save_geo_res(norm_new):
    country_list =['EU footprint', 'LAC footprint']
    va_ind = "Value Added"
    emp_ind = "Employment"
    ghg_ind = "GHG"

    geo_va, geo_va_all, geo_va_sum = ts_geo(norm_new, country_list, va_ind)
    geo_emp, geo_emp_all, geo_emp_sum = ts_geo(norm_new, country_list, emp_ind)
    geo_ghg, geo_ghg_all, geo_ghg_sum = ts_geo(norm_new, country_list, ghg_ind)
    
    filename = "geo_results_" + datetime.now().strftime('%Y%m%d') + ".xlsx"
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    
        geo_va.to_excel(writer, 'geo_va')
        geo_va_all.to_excel(writer, 'geo_va_all')
        geo_va_sum.to_excel(writer, 'geo_va_sum')
        geo_emp.to_excel(writer, 'geo_emp')
        geo_emp_all.to_excel(writer, 'geo_emp_all')
        geo_emp_sum.to_excel(writer, 'geo_emp_sum')
        geo_ghg.to_excel(writer, 'geo_gwp')
        geo_ghg_all.to_excel(writer, 'geo_gwp_all')
        geo_ghg_sum.to_excel(writer, 'geo_gwp_sum')
    return

def save_imp_res(norm_new):
    impact_list = ['Value Added','Employment', 'GHG']
    imp_eu, imp_eu_all, imp_eu_sum = ts_imp(norm_new, impact_list, 'EU footprint')
    imp_la, imp_la_all, imp_la_sum = ts_imp(norm_new, impact_list, 'LAC footprint')
    filename = "imp_results_" + datetime.now().strftime('%Y%m%d') + ".xlsx"
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        imp_eu.to_excel(writer, 'imp_eu')
        imp_eu_all.to_excel(writer, 'imp_eu_all')
        imp_eu_sum.to_excel(writer, 'imp_eu_sum')
        imp_la.to_excel(writer, 'imp_la')
        imp_la_all.to_excel(writer, 'imp_la_all')
        imp_la_sum.to_excel(writer, 'imp_la_sum')
    return

def save_sec_res(norm_new):
    sector_list = ['Construction (45)',"Manufacture of basic iron and steel and of ferro-alloys and first products thereof"]
    va_ind = "Value Added"
    emp_ind = "Employment"
    sec_va, sec_va_all, sec_va_sum = ts_sec(norm_new, sector_list, va_ind)
    sec_emp, sec_emp_all, sec_emp_sum = ts_sec(norm_new, sector_list, emp_ind)
    sec_ghg, sec_ghg_all, sec_ghg_sum = ts_sec(norm_new, sector_list, 'GHG')  
    filename = "sec_results_" + datetime.now().strftime('%Y%m%d') + ".xlsx"
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        sec_va.to_excel(writer, 'sec_va')
        sec_va_all.to_excel(writer, 'sec_va_all')
        sec_va_sum.to_excel(writer, 'sec_va_sum')
        sec_emp.to_excel(writer, 'sec_emp')
        sec_emp_all.to_excel(writer, 'sec_emp_all')
        sec_emp_sum.to_excel(writer, 'sec_emp_sum')
        sec_ghg.to_excel(writer, 'sec_gwp')
        sec_ghg_all.to_excel(writer, 'sec_gwp_all')
        sec_ghg_sum.to_excel(writer, 'sec_gwp_sum')
    return