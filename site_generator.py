
from html import escape
from urllib.parse import quote

from storage import photo_key


def render_index(albums: list[str]) -> str:
    lines = [
        "<!doctype html>",
        "<html>",
        "<head>",
        "    <title>Фотоархив</title>",
        "</head>",
        "<body>",
        "    <h1>Фотоархив</h1>",
    ]

    if not albums:
        lines.append("    <p>Фотоархив пустой.</p>")
    else:
        lines.append("    <ul>")

        for number, album in enumerate(albums, start=1):
            name = escape(album)
            lines.append(
                f'        <li><a href="album{number}.html">'
                f'{name}</a></li>'
            )

        lines.append("    </ul>")

    lines.extend(["</body>", "</html>"])
    return "\n".join(lines)


def render_album(album: str, photos: list[str]) -> str:
    name = escape(album)

    lines = [
        "<!doctype html>",
        "<html>",
        "<head>",
        f'    <title>Фотоальбом "{name}"</title>',
    ]

    if photos:
        lines.extend([
            '    <link rel="stylesheet" type="text/css" '
            'href="https://cdnjs.cloudflare.com/ajax/libs/'
            'galleria/1.6.1/themes/classic/'
            'galleria.classic.min.css" />',
            "    <style>",
            "        .galleria{ width: 960px; height: 540px; background: #000 }",
            "    </style>",
            '    <script src="https://ajax.googleapis.com/'
            'ajax/libs/jquery/3.6.0/jquery.min.js"></script>',
            '    <script src="https://cdnjs.cloudflare.com/'
            'ajax/libs/galleria/1.6.1/galleria.min.js"></script>',
            '    <script src="https://cdnjs.cloudflare.com/'
            'ajax/libs/galleria/1.6.1/themes/classic/'
            'galleria.classic.min.js"></script>',
        ])

    lines.extend([
        "</head>",
        "<body>",
        f'    <h1>Фотоальбом "{name}"</h1>',
    ])

    if not photos:
        lines.append("    <p>Фотоальбом пустой.</p>")
    else:
        lines.append('    <div class="galleria">')

        for filename in photos:
            url = quote(photo_key(album, filename), safe="/")
            title = escape(filename, quote=True)

            lines.append(
                f'        <img src="{escape(url, quote=True)}" '
                f'data-title="{title}">'
            )

        lines.append("    </div>")

    lines.append(
        '    <p>Вернуться на <a href="index.html">'
        'главную страницу</a> фотоархива</p>'
    )

    if photos:
        lines.extend([
            "    <script>",
            "        (function() {",
            "            Galleria.run('.galleria');",
            "        }());",
            "    </script>",
        ])

    lines.extend(["</body>", "</html>"])
    return "\n".join(lines)


def render_error() -> str:
    return """<!doctype html>
<html>
<head>
    <title>Фотоархив</title>
</head>
<body>
    <h1>Ошибка</h1>
    <p>Ошибка при доступе к фотоархиву. Вернитесь на <a href="index.html">главную страницу</a> фотоархива.</p>
</body>
</html>"""
