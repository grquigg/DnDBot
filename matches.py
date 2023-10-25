import random
import asyncio
from utils import check_for_level_up, FlavorTextGenerator

class Match():
    def __init__(self, teamA, teamB, team_rosters, channel, flavorText, teamData, headless=False):
        self.teamA = teamA
        self.teamB = teamB
        self.channel = channel
        self.gen = flavorText
        self.teamData = teamData #the full list of all players in the data and their stats
        self.team_rosters = team_rosters #the current rosters for each team
        self.gen = FlavorTextGenerator(self.gen)
        self.headless = headless
        self.paused = False
        self.scores = {teamA: 0, teamB: 0}

    async def beater_turn(self, beater, channel, a, b):
        response = await self.gen.generateNextBeaterText("crit")
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
                await channel.send("{b} has mistakenly directed the bludger at their own teammate, {h}".format(b=beater["name"], h=self.teamData[hit[1]]["name"]))
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
                text = await self.gen.generateNextBeaterText("fouls", position="chaser")
                action = await self.gen.generateNextBeaterText("fouls", position="moves")
            elif("Keeper" in foul[0]):
                text = await self.gen.generateNextBeaterText("fouls", position="keeper")
            elif("Beater" in foul[0]):
                text = await self.gen.generateNextBeaterText("fouls")
                action = await self.gen.generateNextBeaterText("fouls", position="moves")
            print(text)
            await channel.send(text.format(name=foul[1], house=a, action=action, number=self.teamData[foul[1]]["jersey"]))
            scores[a] -= 10
            # raise NotImplementedError("Need to send text to the channel based on all of the previous prompts")
            # raise NotImplementedError("fix local variable 'action' referenced before assignment error")
        elif(roll>= 4 and roll < 8):
            #generate text
            text = await self.gen.generateNextBeaterText("miss")
            print(text)
            min_roll = random.randint(1, 12)
            hit_player = 0
            for int in range(6):
                comparison_roll = random.randint(1, 12)
                if(min_roll > comparison_roll):
                    min_roll = comparison_roll
                    hit_player = int
            hit = list(self.team_rosters[b].items())[hit_player]
            if(channel != None):
                await channel.send(text.format(beater=beater["name"], opp_name=self.teamData[hit[1]]["name"], house=b, num=self.teamData[hit[1]]["jersey"]))
        elif(roll >= 8 or roll < 12):
            text = await self.gen.generateNextBeaterText("minor")
            print(text)
            min_roll = random.randint(1, 12)
            hit_player = 0
            for int in range(6):
                comparison_roll = random.randint(1, 12)
                if(min_roll > comparison_roll):
                    min_roll = comparison_roll
                    hit_player = int
            hit = list(self.team_rosters[b].items())[hit_player]
            if(self.teamData[hit[1]]["injured"] == True):
                if(channel != None):
                    await channel.send(beater["name"] + " hit " + str(self.teamData[hit[1]]["name"]) + " when they were they were already injured!")
                    await channel.send(str(self.teamData[hit[1]]["name"]) + " was knocked unconscious and cannot play")
                    beater["xp"] += 100
                self.teamData[hit[1]]["critically_injured"] = True
                if(channel != None):
                    await channel.send("Need to substitute for the position " + str(hit[0]))
                self.team_rosters[b][hit[0]] = None
                while(self.team_rosters[b][hit[0]] == None):
                    if(channel == None or b != "Gryffindor"):
                        print("Call search for sub")
                        await search_for_sub(b, hit)
                    await asyncio.sleep(1)
            else:
                self.teamData[hit[1]]["injured"] = True
                if(channel != None):
                    await channel.send(text.format(beater=beater["name"], opp_name=self.teamData[hit[1]]["name"], opp_pos=self.teamData[hit[1]]["position"]))
                    await channel.send("{opp_name} is now injured and will roll with disadvantage".format(opp_name=self.teamData[hit[1]]["name"]))

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
            hit = list(self.team_rosters[b].items())[hit_player]
            if(channel != None):
                await channel.send(beater["name"] + " hit " + str(self.teamData[hit[1]]["name"]) + " and landed a critical hit!")
            beater["xp"] += 100
            await check_for_level_up(beater, channel)
            self.team_rosters[b][hit[0]] = None
            if (channel != None):
                await channel.send("Need to substitute for the position " + str(hit[0]))
            while(self.team_rosters[b][hit[0]] == None):
                if(channel != None or b != "Gryffindor"):
                    await search_for_sub(b, hit)
                await asyncio.sleep(1)

    async def reroll(self, channel, index_i):
        global team_rerolls
        global score
        if(team_rerolls > 0):
            player = team_A_rolls[index_i][0]
            rerollA = random.randint(1, 12) + self.teamData[player]["rank"]
            if(self.teamData[player]["injured"]):
                rerollA -= 1
            rerollB = random.randint(1, 12) + self.teamData[self.team_rosters[self.team_b]["Keeper"]]["rank"]
            if(self.teamData[self.team_rosters[self.team_b]["Keeper"]]):
                rerollB -= 1
            team_A_rolls[index_i] = (player, rerollA + team_A_rolls[index_i][1])
            team_B_rolls[index_i] = team_B_rolls[index_i] + rerollB
            if (team_A_rolls[index_i][1] > team_B_rolls[index_i]):
                self.teamData[team_A_rolls[index_i][0]]["xp"] += 25
                await channel.send(self.teamData[team_A_rolls[index_i][0]]["name"] + " has scored a goal")
                await check_for_level_up(self.teamData[team_A_rolls[index_i][0]], channel)
                scores[team_a] += 30
            elif(team_A_rolls[index_i][1] < team_B_rolls[index_i]):
                if(team_B_rolls[index_i] - team_A_rolls[index_i][1] <= 2):
                    await channel.send(self.teamData[team_A_rolls[index_i][0]]["name"] + " almost managed to score a goal but " + teamData[team_rosters[team_b]["Keeper"]]["name"] + " blocked it at the last second!")
                else:
                    await channel.send(self.teamData[self.team_rosters[team_b]["Keeper"]]["name"] + " has blocked " + teamData[team_A_rolls[index_i][0]]["name"] + " from scoring")
                self.teamData[team_A_rolls[index_i][0]]["xp"] += 5
                keeper = self.team_rosters[self.team_b]["Keeper"]
                self.teamData[keeper]["xp"] += 10
                await check_for_level_up(self.teamData[team_A_rolls[index_i][0]], channel)
                await check_for_level_up(self.teamData[keeper], channel)
            team_rerolls -= 1
            await channel.send(str(team_rerolls) + " rerolls left")
            await channel.send("Type 'continue' to continue")
        else:
            await channel.send("No more rerolls left")

    async def start_match(self):
        print("Start match")
        A = random.randint(1, 20)
        B = random.randint(1, 20)
        num_rounds = random.randint(1, 12)
        scores = {}
        scores[self.teamA] = 0
        scores[self.teamB] = 0
        first_team = ""
        second_team = ""
        #flip a "coin" to determine which team goes first
        coin = random.randint(0, 1)
        if(coin == 0):
            await self.channel.send(self.teamA + " will be on the offensive first")
            first_team = self.teamA
            second_team = self.teamB
        else:
            await self.channel.send(self.teamB + " will be on the offensive first")
            first_team = self.teamB
            second_team = self.teamA

        await self.run_round(first_team, second_team, init=True)
        await self.channel.send("Type 'continue' to continue")
        while(self.paused):
            await asyncio.sleep(1)
        await self.channel.send("Possession has turned over to " + str(second_team))
        await self.run_round(second_team, first_team)
        await self.channel.send("Type 'continue' to continue")
        while(self.paused):
            await asyncio.sleep(1)
        for i in range(1, 1):
            await self.channel.send("The {house} team now has control of the Quaffle".format(house=first_team))
            await self.run_round(first_team, second_team)
            await self.channel.send("Possession has turned over to {house}".format(house=second_team))
            await self.channel.send("Type 'continue' to continue")
            while(self.paused):
                await asyncio.sleep(1)
            await self.run_round(second_team, first_team)
        #rolls for determining who catches the snitch at the end of a match
        teamA_rolls = 0
        teamB_rolls = 0 
        for j in range(3):
            teamA_rolls += random.randint(1, 6)
            teamB_rolls += random.randint(1, 6)
        teamA_rolls += self.teamData[self.team_rosters[first_team]["Seeker"]]["rank"]
        teamB_rolls += self.teamData[self.team_rosters[second_team]["Seeker"]]["rank"]
        while (teamA_rolls == teamB_rolls):
            for j in range(3):
                teamA_rolls += random.randint(1, 6)
                teamB_rolls += random.randint(1, 6)
            teamA_rolls += self.teamData[self.team_rosters[first_team]["Seeker"]]["rank"]
            teamB_rolls += self.teamData[self.team_rosters[second_team]["Seeker"]]["rank"]
        
        if(self.teamData[self.team_rosters[first_team]["Seeker"]]["injured"]):
            teamA_rolls -= 1
        if(self.teamData[self.team_rosters[second_team]["Seeker"]]["injured"]):
            teamB_rolls -= 1

        self.teamData[self.team_rosters[first_team]["Seeker"]]["xp"] += (teamA_rolls * 10)
        self.teamData[self.team_rosters[second_team]["Seeker"]]["xp"] += (teamB_rolls * 10)
        if(teamA_rolls > teamB_rolls):
            scores[self.teamA] += 150
            seeker = self.teamData[self.team_rosters[self.teamA]["Seeker"]]
        else:
            scores[self.teamB] += 150
            seeker = self.teamData[self.team_rosters[self.teamB]["Seeker"]]

        seeker["xp"] += 150
        await self.channel.send("{sk} has caught the Snitch! Ending the game after {r} rounds!".format(sk=seeker["name"], r=num_rounds))
        await check_for_level_up(self.teamData[self.team_rosters[first_team]["Seeker"]], self.channel)
        await check_for_level_up(self.teamData[self.team_rosters[second_team]["Seeker"]], self.channel)
        final_score = "The match has officially ended. {a} has scored {a_score} points. {b} has scored {b_score} points. "
        if(scores[self.teamA] > scores[self.teamB]):
            final_score += "{a} wins the match!"
        elif(scores[self.teamB] > scores[self.teamA]):
            final_score += "{b} wins the match!"
        else:
            await self.channel.send("The score is a tie, so " + second_team + " wins!")
        #need to verify that this actually prints out what it's supposed to
        await self.channel.send(final_score.format(a=self.teamA, a_score=scores[self.teamA], b=self.teamB, b_score=scores[self.teamB]))
        gameStarted = False
        await self.clean_up()

    async def start_match_headless(self):
        A = random.randint(1, 20)
        B = random.randint(1, 20)
        num_rounds = random.randint(1, 12)
        scores = {}
        scores[self.teamA] = 0
        scores[self.teamB] = 0
        first_team = ""
        second_team = ""
        coin = random.randint(0, 1)
        if(coin == 0):
            first_team = self.teamA
            second_team = self.teamB
        else:
            first_team = self.teamB
            second_team = self.teamA
        for i in range(num_rounds):
            await self.run_round_headless(first_team, second_team)
            await self.run_round_headless(second_team, first_team)
        teamA_rolls = 0
        teamB_rolls = 0 
        for j in range(3):
            teamA_rolls += random.randint(1, 6)
            teamB_rolls += random.randint(1, 6)
        teamA_rolls += self.teamData[self.team_rosters[first_team]["Seeker"]]["rank"]
        teamB_rolls += self.teamData[self.team_rosters[second_team]["Seeker"]]["rank"]

        if(self.teamData[self.team_rosters[first_team]["Seeker"]]["injured"]):
            teamA_rolls -= 1
        if(self.teamData[self.team_rosters[second_team]["Seeker"]]["injured"]):
            teamB_rolls -= 1

        self.teamData[self.team_rosters[first_team]["Seeker"]]["xp"] += (teamA_rolls * 10)
        self.teamData[self.team_rosters[second_team]["Seeker"]]["xp"] += (teamB_rolls * 10)
        
        if(teamA_rolls > teamB_rolls):
            scores[self.teamA] += 150
            seeker = self.teamData[self.team_rosters[first_team]["Seeker"]]["name"]
            self.teamData[self.team_rosters[first_team]["Seeker"]]["xp"] += 150
        elif (teamB_rolls > teamA_rolls):
            scores[self.teamB] += 150
            seeker = self.teamData[self.team_rosters[second_team]["Seeker"]]["name"]
            self.teamData[self.team_rosters[second_team]["Seeker"]]["xp"] += 150
        if(scores[self.teamA] > scores[self.teamB]):
            await self.channel.send(first_team + " wins!")
        elif(scores[self.teamB] > scores[self.teamA]):
            await self.channel.send(second_team + " wins!")
        else:
            await self.channel.send("The score is a tie, so " + second_team + " wins!")
        await self.channel.send("Score is " + str(first_team) + ": " + str(scores[self.teamA]) + ", " + str(second_team) + ": " + str(scores[self.teamB]))
        gameStarted = False
        await self.clean_up()

    async def run_round_headless(self, teamA, teamB, team_rosters, teamData):
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
                await self.beater_turn(beater, None, team_a, team_b)

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

    def isHeadless(self):
        return self.headless
    
    async def unpause(self):
        print("Unpause")
        self.paused = not self.paused

    async def run_round(self, a, b, init=False):
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
            val = (k % 3) + 1
            chaser = self.team_rosters[a]["Chaser{}".format(val)]
            r = (chaser, (random.randint(1, 12) + self.teamData[chaser]["rank"]))
            if(self.teamData[chaser]["injured"]):
                roll = r[1]
                r = (chaser, roll - 1)

            team_A_rolls.append(r)
            keeper = self.team_rosters[b]["Keeper"]
            team_B_rolls.append(random.randint(1, 12) + self.teamData[keeper]["rank"])

            if(self.teamData[keeper]["injured"]):
                team_B_rolls[k] -= 1
                
        team_A_rolls.sort(reverse=True, key = lambda x: x[1])
        team_B_rolls.sort(reverse=True)
        #have to keep track of the index
        if(init):
            print("init")
            await self.channel.send("{chaser} has caught the Quaffle! {house} starts the game".format(chaser = self.teamData[team_A_rolls[0][0]]["name"], house=a))
            quaffle_possession = team_A_rolls[0][0]
            prev_possession = team_A_rolls[0][0]
        else:
            quaffle_possession = team_A_rolls[0][0]
        successes = 0
        misses = 0
        for x in range(maxRoll):
            index_i = x
            offensiveMove = await self.gen.generateNextMove("offensive")
            if(beater_rolls[0] == x):
                print("Beater 1 turn")
                beater = self.teamData[self.team_rosters[a]["Beater1"]]
                await self.beater_turn(beater, self.channel, a, b)

            if(beater_rolls[1] == x):
                print("Beater 2 turn")
                beater = self.teamData[self.team_rosters[a]["Beater2"]]
                await self.beater_turn(beater, self.channel, a, b)

            if (team_A_rolls[x][1] > team_B_rolls[x]):
                print("success")
                self.teamData[team_A_rolls[x][0]]["xp"] += 25
                keeper = self.team_rosters[b]["Keeper"]
                if(quaffle_possession == team_A_rolls[x][0]): #same
                    same = await self.gen.generateNextText("same")
                    print(same)
                    counter = await self.gen.generateNextMove("counter")
                    #there should be a distinct move name for this
                    #also if this happens more than once, then stop it
                    #there should be a roll for "interception"
                    await self.channel.send("{chaser} {action} {opposing} with a {counter} and scores a goal using a {offensive} to get past {keeper}".format(chaser=self.teamData[team_A_rolls[x][0]]["name"], 
                    action=same, opposing=b, counter=counter, offensive=offensiveMove, keeper=self.teamData[keeper]["name"]))
                    
                else:
                    different = await self.gen.generateNextText("different")
                    counter = await self.gen.generateNextMove("counter")
                    string = "{q} {dif} with a {counter}, passing the Quaffle to {r} who scores a goal with a {offensive}"
                    await self.channel.send(string.format(q=self.teamData[quaffle_possession]["name"], dif=different, counter=counter, r=self.teamData[team_A_rolls[x][0]]["name"], offensive=offensiveMove))
                await check_for_level_up(self.teamData[team_A_rolls[x][0]], self.channel)
                self.scores[team_a] += 30
                successes += 1
                quaffle_possession = team_A_rolls[x][0]
            elif(team_A_rolls[x][1] < team_B_rolls[x]):
                print("miss")
                self.teamData[team_A_rolls[x][0]]["xp"] += 5
                keeper = self.team_rosters[b]["Keeper"]
                textType = "non-final"
                if(x == maxRoll-1):
                    textType = "final"
                response = await self.gen.generateNextMissText(textType)
                print(response)
                self.teamData[keeper]["xp"] += 10
                misses += 1
                string = "{keeper} {response} {chaser}'s {offensive}. Possession returns to {other}."
                await self.channel.send(string.format(keeper = self.teamData[keeper]["name"], response = response, chaser = self.teamData[team_A_rolls[x][0]]["name"], offensive = offensiveMove, other=a))
                await check_for_level_up(self.teamData[team_A_rolls[x][0]], self.channel)
                await check_for_level_up(self.teamData[keeper], self.channel)
            else:
                continue
            await self.channel.send("Type 'continue' to continue")
            self.paused = True
            while(self.paused):
                await asyncio.sleep(1)
        finalMove = await self.gen.generateNextMissText("final")
        flavor = await self.gen.generateNextMissText("sf")
        string = "{keeper} catches {quaffle}'s attack, {final} the {off} {f}"
        await self.channel.send(string.format(keeper = self.teamData[self.team_rosters[b]["Keeper"]]["name"], quaffle = self.teamData[quaffle_possession]["name"], final=finalMove, off=a, f=flavor))
        score = "{teamA} scores {success} goals and {teamB} blocks {miss} goals. The total score thus far is {teamA}: {scoreA}, {teamB}: {scoreB}"
        await self.channel.send(score.format(teamA=a, success=successes, teamB = b, miss = misses, scoreA = self.scores[team_a], scoreB = self.scores[team_b]))