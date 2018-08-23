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


# class for price levels percentage
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

#class definition of a trade
class trade:

	pair="";
	prices = [];
	amount = 0;
	initiated = False;
	LongShort = "";
	
	def __init__(self,_pair,_amount,_prices,_type):
		self.pair = _pair;
		self.prices = _prices;
		self.amount= _amount;
		self.initiated = False;
		self.LongShort = _type;


	def getPrices(self):
		return self.prices;

	def getPair(self):
		return self.pair;

	def getAmount(self):
		return self.amount;

	def getBought(self):
		return self.initiated;

	def getType(self):
		return self.LongShort;

#function to create a new price, requires an entry price at which to buy _amount, a stop-loss target
# an array of price targtes at which to sell and the percentage eto sell at each target price
# EX: buy 1000 IOTA at 1.19$, set stop at 1.18$, sell 50% at 1.25$ and 50% at 1.30$ looks like:
# newTrade("BUY", IOTAUSDT", 1.19, 1000, 1.18, [1.25, 1.30], [50, 50] )
def newTrade(_type,_pair,_entry,_amount,_stop,_priceTargets,_levels):
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
	thisTrade = trade(_pair,_amount,prices,_type);
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
		_type = trade.getType()

		entry = toCheck[0].getLevel()
		stopLoss = toCheck[1].getLevel()
 
		#creat a new long position
		if _type == "BUY":
			#needs to buy?
			if trade.initiated == False:
				if entry >= (float(_priceNow)):
					executeEntry(counter,toCheck[0],"BUY")
			else:
				#stop loss trigered?
				if stopLoss > (float(_priceNow)):
					executeStopLoss(counter, toCheck[1],"SELL");
					break;
				#price targets reached?
				else:
					for price in toCheck[2:]:
						if price.getLevel() < (float(_priceNow)):
							print ("Target at:",price.getLevel())
							ExecutedAtTarget(counter,price,"SELL")
							break;

		#creat a new short position
		if _type == "SELL":
			#needs to buy?
			if trade.initiated == False:
				if entry <= (float(_priceNow)):
					executeEntry(counter,toCheck[0],"SELL")
			else:
				#stop loss trigered?
				if stopLoss < (float(_priceNow)):
					executeStopLoss(counter, toCheck[1],"BUY");
					break;
				#price targets reached?
				else:
					for price in toCheck[2:]:
						if price.getLevel() > (float(_priceNow)):
							print ("Target at:",price.getLevel())
							ExecutedAtTarget(counter,price,"BUY")
							break;


		counter +=1 ;
	sleep(5)


def executeStopLoss(_index,_price,_type):
	global openTrades
	_trade = openTrades[_index];
	_pair = _trade.getPair();
	_qtt = _trade.getAmount();
	_level = _price.getLevel();
	print ("executing at Stop: ",_type,_qtt,_pair)
	client.create_test_order(
		symbol = _pair,
		side = _type,
		type = "LIMIT",
		timeInForce="GTC",
	    quantity=_qtt,
	    price=_level
		)
	global stoped
	stoped += 1; 
	del openTrades[_index]

def executeEntry(_index,_price,_type):
	global openTrades
	_trade = openTrades[_index];
	_pair = _trade.getPair();
	_qtt = _trade.getAmount();
	_level = _price.getLevel();
	print ("excuting at Entry: ",_type,_qtt,_pair)
	client.create_test_order(
		symbol = _pair,
		side = _type,
		type = "LIMIT",
		timeInForce="GTC",
	    quantity=_qtt,
	    price=_level
		)
	_trade.initiated = True;

def ExecutedAtTarget(_index,_price,_type):
	global openTrades
	_trade = openTrades[_index];
	_pair = _trade.getPair();
	_amount = _trade.getAmount();
	_level = _price.getLevel();
	_perc = _price.getPerc();
	_qtt = _amount *(_perc / 100.0)
	print ("executing at Target: ",_type,_qtt,_pair)
	client.create_test_order(
		symbol = _pair,
		side = _type,
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


#main function
if __name__ == "__main__":
	print ("running...")
	while True:
		#if tardes are set check prices and execute them
		if len(openTrades) !=0:
			print("checking prices....")
			checkPrices()
		else:
			#else if no tardes are set ask for a new tarde
			ask = input("want to add a trade?(y/n): ")
			if ask == "y":
				#get trade info
				_type = input("enter BUY or SELL: ")
				_pair = input("enter a pair: ")
				_entry = input ("enter an entry price: ")
				_amount = input ("enter the amount to tarde: ")
				_stop = input ("enter the stop-loss price: ")

				#first get all price level at which to sell
				_priceTarget = []
				while True:
				    entry = input('Enter a price Target (q to quit): ')
				    if entry.lower() == 'q':
				        break
				    _priceTarget.append(float(entry))

				#then get the percentage on _amount to sell at these levels
				_percTarget = []
				while True:
				    entry = input("Enter the percentage for each price (q to quit): ")
				    if entry.lower() == 'q':
				        break
				    _percTarget.append(float(entry))

				#quick check for correctness
				print(" Your new Trade : newTade",_type,_pair,float(_entry),float(_amount),float(_stop),_priceTarget,_percTarget)
				cont = input("is it correct ?(y/n) ")

				if cont == "y":

					#check if correct number of levels+percentage is given 
					if len(_priceTarget) == len(_percTarget):
						newTrade(_type,_pair,float(_entry),float(_amount),float(_stop),_priceTarget,_percTarget)
					else:
						print("no its not, need same nr. of price targets and percentages")
				elif cont == "n":
					print("lets start again then...")
					
			#if no tarde is given ask again later
			elif ask == "n":
				sleep(10)
				print ("NO TRADES")
