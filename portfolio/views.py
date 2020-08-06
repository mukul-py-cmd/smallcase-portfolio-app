from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers,status
from decimal import Decimal
from django.db.models import Sum
from datetime import datetime,date, timedelta
from .serializers import CreateTradeSerializer,TradeSerializer,SecuritySerializer,HoldingViewSerializer
from .models import Security, Trade

# Create your views here.

#Create and get portfolio APIs for trade.
class Trade_Create_Get_View(APIView):
	
	# Handles new BUY/SELL trades and update securities.
	def post(self,request):
		serializer = CreateTradeSerializer(data = request.data)
		if serializer.is_valid(raise_exception=True):
			try:
				ticker = request.data.get('security').upper()
			except Exception as e:
				return Response("Please check the security" + str(e), status=status.HTTP_400_BAD_REQUEST)

			security = Security.objects.filter(ticker = ticker).first()
			#Handling cases like sell qn > buy quan || Stock is bought for the first time
			if request.data.get('transaction_type') == "SELL":
				if security is None or security.shares < request.data.get('shares'):
					return Response({"message" : "You do not have {0} shares of {1}".format(request.data.get('shares'),ticker)}, status=status.HTTP_400_BAD_REQUEST)
			elif request.data.get('transaction_type') == "BUY":
				if security is None:
					security = Security.objects.create(ticker = ticker, shares = 0, avg_buy_price = 0, booked_profit = 0)
			
			serializer.save(security = security)
			serializer.data['security'] = ticker
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	#For fetching all holdings and their corresponding trades
	def get(self,request):
		security = Security.objects.all()
		serializer = SecuritySerializer(security,many = True)
		return Response(serializer.data)

	


#view to handle update/delete requests corresponding to an trade id
class Trade_Update_Delete_View(APIView):

	#update a trade and update the portfolio/security to it's new appropriate state
	def put(self,request,id):
		trade_instance = get_object_or_404(Trade,id = id)
		security_instance = trade_instance.security
		serializer = CreateTradeSerializer(instance = trade_instance,data=request.data)
		if serializer.is_valid(raise_exception=True):
			try:
				ticker = request.data.get('security').upper()
				is_valid = self.transaction_validity(security_instance, trade_instance, serializer.validated_data, ticker)
				if is_valid:
					self.revert_security_state(security_instance,trade_instance, serializer.validated_data, ticker)
			except Exception as e:
				return  Response({"message" : "Trade can't be updated as " +str(e) }, status=status.HTTP_400_BAD_REQUEST)

			#Get instance of security to add new trade and handle if security is bought first time
			new_security = Security.objects.filter(ticker = ticker).first()
			if serializer.validated_data.get('transaction_type') == "BUY":
				if new_security is None:
					new_security = Security.objects.create(ticker = ticker, shares = 0, avg_buy_price = 0, booked_profit = 0)

			serializer.save(security = new_security)
			
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



	# deleting a trade and simultaneously reversing the portfolio to the older state
	def delete(self,request,id):
		trade_instance = get_object_or_404(Trade, id = id)
		security_instance = trade_instance.security
		try:
			is_valid = self.transaction_validity(security_instance,trade_instance)
			if is_valid:
				self.revert_security_state(security_instance,trade_instance)

		except Exception as e:
			return  Response({"message" : "Trade can't be deleted as " +str(e) }, status=status.HTTP_400_BAD_REQUEST)
		
		trade_instance.delete()
		return Response({"message" : "successfully deleted trade {0}".format(id)})


	def transaction_validity(self,security_instance,trade_instance,data = None,ticker = None):
		all_trades = Trade.objects.filter(security = security_instance).order_by('id')
		curr_shares = 0
		for trade in all_trades:
			if trade.id is not trade_instance.id:
				curr_shares += trade.shares if (trade.transaction_type == "BUY") else (-1 * trade.shares)
				
			#only runs in update requests and when security remains same
			elif (trade.id == trade_instance.id) and data and (ticker == security_instance.ticker):
				curr_shares += trade_instance.shares if (trade_instance.transaction_type == "SELL") else (-1 * trade_instance.shares)
				curr_shares += data.get('shares') if (data.get('transaction_type') == "BUY") else (-1 * data.get('shares'))

			if curr_shares < 0:
					raise Exception("your shares will become negative at trade id {0}".format(trade.id))

		#if update request is not on same security so checking sell quantity
		if data and (ticker is not security_instance.ticker):
			new_security = Security.objects.filter(ticker = ticker).first()
			if data.get('transaction_type') == "SELL":
				if new_security is None or new_security.shares < data.get('shares'):
					raise Exception("You do not have {0} shares of {1}".format(data.get('shares'),ticker))

		return True



	# Function called by update and delete to revert back portfolio/security to it's old appropriate state
	def revert_security_state(self,security_instance,trade_instance,data = None,ticker = None):
		all_trades = Trade.objects.filter(security = security_instance).order_by('id')
		avg = Decimal(0)
		shares = 0
		profit = Decimal(0)
		for trade in all_trades:
			if trade.id is not trade_instance.id:
				if trade.transaction_type  == "BUY":
					price = trade.price
					total_shares = shares + trade.shares
					avg = round(( (avg*Decimal(shares)) + (Decimal(trade.shares) * price))/Decimal(total_shares),3)
					shares = total_shares
				elif trade.transaction_type  == "SELL":
					price =trade.price
					total_shares = shares - trade.shares
					profit  += round(((Decimal(trade.shares)) * (price - avg)),3)
					shares = total_shares
			elif (trade.id == trade_instance.id) and data and (ticker == security_instance.ticker):
				if data.get('transaction_type')  == "BUY":
					price =data.get('price')
					total_shares = shares + data.get('shares')
					avg = round(( (avg*Decimal(shares)) + (Decimal(data.get('shares')) * price))/Decimal(total_shares),3)
					shares = total_shares
				elif data.get('transaction_type')  == "SELL":
					price =data.get('price')
					total_shares = shares - data.get('shares')
					profit  += round(((Decimal(data.get('shares'))) * (price - avg)),3)
					shares = total_shares

		if shares == 0:
			avg = Decimal(0)
		security_instance.shares = shares
		security_instance.booked_profit = profit
		security_instance.avg_buy_price = avg
		security_instance =  security_instance.save()
		return security_instance




#View for fetching all holdings in a portfolio
class HoldingView(APIView):

	def get(self,request):
		holding = Security.objects.all()
		serializer = HoldingViewSerializer(holding,many = True)
		return Response(serializer.data)


#View for fetching returns on the whole portfolio by the formula given. Current price taken as 100.
class ReturnView(APIView):
	current_price = 100
	def get(self,request):

		holding = Security.objects.all()
		serializer = HoldingViewSerializer(holding,many = True)
		cummulative_return = Decimal(0)
		for security in serializer.data:
			cummulative_return += ( Decimal(self.current_price) -Decimal(security.get('avg_buy_price'))) * Decimal(security.get('shares'))

		return Response("Your returns are {0}".format(cummulative_return) ,status=status.HTTP_201_CREATED )


