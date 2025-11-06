# Pants launcher script for PowerShell/Windows
# Auto-downloads and runs the appropriate Pants version from pants.toml

$ErrorActionPreference = "Stop"

# Parse Pants version from pants.toml
$pantsToml = Get-Content "pants.toml" -Raw
if ($pantsToml -match 'pants_version\s*=\s*"([^"]+)"') {
    $pantsVersion = $matches[1]
} else {
    Write-Error "Could not find pants_version in pants.toml"
    exit 1
}

# Set up Pants bootstrap directory
$pantsBootstrap = if ($env:PANTS_BOOTSTRAP) { $env:PANTS_BOOTSTRAP } else { "$env:USERPROFILE\.cache\pants\setup" }
$pantsBinary = "$pantsBootstrap\pants-$pantsVersion.exe"

# Download Pants if not already cached
if (-not (Test-Path $pantsBinary)) {
    Write-Host "Downloading Pants $pantsVersion..."
    New-Item -ItemType Directory -Path $pantsBootstrap -Force | Out-Null

    $downloadUrl = "https://github.com/pantsbuild/scie-pants/releases/download/v$pantsVersion/scie-pants-windows-x86_64.exe"

    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $pantsBinary -UseBasicParsing
        Write-Host "Downloaded Pants $pantsVersion successfully"
    } catch {
        Write-Error "Failed to download Pants: $_"
        exit 1
    }
}

# Execute Pants with all arguments
& $pantsBinary $args
exit $LASTEXITCODE
