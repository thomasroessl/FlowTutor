<h1 align="center">FlowTutor</h1>

<p align="center">
  <img src="https://raw.githubusercontent.com/thomasroessl/FlowTutor/master/logo.png" alt="flowtutor-logo" width="512px" height="141px"/>
  <br>
  <em>FlowTutor is a graphical programming environment designed to cater to the needs of engineering students.</em>
  <br>
</p>

## Prerequisites

The following programs have to be available on the system for FlowTutor to be able to run:

- [Python] >= 3.9
- [tkinter] - For system file dialogs
- [GCC] - C-Compiler
- [GDB] - Debugger

## Documentation

An overview of FlowTutors functionality can be found in the projects [Wiki]

## Running the Python project from source

1. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

2. Activate the virtual environment:
    ```sh
    source venv/bin/activate
    ```

3. Install the FlowTutor package:
    ```sh
    python -m pip install .
    ```

6. Run FlowTutor:
    ```sh
    flowtutor
    ```

## Running on macOS

> **Warning** 
> As of June 2023 there exists a bug in MacOS/GDB, that prevents the debugging functionality of FlowTutor from functioning correctly.

Flowtutor uses GDB for its debugging functionality.
Modern Darwin kernels (used in macOS) restrict the capability to assume control over another process, which GDB needs to debug the program.
To give the correct permissions to GDB it needs to be [code signed].

### 1. Create a certificate
Run the script `macos-setup-codesign.sh` from the `gdb-codesign` folder.
This sets up a certificate in the System Keychain and trusts the certificate for code signing.

### 2. Sign and entitle the gdb binary
Execute the following command with `gdb-entitlement.xml` from the `gdb-codesign` folder:
```sh
codesign --entitlements gdb-entitlement.xml -fs gdb-cert $(which gdb)
```

### 3. Reboot
This refreshes the system's certificates and code-signing data.

## Windows Installer Packages

The application is packaged with Pynsist for easier distribution on Windows.

Because Pynsist makes use of the “bundled” versions of Python the `tkinter` module isn’t included by default.

For the currently used version of Python the [necessary files], namely `_tkinter.lib`, `_tkinter.pyd`, `_tkinter.lib`, `tcl86t.dll` and `tk86t.dll` in `pynsist_pks/` and the contents of `lib/` folder, have been correctly included.

Should the bundled Python version change, these files have to be replaced accordingly.

[Python]: <https://www.python.org/>
[tkinter]: <https://docs.python.org/3/library/tkinter.html>
[GCC]: <https://gcc.gnu.org/>
[GDB]: <https://www.sourceware.org/gdb/>
[code signed]: <https://sourceware.org/gdb/wiki/PermissionsDarwin>
[necessary files]: <https://pynsist.readthedocs.io/en/latest/faq.html#packaging-with-tkinter>
[Wiki]: <https://github.com/thomasroessl/FlowTutor/wiki>