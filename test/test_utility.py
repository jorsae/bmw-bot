import pytest
import sys
sys.path.append('src')
import utility
from enumeration import HallOfFame

def get_hof_emote_test():
    catches = utility.get_hof_emote(HallOfFame.catches)
    assert(catches) == '<:HofCatches:779248403502202901>'
    
    legendary = utility.get_hof_emote(HallOfFame.legendary)
    assert(legendary) == '<:HofLegendary:779249178525564947>'
    
    mythical = utility.get_hof_emote(HallOfFame.mythical)
    assert(mythical) == '<:HofMythical:779248236892258307>'
    
    ultrabeast = utility.get_hof_emote(HallOfFame.ultrabeast)
    assert(ultrabeast) == '<:HofUltrabeast:779247337977413642>'
    
    shiny = utility.get_hof_emote(HallOfFame.shiny)
    assert(shiny) == '<:HofShiny:779250293849587743>'