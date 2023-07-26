import yfinance as yf
import discord
from discord.ext import commands
from operator import itemgetter
from datetime import date
import db

bot = commands.Bot(command_prefix= "!",intents=discord.Intents.all())
bot.message_content = True

data = db.read()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def ping(ctx):
    """ Ping the bot! """
    await ctx.reply("pong " + str(ctx.author.id))

@bot.command()
async def start(ctx):
    """ Start the game! """
    global data
    user = str(ctx.author.id)
    if data.get(user) == None:
        data[user] = {
            "name": ctx.author.name,
            "balance": 10000.00,
            "stocks": {},
            "shorted": {},
            "history": []
        }
        db.write(data)
        await ctx.reply("Created account for " + ctx.author.name)
    else:
        await ctx.reply("User already has account")

@bot.command()
async def restart(ctx):
    """ Restart the game! """
    global data
    user = str(ctx.author.id)
    if data.get(user) == None:
        await ctx.reply("Make an account first bruh")
    else:
        data[user] = {
            "name": ctx.author.name,
            "balance": 10000.00,
            "stocks": {},
            "shorted": {},
            "history": []
        }
        await ctx.reply("Recreated account for " + ctx.author.name)


@bot.command()
async def price(ctx, symbol):
    """ Check a stock's price! """
    price = yf.Ticker(symbol).info["regularMarketPrice"]
    if price == None:
        await ctx.reply("Invalid Stock")
        return
    await ctx.reply(f"Price: {price}")


@bot.command()
async def info(ctx, symbol):
    """ Check stock information! """
    price = yf.Ticker(symbol).info["regularMarketPrice"]
    if price == None:
        await ctx.reply("Invalid stock")
        return
    stock = yf.Ticker(symbol)
    stats = {}
    try:
        stats["Sector"] = stock.info['sector']
        stats["P/E Ratio"] = stock.info['forwardPE']
        stats["Dividend Rate"] = stock.info['dividendRate']
        stats["Market Cap"] = stock.info['marketCap']
        stats["52 Week High"] = stock.info['fiftyTwoWeekHigh']
        stats["52 Week Low"] = stock.info['fiftyTwoWeekLow']
        embed = discord.Embed(title=f"__**{symbol.upper()} Information**__", color=0xf1c40f)
        for stat in stats:
            embed.add_field(name=f'{stat}', value=f'{stats[stat]}')
        await ctx.reply(embed=embed)
    except:
        await ctx.reply("No info buy at your own risk")


@bot.command()
async def bal(ctx, username=None):
    """ Check balance! """
    global data
    user = str(ctx.author.id)
    balance = data[user]['balance']
    if username != None:
        isPlayer = False
        while not isPlayer:
            for name in data:
                if data[id]["name"] == username:
                    isPlayer = True
                    user = name
        if not isPlayer:
            await ctx.reply("user not found")
            return
    msg = ""
    if data[user] == None:
        msg = "Please open an account with !start"
    else:
        msg = f"Balance: {balance}"
    await ctx.reply(msg)

@bot.command()
async def value(ctx, username=None):
    """ Check the value of your stocks! """
    global data
    user = str(ctx.author.id)
    if username != None:
        isPlayer = False
        while not isPlayer:
            for name in data:
                if data[id]["name"] == username:
                    isPlayer = True
                    user = name
        if not isPlayer:
            await ctx.reply("user not found")
            return
    if data[user] == None:
        await ctx.reply("Please open an account with !start")
    value = data[user]["balance"]
    stocks = data[user]["stocks"]
    shorted = data[user]["shorted"]
    for stock in stocks:
        price = round(yf.Ticker(stock).info["regularMarketPrice"],2)
        quantity = stocks[stock]["quantity"]
        value += quantity * price
    for short in shorted:
        price = round(yf.Ticker(short).info["regularMarketPrice"],2)
        initialprice = shorted[short]["iprice"]
        quantity = shorted[short]["quantity"]
        value += (quantity * initialprice) + (quantity * (initialprice - price))
    await ctx.reply(f"Value: {value}")
    

