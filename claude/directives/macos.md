# macOS directives

## Long-running processes

- Never launch dev servers, tunnels, or backend daemons as background Bash processes. They die when the session or tool call ends.
- Instead: write or update a launcher script (`serve.sh`, `run-backend.sh`) and tell me to run it in my own terminal.
- For services that must survive reboot, use a `launchd` plist in `~/Library/LaunchAgents`. Verify the user-scoped dependencies first. If you cannot verify, default to the launcher script.
- Before you start any server, find orphaned listeners with `lsof -nP -iTCP:<port> -sTCP:LISTEN`, kill them, and confirm the port is free.

## Shell quoting (zsh)

- Pass an empty argument as `''`. Generate SSH keys with `-N ''`, then verify with `ssh-keygen -y -P '' -f <key>`.
- Quote globs that zsh would expand (`'*.dart'`); an unmatched glob is an error in zsh.
