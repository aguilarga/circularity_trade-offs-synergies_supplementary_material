# Circularity Trade-offs and Synergies Analysis - Supplementary Information
This repository contains the supplementary material for the paper "How to measure Circularity Trade-offs and Synergies?" based on the conference paper "An MR EEIO-based framework for identifying synergies and trade-offs of circularity interventions"

## ts_analysis_v3.0.py
This code includes all functions for assessing trade-offs and synergies with an MR EEIO Scenario Analysis, including geographical, impact and sectoral dimensions.

***Note on Data:*** Results were obtained by using ***EXIOBASE v3.9.5*** (https://zenodo.org/records/14869924). Before running the code, please download 
***IOT_2020_ixi*** folder 
***Note on Software:*** This code runs with Multifunctional Assessment of Regions through Input-Output (MARIO) Software. Before running the code, please download 
***MARIO Software*** available at: https://github.com/it-is-me-mario/MARIO/blob/dev/doc/source/index.rst

## ts_analysis_v3.0.py
This code aggregates Emissions extensions from EXIOBASE v3.9.5 and covert the emissions into GHG emissions in CO2eq using Global Warming Potential (GWP-100) from the IPCC AR6. Available at: https://zenodo.org/records/6483002

## data input (aggregated) + assumptions.xlsx
This file includes an aggregated version EXIOBASE v3.9.5 using MARIO software and the details for the scenario analysis

## MARIO_Extensions&Aggregations
This folder contains Excel files to run the aggregation of EXIOBASE, and the addition of the GHG emissions extension from ***ghg_exiobase_v3.9.5.py***

## geo_results.xlsx
Results from ***ts_analysis_v3.0.py*** by running ***save_geo_res()*** function, which returns the outcomes of the geographical analysis of trade-offs and synergies.
