Base url : https://stormy-tundra-89363.herokuapp.com

Admin access

/admin



Create Trade [POST]

/trades/add/


To Buy
To Sell
{
	"security" : "sbin",
	"shares" : 5,
	"price" : 6.34,
	"transaction_type" : "BUY"
}


{
	"security" : "Wipro",
	"shares" : 5,
	"price" : 6,
	"transaction_type" : "SELL"
}





Update Trade [PUT]

/trades/<int:id>/

(id = Trade id to update)
(Edit any field in the trade and keep the remaining fields same, as the trade to update)

Suppose Trade to edit is : 
{
                "id": 1,
		   "ticker": "SBIN",
                "shares": 5,
                "price": "6.000",
                "transaction_type": "BUY",
                "traded_time": "2020-08-05T07:37:14.877442Z"
            },
Url : /trades/1/




Editing one field eg: price
Change two fields 
Edit all fields
{
    "security" : "sbin",
    "shares" : 5,
    "price" : 8.2,
    "transaction_type" : "BUY"
}


{
    "security" : "wipro",
    "shares" : 5,
    "price" : 6,
    "transaction_type" : "SELL"
}


{
    "security" : "RIL",
    "shares" : 10,
    "price" : 13,
    "transaction_type" : "SELL"
}




#note : Update and delete have the same urls. They will be differentiated on basis of request verbs [PUT, DELETE]
Remove a trade [Delete]

/trades/<int:id>/
(id = Trade id to delete)

 Example url : /trades/1/


 Fetching portfolio [GET]

Get all securities and their corresponding trades and booked profits

trades/all/

[
    {
        "ticker": "KKK",
        "shares": 1,
        "avg_buy_price": "6.000",
        "booked_profit": "56.000",
        "trades": [
            {
                "id": 1,
                "shares": 5,
                "price": "6.000",
                "transaction_type": "BUY",
                "traded_time": "2020-08-05T07:37:14.877442Z"
            },
            {
                "id": 2,
                "shares": 4,
                "price": "20.000",
                "transaction_type": "SELL",
                "traded_time": "2020-08-05T12:00:35.311152Z"
            }
        ]
    },
    {
        "ticker": "TCS",
        "shares": 4,
        "avg_buy_price": "8.250",
        "booked_profit": "10.000",
        "trades": [
            {
                "id": 3,
                "shares": 5,
                "price": "10.000",
                "transaction_type": "BUY",
                "traded_time": "2020-08-05T12:14:20.486286Z"
            },
            {
                "id": 4,
                "shares": 2,
                "price": "15.000",
                "transaction_type": "SELL",
                "traded_time": "2020-08-05T12:14:47.666240Z"
            },
            {
                "id": 5,
                "shares": 1,
                "price": "3.000",
                "transaction_type": "BUY",
                "traded_time": "2020-08-05T12:15:04.218012Z"
            }
        ]
    }
]

 Fetching holdings [GET]

Get all securities in the portfolio

/holdings/

[
    {
        "ticker": "KKK",
        "shares": 1,
        "avg_buy_price": "6.000",
        "booked_profit": "56.000",
        "last_updated": "2020-08-05T12:00:35.297131Z"
    },
    {
        "ticker": "TCS",
        "shares": 4,
        "avg_buy_price": "8.250",
        "booked_profit": "10.000",
        "last_updated": "2020-08-05T12:15:04.213685Z"
    }
]


Fetching returns [GET]

Fetch all cumulative returns. Current Price is taken as Rs 100

/returns/

"Your returns are 461.000"





































Database Design

Schema has two tables .

Table 1 : Security 

Security table holds all the current securities along with their meta-data.
Security table can’t be directly manipulated by external APIs. User can take a trade using external APIs which in turn will automatically update Security table.

Ticker  = Primary Key (Unique and index)
Booked Profit and Last_updated Added automatically (Can’t be overridden)

Security Table

Ticker
Shares
Avg_buy_price
Booked_profit
Last_updated
WIPRO
25
22.333
156.33
2020-08-05T12:15:04.213685Z


Table 2 : Trade

Trade table holds all the trades taken by a user using exposed APIs. Whenever a trade is made, Security table is updated appropriately. 
A trade can be updated or deleted corresponding to a  trade id.  Trade can be updated on any combinations of field [security, shares,price,transaction type]. Security table will be updated accordingly in the backend.

Id = Primary Key
Security = Foreign Key attached to security model instance on ticker symbol field.
Transaction type  = BUY/SELL


Trade Table
 
id
Security
Shares
Price
Transaction Type
Traded Time
12
WIPRO
12
33.25
BUY
2020-08-05T12:15:04.213685Z




Further Improvements:

Tech improvements to scale the app:

Initial scaling.
Caching can be implemented for all get apis to reduce hitting databases and redundant calculations. Whenever a post, put or delete request is made corresponding cache can be invalidated. [Redis]
Indexing must be done on certain column in database which are frequently used.
Set proper isolation levels to avoid race condition in writes. Current isolation level = [read committed]

Later stage scaling when app grows in services and userbase and our internal teams
Running several server instances and Implementing a load balancer to balance server loads.
Breaking up monolith system into microservice architecture and optimising each service with its own tech stack and resources according to its traffic load. A proxy server will handle the routing of requests to the service requested.
Implementing a master-slave database structure to improve durability and availability. 
Identifying if our services are write heavy or read heavy and implementing the master-slave architecture according to it. If we are read heavy , a proxy server can send write requests to master database which can be in sync with slave databases . Read requests can be served from any database . 
Until the data is synced slaves can serve the stale data increasing availability but reducing consistency.  These parameters can be fine tuned according to needs of our users. 



Feature Wise improvements:
Integrate app directly to where our users are making investments to automatically update the portfolio instead of manually remembering to do so.
Integrating live market prices/knowledge/news as a one stop place for getting all the information about securities in the users portfolio.
A marketplace for investment professionals and traders to sell their investment ideas.



