#!/usr/bin/env python3
"""
The class definition for check some marks in the text.
"""

import re

url_pattern = 'http[s]?://\S+'  # noqa: W605
# NOTE: 正規表現を記載しておりこれをprintするわけではないのでエスケープシークエンスのエラーは無視する.


class WordMarks:
    """
    Define text split marks and split functions.
    """

    def __init__(self) -> None:
        """
        Define text split marks.

        NOTE: RUF001 was ignored, assuming it may contain similar characters in Unicode.
        """
        self.punctuation_marks = ['，', '．', '、', '。', ',', '.']  # noqa: RUF001
        self.exclamation_marks = ['!', '！']  # noqa: RUF001
        self.question_marks = ['?', '？']  # noqa: RUF001
        self.new_line_marks = ['\n', '\r']
        # NOTE: Japanese sentence, so use Full-width letter.
        return

    def split_text(self, text: str) -> list[str]:
        """
        Split the input text based on punctuation and new line marks.

        Args:
            text (str): The input text to be split.

        Returns:
            List[str]: A list of split text segments.
        """
        is_append = False
        split_text = []
        txt = ''
        for letter in text:
            is_sp, _, _, _, _ = self.check_letter(letter)
            if not is_sp and is_append and len(txt) > 0:
                split_text.append(txt)
                txt = ''
                is_append = False

            txt = txt + letter
            if is_sp:
                is_append = True

        if len(txt) > 0:
            split_text.append(txt)

        return split_text

    def split_text_for_voice(self, text: str) -> list[str]:
        """
        Split the input text for voice processing, ignoring new line marks.

        Args:
            text (str): The input text to be split.

        Returns:
            List[str]: A list of split text segments suitable for voice processing.
        """
        is_append = False
        split_text = []
        txt = ''
        for letter in text:
            is_sp, _, _, _, is_n = self.check_letter(letter)
            if not is_sp and is_append and len(txt) > 0:
                split_text.append(txt)
                txt = ''
                is_append = False

            if not is_n:
                txt = txt + letter

            if is_sp:
                is_append = True

        if len(txt) > 0:
            split_text.append(txt)

        return split_text

    def check_letter(self, letter: str) -> tuple[bool, bool, bool, bool, bool]:
        """
        Check the type of the input letter.

        Args:
            letter (str): The input letter to be checked.

        Returns:
            Tuple[bool, bool, bool, bool, bool]: A tuple containing boolean values indicating
            if the letter is a split mark, punctuation, exclamation, question, or new line mark.
        """
        is_p = letter in self.punctuation_marks
        is_e = letter in self.exclamation_marks
        is_q = letter in self.question_marks
        is_n = letter in self.new_line_marks
        is_sp = is_p or is_e or is_q or is_n
        return is_sp, is_p, is_e, is_q, is_n


def url2alternative_text(text: str, alternative_text: str = 'URL') -> str:
    """
    文章中のURLを代替テキストに変換する.

    Args:
        text (str): 変換対象の文章
        alternative_text (str): 代替テキスト
            Defaults; 'URL'

    Returns:
        str: URL部分を代替テキストに変換した文章
    """
    url_list = re.findall(url_pattern, text)
    for url in url_list:
        text = text.replace(url, alternative_text)

    return text
