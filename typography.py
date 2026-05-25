import math
import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class TextToken:
    text: str
    kind: str
    style: str = "normal"


class TypographyMetrics:
    """Heuristic text metrics shared by layout estimation and rendering."""

    STYLE_MULTIPLIERS = {
        "normal": 1.0,
        "bold": 1.08,
        "large_bold": 1.18,
    }

    OPEN_CJK_PUNCT = "《〈（【「『“‘"
    CLOSE_CJK_PUNCT = "》〉）】」』”’"

    def __init__(self, char_width_mm):
        self.char_width_mm = char_width_mm

    def char_width_mm_for_style(self, char, style="normal"):
        width_type = unicodedata.east_asian_width(char)

        if width_type in ("W", "F", "A"):
            width = self.char_width_mm
        elif char.isspace():
            width = self.char_width_mm * 0.34
        elif char in ".,:;!|'`":
            width = self.char_width_mm * 0.28
        elif char in "-/()[]{}":
            width = self.char_width_mm * 0.40
        elif char.isupper():
            width = self.char_width_mm * 0.66
        elif char.isdigit():
            width = self.char_width_mm * 0.54
        else:
            width = self.char_width_mm * 0.50

        return width * self.STYLE_MULTIPLIERS.get(style, 1.0)

    def measure_text_mm(self, text, style="normal"):
        return sum(self.char_width_mm_for_style(char, style) for char in text)

    def tokenize(self, text, style="normal"):
        tokens = []
        index = 0

        while index < len(text):
            char = text[index]

            if char.isspace():
                start = index
                while index < len(text) and text[index].isspace():
                    index += 1
                tokens.append(TextToken(text[start:index], "space", style))
                continue

            if char.isascii() and char.isalnum():
                start = index
                index += 1
                while index < len(text):
                    current = text[index]
                    next_char = text[index + 1] if index + 1 < len(text) else ""
                    if current.isascii() and current.isalnum():
                        index += 1
                    elif current in "+#._" and next_char and next_char.isascii() and next_char.isalnum():
                        index += 1
                    elif current in "-/" and next_char and next_char.isascii() and next_char.isalnum():
                        index += 1
                    else:
                        break
                tokens.append(TextToken(text[start:index], "word", style))
                continue

            width_type = unicodedata.east_asian_width(char)
            kind = "cjk" if width_type in ("W", "F", "A") else "punct"
            tokens.append(TextToken(char, kind, style))
            index += 1

        return tokens

    def markdown_style_runs(self, text):
        runs = []
        cursor = 0
        pattern = re.compile(r"\*\*(.*?)\*\*")

        for match in pattern.finditer(text):
            if match.start() > cursor:
                runs.append((text[cursor:match.start()], "normal"))
            runs.append((match.group(1), "bold"))
            cursor = match.end()

        if cursor < len(text):
            runs.append((text[cursor:], "normal"))

        return runs

    def markdown_tokens(self, text):
        tokens = []
        for run_text, style in self.markdown_style_runs(text):
            tokens.extend(self.tokenize(run_text, style))
        return tokens

    def split_text_by_width(self, text, max_width_mm, style="normal"):
        tokens = self.tokenize(text, style)
        return self._split_tokens_by_width(tokens, max_width_mm, style)

    def truncate_text_by_width(self, text, max_width_mm, style="normal"):
        if self.measure_text_mm(text, style) <= max_width_mm:
            return text

        suffix = "..."
        head, _ = self.split_text_by_width(
            text,
            max(0.0, max_width_mm - self.measure_text_mm(suffix, style)),
            style,
        )
        if not head:
            head, _ = self._hard_split_token(text, max_width_mm, style)
        return head.rstrip() + suffix

    def estimate_lines(self, text, width_mm, markdown_bold=True):
        tokens = self.markdown_tokens(text) if markdown_bold else self.tokenize(text)
        if not tokens:
            return 1

        lines = 1
        current_width = 0.0

        for token in tokens:
            token_width = self.measure_text_mm(token.text, token.style)

            if token.kind == "space":
                if current_width == 0:
                    continue
                if current_width + token_width <= width_mm:
                    current_width += token_width
                continue

            if current_width + token_width <= width_mm:
                current_width += token_width
                continue

            if current_width > 0:
                lines += 1
                current_width = 0.0

            if token_width <= width_mm:
                current_width = token_width
            else:
                overflow_lines = max(1, math.ceil(token_width / width_mm))
                lines += overflow_lines - 1
                current_width = token_width % width_mm

        return lines

    def protect_visible_cjk_spaces(self, text):
        opening = re.escape(self.OPEN_CJK_PUNCT)
        closing = re.escape(self.CLOSE_CJK_PUNCT)

        text = re.sub(
            rf"([{opening}])( +)(?=[A-Za-z0-9])",
            lambda match: match.group(1) + ("~" * len(match.group(2))),
            text,
        )
        text = re.sub(
            rf"(?<=[A-Za-z0-9])( +)([{closing}])",
            lambda match: ("~" * len(match.group(1))) + match.group(2),
            text,
        )
        return text

    def _split_tokens_by_width(self, tokens, max_width_mm, style):
        current_width = 0.0
        head_tokens = []
        last_space_index = None

        for index, token in enumerate(tokens):
            token_width = self.measure_text_mm(token.text, token.style)

            if current_width + token_width > max_width_mm:
                if last_space_index is not None and last_space_index > 0:
                    head = "".join(token.text for token in head_tokens[:last_space_index]).rstrip()
                    tail_tokens = head_tokens[last_space_index:] + tokens[index:]
                    tail = "".join(token.text for token in tail_tokens).lstrip()
                    return head, tail

                if token.kind == "word" and token_width > max_width_mm:
                    hard_head, hard_tail = self._hard_split_token(token.text, max_width_mm, token.style)
                    tail = hard_tail + "".join(token.text for token in tokens[index + 1:])
                    return hard_head.rstrip(), tail.lstrip()

                if head_tokens:
                    head = "".join(token.text for token in head_tokens).rstrip()
                    tail = "".join(token.text for token in tokens[index:]).lstrip()
                    return head, tail

                hard_head, hard_tail = self._hard_split_token(token.text, max_width_mm, token.style)
                tail = hard_tail + "".join(token.text for token in tokens[index + 1:])
                return hard_head.rstrip(), tail.lstrip()

            head_tokens.append(token)
            current_width += token_width

            if token.kind == "space":
                last_space_index = len(head_tokens)

        return "".join(token.text for token in head_tokens).rstrip(), ""

    def _hard_split_token(self, text, max_width_mm, style):
        current_width = 0.0
        chars = []

        for index, char in enumerate(text):
            char_width = self.char_width_mm_for_style(char, style)
            if current_width + char_width > max_width_mm:
                return "".join(chars), text[index:]
            chars.append(char)
            current_width += char_width

        return "".join(chars), ""
