# returns true if the user is an admin. False otherwise
def is_admin(author, settings):
    if type(author) == str:
        return author in settings.admin
    else:
        return str(author) in settings.admin

def str_to_int(value):
    try:
        return int(value)
    except:
        return 1