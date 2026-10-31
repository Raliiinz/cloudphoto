
import argparse
import os
import sys


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

        # Реализацию команд добавим позже
        raise RuntimeError(
            f"Команда {args.command} пока не реализована"
        )

    except (ValueError, RuntimeError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
