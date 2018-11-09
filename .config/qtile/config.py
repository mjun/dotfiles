# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import socket
import subprocess

from libqtile.config import Key, Screen, Group, Drag, Click
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook, extension
from libqtile.widget import Spacer

try:
    from typing import List  # noqa: F401
except ImportError:
    pass

##### VARIOUS CONSTANTS #####

HOME_DIR = os.path.expanduser('~')
MOD_KEY = "mod4"
TERMINAL_CMD = "terminal"

##### COLORS #####

BACKGROUND_COLOR = "#222D31"
FOREGROUND_COLOR = "#F8F8F8"
FOREGROUND_COLOR_SECONDARY = "#D8D8D8"
BORDER_NORMAL = "#595B5B"
BORDER_FOCUS = "#F9FAF9"
BORDER_ACTIVE = "#12876F"

FONT = "Noto Sans"
FONT_SIZE = "10"

BAR_HEIGHT = 24

##### INIT GROUPS #####

groups = [Group(i) for i in "123456789"]
visible_groups = [groups[0].name, ] # always keep first group visible

##### GROUP FUNCTIONS #####

def window_to_prev_group(visible_groups):
    def f(qtile):
        if qtile.currentWindow is not None:
            i = qtile.groups.index(qtile.currentGroup)
            target_group = i - 1 if i > 0 else 8
            prev_group = qtile.groups[target_group].name
            
            # if target group name is not visible, make it visible
            if prev_group not in visible_groups:
                visible_groups.append(prev_group)
            
            # move window to group
            qtile.currentWindow.togroup(prev_group)
            
            # hide current group if empty and if it's not the first group
            if len(qtile.currentGroup.windows) == 0 and qtile.currentGroup.name != visible_groups[0]:
                visible_groups.remove(qtile.currentGroup.name)
            
            # switch to group
            qtile.groupMap[prev_group].cmd_toscreen()
    return f

def window_to_next_group(visible_groups):
    def f(qtile):
        if qtile.currentWindow is not None:
            i = qtile.groups.index(qtile.currentGroup)
            target_group = i + 1 if i < 8 else 0
            next_group = qtile.groups[target_group].name
            
            # if target group name is not visible, make it visible
            if next_group not in visible_groups:
                visible_groups.append(next_group)
                
            # move window to group
            qtile.currentWindow.togroup(next_group)
            
            # hide current group if empty and if it's not the first group
            if len(qtile.currentGroup.windows) == 0 and qtile.currentGroup.name != visible_groups[0]:
                visible_groups.remove(qtile.currentGroup.name)
            
            # switch to group
            qtile.groupMap[next_group].cmd_toscreen()
    return f

def switch_to_group(name, visible_groups):
    def f(qtile):
        if qtile.currentGroup.name != name:
            # hide current group if empty and if it's not the first group
            if len(qtile.currentGroup.windows) == 0 and qtile.currentGroup.name != visible_groups[0]:
                visible_groups.remove(qtile.currentGroup.name)
                
            # if group we are switching to is not visible, make it visible
            if name not in visible_groups:
                visible_groups.append(name)
                
            # finally, switch to group
            qtile.groupMap[name].cmd_toscreen()
    return f
    
def move_window_to_group(name, visible_groups):
    def f(qtile):
        if qtile.currentWindow is not None and qtile.currentGroup.name != name:
            # hide current group if empty and if it's not the first group
            if len(qtile.currentGroup.windows) == 0 and qtile.currentGroup.name != visible_groups[0]:
                visible_groups.remove(qtile.currentGroup.name)
                
            # if target group name is not visible, make it visible
            if name not in visible_groups:
                visible_groups.append(name)
                
            # move current window to group
            qtile.currentWindow.togroup(name)
            
            # switch to group
            qtile.groupMap[name].cmd_toscreen()
    return f

##### KEYBINDINGS #####

