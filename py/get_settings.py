def characteristic():
    with open('settings\characteristic_settings.txt', 'r', encoding='utf-8') as setting:
        dictionary = dict()
        for i in setting.readlines():
            if i != '\n':
                i = i.split(':', 1)
                dictionary[i[0]] = dict([u.strip().split(': ') for u in i[1].split(', ')])
        
        exceptions = ['filename', 'bullet_filename', 'engine_filename', 'idle_filename', 'powering_filename', 'shield_filename', 'fire_filename', 'death_filename']
        spaceships = ['player_spaceship1']

        for key in dictionary.keys():
            for key1 in dictionary[key].keys():
                if key1 == 'filename' and key in spaceships:
                    dictionary[key][key1] = dictionary[key][key1].split(';')
                
                elif key1 == 'turn_angle':
                    dictionary[key][key1] = float(dictionary[key][key1])
                    
                elif key1 not in exceptions:
                    dictionary[key][key1] = int(dictionary[key][key1])

    return dictionary

def create_player_ship():
    with open('settings\current_player_settings.txt', 'r', encoding='utf-8') as setting:
        return [i.strip() for i in setting.readlines()]
    
def enemy_placement(filename):
    with open('levels\\' + filename, 'r', encoding='utf-8') as settings:
        return [[u.split('|') for u in i.strip().split('\n')] for i in ''.join(settings.readlines()).split('---\n')]
