# PowerShell script to run the Pharmacy POS application
Write-Host "Pharmacy POS System" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "Starting application..." -ForegroundColor Yellow

try {
    Set-Location -Path "D:\POS"
    python main.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to start the application" -ForegroundColor Red
        Write-Host "Please check if Python is installed and in your PATH" -ForegroundColor Red
        pause
    }
} catch {
    Write-Host "Error running the application: $_" -ForegroundColor Red
    pause
}