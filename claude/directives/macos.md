# macOS directives

## Long-running processes

- Never launch dev servers, tunnels, or backend daemons as background Bash processes. The session owns them and nothing restarts them.
- Instead: write or update a launcher script (`serve.sh`, `run-backend.sh`) and tell me to run it in my own terminal.
- For services that must start at login, use a `launchd` plist in `~/Library/LaunchAgents` with `KeepAlive` for restarts. Load it with `launchctl bootstrap gui/$(id -u) <plist>`.
- A LaunchAgent does not inherit the shell `PATH` (`/opt/homebrew/bin` is missing). Set `EnvironmentVariables` or use absolute paths, and verify the user-scoped dependencies first. If you cannot verify, default to the launcher script.
- Before you start any server, find listeners with `lsof -nP -iTCP:<port> -sTCP:LISTEN`, kill them, and confirm the port is free. Sockets of other users need `sudo`.

## Shell quoting (zsh)

- A word that starts with `=` expands as a command path. `echo ===X` fails with `==X not found`. Quote it: `echo '===X'`.
- Quote globs that zsh would expand (`'*.dart'`). An unmatched glob is an error in zsh.
- Generate SSH keys with `-N ''`, then verify with `ssh-keygen -y -P '' -f <key>`.
