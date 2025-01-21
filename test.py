import time
import subprocess
import tempfile
import os
import sys

import asyncio
import functools

import prompt_toolkit
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.patch_stdout import patch_stdout

import pygments
from pygments.filter import Filter
from pygments.lexer import Lexer
from pygments.lexers.data import JsonLdLexer
from prompt_toolkit.formatted_text import FormattedText, PygmentsTokens


def handle_output(*output, source: str = None, **kwargs):
    end = "" if source else "\n"
    if source == "stderr":
        color = "fg:ansired"
    elif not source:
        color = self.color or "fg:ansiblue"
    else:
        color = None
    log_msg(*output, color=color, prefix=source, end=end, **kwargs)


def log_msg(*msg, color="fg:ansimagenta", **kwargs):
    print(*msg)


async def main(loop: asyncio.AbstractEventLoop):
    tempfile1 = tempfile.NamedTemporaryFile(mode='w+', encoding="utf-8", buffering=-1)
    tempfile2 = tempfile.NamedTemporaryFile(mode='w+', encoding="utf-8", buffering=-1)
    args = ["python", "echo.py"]
    proc = subprocess.Popen(
        args,
        env=os.environ.copy(),
        stdout=tempfile1,
        stderr=tempfile2,
        encoding="utf-8",
        preexec_fn=os.setsid,
    )

    stdout = loop.run_in_executor(
        None,
        tmpfile_output_reader,
        proc,
        tempfile1,
        functools.partial(handle_output, source="stdout"),
    )


def tmpfile_output_reader(proc, handle, callback, *args, **kwargs):
    # proc.poll returns None until the subprocess ends,
    # it will then return the exit code, hopefully 0 ;)
    handle.seek(0)
    while proc.poll() is None:
        where = handle.tell()
        lines = handle.read()
        if not lines:
            # Adjust the sleep interval to your needs
            time.sleep(0.1)
            handle.seek(where)
        else:
            callback(lines, *args)
    lines = handle.read()
    callback(lines, *args)

    # It's done
    print("Process ended, ret code:", p.returncode)


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            main(loop)
        )
    except KeyboardInterrupt:
        os._exit(1)
