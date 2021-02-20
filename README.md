

# (doesn't work... )
# https://unix.stackexchange.com/questions/25372/turn-off-buffering-in-pipe#comment225838_25378
# https://unix.stackexchange.com/questions/25372/turn-off-buffering-in-pipe#comment1037095_53445
brew install coreutils
./log_stream.py /dev/cu.Repleo-PL2303-00001014 | gstdbuf -o0 tee -a ~/Desktop/co2-overnight.csv
