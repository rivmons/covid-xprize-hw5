import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse
from covid_xprize.standard_predictor.xprize_predictor import NPI_COLUMNS
from covid_xprize.scoring.prescriptor_scoring import weight_prescriptions_by_cost
from covid_xprize.scoring.prescriptor_scoring import generate_cases_and_stringency_for_prescriptions
from covid_xprize.scoring.prescriptor_scoring import compute_domination_df
from covid_xprize.scoring.prescriptor_scoring import compute_pareto_set
from covid_xprize.validation.prescriptor_validation import validate_submission
import multiprocessing as mp

# Can set these longer for better evaluation. Will increase eval time
START_DATE = "2020-08-01"
END_DATE = "2020-08-05"

from covid_xprize.scoring.predictor_scoring import load_dataset
from covid_xprize.validation.scenario_generator import generate_scenario

# parser = argparse.ArgumentParser()
# parser.add_argument('-coeff', required=True)
# parser.add_argument('-checkpoint', required=True)
# args = parser.parse_args()

# print(args.coeff, args.checkpoint)

LATEST_DATA_URL = 'https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker-legacy/main/legacy_data_202207/OxCGRT_latest.csv'
GEO_FILE = "countries_regions.csv"

latest_df = load_dataset(LATEST_DATA_URL, GEO_FILE)

IP_FILE = "robojudge_test_scenario.csv"
countries = None
scenario_df = generate_scenario(START_DATE, END_DATE, latest_df, countries, scenario="Freeze")
scenario_df.to_csv(IP_FILE, index=False)

# Cost weightings for each IP for each geo
TEST_COST = "covid_xprize/validation/data/uniform_random_costs.csv"

prescription_files = {
    'NeatNSGA': f'covid_xprize/examples/prescriptors/neat/nsga2/test_prescriptions_nsga2.csv',
    'Neat_0.1': f'covid_xprize/examples/prescriptors/neat/prescriptions/test_prescriptions_0.1.csv',
    # 'Neat_0.2': f'covid_xprize/examples/prescriptors/neat/prescriptions/test_prescriptions_0.2.csv',
    # 'Neat_0.3': f'covid_xprize/examples/prescriptors/neat/prescriptions/test_prescriptions_0.3.csv',
    # 'Neat_0.4': f'covid_xprize/examples/prescriptors/neat/prescriptions/test_prescriptions_0.4.csv',
    # 'Neat_0.5': f'covid_xprize/examples/prescriptors/neat/prescriptions/test_prescriptions_0.5.csv',
    # 'Neat_0.6': f'covid_xprize/examples/prescriptors/neat/prescriptions/test_prescriptions_0.6.csv',
    # 'Neat_0.7': f'covid_xprize/examples/prescriptors/neat/prescriptions/test_prescriptions_0.7.csv',
    # 'Neat_0.8': f'covid_xprize/examples/prescriptors/neat/prescriptions/test_prescriptions_0.8.csv',
    'Neat_0.9': f'covid_xprize/examples/prescriptors/neat/prescriptions/test_prescriptions_0.9.csv'
    # 'Neat_0.55': f'covid_xprize/examples/prescriptors/neat/prescriptions/test_prescriptions_0.55.csv'


    # 'Random1': 'covid_xprize/examples/prescriptors/random/prescriptions/random_presc_1.csv',
    # 'Random2': 'covid_xprize/examples/prescriptors/random/prescriptions/random_presc_2.csv',
    # 'BlindGreedy': 'covid_xprize/examples/prescriptors/blind_greedy/prescriptions/blind_greedy.csv',
}

# Validate the prescription files
for prescriptor_name, output_file in prescription_files.items():
    errors = validate_submission(START_DATE, END_DATE, IP_FILE, output_file)
    if errors:
        for error in errors:
            print(f"{prescriptor_name}: {error}")
    else:
        print(f"{prescriptor_name}: All good!")
        
def gen_cs_prescriptions(prescription_name, prescription_file):
    df, preds = generate_cases_and_stringency_for_prescriptions(START_DATE, END_DATE, prescription_file, TEST_COST, IP_FILE)
    return (prescription_name, df)
        
# Collect case and stringency data for all prescriptors
dfs = []
params = sorted(prescription_files.items())
cpus = np.min([mp.cpu_count(), len(params)])
print(params)
with mp.Pool(cpus) as p:
    presc_mp = p.starmap(gen_cs_prescriptions, params)
    p.close()
    p.join()

