import pandas as pd
import tempfile
import os
from pyspark.sql import SparkSession, DataFrame


class ExcelReader:
    """Utility class to read Excel files and convert them to PySpark DataFrames"""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
    
    def read_excel_sheet(self, excel_path: str, sheet_name: str) -> DataFrame:
        """
        Read a specific sheet from an Excel file and return a PySpark DataFrame
        
        :param excel_path: Path to the Excel file
        :param sheet_name: Name of the sheet to read
        :return: PySpark DataFrame
        """
        try:
            # Read Excel file with pandas
            print(f"Reading Excel file: {excel_path}, Sheet: {sheet_name}")
            df_pandas = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            print(f"Excel sheet contains {len(df_pandas)} rows and {len(df_pandas.columns)} columns")
            
            # Create temporary CSV file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
                temp_csv_path = temp_file.name
                df_pandas.to_csv(temp_csv_path, index=False)
            
            # Read CSV into PySpark DataFrame
            df_spark = self.spark.read \
                .option("header", True) \
                .option("inferSchema", True) \
                .csv(temp_csv_path)
            
            # Clean up temporary file
            os.unlink(temp_csv_path)
            
            print(f"Successfully converted Excel to PySpark DataFrame")
            return df_spark
            
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            raise e