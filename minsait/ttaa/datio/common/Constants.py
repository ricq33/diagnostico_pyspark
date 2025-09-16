import os

# Load configuration from params file if available
def load_config():
    config = {}
    params_file = "params.properties"
    
    if os.path.exists(params_file):
        try:
            with open(params_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error loading configuration: {e}")
    
    return config

# Load configuration
config = load_config()

# Default values
SPARK_MODE = config.get("SPARK_MODE", "local[*]")
HEADER = "header"
INFER_SCHEMA = "inferSchema"
INPUT_PATH = config.get("INPUT_PATH", "resources/data/players_21.xlsx")
INPUT_SHEET_NAME = config.get("INPUT_SHEET_NAME", "players_data")
OUTPUT_PATH = config.get("OUTPUT_PATH", "resources/data/output")
OVERWRITE = "overwrite"
AGE_FILTER_PARAM = int(config.get("AGE_FILTER_PARAM", "0"))  # 0 = all players, 1 = players < 23 years only
