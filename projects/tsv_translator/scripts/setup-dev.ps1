# PowerShell script for setting up development environment
# Usage: .\scripts\setup-dev.ps1

Write-Host "TSV Translator Development Setup" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Set location to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    Write-Host "📁 Project root: $projectRoot" -ForegroundColor Gray
    Write-Host ""

    # Check if uv is installed
    Write-Host "🔍 Checking for uv..." -ForegroundColor Yellow
    try {
        $uvVersion = & uv --version 2>$null
        Write-Host "✅ uv found: $uvVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ uv not found!" -ForegroundColor Red
        Write-Host "Please install uv first: https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor Yellow
        exit 1
    }

    # Install dependencies
    Write-Host ""
    Write-Host "📦 Installing development dependencies..." -ForegroundColor Yellow
    & uv sync --extra dev --extra test

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }

    Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green

    # Verify installation by running a quick test
    Write-Host ""
    Write-Host "🧪 Running quick verification test..." -ForegroundColor Yellow
    & uv run python -c "import tsv_translator; print('TSV Translator imported successfully')"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Package import successful!" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Package import failed, but dependencies are installed" -ForegroundColor Yellow
    }

    # Create directories if they don't exist
    Write-Host ""
    Write-Host "📁 Creating required directories..." -ForegroundColor Yellow

    $dirs = @("logs", "htmlcov", ".pytest_cache")
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✅ Created directory: $dir" -ForegroundColor Green
        }
        else {
            Write-Host "✅ Directory exists: $dir" -ForegroundColor Gray
        }
    }

    # Show available commands
    Write-Host ""
    Write-Host "🚀 Development environment setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Cyan
    Write-Host "  .\scripts\test.ps1                 # Run all tests" -ForegroundColor White
    Write-Host "  .\scripts\test.ps1 -Coverage       # Run tests with coverage" -ForegroundColor White
    Write-Host "  .\scripts\test.ps1 -Quick          # Run unit tests only" -ForegroundColor White
    Write-Host "  uv run tsv-info --help             # Test CLI command" -ForegroundColor White
    Write-Host "  uv run pytest -v                   # Verbose test run" -ForegroundColor White
    Write-Host "  uv run ruff check .                # Run linter" -ForegroundColor White
    Write-Host "  uv run black .                     # Format code" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Documentation:" -ForegroundColor Cyan
    Write-Host "  README.md                          # Project overview" -ForegroundColor White
    Write-Host "  docs/                              # Detailed documentation" -ForegroundColor White
    Write-Host ""

}
catch {
    Write-Error "Error during setup: $_"
    exit 1
}
finally {
    Pop-Location
}