# FlowTutor

## Running on macOS

Flowtutor uses GDB for its debugging functionality.
Modern Darwin kernels (used in macOS) restrict the capability to assume control over another process, which GDB needs to debug the program.
To give the correct permissions to GDB it needs to be [code signed].

### 1. Create a certificate
Run the script `macos-setup-codesign.sh` from the `gdb-codesign` folder.
This sets up a certificate in the System Keychain and trusts the certificate for code signing.

### 2. Sign and entitle the gdb binary
Execute the following command with `gdb-entitlement.xml` from the `gdb-codesign` folder.
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



[code signed]: <https://sourceware.org/gdb/wiki/PermissionsDarwin>

[necessary files]: <https://pynsist.readthedocs.io/en/latest/faq.html#packaging-with-tkinter>