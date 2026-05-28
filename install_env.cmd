@echo off
REM 绕过 PowerShell 执行策略，运行依赖安装脚本（带进度 / ETA 监视说明见 README）
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_env.ps1" %*
