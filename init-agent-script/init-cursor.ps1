#Requires -Version 5.1
<#
.SYNOPSIS
  建立 .cursor → .agents 的 Junction，供 Cursor 使用本機唯一真實設定。

.DESCRIPTION
  - 僅在 repo 內以相對路徑推算根目錄，不寫死磁碟機路徑。
  - 若 .cursor 已是指向 .agents 的 Junction，視為已完成並結束。
  - 若 .cursor 已存在且為實體資料夾（或指向其他目標的捷徑），拒絕覆蓋並警告。
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
    # 本腳本位於 .agents/init-script/
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

Initialize-Utf8Console

$RepoRoot = Get-RepoRoot
Set-Location -LiteralPath $RepoRoot

$AgentsPath = Join-Path $RepoRoot '.agents'
$CursorPath = Join-Path $RepoRoot '.cursor'

Write-Host '========================================' -ForegroundColor Cyan
Write-Host ' Cursor 本機捷徑初始化 (init-cursor)' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ("Repo 根目錄: {0}" -f $RepoRoot)
Write-Host ''

if (-not (Test-Path -LiteralPath $AgentsPath -PathType Container)) {
    Write-Host '[錯誤] 找不到唯一真實目錄 .agents，請確認是在完整 clone 的 repo 內執行。' -ForegroundColor Red
    Wait-AndExit 1
}

if (Test-Path -LiteralPath $CursorPath) {
    $cursorItem = Get-Item -LiteralPath $CursorPath -Force
    $linkType = $cursorItem.LinkType
    $target = Get-LinkTargetPath -Item $cursorItem

    if ($linkType -eq 'Junction' -and (Test-SamePath -Left $target -Right $AgentsPath)) {
        Write-Host '[完成] .cursor 已是指向 .agents 的 Junction，無需再建。' -ForegroundColor Green
        Wait-AndExit 0
    }

    Write-Host '[警告] 偵測到既有的 .cursor，且不是本腳本應建立的 Junction（指向 .agents）。' -ForegroundColor Yellow
    Write-Host '       為避免覆蓋您本機的原始設定，已中止，不會刪除或覆寫任何內容。' -ForegroundColor Yellow
    Write-Host ''
    Write-Host ("  路徑     : {0}" -f $CursorPath)
    Write-Host ("  類型     : {0}" -f $(if ($linkType) { $linkType } else { '實體資料夾/檔案' }))
    if ($target) {
        Write-Host ("  目前目標 : {0}" -f $target)
    }
    Write-Host ''
    Write-Host '請您自行備份並移除（或改名）該路徑後，再重新執行本腳本：' -ForegroundColor Yellow
    Write-Host ("  {0}" -f $PSCommandPath)
    Wait-AndExit 1
}

try {
    New-Item -ItemType Junction -Path $CursorPath -Target $AgentsPath | Out-Null
    Write-Host '[完成] 已建立 Junction：.cursor → .agents' -ForegroundColor Green
    Wait-AndExit 0
} catch {
    Write-Host '[錯誤] 建立 .cursor Junction 失敗。' -ForegroundColor Red
    Write-Host ("  {0}" -f $_.Exception.Message) -ForegroundColor Red
    Wait-AndExit 1
}
