# Check for Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git not found. Installing Git..."
    winget install --id Git.Git -e --source winget
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Check for GitHub CLI
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "GitHub CLI not found. Installing GitHub CLI..."
    winget install --id GitHub.cli -e --source winget
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Configure Git
git config --global user.email "abhijeet.naib1993@gmail.com"
git config --global user.name "Abhijeet Naib"

# Login to GitHub
Write-Host "Please login to GitHub..."
gh auth login

# Initialize and Publish Repo
if (-not (Test-Path .git)) {
    git init
    git add .
    git commit -m "Initial commit"
}

# Create GitHub Repo and Push
# Check if remote origin exists
if (-not (git remote get-url origin -ErrorAction SilentlyContinue)) {
    gh repo create pocketbuzz --public --source=. --remote=origin
    git push -u origin main
} else {
    Write-Host "Remote origin already exists."
    git push -u origin main
}
