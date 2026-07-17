# fish-ask

Generate shell commands and put them in your Fish input so you can edit them before running.

## Install

### Linux, macOS, WSL, Cygwin, or MSYS2

```fish
git clone https://github.com/Renskursa/fish-ask.git
cd fish-ask
./install.sh
```

Open a new terminal after installing.

### Windows Command Prompt

Python 3 and either Codex or Ollama must be installed and available in `PATH`.

```bat
git clone https://github.com/Renskursa/fish-ask.git
cd fish-ask
install.cmd
```

Open a new Command Prompt after installing. The Windows command prints the generated CMD
command so you can review it before running it:

```bat
ask "find all large log files"
```

To uninstall from Windows, run `uninstall.cmd` from the cloned repository.

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

In Windows Command Prompt, use `setx` and then open a new terminal:

```bat
setx ASK_PROVIDER ollama-local
setx ASK_OLLAMA_MODEL qwen3.5:9b
```

Set `ASK_SHELL` to override the generated command syntax when needed.
