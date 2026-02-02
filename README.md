# mc-bot

Small discord bot for managing a Minecraft servers.

## Running

If for some reason you want to run this yourself, you can use [nix](https://nixos.org/)
to build it. Just run `nix build`.

If you don't want to use nix, you can probably use `uv` (the underlying build
system that our nix derivation relies on).

You'll have to supply a set of env vars as well. Currently, we use the following:
```
DISCORD_TOKEN=
PROJECT_ID=
ZONE=
SERVER=

SSH_USER=
SSH_KEY_PATH=

CF_API_KEY=

WHITELIST=
```
