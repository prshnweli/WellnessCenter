. "$PSScriptroot\..\settings.ps1"

$file = @("errors.csv")

$Body = "
Attached is a spreadsheet of ids that were checked in today that do not exist in our current database.
These records will not be added into Aeries. 
"

$Email = @{
    To = $Global:Recipients
    Body = $Body
    Subject = "Wellness Center Errors"
    Attachments = $file
}
Send-MailMessage @smtp @Email
