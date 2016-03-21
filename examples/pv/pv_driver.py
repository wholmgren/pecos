import pecos
import datetime
import yaml
import pv_application
import os

# Input
system_name = 'Baseline_System'
analysis_date = datetime.date(2015, 11, 11)
config_file = 'Baseline_config.yml'

# Open config file and extract information
fid = open(config_file, 'r')
config = yaml.load(fid)
fid.close()
general = config['General'] 
MET_trans = config['MET Translation'] # translation dictonary for weather file
BASE_trans = config['Baseline6kW Translation'] # translation dictonary for pv file
specs = config['Specifications']
composite_signals = config['Composite Signals']
corrupt_values = config['Corrupt Values']
range_bounds = config['Range Bounds']
increment_bounds = config['Increment Bounds']

 # Define output files and directories
results_directory = 'Results'
if not os.path.exists(results_directory):
    os.makedirs(results_directory)
results_subdirectory = os.path.join(results_directory, system_name + str(analysis_date))
if not os.path.exists(results_subdirectory):
    os.makedirs(results_subdirectory)
metrics_file = os.path.join(results_directory, system_name + '_metrics.csv')
test_results_file = os.path.join(results_subdirectory, system_name + '_test_results.csv')
report_file =  os.path.join(results_subdirectory, system_name + '.html')

# Create an PerformanceMonitoring instance
pm = pecos.monitoring.PerformanceMonitoring()

# Add pv system data
database_name = 'Baseline6kW'
database_file = database_name + analysis_date.strftime(general['Date Format']) + '.dat'
df = pecos.io.read_campbell_scientific(database_file, general['Index Column'], encoding='utf-16')
df.index = df.index.tz_localize(specs['Timezone'])
pm.add_dataframe(df, database_name)
pm.add_translation_dictonary(BASE_trans, database_name)
    
# Add weather data
database_name = 'MET'
database_file = database_name + analysis_date.strftime(general['Date Format']) + '.dat'
df = pecos.io.read_campbell_scientific(database_file, general['Index Column'], encoding='utf-16')
df.index = df.index.tz_localize(specs['Timezone'])
pm.add_dataframe(df, database_name)
pm.add_translation_dictonary(MET_trans, database_name)

# Check timestamp
pm.check_timestamp(specs['Frequency']) 
    
# Generate time filter
time_filter = pv_application.calculate_time_filter(pm.df.index, specs)  
pm.add_time_filter(time_filter)

# Check missing
pm.check_missing()

# Check corrupt
pm.check_corrupt(corrupt_values) 

# Add composite signals
for composite_signal in composite_signals:
    for key,value in composite_signal.items():
        signal = pm.evaluate_string(key, value, specs)
        pm.add_signal(key, signal)

# Check range
for key,value in range_bounds.items():
    pm.check_range(value, key, specs) 

# Check increment
for key,value in increment_bounds.items():
    pm.check_increment([value[0], value[1]], key, specs, min_failures=value[2]) 
    
# Compute metrics
QCI = pecos.metrics.qci(pm)
pv_metrics = pv_application.metrics(pm)
metrics = QCI.join(pv_metrics)

# Generate custom graphics
filename = os.path.join(results_subdirectory, system_name)
pv_application.graphics(filename, pm)

# Generate report
pecos.io.write_metrics(metrics_file, metrics)
pecos.io.write_test_results(test_results_file, pm.test_results)
pecos.io.write_monitoring_report(report_file, results_subdirectory, pm, metrics, config)
    
