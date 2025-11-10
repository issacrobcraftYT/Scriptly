APP_NAME = "Scriptly"
AUTHOR = "MoonIsaa"
VERSION = "0.2.0"
LICENSE = "MIT License"
COPYRIGHT_YEAR = 2025
HOMEPAGE = "not created"

METADATA = {
    "name": APP_NAME,
    "author": AUTHOR,
    "version": VERSION,
    "license": LICENSE,
    "year": COPYRIGHT_YEAR,
    "homepage": HOMEPAGE,
}

def get_version(prepend_v=False):
    return f"v{VERSION}" if prepend_v else VERSION
