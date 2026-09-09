import logging
import logging.config
from pathlib import Path

from pytest import MonkeyPatch

from api.main import configure_logging


def test_configure_logging_writes_app_log(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "logging_config.yaml").write_text(
        """
version: 1
disable_existing_loggers: false
formatters:
  default:
    format: "%(name)s - %(levelname)s - %(message)s"
handlers:
  file:
    class: logging.FileHandler
    formatter: default
    filename: logs/app.log
    encoding: utf-8
root:
  level: INFO
  handlers: [file]
""",
        encoding="utf-8",
    )
    monkeypatch.setattr("api.main.project_root", lambda: tmp_path)

    try:
        configure_logging()
        logging.getLogger("rag.lc_retrievers").info("retrieve hybrid=True fts=True")
        for handler in logging.getLogger().handlers:
            handler.flush()
        log_text = (tmp_path / "logs" / "app.log").read_text(encoding="utf-8")
    finally:
        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                    }
                },
                "root": {"level": "WARNING", "handlers": ["console"]},
            }
        )

    assert "retrieve hybrid=True fts=True" in log_text
