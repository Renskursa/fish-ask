function ask --description 'Generate an editable Fish command with Codex or Ollama'
    if test (count $argv) -eq 0
        echo 'usage: ask [--provider PROVIDER] [--model MODEL] "what you want a command for"' >&2
        return 2
    end

    # Help and version are informational; show them instead of inserting them.
    if contains -- $argv[1] -h --help --version
        command ask $argv
        return $status
    end

    # `command` bypasses this function and runs ~/.local/bin/ask.
    set -l generated (command ask $argv)
    set -l ask_status $status
    if test $ask_status -ne 0
        return $ask_status
    end

    commandline --replace -- (string join \n $generated)
    commandline --function repaint
end
