#Requires -Version 5.1
<#
.SYNOPSIS
  建立 .claude → .agents 的 Junction，以及根目錄 .mcp.json → .agents/mcp.json 的 SymbolicLink。

.DESCRIPTION
  - 僅在 repo 內以相對路徑推算根目錄，不寫死磁碟機路徑。
  - 若目標已是正確捷徑，該步驟略過。
  - 若路徑已存在且為實體資料夾/檔案（或錯誤捷徑），拒絕覆蓋並警告。
  - 根目錄 .mcp.json 使用 SymbolicLink；若權限不足，提示改以系統管理員身分執行。
#>

$ErrorActionPreference = 'Stop'

function Initialize-Utf8Console {
    try {
        chcp 65001 | Out-Null
    } catch {}
    $utf8 = [System.Text.UTF8Encoding]::new($false)
    try { [Console]::InputEncoding = $utf8 } catch {}
    try { [Console]::OutputEncoding = $utf8 } catch {}
    $global:OutputEncoding = $utf8
}

function Wait-AndExit {
    param([int]$Code = 0)
    Write-Host ''
    Read-Host '按 Enter 鍵結束'
    exit $Code
}

function Get-RepoRoot {
    # 本腳本位於 .agents/init-agent-script/
    return (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

function Get-LinkTargetPath {
    param([System.IO.FileSystemInfo]$Item)
    if (-not $Item.LinkType) { return $null }
    $t = $Item.Target
    if ($null -eq $t) { return $null }
    if ($t -is [Array]) {
        if ($t.Count -eq 0) { return $null }
        return [string]$t[0]
    }
    return [string]$t
}

function Test-SamePath {
    param([string]$Left, [string]$Right)
    if ([string]::IsNullOrWhiteSpace($Left) -or [string]::IsNullOrWhiteSpace($Right)) {
        return $false
    }
    $leftFull = [System.IO.Path]::GetFullPath($Left).TrimEnd('\', '/')
    $rightFull = [System.IO.Path]::GetFullPath($Right).TrimEnd('\', '/')
    return [string]::Equals($leftFull, $rightFull, [System.StringComparison]::OrdinalIgnoreCase)
}

function Test-IsExpectedAgentsJunction {
    param(
        [System.IO.FileSystemInfo]$Item,
        [string]$AgentsPath
    )
    if ($Item.LinkType -ne 'Junction') { return $false }
    $target = Get-LinkTargetPath -Item $Item
    return (Test-SamePath -Left $target -Right $AgentsPath)
}

function Test-IsExpectedMcpSymlink {
    param(
        [System.IO.FileSystemInfo]$Item,
        [string]$RepoRoot,
        [string]$AgentsMcpPath
    )
    if ($Item.LinkType -ne 'SymbolicLink') { return $false }
    $target = Get-LinkTargetPath -Item $Item
    if ([string]::IsNullOrWhiteSpace($target)) { return $false }

    # Target 可能是相對路徑（例如 .agents\mcp.json）或絕對路徑
    if ([System.IO.Path]::IsPathRooted($target)) {
        return (Test-SamePath -Left $target -Right $AgentsMcpPath)
    }
    $resolved = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $target))
    return (Test-SamePath -Left $resolved -Right $AgentsMcpPath)
}

function Show-ConflictAndExit {
    param(
        [string]$Path,
        [System.IO.FileSystemInfo]$Item,
        [string]$ExpectedDescription
    )
    $linkType = $Item.LinkType
    $target = Get-LinkTargetPath -Item $Item

    Write-Host ('[警告] 偵測到既有的 {0}，且不是本腳本應建立的捷徑（{1}）。' -f $Path, $ExpectedDescription) -ForegroundColor Yellow
    Write-Host '       為避免覆蓋您本機的原始設定，已中止，不會刪除或覆寫任何內容。' -ForegroundColor Yellow
    Write-Host ''
    Write-Host ("  路徑     : {0}" -f $Path)
    Write-Host ("  類型     : {0}" -f $(if ($linkType) { $linkType } else { '實體資料夾/檔案' }))
    if ($target) {
        Write-Host ("  目前目標 : {0}" -f $target)
    }
    Write-Host ''
    Write-Host '請您自行備份並移除（或改名）該路徑後，再重新執行本腳本：' -ForegroundColor Yellow
    Write-Host ("  {0}" -f $PSCommandPath)
    Wait-AndExit 1
}

Initialize-Utf8Console

$RepoRoot = Get-RepoRoot
Set-Location -LiteralPath $RepoRoot

$AgentsPath = Join-Path $RepoRoot '.agents'
$ClaudePath = Join-Path $RepoRoot '.claude'
$AgentsMcpPath = Join-Path $AgentsPath 'mcp.json'
$RootMcpPath = Join-Path $RepoRoot '.mcp.json'
# 相對目標：以 repo 根目錄為基準，利於各機器通用
$RootMcpRelativeTarget = Join-Path '.agents' 'mcp.json'

Write-Host '========================================' -ForegroundColor Cyan
Write-Host ' Claude Code 本機捷徑初始化 (init-claude)' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ("Repo 根目錄: {0}" -f $RepoRoot)
Write-Host ''

if (-not (Test-Path -LiteralPath $AgentsPath -PathType Container)) {
    Write-Host '[錯誤] 找不到唯一真實目錄 .agents，請確認是在完整 clone 的 repo 內執行。' -ForegroundColor Red
    Wait-AndExit 1
}

if (-not (Test-Path -LiteralPath $AgentsMcpPath -PathType Leaf)) {
    Write-Host '[錯誤] 找不到唯一真實檔案 .agents/mcp.json。' -ForegroundColor Red
    Wait-AndExit 1
}

# ---- 預檢查：任一衝突則整段中止（不部分建立）----
$claudeOk = $false
$mcpOk = $false

if (Test-Path -LiteralPath $ClaudePath) {
    $claudeItem = Get-Item -LiteralPath $ClaudePath -Force
    if (Test-IsExpectedAgentsJunction -Item $claudeItem -AgentsPath $AgentsPath) {
        $claudeOk = $true
    } else {
        Show-ConflictAndExit -Path $ClaudePath -Item $claudeItem -ExpectedDescription '.claude → .agents 的 Junction'
    }
}

if (Test-Path -LiteralPath $RootMcpPath) {
    $mcpItem = Get-Item -LiteralPath $RootMcpPath -Force
    if (Test-IsExpectedMcpSymlink -Item $mcpItem -RepoRoot $RepoRoot -AgentsMcpPath $AgentsMcpPath) {
        $mcpOk = $true
    } else {
        Show-ConflictAndExit -Path $RootMcpPath -Item $mcpItem -ExpectedDescription '.mcp.json → .agents/mcp.json 的 SymbolicLink'
    }
}

# ---- 建立 Junction ----
if ($claudeOk) {
    Write-Host '[略過] .claude 已是指向 .agents 的 Junction。' -ForegroundColor Green
} else {
    try {
        New-Item -ItemType Junction -Path $ClaudePath -Target $AgentsPath | Out-Null
        Write-Host '[完成] 已建立 Junction：.claude → .agents' -ForegroundColor Green
    } catch {
        Write-Host '[錯誤] 建立 .claude Junction 失敗。' -ForegroundColor Red
        Write-Host ("  {0}" -f $_.Exception.Message) -ForegroundColor Red
        Wait-AndExit 1
    }
}

# ---- 建立 SymbolicLink（.mcp.json）----
if ($mcpOk) {
    Write-Host '[略過] 根目錄 .mcp.json 已是指向 .agents/mcp.json 的 SymbolicLink。' -ForegroundColor Green
} else {
    try {
        New-Item -ItemType SymbolicLink -Path $RootMcpPath -Target $RootMcpRelativeTarget | Out-Null
        Write-Host '[完成] 已建立 SymbolicLink：.mcp.json → .agents/mcp.json' -ForegroundColor Green
    } catch {
        Write-Host '[錯誤] 建立根目錄 .mcp.json 的 SymbolicLink 失敗。' -ForegroundColor Red
        Write-Host ("  {0}" -f $_.Exception.Message) -ForegroundColor Red
        Write-Host ''
        Write-Host 'Windows 建立 SymbolicLink 通常需要「系統管理員權限」，或已啟用「開發人員模式」。' -ForegroundColor Yellow
        Write-Host '請改以「系統管理員身分」開啟 PowerShell 後，再執行本腳本：' -ForegroundColor Yellow
        Write-Host ("  {0}" -f $PSCommandPath)
        Write-Host ''
        Write-Host '（若 .claude Junction 已在上方建立成功，可保留；修好權限後重跑即可補上 .mcp.json。）' -ForegroundColor DarkYellow
        Wait-AndExit 1
    }
}

Write-Host ''
Write-Host '[完成] Claude Code 本機捷徑已就緒。' -ForegroundColor Green
Wait-AndExit 0
