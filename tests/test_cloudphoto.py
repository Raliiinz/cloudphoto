
import io
import os
import sys
import tempfile
import unittest

from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import Mock, patch

from cloudphoto import main
from storage import PhotoStorage, utf8_sort
from site_generator import render_index, render_album


class CloudPhotoTests(unittest.TestCase):

    def test_utf8_sort(self):
        names = ["я", "A", "Я", "a"]

        result = utf8_sort(names)

        self.assertEqual(
            result,
            sorted(names, key=lambda name: name.encode("utf-8")),
        )

    def test_html_escaping(self):
        html = render_index(['Море & пляж'])

        self.assertIn("Море &amp; пляж", html)

    def test_album_html_escaping(self):
        html = render_album(
            'Отпуск & отдых',
            ['Море "лето".jpg'],
        )

        self.assertIn(
            'data-title="Море &quot;лето&quot;.jpg"',
            html,
        )
        self.assertIn("Отпуск &amp; отдых", html)

    def test_upload_accepts_uppercase_extension(self):
        with tempfile.TemporaryDirectory() as directory:
            photo = Path(directory) / "PHOTO.JPG"
            photo.write_bytes(b"test image")

            storage = PhotoStorage.__new__(PhotoStorage)
            storage.bucket = "test-bucket"
            storage.client = Mock()
            storage.album_exists = Mock(return_value=False)

            count = storage.upload_photos("Отпуск", directory)

            self.assertEqual(count, 1)
            storage.client.upload_file.assert_called_once()

    def test_upload_accepts_dot_jpg_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            photo = Path(directory) / ".jpg"
            photo.write_bytes(b"test image")

            storage = PhotoStorage.__new__(PhotoStorage)
            storage.bucket = "test-bucket"
            storage.client = Mock()
            storage.album_exists = Mock(return_value=False)

            count = storage.upload_photos("Отпуск", directory)

            self.assertEqual(count, 1)

    def test_download_rejects_unwritable_directory(self):
        storage = PhotoStorage.__new__(PhotoStorage)
        storage.list_photos = Mock(return_value=[])

        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "storage.tempfile.TemporaryFile",
                side_effect=PermissionError("Access denied"),
            ):
                with self.assertRaises(ValueError):
                    storage.download_photos("Отпуск", directory)

    def test_empty_path_is_invalid(self):
        env = {
            "BUCKET": "test-bucket",
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",
        }

        argv = [
            "cloudphoto",
            "upload",
            "--album",
            "Отпуск",
            "--path",
            "",
        ]

        with (
            patch.dict(os.environ, env),
            patch.object(sys, "argv", argv),
            redirect_stderr(io.StringIO()) as stderr,
        ):
            result = main()

        self.assertEqual(result, 1)
        self.assertIn(
            "Ошибка в аргументах",
            stderr.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
