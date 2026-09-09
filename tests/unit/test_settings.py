from pathlib import Path

from pytest import MonkeyPatch, raises

from core.settings import AppSettings, provider_key_mismatch


def test_load_yaml_and_env(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "sk-or-test-key")
    vectordb = tmp_path / "vectordb"
    memory = tmp_path / "cache" / "memory.sqlite"
    monkeypatch.setenv("VECTOR_DB_URI", str(vectordb))
    monkeypatch.setenv("MEMORY_DB_PATH", str(memory))
    config = tmp_path / "model_config.yaml"
    config.write_text(
        f"""
llm:
  base_url: "https://openrouter.ai/api/v1"
  model: "openai/gpt-4o-mini"
embeddings:
  base_url: "https://openrouter.ai/api/v1"
  model: "openai/text-embedding-3-large"
vector_db:
  uri: "{vectordb.as_posix()}"
memory:
  path: "{memory.as_posix()}"
""",
        encoding="utf-8",
    )
    settings = AppSettings.load(config_path=config)
    assert settings.llm_api_key == "sk-or-test-key"
    assert settings.llm.model == "openai/gpt-4o-mini"
    assert "openai/gpt-4o-mini" in settings.llm.models
    assert settings.vector_db_path == vectordb


def test_provider_key_mismatch_openrouter_with_openai_key() -> None:
    message = provider_key_mismatch(
        "sk-proj-demo",
        "https://openrouter.ai/api/v1",
        "https://openrouter.ai/api/v1",
    )
    assert message is not None
    assert "OpenRouter" in message


def test_provider_key_mismatch_ok_for_openai_host() -> None:
    assert (
        provider_key_mismatch(
            "sk-proj-demo",
            "https://api.openai.com/v1",
            "https://api.openai.com/v1",
        )
        is None
    )


def test_load_rejects_openrouter_url_with_openai_key(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setenv("LLM_API_KEY", "sk-proj-demo")
    config = tmp_path / "model_config.yaml"
    config.write_text(
        """
llm:
  base_url: "https://openrouter.ai/api/v1"
  model: "openai/gpt-4o-mini"
embeddings:
  base_url: "https://openrouter.ai/api/v1"
  model: "openai/text-embedding-3-large"
""",
        encoding="utf-8",
    )
    with raises(ValueError, match="OpenRouter"):
        AppSettings.load(config_path=config)
