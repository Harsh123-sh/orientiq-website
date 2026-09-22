# Starts the local Django server on the first available localhost port,
# beginning with 8000. It never stops or changes processes using a port.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "ORENTIQ's virtual environment was not found at .venv\\Scripts\\python.exe. Create or restore .venv, then try again."
}

function Test-LocalPortAvailable {
    param([int]$Port)

    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
    try {
        $listener.Start()
        return $true
    }
    catch [System.Net.Sockets.SocketException] {
        return $false
    }
    finally {
        $listener.Stop()
    }
}

$port = 8000
while (-not (Test-LocalPortAvailable -Port $port)) {
    $port++
}

if ($port -eq 8000) {
    Write-Host "Starting ORENTIQ on port 8000."
}
elseif ($port -eq 8001) {
    Write-Host "Port 8000 is already in use. Starting ORENTIQ on port 8001."
}
else {
    $occupiedPorts = (8000..($port - 1)) -join ", "
    Write-Host "Ports $occupiedPorts are in use. Starting ORENTIQ on port $port."
}

Write-Host "Open http://127.0.0.1:$port/"
& $python manage.py runserver "127.0.0.1:$port" @args
exit $LASTEXITCODE
