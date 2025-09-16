import os
from typing import Dict


class ConfigLoader:
    """Utility to load configuration parameters from properties file"""
    
    @staticmethod
    def load_params(file_path: str = "params.properties") -> Dict[str, str]:
        """
        Load parameters from properties file
        :param file_path: Path to the properties file
        :return: Dictionary with parameter key-value pairs
        """
        params = {}
        
        if not os.path.exists(file_path):
            print(f"Warning: Configuration file {file_path} not found. Using defaults.")
            return params
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            params[key.strip()] = value.strip()
            
            print(f"Loaded configuration from {file_path}")
            return params
            
        except Exception as e:
            print(f"Error loading configuration file {file_path}: {e}")
            return params