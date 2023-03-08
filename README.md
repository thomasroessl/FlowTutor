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

[code signed]: <http://daringfireball.net>