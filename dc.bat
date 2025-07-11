@echo off
REM docker-compose shortcuts

IF "%1"=="up" (
  docker compose up --build -d
  GOTO :EOF
)

IF "%1"=="down" (
  docker compose down
  GOTO :EOF
)

IF "%1"=="test" (
  docker compose run --rm tests pytest --maxfail=1 --disable-warnings -q
  GOTO :EOF
)

IF "%1"=="lint" (
  docker compose run --rm lint
  GOTO :EOF
)

IF "%1"=="shell" (
  docker compose run --rm web bash
  GOTO :EOF
)

ECHO Usage: dc ^<up^|down^|test^|lint^|shell^>
