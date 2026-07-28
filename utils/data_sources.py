# utils/data_sources.py - External data sources (Google Sheets, Airtable)

import pandas as pd
import requests
import re
from urllib.parse import urlparse, quote
from typing import Dict, List

class DataSourceHandler:
    """
    External data source handler:
    - Google Sheets URLs
    - Airtable API
    """

    @staticmethod
    def create_google_sheets_csv_url(google_sheets_url: str) -> str:
        """
        Convert Google Sheets URL to CSV export URL.
        Automatically extracts the GID from the URL if present.

        Args:
            google_sheets_url (str): Google Sheets URL (sharing or browser bar)

        Returns:
            str: CSV export URL
        """
        try:
            # Extract spreadsheet ID from various Google Sheets URL formats
            patterns = [
                r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
                r'key=([a-zA-Z0-9-_]+)',
                r'/d/([a-zA-Z0-9-_]+)'
            ]

            spreadsheet_id = None
            for pattern in patterns:
                match = re.search(pattern, google_sheets_url)
                if match:
                    spreadsheet_id = match.group(1)
                    break

            if not spreadsheet_id:
                raise ValueError("Could not extract spreadsheet ID from URL")

            # Auto-extract GID from URL (supports ?gid=, &gid=, #gid= formats)
            gid_match = re.search(r'[?&#]gid=(\d+)', google_sheets_url)
            sheet_gid = gid_match.group(1) if gid_match else None

            # Create CSV export URL
            if sheet_gid:
                csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_gid}"
            else:
                csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"

            return csv_url

        except Exception as e:
            raise ValueError(f"Failed to create Google Sheets CSV URL: {str(e)}")
    
    @staticmethod
    def load_from_google_sheets(google_sheets_url: str, max_rows: int = 0) -> pd.DataFrame:
        """
        Load data from Google Sheets URL.
        GID is automatically extracted from the URL if present.

        Args:
            google_sheets_url (str): Google Sheets URL (sharing or browser bar)
            max_rows (int): Row cap for the loaded sheet (0 = unlimited)

        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            csv_url = DataSourceHandler.create_google_sheets_csv_url(google_sheets_url)

            # Download CSV data
            response = requests.get(csv_url, timeout=30)
            response.raise_for_status()

            # Load into DataFrame
            df = pd.read_csv(pd.io.common.StringIO(response.text), nrows=max_rows or None)

            return df

        except Exception as e:
            raise ValueError(f"Failed to load from Google Sheets: {str(e)}")
    
    # AIRTABLE METHODS

    @staticmethod
    def validate_airtable_credentials(api_key: str, base_id: str) -> bool:
        """
        Validate Airtable API credentials by attempting to get base schema
        
        Args:
            api_key (str): Airtable API key
            base_id (str): Airtable base ID
            
        Returns:
            bool: True if credentials are valid
        """
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Try to get base schema to validate credentials
            url = f"https://api.airtable.com/v0/meta/bases/{quote(base_id, safe='')}/tables"
            response = requests.get(url, headers=headers, timeout=10)
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    @staticmethod
    def get_airtable_tables(api_key: str, base_id: str) -> List[Dict]:
        """
        Get list of tables from Airtable base
        
        Args:
            api_key (str): Airtable API key
            base_id (str): Airtable base ID
            
        Returns:
            List[Dict]: List of table information
        """
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Get base schema
            url = f"https://api.airtable.com/v0/meta/bases/{quote(base_id, safe='')}/tables"
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            tables = []
            for table in data.get('tables', []):
                tables.append({
                    'id': table.get('id'),
                    'name': table.get('name'),
                    'primaryFieldId': table.get('primaryFieldId'),
                    'fields': table.get('fields', [])
                })
            
            return tables
            
        except Exception as e:
            raise ValueError(f"Failed to get Airtable tables: {str(e)}")
    
    @staticmethod
    def load_from_airtable(api_key: str, base_id: str, table_name: str, max_rows: int = 0) -> pd.DataFrame:
        """
        Load data from Airtable table

        Args:
            api_key (str): Airtable API key
            base_id (str): Airtable base ID
            table_name (str): Name of the table to load
            max_rows (int): Record cap across pagination (0 = unlimited)

        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # Build the API URL
            url = f"https://api.airtable.com/v0/{quote(base_id, safe='')}/{quote(table_name, safe='')}"

            all_records = []
            offset = None

            # Handle pagination
            while True:
                params = {}
                if offset:
                    params['offset'] = offset

                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                records = data.get('records', [])

                # Extract fields from each record
                for record in records:
                    record_data = record.get('fields', {})
                    record_data['airtable_record_id'] = record.get('id')
                    record_data['airtable_created_time'] = record.get('createdTime')
                    all_records.append(record_data)

                if max_rows and len(all_records) >= max_rows:
                    all_records = all_records[:max_rows]
                    break

                # Check for more pages
                offset = data.get('offset')
                if not offset:
                    break
            
            if not all_records:
                raise ValueError(f"No records found in table '{table_name}'")
            
            # Convert to DataFrame
            df = pd.DataFrame(all_records)
            
            # Clean up column names (replace spaces with underscores, etc.)
            df.columns = [col.replace(' ', '_').replace('-', '_') for col in df.columns]
            
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to load from Airtable: {str(e)}")
    
    @staticmethod
    def validate_url(url: str, source_type: str) -> bool:
        """
        Validate URL format for specific source types

        Args:
            url (str): URL to validate
            source_type (str): Type of source ('google_sheets' or 'airtable')

        Returns:
            bool: True if URL is valid for the source type
        """
        try:
            parsed = urlparse(url)
            # parsed.hostname strips userinfo ("user@host") and port, lowercased —
            # substring checks on netloc are bypassable (e.g. docs.google.com.evil.com)
            host = parsed.hostname or ''
            if parsed.scheme != 'https' or not host:
                return False

            if source_type == 'google_sheets':
                return host == 'docs.google.com' and '/spreadsheets/' in parsed.path

            elif source_type == 'airtable':
                # Airtable doesn't use URLs for API access, so this is not used
                # But we keep it for consistency
                return DataSourceHandler._host_allowed(host, 'airtable.com')

            return False

        except Exception:
            return False

    @staticmethod
    def _host_allowed(host: str, allowed_domain: str) -> bool:
        """True only for the exact domain or a real subdomain of it."""
        return host == allowed_domain or host.endswith('.' + allowed_domain)