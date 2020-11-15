import re
GET_USER = re.compile('@!?\d{18}')

a = 'congratulations <@!300744899563618306>! you caught a level 27 gastly!'
b = 'congratulations <@300744899563618306>! you caught a level 27 gastly!'

print(GET_USER.search(a))
print(GET_USER.search(b))