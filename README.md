
# Window Profiler

Saves window size/position/state for a workspace or global and restores them either manually or automatically on opening.

This is written and tested for openbox but should work with any stacking window manager. Probably won't work with wayland but can't test it right now (well ok.. i'm too lazy.. drop me a line).

&nbsp;

## Requirements

`python >= 3.9, gtk3, libwnck3`

for arch linux:

```sh
pacman -S python gtk3 libwnck3
```

For other distributions please consult google.

&nbsp;

## Installation

Just clone or copy the repository wherever you want and
`chmod +x ./windowprofiler/windowprofiler.py`.

If you want to, create a symlink in your bin directory, like `ln -s /opt/windowprofiler/windowprofiler.py /usr/bin/windowprofiler`

&nbsp;

## Usage

This program is designed to work with keybindings.
The most important parameter for which a keybinding should be created is `-m` or `--manage`.
I also recommend to create some for the parameter `--restore` and maybe `--restore-all`.

(see `windowprofiler --help` for info about the parameters).

### Managing Window Profiles / -m / --manage

Create a keybinding for `windowprofiler.py -m`, select the window you wish to manage and press that keybinding.
The following dialog will appear.

![manage widnow profiles](https://dubitabam.github.io/windowprofiler/manage.png)

#### Profile

You can create multiple profiles for a window. The name doesn't matter.

#### Resolutions

This is a comma seperated list of resulotions the profile will apply to. If you have multiple displays, this is the combined resolution of all displays.

#### Workspace

Select the workspace the profile will apply to or check `Global` to make the profile apply to all workspaces. Note that a workspace specific profile always takes precedence.

#### Restore-Options

Check `Auto apply on new windows` to have the profile automatically restored when a new window is opened.
You have to run windowprofiler in demon mode (`-d`).

If you set `Apply only on the nth window` the profile will only be applied to the 1st, 2nd, ... window that is on the current workspace or all workspaces for global profiles.

Rest of the options in this section should be self-explanatory.

#### Additional-Options

Here you can make the profile match only windows with a certain text in the title bar.

### Restoring profiles / --restore / --restore-all

Create a keybinding for `windowprofiler.py -restore` and/or `windowprofiler.py --restore-all`.
Select a window you have a saved profile for and press the keybinding for `--restore`. If a suitable profile is found it'll be applied.
`--restore-all` does the same thing but for all windows on current workspace.

### Demon

To automatically restore profiles on newly opened windows you have to run windowprofiler in demon mode. Just create an autostart entry, e.g. for openbox add a line like this to openbox's autostart file `windowprofiler.py -d`.

### Keybindings

Use whatever your distribution offers.
[sxhkd](https://github.com/baskerville/sxhkd) is a good option.

Here's my sxhkd config:
```sh
super + ctrl + alt + {m,p,r,a}
    /usr/bin//window-profiler {-m,-p,-r,-a}
```

### Logging

To enbable logging just add `--log-file=PATH` and/or `--log-console` to the command line.
Use `--log-level` to set the level of logging. Valid values are `DEBUG`, `INFO`, `WARN`, `ERROR`, `CRITICAL`, the default is `INFO`.
