cd C:\Users\Prashan.Welipitiya\Documents\Prashan\WellnessCenter

if (test-path '$PSScriptRoot\errors.csv'){
  Remove-Item '$PSScriptRoot\errors.csv'
}

# Run the Python Script
python run.py

& "$PSScriptRoot\Tasks\email.ps1"
