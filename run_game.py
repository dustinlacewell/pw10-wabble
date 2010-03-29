import cProfile

from src.main import run

cProfile.run('run()', 'profile.txt')