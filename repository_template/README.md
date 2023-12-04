# Your project name


## Содержимое

1. [Как развернуть local-окружение](#local-setup)
2. [Как вести разработку](#development)
    1. [Где искать задание на разработку ПО](#place-to-find-assignment)
    1. [Команды для быстрого запуска с помощью make](#make-commands)
    1. [Как обновить local-окружение](#update-local-env)
    1. [Как установить python-пакет в образ с Django](#add-python-package-to-django-image)
    1. [Как запустить линтеры Python](#run-python-linters)
    1. [Как запустить тесты](#run-tests)
    1. [Как писать автотесты](#write-tests)
3. [Как развернуть dev-окружение](#dev-env)

<a name="local-setup"></a>

## Как развернуть local-окружение

### Необходимое ПО

Для запуска ПО вам понадобятся консольный Git, Docker и Docker Compose. Инструкции по их установке ищите на официальных сайтах:

- [Install Docker Desktop](https://www.docker.com/get-started/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

Для тех, кто использует Windows необходимы также программы **git** и **git bash**. В git bash надо добавить ещё команду make:

- Go to [ezwinports](https://sourceforge.net/projects/ezwinports/files/)
- Download make-4.2.1-without-guile-w32-bin.zip (get the version without guile)
- Extract zip
- Copy the contents to C:\ProgramFiles\Git\mingw64\ merging the folders, but do NOT overwrite/replace any exisiting files.

Все дальнейшие команды запускать из-под **git bash**

### Подготовка файла .env

Для локального развертывания приложения необходимо в корне проекта создать файл `.env` со следующими переменными:

```shell
TG__BOT_TOKEN=your_tg_bot_token
```

## Работа с кодом с использованием docker
Склонируйте репозиторий.


В репозитории используются хуки pre-commit, чтобы автоматически запускать линтеры и автотесты. Перед началом разработки установите [pre-commit package manager](https://pre-commit.com/).

В корне репозитория запустите команду для настройки хуков:

```shell
$ pre-commit install
```

В последующем при коммите автоматически будут запускаться линтеры и автотесты. Есть линтеры будет недовольны, или автотесты сломаются, то коммит прервётся с ошибкой.

Сначала скачайте и соберите докер-образы с помощью Docker Сompose:

```shell
$ docker compose pull --ignore-buildable
$ docker compose build
```

Для запуска сайта вам понадобится телеграм-бот. Зарегистрируйте своего отладочного бота в [BotFather](https://t.me/BotFather), получите токен и положите его в файл `.env` в корне проекта:

```sh
# file .env:
TG__BOT_TOKEN="1616161616:AAF01OAAF01OAAF01OAAF01OAAF01O"
```

Запустите докер-контейнеры и не выключайте:

```shell
$ docker compose up
```

Накатить миграции можно с помощью команды:

```shell
$ docker compose run --rm django python manage.py migrate
```

Сайт доступен по адресу [127.0.0.1:8000](http://127.0.0.1:8000). Вход в админку находится по адресу [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/). Вы можете создать суперпользователя командой:

``` shell
docker compose run --rm django python manage.py createsuperuser --no-input
```
После выполнения команды в системе создастся суперпользователь с реквизитами:
- `admin`, пароль `admin123`

Первый запуск автотестов Django может занимать много времени из-за создания тестовой БД. А так как автотесты сами запускаются при коммите, то это может привести к неожиданному "зависанию" git. Проблема случается только при первом запуске. Чтобы не споткнуться на таком лучше сразу запустите автотесты в первый раз, чтобы создать тестовую БД:

```shell
$ docker compose run --rm django pytest ./ .contrib-candidates/
```

Для работы телеграм-бота надо зарегистрировать вебхук на серверах Telegram, а для этого понадобится публичный адрес.
Получить его можно с помощью [https://ngrok.com/](https://ngrok.com/).<br>
Перейдите по ссылке и пройдите регистрацию.
На сайте будут подробные инструкции по установке **ngrok** на вашу операционную систему.<br>

Чтобы получить публичный IP адрес для вашей разработческой машины сначала авторизуйте ngrok с помощью команды
`ngrok config add-authtoken`, как это указано в личном кабинете на сайте [https://ngrok.com/](https://ngrok.com/), а затем запустите
команду:

```shell
$ ngrok http 8000
Session Status                online
Account                       Евгений Евсеев (Plan: Free)
Version                       3.3.1
Region                        Europe (eu)
Latency                       48ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://3b1d-95-70-162-108.ngrok-free.app -> http://127.0.0.1:8000
Connections                   ttl     opn     rt1     rt5     p50     p90
                              19      0       0.00    0.00    0.04    0.10
```

Ngrok сообщит вам публичный адрес и начнём пробрасывать входящий трафик на порт 8000 вашего локального компьютера.
Обратите внимание, что бесплатная версия Ngrok предоставляет временные адреса, которые меняются при каждом запуске `ngrok`. Лучше
не выключайте `ngrok` во время работы с сайтом.

Далее необходимо добавить домен полученного от Ngrok публичного адреса в переменные окружения `DJ__ALLOWED_HOSTS` и
`DJ__CSRF_TRUSTED_ORIGINS`, иначе Django откажется обрабатывать входящие сообщения от серверов Telegram.
Если вы используете бесплатную версию Ngrok, то всё уже настроено заранее и ничего предпринимать не надо. А если у вас
платная версия, то сверьте полученный публичный адрес с указанными в настройках. Если они отличаются, то подмените их с помощью `docker-compose.override.yml`, затем перезапустите сервисы. [Подробнее про override-файл](https://docs.docker.com/compose/extends/#multiple-compose-files).

Теперь осталось сообщить серверу телеграм, о нашем webhook-сервере:

```shell
$ # Замените `https://example.ngrok-free.app` на полученный от ngrok публичный адрес
$ PUBLIC_URL="https://example.ngrok-free.app"
$ # Замените `1613441681:example` на токен вашего телеграм бота
$ TG__BOT_TOKEN="1613441681:example"
$ curl https://api.telegram.org/bot${TG__BOT_TOKEN}/setWebhook
$ curl -F "url=${PUBLIC_URL}/webhook/" https://api.telegram.org/bot${TG__BOT_TOKEN}/setWebhook
{"ok":true,"result":true,"description":"Webhook was set"}
```

<a name="development"></a>
## Как вести разработку

Все файлы из каталога `./src` смонтированы в docker-контейнер, а веб-сервер запущен в режиме live-reload, поэтому изменение кода на компьютере сразу отражается на запущенном в local-окружении сайте. Если веб-сервер "упал", то следует остановить контейнеры и перезапустить команду:

```shell
$ docker compose up
```

<a name="place-to-find-assignment"></a>
### Где искать задание на разработку ПО

ПО в репозитории покрыто yaml-заданиями в формате Product Flow.

В документации описаны истории не только пользователей сайта, но также программистов, сис.админов и других участников разработки ПО.

Файлы с yaml-заданиями лежат в каталоге [product_docs](product_docs).

Полезные внешние ссылки:

- [Product Flow — фреймворк продуктовой разработки](https://github.com/devmanorg/product-flow/)

<a name="make-commands"></a>

### Команды для быстрого запуска с помощью make

Для часто используемых команд Docker Compose подготовлен набор альтернативных коротких команд `make`. Например, чтобы запустить автотесты надо выполнить любую из команд приведённых ниже, но вторая записывает короче, и её легче запомнить:

```shell
$ docker compose run --rm django pytest ./ .contrib-candidates/
```

```shell
$ make test
```

Полный набор доступных команд `make` и их скриптов можно найти в файле [Makefile](Makefile). Тот же список доступных команд можно вывести в консоль через встроенную справку:

```shell
$ make help
Cписок доступных команд:
update                         Обновляет local-окружение: скачивает и пересобирает докер-образы, применяет миграции и создаёт суперпользователя
lint                           Проверяет линтером код в репозитории
lint_file                      Проверяет линтером открытых в редакторе файл
test                           Запускает автотесты
makemigrations                 Создаёт новые файлы миграций Django ORM
migrate                        Применяет новые миграции Django ORM
help                           Отображает список доступных команд и их описания
```

<a name="update-local-env"></a>
### Как обновить local-окружение

Чтобы обновить local-окружение до последней версии подтяните код из центрального окружения и пересоберите докер-образы:

``` shell
$ git pull
$ docker compose pull --ignore-buildable
$ docker compose build
```

После обновлении кода из репозитория стоит также обновить и схему БД. Вместе с коммитом могли прилететь новые миграции схемы БД, и без них код не запустится.

Чтобы не гадать заведётся код или нет — запускайте при каждом обновлении команду `migrate`. Если найдутся свежие миграции, то команда их применит:

```shell
$ docker compose run --rm django ./manage.py migrate
…
Running migrations:
  No migrations to apply.
```

Всё вышеперечисленное можно сделать одной командой `make update`.

<a name="add-python-package-to-django-image"></a>
### Как установить python-пакет в образ с Django

В качестве менеджера пакетов для образа с Django используется [Poetry](https://python-poetry.org/docs/).

Конфигурационные файлы Poetry `pyproject.toml` и `poetry.lock` проброшены в контейнер в виде volume, поэтому изменения зависимостей внутри контейнера попадают и наружу в git-репозиторий.

Вот пример как добавить в зависимости библиотеку asks. Подключитесь к уже работающему контейнеру `django` и внутри запустите команду `poetry add asks`:

```shell
$ docker compose exec django bash
container:$ poetry add asks==3.0.0
```

Конфигурационные файлы `pyproject.toml` и `poetry.lock` обновятся не только внутри контейнера, но и в репозитории благодаря настроенным docker volumes. Осталось только закоммитить изменения.

Чтобы все новые контейнеры также получали свежий набор зависимостей не забудьте обновить докер-образ:

```shell
$ docker compose build django
```

Аналогичным образом можно удалять python-пакеты:

```shell
$ docker compose exec django bash
container:$ poetry remove asks
```

<a name="run-python-linters"></a>
### Как запустить линтеры Python

Линтеры запускаются в отдельном docker-контейнере, а код подключается к нему с помощью volume. Например, чтобы проверить линтером код в каталоге `src` запустите команду:

```shell
$ docker compose run --rm linters flake8 /src/
/src/env_settings.py:33:121: E501 line too long (197 > 120 characters)
1
```
Цифра в конце `1` -- это количество найденных линтером ошибок форматирования кода.

Того же результата можно добиться с помощью альтернативной короткой команды `make lint`.

Тот же образ с линтером можно использовать, чтобы подсветить ошибки форматирования прямо внутри IDE. Вот пример настройки Sublime Text с предустановленными плагинами [SublimeLinter](http://www.sublimelinter.com/en/stable/) и [SublimeLinter-flake8](https://packagecontrol.io/packages/SublimeLinter-flake8):

```jsonc
// project settings file
{
    "settings": {
        // specify folder where docker-compose.yaml file placed to be able to launch `docker compose`
        "SublimeLinter.linters.flake8.working_dir": "/path/to/repo/",
        "SublimeLinter.linters.flake8.executable": ["docker", "compose", "run", "--rm", "linters", "flake8"],
    },
}
```

<a name="run-tests"></a>
### Как запустить тесты

В проекте используются вперемешку и стандартные юнит-тесты Django, и автотесты [pytest](https://docs.pytest.org/). Можно разом запустить их все вместе:

```shell
$ docker compose run --rm django pytest ./ .contrib-candidates/
[+] Building 0.0s (0/0)
[+] Creating 1/0
 ✔ Container postgres-1                                            0.0s
[+] Building 0.0s (0/0)
=========================== test session starts ===========================
platform linux -- Python 3.11.3, pytest-7.3.1, pluggy-1.0.0
cachedir: /pytest_cache_dir
django: settings: project.settings (from env)
rootdir: /opt/app
configfile: pyproject.toml
plugins: anyio-3.7.0, django-4.5.2, httpx-0.22.0
collected 2 items

project/test_tools_for_testing.py ..                        [100%]

=========================== 2 passed in 0.40s ===========================
```

Того же результата можно добиться с помощью альтернативной короткой команды `make test`.

Если вы чините поломанный тест, часто его запускаете и не хотите ждать когда отработают остальные, то можно запускать их по-отдельности. При этом полезно включать опцию `-s`, чтобы pytest не перехватывал вывод в консоль и выводил все сообщения. Пример для теста `test_httpx_mocking` из файла `test_tools_for_testing.py`:

```shell
$ docker compose run --rm django pytest -s test_tools_for_testing.py::test_httpx_mocking
```

Подробнее про [Pytest usage](https://docs.pytest.org/en/6.2.x/usage.html).

<a name="write-tests"></a>
### Как писать автотесты к Django

Примеры автотестов с асинхронным кодом, базой данных, моками запросов к API и прочими сложными ситуациями можно найти в файле [test_tools_for_testing.py](/django/src/test_tools_for_testing.py).

На проекте придерживаемся нескольких правил:

**Не пишем автотесты без надобности**. На этом проекте мы не стремимся к 100% покрытию автотестами. Написание и поддержка автотестов требуют времени и не всегда окупаются. Новые автотесты пишем только в тех случаях, когда с ними решить задачу и отладить код можно быстрее, чем без них.

**Плотное покрытие внизу и тонкое — наверху**. Юнит-тесты тем лучше, чем более низкоуровневый компонент они покрывают. Например, если у вас есть две функции, где первая вызывает вторую, и сложный код прячется во второй, то лучше плотно покрыть автотестами только вторую вложенную функцию, а первую совсем обойти стороной. Низкоуровневые автотесты проще писать, их реже приходится переписывать, чем высокоуровневые — у тех много corner cases, много степеней свободы, и их поведение часто меняется в процессе разработки ПО. Высокоуровневые автотесты сначала будет трудно написать, а затем ещё сложнее их поддерживать в актуальном состоянии.

**Кладём код автотестов рядом с тем кодом, который тестируем**. Код новых автотестов старайтесь раскидать по папкам django-приложений и модулей python. Не пытайтесь собрать все автотесты в одном месте -- так только сложнее будет их поддерживать.


<a name="dev-env"></a>
## Как развернуть dev-окружение

Инструкции по развертыванию и обновлению ПО лежат в отдельном файле README. [Инструкции к окружению `.deploy/dev-naughty-swanson`](.deploy/dev-naughty-swanson/README.md).