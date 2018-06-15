from binance.client import Client
from time import time, sleep
import math

#make connector with API keyes 
client = Client(
	"KEY",
	"KEY2"
	)


#global variables
openTrades = [];
filled = 0 ;
stoped = 0;

#main function
if __name__ == "__main__":
	print ("running...")
	while True:
		if len(openTrades) !=0:
			checkPrices()
		else:
			print ("ADD A NEW TRADE")
			sleep(10)
			print ("NO TRADES")

# class for price levels + percentage
class priceTarget:

	level=0;
	perc=0;
	def __init__(self,_level,_perc):
		self.level=_level;
		self.perc=_perc;

	def getLevel(self):
		return self.level;

	def getPerc(self):
		return self.perc;

#class defining a trade
class trade:

	pair="";
	prices = [];
	amount = 0;
	bought = False;
	
	def __init__(self,_pair,_amount,_prices):
		self.pair = _pair;
		self.prices = _prices;
		self.amount= _amount;
		self.bought = False;

	def getPrices(self):
		return self.prices;

	def getPair(self):
		return self.pair;

	def getAmount(self):
		return self.amount;

	def getBought(self):
		return self.bought;



#function to create a new price, requires an entry price at which to buy _amount, a stop-loss target
# an array of price targtes at which to sell and the percentage eto sell at each target price
# EX: buy 1000 IOTA at 1.19$, set stop at 1.18$, sell 50% at 1.25$ and 50% at 1.30$ looks like:
# newTrade("IOTAUSDT",1.19,1000,1.18,[1.25,1.30],[50,50])
def newTrade(_pair,_entry,_amount,_stop,_priceTargets,_levels):
	prices = [];
	prices.append(priceTarget(_entry,100))
	prices.append(priceTarget(_stop,100))

	#create array with price targets
	count = 0
	for price in _priceTargets:
		target = priceTarget(price,_levels[count])
		count = count + 1;
		prices.append(target)

	#price array has [_entry,_stop,targets....]
	thisTrade = trade(_pair,_amount,prices);
	global openTrades
	openTrades.append(thisTrade);


# checks current price to see if action is required
def checkPrices():
	counter=0;
	for trade in openTrades:

		toCheck = trade.getPrices()
		_pair = trade.getPair()

		_priceNow=client.get_ticker(symbol=_pair)["lastPrice"]

		print (_priceNow)

		entry = toCheck[0].getLevel()
		stopLoss = toCheck[1].getLevel()

		#needs to buy?
		if trade.bought == False:
			if entry >= (float(_priceNow)):
				executeBuy(counter,toCheck[0])
		else:
			#stop loss trigered?
			if stopLoss > (float(_priceNow)):
				executeStopLoss(counter, toCheck[1]);
				break;
			#price targets reached?
			else:
				for price in toCheck[2:]:
					if price.getLevel() < (float(_priceNow)):
						print ("Target at:",price.getLevel())
						sellPositionTarget(counter,price)
						break;
		counter +=1 ;
	sleep(5)


def executeStopLoss(_index,_price):
	global openTrades
	_trade = openTrades[_index];
	_pair = _trade.getPair();
	_qtt = _trade.getAmount();
	_level = _price.getLevel();
	print ("selling at Stop: ",_qtt,_pair)
	client.create_test_order(
		symbol = _pair,
		side = "SELL",
		type = "LIMIT",
		timeInForce="GTC",
	    quantity=_qtt,
	    price=_level
		)
	global stoped
	stoped += 1; 
	del openTrades[_index]

def executeBuy(_index,_price):
	global openTrades
	_trade = openTrades[_index];
	_pair = _trade.getPair();
	_qtt = _trade.getAmount();
	_level = _price.getLevel();
	print ("buying at Entry: ",_qtt,_pair)
	client.create_test_order(
		symbol = _pair,
		side = "BUY",
		type = "LIMIT",
		timeInForce="GTC",
	    quantity=_qtt,
	    price=_level
		)
	_trade.bought = True;

def sellPositionTarget(_index,_price):
	global openTrades
	_trade = openTrades[_index];
	_pair = _trade.getPair();
	_amount = _trade.getAmount();
	_level = _price.getLevel();
	_perc = _price.getPerc();
	_qtt = _amount *(_perc / 100.0)
	print ("selling at Target: ",_qtt,_pair)
	client.create_test_order(
		symbol = _pair,
		side = "SELL",
		type = "LIMIT",
		timeInForce="GTC",
	    quantity=_qtt,
	    price=_level
	)

	if len(_trade.getPrices()) == 2 :
		global filled;
		filled += 1
		del openTrades[_index]
	else:
		_trade.getPrices().remove(_price)


