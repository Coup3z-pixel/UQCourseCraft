#!/bin/sh

# Set Session Name
SESSION="UQCourseCraft"
SESSIONEXISTS=$(tmux list-sessions | grep $SESSION)

# Only create tmux session if it doesn't already exist
if [ "$SESSIONEXISTS" = "" ]
then
    # Start New Session with our name
    tmux new-session -d -s $SESSION

    # setup Writing window
    tmux rename-window -t 0 'Writing'
    tmux send-keys -t 'Writing' "nvim ." C-m

    # Name first Pane and start zsh
    tmux new-window -t $SESSION:1 -n 'frontend'
	tmux send-keys -t 'frontend' 'cd ./frontend' C-m
    tmux send-keys -t 'frontend' 'pnpm run dev' C-m 'clear' C-m # Switch to bind script?

	tmux new-window -t $SESSION:2 -n 'flask'
	tmux send-keys -t 'flask' 'cd ./backend' C-m
	tmux send-keys -t 'flask' 'source .venv/bin/activate' C-m
	tmux send-keys -t 'flask' 'flask --app main run --debug' C-m 'clear' C-m

    # Setup an additional shell
    tmux new-window -t $SESSION:3 -n 'Shell'
fi

# Attach Session, on the Main window
tmux attach-session -t $SESSION:0
