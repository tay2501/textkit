# PowerShell script for running tests on Windows
# Usage: .\scripts\test.ps1 [options]

param(
    [switch]$Coverage,
    [switch]$Quick,
    [switch]$Integration,
    [switch]$Verbose,
    [switch]$Help
)

if ($Help) {
    Write-Host "TSV Translator Test Runner"
    Write-Host ""
    Write-Host "Usage: .\scripts\test.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Coverage     Run tests with coverage report"
    Write-Host "  -Quick        Run only unit tests"
    Write-Host "  -Integration  Run only integration tests"
    Write-Host "  -Verbose      Verbose output"
    Write-Host "  -Help         Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\scripts\test.ps1                    # Run all tests"
    Write-Host "  .\scripts\test.ps1 -Coverage          # Run with coverage"
    Write-Host "  .\scripts\test.ps1 -Quick             # Run unit tests only"
    Write-Host "  .\scripts\test.ps1 -Integration       # Run integration tests"
    exit 0
}

# Set location to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    Write-Host "TSV Translator Test Runner" -ForegroundColor Green
    Write-Host "Project root: $projectRoot" -ForegroundColor Gray
    Write-Host ""

    # Build pytest command
    $pytestArgs = @()

    if ($Quick) {
        Write-Host "Running unit tests only..." -ForegroundColor Yellow
        $pytestArgs += "-m", "unit"
    }
    elseif ($Integration) {
        Write-Host "Running integration tests only..." -ForegroundColor Yellow
        $pytestArgs += "-m", "integration"
    }
    else {
        Write-Host "Running all tests..." -ForegroundColor Yellow
    }

    if ($Coverage) {
        Write-Host "Coverage reporting enabled" -ForegroundColor Cyan
        $pytestArgs += "--cov=tsv_translator"
        $pytestArgs += "--cov-report=term-missing"
        $pytestArgs += "--cov-report=html:htmlcov"
    }

    if ($Verbose) {
        $pytestArgs += "-v"
    }

    # Run tests
    Write-Host "Executing: uv run pytest $($pytestArgs -join ' ')" -ForegroundColor Gray
    & uv run pytest @pytestArgs

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ All tests passed!" -ForegroundColor Green

        if ($Coverage) {
            Write-Host ""
            Write-Host "📊 Coverage report generated in htmlcov/index.html" -ForegroundColor Cyan
        }
    }
    else {
        Write-Host ""
        Write-Host "❌ Some tests failed!" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}
catch {
    Write-Error "Error running tests: $_"
    exit 1
}
finally {
    Pop-Location
}