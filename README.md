
# Фотоархив CloudPhoto

`cloudphoto` — консольное приложение для управления фотоальбомами в Yandex Object Storage и публикации статического сайта.

Сайт: https://photos.vvot02.itiscl.ru/

## Установка

Программа написана на Python 3.10+ и поддерживает Linux x86_64.

```bash
git clone https://github.com/Raliiinz/cloudphoto.git
cd cloudphoto

python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

После установки программа доступна как `cloudphoto`.

## Настройка

Для подключения к Yandex Object Storage используются переменные окружения:

| Переменная | Назначение |
|---|---|
| `BUCKET` | Имя бакета |
| `AWS_ACCESS_KEY_ID` | Идентификатор статического ключа |
| `AWS_SECRET_ACCESS_KEY` | Секретная часть ключа |

Пример настройки:

```bash
export BUCKET="photos.vvot02.itiscl.ru"
export AWS_ACCESS_KEY_ID="<access_key>"
export AWS_SECRET_ACCESS_KEY="<secret_key>"
```

Регион `ru-central1` и endpoint `https://storage.yandexcloud.net` заданы в коде. Конфигурационный файл не используется.

## Команды

```bash
cloudphoto list
cloudphoto list --album "Отпуск"

cloudphoto upload --album "Отпуск" --path ./photos
cloudphoto download --album "Отпуск" --path ./downloads

cloudphoto delete --album "Отпуск" --photo "Море.jpg"
cloudphoto delete --album "Отпуск"

cloudphoto mksite
```

Без `--path` используется текущий каталог. Поддерживаются фотографии `.jpg` и `.jpeg` без учёта регистра расширения. При повторной загрузке или скачивании файлы с одинаковыми именами заменяются.

После изменения фотографий или альбомов необходимо повторно выполнить `mksite` для обновления сайта.

## Организация хранилища

Объекты в бакете хранятся по следующей схеме:

```text
albums/
  <album_utf8_hex>/
    __album__
    photos/
      <filename_utf8_hex>

index.html
error.html
album1.html ... albumN.html
```

Имена альбомов и фотографий преобразуются в шестнадцатеричное представление UTF-8 (hex).

**Обоснование схемы:**

- Hex-кодирование позволяет однозначно восстановить исходные имена, сохраняя кириллицу, пробелы и регистр символов.
- Объект `__album__` обозначает существование альбома, в том числе пустого.
- Фотографии разных альбомов имеют разные префиксы, поэтому одинаковые имена файлов не конфликтуют.
- HTML-страницы находятся отдельно от фотографий и служебных объектов альбомов.

Списки альбомов и фотографий сортируются по байтам UTF-8 с учётом регистра.

## Публикация сайта

Команда `mksite` создаёт главную страницу `index.html`, страницы альбомов `albumN.html` и страницу ошибки `error.html`.

Для просмотра фотографий используется Galleria 1.6.1. Команда также настраивает статический хостинг и публичный доступ на чтение объектов.

## Инфраструктура

Terraform-конфигурация находится в `infrastructure/`. Она создаёт бакет, сервисный аккаунт со статическим ключом, DNS-запись и привязку HTTPS-сертификата.

Для Terraform необходима переменная окружения `YC_TOKEN`. Конфигурация принимает `folder_id`, `bucket_name`, `domain`, `cert_id` и `dns_zone_id`.

Развёртывание:

```bash
terraform -chdir=infrastructure init
terraform -chdir=infrastructure plan
terraform -chdir=infrastructure apply
```

DNS-зона и сертификат Let's Encrypt создаются в предварительных заданиях.

## Тестирование

```bash
python -m unittest discover -s tests -v
```

Установка и запуск CLI проверены в Linux x86_64 через Docker.
