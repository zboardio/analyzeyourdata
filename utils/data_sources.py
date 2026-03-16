# utils/data_sources.py - Enhanced with Airtable support

import pandas as pd
import requests
import base64
import re
from urllib.parse import urlparse
import tempfile
from typing import Dict, List, Tuple, Optional
import json

class DataSourceHandler:
    """
    Enhanced data source handler supporting multiple input methods:
    - Direct file upload
    - Microsoft SharePoint URLs
    - Google Sheets URLs
    - Airtable API
    """
    
    @staticmethod
    def create_sharepoint_direct_url(sharepoint_link: str) -> str:
        """
        Convert SharePoint sharing link to direct download URL
        
        Args:
            sharepoint_link (str): SharePoint sharing URL
            
        Returns:
            str: Direct download URL for OneDrive API
        """
        try:
            # Encode the URL to base64
            data_bytes64 = base64.b64encode(bytes(sharepoint_link, 'utf-8'))
            data_bytes64_string = data_bytes64.decode('utf-8').replace('/', '_').replace('+', '-').rstrip("=")
            
            # Create OneDrive API URL
            result_url = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_string}/root/content"
            return result_url
            
        except Exception as e:
            raise ValueError(f"Failed to create SharePoint direct URL: {str(e)}")
    
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
    def get_google_sheets_info(google_sheets_url: str) -> Tuple[str, List[Dict]]:
        """
        Get spreadsheet information including available sheets
        
        Args:
            google_sheets_url (str): Google Sheets sharing URL
            
        Returns:
            Tuple[str, List[Dict]]: Spreadsheet ID and list of sheet information
        """
        try:
            # Extract spreadsheet ID
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
            
            # Try to get sheet information (this requires the spreadsheet to be publicly readable)
            # For now, we'll return a default structure
            sheets_info = [
                {'name': 'Sheet1', 'gid': '0'},  # Default first sheet
            ]
            
            return spreadsheet_id, sheets_info
            
        except Exception as e:
            raise ValueError(f"Failed to get Google Sheets info: {str(e)}")
    
    @staticmethod
    def load_from_sharepoint(sharepoint_url: str) -> Tuple[pd.DataFrame, List[str]]:
        """
        Load data from SharePoint URL
        
        Args:
            sharepoint_url (str): SharePoint sharing URL
            
        Returns:
            Tuple[pd.DataFrame, List[str]]: DataFrame and list of available sheet names
        """
        try:
            direct_url = DataSourceHandler.create_sharepoint_direct_url(sharepoint_url)
            
            # Download the file
            response = requests.get(direct_url, timeout=30)
            response.raise_for_status()
            
            # Determine file type from content or URL
            content_type = response.headers.get('content-type', '').lower()
            
            if 'excel' in content_type or 'spreadsheet' in content_type:
                # Handle Excel files
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file.flush()
                    
                    # Read Excel file and get sheet names
                    excel_file = pd.ExcelFile(tmp_file.name)
                    sheet_names = excel_file.sheet_names
                    
                    # Load first sheet by default
                    df = pd.read_excel(tmp_file.name, sheet_name=0)
                    
                return df, sheet_names
            else:
                # Assume CSV format
                df = pd.read_csv(pd.io.common.StringIO(response.text))
                return df, ['Sheet1']
                
        except Exception as e:
            raise ValueError(f"Failed to load from SharePoint: {str(e)}")
    
    @staticmethod
    def load_from_google_sheets(google_sheets_url: str) -> pd.DataFrame:
        """
        Load data from Google Sheets URL.
        GID is automatically extracted from the URL if present.

        Args:
            google_sheets_url (str): Google Sheets URL (sharing or browser bar)

        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            csv_url = DataSourceHandler.create_google_sheets_csv_url(google_sheets_url)
            
            # Download CSV data
            response = requests.get(csv_url, timeout=30)
            response.raise_for_status()
            
            # Load into DataFrame
            df = pd.read_csv(pd.io.common.StringIO(response.text))
            
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to load from Google Sheets: {str(e)}")
    
    @staticmethod
    def load_sharepoint_sheet(sharepoint_url: str, sheet_name: str) -> pd.DataFrame:
        """
        Load specific sheet from SharePoint Excel file
        
        Args:
            sharepoint_url (str): SharePoint sharing URL
            sheet_name (str): Name of the sheet to load
            
        Returns:
            pd.DataFrame: Loaded data from specific sheet
        """
        try:
            direct_url = DataSourceHandler.create_sharepoint_direct_url(sharepoint_url)
            
            # Download the file
            response = requests.get(direct_url, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file and read specific sheet
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(response.content)
                tmp_file.flush()
                
                df = pd.read_excel(tmp_file.name, sheet_name=sheet_name)
                
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to load sheet '{sheet_name}' from SharePoint: {str(e)}")
    
    # NEW AIRTABLE METHODS
    
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
            url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
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
            url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
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
    def load_from_airtable(api_key: str, base_id: str, table_name: str) -> pd.DataFrame:
        """
        Load data from Airtable table
        
        Args:
            api_key (str): Airtable API key
            base_id (str): Airtable base ID
            table_name (str): Name of the table to load
            
        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Build the API URL
            url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
            
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
            source_type (str): Type of source ('sharepoint', 'google_sheets', or 'airtable')
            
        Returns:
            bool: True if URL is valid for the source type
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            if source_type == 'sharepoint':
                # Check for SharePoint/OneDrive domains
                valid_domains = ['1drv.ms', 'onedrive.live.com', 'sharepoint.com', 'office.com']
                return any(domain in parsed.netloc.lower() for domain in valid_domains)
            
            elif source_type == 'google_sheets':
                # Check for Google Sheets domains
                return 'docs.google.com' in parsed.netloc.lower() and 'spreadsheets' in url.lower()
            
            elif source_type == 'airtable':
                # Airtable doesn't use URLs for API access, so this is not used
                # But we keep it for consistency
                return 'airtable.com' in parsed.netloc.lower()
            
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def validate_airtable_base_id(base_id: str) -> bool:
        """
        Validate Airtable base ID format
        
        Args:
            base_id (str): Airtable base ID to validate
            
        Returns:
            bool: True if base ID format is valid
        """
        try:
            # Airtable base IDs start with 'app' followed by 14 alphanumeric characters
            pattern = r'^app[a-zA-Z0-9]{14}$'
            return bool(re.match(pattern, base_id))
        except Exception:
            return False