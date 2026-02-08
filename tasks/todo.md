# Add Keychain Support for E*TRADE Credentials

## Todo
- [x] 1. Add `keyring` to `requirements.txt`
- [x] 2. Update `config/config.ini.example` with `USE_KEYRING_ETRADEKEYS` flag and comments
- [x] 3. Modify `src/etrade_core/auth.py` — conditional keyring import, helper function, flag check in `get_etrade_service`
- [x] 4. Add keychain credential storage to `src/cli/main.py`
- [x] 5. Fix: move keychain setup out of `main_menu` into a CLI subcommand (chicken-and-egg problem)
- [x] 6. Create `setup-keychain.sh` shell script

## Review

### Summary of Changes

**`requirements.txt`** — Added `keyring` dependency.

**`config/config.ini.example`** — Added `USE_KEYRING_ETRADEKEYS = false` with comments explaining the two credential modes.

**`src/etrade_core/auth.py`** — Three additions:
- Conditional `import keyring` with `_HAS_KEYRING` flag and `KEYRING_SERVICE` constant
- `_get_credentials_from_keyring(env)` helper that reads key/secret from Keychain with clear error messages
- `get_etrade_service()` now checks `USE_KEYRING_ETRADEKEYS` config flag to choose credential source; base URLs always come from `config.ini`

**`src/cli/main.py`** — Changes:
- `store_keychain_credentials()` function that prompts for env, key, and secret, then stores them via `keyring.set_password()`
- Added `setup-keychain` CLI subcommand so credentials can be stored *before* authentication
- Removed the unreachable "Store credentials in Keychain" menu option from `main_menu` (was behind auth wall — chicken-and-egg problem)

**`setup-keychain.sh`** *(new)* — Shell script mirroring `etrade-auth.sh` that runs `python src/cli/main.py setup-keychain`.

### User Flow
1. `./setup-keychain.sh` — prompts for env, key, and secret, stores in macOS Keychain
2. Set `USE_KEYRING_ETRADEKEYS = true` in `config/config.ini`
3. `./etrade-auth.sh` or MCP server works as normal, reading credentials from Keychain

### What's Unchanged
- All token handling (tokens.json, save/load)
- Base URLs remain in config.ini
- MCP server, accounts, market modules — zero changes
- Default behavior (USE_KEYRING_ETRADEKEYS=false) is identical to before
