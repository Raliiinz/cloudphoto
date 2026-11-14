
import argparse
import os
import sys

from botocore.exceptions import BotoCoreError, ClientError
from storage import PhotoStorage
from boto3.exceptions import S3UploadFailedError

from site_generator import render_index, render_album, render_error


REQUIRED_ENV_VARS = (
    "BUCKET",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
)


class CloudPhotoParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError("Ошибка в аргументах")


def check_environment():
    for name in REQUIRED_ENV_VARS:
        if not os.environ.get(name):
            raise RuntimeError("Не заданы переменные окружения")


def create_parser():
    parser = CloudPhotoParser(prog="cloudphoto")

    commands = parser.add_subparsers(
        dest="command",
        required=True,
        parser_class=CloudPhotoParser,
    )

    list_cmd = commands.add_parser("list")
    list_cmd.add_argument("--album")

    upload_cmd = commands.add_parser("upload")
    upload_cmd.add_argument("--album", required=True)
    upload_cmd.add_argument("--path", default=".")

    download_cmd = commands.add_parser("download")
    download_cmd.add_argument("--album", required=True)
    download_cmd.add_argument("--path", default=".")

    delete_cmd = commands.add_parser("delete")
    delete_cmd.add_argument("--album", required=True)
    delete_cmd.add_argument("--photo")

    commands.add_parser("mksite")

    return parser


def main():
    try:
        check_environment()

        args = create_parser().parse_args()

        for field in ("album", "photo", "path"):
            value = getattr(args, field, None)

            if value is not None:
                if not value:
                    raise ValueError("Ошибка в аргументах")

                if field in ("album", "photo") and "/" in value:
                    raise ValueError("Ошибка в аргументах")

        if args.command == "list":
            storage = PhotoStorage()

            if args.album is None:
                items = storage.list_albums()
            else:
                items = storage.list_photos(args.album)

            for item in items:
                print(item)

            return 0
        
        if args.command == "upload":
            storage = PhotoStorage()

            count = storage.upload_photos(
                album=args.album,
                directory=args.path,
            )

            print(
                f"Загружено фотографий: {count}"
            )

            return 0

        if args.command == "download":
            storage = PhotoStorage()

            count = storage.download_photos(
                album=args.album,
                directory=args.path,
            )

            print(f"Скачано фотографий: {count}")

            return 0
        
        if args.command == "delete":
            storage = PhotoStorage()

            if args.photo is not None:
                storage.delete_photo(
                    album=args.album,
                    filename=args.photo,
                )
                print(f"Удалена фотография: {args.photo}")

            else:
                storage.delete_album(
                    album=args.album,
                )
                print(f"Удалён альбом: {args.album}")

            return 0

        if args.command == "mksite":
            storage = PhotoStorage()

            albums = storage.list_albums()

            for number, album in enumerate(albums, start=1):
                photos = storage.list_photos(album)

                html = render_album(album, photos)

                storage.upload_html(
                    key=f"album{number}.html",
                    html=html,
                )

            storage.upload_html(
                key="index.html",
                html=render_index(albums),
            )

            storage.upload_html(
                key="error.html",
                html=render_error(),
            )

            storage.delete_obsolete_album_pages(len(albums))
            storage.configure_website()

            print(
                f"Сайт опубликован. Альбомов: {len(albums)}"
            )

            return 0

        raise RuntimeError(
            f"Команда {args.command} пока не реализована"
        )

    except (
        ValueError,
        RuntimeError,
        OSError,
        ClientError,
        BotoCoreError,
        S3UploadFailedError,
    ) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
