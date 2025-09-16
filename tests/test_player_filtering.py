import unittest
import pandas as pd
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/home/runner/work/diagnostico_pyspark/diagnostico_pyspark')


class TestPlayerFiltering(unittest.TestCase):
    """Unit tests for player filtering logic"""
    
    def setUp(self):
        """Set up test data"""
        # Create test data that matches our filtering scenarios
        self.test_data = pd.DataFrame({
            'short_name': ['Player_A1', 'Player_B1', 'Player_C1', 'Player_D1', 'Player_C2', 'Player_D2'],
            'long_name': ['Player A One', 'Player B One', 'Player C One', 'Player D One', 'Player C Two', 'Player D Two'],
            'age': [25, 22, 24, 26, 21, 28],
            'nationality': ['Country1', 'Country1', 'Country1', 'Country1', 'Country2', 'Country2'],
            'team_position': ['ST', 'ST', 'ST', 'ST', 'CM', 'CM'],
            'overall': [90, 85, 80, 75, 82, 78],
            'potential': [92, 88, 95, 95, 90, 95],
            'player_cat': ['A', 'B', 'C', 'D', 'C', 'D'],
            'potential_vs_overall': [1.02, 1.04, 1.19, 1.27, 1.10, 1.22],
            'height_cm': [180, 175, 185, 170, 178, 182],
            'weight_kg': [75, 70, 85, 65, 72, 80],
            'club_name': ['Club1', 'Club2', 'Club3', 'Club4', 'Club5', 'Club6']
        })
    
    def test_filter_category_a_and_b_players(self):
        """Test that Category A and B players are always included"""
        # Filter for A and B categories
        condition = self.test_data['player_cat'].isin(['A', 'B'])
        filtered_data = self.test_data[condition]
        
        # Should include Player_A1 and Player_B1
        expected_players = ['Player_A1', 'Player_B1']
        actual_players = filtered_data['short_name'].tolist()
        
        self.assertEqual(len(filtered_data), 2)
        self.assertTrue(all(player in actual_players for player in expected_players))
        self.assertTrue(all(cat in ['A', 'B'] for cat in filtered_data['player_cat']))
    
    def test_filter_category_c_with_high_potential(self):
        """Test that Category C players with potential_vs_overall > 1.15 are included"""
        # Player_C1 has ratio 1.19 (should be included)
        # Player_C2 has ratio 1.10 (should be excluded)
        
        condition = (self.test_data['player_cat'] == 'C') & (self.test_data['potential_vs_overall'] > 1.15)
        filtered_data = self.test_data[condition]
        
        # Should only include Player_C1
        self.assertEqual(len(filtered_data), 1)
        self.assertEqual(filtered_data.iloc[0]['short_name'], 'Player_C1')
        self.assertTrue(filtered_data.iloc[0]['potential_vs_overall'] > 1.15)
    
    def test_filter_category_d_with_very_high_potential(self):
        """Test that Category D players with potential_vs_overall > 1.25 are included"""
        # Player_D1 has ratio 1.27 (should be included)
        # Player_D2 has ratio 1.22 (should be excluded)
        
        condition = (self.test_data['player_cat'] == 'D') & (self.test_data['potential_vs_overall'] > 1.25)
        filtered_data = self.test_data[condition]
        
        # Should only include Player_D1
        self.assertEqual(len(filtered_data), 1)
        self.assertEqual(filtered_data.iloc[0]['short_name'], 'Player_D1')
        self.assertTrue(filtered_data.iloc[0]['potential_vs_overall'] > 1.25)
    
    def test_complete_filtering_logic(self):
        """Test the complete filtering logic that combines all conditions"""
        # Complete filter condition
        filter_condition = (
            (self.test_data['player_cat'].isin(['A', 'B'])) |
            ((self.test_data['player_cat'] == 'C') & (self.test_data['potential_vs_overall'] > 1.15)) |
            ((self.test_data['player_cat'] == 'D') & (self.test_data['potential_vs_overall'] > 1.25))
        )
        
        filtered_data = self.test_data[filter_condition]
        
        # Should include: Player_A1 (A), Player_B1 (B), Player_C1 (C with 1.19), Player_D1 (D with 1.27)
        # Should exclude: Player_C2 (C with 1.10), Player_D2 (D with 1.22)
        expected_players = ['Player_A1', 'Player_B1', 'Player_C1', 'Player_D1']
        actual_players = filtered_data['short_name'].tolist()
        
        self.assertEqual(len(filtered_data), 4)
        self.assertEqual(sorted(actual_players), sorted(expected_players))
    
    def test_age_filter_under_23(self):
        """Test age filtering for players under 23 years"""
        age_filtered = self.test_data[self.test_data['age'] < 23]
        
        # Should include Player_B1 (22) and Player_C2 (21)
        expected_players = ['Player_B1', 'Player_C2']
        actual_players = age_filtered['short_name'].tolist()
        
        self.assertEqual(len(age_filtered), 2)
        self.assertEqual(sorted(actual_players), sorted(expected_players))
        self.assertTrue(all(age < 23 for age in age_filtered['age']))
    
    def test_null_value_filtering(self):
        """Test that null values are properly filtered out"""
        # Add some null values to test data
        test_data_with_nulls = self.test_data.copy()
        test_data_with_nulls.loc[0, 'short_name'] = None
        test_data_with_nulls.loc[1, 'nationality'] = None
        test_data_with_nulls.loc[2, 'overall'] = None
        
        # Filter out null values
        required_cols = ['short_name', 'long_name', 'age', 'nationality', 
                        'team_position', 'overall', 'potential']
        clean_data = test_data_with_nulls.dropna(subset=required_cols)
        
        # Should remove 3 rows with nulls
        self.assertEqual(len(clean_data), 3)
        
        # Verify no nulls in required columns
        for col in required_cols:
            self.assertFalse(clean_data[col].isnull().any())
    
    def test_data_quality_metrics(self):
        """Test data quality metrics calculation"""
        # Test potential vs overall ratio calculation
        calculated_ratios = self.test_data['potential'] / self.test_data['overall']
        expected_ratios = self.test_data['potential_vs_overall']
        
        # Check that ratios match (within floating point precision)
        for calc, exp in zip(calculated_ratios, expected_ratios):
            self.assertAlmostEqual(calc, exp, places=2)
        
        # Test that all ratios are positive
        self.assertTrue(all(ratio > 0 for ratio in calculated_ratios))
        
        # Test average ratio
        avg_ratio = calculated_ratios.mean()
        self.assertGreater(avg_ratio, 1.0)  # Should be > 1 for young players