for name, df_p in presc_mp:
    print(name, df_p.head())
    df_p['PrescriptorName'] = name
    dfs.append(df_p)

# for prescriptor_name, prescription_file in sorted(prescription_files.items()):
#     print("Generating predictions for", prescriptor_name)
#     df, preds = generate_cases_and_stringency_for_prescriptions(START_DATE, END_DATE, prescription_file, TEST_COST, IP_FILE)
#     df['PrescriptorName'] = prescriptor_name
#     dfs.append(df)
df = pd.concat(dfs)

ddf = compute_domination_df(df)

# Get number of dominated prescriptions for each submission. This is the "Domination Count"
ddf.groupby('DominatingName', group_keys=False).count().sort_values('DominatedIndex', ascending=False)['DominatedIndex']

def plot_pareto_curve(objective1_list, objective2_list):
    """
    Plot the pareto curve given the objective values for a set of solutions.
    This curve indicates the area dominated by the solution set, i.e., 
    every point up and to the right is dominated.
    """
    
    # Compute pareto set from full solution set.
    objective1_pareto, objective2_pareto = compute_pareto_set(objective1_list, 
                                                              objective2_list)
    
    # Sort by first objective.
    objective1_pareto, objective2_pareto = list(zip(*sorted(zip(objective1_pareto,
                                                                objective2_pareto))))
    
    # Compute the coordinates to plot.
    xs = []
    ys = []
    
    xs.append(objective1_pareto[0])
    ys.append(objective2_pareto[0])
    
    for i in range(0, len(objective1_pareto)-1):
        
        # Add intermediate point between successive solutions
        xs.append(objective1_pareto[i+1])
        ys.append(objective2_pareto[i])
        
        # Add next solution on front
        xs.append(objective1_pareto[i+1])
        ys.append(objective2_pareto[i+1])
        
    plt.plot(xs, ys)
    
# Plot overall stringency and cases of each prescription
plt.figure(figsize=(10,8))
for prescriptor_name in prescription_files:
    pdf = df[df['PrescriptorName'] == prescriptor_name]
    overall_pdf = pdf.groupby('PrescriptionIndex', group_keys=False).mean().reset_index()
    print(overall_pdf['Stringency'], overall_pdf['PredictedDailyNewCases'])
    plt.scatter(overall_pdf['Stringency'],
                overall_pdf['PredictedDailyNewCases'], 
                label=prescriptor_name)
    plot_pareto_curve(list(overall_pdf['Stringency']),
                      list(overall_pdf['PredictedDailyNewCases']))
plt.xlabel('Mean stringency')
plt.ylabel('Mean cases per day per geo')
plt.legend()
plt.savefig(f'covid_xprize/examples/prescriptors/neat/nsga2/pareto_bounded.png')
plt.close()

# Plot stacked line chart of npis over time for a prescription for a particular geo

#submission_file = 'covid_xprize.examples/prescriptors/neat/test_prescriptions/pres.csv'
submission_file = 'covid_xprize/examples/prescriptors/random/prescriptions/random_presc_1.csv'

prescription_index = 2
country_name = 'United States'
region_name = None

pdf = pd.read_csv(submission_file)
gdf = pdf[(pdf['PrescriptionIndex'] == prescription_index) &
          (pdf['CountryName'] == country_name) &
          (pdf['RegionName'].isna() if region_name is None else (pdf['RegionName'] == 'region_name'))]
gdf.plot.area(x='Date', y=NPI_COLUMNS, figsize=(10,8), ylabel='Stringency')
# plt.savefig(f'covid_xprize/examples/prescriptors/neat/prescriptions/gdf_all.png')
# plt.close()

# Plot stringency and cases of each prescription for a particular country
# country_name = 'Aruba'
# cdf = df[df.CountryName == country_name]

# plt.figure(figsize=(10,8))
# for prescriptor_name in prescription_files:
#     pdf = cdf[cdf['PrescriptorName'] == prescriptor_name]
#     #overall_pdf = pdf.groupby('PrescriptionIndex', group_keys=False).mean().reset_index()
#     plt.scatter(pdf['Stringency'],
#                 pdf['PredictedDailyNewCases'], 
#                 label=prescriptor_name)
#     plot_pareto_curve(list(pdf['Stringency']),
#                       list(pdf['PredictedDailyNewCases']))
# plt.xlabel('Mean stringency')
# plt.ylabel('Mean cases per day per geo')
# plt.title(country_name)
# plt.legend()
# plt.show()
