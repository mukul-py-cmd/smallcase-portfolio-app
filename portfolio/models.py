from django.db import models

# Create your models here.


#Security model which consitutes a portfolio
class Security(models.Model):
	ticker = models.CharField(max_length=15, primary_key=True)
	shares = models.IntegerField()
	avg_buy_price = models.DecimalField(max_digits=7, decimal_places=3)
	booked_profit = models.DecimalField(max_digits=15, decimal_places=3)
	last_updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.ticker


#Trade Model which consitutes a security[security attached to, price, shares, "BUY/SELL" , traded_time(automated)]
class Trade(models.Model):
	BUY = 'BUY'
	SELL = 'SELL'
	TRANS_CHOICES = [
	    (BUY, 'BUY'),
	    (SELL, 'SELL'),
	]
	security = models.ForeignKey(Security, related_name='trades', on_delete=models.CASCADE)
	shares = models.IntegerField()
	price = models.DecimalField(max_digits=7, decimal_places=3)
	transaction_type = models.CharField(
        max_length=4,
        choices=TRANS_CHOICES,
        default=BUY,
    )
	traded_time = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.security.ticker + " " + self.transaction_type + " " + str(self.traded_time)

