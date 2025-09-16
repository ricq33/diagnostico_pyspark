"""
Database cleaning scripts for player data processing
These scripts generate SQL and data operations for database maintenance
"""

import pandas as pd
from typing import List, Dict, Any
import os


class DatabaseCleaningScripts:
    """Generate scripts for database cleaning operations"""
    
    def __init__(self, processed_data: pd.DataFrame):
        self.data = processed_data
    
    def generate_data_quality_report(self) -> str:
        """Generate a data quality report for database administrators"""
        report = []
        report.append("=== DATA QUALITY REPORT ===")
        report.append(f"Total records processed: {len(self.data)}")
        report.append(f"Unique players: {self.data['short_name'].nunique()}")
        report.append(f"Unique nationalities: {self.data['nationality'].nunique()}")
        report.append(f"Unique clubs: {self.data['club_name'].nunique()}")
        report.append(f"Unique positions: {self.data['team_position'].nunique()}")
        
        report.append("\nPlayer Category Distribution:")
        cat_dist = self.data['player_cat'].value_counts().sort_index()
        for cat, count in cat_dist.items():
            percentage = (count / len(self.data)) * 100
            report.append(f"  Category {cat}: {count} players ({percentage:.1f}%)")
        
        report.append(f"\nAge distribution:")
        report.append(f"  Average age: {self.data['age'].mean():.1f} years")
        report.append(f"  Min age: {self.data['age'].min()} years")
        report.append(f"  Max age: {self.data['age'].max()} years")
        
        report.append(f"\nPotential vs Overall ratio:")
        report.append(f"  Average ratio: {self.data['potential_vs_overall'].mean():.3f}")
        report.append(f"  Players with high potential (>1.2): {len(self.data[self.data['potential_vs_overall'] > 1.2])}")
        
        return "\n".join(report)
    
    def generate_create_table_script(self, table_name: str = "clean_players") -> str:
        """Generate CREATE TABLE script for the cleaned data"""
        script = f"""
-- Create table for cleaned player data
CREATE TABLE IF NOT EXISTS {table_name} (
    short_name VARCHAR(100) NOT NULL,
    long_name VARCHAR(200) NOT NULL,
    age INT NOT NULL,
    height_cm INT,
    weight_kg INT,
    nationality VARCHAR(100) NOT NULL,
    club_name VARCHAR(200),
    overall_rating INT NOT NULL,
    potential_rating INT NOT NULL,
    team_position VARCHAR(10) NOT NULL,
    player_category CHAR(1) NOT NULL CHECK (player_category IN ('A', 'B', 'C', 'D')),
    potential_vs_overall DECIMAL(5,3) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (short_name, nationality, team_position)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_nationality ON {table_name}(nationality);
CREATE INDEX IF NOT EXISTS idx_position ON {table_name}(team_position);
CREATE INDEX IF NOT EXISTS idx_category ON {table_name}(player_category);
CREATE INDEX IF NOT EXISTS idx_overall ON {table_name}(overall_rating);
CREATE INDEX IF NOT EXISTS idx_potential_ratio ON {table_name}(potential_vs_overall);
"""
        return script
    
    def generate_data_validation_script(self, table_name: str = "clean_players") -> str:
        """Generate data validation queries for database integrity"""
        script = f"""
-- Data validation queries for {table_name}
-- Run these queries to ensure data integrity after loading

-- 1. Check for duplicate records
SELECT short_name, nationality, team_position, COUNT(*) as count
FROM {table_name}
GROUP BY short_name, nationality, team_position
HAVING COUNT(*) > 1;

-- 2. Validate player categories
SELECT player_category, COUNT(*) as count
FROM {table_name}
GROUP BY player_category
ORDER BY player_category;

-- 3. Check potential vs overall ratio bounds
SELECT 
    MIN(potential_vs_overall) as min_ratio,
    MAX(potential_vs_overall) as max_ratio,
    AVG(potential_vs_overall) as avg_ratio
FROM {table_name};

-- 4. Validate age ranges
SELECT 
    MIN(age) as min_age,
    MAX(age) as max_age,
    AVG(age) as avg_age
FROM {table_name};

-- 5. Check for null values (should be none after cleaning)
SELECT 
    SUM(CASE WHEN short_name IS NULL THEN 1 ELSE 0 END) as null_short_name,
    SUM(CASE WHEN nationality IS NULL THEN 1 ELSE 0 END) as null_nationality,
    SUM(CASE WHEN team_position IS NULL THEN 1 ELSE 0 END) as null_position,
    SUM(CASE WHEN overall_rating IS NULL THEN 1 ELSE 0 END) as null_overall
FROM {table_name};

-- 6. Top performers by category
SELECT player_category, short_name, nationality, team_position, overall_rating
FROM {table_name}
WHERE player_category IN ('A', 'B')
ORDER BY player_category, overall_rating DESC
LIMIT 20;
"""
        return script
    
    def generate_cleanup_script(self, table_name: str = "clean_players") -> str:
        """Generate cleanup script for removing low-quality data"""
        script = f"""
-- Cleanup script for removing low-quality player data from {table_name}
-- Use with caution - this will permanently delete data

-- 1. Remove players with very low potential ratio (if needed)
-- DELETE FROM {table_name} 
-- WHERE player_category = 'D' AND potential_vs_overall < 1.1;

-- 2. Remove players above certain age for specific analysis
-- DELETE FROM {table_name} 
-- WHERE age > 35;

-- 3. Remove duplicate entries (keep the one with highest overall rating)
-- DELETE t1 FROM {table_name} t1
-- INNER JOIN {table_name} t2 
-- WHERE t1.short_name = t2.short_name 
--   AND t1.nationality = t2.nationality
--   AND t1.team_position = t2.team_position
--   AND t1.overall_rating < t2.overall_rating;

-- 4. Archive old data (example)
-- CREATE TABLE {table_name}_archive AS 
-- SELECT * FROM {table_name} 
-- WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- 5. Update statistics after cleanup
-- ANALYZE TABLE {table_name};
"""
        return script
    
    def save_all_scripts(self, output_dir: str = "database_scripts"):
        """Save all generated scripts to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save data quality report
        with open(f"{output_dir}/data_quality_report.txt", "w") as f:
            f.write(self.generate_data_quality_report())
        
        # Save SQL scripts
        with open(f"{output_dir}/01_create_table.sql", "w") as f:
            f.write(self.generate_create_table_script())
        
        with open(f"{output_dir}/02_data_validation.sql", "w") as f:
            f.write(self.generate_data_validation_script())
        
        with open(f"{output_dir}/03_cleanup_operations.sql", "w") as f:
            f.write(self.generate_cleanup_script())
        
        print(f"Database cleaning scripts saved to {output_dir}/")


def generate_database_scripts_from_excel(excel_path: str, sheet_name: str):
    """Main function to generate database scripts from Excel data"""
    
    print("Reading Excel file and processing data...")
    
    # Read and clean data
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    # Apply the same cleaning logic as in our PySpark implementation
    df_clean = df.dropna(subset=['short_name', 'long_name', 'age', 'nationality', 
                                'team_position', 'overall', 'potential']).copy()
    
    # Add player categories
    df_clean['rank'] = df_clean.groupby(['nationality', 'team_position'])['overall'].rank(method='min', ascending=False)
    
    def categorize_player(rank):
        if rank <= 3:
            return 'A'
        elif rank <= 5:
            return 'B'
        elif rank <= 10:
            return 'C'
        else:
            return 'D'
    
    df_clean['player_cat'] = df_clean['rank'].apply(categorize_player)
    
    # Add potential vs overall ratio
    df_clean['potential_vs_overall'] = df_clean['potential'] / df_clean['overall']
    
    # Apply database filters
    filter_condition = (
        (df_clean['player_cat'].isin(['A', 'B'])) |
        ((df_clean['player_cat'] == 'C') & (df_clean['potential_vs_overall'] > 1.15)) |
        ((df_clean['player_cat'] == 'D') & (df_clean['potential_vs_overall'] > 1.25))
    )
    
    df_filtered = df_clean[filter_condition]
    
    # Select final columns
    final_columns = ['short_name', 'long_name', 'age', 'height_cm', 'weight_kg', 
                    'nationality', 'club_name', 'overall', 'potential', 'team_position',
                    'player_cat', 'potential_vs_overall']
    
    df_final = df_filtered[final_columns]
    
    print(f"Processed {len(df_final)} quality player records")
    
    # Generate database scripts
    db_scripts = DatabaseCleaningScripts(df_final)
    db_scripts.save_all_scripts()
    
    return df_final


if __name__ == "__main__":
    # Example usage
    repo_root = "/home/runner/work/diagnostico_pyspark/diagnostico_pyspark"
    excel_path = os.path.join(repo_root, "resources/data/players_21.xlsx")
    
    df = generate_database_scripts_from_excel(excel_path, "players_data")
    print(f"\nGenerated database cleaning scripts for {len(df)} player records")