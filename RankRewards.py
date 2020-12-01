from datetime import date

def give_rewards():
    print('checking')
    give_weekly = give_weekly_rewards()
    print(f'{give_weekly=}')
    give_monthly = give_monthly_rewards()
    print(f'{give_monthly=}')

# Returns true if should give out weekly rewards
def give_weekly_rewards():
    if date.today().weekday() == 0:
        return True
    else:
        return False

# Returns true if should give out monthly rewards
def give_monthly_rewards():
    return date.today().day == 1