"""Purpose: Handles all data cleaning operations triggered by voice commands. Supports CSV/Excel, saves processed data as JSON for frontend visualization.

Voice Commands Supported:
- "remove duplicates" 
- "fill missing [column]" 
- "drop column [column]"
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
        self.processed_file = ""  # ✅ FIXED: Add this line!
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
            print(f"✅ Loaded: {self.filename} ({self.data.shape})")
            return True
        except Exception as e:
            print(f"❌ Load error: {e}")
            return False
    
    def save_processed(self) -> str:
        """✅ FIXED: Now sets self.processed_file"""
        if self.data is None:
            return ""
        
        output_file = f"{self.processed_path}{self.filename}_cleaned.json"
        data_dict = {
            'filename': self.filename,
            'columns': self.data.columns.tolist(),
            'data': self.data.to_dict('records'),
            'shape': list(self.data.shape)  # ✅ JSON serializable
        }
        
        with open(output_file, 'w') as f:
            json.dump(data_dict, f, indent=2)
        
        self.processed_file = output_file  # ✅ CRITICAL FIX!
        print(f"💾 Saved: {self.processed_file}")
        return output_file
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'filename': self.filename,
            'loaded': self.data is not None,
            'shape': list(self.data.shape) if self.data is not None else None,
            'columns': self.data.columns.tolist() if self.data is not None else []
        }
    
    def clean_duplicates(self) -> Dict[str, Any]:
        if self.data is None:
            return {'success': False, 'message': 'No data loaded'}
        
        initial_rows = len(self.data)
        self.data = self.data.drop_duplicates()
        print(f"🧹 Removed {initial_rows - len(self.data)} duplicates")
        return {
            'success': True,
            'removed': initial_rows - len(self.data),
            'rows': len(self.data)
        }
    
    def fill_missing_mean(self, column: str) -> Dict[str, Any]:
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
        if self.data is None or column not in self.data.columns:
            return {'success': False, 'message': f'Column {column} not found'}
        
        self.data = self.data.drop(columns=[column])
        return {
            'success': True,
            'dropped': 1,
            'columns': len(self.data.columns)
        }
    
    def get_preview(self, rows: int = 10) -> List[Dict[str, Any]]:  # ✅ 10 rows
        return self.data.head(rows).to_dict('records') if self.data is not None else []

# Global processor instance
processor = DataProcessor()