dmenu = extension.DmenuRun(
    dmenu_prompt="run:",
    dmenu_ignorecase=True,
    background=BACKGROUND_COLOR,
    foreground=FOREGROUND_COLOR,
    selected_background=BORDER_ACTIVE,
    selected_foreground=FOREGROUND_COLOR,
    dmenu_height=BAR_HEIGHT,
    dmenu_font='{}-{}'.format(FONT, FONT_SIZE)
)

session_dmenu = extension.DmenuRun(
    dmenu_command=HOME_DIR + "/.config/qtile/session_dmenu.sh",
    dmenu_prompt="session:",
    dmenu_ignorecase=True,
    background=BACKGROUND_COLOR,
    foreground=FOREGROUND_COLOR,
    selected_background=BORDER_ACTIVE,
    selected_foreground=FOREGROUND_COLOR,
    dmenu_height=BAR_HEIGHT,
    dmenu_font='{}-{}'.format(FONT, FONT_SIZE)
)

keys = [
    # Switch between windows in current stack pane
    Key([MOD_KEY], "k", lazy.layout.down()),
    Key([MOD_KEY], "j", lazy.layout.up()),

    # Move windows up or down in current stack
    Key([MOD_KEY, "shift"], "k", lazy.layout.shuffle_down()),
    Key([MOD_KEY, "shift"], "j", lazy.layout.shuffle_up()),
    
    # Shrink/Grow windows (XMonadTall) / Increase/decrease number in master pane (Tile)
    Key([MOD_KEY, "shift"], "l", 
        lazy.layout.grow().when('xmonad-tall'),
        lazy.layout.increase_nmaster().when('tile'),
    ),
    Key([MOD_KEY, "shift"], "h", 
        lazy.layout.shrink().when('xmonad-tall'),
        lazy.layout.decrease_nmaster().when('tile'),
    ),
    
    # Min/Max/Restore
    Key([MOD_KEY, "control"], "n", lazy.layout.normalize()),
    Key([MOD_KEY, "control"], "m", lazy.layout.maximize()),

    # Move windows between workspaces
    Key([MOD_KEY, "shift"], "Left", lazy.function(window_to_prev_group(visible_groups))),
    Key([MOD_KEY, "shift"], "Right", lazy.function(window_to_next_group(visible_groups))),

    # Switch window focus to other pane(s) of stack
    Key([MOD_KEY], "space", lazy.window.toggle_floating()),

    # Swap panes of split stack / Switch which side main pane occupies (XmonadTall)
    Key([MOD_KEY, "shift"], "space", lazy.layout.rotate(), lazy.layout.flip()),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([MOD_KEY, "shift"], "Return", lazy.layout.toggle_split()),
    
    # Lock screen
    Key([MOD_KEY, "control"], "l", lazy.spawn("blurlock")),
    
    # Toggle between different layouts as defined below
    Key([MOD_KEY], "Tab", lazy.next_layout()),
    
    Key([MOD_KEY, "shift"], "q", lazy.window.kill()),                   # close window

    Key([MOD_KEY, "control"], "q", lazy.run_extension(session_dmenu)),  # session menu
    
    Key([MOD_KEY], "m", lazy.spawn("morc_menu")),                       # classic menu with groups
    Key([MOD_KEY], "s", lazy.spawn(TERMINAL_CMD + " -e 'bmenu'")),      # settings menu
    Key([MOD_KEY], 'r', lazy.run_extension(dmenu)),                     # run menu
    
    # Application start bindings
    Key([MOD_KEY], "Return", lazy.spawn(TERMINAL_CMD)),
    
    Key([MOD_KEY], "w", lazy.spawn("firefox")),
    Key([MOD_KEY], "f", lazy.spawn("pcmanfm")),
    Key([MOD_KEY], "e", lazy.spawn("geany")),
]

##### NAMED GROUPS #####

for group in groups:
    keys.append(Key([MOD_KEY], group.name, lazy.function(switch_to_group(group.name, visible_groups))))
    keys.append(Key([MOD_KEY, "shift"], group.name, lazy.function(move_window_to_group(group.name, visible_groups))))

