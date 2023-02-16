import random
import asyncio
from .utils import check_for_level_up, generateNextBeaterText

async def beater_turn(beater, channel, a, b):
    response = await generateNextBeaterText("crit")
    roll = random.randint(1, 12) + beater["rank"]
    if (beater["injured"]):
        roll =- 1
    #1 should be crit fail, hit own team member
    #2 or 3 foul
    print("Roll: " + str(roll))
    #initial roll is 7
    if(roll == 1): #they are going to accidentally hit their own teammate
        min_roll = 12
        hit_player = -1
        for int in range(6):
            comparison_roll = random.randint(1, 12)
            if(min_roll > comparison_roll):
                min_roll = comparison_roll
                hit_player = int
        hit = list(team_rosters[a].items())[hit_player]
        if(channel != None):
            await channel.send("{b} has mistakenly directed the bludger at their own teammate, {h}".format(b=beater["name"], h=teamData[hit[1]]["name"]))
            if(teamData[hit[1]]["injured"] == True):
                print("Player was already injured")
                response = "{b} has knocked {h} out of the game! {a} will have to substitute"
                await channel.send(response.format(b=beater["name"], h=teamData[hit[1]]["name"], a=a))
                # response = await generateNextText("crit") #it appears as though this was the problem
        beater["xp"] -= 45
                
    elif(roll > 1 and roll <= 3):
        min_roll = 12
        
        foul_player = -1
        for int in range(6):
            comparison_roll = random.randint(1, 12)
            if(min_roll > comparison_roll):
                min_roll = comparison_roll
                foul_player = int
        foul = list(team_rosters[a].items())[foul_player]
        while("Seeker" in foul[0]): #seekers cannot commit fouls
            foul_player = -1
            for int in range(6):
                comparison_roll = random.randint(1, 12)
                if(min_roll > comparison_roll):
                    min_roll = comparison_roll
                    foul_player = int
            foul = list(team_rosters[a].items())[foul_player]
        text = ""
        action = ""
        if("Chaser" in foul[0]):
            text = await generateNextBeaterText("fouls", position="chaser")
            action = await generateNextBeaterText("fouls", position="moves")
        elif("Keeper" in foul[0]):
            text = await generateNextBeaterText("fouls", position="keeper")
        elif("Beater" in foul[0]):
            text = await generateNextBeaterText("fouls")
            action = await generateNextBeaterText("fouls", position="moves")
        print(text)
        await channel.send(text.format(name=foul[1], house=a, action=action, number=teamData[foul[1]]["jersey"]))
        scores[a] -= 10
        # raise NotImplementedError("Need to send text to the channel based on all of the previous prompts")
        # raise NotImplementedError("fix local variable 'action' referenced before assignment error")
    elif(roll>= 4 and roll < 8):
        #generate text
        text = await generateNextBeaterText("miss")
        print(text)
        min_roll = random.randint(1, 12)
        hit_player = 0
        for int in range(6):
            comparison_roll = random.randint(1, 12)
            if(min_roll > comparison_roll):
                min_roll = comparison_roll
                hit_player = int
        hit = list(team_rosters[b].items())[hit_player]
        if(channel != None):
            await channel.send(text.format(beater=beater["name"], opp_name=teamData[hit[1]]["name"], house=b, num=teamData[hit[1]]["jersey"]))
    elif(roll >= 8 or roll < 12):
        text = await generateNextBeaterText("minor")
        print(text)
        min_roll = random.randint(1, 12)
        hit_player = 0
        for int in range(6):
            comparison_roll = random.randint(1, 12)
            if(min_roll > comparison_roll):
                min_roll = comparison_roll
                hit_player = int
        hit = list(team_rosters[b].items())[hit_player]
        if(teamData[hit[1]]["injured"] == True):
            if(channel != None):
                await channel.send(beater["name"] + " hit " + str(teamData[hit[1]]["name"]) + " when they were they were already injured!")
                await channel.send(str(teamData[hit[1]]["name"]) + " was knocked unconscious and cannot play")
                beater["xp"] += 100
            teamData[hit[1]]["critically_injured"] = True
            if(channel != None):
                await channel.send("Need to substitute for the position " + str(hit[0]))
            team_rosters[b][hit[0]] = None
            while(team_rosters[b][hit[0]] == None):
                if(channel == None or b != "Gryffindor"):
                    print("Call search for sub")
                    await search_for_sub(b, hit)
                await asyncio.sleep(1)
        else:
            teamData[hit[1]]["injured"] = True
            if(channel != None):
                await channel.send(text.format(beater=beater["name"], opp_name=teamData[hit[1]]["name"], opp_pos=teamData[hit[1]]["position"]))
                await channel.send("{opp_name} is now injured and will roll with disadvantage".format(opp_name=teamData[hit[1]]["name"]))

        beater["xp"] += 50
        await check_for_level_up(beater, channel)
    elif(roll >= 12):
        min_roll = random.randint(1, 12)
        hit_player = 0
        for int in range(6):
            comparison_roll = random.randint(1, 12)
            if(min_roll > comparison_roll):
                min_roll = comparison_roll
                hit_player = int
        hit = list(team_rosters[b].items())[hit_player]
        if(channel != None):
            await channel.send(beater["name"] + " hit " + str(teamData[hit[1]]["name"]) + " and landed a critical hit!")
        beater["xp"] += 100
        await check_for_level_up(beater, channel)
        team_rosters[b][hit[0]] = None
        if (channel != None):
            await channel.send("Need to substitute for the position " + str(hit[0]))
        while(team_rosters[b][hit[0]] == None):
            if(channel != None or b != "Gryffindor"):
                await search_for_sub(b, hit)
            await asyncio.sleep(1)


