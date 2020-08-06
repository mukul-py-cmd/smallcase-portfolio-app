from rest_framework import serializers
from .models import Security, Trade
from decimal import Decimal


class TradeSerializer(serializers.ModelSerializer):
	class Meta:
	    model = Trade
	    fields = ['id','shares','price','transaction_type','traded_time']


#For fetching all holdings and corresponding trades
class SecuritySerializer(serializers.ModelSerializer):
	trades = TradeSerializer(many = True)
	class Meta:
		model = Security
		fields = ['ticker','shares','avg_buy_price','booked_profit','trades']


#For fetching all holdings
class HoldingViewSerializer(serializers.ModelSerializer):
	class Meta:
		model = Security
		fields = '__all__'


#For creating and updating trades
class CreateTradeSerializer(serializers.ModelSerializer):
	class Meta:
	    model = Trade
	    fields = ['shares','price','transaction_type']

	#override  parent create to update the security and then add the trade
	def create(self, validated_data):
	    self.update_security(validated_data)
	    trade = Trade.objects.create(**validated_data)	    
	    return trade

	#override parent update to update the security and then add the trade
	def update(self,instance, validated_data):
		# if update request in same security , security calculations already handled
		if instance.security == validated_data.get('security'):
			print("matched")
		# old security calculations are already handled. call update for new security updation
		else:
			self.update_security(validated_data)
			print("unmatched")
		
		return super().update(instance,validated_data)

		
	#updating security
	def update_security(self,validated_data):
		security = validated_data.get('security')	    
		shares = validated_data.get('shares')
		price = validated_data.get('price')
		transaction_type = validated_data.get('transaction_type')

		#updating security fields like shares, average_price and profit_booked after each trade
		if transaction_type == "BUY":
			security.avg_buy_price = round(((security.avg_buy_price * Decimal(security.shares)) + (price*Decimal(shares)))/Decimal((shares +security.shares )),3)
			security.shares = shares +security.shares
		elif transaction_type == "SELL":
			security.booked_profit = round(security.booked_profit + (Decimal(shares) * (price - security.avg_buy_price)),3)
			security.shares = security.shares - shares
			# if security.shares == 0:
			# 	security.avg_buy_price = 0
		return security.save()


		









