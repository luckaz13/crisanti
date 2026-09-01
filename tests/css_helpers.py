import re


def css_rule(css: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]+)\}}", css)
    if match is None:
        raise AssertionError(f"missing CSS selector: {selector}")
    return match.group(1)
