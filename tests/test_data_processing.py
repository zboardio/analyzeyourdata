import io
import sqlite3

import pandas as pd
import pytest

from utils.data_processing import (
    parse_uploaded_file,
    load_sqlite_tables,
    load_sqlite_table_data,
    handle_datetime_conversion,
)


class TestParseUploadedFile:
    def test_csv(self):
        df = parse_uploaded_file(b'a,b\n1,2\n3,4\n', 'test.csv')
        assert df.shape == (2, 2) and list(df.columns) == ['a', 'b']

    def test_csv_custom_delimiter(self):
        df = parse_uploaded_file(b'a;b\n1;2\n', 'test.csv', delimiter=';')
        assert df.shape == (1, 2)

    def test_json(self):
        df = parse_uploaded_file(b'[{"a": 1, "b": 2}, {"a": 3, "b": 4}]', 'test.json')
        assert df.shape == (2, 2)

    def test_xlsx(self):
        buf = io.BytesIO()
        pd.DataFrame({'a': [1, 2], 'b': ['x', 'y']}).to_excel(buf, index=False)
        df = parse_uploaded_file(buf.getvalue(), 'test.xlsx')
        assert df.shape == (2, 2)

    def test_parquet(self):
        buf = io.BytesIO()
        pd.DataFrame({'a': [1, 2, 3]}).to_parquet(buf)
        df = parse_uploaded_file(buf.getvalue(), 'test.parquet')
        assert df.shape == (3, 1)

    def test_unnamed_columns_removed(self):
        df = parse_uploaded_file(b',a,b\n0,1,2\n', 'test.csv')
        assert not any(str(c).startswith('Unnamed') for c in df.columns)

    def test_all_nan_rows_dropped(self):
        df = parse_uploaded_file(b'a,b\n1,2\n,\n3,4\n', 'test.csv')
        assert df.shape[0] == 2

    def test_unsupported_extension_raises(self):
        with pytest.raises(ValueError):
            parse_uploaded_file(b'whatever', 'test.exe')

    def test_corrupt_file_raises_valueerror(self):
        with pytest.raises(ValueError):
            parse_uploaded_file(b'not really excel', 'test.xlsx')


def _sqlite_bytes():
    """SQLite DB bytes with a normal table and a hostile-named table."""
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE normal (id INTEGER, name TEXT)')
    conn.executemany('INSERT INTO normal VALUES (?, ?)', [(i, f'row{i}') for i in range(50)])
    evil = 'x"; DROP TABLE normal; --'
    quoted = '"' + evil.replace('"', '""') + '"'
    conn.execute(f'CREATE TABLE {quoted} (a INTEGER)')
    conn.execute(f'INSERT INTO {quoted} VALUES (7)')
    conn.commit()
    data = conn.serialize()
    conn.close()
    return data, evil


class TestSqlite:
    def test_list_tables(self):
        db, evil = _sqlite_bytes()
        tables, info = load_sqlite_tables(db)
        assert set(tables) == {'normal', evil}
        assert info['normal']['rows'] == 50
        assert info['normal']['columns'] == ['id', 'name']

    def test_load_table(self):
        db, _ = _sqlite_bytes()
        df = load_sqlite_table_data(db, 'normal')
        assert len(df) == 50

    def test_row_cap_applied(self):
        db, _ = _sqlite_bytes()
        assert len(load_sqlite_table_data(db, 'normal', max_rows=10)) == 10

    def test_hostile_table_name_is_data_not_sql(self):
        db, evil = _sqlite_bytes()
        df = load_sqlite_table_data(db, evil)
        assert len(df) == 1 and df['a'].iloc[0] == 7
        # 'normal' must survive — nothing was injected/executed
        tables, _ = load_sqlite_tables(db)
        assert 'normal' in tables

    def test_unknown_table_rejected(self):
        db, _ = _sqlite_bytes()
        with pytest.raises(ValueError, match='not found'):
            load_sqlite_table_data(db, 'nonexistent')

    def test_garbage_bytes_raise_valueerror(self):
        with pytest.raises(ValueError):
            load_sqlite_tables(b'this is not a sqlite file')


class TestDatetimeConversion:
    def test_format_conversion_and_derived_columns(self):
        df = pd.DataFrame({'when': ['2024-10-30 09:21:21', '2024-01-01 00:00:00']})
        out = handle_datetime_conversion(df, 'when', '%Y-%m-%d %H:%M:%S')
        assert out['ts'].dt.year.tolist() == [2024, 2024]
        assert out['tsHour'].tolist() == [9, 0]
        assert out['tsWeekday'].iloc[0] == 'Wednesday'
        assert out['tsCalendarWeek'].iloc[0] == 'CW44'
        assert out['tsMonth'].iloc[1] == 'January'
        assert out['tsQuarter'].iloc[0] == 'Q4'
        assert out['tsYearMonth'].iloc[0] == '2024M10'
        assert out['tsYearQuarter'].iloc[0] == '2024Q4'
        assert (out['count'] == 1).all()

    def test_unix_seconds(self):
        df = pd.DataFrame({'epoch': [1700000000]})
        out = handle_datetime_conversion(df, 'epoch', 'unix_s')
        assert out['tsYear'].iloc[0] == 2023

    def test_unix_milliseconds(self):
        df = pd.DataFrame({'epoch': [1700000000000]})
        out = handle_datetime_conversion(df, 'epoch', 'unix_ms')
        assert out['tsYear'].iloc[0] == 2023

    def test_wrong_format_raises(self):
        df = pd.DataFrame({'when': ['30.10.2024']})
        with pytest.raises(Exception):
            handle_datetime_conversion(df, 'when', '%Y-%m-%d')
