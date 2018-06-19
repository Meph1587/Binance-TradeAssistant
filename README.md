# Binance-TradeAssistant
Allows to place multiple orders with same balance using a programm to set buy/sell orders a predefined levels.
It supports predefined entry level, Stop-Loss as well as multiple exit levels.

## How it works:
download the code </br>
get the API keyes for your binance account </br>
paste them into the code by replacing KEY and KEY2 </br>
open Comand Line Interface, cd to folder with code </br>
```
python tradeAssist.py 
```
schedule a new trade by following the instructions</br>
EX: </br>
enter BUY or SELL: "BUY"</br>
enter a pair: "ETHUSDT"</br>
enter an entry price: "530"</br>
enter the amount to tarde: "0.75"</br>
enter the stop-loss price: "525"</br>
Enter a price Target (q to quit): "570"</br>
Enter a price Target (q to quit): "580"</br>
Enter a price Target (q to quit): "q"</br>
Enter the percentage for each price (q to quit): "50"</br>
Enter the percentage for each price (q to quit): "50"</br>
Enter the percentage for each price (q to quit): "q"</br>
(' Your new Trade : newTade', 'BUY', 'ETHUSDT', 530.0, 0.75, 525.0, [570.0, 580.0], [50.0, 50.0])


## Important
The code executes test-orders, to execute real orders change the code from create_test_order to create_order. Do this at your own risk.


