def characteristic():
    with open('settings\characteristic_settings.txt', 'r', encoding='utf-8') as setting:
        dictionary = dict()
        for i in setting.readlines():
            i = i.split(':', 1)
            dictionary[i[0]] = dict([u.strip().split(': ') for u in i[1].split(', ')])
        
        for key in dictionary.keys():
            for key1 in dictionary[key].keys():
                if key1 == 'filename':
                    dictionary[key][key1] = dictionary[key][key1].split(';')
                elif key1 != 'class':
                    dictionary[key][key1] = int(dictionary[key][key1])
    return dictionary

def made_spaceship():
    with open('settings\spaceship_settings.txt', 'r', encoding='utf-8') as setting:
        return [i.strip() for i in setting.readlines()]

