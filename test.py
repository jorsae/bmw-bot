import re
GET_USER = re.compile('@!?\d{17,18}')

a = '<@!89452245153779712>! '
b = 'congratulations <@300744899563618306>! you caught a level 27 gastly!'

print(GET_USER.search(a))
print(GET_USER.search(b))