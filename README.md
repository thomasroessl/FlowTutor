<h1 align="center">
    <img src="https://raw.githubusercontent.com/thomasroessl/FlowTutor/master/logo.png" alt="flowtutor-logo" style="max-width=512px;max-height:141px;"/>
</h1>

<h4 align="center">
    A graphical programming environment using flowcharts.
</h4>

<h1></h1>

<p align="center">
  <a href=""><img src="https://img.shields.io/pypi/pyversions/flowtutor" alt="Python versions"></a>
  <a href="https://pypi.org/project/flowtutor/"><img src="https://img.shields.io/pypi/v/flowtutor" alt="PYPI"></a>
  <a href="https://cd.roessl.org/job/FlowTutor/"><img src="https://cd.roessl.org/job/FlowTutor/badge/icon" alt="Jenkins"></a>
</p>

## Prerequisites

The following programs have to be available on the system for FlowTutor to be able to run:

- [Python] >= 3.9
- For C programs only:
    - [GCC] - C-Compiler
    - [GDB] - Debugger

## Documentation

An overview of FlowTutors functionality can be found in the projects [Wiki]

## Running

FlowTutor is available through the Python Package Index:

```sh
python -m pip install flowtutor
```

## Running C programs on macOS

> **Warning** 
> As of June 2023 there exists a bug in MacOS/GDB, that prevents the debugging functionality of FlowTutor from functioning correctly.

Flowtutor uses GDB for its C debugging functionality.
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


[Python]: <https://www.python.org/>
[GCC]: <https://gcc.gnu.org/>
[GDB]: <https://www.sourceware.org/gdb/>
[code signed]: <https://sourceware.org/gdb/wiki/PermissionsDarwin>
[Wiki]: <https://github.com/thomasroessl/FlowTutor/wiki>