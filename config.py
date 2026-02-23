# config.py

import os
from pathlib import Path
from datetime import datetime

class Config:
    """
    Centralized configuration management for the data analysis app.
    All configurable values should be defined here and controlled via environment variables.
    """

    # Git commit hash — injected at Docker build time, used for traceability
    GIT_COMMIT = os.getenv('GIT_COMMIT', 'dev')

    # App Basic Settings
    APP_TITLE = os.getenv('APP_TITLE', 'Analyze Your Data')
    APP_BRAND_NAME = os.getenv('APP_BRAND_NAME', 'Analyze Your Data')
    APP_DESCRIPTION = os.getenv('APP_DESCRIPTION', 'A powerful, simple tool for data analysis and visualization. Upload, analyze, and create stunning charts in minutes.')
    
    # Server Settings
    APP_HOST = os.getenv('APP_HOST', '127.0.0.1')
    APP_PORT = int(os.getenv('APP_PORT', 8050))
    APP_DEBUG = os.getenv('APP_DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    # File Upload Settings
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 20))
    SUPPORTED_FILE_FORMATS = os.getenv('SUPPORTED_FILE_FORMATS', 'csv,xlsx,xls,json,parquet,h5,hdf5,h6,plh,txt,log,db,sqlite,sqlite3').split(',')
    
    # Content Directories
    MARKDOWN_DIRECTORY = os.getenv('MARKDOWN_DIRECTORY', 'assets/markdown')
    ASSETS_DIRECTORY = os.getenv('ASSETS_DIRECTORY', 'assets')
    
    # UI Assets
    LOGO_PATH = os.getenv('LOGO_PATH', '/assets/logo.png')  # If empty, logo is hidden in navbar
    # Favicon: Dash auto-discovers /assets/favicon.svg — added cofig for SVG, as Dash v4.0 supports only ICO

    # External Links
    GITHUB_URL = os.getenv('GITHUB_URL', 'https://github.com/your-repo')
    WEBSITE_URL = os.getenv('WEBSITE_URL', 'https://zboardio-webpage.pages.dev/en/')
    CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'contact@zboardio.com')
    DOCUMENTATION_URL = os.getenv('DOCUMENTATION_URL', '')  # If empty, docs buttons are hidden
    DONATE_URL = os.getenv('DONATE_URL', '')
    YOUTUBE_INTRO_URL = os.getenv('YOUTUBE_INTRO_URL', '')

    # Powered By section URLs (empty = tile hidden)
    POWERED_BY_PLOTLY_DASH_URL = os.getenv('POWERED_BY_PLOTLY_DASH_URL', 'https://dash.plotly.com')
    POWERED_BY_DASH_AG_GRID_URL = os.getenv('POWERED_BY_DASH_AG_GRID_URL', 'https://dash.plotly.com/dash-ag-grid')
    POWERED_BY_AG_GRID_URL = os.getenv('POWERED_BY_AG_GRID_URL', 'https://www.ag-grid.com')
    POWERED_BY_AUTHOR_NAME = os.getenv('POWERED_BY_AUTHOR_NAME', 'zboardio')  # Short name for tile
    # WEBSITE_URL is used for the author tile link

    # Company/Branding
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'Smart Engineering by zboardio')  # Full name for footer
    # Dynamic copyright year - always current year unless specifically overridden
    COPYRIGHT_YEAR = os.getenv('COPYRIGHT_YEAR', str(datetime.now().year))
    
    # AgGrid Settings
    AG_GRID_LICENSE_KEY = os.getenv("AG_GRID_LICENSE_KEY")
    AG_GRID_THEME = os.getenv('AG_GRID_THEME', 'ag-theme-alpine')
    AG_GRID_HEIGHT = int(os.getenv('AG_GRID_HEIGHT', 700))
    
    # Chart Settings
    DEFAULT_CHART_TYPE = os.getenv('DEFAULT_CHART_TYPE', 'scatter')
    CHART_HEIGHT = int(os.getenv('CHART_HEIGHT', 700))
    CHART_COLOR_SCHEME = os.getenv('CHART_COLOR_SCHEME', 'plotly')
    
    # Language Settings
    APP_LANGUAGE = os.getenv('APP_LANGUAGE', os.getenv('DEFAULT_LANGUAGE', 'en'))
    DEFAULT_LANGUAGE = APP_LANGUAGE
    SUPPORTED_LANGUAGES = os.getenv('SUPPORTED_LANGUAGES', 'en,cs,da,de,es,fr,hr,it,nl,pl,pt,sk,sl,sv,uk').split(',')

    # Language instance URLs (for navbar cross-links)
    APP_URL_EN = os.getenv('APP_URL_EN', 'http://localhost:8050')
    APP_URL_CS = os.getenv('APP_URL_CS', 'http://localhost:8051')
    APP_URL_DA = os.getenv('APP_URL_DA', 'http://localhost:8054')
    APP_URL_DE = os.getenv('APP_URL_DE', 'http://localhost:8052')
    APP_URL_ES = os.getenv('APP_URL_ES', 'http://localhost:8055')
    APP_URL_FR = os.getenv('APP_URL_FR', 'http://localhost:8056')
    APP_URL_HR = os.getenv('APP_URL_HR', 'http://localhost:8057')
    APP_URL_IT = os.getenv('APP_URL_IT', 'http://localhost:8058')
    APP_URL_NL = os.getenv('APP_URL_NL', 'http://localhost:8059')
    APP_URL_PL = os.getenv('APP_URL_PL', 'http://localhost:8053')
    APP_URL_PT = os.getenv('APP_URL_PT', 'http://localhost:8060')
    APP_URL_SK = os.getenv('APP_URL_SK', 'http://localhost:8061')
    APP_URL_SL = os.getenv('APP_URL_SL', 'http://localhost:8062')
    APP_URL_SV = os.getenv('APP_URL_SV', 'http://localhost:8063')
    APP_URL_UK = os.getenv('APP_URL_UK', 'http://localhost:8064')
    
    # Database Settings (for future MongoDB logging)
    MONGODB_URI = os.getenv('MONGO_URI', os.getenv('MONGODB_URI', ''))
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'analyzeYourData')
    MONGODB_COLLECTION_LOGS = os.getenv('MONGODB_COLLECTION_LOGS', 'usageLogs')
    MONGODB_COLLECTION_FEEDBACK = os.getenv('MONGODB_COLLECTION_FEEDBACK', 'feedback')
    
    # SQLite Settings
    SQLITE_SUPPORTED_EXTENSIONS = ['.db', '.sqlite', '.sqlite3']
    SQLITE_MAX_TABLE_ROWS_PREVIEW = int(os.getenv('SQLITE_MAX_TABLE_ROWS_PREVIEW', 100000))  # Limit for large tables
    SQLITE_QUERY_TIMEOUT = int(os.getenv('SQLITE_QUERY_TIMEOUT', 30))  # Seconds

    # Data Processing Settings
    DATETIME_FORMATS = [
        # Custom & Unix — most flexible, at the top
        {'label': 'Custom Python strftime() format', 'value': 'custom'},
        {'label': 'Unix timestamp | seconds', 'value': 'unix_s'},
        {'label': 'Unix timestamp | milliseconds', 'value': 'unix_ms'},

        # ISO-8601 (T separator)
        {'label': '2024-10-30T09:21:21.210 | ISO-8601 ', 'value': '%Y-%m-%dT%H:%M:%S.%f'},
        {'label': '2024-10-30T09:21:21 | ISO-8601, NO ms)', 'value': '%Y-%m-%dT%H:%M:%S'},

        # YYYY-MM-DD (dash, international standard)
        {'label': '2024-10-30 09:21:21.210', 'value': '%Y-%m-%d %H:%M:%S.%f'},
        {'label': '2024-10-30 09:21:21', 'value': '%Y-%m-%d %H:%M:%S'},
        {'label': '2024-10-30', 'value': '%Y-%m-%d'},

        # DD-MM-YYYY (dash, EU)
        {'label': '30-10-2024 09:21:21.210', 'value': '%d-%m-%Y %H:%M:%S.%f'},
        {'label': '30-10-2024 09:21:21 | NO ms', 'value': '%d-%m-%Y %H:%M:%S'},
        {'label': '30-10-2024', 'value': '%d-%m-%Y'},

        # DD.MM.YYYY (dot, EU)
        {'label': '30.10.2024 09:21:21.210', 'value': '%d.%m.%Y %H:%M:%S.%f'},
        {'label': '30.10.2024 09:21:21 | NO ms', 'value': '%d.%m.%Y %H:%M:%S'},
        {'label': '30.10.2024', 'value': '%d.%m.%Y'},

        # DD/MM/YYYY (slash, EU)
        {'label': '30/10/2024 09:21:21.210', 'value': '%d/%m/%Y %H:%M:%S.%f'},
        {'label': '30/10/2024 09:21:21 | NO ms', 'value': '%d/%m/%Y %H:%M:%S'},
        {'label': '30/10/2024', 'value': '%d/%m/%Y'},

        # MM/DD/YYYY (slash, US)
        {'label': '10/30/2024 09:21:21.210 AM', 'value': '%m/%d/%Y %I:%M:%S.%f %p'},
        {'label': '10/30/2024 09:21:21 AM | NO ms', 'value': '%m/%d/%Y %I:%M:%S %p'},
        {'label': '10/30/2024 09:21:21.210', 'value': '%m/%d/%Y %H:%M:%S.%f'},
        {'label': '10/30/2024 09:21:21 | NO ms ', 'value': '%m/%d/%Y %H:%M:%S'},
        {'label': '10/30/2024', 'value': '%m/%d/%Y'},
    ]
    
    # Memory Monitoring
    MEMORY_MONITORING_ENABLED = os.getenv('MEMORY_MONITORING_ENABLED', 'True').lower() in ['true', '1', 'yes']
    MEMORY_MONITORING_INTERVAL = int(os.getenv('MEMORY_MONITORING_INTERVAL', 3))
    
    # Security Settings
    # SECRET_KEY: Used for session management, CSRF protection, and other security features
    # In production, this should be a strong, unique secret
    # For this data analysis tool, it's mainly used for secure session handling
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    @classmethod
    def get_supported_file_extensions(cls):
        """Get list of supported file extensions"""
        return [f".{ext}" for ext in cls.SUPPORTED_FILE_FORMATS]
    
    @classmethod
    def get_sqlite_extensions(cls):
        """Get list of SQLite file extensions"""
        return cls.SQLITE_SUPPORTED_EXTENSIONS
    
    @classmethod
    def is_sqlite_file(cls, filename):
        """Check if filename has SQLite extension"""
        if not filename:
            return False
        ext = '.' + filename.split('.')[-1].lower()
        return ext in cls.SQLITE_SUPPORTED_EXTENSIONS

    @classmethod
    def get_current_year(cls):
        """Get current year for copyright (always up-to-date)"""
        return datetime.now().year
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration values"""
        errors = []
        
        if not cls.AG_GRID_LICENSE_KEY and cls.AG_GRID_LICENSE_KEY != "":
            errors.append("AG_GRID_LICENSE_KEY is not set")
        
        if cls.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be greater than 0")
        
        if not Path(cls.MARKDOWN_DIRECTORY).exists():
            errors.append(f"MARKDOWN_DIRECTORY '{cls.MARKDOWN_DIRECTORY}' does not exist")
        
        if cls.SQLITE_MAX_TABLE_ROWS_PREVIEW <= 0:
            errors.append("SQLITE_MAX_TABLE_ROWS_PREVIEW must be greater than 0")
        
        if cls.SQLITE_QUERY_TIMEOUT <= 0:
            errors.append("SQLITE_QUERY_TIMEOUT must be greater than 0")
        
        return errors