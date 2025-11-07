#Requires -Version 5.1
param(
  [Parameter(Mandatory=$true)][string]$Host,
  [string]$Ref = "main",
  [int]$TimeoutSec = 180
)
$ErrorActionPreference = 'Stop'
# Примерная идемпотентная обёртка: дергает Ansible playbook вашего проекта.
# Здесь демонстрационный вызов — замените путь/команду под вашу инфраструктуру.
try {
  Write-Output "DEPLOY host=$Host ref=$Ref"
  # Пример: ansible-playbook -i infra/ansible/inventory -e host=$Host -e ref=$Ref infra/ansible/playbook.yml
  # Здесь вместо Ansible — эмуляция шага:
  Start-Sleep -Seconds 3
  Write-Output "DEPLOY DONE host=$Host ref=$Ref"
  exit 0
} catch {
  Write-Output "DEPLOY FAIL: $($_.Exception.Message)"
  exit 2
}


