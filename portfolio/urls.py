from django.urls import path
from .views import Trade_Create_Get_View, HoldingView, ReturnView, Trade_Update_Delete_View






urlpatterns = [
	path('trades/<int:id>/', Trade_Update_Delete_View.as_view(),name = 'update-trade'),
    path('trades/add/', Trade_Create_Get_View.as_view(),name = 'add-trade'),
    path('trades/<int:id>/', Trade_Update_Delete_View.as_view(),name = 'delete-trade'),    
    path('trades/all/', Trade_Create_Get_View.as_view(),name = 'fetch-portfolio'),
    path('holdings/', HoldingView.as_view(),name = 'fetch-holdings'),
    path('returns/', ReturnView.as_view(),name = 'fetch-returns'),

]
