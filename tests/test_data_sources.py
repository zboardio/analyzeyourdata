import pytest

from utils.data_sources import DataSourceHandler as H


class TestValidateUrlGoogleSheets:
    def test_legit_url(self):
        assert H.validate_url('https://docs.google.com/spreadsheets/d/abc123/edit?gid=0#gid=0', 'google_sheets')

    def test_subdomain_suffix_attack_rejected(self):
        assert not H.validate_url('https://docs.google.com.evil.com/spreadsheets/d/abc/edit', 'google_sheets')

    def test_userinfo_attack_rejected(self):
        assert not H.validate_url('https://docs.google.com@evil.com/spreadsheets/d/abc/edit', 'google_sheets')

    def test_http_rejected(self):
        assert not H.validate_url('http://docs.google.com/spreadsheets/d/abc/edit', 'google_sheets')

    def test_spreadsheets_in_query_rejected(self):
        assert not H.validate_url('https://evil.com/?x=/spreadsheets/docs.google.com', 'google_sheets')

    def test_empty_and_garbage(self):
        assert not H.validate_url('', 'google_sheets')
        assert not H.validate_url('not a url', 'google_sheets')


class TestValidateUrlAirtable:
    def test_legit_url(self):
        assert H.validate_url('https://airtable.com/appXXX/tblYYY', 'airtable')

    def test_subdomain_ok(self):
        assert H.validate_url('https://www.airtable.com/base', 'airtable')

    def test_evil_prefix_rejected(self):
        assert not H.validate_url('https://evilairtable.com/x', 'airtable')

    def test_suffix_attack_rejected(self):
        assert not H.validate_url('https://airtable.com.evil.com/x', 'airtable')


def test_unknown_source_type_rejected():
    assert not H.validate_url('https://docs.google.com/spreadsheets/d/abc', 'sharepoint')
    assert not H.validate_url('https://docs.google.com/spreadsheets/d/abc', 'other')


class TestHostAllowed:
    def test_exact(self):
        assert H._host_allowed('airtable.com', 'airtable.com')

    def test_subdomain(self):
        assert H._host_allowed('api.airtable.com', 'airtable.com')

    def test_prefix_rejected(self):
        assert not H._host_allowed('evilairtable.com', 'airtable.com')

    def test_suffix_rejected(self):
        assert not H._host_allowed('airtable.com.evil.com', 'airtable.com')


class TestGoogleSheetsCsvUrl:
    def test_url_with_gid(self):
        url = H.create_google_sheets_csv_url('https://docs.google.com/spreadsheets/d/ABC-123_x/edit?gid=42#gid=42')
        assert url == 'https://docs.google.com/spreadsheets/d/ABC-123_x/export?format=csv&gid=42'

    def test_url_without_gid(self):
        url = H.create_google_sheets_csv_url('https://docs.google.com/spreadsheets/d/ABC/edit')
        assert url == 'https://docs.google.com/spreadsheets/d/ABC/export?format=csv'

    def test_unparseable_url_raises(self):
        with pytest.raises(ValueError):
            H.create_google_sheets_csv_url('https://docs.google.com/nothing-here')
