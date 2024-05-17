# Python ctypes-based bindings for libvlc

![](https://img.shields.io/github/actions/workflow/status/yanns1/python-vlc/tests.yml?event=push&label=tests)

This file documents the bindings generator, not the bindings
themselves. For the bindings documentation, see the README.module
file.

The bindings generator generates ctypes-bindings from the include
files defining the public API. The same generated module should be
compatible with various versions of libvlc 2.\* and 3.\*. However, there
may be incompatible changes between major versions. Versioned bindings
for 2.2 and 3.0 are provided in the repository.

## License

The module generator is licensed under the GNU General Public License
version 2 or later. The generated module is licensed, like libvlc,
under the GNU Lesser General Public License 2.1 or later.

## Development

You can get the latest version of the code generator from
<https://github.com/oaubert/python-vlc/> or
<http://git.videolan.org/?p=vlc/bindings/python.git>.

The code expects to be placed inside a VLC source tree, in
vlc/bindings/python, so that it finds the development include files,
or to find the installed include files in /usr/include (on Debian,
install libvlc-dev).

Once you have cloned the project, you can run

```
python3 dev_setup.py
```

from the root.
This script will install everything that is needed (submodules,
virtual environment, packages, etc.) for you to generate the bindings.
Then, activate the virtual environment:

- On Linux with Bash:
  ```
  . .venv/bin/activate
  ```
- On Windows with Powershell:
  ```
  .\.venv\Scripts\Activate.ps1
  ```

See https://docs.python.org/3/library/venv.html#how-venvs-work for other os-shell combinations.

To generate the vlc.py module and its documentation, for both the
development version and the installed VLC version, use `make`.

For running tests, use `make test`.
Note that you need vlc installed because some tests require the
libvlc's dynamic library to be present on the system.

If you want to generate the bindings from an installed version of the
VLC includes (which are expected to be in /usr/include/vlc), use the
'installed' target: `make installed`.

See more recipes in the Makefile.

To install python-vlc for development purposes (add a symlink to your Python
library) simply do

```
python setup.py develop
```

preferably inside a virtualenv. You can uninstall it later with

```
python setup.py develop --uninstall
```

Documentation building needs epydoc. An online build is available at
<http://olivieraubert.net/vlc/python-ctypes/>

## Packaging

The generated module version number is built from the VLC version
number and the generator version number:

vlc_major.vlc_minor.(1000 * vlc_micro + 100 * generator_major + generator_minor)

so that it shared it major.minor with the corresponding VLC.

To generate the reference PyPI module (including setup.py, examples
and metadata files), use

```
make dist
```

## Architecture

First of all, the bindings generator is in generator/generate.py.

It really is the conjunction of two things:

1. A **parser** of C header files (those of libvlc): that is the class `Parser`.
1. A **generator** of Python bindings: that is the class `PythonGenerator`.

`Parser` parses libvlc's headers and produce a kind of AST where nodes are
instances of either `Struct`, `Union`, `Func`, `Par`, `Enum` or `Val`.
The information kept is what is necessary for `PythonGenerator` to then produce
the bindings.

Until version 2 of the bindings generator, parsing was regex-based.
It worked pretty well thanks to the consistent coding style of libvlc.
However, it remained rather fragile.

Since version 2, parsing is done using [Tree-sitter](https://tree-sitter.github.io/tree-sitter/).
More specifically, we use the [C Tree-sitter grammar](https://github.com/tree-sitter/tree-sitter-c)
and [Tree-sitter's Python bindings](https://github.com/tree-sitter/py-tree-sitter).
It offers a more complete and robust parsing of C code.
The job of `Parser` is thus to transform the AST[^1] produced by Tree-sitter into an "AST"
understandable by the generator.

## LibVLC Discord

[![Join the chat at https://discord.gg/3h3K3JF](https://img.shields.io/discord/716939396464508958?label=discord)](https://discord.gg/3h3K3JF)

python-vlc is part of the LibVLC Discord Community server. Feel free to come say hi!

## How to contribute

Contributions such as:

- reporting and fixing bugs,
- contributing unit tests
- contributing examples

are welcomed!

[^1]: To be exact, it produces a CST: Concrete Syntax Tree.
