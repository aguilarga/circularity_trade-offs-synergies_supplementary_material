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

Data: EXIOBASE v3.ixi_2019 

Data access: https://zenodo.org/record/5589597

author: aguilarga

Latest update: November 22, 2024
"""

# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Import data

A = pd.read_csv("IOT_2019_ixi/A.txt", sep="\t", index_col=[0, 1], header=[0, 1])  # A matrix
Y = pd.read_csv("IOT_2019_ixi/Y.txt", sep="\t", index_col=[0, 1], header=[0, 1])  # Y matrix
M = pd.read_csv('IOT_2019_ixi/impacts/F.txt', sep='\t', index_col=[0], header=[0, 1])  # impacts matrix

# MRIOA variables

I = np.identity(A.shape[0]) # A.shape[0] is the total number of columns in the A matrix
L = np.linalg.inv(I-A)
# Multipliers and inverse diagonalized
x = L@Y.sum(axis=1) # Multipliers = Total output
x_ = x.copy() # copy Multipliers
x_[x_!=0] = 1/x_[x_!=0] # divided by 1 values that are non-zeros
inv_diag_x = np.diag(x_) # Multipliers inverse diagonalized

# Intensities (total)
m = M @ inv_diag_x # intensities of the impacts (i.e., characterized extensions)

# Intensities (selected)
va_ind = "Value Added"
#va = m.loc[va_ind] # Value Added intensity impact vector
emp_ind = "Employment"
#emp = m.loc[emp_ind] # Employment intensity impact vector
ghg_ind = "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"
#ghg =  m.loc[ghg_ind] # GWP-100 intensity impact vector

# Step 1: Scenario analysis

""" 
Description:
Impacts of the adoption of circularity interventions in the EU and LATAM 
construction sector. For this example, it is analyzed three dimensions:    
    - Geographical: EU vs. LATAM
    - Impacts: Value Added vs. Employment vs. GWP (=GHG emissions)
    - Sectors: Construction vs.
                Manufacture of basic iron and steel 
                and of ferro-alloys and first products thereof
Circularity interventions:
    Product lifetime extension:
        - Increasing refurbisment by 40%
        - Decreasing 60% of construction final demand in EU and LATAM
        -Increasing 60% inter-industry demand of construction-construction 
        in EU and LATAM
    Resource efficiency:
        - Replacing 90% of primary steel with secondary steel 
        in construction 
        - Replacing 90% of primary alumnium with secondary steel 
        in construction
        - Increasing 50% occupancy of non-residential buildings
Variables:
    - kt = Technical change coefficient (e.g)
    - kp = Market penetration
    - alpha = weighting coeffient
