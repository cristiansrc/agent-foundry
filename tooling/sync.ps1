#Requires -Version 5.1
<#
.SYNOPSIS
  Instala agentes + skills de agent-foundry en OpenCode (Windows).
  Port de tooling/sync.sh + build del adapter OpenCode (adapters/shared/render.py).

.DESCRIPTION
  1. Genera adapters/opencode/out con Python (equivale a tooling/build.sh, parte opencode).
  2. Backup previo en ZIP (equivale al tar.gz de sync.sh).
  3. Replica OUT/agents -> TARGET/agents y OUT/skills -> TARGET/skills (equivale a rsync --delete).
  4. Copia OUT/plugin/foundry-model-router.ts -> TARGET/plugins/.
  5. Fusiona OUT/config.patch.json en TARGET/opencode.json sin tocar MCPs/proveedores.

.USO
  powershell -ExecutionPolicy Bypass -File tooling/sync.ps1
  powershell -ExecutionPolicy Bypass -File tooling/sync.ps1 -Yes
  powershell -ExecutionPolicy Bypass -File tooling/sync.ps1 -SkipBuild -Yes
  $env:AGENT_FOUNDRY_BACKUP_DIR="D:\backups"; .\tooling\sync.ps1 -Yes

REQUISITOS: Python 3 real + PyYAML (python -m pip install pyyaml).
#>
[CmdletBinding()]
param(
  [switch]$Yes,        # no pedir confirmacion
  [switch]$SkipBuild,  # no regenerar OUT, solo instalar
  [string]$Target = "",    # por defecto $env:USERPROFILE\.config\opencode
  [string]$BackupDir = ""  # por defecto $env:AGENT_FOUNDRY_BACKUP_DIR o ~/.local/share/...
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path $PSScriptRoot -Parent
$OUT = Join-Path $ROOT "adapters\opencode\out"
if ([string]::IsNullOrWhiteSpace($Target)) { $Target = Join-Path $env:USERPROFILE ".config\opencode" }
if ([string]::IsNullOrWhiteSpace($BackupDir)) {
  if (-not [string]::IsNullOrWhiteSpace($env:AGENT_FOUNDRY_BACKUP_DIR)) { $BackupDir = $env:AGENT_FOUNDRY_BACKUP_DIR }
  else { $BackupDir = Join-Path $env:USERPROFILE ".local\share\agent-foundry\backups" }
}

function Find-Python {
  foreach ($c in @("python", "py", "python3")) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd) {
      try { & $cmd.Source -c "import yaml" 2>$null; if ($LASTEXITCODE -eq 0) { return $cmd.Source } }
      catch { }
      # python encontrado pero sin yaml: devolverlo igual y fallar despues con mensaje claro
      $script:PythonWithoutYaml = $cmd.Source
    }
  }
  return $null
}

# 1. Build del adapter OpenCode (salta con -SkipBuild)
$agentsOut = Join-Path $OUT "agents"
$pluginOut = Join-Path $OUT "plugin\foundry-model-router.ts"
$patchOut = Join-Path $OUT "config.patch.json"
if (-not $SkipBuild) {
  $Python = Find-Python
  if (-not $Python) {
    if ($script:PythonWithoutYaml) { throw "Python encontrado en '$($script:PythonWithoutYaml)' pero sin PyYAML. Ejecuta: python -m pip install pyyaml" }
    throw "Python 3 no encontrado. Instala con: winget install Python.Python.3.12  (luego: python -m pip install pyyaml)"
  }
  Write-Host "== Build: opencode =="
  & $Python (Join-Path $ROOT "adapters\shared\render.py")
  if ($LASTEXITCODE -ne 0) { throw "Fallo el render de OpenCode (exit $LASTEXITCODE)" }
}

# 2. Verificar OUT (igual que sync.sh:9-16)
if (-not (Test-Path $agentsOut)) { throw "ERROR: no existe $agentsOut. Ejecuta sin -SkipBuild para generarlo." }
if (-not (Test-Path $pluginOut)) { throw "ERROR: falta $pluginOut. Ejecuta sin -SkipBuild para generarlo." }
if (-not (Test-Path $patchOut)) { throw "ERROR: falta $patchOut. Ejecuta sin -SkipBuild para generarlo." }

