"""tests for the 'pip' command."""
import os
import sys
import unittest

from six.moves import reload_module

from stash.tests.stashtest import StashTestCase, requires_network


class PipTests(StashTestCase):
    """tests for the 'pip' command."""
    def setUp(self):
        """setup the tests"""
        self.cwd = self.get_data_path()
        StashTestCase.setUp(self)

    def tearDown(self):
        """clean up a test."""
        try:
            self.purge_packages()
        except Exception as e:
            self.logger.warning("Could not purge packages: " + repr(e))
        StashTestCase.tearDown(self)

    def get_data_path(self):
        """return the data/ sibling path"""
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))

    def purge_packages(self):
        """uninstall all packages."""
        output = self.run_command("pip list", exitcode=0)
        lines = output.split("\n")
        packages = [line.split(" ")[0] for line in lines]
        for package in packages:
            if package in ("", " ", "\n"):
                continue
            self.run_command("pip uninstall " + package)

    def reload_module(self, m):
        """reload a module."""
        reload_module(m)


    def test_help(self):
        """test 'pip --help'"""
        output = self.run_command("pip --help", exitcode=0)
        self.assertIn("pip", output)
        self.assertIn("-h", output)
        self.assertIn("--help", output)
        self.assertIn("-v", output)
        self.assertIn("-6", output)
        self.assertIn("--verbose", output)
        self.assertIn("install", output)
        self.assertIn("uninstall", output)
        self.assertIn("versions", output)
        self.assertIn("search", output)
        self.assertIn("download", output)
        self.assertIn("list", output)

    @requires_network
    def test_search(self):
        """test 'pip search <term>'"""
        output = self.run_command("pip search pytest", exitcode=0)
        self.assertIn("pytest", output)
        self.assertIn("pytest-cov", output)
        self.assertIn("pytest-env", output)

    @requires_network
    def test_versions(self):
        """test 'pip versions <package>'."""
        output = self.run_command("pip versions pytest", exitcode=0)
        self.assertIn("pytest - 2.0.0", output)
        self.assertIn("pytest - 2.5.0", output)
        self.assertIn("pytest - 3.0.0", output)
        self.assertIn("pytest - 3.5.0", output)

    @requires_network
    def test_install_pypi_simple_1(self):
        """test 'pip install <pypi_package>' (Test 1)."""
        output = self.run_command("pip --verbose install benterfaces", exitcode=0)
        self.assertIn("Downloading package", output)
        self.assertIn("Running setup file", output)
        self.assertIn("Package installed: benterfaces", output)
        self.assertNotIn("Failed to run setup.py", output)
        try:
            import benterfaces
        except ImportError as e:
            self.logger.info("sys.path = " + str(sys.path))
            raise AssertionError("Could not import installed module: " + repr(e))

    @requires_network
    def test_install_pypi_simple_2(self):
        """test 'pip install <pypi_package>' (Test 2)."""
        output = self.run_command("pip --verbose install nose", exitcode=0)
        self.assertIn("Downloading package", output)
        self.assertIn("Running setup file", output)
        self.assertIn("Package installed: nose", output)
        self.assertNotIn("Failed to run setup.py", output)
        try:
            import nose
        except ImportError as e:
            self.logger.info("sys.path = " + str(sys.path))
            raise AssertionError("Could not import installed module: " + repr(e))

    @requires_network
    def test_install_pypi_version_1(self):
        """test 'pip install <pypi_package>==<specific_version_1>' (Test 1)."""
        output = self.run_command("pip --verbose install rsa==3.4.2", exitcode=0)
        self.assertIn("Downloading package", output)
        self.assertIn("Running setup file", output)
        self.assertIn("Package installed: rsa", output)
        self.assertNotIn("Failed to run setup.py", output)
        try:
            import rsa
            self.reload_module(rsa)
        except ImportError as e:
            self.logger.info("sys.path = " + str(sys.path))
            raise AssertionError("Could not import installed module: " + repr(e))
        else:
            self.assertEqual(rsa.__version__, "3.4.2")

    @requires_network
    def test_install_pypi_version_2(self):
        """test 'pip install <pypi_package>==<specific_version_2>' (Test 2)."""
        output = self.run_command("pip --verbose install rsa==3.2.2", exitcode=0)
        self.assertIn("Downloading package", output)
        self.assertIn("Running setup file", output)
        self.assertIn("Package installed: rsa", output)
        self.assertNotIn("Failed to run setup.py", output)
        try:
            import rsa
            self.reload_module(rsa)
        except ImportError as e:
            self.logger.info("sys.path = " + str(sys.path))
            raise AssertionError("Could not import installed module: " + repr(e))
        else:
            self.assertEqual(rsa.__version__, "3.2.2")

    @unittest.skip("test not fully working")
    @requires_network
    def test_update(self):
        """test 'pip update <pypi_package>'."""
        output = self.run_command("pip --verbose install rsa==3.2.3", exitcode=0)
        self.assertIn("Downloading package", output)
        self.assertIn("Running setup file", output)
        self.assertIn("Package installed: rsa", output)
        self.assertNotIn("Failed to run setup.py", output)
        try:
            import rsa
            self.reload_module(rsa)
        except ImportError as e:
            self.logger.info("sys.path = " + str(sys.path))
            raise AssertionError("Could not import installed module: " + repr(e))
        else:
            self.assertEqual(rsa.__version__, "3.2.3")
            del rsa
        output = self.run_command("pip --verbose update rsa", exitcode=0)
        try:
            import rsa
            self.reload_module(rsa)
        except ImportError as e:
            self.logger.info("sys.path = " + str(sys.path))
            raise AssertionError("Could not import installed module: " + repr(e))
        else:
            self.assertNotEqual(rsa.__version__, "3.2.3")
            del rsa

    def test_install_local(self):
        """test 'pip install <path/to/package/>'."""
        self.run_command("zip ./stpkg.zip ./stpkg/", exitcode=0)
        output = self.run_command("pip --verbose install stpkg.zip", exitcode=0)
        self.assertIn("Package installed: stpkg.zip", output)
        self.assertNotIn("Downloading package", output)
        self.assertIn("Running setup file", output)
        self.assertNotIn("Failed to run setup.py", output)

        output = self.run_command("stash_pip_test", exitcode=0)
        self.assertIn("local pip test successfull!", output)

    def test_install_github(self):
        """test 'pip install <owner>/<repo>'."""
        output = self.run_command("pip --verbose install bennr01/benterfaces", exitcode=0)
        self.assertIn("Working on GitHub repository ...", output)
        self.assertIn("Running setup file", output)
        self.assertIn("Package installed: benterfaces-master", output)
        self.assertNotIn("Failed to run setup.py", output)
