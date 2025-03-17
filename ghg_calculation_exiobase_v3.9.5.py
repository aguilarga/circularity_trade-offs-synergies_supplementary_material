# -*- coding: utf-8 -*-
"""

This code retrieves emissions extensions from EXIOBASE and converted  
into GHG emissions in CO2eq using Global Warming Potential values from IPPC-AR6

Python version: v3.10.16

EXIOBASE version: v3.9.5 ixi_2020 

Data access: https://zenodo.org/records/14869924

Author: aguilarga (https://github.com/aguilarga)

Latest update: March 15, 2025
"""

# Import packages
import pandas as pd

# Import data
    
exio_path = 'IOT_2020_ixi_v3.9.5' # Add/Change directory for database folder

# Emissions extension
env_ext = pd.read_csv(exio_path +'/air_emissions/F.txt', sep='\t', index_col=[0], header=[0, 1])  # impacts matrix

# GWP values (IPCC AR6 data in https://zenodo.org/records/6483002)
gwp_values = {
    # Carbon Dioxide (CO2)
    'CO2 - combustion - air': 1,
    'CO2 - agriculture - peat decay - air': 1,
    
    # Methane (CH4)
    'CH4 - combustion - air': 27,
    'CH4 - agriculture - air': 27,
    
    # Nitrous Oxide (N2O)
    'N2O - combustion - air': 273,
    'N2O - agriculture - air': 273,
    
    # Sulfur Hexafluoride (SF6)
    'SF6 - air': 25200,
    
    # Hydrofluorocarbons (HFCs)
    'HFC - air': 1,  # In kg CO2-eq from EXIOBASE
    
    # Perfluorocarbons (PFCs)
    'PFC - air': 1  # In kg CO2-eq from EXIOBASE
}

    # Filter relevant emissions and apply GWP values
ghg_emissions = env_ext.loc[env_ext.index.intersection(gwp_values.keys())]  # Select GHGs
ghg_emissions_gwp = ghg_emissions.mul(pd.Series(gwp_values), axis=0)  # Apply GWP values
ghg_gwp_sum = ghg_emissions_gwp.sum()

ghg_gwp_sum.to_excel("ghg_emissions_extension.xlsx", index=False)