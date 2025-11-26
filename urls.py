from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('account/<int:account_id>/', views.account_detail, name='account_detail'),
    path('create-account/', views.create_account, name='create_account'),
    path('account/<int:account_id>/transaction/', views.make_transaction, name='make_transaction'),
    path('apply-loan/', views.apply_loan, name='apply_loan'),
    path('loans/', views.loan_list, name='loan_list'),
]