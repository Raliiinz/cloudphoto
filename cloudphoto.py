
import argparse
import os
import sys

from botocore.exceptions import BotoCoreError, ClientError
from storage import PhotoStorage
from boto3.exceptions import S3UploadFailedError


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

        for field in ("album", "photo"):
            value = getattr(args, field, None)

            if value is not None and (
                not value or "/" in value
            ):
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

        # Остальные команды реализуем позднее.
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
