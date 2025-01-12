def characteristic():
    with open('settings\characteristic_settings.txt', 'r', encoding='utf-8') as setting:
        dictionary = dict()
        for i in setting.readlines():
            if i != '\n':
                i = i.split(':', 1)
                dictionary[i[0]] = dict([u.strip().split(': ') for u in i[1].split(', ')])
        
        exceptions = ['filename', 'bullet_filename', 'engine_filename', 'idle_filename', 'powering_filename', 'shield_filename']
        spaceships = ['player_spaceship1']

        for key in dictionary.keys():
            for key1 in dictionary[key].keys():
                if key1 == 'filename' and key in spaceships:
                    dictionary[key][key1] = dictionary[key][key1].split(';')
                elif key1 not in exceptions:
                    dictionary[key][key1] = int(dictionary[key][key1])
    return dictionary

def create_lvl():
    with open('settings\lvl_settings.txt', 'r', encoding='utf-8') as setting:
        return [i.strip() for i in setting.readlines()]
    


