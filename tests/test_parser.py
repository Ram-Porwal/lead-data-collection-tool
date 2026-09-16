from lead_collector.extraction.parser import HTMLParser


def test_parse_extracts_title_and_description():
    html = """
    <html>
        <head>
            <title>Example Company</title>
            <meta
                name="description"
                content="A software company."
            >
        </head>
        <body>
            <p>We build useful software.</p>
        </body>
    </html>
    """

    result = HTMLParser().parse(html)

    assert result.title == "Example Company"
    assert result.description == "A software company."


def test_parse_extracts_clean_visible_text():
    html = """
    <html>
        <head>
            <style>.hidden { display: none; }</style>
            <script>alert("test");</script>
        </head>
        <body>
            <h1>Example Company</h1>
            <p>We build software.</p>
        </body>
    </html>
    """

    result = HTMLParser().parse(html)

    assert "Example Company" in result.text
    assert "We build software." in result.text
    assert "alert" not in result.text
    assert "display: none" not in result.text


def test_parse_extracts_links():
    html = """
    <html>
        <body>
            <a href="/about">About</a>
            <a href="https://example.com/contact">Contact</a>
        </body>
    </html>
    """

    result = HTMLParser().parse(
        html,
        base_url="https://example.com",
    )

    assert result.links == [
        "https://example.com/about",
        "https://example.com/contact",
    ]


def test_parse_handles_missing_title_and_description():
    html = """
    <html>
        <body>
            <p>Hello world.</p>
        </body>
    </html>
    """

    result = HTMLParser().parse(html)

    assert result.title is None
    assert result.description is None
    assert result.text == "Hello world."
    assert result.links == []


def test_parse_skips_empty_links():
    html = """
    <html>
        <body>
            <a href="">Empty</a>
            <a href="  ">Whitespace</a>
            <a href="/valid">Valid</a>
        </body>
    </html>
    """

    result = HTMLParser().parse(
        html,
        base_url="https://example.com",
    )

    assert result.links == [
        "https://example.com/valid",
    ]