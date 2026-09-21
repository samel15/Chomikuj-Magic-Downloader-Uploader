#!/usr/bin/env python3

import re

LOCAL_EXTENSION_RE = re.compile(r"\.[A-Za-z0-9]+$")
LOCAL_FORBIDDEN_CHARS = set('<>:"/\\|?*')
LOCAL_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def encode_local_component(name, allow_extension=False):
    text = str(name or "")
    extension = ""
    if allow_extension:
        match = LOCAL_EXTENSION_RE.search(text)
        if match and 0 < match.start() < len(text) - 1:
            text, extension = text[: match.start()], match.group(0)

    encoded = []
    for index, char in enumerate(text):
        if _is_safe_char(char) and not _is_unsafe_edge_char(char, index, len(text)):
            encoded.append(char)
        else:
            encoded.extend(_encode_char(char))
    encoded_text = "".join(encoded) or "_"

    if _is_reserved_windows_name(encoded_text):
        first_char, rest = encoded_text[0], encoded_text[1:]
        encoded_text = "".join(_encode_char(first_char)) + rest

    return encoded_text + extension


def _is_safe_char(char):
    return ord(char) >= 32 and char not in LOCAL_FORBIDDEN_CHARS and char != "~"


def _is_unsafe_edge_char(char, index, length):
    return char in " ." and (index == 0 or index == length - 1)


def _is_reserved_windows_name(text):
    device_name = text.split(".", 1)[0]
    return device_name.upper() in LOCAL_RESERVED_NAMES


def _encode_char(char):
    return [f"~{byte:02x}" for byte in char.encode("utf-8")]
