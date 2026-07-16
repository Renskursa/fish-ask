# fish-ask

Generate shell commands and put them in your Fish input so you can edit them before running.

## Install

```fish
git clone https://github.com/Renskursa/fish-ask.git
cd fish-ask
./install.sh
```

Open a new terminal after installing.

## Usage

Codex is used by default:

```fish
ask "search for a package with pacman"
```

Use local Ollama:

```fish
ask -p ollama-local -m qwen3.5:9b "search for a package with pacman"
```

Use Ollama Cloud:

```fish
ask -p ollama-cloud -m deepseek-v4-pro:cloud "search for a package with pacman"
```

Change the default provider:

```fish
set -Ux ASK_PROVIDER ollama-local
set -Ux ASK_OLLAMA_MODEL qwen3.5:9b
```
