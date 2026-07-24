skill 和 commands 統一儲存在 .agents/ 底下
使用腳本建立 agent 專用捷徑
只需要執行一次

in workspace
1. add .agents/ to .gitignore
2. .vscode/settings.json
{
  "git.autoRepositoryDetection": true,
  "git.repositoryScanMaxDepth": 1
}