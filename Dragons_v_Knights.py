import urllib.request
import json
import ast
import re
import operator

numBattles = 0
victory = 0
#request number of battles required
try:
    loop = int(input("Type the number of battles required: "))
except:
    print('Number required')
    loop = 0
	
#Log file created in current directory
f = open('Dragons_v_Knights_results.txt', 'w')

while loop > 0:
    #Fetch new game
    try:
        with urllib.request.urlopen('http://www.dragonsofmugloar.com/api/game') as response:
           game = ast.literal_eval(response.read().decode('utf8'))
    except:
        print('http://www.dragonsofmugloar.com/api/game not responding')
        f.write('http://www.dragonsofmugloar.com/api/game not responding')
        break
    
    gameID = str(game['gameId'])
    f.write("Game started: " + str(game) + '\n')


    #Fetch weather report
    try:
        with urllib.request.urlopen('http://www.dragonsofmugloar.com/weather/api/report/' + gameID) as response:
           weather = response.read().decode('utf8')
    except:
        print('http://www.dragonsofmugloar.com/weather/api/report/' + gameID + ' not responding')
        f.write('http://www.dragonsofmugloar.com/weather/api/report/' + gameID + ' not responding')
        break

    #Search weather report for code, assume normal weather for fog or failure to find code.  
    try:
        code = str(re.search('code>...</code', weather).group(0)[5:8])
    except AttributeError:
        code = 'NMR'

	#remove name and sort knight's attributes from highest to lowest in preparation for points distribution 
    game['knight'].pop('name', None)
    orderedKnight = sorted(game['knight'].items(), key=operator.itemgetter(1), reverse=True)

    compare = {
      	'attack' : 'scaleThickness',
    	'agility' : 'wingStrength',
    	'armor' : 'clawSharpness',
    	'endurance' : 'fireBreath'
    }
	
    #zen dragon as default
    dragon = {
    'scaleThickness' : 5,
    'clawSharpness' : 5,
    'wingStrength' : 5,
    'fireBreath' : 5
    }

    #distribute points based on weather
    if code == 'T E':
        #long summer, zen dragon, send as is
        pass
    elif code == 'HVA':
        #rain - no fire, extra sharp claws
        dragon = {
            'scaleThickness' : 5,
            'clawSharpness' : 10,
            'wingStrength' : 5,
            'fireBreath' : 0
    	}
    else:
        spareP = 0
        #largest stat, increase by two if possible
        if orderedKnight[0][1] + 2 > 10:
            dragon[compare[orderedKnight[0][0]]] = 10
            spareP += orderedKnight[0][1] - 8
        else:
            dragon[compare[orderedKnight[0][0]]] = orderedKnight[0][1] + 2
        #reduce next stat by 1
        dragon[compare[orderedKnight[1][0]]] = orderedKnight[1][1] - 1
        #reduce next stat by 1
        dragon[compare[orderedKnight[2][0]]] = orderedKnight[2][1] - 1
        #add any spare points to the lowest stat
        dragon[compare[orderedKnight[3][0]]] = orderedKnight[3][1] + spareP

    newConditions = {"dragon":dragon}		
    if code == 'SRO':
        #Storm, don't send the dragon
        newConditions = {}

    #Solve the current game
    conditionsSetURL = 'http://www.dragonsofmugloar.com/api/game/' + gameID + '/solution'
    params = json.dumps(newConditions).encode('utf8')
    try:
        req = urllib.request.Request(conditionsSetURL, data=params, headers={'content-type': 'application/json'}, method='PUT')
    except:
        print('http://www.dragonsofmugloar.com/api/game/' + gameID + '/solution' + ' not responding')
        f.write('http://www.dragonsofmugloar.com/api/game/' + gameID + '/solution' + ' not responding')
        break        

    response = urllib.request.urlopen(req)
    message = response.read().decode('utf8')
	
	#Determine percentage wins and update file with results
    try:
        result = str(re.search('Victory', message).group(0))
    except AttributeError:
        result = 'Defeat'	
    f.write("Dragon sent: " + str(dragon) + '\n')
    if (result == 'Victory'):
        victory += 1
        f.write(str(message) + '\n')
    else:
        f.write(str(message) + '\n')
    numBattles += 1
    f.write("Percentage wins: " + str((victory * 100)/numBattles) + '\n')
    f.write("Battle number: " + str(numBattles) + '\n')
    f.write("\n\n****************************************************************************************\n")
    loop -= 1
    print("Battle number " + str(numBattles) + " complete")
    
	

f.close()