@bot.command()
async def buy(ctx, symbol, quantity): 
    """ Buy stocks! """
    global data
    symbol = symbol.upper()
    user = str(ctx.author.id)
    price = round(yf.Ticker(symbol).info['regularMarketPrice'], 2)
    balance = data[user]["balance"]
    stocks = data[user]["stocks"]
    history = data[user]["history"]
    if data[user] == None:
        await ctx.reply("Please open an account with !start")
        return
    if price == None:
        await ctx.reply("Invalid stock")
        return
    if isinstance(quantity, float):
        await ctx.reply("Invalid quantity")
        return
    quantity = int(quantity)
    if quantity <= 0:
        await ctx.reply("Invalid quantity")
        return
    cost = quantity * price
    if balance < cost:
        await ctx.reply("Not enough money bozo")
        return
    if stocks[symbol] == None:
        stocks[symbol]["iprice"] = price
        stocks[symbol]["quantity"] = quantity
    else:
        price = round(((stocks[symbol]["iprice"] * stocks[symbol]["quantity"]) + (cost)) / (stocks[symbol]["quantity"] + quantity),2)
        stocks[symbol]["iprice"] = price
        stocks[symbol]["quantity"] += quantity
    balance -= cost
    history.append(f"Bought {quantity} share(s) of {symbol} at {price} on {date.today()}")
    db.write(data)
    await ctx.reply(f"Bought {quantity} share(s) of {symbol}")


@bot.command()
async def sell(ctx, symbol, quantity=None):
    """ Sell stocks! """
    global data
    symbol = symbol.upper()
    user = str(ctx.author.id)
    price = round(yf.Ticker(symbol).info['regularMarketPrice'],2)
    balance = data[user]["balance"]
    stocks = data[user]["stocks"]
    history = data[user]["history"]
    if data[user] == None:
        await ctx.reply("Please open an account with !start")
        return
    if price == None:
        await ctx.reply("Invalid stock")
        return
    if stocks.get(symbol) == None:
        await ctx.reply("Stock not owned")
        return
    if isinstance(quantity, float):
        await ctx.reply("Invalid quantity")
        return
    quantity = int(quantity)
    if quantity <= 0:
        await ctx.reply("Invalid Quantity")
        return
    if quantity > stocks[symbol]:
        await ctx.reply("Buy some more first kid")
        return
    value = quantity * price
    balance += value
    stocks[symbol]["quantity"] -= quantity
    if stocks[symbol]["quantity"] == 0:
        stocks.pop(symbol)
    history.append(f"Sold {quantity} share(s) of {symbol} at {price} on {date.today()}")
    db.write(data)
    await ctx.reply(f"Sold {quantity} share(s) of {symbol}")


@bot.command()
async def short(ctx, symbol, quantity):
    """ Short a stock! """
    global data
    symbol = symbol.upper()
    user = str(ctx.author.id)
    price = round(yf.Ticker(symbol).info['regularMarketPrice'], 2)
    balance = data[user]["balance"]
    shorted = data[user]["shorted"]
    history = data[user]["history"]
    if data[user] == None:
        await ctx.reply("Please open an account with !start")
        return
    if price == None:
        await ctx.reply("Invalid stock")
        return
    if isinstance(quantity, float):
        await ctx.reply("Invalid quantity")
        return
    quantity = int(quantity)
    if quantity <= 0:
        await ctx.reply("Invalid quantity")
        return
    cost = quantity * price
    if balance < cost:
        await ctx.reply("Not enough money bozo")
        return
    if shorted[symbol] == None:
        shorted[symbol]["iprice"] = price
        shorted[symbol]["quantity"] = quantity
    else:
        price = round(((shorted[symbol]["iprice"] * shorted[symbol]["quantity"]) + (cost)) / (shorted[symbol]["quantity"] + quantity), 2)
        shorted[symbol]["iprice"] = price
        shorted[symbol]["quantity"] += quantity
    balance -= cost
    history.append(f"Shorted {quantity} share(s) of {symbol} at {price} on {date.today()}")
    db.write(data)
    await ctx.reply(f"Shorted {quantity} share(s) of {symbol}")


