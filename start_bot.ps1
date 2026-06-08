$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Виртуальное окружение не найдено, создаю .venv..."
    python -m venv .venv
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Не удалось найти .venv\Scripts\python.exe после создания окружения."
}

Write-Host "Устанавливаю/обновляю зависимости..."
& $venvPython -m pip install -r requirements.txt

Write-Host "Запускаю бота..."
& $venvPython main.py
