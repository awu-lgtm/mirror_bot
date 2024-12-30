## Install
```
conda env create -n mirror_bot -f dependencies.yml
conda activate mirror_bot
```
Also need npm.

In `mirror_bot_gui`, run
```
npm install
```

## Run
In `src`, run
```
python server.py
```

### UI
In `mirror_bot_gui`, run
```
npm run serve
```

The folder that stores the log and images is printed in the terminal at the start of the program.