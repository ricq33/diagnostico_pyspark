import pyspark.sql.functions as f
from pyspark.sql import SparkSession, WindowSpec, Window, DataFrame, Column

from minsait.ttaa.datio.common.Constants import *
from minsait.ttaa.datio.common.naming.PlayerInput import *
from minsait.ttaa.datio.common.naming.PlayerOutput import *
from minsait.ttaa.datio.utils.Writer import Writer
from minsait.ttaa.datio.utils.ExcelReader import ExcelReader


class Transformer(Writer):
    def __init__(self, spark: SparkSession):
        self.spark: SparkSession = spark
        self.excel_reader = ExcelReader(spark)
        
        # Read data from Excel
        df: DataFrame = self.read_input()
        df.printSchema()
        
        # Apply age filter if configured
        if AGE_FILTER_PARAM == 1:
            df = self.apply_age_filter(df)
            print("Applied age filter: players < 23 years only")
        
        # Apply data cleaning and transformations
        df = self.clean_data(df)
        df = self.add_player_category(df)
        df = self.add_potential_vs_overall(df)
        df = self.apply_database_filters(df)
        df = self.column_selection(df)

        # Display results
        df.show(n=100, truncate=False)
        df.printSchema()

        # Write output
        self.write(df)

    def read_input(self) -> DataFrame:
        """
        Read data from Excel file (specific sheet)
        :return: a DataFrame read from Excel file
        """
        return self.excel_reader.read_excel_sheet(INPUT_PATH, INPUT_SHEET_NAME)

    def clean_data(self, df: DataFrame) -> DataFrame:
        """
        Apply basic data cleaning transformations
        :param df: is a DataFrame with players information
        :return: a DataFrame with filter transformation applied
        """
        df = df.filter(
            (short_name.column().isNotNull()) &
            (long_name.column().isNotNull()) &
            (age.column().isNotNull()) &
            (nationality.column().isNotNull()) &
            (team_position.column().isNotNull()) &
            (overall.column().isNotNull()) &
            (potential.column().isNotNull())
        )
        return df
    
    def apply_age_filter(self, df: DataFrame) -> DataFrame:
        """
        Filter players by age if configured
        :param df: DataFrame with player data
        :return: DataFrame filtered by age
        """
        return df.filter(age.column() < 23)
    
    def add_player_category(self, df: DataFrame) -> DataFrame:
        """
        Add player_cat column based on ranking within nationality and position
        Categories:
        - A: Top 3 players in position per country
        - B: Top 5 players in position per country
        - C: Top 10 players in position per country
        - D: All other players
        """
        w: WindowSpec = Window \
            .partitionBy(nationality.column(), team_position.column()) \
            .orderBy(overall.column().desc())
        
        rank: Column = f.rank().over(w)
        
        player_category: Column = f.when(rank <= 3, "A") \
            .when(rank <= 5, "B") \
            .when(rank <= 10, "C") \
            .otherwise("D")
        
        df = df.withColumn(player_cat.name, player_category)
        return df
    
    def add_potential_vs_overall(self, df: DataFrame) -> DataFrame:
        """
        Add potential_vs_overall column (potential / overall)
        :param df: DataFrame with player data
        :return: DataFrame with potential_vs_overall column
        """
        potential_ratio: Column = potential.column() / overall.column()
        df = df.withColumn(potential_vs_overall.name, potential_ratio)
        return df
    
    def apply_database_filters(self, df: DataFrame) -> DataFrame:
        """
        Apply database cleaning filters based on player_cat and potential_vs_overall
        Filter conditions:
        - If player_cat is A or B: include
        - If player_cat is C and potential_vs_overall > 1.15: include
        - If player_cat is D and potential_vs_overall > 1.25: include
        """
        filter_condition = (
            (player_cat.column().isin(["A", "B"])) |
            ((player_cat.column() == "C") & (potential_vs_overall.column() > 1.15)) |
            ((player_cat.column() == "D") & (potential_vs_overall.column() > 1.25))
        )
        
        return df.filter(filter_condition)

    def column_selection(self, df: DataFrame) -> DataFrame:
        """
        Select final output columns for database
        :param df: is a DataFrame with players information
        :return: a DataFrame with required columns for database output
        """
        df = df.select(
            short_name.column(),
            long_name.column(),
            age.column(),
            height_cm.column(),
            weight_kg.column(),
            nationality.column(),
            club_name.column(),
            overall.column(),
            potential.column(),
            team_position.column(),
            player_cat.column(),
            potential_vs_overall.column()
        )
        return df


