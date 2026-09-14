from lead_collector.config import Settings


def test_settings_load_serpapi_key_from_environment(monkeypatch):
    monkeypatch.setenv("SERPAPI_KEY", "test-api-key")

    settings = Settings()

    assert settings.serpapi_key == "test-api-key"