import discord
from discord.ext import commands
import random
import consts
import cogs.economy as economy
import logging
import asyncio

logger = logging.getLogger("cherry.gambling")

class GamblingCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="flip", aliases=["coinflip"])
	async def coin_flip(self, ctx, amt=0, call="heads"):
		user = ctx.author
		logger.info(f"{user} flipping coin for {amt} cherries on {call} is invalid")

		if (bet := consts.Coin.get(call)) is None:
			logger.info(f"Call {call} is invalid")
			await ctx.send(f"{call} is not a valid coin side. Your call can be either heads or tails")

		logger.debug(f"Call is {call}")

		if (balance := economy.get_balance(user)) < amt:
			logger.info(f"Balance {balance} is less than bet amount {amt}")
			await ctx.send(f"Your balance is not enough to cover your bet of {bet}")

		logger.debug(f"Bet amount is {amt}")

		flip = random.choice(list(consts.Coin))
		logger.debug(f"Flipped {flip.value}")
		embed = discord.Embed(color=consts.EMBED_COLOR)
		if flip == bet:
			new_balance = balance + amt
			logger.debug(f"User balance changed from {balance} to {new_balance}")
			embed.add_field(name=":cherries: Flip Cherries: Win :cherries:", value=f"I flipped {flip.value}! {user.mention} won {amt} cherries! You now have {new_balance} cherries.", inline=False)
		else:
			new_balance = balance - amt
			logger.debug(f"User balance changed from {balance} to {new_balance}")
			embed.add_field(name=":cherries: Flip Cherries: Loss :cherries:", value=f"I flipped {flip.value}! {user.mention} lost {amt} cherries. You now have {new_balance} cherries.", inline=False) 
		
		logger.debug(f"Changing user balance to match win/loss")
		economy.set_balance(user, new_balance)
		await ctx.send(embed=embed)
		logger.info(f"Successfully flipped coin for {user}")


	@commands.command(name="blackjack", aliases=["bj"])
	async def blackjack(self, ctx, amt:int=0):
		user = ctx.author
		state = consts.Blackjack_State.IN_PROGRESS
		
		balance = economy.get_balance(user)
		if balance < amt:
			logger.info(f"Failed starting blackjack game, user balance is {balance} which is less than {amt}")
			embed = discord.Embed(color=consts.EMBED_COLOR)
			embed.add_field(name=":spades: Blackjack: Cancelled :spades:", value=f"{user.mention}, you don't have enough cherries to gamble. Your current balance is {balance}", inline=False)
			await ctx.send(embed=embed)
			return
		
		logger.info(f"Starting blackjack game for {user} for {amt} cherries")

		player_cards = draw_cards(2)
		player_hand_total = get_blackjack_total(player_cards)
		dealer_cards = draw_cards(2, player_cards)
		dealer_hand_total = get_blackjack_total(dealer_cards)

		logger.debug(f"Starting hands: dealer has {dealer_cards} with total {dealer_hand_total}, {user} has {player_cards} with total {player_hand_total}")


		embed = discord.Embed(color=consts.EMBED_COLOR)
		embed.add_field(name=f":spades: Blackjack: In progress :spades:", value=consts.BLACKJACK_HELP, inline=False)
		embed.add_field(name=f"{user}", value=display_cards(player_cards), inline=False)
		embed.add_field(name=f"Dealer", value=display_cards(dealer_cards, hidden=1), inline=False)
		msg = await ctx.send(embed=embed)
	
		def check(reaction, user):
			logger.debug(f"Received {reaction}, {user} from blackjack input check")
			return user == ctx.author and str(reaction) in ["\N{Regional Indicator Symbol Letter H}", "\N{Regional Indicator Symbol Letter S}"]
		while not state in [consts.Blackjack_State.STAND, consts.Blackjack_State.LOSE]:
			await msg.add_reaction("\N{Regional Indicator Symbol Letter H}")
			await msg.add_reaction("\N{Regional Indicator Symbol Letter S}")
			try:
				logger.debug("Adding reactions and waiting for player input")
				reaction, user = await self.bot.wait_for('reaction_add', timeout=300.0, check=check)
			except asyncio.TimeoutError:
				logger.debug(f"Timed out: automatically standing {user}")
				state = consts.Blackjack_State.STAND
			else:
				if str(reaction) == "\N{Regional Indicator Symbol Letter H}":
					logger.debug(f"Received 'Hit' input")
					player_cards += draw_cards(1, player_cards, dealer_cards)
					player_hand_total = get_blackjack_total(player_cards)
					logger.debug(f"New player hand is {player_cards} with total {player_hand_total}")
					if player_hand_total > 21:
						logger.debug(f"{user} went bust")
						state = consts.Blackjack_State.LOSE
					else:
						logger.debug(f"No bust, updating display")
						embed = discord.Embed(color=consts.EMBED_COLOR)
						embed.add_field(name=f":spades: Blackjack: In progress :spades:", value=consts.BLACKJACK_HELP, inline=False)
						embed.add_field(name=f"{user}", value=display_cards(player_cards), inline=False)
						embed.add_field(name=f"Dealer", value=display_cards(dealer_cards, hidden=1), inline=False)
						await msg.edit(embed=embed)
						
				else:
					logger.debug(f"Received 'Stand' input")
					state = consts.Blackjack_State.STAND

				logger.debug(f"Removing {user}'s reaction")
				await reaction.remove(user)
		
		if state == consts.Blackjack_State.STAND:
			logger.debug(f"Processing dealer's turns")
			while (dealer_hand_total := get_blackjack_total(dealer_cards)) < 16:
				logger.debug(f"Dealer is hitting with total {dealer_hand_total}")
				dealer_cards += draw_cards(1, player_cards, dealer_cards)
				logger.debug(f"New dealer hand is {dealer_cards}")

			if dealer_hand_total <= 21:
				if dealer_hand_total > player_hand_total:
					logger.debug(f"Dealer wins {dealer_hand_total} to {player_hand_total}")
					state = consts.Blackjack_State.LOSE
				elif dealer_hand_total < player_hand_total:
					logger.debug(f"Player wins {player_hand_total} to {dealer_hand_total}")
					state = consts.Blackjack_State.WIN
				elif dealer_hand_total == 21 and player_hand_total == 21:
					if len(dealer_cards) == len(player_cards):
						logger.debug(f"Player and dealer tie: {player_hand_total} to {dealer_hand_total}")
						state = consts.Blackjack_State.TIE
					elif len(dealer_cards) == 5:
						logger.debug(f"Dealer wins with a 5 card black jack, {dealer_hand_total} to {player_hand_total}")
						state = consts.Blackjack_State.LOSE
					elif len(player_cards) == 5:
						logger.debug(f"Player wins with a 5 card black jack, {player_hand_total} to {dealer_hand_total}")
						state = consts.Blackjack_State.WIN
					elif len(dealer_cards) == 2:
						logger.debug(f"Dealer wins with a 2 card black jack, {dealer_hand_total} to {player_hand_total}")
						state = consts.Blackjack_State.LOSE
					elif len(player_cards) == 2:
						logger.debug(f"Player wins with a 2 card black jack, {player_hand_total} to {dealer_hand_total}")
						state = consts.Blackjack_State.WIN
					else:
						logger.debug(f"Player and dealer tie: {player_hand_total} to {dealer_hand_total}")
						state = consts.Blackjack_State.TIE

				else:
					logger.debug(f"Player and dealer tie: {player_hand_total} to {dealer_hand_total}")
					state = consts.Blackjack_State.TIE
			else:
				logger.debug(f"Dealer busts so player wins, {player_hand_total} to {dealer_hand_total}")
				state = consts.Blackjack_State.WIN

		embed = discord.Embed(color=consts.EMBED_COLOR)
		if state == consts.Blackjack_State.WIN:
			if player_hand_total == 21 and len(player_cards) in [2,5]:
				embed.add_field(name=f":spades: Blackjack: Win! :spades:", value=f"{user.mention} won {amt} cherries with a {len(player_cards)} card blackjack! New balance is {balance + amt} cherries", inline=False)
			else:
				embed.add_field(name=f":spades: Blackjack: Win! :spades:", value=f"{user.mention} won {amt} cherries! New balance is {balance + amt} cherries", inline=False)
			logger.debug(f"{user} gained {amt} cherries for new balance of {balance + amt}")
			economy.set_balance(user, balance + amt)
			logger.info(f"Finished blackjack game: {user} won {amt} cherries")
		elif state == consts.Blackjack_State.LOSE:
			if dealer_hand_total == 21 and len(dealer_cards) in [2,5]:
				embed.add_field(name=f":spades: Blackjack: Loss :spades:", value=f"{user.mention} lost {amt} cherries against a {len(player_cards)} card blackjack. New balance is {balance - amt} cherries", inline=False)
			else:
				embed.add_field(name=f":spades: Blackjack: Loss :spades:", value=f"{user.mention} lost {amt} cherries. New balance is {balance - amt} cherries", inline=False)
			logger.debug(f"{user} lost {amt} cherries for new balance of {balance - amt}")
			economy.set_balance(user, balance - amt)
			logger.info(f"Finished blackjack game: {user} lost {amt} cherries")
		else:
			embed.add_field(name=f":spades: Blackjack: Tie :spades:", value=f"{user.mention} tied with {self.bot.mention}. You got your cherries back.", inline=False)
			logger.info(f"Finished blackjack game: {user} tied with dealer")

		embed.add_field(name=f"{user}", value=f"{display_cards(player_cards)} = {player_hand_total}", inline=False)
		embed.add_field(name=f"Dealer", value=f"{display_cards(dealer_cards)} = {dealer_hand_total}", inline=False)
		await msg.edit(embed=embed)
		await msg.clear_reactions()

