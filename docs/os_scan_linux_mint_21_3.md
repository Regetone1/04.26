# Проверка Linux Mint 21.3 Virginia на уязвимости

В выданной формулировке лабораторной работы подробно описаны задачи 1–3 по зависимостям проекта. Так как в варианте дополнительно указан дистрибутив **Linux Mint 21.3**, ниже приведён набор команд, который можно использовать для проверки ОС и включить в демонстрацию.

## Информация о системе

```bash
lsb_release -a
uname -a
cat /etc/os-release
```

## Обновление индексов пакетов

```bash
sudo apt update
apt list --upgradable
```

## Проверка доступных security-обновлений

```bash
sudo apt install update-manager-core unattended-upgrades needrestart -y
ubuntu-security-status
sudo unattended-upgrade --dry-run --debug
needrestart -r l
```

## Проверка системы Lynis

```bash
sudo apt install lynis -y
sudo lynis audit system --quick
```

## Дополнительная проверка Trivy

```bash
sudo apt install wget apt-transport-https gnupg lsb-release -y
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo gpg --dearmor -o /usr/share/keyrings/trivy.gpg
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt update
sudo apt install trivy -y
sudo trivy fs --scanners vuln --severity HIGH,CRITICAL /
```

## Рекомендуемые действия по итогам проверки ОС

1. Установить security-обновления через `sudo apt upgrade`.
2. Перезагрузить систему, если `needrestart` показывает необходимость перезапуска ядра или сервисов.
3. Включить автоматические security-обновления через `unattended-upgrades`.
4. Удалить неиспользуемые пакеты через `sudo apt autoremove`.
5. Повторить проверку Lynis/Trivy после обновления.