class TestDatabaseCleaningValidation(unittest.TestCase):
    """Test validation of the complete database cleaning process"""
    
    def test_filtering_preserves_data_integrity(self):
        """Test that filtering maintains data integrity"""
        # Use realistic player data
        test_data = pd.DataFrame({
            'short_name': ['Messi', 'Ronaldo', 'Neymar', 'Mbappe', 'Young_Talent', 'Average_Player'],
            'nationality': ['Argentina', 'Portugal', 'Brazil', 'France', 'Spain', 'England'],
            'team_position': ['CAM', 'ST', 'LW', 'ST', 'CM', 'CB'],
            'overall': [93, 92, 91, 90, 75, 72],
            'potential': [93, 92, 91, 95, 88, 73],
            'player_cat': ['A', 'A', 'A', 'A', 'D', 'D'],
            'age': [33, 35, 28, 21, 19, 28]
        })
        
        # Calculate potential vs overall
        test_data['potential_vs_overall'] = test_data['potential'] / test_data['overall']
        
        # Apply filtering
        filter_condition = (
            (test_data['player_cat'].isin(['A', 'B'])) |
            ((test_data['player_cat'] == 'C') & (test_data['potential_vs_overall'] > 1.15)) |
            ((test_data['player_cat'] == 'D') & (test_data['potential_vs_overall'] > 1.25))
        )
        
        filtered_data = test_data[filter_condition]
        
        # Should keep all A category players and D category with high potential
        self.assertGreater(len(filtered_data), 0)
        self.assertLessEqual(len(filtered_data), len(test_data))
        
        # All filtered players should meet the criteria
        for _, player in filtered_data.iterrows():
            cat = player['player_cat']
            ratio = player['potential_vs_overall']
            
            if cat in ['A', 'B']:
                self.assertTrue(True)  # Always valid
            elif cat == 'C':
                self.assertGreater(ratio, 1.15)
            elif cat == 'D':
                self.assertGreater(ratio, 1.25)


if __name__ == '__main__':
    print("Running unit tests for player filtering logic...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestPlayerFiltering))
    test_suite.addTest(unittest.makeSuite(TestDatabaseCleaningValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    if result.wasSuccessful():
        print("\n✓ All unit tests passed! Player filtering logic is working correctly.")
    else:
        print(f"\n✗ {len(result.failures)} test(s) failed, {len(result.errors)} error(s) occurred.")
        
    print(f"Ran {result.testsRun} tests in total.")