"""
## BAU scenario impacts per sector
va = np.diag(m.loc[va_ind]) @ x
emp = np.diag(m.loc[emp_ind]) @ x
ghg = np.diag(m.loc[ghg_ind]) @ x

## CE Scenario
Y_ce = Y.copy() # copy A matrix
A_ce = A.copy() # copy A matrix
Y_by_country = Y.copy()
Y_by_country = Y_by_country.T.groupby(level=0).sum().T
country_ind = ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 
          'FR', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT',
          'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'WL', 'MX', 'BR'] # all EU and LATAM countries 

## Product lifetime extension
### Primary change"
pc_1_row = "Construction (45)"
pc_1_country_column = country_ind
pc_1 = {"kt": -1.1, "kp": 1.0}  # Summing 60% and 50% occupancy
Y_ce.loc[pd.IndexSlice[:,pc_1_row], 
         pd.IndexSlice[pc_1_country_column,:]
         ] *= 1 + pc_1["kt"] * pc_1["kp"]
### Secondary change
sc_1 = {"kt": 1.2, "kp": 1} # Summing 60% and 40% from refurbishment
sc_1_row = "Construction (45)"
sc_1_country_row = country_ind
sc_1_column = "Construction (45)"
sc_1_country_column = country_ind
# implement secondary change
A_ce.loc[pd.IndexSlice[sc_1_country_row,sc_1_row],
         pd.IndexSlice[sc_1_country_column,sc_1_column]
         ] *= 1 + sc_1["kt"] * sc_1["kp"]

## Resource efficiency (Steel)
### Primary change
pc_2 = {"kt": -0.9, "kp": 1} 
pc_2_row = "Manufacture of basic iron and steel and of ferro-alloys and first products thereof"
pc_2_country_row = country_ind
pc_2_column = "Construction (45)"
pc_2_country_column = country_ind
# implement secondary change
A_ce.loc[pd.IndexSlice[pc_2_country_row, pc_2_row],
         pd.IndexSlice[pc_2_country_column, pc_2_column]
         ] *= 1 + pc_2["kt"] * pc_2["kp"]
### Secondary change (substitution)
sc_2 = {"alpha": 456}
sc_2_row = "Re-processing of secondary steel into new steel"
sc_2_country_row = country_ind
sc_2_column = "Construction (45)"
sc_2_country_column = country_ind
df_ori_2 = A_ce.loc[pd.IndexSlice[sc_2_country_row, sc_2_row],
         pd.IndexSlice[sc_2_country_column, sc_2_column]]
df_sub_2 = A.loc[pd.IndexSlice[pc_2_country_row, pc_2_row], 
               pd.IndexSlice[pc_2_country_column, pc_2_column]
               ] - A_ce.loc[pd.IndexSlice[pc_2_country_row, pc_2_row],
                            pd.IndexSlice[pc_2_country_column, pc_2_column]]
df_sub_2.index = df_ori_2.index
A_ce.loc[pd.IndexSlice[sc_2_country_row, sc_2_row],
         pd.IndexSlice[sc_2_country_column, sc_2_column]
         ]= df_ori_2 + sc_2["alpha"]*df_sub_2

## Resource efficiency (Aluminium)
### Primary change
pc_3 = {"kt": -0.9, "kp": 1} 
pc_3_row = "Aluminium production"
pc_3_country_row = country_ind
pc_3_column = "Construction (45)"
pc_3_country_column = country_ind
# implement secondary change
A_ce.loc[pd.IndexSlice[pc_3_country_row, pc_3_row],
         pd.IndexSlice[pc_3_country_column, pc_3_column]
         ] *= 1 + pc_3["kt"] * pc_3["kp"]
### Secondary change (substitution)
sc_3 = {"alpha":  456}
sc_3_row = "Re-processing of secondary aluminium into new aluminium"
sc_3_country_row = country_ind
sc_3_column = "Construction (45)"
sc_3_country_column = country_ind
df_ori_3=A_ce.loc[pd.IndexSlice[sc_3_country_row, sc_3_row],
         pd.IndexSlice[sc_3_country_column, sc_3_column]]
df_sub_3= A.loc[pd.IndexSlice[pc_3_country_row, pc_3_row], 
               pd.IndexSlice[pc_3_country_column, pc_3_column]
               ] - A_ce.loc[pd.IndexSlice[pc_3_country_row, pc_3_row],
                            pd.IndexSlice[pc_3_country_column, pc_3_column]]
df_sub_3.index = df_ori_3.index
A_ce.loc[pd.IndexSlice[sc_3_country_row, sc_3_row],
         pd.IndexSlice[sc_3_country_column, sc_3_column]
         ]= df_ori_3+ sc_3["alpha"]*df_sub_3
## Multipliers CE scenario
L_ce = np.linalg.inv(I-A_ce)
x_ce = L_ce @ Y_ce.sum(1)

va_ce = np.diag(m.loc[va_ind]) @ x_ce
emp_ce = np.diag(m.loc[emp_ind]) @ x_ce
ghg_ce = np.diag(m.loc[ghg_ind]) @ x_ce

# Step 2: Harmonization
column_labels = ['Value added', 'Employment', 'GHG']
bau = pd.DataFrame({'Value Added': va, 'Employment': emp, 'GHG': ghg}, 
                   index=A.index)
sc1 = pd.DataFrame({'Value Added': va_ce, 'Employment': emp_ce, 'GHG': ghg_ce},
                   index=A.index)
bau_sum = bau.sum()
norm = ((sc1 - bau) / bau_sum) * 100
norm = norm.fillna(0) # Replace resulting NaN values with zeros in Norm

## Changes in sign for environmental impacts
norm.loc[:,'GHG']*= -1

## Aggregation EU countries
EU27_ind =['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 
          'FR', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT',
          'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK']
norm_eu = norm.loc[pd.IndexSlice[EU27_ind,:],:]
norm_eu= norm_eu.groupby(level=1).sum()
norm_eu['country'] = ['EU']*163
norm_eu.set_index('country', append=True, inplace=True)
norm_eu=norm_eu.swaplevel('sector', 'country')

## Aggregation LATAM countries
LATAM_ind =['WL', 'BR', 'MX']
norm_latam = norm.loc[pd.IndexSlice[LATAM_ind,:],:]
norm_latam= norm_latam.groupby(level=1).sum()
norm_latam['country'] = ['LATAM']*163
norm_latam.set_index('country', append=True, inplace=True)
norm_latam =norm_latam.swaplevel('sector', 'country')

## EU + LATAM matrix
norm_new = pd.concat([norm_eu, norm_latam])

# Step 3 & 4: Concatenating dimensions, and Trade-offs and Synergies analysis

## GEO Function
def ts_geo(data, country_list, impact):
    df_ = data.copy()
    df_geo = df_.loc[pd.IndexSlice[country_list,:],impact]
    # Group by country and sector, then unstack for plotting
    grouped = df_geo.unstack(level='country')
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
    total = df_geo.groupby('country').sum()
 
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

## IMPACT Function
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

## SECTOR Function
def ts_sec(data, sector_list, impact):
    df_ = data.copy()
    df_sec = df_.loc[pd.IndexSlice[:, sector_list],impact]
    
    # Group by country and sector, then unstack for plotting
    grouped = df_sec.unstack(level='sector')
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
    total = df_sec.groupby('sector').sum()
 
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

# Examples

## Geographical trade-offs and synergies analysis
country_list =['EU', 'LATAM']
ts_geo(norm_new, country_list, va_ind)
ts_geo(norm_new, country_list, emp_ind)
ts_geo(norm_new, country_list, 'GHG')

## Impact trade-offs and synergies analysis
impact_list = ['Value Added','Employment', 'GHG']
ts_imp(norm_new, impact_list, 'EU')
ts_imp(norm_new, impact_list, 'LATAM')

## Sectoral trade-offs and synergies analysis
sector_list = ['Construction (45)',"Manufacture of basic iron and steel and of ferro-alloys and first products thereof"]
ts_sec(norm, sector_list, va_ind)
ts_sec(norm, sector_list, emp_ind)
ts_sec(norm, sector_list, 'GHG')

# Save results functions 
def save_geo_res(norm_new):
    country_list =['EU', 'LATAM']
    va_ind = "Value Added"
    emp_ind = "Employment"

    geo_va, geo_va_all, geo_va_sum = ts_geo(norm_new, country_list, va_ind)
    geo_emp, geo_emp_all, geo_emp_sum = ts_geo(norm_new, country_list, emp_ind)
    geo_ghg, geo_ghg_all, geo_ghg_sum = ts_geo(norm_new, country_list, 'GHG')
    
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
    imp_eu, imp_eu_all, imp_eu_sum = ts_imp(norm_new, impact_list, 'EU')
    imp_la, imp_la_all, imp_la_sum = ts_imp(norm_new, impact_list, 'LATAM')
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