"""
Draws num random cards that are not in the hands given and returns it
"""
def draw_cards(num, *args):
	logger.info(f"Picking {num} cards while excluding {args}")
	deck = consts.DECK.copy()
	logger.debug(f"Full deck is {deck}")
	for hand in args:
		logger.debug(f"Current hand is {hand}")
		for card in hand:
			logger.debug(f"Removing card {card}")
			deck.remove(card)

	# logger.debug(f"Final deck is {deck}")

	draw = []
	for _ in range(num):
		card = random.choice(deck)
		logger.debug(f"Randomly picked card is {card}")
		draw.append(card)
		deck.remove(card)

	logger.info(f"Successfully picked cards {draw}")
	return draw

"""
Converts an array of card tuples into a string and a numeric value
"""
def display_cards(cards, hidden=0):
	logger.info(f"Displaying {cards} with the first {hidden} hidden")
	readable_cards = []
	for i in range(len(cards)):
		if hidden > 0:
			readable_cards.append(":grey_question:")
			hidden -= 1
		else:
			readable_cards.append(f"{cards[i][0].value} {cards[i][1].value}")
		logger.debug(f"Card list is now {readable_cards}")

	readable = " ".join(readable_cards)
	logger.info(f"Successfully converted {cards} to readable string {readable}")
	return readable

"""
Gets the card total for blackjack
"""
def get_blackjack_total(cards):
	logger.info(f"Getting the total for {cards}")
	sums = [0,0] # first entry is with the 11, second entry is without
	has_11 = False
	for card in cards:
		logger.debug(f"Current card is {card}")
		if card[0].value in ["J", "Q", "K"]:
			sums[0] += 10
			sums[1] += 10
			logger.debug(f"Adding 10 to sums to get {sums}")
		elif card[0].value == "A":
			if not has_11:
				has_11 = True
				sums[0] += 11
				sums[1] += 1
				logger.debug(f"Added first 11, sums is now {sums}")
			else:
				sums[0] += 1
				sums[1] += 1
				logger.debug(f"Already added an 11 so adding 1 to sums to get {sums}")
		else:
			sums[0] += int(card[0].value)
			sums[1] += int(card[0].value)
			logger.debug(f"Adding {card[0].value} to sums to get {sums}")

	best_total = sums[0] if sums[0] <= 21 else sums[1]
	logger.info(f"Best hand total is {best_total}")
	return best_total


async def setup(bot):
	await bot.add_cog(GamblingCog(bot))
