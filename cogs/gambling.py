import discord
from discord.ext import commands
import random
import sys
from consts import *
from cogs.economy import changeBalance, getBalance

class GamblingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="flipmoons", aliases=["flip"])
    async def coinFlip(self, ctx, amt:int, bet:str):
        data = getData(MOONS_DATA)
        user = ctx.author.id
        if bet not in COIN_FACES:
            return
        if bet == "h":
            bet = "heads"
        elif bet == "t":
            bet = "tails"

        userData = data.get(str(user))
        if userData == None or int(userData.get("moons")) == 0:
            return

        currentMoons = data.get(str(user)).get("moons")
        if currentMoons < amt:
            return

        flip = random.choice(HEADS_OR_TAILS)
        if flip == bet:
            changeBalance(user, amt)
            embedVar = discord.Embed(color=EMBED_COLOR)
            embedVar.add_field(name=":full_moon: Flip Moons: Win! :full_moon:", value="I flipped {}! <@!{}> won {}:full_moon:! You now have {}:full_moon:.".format(flip, user, amt, currentMoons+amt), inline=False)
            await ctx.send(embed=embedVar)
        else:
            changeBalance(user, -amt)
            embedVar = discord.Embed(color=EMBED_COLOR)
            embedVar.add_field(name=":full_moon: Flip Moons: Loss :full_moon:", value="I flipped {}! <@!{}> lost {}:full_moon:. You now have {}:full_moon:.".format(flip, user, amt, currentMoons-amt), inline=False)
            await ctx.send(embed=embedVar)



    @commands.command(name="blackjack", aliases=["bj"])
    async def blackjack(self, ctx, subcmd:str, amt:int=0):
        data = getData(GAMBLING_DATA)
        user = ctx.author.id
        finish = False
        if subcmd == "new":
            if data.get(user) != None and data.get(user).get("blackjack") != None: #already game in progress
                return
            if amt == 0 or amt < getBalance(user):
                return
            playerCards = []
            dealerCards = []
            playerCards.append(drawCard(playerCards, dealerCards))
            dealerCards.append(drawCard(playerCards, dealerCards))
            playerCards.append(drawCard(playerCards, dealerCards))
            dealerCards.append(drawCard(playerCards, dealerCards))

            player = displayCardsBJ(playerCards, False)
            dealer = displayCardsBJ(dealerCards, True)
            embedVar = discord.Embed(color=EMBED_COLOR)
            embedVar.add_field(name="{} ({})".format(ctx.author.nick, player[0]), value=player[1], inline=False)
            embedVar.add_field(name="Dealer ({})".format(dealer[0]), value=dealer[1], inline=False)
            messageId = (await ctx.send(embed=embedVar)).id
            channelId = ctx.channel.id
            if data.get(str(user)) == None:
                data.update({str(user): {"blackjack": [playerCards, dealerCards, channelId, messageId, amt] } })
            else:
                data.get(str(user)).update({"blackjack": [playerCards, dealerCards, channelId, messageId, amt] })
        elif subcmd == "hit":
            if data.get(user) == None or data.get(user).get("blackjack") == None: #no data or no game in progress
                return
            userData = data.get(str(user)).get("blackjack")
            playerCards = userData[0]
            dealerCards = userData[1]
            playerCards.append(drawCard(playerCards, dealerCards))
            player = displayCardsBJ(playerCards, False)
            dealer = displayCardsBJ(dealerCards, True)
            if player[1] > 21: #bust
                finish = True
            else:
                embedVar = discord.Embed(color=EMBED_COLOR)
                embedVar.add_field(name="{} ({})".format(ctx.author.nick, player[0]), value=player[1], inline=False)
                embedVar.add_field(name="Dealer ({})".format(dealer[0]), value=dealer[1], inline=False)
                messageId = (await ctx.send(embed=embedVar)).id
                channelId = ctx.channel.id
                data.get(str(user)).get("blackjack")[0] = playerCards
        elif subcmd == "stay":
            if data.get(user) == None or data.get(user).get("blackjack") == None: #no data or no game in progress
                return
            finish = True
        else:
            #print out info about blackjack
            pass


        if finish:
            userData = data.get(str(user)).get("blackjack")
            playerCards = userData[0]
            dealerCards = userData[1]
            while True:
                if displayCardsBJ(dealerCards, False)[1] >= 17:
                    break
                else:
                    dealerCards.append(drawCard(playerCards, dealerCards))
            userCards = displayCardsBJ(userData, False)
            dealerCards = displayCardsBJ(dealerCards, False)
            embedVar = discord.Embed(color=EMBED_COLOR)
            if userCards[1] > 21:
                embedVar.add_field(name="Blackjack > Bust!".format(ctx.author.nick, player[1]), value="You lost {} moons!".format(userData[4]), inline=False)
                changeBalance(user, -userData[4])
            elif dealerCards[1] > 21 or userCards[1] > dealerCards[1]:
                embedVar.add_field(name="Blackjack > Win!".format(ctx.author.nick, player[1]), value="You won {} moons!".format(userData[4]), inline=False)
                changeBalance(user, userData[4])
            else:
                embedVar.add_field(name="Blackjack > Tie!".format(ctx.author.nick, player[1]), value="You got your money back".format(userData[4]), inline=False)
            embedVar.add_field(name="{} ({})".format(ctx.author.nick, userCards[0]), value=userData[1], inline=False)
            embedVar.add_field(name="Dealer ({})".format(dealerCards[0]), value=dealerCards[1], inline=False)
            channel = bot.get_channel(int(userData[2]))
            msg = await channel.fetch_message(int(userData[3]))
            await msg.edit(embed=embedVar)
            data.get(str(user)).update({"blackjack": None})


def drawCard(playerCards, dealerCards):
    """Draws a random card that is not in playerCards or dealerCards and returns it"""

    while True:
        card = ([random.choice(CARD_SUITS), random.choice(CARD_VALUES)])
        if card not in playerCards and card not in dealerCards:
            return card


def displayCardsBJ(cards, hidden):
    """Converts an array of card tuples into a string and a numeric value for blackjack"""

    cardStr = ""
    cardVal = 0
    if hidden:
        cardStr = cards[0][0] + str(cards[0][1]) + " "
        for i in range(len(cards)-1):
            cardStr += ":grey_question: "
    else:
        aces = 0
        for c in cards:
            cardStr += c[0]+str(c[1])
            if c[1].isnumeric():
                cardVal += c[1]
            elif c[1] == "A":
                aces+=1
            else:
                cardVal += 10
        for a in range(aces):
            if cardVal+11 <= 21:
                cardVal+=11
            else:
                cardVal+=1
    return [cardStr, cardVal]


def setup(bot):
    bot.add_cog(GamblingCog(bot))
