import importlib

import pytest

import config as config_module


@pytest.fixture
def reload_config(monkeypatch):
    """Reload config with given env vars; restore the original module after."""
    def _reload(**env):
        for key in ('AG_GRID_LICENSE_KEY', 'AG_GRID_ENABLE_ENTERPRISE'):
            monkeypatch.delenv(key, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        return importlib.reload(config_module).Config

    yield _reload
    # monkeypatch has restored the env by now; reload once more to reset state
    importlib.reload(config_module)


class TestEnterpriseSwitch:
    def test_auto_without_key_is_community(self, reload_config):
        cfg = reload_config()
        assert cfg.AG_GRID_ENTERPRISE_ENABLED is False

    def test_auto_with_key_enables_enterprise(self, reload_config):
        cfg = reload_config(AG_GRID_LICENSE_KEY='some-key')
        assert cfg.AG_GRID_ENTERPRISE_ENABLED is True

    def test_forced_true_without_key(self, reload_config):
        cfg = reload_config(AG_GRID_ENABLE_ENTERPRISE='true')
        assert cfg.AG_GRID_ENTERPRISE_ENABLED is True

    def test_forced_false_with_key(self, reload_config):
        cfg = reload_config(AG_GRID_LICENSE_KEY='some-key', AG_GRID_ENABLE_ENTERPRISE='false')
        assert cfg.AG_GRID_ENTERPRISE_ENABLED is False

    def test_empty_key_treated_as_unset(self, reload_config):
        cfg = reload_config(AG_GRID_LICENSE_KEY='')
        assert cfg.AG_GRID_LICENSE_KEY is None
        assert cfg.AG_GRID_ENTERPRISE_ENABLED is False


class TestValidateConfig:
    def test_defaults_have_no_errors(self, reload_config):
        errors, warnings = reload_config().validate_config()
        assert errors == []

    def test_unlicensed_enterprise_warns(self, reload_config):
        cfg = reload_config(AG_GRID_ENABLE_ENTERPRISE='true')
        errors, warnings = cfg.validate_config()
        assert errors == []
        assert any('evaluation mode' in w for w in warnings)

    def test_licensed_enterprise_does_not_warn(self, reload_config):
        cfg = reload_config(AG_GRID_LICENSE_KEY='some-key')
        _, warnings = cfg.validate_config()
        assert not any('evaluation' in w for w in warnings)


class TestLimits:
    def test_content_length_auto_is_5x(self, reload_config):
        cfg = reload_config()
        assert cfg.MAX_CONTENT_LENGTH_MB == cfg.MAX_FILE_SIZE_MB * 5

    def test_content_length_override(self, reload_config, monkeypatch):
        monkeypatch.setenv('MAX_CONTENT_LENGTH_MB', '250')
        cfg = importlib.reload(config_module).Config
        assert cfg.MAX_CONTENT_LENGTH_MB == 250

    def test_external_rows_default_unlimited(self, reload_config):
        assert reload_config().MAX_EXTERNAL_ROWS == 0
