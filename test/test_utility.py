import pytest
import sys
sys.path.append('src')
import constants
import utility
from enumeration import HallOfFame

def test_get_hof_emote():
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

def test_get_rank_by_page():
    page1 = utility.get_rank_by_page(1)
    assert(page1 == 10)
    page2 = utility.get_rank_by_page(2)
    assert(page2 == 20)
    page9 = utility.get_rank_by_page(9)
    assert(page9 == 90)
    
    page_neg2 = utility.get_rank_by_page(-2)
    assert(page_neg2 == -20)

def test_str_to_int():
    assert(utility.str_to_int(10) == 10)
    assert(utility.str_to_int(-20) == -20)
    assert(utility.str_to_int('test') == 1)
    assert(utility.str_to_int(13.2) == 13)
