"""Purpose: Handles all data cleaning operations triggered by voice commands. Supports CSV/Excel, saves processed data as JSON for frontend visualization.

Voice Commands Supported:

"remove duplicates"

"fill missing with mean [column]"

"drop column [column]"

"""


import pandas as pd
import numpy as np
from typing import Dict, Any, List
import json
from pathlib import Path
import os

class DataProcessor:
    def __init__(self):
        self.data = None
        self.filename = None
        self.processed_path = "processed_data/"
        os.makedirs(self.processed_path, exist_ok=True)
    
    def load_data(self, file_path: str) -> bool:
        """Load uploaded CSV/Excel file"""
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.data = pd.read_excel(file_path)
            else:
                return False
            
            self.filename = Path(file_path).stem
            print(f"Loaded data: {self.data.shape[0]} rows, {self.data.shape[1]} columns")
            return True
        except Exception as e:
            print(f"Load error: {e}")
            return False
    
    def save_processed(self) -> str:
        """Save cleaned data as JSON for frontend"""
        if self.data is None:
            return ""
        
        output_file = f"{self.processed_path}{self.filename}_cleaned.json"
        data_dict = {
            'filename': self.filename,
            'columns': self.data.columns.tolist(),
            'data': self.data.to_dict('records'),
            'shape': self.data.shape
        }
        
        with open(output_file, 'w') as f:
            json.dump(data_dict, f, indent=2)
        
        return output_file
    
    def get_status(self) -> Dict[str, Any]:
        """Get current data status"""
        return {
            'filename': self.filename,
            'loaded': self.data is not None,
            'shape': self.data.shape if self.data is not None else None,
            'columns': self.data.columns.tolist() if self.data is not None else []
        }
    
    def clean_duplicates(self) -> Dict[str, Any]:
        """Voice command: 'remove duplicates'"""
        if self.data is None:
            return {'success': False, 'message': 'No data loaded'}
        
        initial_rows = len(self.data)
        self.data = self.data.drop_duplicates()
        return {
            'success': True,
            'removed': initial_rows - len(self.data),
            'rows': len(self.data)
        }
    
    def fill_missing_mean(self, column: str) -> Dict[str, Any]:
        """Voice command: 'fill missing with mean [column]'"""
        if self.data is None or column not in self.data.columns:
            return {'success': False, 'message': f'Column {column} not found'}
        
        initial_missing = self.data[column].isnull().sum()
        self.data[column] = self.data[column].fillna(self.data[column].mean())
        return {
            'success': True,
            'filled': initial_missing,
            'rows': len(self.data)
        }
    
    def drop_column(self, column: str) -> Dict[str, Any]:
        """Voice command: 'drop column [column]'"""
        if self.data is None or column not in self.data.columns:
            return {'success': False, 'message': f'Column {column} not found'}
        
        initial_cols = len(self.data.columns)
        self.data = self.data.drop(columns=[column])
        return {
            'success': True,
            'dropped': 1,
            'columns': len(self.data.columns)
        }
    
    def get_preview(self, rows: int = 5) -> List[Dict[str, Any]]:
        """Get data preview for frontend"""
        return self.data.head(rows).to_dict('records')

# Global processor instance
processor = DataProcessor()
