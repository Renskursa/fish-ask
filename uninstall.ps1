$ErrorActionPreference = "Stop"

$defaultInstallDir = Join-Path $env:LOCALAPPDATA "Programs\fish-ask\bin"
$installDir = if ($env:ASK_INSTALL_DIR) {
    [IO.Path]::GetFullPath($env:ASK_INSTALL_DIR)
} else {
    $defaultInstallDir
}

foreach ($fileName in @("ask", "ask.cmd")) {
    $filePath = Join-Path $installDir $fileName
    if (Test-Path -LiteralPath $filePath) {
        Remove-Item -Force -LiteralPath $filePath
    }
}

if ((Test-Path -LiteralPath $installDir) -and -not (Get-ChildItem -Force -LiteralPath $installDir)) {
    Remove-Item -Force -LiteralPath $installDir
    $installRoot = Split-Path -Parent $installDir
    if ((Test-Path -LiteralPath $installRoot) -and -not (Get-ChildItem -Force -LiteralPath $installRoot)) {
        Remove-Item -Force -LiteralPath $installRoot
    }
}

if ($env:ASK_SKIP_PATH -ne "1") {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $expandedInstallDir = [Environment]::ExpandEnvironmentVariables($installDir).TrimEnd("\", "/")
    $entries = @($userPath -split ";" | Where-Object {
        $_ -and (
            [Environment]::ExpandEnvironmentVariables($_).TrimEnd("\", "/") -ine $expandedInstallDir
        )
    })
    [Environment]::SetEnvironmentVariable("Path", ($entries -join ";"), "User")
}

Write-Host "Uninstalled ask. Open a new Command Prompt to refresh PATH."
