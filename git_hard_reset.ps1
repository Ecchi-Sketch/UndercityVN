# Script to perform a git hard reset after fetching and showing the log

# Fetch from origin
Write-Host "Fetching from origin... (git fetch origin)"
& git fetch origin

# Show log for origin/main
Write-Host "Displaying log for origin/main... (git log origin/main --oneline --graph)"
& git log origin/main --oneline --graph --max-count=20 # Limiting to 20 commits for brevity

# Prompt user for commit hash
$commitHash = Read-Host -Prompt "Enter the commit hash to reset to (e.g., a1b2c3d). BE CAREFUL: This is a destructive operation!"

if ([string]::IsNullOrWhiteSpace($commitHash)) {
    Write-Error "No commit hash entered. Aborting reset."
    exit 1
}

# Confirm hard reset
$confirmation = Read-Host -Prompt "Are you sure you want to hard reset to '$commitHash'? This will discard local changes and unpushed commits. Type 'yes' to confirm."

if ($confirmation -ne 'yes') {
    Write-Host "Hard reset aborted by user."
    exit 0
}

# Perform hard reset
Write-Host "Performing hard reset to '$commitHash'... (git reset --hard $commitHash)"
& git reset --hard $commitHash

Write-Host "Hard reset process complete. Current status:"
& git status
