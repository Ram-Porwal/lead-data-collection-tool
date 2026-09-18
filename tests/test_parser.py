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

    assert result.site_name is None
    assert result.canonical_url is None
    assert result.organization_name is None


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


def test_parse_extracts_open_graph_site_name():
    html = """
    <html>
        <head>
            <meta
                property="og:site_name"
                content="Talentica"
            >
        </head>
        <body>
            <p>Software engineering company.</p>
        </body>
    </html>
    """

    result = HTMLParser().parse(html)

    assert result.site_name == "Talentica"


def test_parse_extracts_canonical_url():
    html = """
    <html>
        <head>
            <link
                rel="canonical"
                href="https://www.talentica.com/"
            >
        </head>
        <body>
            <p>Talentica</p>
        </body>
    </html>
    """

    result = HTMLParser().parse(
        html,
        base_url="https://example.com",
    )

    assert result.canonical_url == "https://www.talentica.com/"


def test_parse_extracts_organization_name_from_json_ld():
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Talentica"
            }
            </script>
        </head>
        <body>
            <p>Software engineering company.</p>
        </body>
    </html>
    """

    result = HTMLParser().parse(html)

    assert result.organization_name == "Talentica"


def test_parse_extracts_organization_metadata():
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Example Technologies",
                "industry": "Software",
                "email": "sales@example.com",
                "telephone": "+91 98765 43210",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "Ahmedabad",
                    "addressRegion": "Gujarat",
                    "addressCountry": "India"
                }
            }
            </script>
        </head>
        <body>
            Example Technologies
        </body>
    </html>
    """

    page = HTMLParser().parse(
        html,
        base_url="https://example.com",
    )

    assert page.organization_name == "Example Technologies"
    assert page.organization_industry == "Software"
    assert page.organization_email == "sales@example.com"
    assert page.organization_telephone == "+91 98765 43210"
    assert page.organization_city == "Ahmedabad"
    assert page.organization_state == "Gujarat"
    assert page.organization_country == "India"


def test_parse_handles_nested_address_country():
    html = """
    <script type="application/ld+json">
    {
        "@type": "Organization",
        "name": "Example Technologies",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Ahmedabad",
            "addressRegion": "Gujarat",
            "addressCountry": {
                "@type": "Country",
                "name": "India"
            }
        }
    }
    </script>
    """

    page = HTMLParser().parse(html)

    assert page.organization_name == "Example Technologies"
    assert page.organization_city == "Ahmedabad"
    assert page.organization_state == "Gujarat"
    assert page.organization_country == "India"


def test_parse_ignores_malformed_organization_json():
    html = """
    <script type="application/ld+json">
    {"@type": "Organization", "name":
    </script>

    <title>Example Company</title>
    """

    page = HTMLParser().parse(html)

    assert page.organization_name is None
    assert page.organization_industry is None
    assert page.organization_email is None