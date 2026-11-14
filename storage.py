
import os

import boto3
from botocore.exceptions import ClientError
from pathlib import Path
import re
import tempfile

ENDPOINT_URL = "https://storage.yandexcloud.net"
REGION = "ru-central1"

ALBUMS_PREFIX = "albums/"
ALBUM_MARKER = "__album__"


def encode_name(name: str) -> str:
    return name.encode("utf-8").hex()


def decode_name(encoded: str) -> str:
    return bytes.fromhex(encoded).decode("utf-8")


def album_prefix(album: str) -> str:
    return f"{ALBUMS_PREFIX}{encode_name(album)}/"


def album_marker_key(album: str) -> str:
    return f"{album_prefix(album)}{ALBUM_MARKER}"


def photos_prefix(album: str) -> str:
    return f"{album_prefix(album)}photos/"


def photo_key(album: str, filename: str) -> str:
    return f"{photos_prefix(album)}{encode_name(filename)}"


def utf8_sort(values):
    return sorted(values, key=lambda value: value.encode("utf-8"))


class PhotoStorage:
    def __init__(self):
        self.bucket = os.environ["BUCKET"]

        self.client = boto3.client(
            "s3",
            endpoint_url=ENDPOINT_URL,
            region_name=REGION,
        )

    def list_keys(self, prefix: str):
        paginator = self.client.get_paginator("list_objects_v2")

        for page in paginator.paginate(
            Bucket=self.bucket,
            Prefix=prefix,
        ):
            for obj in page.get("Contents", []):
                yield obj["Key"]

    def album_exists(self, album: str) -> bool:
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=album_marker_key(album),
            )
            return True

        except ClientError as error:
            status = error.response["ResponseMetadata"][
                "HTTPStatusCode"
            ]

            if status == 404:
                return False

            raise

    def list_albums(self):
        albums = set()

        for key in self.list_keys(ALBUMS_PREFIX):
            parts = key.split("/")

            if (
                len(parts) != 3
                or parts[0] != "albums"
                or parts[2] != ALBUM_MARKER
            ):
                continue

            try:
                encoded = parts[1]
                name = decode_name(encoded)

                if name and encode_name(name) == encoded:
                    albums.add(name)

            except (ValueError, UnicodeError):
                continue

        return utf8_sort(albums)

    def list_photos(self, album: str):
        if not self.album_exists(album):
            raise ValueError(
                f"В фотоархиве нет альбома с именем {album}"
            )

        prefix = photos_prefix(album)
        photos = []

        for key in self.list_keys(prefix):
            encoded = key[len(prefix):]

            try:
                filename = decode_name(encoded)

                if (
                    encode_name(filename) == encoded
                    and filename.lower().endswith(
                        (".jpg", ".jpeg")
                    )
                ):
                    photos.append(filename)

            except (ValueError, UnicodeError):
                continue

        return utf8_sort(photos)

    
    def upload_photos(self, album: str, directory: str):
        path = Path(directory)

        if not path.is_dir():
            raise ValueError(
                f"Каталог не существует или недоступен: {directory}"
            )

        photos = [
            file
            for file in path.iterdir()
            if file.is_file()
            and file.name.lower().endswith((".jpg", ".jpeg"))
        ]

        if not photos:
            raise ValueError("В каталоге нет фотографий")

        photos.sort(key=lambda file: file.name.encode("utf-8"))

        if not self.album_exists(album):
            self.client.put_object(
                Bucket=self.bucket,
                Key=album_marker_key(album),
                Body=b"",
            )

        for file in photos:
            key = photo_key(album, file.name)

            self.client.upload_file(
                Filename=str(file),
                Bucket=self.bucket,
                Key=key,
                ExtraArgs={"ContentType": "image/jpeg"},
            )

        return len(photos)

    
    def download_photos(self, album: str, directory: str):
        path = Path(directory)

        if not path.is_dir():
            raise ValueError(
                f"Каталог не существует или недоступен: {directory}"
            )

        try:
            with tempfile.TemporaryFile(dir=path):
                pass
        except OSError as error:
            raise ValueError(
                f"Каталог недоступен для записи: {directory}"
            ) from error

        photos = self.list_photos(album)

        for filename in photos:
            key = photo_key(album, filename)
            destination = path / filename

            self.client.download_file(
                Bucket=self.bucket,
                Key=key,
                Filename=str(destination),
            )

        return len(photos)
    
    def delete_photo(self, album: str, filename: str):
        photos = self.list_photos(album)

        if filename not in photos:
            raise ValueError(
                f"В альбоме {album} нет фотографии {filename}"
            )

        self.client.delete_object(
            Bucket=self.bucket,
            Key=photo_key(album, filename),
        )

    def delete_album(self, album: str):
        if not self.album_exists(album):
            raise ValueError(
                f"В фотоархиве нет альбома с именем {album}"
            )

        keys = list(self.list_keys(album_prefix(album)))
        marker = album_marker_key(album)

        for key in keys:
            if key != marker:
                self.client.delete_object(
                    Bucket=self.bucket,
                    Key=key,
                )

        self.client.delete_object(
            Bucket=self.bucket,
            Key=marker,
        )
    
    def upload_html(self, key: str, html: str):
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=html.encode("utf-8"),
            ContentType="text/html; charset=utf-8",
        )

    def configure_website(self):
        self.client.put_bucket_website(
            Bucket=self.bucket,
            WebsiteConfiguration={
                "IndexDocument": {
                    "Suffix": "index.html"
                },
                "ErrorDocument": {
                    "Key": "error.html"
                },
            },
        )

        self.client.put_bucket_acl(
            Bucket=self.bucket,
            ACL="public-read",
        )


    def delete_obsolete_album_pages(self, album_count: int):
        for key in self.list_keys("album"):
            match = re.fullmatch(
                r"album([1-9][0-9]*)\.html",
                key,
            )

            if match is None:
                continue

            page_number = int(match.group(1))

            if page_number > album_count:
                self.client.delete_object(
                    Bucket=self.bucket,
                    Key=key,
                )
