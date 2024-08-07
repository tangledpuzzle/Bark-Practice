import fire
from commands import Commands


def run():
    commands = Commands()
    try:
        fire.Fire(commands)
    except Exception as e:
        print(e)