async def run_round_headless(teamA, teamB, team_rosters, teamData):
    global team_A_rolls
    global team_B_rolls
    team_a = teamA
    team_b = teamB   
    global scores
    team_rolls = []
    for j in range(3):
        roll = random.randint(1, 12)
        team_rolls.append(roll)

    maxRoll = max(team_rolls)

    team_A_rolls = []
    team_B_rolls = []
    beater_rolls = []
    for int in range(2):
        beater_rolls.append(random.randint(0, maxRoll))
    for k in range(maxRoll):
        if(k % 3 == 0):
            chaser = team_rosters[team_a]["Chaser1"]
        elif(k % 3 == 1):
            chaser = team_rosters[team_a]["Chaser2"]
        else:
            chaser = team_rosters[team_a]["Chaser3"]

        r = (chaser, (random.randint(1, 12) + teamData[chaser]["rank"]))
        if(teamData[chaser]["injured"]):
            roll = r[1]
            r = (chaser, roll - 1)
        team_A_rolls.append(r)
        keeper = team_rosters[team_b]["Keeper"]
        team_B_rolls.append(random.randint(1, 12) + teamData[keeper]["rank"])

        if(teamData[keeper]["injured"]):
            print("keeper is injured")
            team_B_rolls[k] -= 1
            
    team_A_rolls.sort(reverse=True, key = lambda x: x[1])
    team_B_rolls.sort(reverse=True)

    #have to keep track of the index 
    for x in range(maxRoll):
        index_i = x
        if(beater_rolls[0] == x):
            print("beater turn")
            beater = teamData[team_rosters[team_a]["Beater1"]]
            await beater_turn(beater, None, team_a, team_b)

        if(beater_rolls[1] == x):
            beater = teamData[team_rosters[team_a]["Beater2"]]
            await beater_turn(beater, None, team_a, team_b)

        if (team_A_rolls[x][1] > team_B_rolls[x]):

            teamData[team_A_rolls[x][0]]["xp"] += 25
            await check_for_level_up(teamData[team_A_rolls[x][0]], None)
            scores[team_a] += 30
        elif(team_A_rolls[x][1] < team_B_rolls[x]):
            teamData[team_A_rolls[x][0]]["xp"] += 5
            keeper = team_rosters[team_b]["Keeper"]
            teamData[keeper]["xp"] += 10
            await check_for_level_up(teamData[team_A_rolls[x][0]], None)
            await check_for_level_up(teamData[keeper], None)
        else:
            continue