##### LAYOUTS #####

layout_theme = {
    "border_width": 1,
    "margin": 5,
    "border_focus": BORDER_FOCUS,
    "border_normal": BORDER_NORMAL
}

layouts = [
    layout.Max(**layout_theme),
    layout.MonadTall(**layout_theme),
    layout.Tile(shift_windows=True, **layout_theme),
    layout.Floating(**layout_theme)
]

##### WIDGETS #####

widget_defaults = dict(
    fontsize=12,
    padding=2
)
extension_defaults = widget_defaults.copy()

##### SCREENS #####

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.GroupBox(
                    active = FOREGROUND_COLOR, 
                    inactive = FOREGROUND_COLOR,
                    rounded = False,
                    highlight_method = "block",
                    this_current_screen_border = BORDER_ACTIVE,
                    this_screen_border = BORDER_ACTIVE,
                    other_current_screen_border = BACKGROUND_COLOR,
                    other_screen_border = BACKGROUND_COLOR,
                    foreground = FOREGROUND_COLOR, 
                    background = BACKGROUND_COLOR,
                    visible_groups = visible_groups,
                    margin = 0,
                    padding_x = 2,
                    padding_y = 5
                ),
                widget.Sep(
                    linewidth = 0,
                    padding = 6,
                    foreground = BACKGROUND_COLOR, 
                    background = BACKGROUND_COLOR
                ),
                widget.WindowName(
                    foreground = FOREGROUND_COLOR_SECONDARY, 
                    background = BACKGROUND_COLOR,
                    padding_x = 4
                ),
                widget.Systray(
                    foreground = FOREGROUND_COLOR, 
                    background = BACKGROUND_COLOR
                ),
                widget.Sep(
                    linewidth = 0,
                    padding = 6,
                    foreground = BACKGROUND_COLOR, 
                    background = BACKGROUND_COLOR
                ),
                widget.Clock(
					format='%d.%m.%Y %H:%M',
					foreground = FOREGROUND_COLOR, 
                    background = BACKGROUND_COLOR
                ),
                widget.Sep(
                    linewidth = 0,
                    padding = 6,
                    foreground = BACKGROUND_COLOR, 
                    background = BACKGROUND_COLOR
                ),
                widget.CurrentLayoutIcon(
                    background = BORDER_NORMAL
                )
            ],
            BAR_HEIGHT,
        ),
    ),
]

##### FLOATING WINDOWS #####

@hook.subscribe.client_new
def floating(window):
    floating_types = ['notification', 'toolbar', 'splash', 'dialog']
    transient = window.window.get_wm_transient_for()
    if window.window.get_wm_type() in floating_types or transient:
        window.floating = True

# Drag floating layouts.
mouse = [
    Drag([MOD_KEY], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([MOD_KEY], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([MOD_KEY], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        {'wmclass': 'confirm'},
        {'wmclass': 'dialog'},
        {'wmclass': 'download'},
        {'wmclass': 'error'},
        {'wmclass': 'file_progress'},
        {'wmclass': 'notification'},
        {'wmclass': 'splash'},
        {'wmclass': 'toolbar'},
        {'wmclass': 'confirmreset'},  # gitk
        {'wmclass': 'makebranch'},  # gitk
        {'wmclass': 'maketag'},  # gitk
        {'wname': 'branchdialog'},  # gitk
        {'wname': 'pinentry'},  # GPG key password entry
        {'wmclass': 'ssh-askpass'},  # ssh-askpass
    ],
    border_focus=BORDER_FOCUS, 
    border_normal = BORDER_NORMAL
)
auto_fullscreen = True
focus_on_window_activation = "smart"

# Autostart applications
@hook.subscribe.startup_once
def startup_once():
    subprocess.call([HOME_DIR + '/.config/qtile/startup_once.sh'])
    
@hook.subscribe.startup
def startup():
    subprocess.call([HOME_DIR + '/.config/qtile/startup.sh'])

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, github issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
