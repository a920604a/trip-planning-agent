param(
    [string]$action = "start"  # 預設動作 start，可選 start / stop
)

# 設定要用的端口與 server
$servers = @(
    @{ name="weather_server"; port=8001; module="agents.weather_server:app" },
    @{ name="map_server"; port=8002; module="agents.map_server:app" }
)

function Stop-Servers {
    foreach ($srv in $servers) {
        $port = $srv.port
        $pids = netstat -ano | findstr ":$port" | ForEach-Object { ($_ -split '\s+')[-1] }
        foreach ($processId in $pids) {
            if ($processId) {
                Write-Host "Stopping $($srv.name) on port $port (PID $processId)"
                taskkill /PID $processId /F | Out-Null
            }
        }
    }
    Write-Host "✅ All specified servers stopped."
}

function Start-Servers {
    # 先停止已有 server
    Stop-Servers

    # 設定環境變數
    try {
        $GOOGLE_API_KEY = [System.Environment]::GetEnvironmentVariable("GOOGLE_API_KEY")
        $GOOGLE_MAPS_API_KEY = [System.Environment]::GetEnvironmentVariable("GOOGLE_MAPS_API_KEY")
        [System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", $GOOGLE_API_KEY, "Process")
        [System.Environment]::SetEnvironmentVariable("GOOGLE_MAPS_API_KEY", $GOOGLE_MAPS_API_KEY, "Process")
        Write-Host "✅ Setup and authentication complete."
    } catch {
        Write-Host "🔑 Authentication Error: $_"
    }

    # 啟動 server
    foreach ($srv in $servers) {
        $module = $srv.module
        $port = $srv.port
        Write-Host "Starting $($srv.name) on port $port..."
        Start-Process -NoNewWindow -FilePath "uvicorn" -ArgumentList "$module --host localhost --port $port"
    }
    Write-Host "✅ All specified servers started."
}

switch ($action.ToLower()) {
    "start" { Start-Servers }
    "stop"  { Stop-Servers }
    default { Write-Host "Invalid action. Use 'start' or 'stop'." }
}
