# spooky scary game jam skeleton

Project Purpose: Iron out some python-pyglet-2drendering-packaging inconveniences before participating in a game jam

## Requirements

Built with python 3.6.6. I used [pyenv/pyenv](https://github.com/pyenv/pyenv) to manage my python installation.

Uses [pypa/pipenv](https://github.com/pypa/pipenv) for virtualenv and pip reqs management (probably overkill).

To get the environment running:
```
pipenv install
pipenv install --dev
```

Then, to run:
```
pipenv run python ./run_game.py
```

## Building

```
pipenv run pyinstaller run_game.spec -y
```

There should now be an executable in the /dist/ folder


## Goals

This project is written in preparation for [Ludum Dare 44](https://ldjam.com/events/ludum-dare/44).

Since I always end up wasting too much time on this prep stuff and then giving up, I thought I'd start early this time.

*Key Features to Get Out of the way*

1. Scene Switcher (menu/level/pause/gameover/etc)
2. Resource Manager (data loading/unloading depending on the scene)
3. OpenGL 2D rendering (draw and batch images with x,y,z(?), size and rotation values under a movable, rotateable, zoomable camera)
4. Fix the stinking rendering bug where there is this one pixel black line on the left side of every image?
5. Z Depth, either by sorting or by figuring out a workaround for opengl alpha rendering ignoring z depth
6. Packaging/Distribution (looks like pyinstaller works on macos with a little tweaking)