@bot.command()
async def cover(ctx, symbol, quantity=None):
    """ Cover a stock! """
    global data
    symbol = symbol.upper()
    user = str(ctx.author.id)
    price = round(yf.Ticker(symbol).info['regularMarketPrice'],2)
    balance = data[user]["balance"]
    shorted = data[user]["shorted"]
    history = data[user]["history"]
    if data[user] == None:
        await ctx.reply("Please open an account with !start")
        return
    if price == None:
        await ctx.reply("Invalid stock")
        return
    if shorted.get(symbol) == None:
        await ctx.reply("Stock not owned")
        return
    if isinstance(quantity, float):
        await ctx.reply("Invalid quantity")
        return
    quantity = int(quantity)
    if quantity <= 0:
        await ctx.reply("Invalid quantity")
        return
    if quantity > shorted[symbol]:
        await ctx.reply("Buy some more first kid")
        return
    initialprice = shorted[symbol]["iprice"]
    value = (initialprice * quantity) + (quantity * (initialprice - price))
    balance += value
    shorted[symbol]["quantity"] -= quantity
    if shorted[symbol]["quantity"] == 0:
        shorted.pop(symbol)
    history.append(f"Covered {quantity} share(s) of {symbol} at {price} on {date.today()}")
    db.write(data)
    await ctx.reply(f"Covered {quantity} share(s) of {symbol}")


@bot.command()
async def portfolio(ctx, username=None):
    """ Check your portfolio! """
    global data
    user = str(ctx.author.id)
    if username != None:
        isPlayer = False
        while not isPlayer:
            for name in data:
                if data[id]["name"] == username:
                    isPlayer = True
                    user = name
        if not isPlayer:
            await ctx.reply("user not found")
            return
    if data[user] == None:
        await ctx.reply("Please open an account with !start")
    name = data[user]["name"]
    stocks = data[user]["stocks"]
    shorted = data[user]["shorted"]
    embed = discord.Embed(title=f"__**{name} Portfolio:**__", color=0x1abc9c)
    for stock in stocks:
        price = round(yf.Ticker(stock).info["regularMarketPrice"],2)
        quantity = stocks[stock]["quantity"]
        initialprice = stocks[stock]["iprice"]
        embed.add_field(name=f'{stock}', value=f'Quantity: {quantity}\nInitial Price: {initialprice}\nCurrent Price: {price}')
    for short in shorted:
        price = round(yf.Ticker(short).info["regularMarketPrice"],2)
        quantity = shorted[short]["quantity"]
        initialprice = shorted[short]["iprice"]
        embed.add_field(name=f'(S){short}', value=f'Quantity: {quantity}\nInitial Price: {initialprice}\nCurrent Price: {price}')
    await ctx.reply(embed=embed)

@bot.command()
async def leaderboard(ctx):
    """ Check the game's leaderboard! """
    global data
    leaderboard = {}
    for user in data:
        name = data[user]["name"]
        value = data[user]['balance']
        stocks = data[user]["stocks"]
        shorted = data[user]["shorted"]
        for stock in stocks:
            price = round(yf.Ticker(stock).info["regularMarketPrice"],2)
            quantity = stocks[stock]["quantity"]
            value += quantity * price
        for short in shorted:
            price = round(yf.Ticker(short).info["regularMarketPrice"],2)
            initialprice = shorted[short]["iprice"]
            quantity = shorted[short]["quantity"]
            value += (quantity * initialprice) + (quantity * (initialprice - price))
        leaderboard[name] = value
    ls = sorted(leaderboard.items(), key=lambda x:x[1], reverse=True)
    disp = len(ls)
    embed = discord.Embed(title=f"__**Leaderboard ({date.today()}):**__", color=0xe74c3c)
    if len(ls) > 5:
        disp = 5
    for i in range(disp):
        name =  ls[i][0]
        value = ls[i][2]
        embed.add_field(name=f'{i+1}. {name}', value=f'Value: {value}', inline=False)
    await ctx.reply(embed=embed)


@bot.command()
async def history(ctx, username=None):
    """ Check your transaction history! """
    global data
    user = str(ctx.author.id)
    if username != None:
        isPlayer = False
        while not isPlayer:
            for name in data:
                if data[id]["name"] == username:
                    isPlayer = True
                    user = name
        if not isPlayer:
            await ctx.reply("user not found")
            return
    if data[user] == None:
        await ctx.reply("Please open an account with !start")
    name = data[user]["name"]
    history = data[user]["history"]
    disp = len(history)
    embed = discord.Embed(title=f"__**{name}'s Transaction History:**__", color=0xe74c3c)
    for i in range(disp):
        embed.add_field(value=f'{i+1}. {history[i]}', inline=False)


bot.run("MTAzMTY4MTcwNDY0MzAxMDY4MQ.Gn0ecJ.-GjooqrUD_iZwUzfWL6owq8IlqphUGjZxxiXVM")
