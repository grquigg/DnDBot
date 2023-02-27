import random

async def check_for_level_up(player, channel):
    if(player["xp"] > 100 and player["rank"] < 1):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 1!")
        player["rank"] = 1
    elif(player["xp"] > 250 and player["rank"] < 2):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 2!")
        player["rank"] = 2
    elif(player["xp"] > 450 and player["rank"] < 3):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 3!")
        player["rank"] = 3
    elif(player["xp"] > 700 and player["rank"] < 4):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 4!")
        player["rank"] = 4
    elif(player["xp"] > 1000 and player["rank"] < 5):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 5!")
        player["rank"] = 5
    elif(player["xp"] > 1400 and player["rank"] < 6):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 6!")
        player["rank"] = 6

class FlavorTextGenerator():
    def __init__(self, flavorText=None):
        self.flavorText = flavorText

    async def generateNextText(self, textType):
        index = random.randint(0, len(self.flavorText["hits"][textType])-1)
        return self.flavorText["hits"][textType][index]

    async def generateNextMissText(self, textType):
        index = random.randint(0, len(self.flavorText["misses"][textType])-1)
        return self.flavorText["misses"][textType][index]

    async def generateNextBeaterText(self, textType, position="beater"):
        if(textType == "fouls"):
            index = random.randint(0, len(self.flavorText["fouls"][position])-1)
            return self.flavorText[textType][position][index]
        index = random.randint(0, len(self.flavorText[textType])-1)
        return self.flavorText[textType][index]

    async def generateNextMove(self, moveType):
        index = random.randint(0, len(self.flavorText["moves"][moveType])-1)
        return self.flavorText["moves"][moveType][index]
    
    async def generateNextActionText(self):
        index = random.randint(0, len(self.flavorText["fouls"]["moves"]))
        return self.flavorText["fouls"]["moves"][index]