# Инструкция по автоматическому деплою и обновлению ПО

## Содержимое

2. [Обновление уже развернутого ПО](#обновление-уже-развернутого-по)
   1. [Обновить ПО до текущего коммита](#обновить-по-до-текущего-коммита)
   2. [Обновить ПО из другой ветки](#обновить-по-из-другой-ветки)
3. [Первичный деплой в окружение dev-naughty-swanson](#первичный-деплой-в-окружение-dev-naughty-swanson)
   1. [Создание недостающих секретов](#создание-недостающих-секретов)
   2. [Добавление суперюзера](#добавление-суперюзера)


## Обновление уже развернутого ПО

### Обновить ПО до текущего коммита

Этот вариант деплоя подойдёт вам, если вы хотите выкатить на сервер текущий коммит — тот, в котором сейчас находится ваш репозиторий с кодом.

Получите информацию о последнем коммите:
```shell
git log -1
# пример вывода:
# commit db06af20bff6df565788a626674f67af379cb863 (HEAD -> main, origin/main, origin/HEAD)
# Author: Sergryap <rs1180@mail.ru>
# Date:   Tue Aug 15 10:50:17 2023 +0500
#
#    Minor handle_proxys_exception testing improvement
```

Убедитесь, что в [GitLab CI/CD Pipelines](https://gitlab.levelupdev.ru/proxys-io/proxys-telegram-bot/-/pipelines) готова сборка для вашего коммита. Докер-образы собираются автоматически после пуша в репозиторий. Процесс занимает до пяти минут.

Если нашли нужную сборку, то запустите деплойный скрипт:

```shell
bash envs/dev-naughty-swanson/deploy.sh
# Пример вывода при успешном деплое:
# …
# Project deployed successfully
# Commit hash of deployed version:: c900c9221d62e24ef227e2c427db5caaed81d051
```

Админ-панель будет доступна по адресу [https://dev-naughty-swanson.sirius-k8s.dvmn.org/admin/](https://dev-naughty-swanson.sirius-k8s.dvmn.org/admin/). Логин и пароль суперпользователя: `root`, `dfpkdsmgnnb*34865h!3`.

Если суперюзера в БД нет, воспользуйтесь [инструкцией](#добавление-суперюзера) по созданию нового суперюзера.

### Обновить ПО из другой ветки

Если вы находитесь в одной ветке репозитория с незакоммиченными изменениями, а надо срочно обновить ПО из другой ветки, например, из `main`, то воспользуйтесь git stash. Сохраните незакоммиченные изменения:

```shell
git stash save
```

Перейдите в другую ветку `main`:

```shell
git checkout main
```

Получите информацию о последнем коммите:
```shell
git log -1
# пример вывода:
# commit db06af20bff6df565788a626674f67af379cb863 (HEAD -> main, origin/main, origin/HEAD)
# Author: Sergryap <rs1180@mail.ru>
# Date:   Tue Aug 15 10:50:17 2023 +0500
#
#    Minor handle_proxys_exception testing improvement
```

Убедитесь, что в [GitLab CI/CD Pipelines](https://gitlab.levelupdev.ru/proxys-io/proxys-telegram-bot/-/pipelines) готова сборка для вашего коммита. Докер-образы собираются автоматически после пуша в репозиторий. Процесс занимает до пяти минут.

Если нашли нужную сборку, то запустите деплойный скрипт:

```shell
bash envs/dev-naughty-swanson/deploy.sh
# Пример вывода при успешном деплое:
# …
# Project deployed successfully
# Commit hash of deployed version:: c900c9221d62e24ef227e2c427db5caaed81d051
```

Затем вернитесь на прежнюю ветку и введите команду:

```shell
git stash pop
```

Все незакоммиченные изменения будут возвращены, и вы снова окажетесь в состоянии, в котором были до переключения на ветку main.

## Первичный деплой в окружение dev-naughty-swanson

Установите и настройте себе `kubectl` локально прежде, чем двигаться дальше по инструкциям.

В облаке уже должны быть выделены ресурсы. [dev-naughty-swanson](https://sirius-env-registry.website.yandexcloud.net/dev-naughty-swanson.html).

### Создание недостающих секретов

Создайте манифест django-secret.yaml:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: django
  namespace: dev-naughty-swanson
stringData:
  debug: "false"
  secret_key: "your-secret-key"  # Замените значение на своё
  webapp_root_url: "your-webapp-root-url"  # Замените значение на своё
```

Затем запустите его командой:

```shell
kubectl apply -f django-secret.yaml
# …
# secret/django created
```

Создайте манифест tg-bot-secret.yaml:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tg-bot
  namespace: dev-naughty-swanson
stringData:
  bot_username: "your-bot-username"  # Замените значение на своё
  token: "your-bot-token"  # Замените значение на своё
  webhook_token: "your-webhook-token"  # Замените значение на своё
```

Затем запустите его командой:

```shell
kubectl apply -f tg-bot-secret.yaml
# …
# secret/tg-bot created
```

### Добавление суперюзера

Получите имя запущенного пода с помощью команды:

```shell
kubectl get pods
# …
# NAME                                 READY   STATUS    RESTARTS   AGE
# django-deployment-5bf4545594-sl5c4   1/1     Running   0          7d13h
```

Чтобы попасть в оболочку bash внутри пода запустите команду:

```shell
kubectl exec -it django-deployment-5bf4545594-sl5c4 bash
# Вместо django-deployment-5bf4545594-sl5c4 используйте имя вашего пода
# …
# kubectl exec [POD] [COMMAND] is DEPRECATED and will be removed in a future version. Use kubectl exec [POD] -- [COMMAND] instead.
# root@django-deployment-5bf4545594-sl5c4:/opt/app/src#
```

Создайте суперюзера:

```shell
./manage.py createsuperuser
```

Для выхода из bash-оболочки пода введите `exit`.


Запустить сценарий развертывания:

```shell
bash envs/dev-naughty-swanson/deploy.sh
# Пример вывода при успешном деплое:
# …
# Project deployed successfully
# Commit hash of deployed version:: c900c9221d62e24ef227e2c427db5caaed81d051
```

Админ-панель будет доступна по адресу [https://dev-naughty-swanson.sirius-k8s.dvmn.org/admin](https://dev-naughty-swanson.sirius-k8s.dvmn.org/admin). Для авторизации введите имя и пароль созданного суперюзера.
