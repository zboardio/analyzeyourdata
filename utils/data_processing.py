import io
import base64
import tempfile
import sqlite3
import pandas as pd
import h5py
import numpy as np


def load_sqlite_tables(file_path):
    """Load list of tables from SQLite database"""
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Get table info
        table_info = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]

            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]

            table_info[table] = {
                'rows': row_count,
                'columns': columns
            }

        conn.close()
        return tables, table_info

    except Exception as e:
        raise ValueError(f"Error reading SQLite database: {str(e)}")


def load_sqlite_table_data(file_path, table_name):
    """Load specific table data from SQLite database"""
    try:
        conn = sqlite3.connect(file_path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception as e:
        raise ValueError(f"Error loading table '{table_name}': {str(e)}")


def _decode_bytes_columns(df):
    """Convert bytes columns to strings (HDF5 stores strings as bytes)."""
    for col in df.columns:
        if df[col].dtype == object and len(df[col]) > 0:
            sample = df[col].iloc[0]
            if isinstance(sample, (bytes, np.bytes_)):
                df[col] = df[col].str.decode('utf-8', errors='replace')
    return df


def _read_hdf5(file_path):
    """Read HDF5 file, supporting both Pandas-created and generic h5py formats."""
    # Try Pandas format first (PyTables)
    try:
        return _decode_bytes_columns(pd.read_hdf(file_path))
    except Exception:
        pass

    # Fallback: read with h5py (generic HDF5)
    datasets = {}
    with h5py.File(file_path, 'r') as f:
        def _collect(name, obj):
            if isinstance(obj, h5py.Dataset) and obj.ndim in (1, 2):
                datasets[name] = obj[:]
        f.visititems(_collect)

    if not datasets:
        raise ValueError("No compatible datasets found in HDF5 file.")

    # Single 2D dataset → DataFrame directly
    if len(datasets) == 1:
        name, data = next(iter(datasets.items()))
        if data.ndim == 2:
            return _decode_bytes_columns(pd.DataFrame(data))
        return _decode_bytes_columns(pd.DataFrame({name: data}))

    # Multiple 1D datasets of same length → columns
    lengths = {name: arr.shape[0] for name, arr in datasets.items()}
    common_len = max(set(lengths.values()), key=list(lengths.values()).count)
    cols = {name.split('/')[-1]: arr for name, arr in datasets.items() if arr.shape[0] == common_len and arr.ndim == 1}
    if cols:
        return _decode_bytes_columns(pd.DataFrame(cols))

    # Fallback: use first 2D dataset
    for name, data in datasets.items():
        if data.ndim == 2:
            return _decode_bytes_columns(pd.DataFrame(data))

    # Last resort: first 1D dataset
    name, data = next(iter(datasets.items()))
    return _decode_bytes_columns(pd.DataFrame({name.split('/')[-1]: data}))


def parse_uploaded_file(contents, filename, delimiter=','):
    """Parse uploaded file and return pandas DataFrame"""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    file_ext = filename.split('.')[-1].lower()

    try:
        if file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(decoded))
        elif file_ext in ['csv', 'txt', 'log']:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter=delimiter)
        elif file_ext == 'json':
            df = pd.read_json(io.BytesIO(decoded))
        elif file_ext == 'parquet':
            df = pd.read_parquet(io.BytesIO(decoded))
        elif file_ext in ['h5', 'hdf5']:
            with tempfile.NamedTemporaryFile(delete=True, suffix='.h5') as tmp:
                tmp.write(decoded)
                tmp.flush()
                df = _read_hdf5(tmp.name)
        elif file_ext in ['db', 'sqlite', 'sqlite3']:
            # Handle SQLite files
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
                tmp.write(decoded)
                tmp.flush()

                # Return file path for SQLite handling
                return tmp.name, 'sqlite'
        else:
            raise ValueError("Unsupported file format.")
    except Exception as e:
        raise ValueError(f"Error processing file: {str(e)}")

    # Clean up non-SQLite files
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.dropna(how='all', inplace=True)

    # Normalize datetime
    datetime_columns = df.select_dtypes(include=['datetime64[ns]', 'object']).columns
    for col in datetime_columns:
        if df[col].dtype == 'datetime64[ns]':
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    return df


def handle_datetime_conversion(df, datetime_col, datetime_format):
    """Handle enhanced datetime conversion including Unix timestamps"""
    if datetime_format == 'unix_s':
        df['ts'] = pd.to_datetime(df[datetime_col], unit='s')
    elif datetime_format == 'unix_ms':
        df['ts'] = pd.to_datetime(df[datetime_col], unit='ms')
    else:
        df['ts'] = pd.to_datetime(df[datetime_col], format=datetime_format)

    # Generate enhanced datetime columns
    df['tsDate'] = df['ts'].dt.date
    df['tsHour'] = df['ts'].dt.hour
    df['tsDateHour'] = df['ts'].dt.floor('h')
    df['tsWeekday'] = df['ts'].dt.day_name()
    df['tsCalendarWeek'] = df['ts'].dt.isocalendar().week.apply(lambda x: f"CW{x:02d}")
    df['tsMonth'] = df['ts'].dt.strftime('%B')
    df['tsQuarter'] = df['ts'].dt.to_period('Q').apply(lambda x: f"Q{x.quarter}")
    df['tsYear'] = df['ts'].dt.year
    df['tsYearCalendarWeek'] = df['ts'].dt.year.astype(str) + df['tsCalendarWeek']
    df['tsYearMonth'] = df['ts'].dt.year.astype(str) + df['ts'].dt.month.apply(lambda x: f"M{x:02d}")
    df['tsYearQuarter'] = df['ts'].dt.to_period('Q').apply(lambda x: f"{x.year}Q{x.quarter}")
    df['count'] = 1

    return df
