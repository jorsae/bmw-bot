import pytest
import sys
sys.path.append('src')
import utility
from enumeration import HallOfFame

def get_hof_emote_test():
    catches = utility.get_hof_emote(HallOfFame.catches)
    assert('<:HofCatches:779248403502202901>' == catches)