# Windows directives

## Long-Running Processes

- Never launch dev servers, ngrok, or backend daemons as background Bash processes. They die when the session or the tool call ends.
- Instead: write or update a `.bat` launcher (`serve.bat`, `run-backend.bat`) and tell me to run it in my own terminal.
- For services, use NSSM only after you verify the target account has the user-scoped dependencies (Python packages, Playwright browsers). If you cannot verify, default to the `.bat` launcher.
- Before you start any server, kill the orphaned listeners on the target port (IPv4 and IPv6 bindings) and confirm the port is free.

## PowerShell Native-Command Quoting

- PowerShell 7 passes `'""'` to a native exe as the two literal characters `""`, not an empty string. Pass an empty argument as `''` or `""`.
- Example: `ssh-keygen -N '""'` made a key whose passphrase was literally `""`, and Voltius kept asking for one. Fix: `ssh-keygen -p`, old passphrase `""`, new passphrase empty.
- Generate SSH keys with `-N ''`, then verify with `ssh-keygen -y -P '' -f <key>` before you hand the key over.
