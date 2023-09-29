import codecs
import os
import shutil
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest import TestCase

from aider import models
from aider.coders import Coder
from aider.commands import Commands
from aider.dump import dump  # noqa: F401
from aider.io import InputOutput


class TestCommands(TestCase):
    def setUp(self):
        self.original_cwd = os.getcwd()
        self.tempdir = tempfile.mkdtemp()
        os.chdir(self.tempdir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tempdir)

    def test_cmd_add(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(models.GPT35, None, io, openai_api_key="deadbeef")
        commands = Commands(io, coder)

        # Call the cmd_add method with 'foo.txt' and 'bar.txt' as a single string
        commands.cmd_add("foo.txt bar.txt")

        # Check if both files have been created in the temporary directory
        self.assertTrue(os.path.exists("foo.txt"))
        self.assertTrue(os.path.exists("bar.txt"))

    def test_cmd_add_with_glob_patterns(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(models.GPT35, None, io, openai_api_key="deadbeef")
        commands = Commands(io, coder)

        # Create some test files
        with open("test1.py", "w") as f:
            f.write("print('test1')")
        with open("test2.py", "w") as f:
            f.write("print('test2')")
        with open("test.txt", "w") as f:
            f.write("test")

        # Call the cmd_add method with a glob pattern
        commands.cmd_add("*.py")

        # Check if the Python files have been added to the chat session
        self.assertIn(os.path.abspath("test1.py"), coder.abs_fnames)
        self.assertIn(os.path.abspath("test2.py"), coder.abs_fnames)

        # Check if the text file has not been added to the chat session
        self.assertNotIn(os.path.abspath("test.txt"), coder.abs_fnames)

    def test_cmd_add_no_match(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(models.GPT35, None, io, openai_api_key="deadbeef")
        commands = Commands(io, coder)

        # Call the cmd_add method with a non-existent file pattern
        commands.cmd_add("*.nonexistent")

        # Check if no files have been added to the chat session
        self.assertEqual(len(coder.abs_fnames), 0)

    def test_cmd_drop_with_glob_patterns(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(models.GPT35, None, io, openai_api_key="deadbeef")
        commands = Commands(io, coder)

        subdir = Path("subdir")
        subdir.mkdir()
        (subdir / "subtest1.py").touch()
        (subdir / "subtest2.py").touch()

        Path("test1.py").touch()
        Path("test2.py").touch()

        # Add some files to the chat session
        commands.cmd_add("*.py")

        self.assertEqual(len(coder.abs_fnames), 2)

        # Call the cmd_drop method with a glob pattern
        commands.cmd_drop("*2.py")

        # Check if the Python files have been removed from the chat session
        self.assertIn(os.path.abspath("test1.py"), coder.abs_fnames)
        self.assertNotIn(os.path.abspath("test2.py"), coder.abs_fnames)

    def test_cmd_add_bad_encoding(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)
        from aider.coders import Coder

        coder = Coder.create(models.GPT35, None, io, openai_api_key="deadbeef")
        commands = Commands(io, coder)

        # Create a new file foo.bad which will fail to decode as utf-8
        with codecs.open("foo.bad", "w", encoding="iso-8859-15") as f:
            f.write("ÆØÅ")  # Characters not present in utf-8

        commands.cmd_add("foo.bad")

        self.assertEqual(coder.abs_fnames, set())

    def test_cmd_tokens(self):
        # Initialize the Commands and InputOutput objects
        io = InputOutput(pretty=False, yes=True)

        coder = Coder.create(models.GPT35, None, io, openai_api_key="deadbeef")
        commands = Commands(io, coder)

        commands.cmd_add("foo.txt bar.txt")

        # Redirect the standard output to an instance of io.StringIO
        stdout = StringIO()
        sys.stdout = stdout

        commands.cmd_tokens("")

        # Reset the standard output
        sys.stdout = sys.__stdout__

        # Get the console output
        console_output = stdout.getvalue()

        self.assertIn("foo.txt", console_output)
        self.assertIn("bar.txt", console_output)
