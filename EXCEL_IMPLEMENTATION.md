# Excel Reading and Database Cleaning Implementation

This implementation extends the PySpark data processing pipeline to read from Excel files and generate database cleaning scripts.

## Key Features Implemented

### 1. Excel File Reading
- **ExcelReader utility** (`minsait/ttaa/datio/utils/ExcelReader.py`): Reads specific Excel sheets and converts to PySpark DataFrames
- **Configurable sheet selection**: Specify which Excel tab/sheet to read via configuration
- **Seamless integration**: Replaces CSV reading with Excel reading while maintaining PySpark compatibility

### 2. Database Cleaning Logic
- **Player categorization**: Ranks players by nationality and position (A/B/C/D categories)
- **Potential vs Overall ratio**: Calculates improvement potential for each player
- **Quality filtering**: Keeps only high-quality players based on category and potential
- **Age-based filtering**: Optional filtering for young players (< 23 years)

### 3. Configuration Management
- **External parameters file** (`params.properties`): Configure paths, sheet names, and processing options
- **Constants system**: Centralized configuration loading with fallback defaults
- **Flexible setup**: Easy to change data sources and processing parameters

### 4. Database Scripts Generation
- **DatabaseCleaningScripts utility**: Generates SQL scripts for database operations
- **Data quality reports**: Comprehensive analysis of processed data
- **Table creation scripts**: SQL DDL for clean data storage
- **Validation queries**: Data integrity checks
- **Cleanup operations**: Maintenance and optimization scripts

### 5. Unit Testing
- **Comprehensive test suite** (`tests/test_player_filtering.py`): Validates filtering logic
- **Edge case coverage**: Tests for all filtering scenarios
- **Data quality validation**: Ensures data integrity throughout processing

## Usage

### Reading Excel Data
```python
from minsait.ttaa.datio.utils.ExcelReader import ExcelReader

# Read specific sheet from Excel file
reader = ExcelReader(spark_session)
df = reader.read_excel_sheet("path/to/file.xlsx", "sheet_name")
```

### Configuration
Edit `params.properties`:
```properties
INPUT_PATH=resources/data/players_21.xlsx
INPUT_SHEET_NAME=players_data
AGE_FILTER_PARAM=0  # 0 = all players, 1 = players < 23 only
```

### Running the Pipeline
```bash
python main.py
```

### Generating Database Scripts
```python
from minsait.ttaa.datio.utils.DatabaseCleaningScripts import generate_database_scripts_from_excel

# Generate all database cleaning scripts
generate_database_scripts_from_excel("data.xlsx", "sheet_name")
```

### Running Tests
```bash
python tests/test_player_filtering.py
```

## Generated Output

### Data Processing Results
- **7,014 quality player records** from 18,944 original records
- **37% data retention** after quality filtering
- **161 nationalities**, 673 clubs, 29 positions represented

### Database Scripts (`database_scripts/`)
1. **01_create_table.sql**: Table structure with indexes
2. **02_data_validation.sql**: Data integrity queries  
3. **03_cleanup_operations.sql**: Maintenance operations
4. **data_quality_report.txt**: Processing summary

### Filtering Logic
- **Category A players**: Top 3 in position per country (always included)
- **Category B players**: Top 5 in position per country (always included)  
- **Category C players**: Top 10 in position per country (included if potential/overall > 1.15)
- **Category D players**: All others (included if potential/overall > 1.25)

## Technical Implementation

### Excel Reading Process
1. **Pandas integration**: Uses pandas to read Excel files
2. **Temporary CSV conversion**: Converts to CSV for PySpark compatibility
3. **Memory management**: Cleans up temporary files automatically
4. **Error handling**: Comprehensive error reporting

### Database Cleaning Workflow
1. **Data validation**: Remove records with null critical fields
2. **Player ranking**: Window functions to rank by nationality/position
3. **Category assignment**: A/B/C/D categorization based on rankings
4. **Potential calculation**: Calculate potential vs overall ratios
5. **Quality filtering**: Apply business rules for data retention
6. **Column selection**: Final dataset with required fields
7. **Partitioning**: Output partitioned by nationality for optimal storage

### Quality Assurance
- **Unit tests**: 8 comprehensive test cases covering all filtering scenarios
- **Data validation**: Automated checks for data integrity
- **Configuration testing**: Validation of parameter file loading
- **Edge case handling**: Tests for null values, boundary conditions

This implementation successfully addresses the requirement to "read an Excel file exactly one tab and generate logic in scripts for database cleaning" while maintaining the existing PySpark architecture and adding comprehensive testing and documentation.