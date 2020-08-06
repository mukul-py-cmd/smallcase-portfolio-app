
from decimal import Decimal
trades = [
            {
                "id": 28,
                "shares": 10,
                "price": "6.784",
                "transaction_type": "BUY",
                "traded_time": "2020-08-05T18:50:44.844422Z"
            },
            {
                "id": 30,
                "shares": 8,
                "price": "7.589",
                "transaction_type": "SELL",
                "traded_time": "2020-08-05T18:48:46.202032Z"
            }
        ]


"""

{
	"security" : "KKK",
	"shares" : 5,
	"price" : 6,
	"transaction_type" : "BUY"
}
"""
avg = 0
shares = 0
profit = 0

for trade in trades:
	if trade.get('transaction_type') == "BUY":
		price = Decimal(trade.get('price'))
		total_shares = shares + trade.get('shares')
		avg = round(( (avg*shares) + (trade.get('shares') * price))/total_shares,3)
		shares = total_shares
	elif trade.get('transaction_type') == "SELL":
		price = Decimal(trade.get('price'))
		total_shares = shares - trade.get('shares')
		profit  += round((trade.get('shares') * (price - avg)),3)
		shares = total_shares



print( str(shares) )
print(str(avg) )
print( str(profit) )