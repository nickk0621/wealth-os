$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$python = $null
foreach ($candidate in @("py", "python", "python3")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) { $python = $candidate; break }
}
if (-not $python) { throw "Python 3.10+ was not found." }

& $python -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10+ is required'; print('Using Python', sys.version.split()[0])"

if (-not (Test-Path ".venv")) { & $python -m venv .venv }
$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
$venvPip = Join-Path $Root ".venv\Scripts\pip.exe"

& $venvPython -m pip install --upgrade pip
& $venvPip install -e .

if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
$envText = Get-Content ".env" -Raw
if ($envText -notmatch '(?m)^OPENAI_API_KEY=.+$') {
    $secure = Read-Host "Paste your OpenAI API key (stored only in local .env)" -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try { $key = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
    if ($envText -match '(?m)^OPENAI_API_KEY=.*$') {
        $envText = [regex]::Replace($envText, '(?m)^OPENAI_API_KEY=.*$', "OPENAI_API_KEY=$key")
    } else {
        $envText = $envText.TrimEnd() + "`r`nOPENAI_API_KEY=$key`r`n"
    }
    Set-Content ".env" $envText -NoNewline
}

New-Item -ItemType Directory -Force -Path "secrets", "data" | Out-Null

& (Join-Path $Root ".venv\Scripts\wealth-os.exe") doctor

$answer = Read-Host "Launch the Wealth OS dashboard now? [Y/n]"
if ([string]::IsNullOrWhiteSpace($answer) -or $answer -match '^[Yy]$') {
    & (Join-Path $Root ".venv\Scripts\wealth-os.exe") dashboard
} else {
    Write-Host "Setup complete. Later run: .\.venv\Scripts\Activate.ps1; wealth-os dashboard"
}
