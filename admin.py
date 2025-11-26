from django.contrib import admin
from .models import Customer, Account, Transaction, Loan

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'customer', 'account_type', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['account_number', 'customer__user__first_name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'transaction_type', 'amount', 'timestamp']
    list_filter = ['transaction_type', 'timestamp']
    search_fields = ['account__account_number']

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['customer', 'loan_type', 'amount', 'interest_rate', 'is_approved']
    list_filter = ['loan_type', 'is_approved']
    search_fields = ['customer__user__first_name']