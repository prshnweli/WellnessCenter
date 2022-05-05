$ErrorActionPreference = 'stop'
$ProgressPreference = 'SilentlyContinue'


$Global:BackupDir = "$PSScriptRoot\Backups"
$Global:TempDir = "$PSScriptRoot\Temp"
$Global:SqlDir = "$PSScriptRoot\Sql"
$Global:ModuleDir = "$PSScriptRoot\Modules"

# Email Server
$Global:SMTP = @{
    UseSsl     = $true
    Bcc        = 'spam@mhusd.org'
    From       = 'noreply@mhusd.org'
    SmtpServer = 'smtp-relay.gmail.com'
}

$Global:Recipients = @(
    'welipitiyap@mhusd.org'
    'citerellan@mhusd.org'
)
