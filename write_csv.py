import pandas as pd
import os

class CSVWriter:
    def __init__(self, filename="PEFC_data.csv"):
        self.filename = filename
        self.columns = [
            "Name", "Address", "City", "Country", "VAT", "Phone", "Email", "Website", "LicenseValid"
        ]
        self.initialize_csv()

    def initialize_csv(self):
        """Creates a CSV file with headers if it doesn't already exist."""
        if not os.path.exists(self.filename):
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(self.filename, index=False)

    def write_row(self, data):
        """Writes a new row to the CSV file."""
        df = pd.DataFrame([data], columns=self.columns)
        df.to_csv(self.filename, mode='a', index=False, header=False)