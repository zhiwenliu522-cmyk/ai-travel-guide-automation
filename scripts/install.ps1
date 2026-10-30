param(
    [string]$CodexRoot
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($CodexRoot)) {
    $userProfilePath = [Environment]::GetFolderPath('UserProfile')
    $CodexRoot = Join-Path $userProfilePath '.codex'
}

$projectRoot = Split-Path -Parent $PSScriptRoot
$sourceSkill = Join-Path $projectRoot 'skills\customize-travel-guide'
$skillsRoot = Join-Path $CodexRoot 'skills'
$destinationSkill = Join-Path $skillsRoot 'customize-travel-guide'

if (-not (Test-Path -LiteralPath (Join-Path $sourceSkill 'SKILL.md'))) {
    throw "未找到 Skill 源文件：$sourceSkill"
}

New-Item -ItemType Directory -Force -Path $destinationSkill | Out-Null
Copy-Item -Path (Join-Path $sourceSkill '*') -Destination $destinationSkill -Recurse -Force

Write-Host "已安装到：$destinationSkill"
Write-Host '请重启 Codex 后使用 $customize-travel-guide'

