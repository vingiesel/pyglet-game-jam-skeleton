
def run():
    from game.engine.manager import game_window
    from game.scenes.game import Game

    game_window.change_scene(Game)

    game_window.run()