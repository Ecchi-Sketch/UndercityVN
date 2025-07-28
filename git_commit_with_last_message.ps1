# Script to perform git status, add all, and commit with the last commit message pre-populated

# Show git status
Write-Host "Showing git status..."
& git status

# Add all changes
Write-Host "Adding all changes... (git add .)"
& git add .

# Get the last commit message
$lastCommitMessage = (& git log -1 --pretty=%B).Trim()

# Prompt the user with the last commit message, allowing them to edit it
Write-Host "Last commit message was: '$lastCommitMessage'"
$commitMessage = Read-Host -Prompt "Enter commit message (defaults to last message if empty, or type your new message)"

if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = $lastCommitMessage
}

# Commit with the specified message
Write-Host "Committing with message: '$commitMessage'..."
& git commit -m "$commitMessage"

Write-Host "Pushing changes to remote... (git push)"
& git push

Write-Host "Commit and push process complete."
