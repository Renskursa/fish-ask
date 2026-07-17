$ErrorActionPreference = "Stop"

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$defaultInstallDir = Join-Path $env:LOCALAPPDATA "Programs\fish-ask\bin"
$installDir = if ($env:ASK_INSTALL_DIR) {
    [IO.Path]::GetFullPath($env:ASK_INSTALL_DIR)
} else {
    $defaultInstallDir
}

New-Item -ItemType Directory -Force -Path $installDir | Out-Null
Copy-Item -Force -LiteralPath (Join-Path $repoDir "bin\ask") -Destination $installDir
Copy-Item -Force -LiteralPath (Join-Path $repoDir "bin\ask.cmd") -Destination $installDir

if ($env:ASK_SKIP_PATH -ne "1") {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $entries = @($userPath -split ";" | Where-Object { $_ })
    $expandedInstallDir = [Environment]::ExpandEnvironmentVariables($installDir).TrimEnd("\", "/")
    $alreadyOnPath = $entries | Where-Object {
        [Environment]::ExpandEnvironmentVariables($_).TrimEnd("\", "/") -ieq $expandedInstallDir
    }
    if (-not $alreadyOnPath) {
        $newPath = (@($entries) + $installDir) -join ";"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    }
}

Write-Host "Installed ask in $installDir."
