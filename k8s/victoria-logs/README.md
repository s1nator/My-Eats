# Деплой VictoriaLogs и Vector

Команды, использованные для установки VictoriaLogs и доставки логов из Kubernetes через Vector.

Команды необходимо выполнять из этой директории, чтобы Helm-файлы values были доступны по указанным относительным путям:

```bash
cd k8s/victoria-logs
```

## Установка VictoriaLogs

```bash
helm repo add vm https://victoriametrics.github.io/helm-charts
helm repo update

kubectl create namespace victoria-logs

helm install victoria-logs vm/victoria-logs-single \
  --namespace victoria-logs \
  -f values.yaml
```

## Установка Vector

```bash
helm repo add vector https://helm.vector.dev
helm repo update

helm install vector vector/vector \
  --namespace victoria-logs \
  -f vector-values.yaml
```

Конфигурация Vector находится в файле
[`vector-values.yaml`](./vector-values.yaml), а результаты проверки поступления
логов — в [`Отчет.md`](./Отчет.md).
