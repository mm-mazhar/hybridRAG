# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- FastAPI ingest/retrieve API with Docling hybrid chunking, LanceDB hybrid search, and SQLite memory.
- Next.js chat UI (AI Elements) that retrieves passages from FastAPI, then streams from an OpenAI-compatible model.
- Docker Compose stack for the API and web app, plus Archify architecture / ingest / sequence diagrams.
- Git branch, commit, and CI policy (lefthook hooks, GitHub Actions, Dependabot).

### Changed

- Replaced the Streamlit app with the split FastAPI + Next.js stack.