$nAgents = (Get-ChildItem $agentsOut -Filter *.md | Measure-Object).Count
$skillsOut = Join-Path $OUT "skills"
$nSkills = 0
if (Test-Path $skillsOut) { $nSkills = (Get-ChildItem $skillsOut -Directory | Measure-Object).Count }

Write-Host "Esto sobrescribira:"
Write-Host "  $Target\agents\*.md   <- $agentsOut ($nAgents archivos)"
Write-Host "  $Target\skills\*      <- $skillsOut ($nSkills skills)"
Write-Host "  $Target\plugins\foundry-model-router.ts <- $pluginOut"
Write-Host "  $Target\opencode.json <- fusiona default_agent sin tocar MCPs/proveedores"
if (-not $Yes) {
  $answer = Read-Host "Continuar? [y/N]"
  if ($answer -ne "y" -and $answer -ne "Y") { Write-Host "Cancelado."; exit 1 }
}

# 3. Backup previo (equivale al tar.gz de sync.sh:28-34)
New-Item -ItemType Directory -Force $Target | Out-Null
New-Item -ItemType Directory -Force $BackupDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupZip = Join-Path $BackupDir "opencode-pre-sync-$stamp.zip"
$backupItems = @()
foreach ($n in @("agents", "skills", "plugins")) {
  $p = Join-Path $Target $n
  if (Test-Path $p) { $backupItems += $p }
}
$jsonTarget = Join-Path $Target "opencode.json"
if (Test-Path $jsonTarget) { $backupItems += $jsonTarget }
if ($backupItems.Count -gt 0) {
  Compress-Archive -Path $backupItems -DestinationPath $backupZip -Force
  Write-Host "Backup: $backupZip"
} else {
  Write-Host "Backup: omitido (TARGET vacio, primera instalacion)"
  $backupZip = $null
}

# 4. Replica con limpieza (equivale a rsync --delete de sync.sh:36-37)
function Sync-Dir([string]$From, [string]$To) {
  New-Item -ItemType Directory -Force $To | Out-Null
  Get-ChildItem -Path $To -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item -Path (Join-Path $From "*") -Destination $To -Recurse -Force
}
Sync-Dir $agentsOut (Join-Path $Target "agents")
Sync-Dir $skillsOut (Join-Path $Target "skills")
New-Item -ItemType Directory -Force (Join-Path $Target "plugins") | Out-Null
Copy-Item -Path $pluginOut -Destination (Join-Path $Target "plugins\foundry-model-router.ts") -Force
Write-Host "Copiados: $nAgents agentes, $nSkills skills + plugin."

# 5. Fusion JSON (equivale al bloque python de sync.sh:40-49: solo actualiza claves del patch)
$patch = Get-Content -Raw -Path $patchOut | ConvertFrom-Json
$current = @{}
if (Test-Path $jsonTarget) {
  $raw = Get-Content -Raw -Path $jsonTarget
  if (-not [string]::IsNullOrWhiteSpace($raw)) {
    $obj = $raw | ConvertFrom-Json
    foreach ($prop in $obj.PSObject.Properties) { $current[$prop.Name] = $prop.Value }
  }
}
foreach ($prop in $patch.PSObject.Properties) { $current[$prop.Name] = $prop.Value }
($current | ConvertTo-Json -Depth 20) + "`n" | Set-Content -Path $jsonTarget -Encoding UTF8
Write-Host "opencode.json actualizado (MCPs/proveedores intactos)."

Write-Host ""
Write-Host "SYNC OK"
if ($backupZip) {
  Write-Host "Rollback si hace falta:"
  Write-Host "  Expand-Archive -Path `"$backupZip`" -DestinationPath `"$Target`" -Force"
}
Write-Host "Reinicia OpenCode (config y plugins cargan al arrancar)."
