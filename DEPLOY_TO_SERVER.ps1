# Deployment script for Subreddit Recommendation Engine
$SERVER_IP = "168.144.25.244"
$REMOTE_DIR = "/root/subreddit-engine"
$USER = "root"

Write-Host "--- Starting Deployment to $SERVER_IP ---" -ForegroundColor Cyan

# 1. Zip local directory (excluding .venv, .git, and large raw data)
Write-Host "Compressing project files..." -ForegroundColor Yellow
$zipFile = "project.zip"
if (Test-Path $zipFile) { Remove-Item $zipFile }

$tempDir = Join-Path $env:TEMP "deploy_tmp"
if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir }
New-Item -ItemType Directory -Path $tempDir

# Select only relevant files (ignore data/raw which is huge as pipeline will download it on server)
$itemsToCopy = "Dockerfile", "docker-compose.yml", "*.py", "requirements.txt", "models", "app"
foreach ($item in $itemsToCopy) {
    if (Test-Path $item) {
        Copy-Item -Path $item -Destination $tempDir -Recurse -Exclude ".venv", ".git", "__pycache__"
    }
}

if (Test-Path "data") {
    $dataDest = Join-Path $tempDir "data"
    New-Item -ItemType Directory -Path $dataDest
    # Copy processed database (prod.sqlite) but skip huge raw files
    Copy-Item -Path "data\processed" -Destination $dataDest -Recurse -ErrorAction SilentlyContinue
}

Compress-Archive -Path "$tempDir\*" -DestinationPath $zipFile
Remove-Item -Recurse -Force $tempDir

# 2. Transfer project to server
Write-Host "Uploading to server ($SERVER_IP)..." -ForegroundColor Yellow
scp $zipFile "$($USER)@$($SERVER_IP):/root/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Upload failed. Check your password or server SSH settings." -ForegroundColor Red
    if (Test-Path $zipFile) { Remove-Item $zipFile }
    exit 1
}

# 3. SSH into server and setup
Write-Host "Executing remote commands (Docker setup)..." -ForegroundColor Yellow
$sshCmds = @"
apt-get update
apt-get install -y unzip curl
# Install Docker if not present
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
fi
# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-`$(uname -s)-`$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Clean up old images/containers to solve "No space left on device" error
docker system prune -af
docker volume prune -f

# Clean up old database to reset schema
rm -f $REMOTE_DIR/data/processed/prod.sqlite

mkdir -p $REMOTE_DIR
unzip -o /root/$zipFile -d $REMOTE_DIR
cd $REMOTE_DIR
docker-compose down
docker-compose up --build -d
"@

ssh "$($USER)@$($SERVER_IP)" $sshCmds
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Remote command execution failed." -ForegroundColor Red
    Remove-Item $zipFile
    exit 1
}

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Task 1 (Search): http://$SERVER_IP:8000/search?q=query" -ForegroundColor Green
Write-Host "Task 2 (Leads):  http://$SERVER_IP:8000/docs" -ForegroundColor Green
Remove-Item $zipFile
