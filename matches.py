import random
import asyncio
from utils import check_for_level_up, FlavorTextGenerator

class Match():
    def __init__(self, teamA, teamB, team_rosters, channel, flavorText, teamData):
        self.teamA = teamA
        self.teamB = teamB
        self.channel = channel
        self.flavorText = flavorText
        self.teamData = teamData
        self.team_rosters = team_rosters

    async def beater_turn(self, beater, channel, a, b):
        response = await self.flavorText.generateNextBeaterText("crit")
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
            hit = list(self.team_rosters[a].items())[hit_player]
            if(channel != None):
                await channel.send("{b} has mistakenly directed the bludger at their own teammate, {h}".format(b=beater["name"], h=teamData[hit[1]]["name"]))
                if(self.teamData[hit[1]]["injured"] == True):
                    print("Player was already injured")
                    response = "{b} has knocked {h} out of the game! {a} will have to substitute"
                    await channel.send(response.format(b=beater["name"], h=self.teamData[hit[1]]["name"], a=a))
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
            foul = list(self.team_rosters[a].items())[foul_player]
            while("Seeker" in foul[0]): #seekers cannot commit fouls
                foul_player = -1
                for int in range(6):
                    comparison_roll = random.randint(1, 12)
                    if(min_roll > comparison_roll):
                        min_roll = comparison_roll
                        foul_player = int
                foul = list(self.team_rosters[a].items())[foul_player]
            text = ""
            action = ""
            if("Chaser" in foul[0]):
                text = await self.generateNextBeaterText("fouls", position="chaser")
                action = await self.generateNextBeaterText("fouls", position="moves")
            elif("Keeper" in foul[0]):
                text = await self.generateNextBeaterText("fouls", position="keeper")
            elif("Beater" in foul[0]):
                text = await self.generateNextBeaterText("fouls")
                action = await self.generateNextBeaterText("fouls", position="moves")
            print(text)
            await channel.send(text.format(name=foul[1], house=a, action=action, number=self.teamData[foul[1]]["jersey"]))
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

    async def run_round(a, b, channel, team_rosters, teamData, flavorGen, init=False):
        # global control_sequence
        # global team_A_rolls
        # global team_B_rolls
        # global index_i
        # global team_rerolls
        # global team_a
        # global team_b
        # global quaffle_possession
        # global prev_possession
        quaffle_possession = "" #keeps track of who has the quaffle
        prev_possession = ""
        last_roll_success = False #keeps track of whether the last roll was a success or not (used for flavor text)
        team_a = a
        team_b = b
        team_rerolls = 3
        control_sequence = False
        team_rolls = []
        for j in range(3):
            roll = random.randint(1, 12)
            team_rolls.append(roll)

        maxRoll = max(team_rolls)
        team_A_rolls = []
        team_B_rolls = []
        beater_rolls = []
        for int in range(2):
            beater_rolls.append(random.randint(0, maxRoll-1))

        for k in range(maxRoll):
            r = ()
            if(k % 3 == 0):
                chaser = team_rosters[a]["Chaser1"]
            elif(k % 3 == 1):
                chaser = team_rosters[a]["Chaser2"]
            else:
                chaser = team_rosters[a]["Chaser3"]
            r = (chaser, (random.randint(1, 12) + teamData[chaser]["rank"]))
            if(teamData[chaser]["injured"]):
                roll = r[1]
                r = (chaser, roll - 1)

            team_A_rolls.append(r)
            keeper = team_rosters[b]["Keeper"]
            team_B_rolls.append(random.randint(1, 12) + teamData[keeper]["rank"])

            if(teamData[keeper]["injured"]):
                team_B_rolls[k] -= 1
                
        team_A_rolls.sort(reverse=True, key = lambda x: x[1])
        team_B_rolls.sort(reverse=True)
        #have to keep track of the index
        if(init):
            print("init")
            await channel.send("{chaser} has caught the Quaffle! {house} starts the game".format(chaser = teamData[team_A_rolls[0][0]]["name"], house=a))
            quaffle_possession = team_A_rolls[0][0]
            prev_possession = team_A_rolls[0][0]
        else:
            quaffle_possession = team_A_rolls[0][0]
        successes = 0
        misses = 0
        for x in range(maxRoll):
            index_i = x
            offensiveMove = await flavorGen.generateNextMove("offensive")
            if(beater_rolls[0] == x):
                print("Beater 1 turn")
                beater = teamData[team_rosters[a]["Beater1"]]
                await beater_turn(beater, channel, a, b)

            if(beater_rolls[1] == x):
                print("Beater 2 turn")
                beater = teamData[team_rosters[a]["Beater2"]]
                await beater_turn(beater, channel, a, b)

            if (team_A_rolls[x][1] > team_B_rolls[x]):
                print("success")
                teamData[team_A_rolls[x][0]]["xp"] += 25
                keeper = team_rosters[b]["Keeper"]
                if(quaffle_possession == team_A_rolls[x][0]): #same
                    same = await flavorGen.generateNextText("same")
                    print(same)
                    counter = await flavorGen.generateNextMove("counter")
                    #there should be a distinct move name for this
                    #also if this happens more than once, then stop it
                    #there should be a roll for "interception"
                    await channel.send("{chaser} {action} {opposing} with a {counter} and scores a goal using a {offensive} to get past {keeper}".format(chaser=teamData[team_A_rolls[x][0]]["name"], 
                    action=same, opposing=b, counter=counter, offensive=offensiveMove, keeper=teamData[keeper]["name"]))
                    
                else:
                    different = await flavorGen.generateNextText("different")
                    counter = await flavorGen.generateNextMove("counter")
                    string = "{q} {dif} with a {counter}, passing the Quaffle to {r} who scores a goal with a {offensive}"
                    await channel.send(string.format(q=teamData[quaffle_possession]["name"], dif=different, counter=counter, r=teamData[team_A_rolls[x][0]]["name"], offensive=offensiveMove))
                await check_for_level_up(teamData[team_A_rolls[x][0]], channel)
                scores[team_a] += 30
                successes += 1
                quaffle_possession = team_A_rolls[x][0]
            elif(team_A_rolls[x][1] < team_B_rolls[x]):
                print("miss")
                teamData[team_A_rolls[x][0]]["xp"] += 5
                keeper = team_rosters[b]["Keeper"]
                textType = "non-final"
                if(x == maxRoll-1):
                    textType = "final"
                response = await flavorGen.generateNextMissText(textType)
                print(response)
                teamData[keeper]["xp"] += 10
                misses += 1
                string = "{keeper} {response} {chaser}'s {offensive}. Possession returns to {other}."
                await channel.send(string.format(keeper = teamData[keeper]["name"], response = response, chaser = teamData[team_A_rolls[x][0]]["name"], offensive = offensiveMove, other=a))
                await check_for_level_up(teamData[team_A_rolls[x][0]], channel)
                await check_for_level_up(teamData[keeper], channel)
            else:
                continue
            await channel.send("Type 'continue' to continue")
            while(control_sequence == False):
                await asyncio.sleep(1)
            control_sequence = False
        finalMove = await flavorGen.generateNextMissText("final")
        flavor = await flavorGen.generateNextMissText("sf")
        string = "{keeper} catches {quaffle}'s attack, {final} the {off} {f}"
        await channel.send(string.format(keeper = teamData[team_rosters[b]["Keeper"]]["name"], quaffle = teamData[quaffle_possession]["name"], final=finalMove, off=a, f=flavor))
        score = "{teamA} scores {success} goals and {teamB} blocks {miss} goals. The total score thus far is {teamA}: {scoreA}, {teamB}: {scoreB}"
        await channel.send(score.format(teamA=a, success=successes, teamB = b, miss = misses, scoreA = scores[team_a], scoreB = scores[team_b]))

    async def start_match(channel, teamA, teamB, team_rosters, teamData, flavorText):
        gen = FlavorTextGenerator(flavorText)
        A = random.randint(1, 20)
        B = random.randint(1, 20)
        num_rounds = random.randint(1, 12)
        scores = {}
        scores[teamA] = 0
        scores[teamB] = 0
        first_team = ""
        second_team = ""
        coin = random.randint(0, 1)
        if(coin == 0):
            await channel.send(teamA + " will be on the offensive first")
            first_team = teamA
            second_team = teamB
        else:
            await channel.send(teamB + " will be on the offensive first")
            first_team = teamB
            second_team = teamA
        await run_round(first_team, second_team, channel, team_rosters, teamData, gen, init=True)
        await channel.send("Type 'continue' to continue")
        while(control_sequence == False):
            await asyncio.sleep(1)
        await channel.send("Possession has turned over to " + str(second_team))
        await run_round(second_team, first_team, channel)
        await channel.send("Type 'continue' to continue")
        while(control_sequence == False):
            await asyncio.sleep(1)
        for i in range(1, 1):
            await channel.send("The {house} team now has control of the Quaffle".format(house=first_team))
            await run_round(first_team, second_team, channel)
            await channel.send("Possession has turned over to {house}".format(house=second_team))
            await channel.send("Type 'continue' to continue")
            while(control_sequence == False):
                await asyncio.sleep(1)
            await run_round(second_team, first_team, channel)
        teamA_rolls = 0
        teamB_rolls = 0 
        for j in range(3):
            teamA_rolls += random.randint(1, 6)
            teamB_rolls += random.randint(1, 6)
        teamA_rolls += teamData[team_rosters[first_team]["Seeker"]]["rank"]
        teamB_rolls += teamData[team_rosters[second_team]["Seeker"]]["rank"]
        while (teamA_rolls == teamB_rolls):
            for j in range(3):
                teamA_rolls += random.randint(1, 6)
                teamB_rolls += random.randint(1, 6)
            teamA_rolls += teamData[team_rosters[first_team]["Seeker"]]["rank"]
            teamB_rolls += teamData[team_rosters[second_team]["Seeker"]]["rank"]
        
        if(teamData[team_rosters[first_team]["Seeker"]]["injured"]):
            teamA_rolls -= 1
        if(teamData[team_rosters[second_team]["Seeker"]]["injured"]):
            teamB_rolls -= 1

        teamData[team_rosters[first_team]["Seeker"]]["xp"] += (teamA_rolls * 10)
        teamData[team_rosters[second_team]["Seeker"]]["xp"] += (teamB_rolls * 10)
        if(teamA_rolls > teamB_rolls):
            scores[teamA] += 150
            seeker = teamData[team_rosters[teamA]["Seeker"]]
        else:
            scores[teamB] += 150
            seeker = teamData[team_rosters[teamB]["Seeker"]]

        print(seeker)
        seeker["xp"] += 150
        await channel.send("{sk} has caught the Snitch! Ending the game after {r} rounds!".format(sk=seeker["name"], r=num_rounds))
        await check_for_level_up(teamData[team_rosters[first_team]["Seeker"]], channel)
        await check_for_level_up(teamData[team_rosters[second_team]["Seeker"]], channel)
        final_score = "The match has officially ended. {a} has scored {a_score} points. {b} has scored {b_score} points. "
        if(scores[teamA] > scores[teamB]):
            final_score += "{a} wins the match!"
        elif(scores[teamB] > scores[teamA]):
            final_score += "{b} wins the match!"
        else:
            await channel.send("The score is a tie, so " + second_team + " wins!")
        #need to verify that this actually prints out what it's supposed to
        await channel.send(final_score.format(a=teamA, a_score=scores[teamA], b=teamB, b_score=scores[teamB]))
        gameStarted = False
        await clean_up()