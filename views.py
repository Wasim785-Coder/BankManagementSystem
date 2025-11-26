from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Customer, Account, Transaction, Loan
from .forms import UserRegistrationForm, CustomerProfileForm, AccountCreationForm, TransactionForm, LoanApplicationForm
import random
import string

def generate_account_number():
    return ''.join(random.choices(string.digits, k=12))

def home(request):
    return render(request, 'banking/home.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = CustomerProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            # Create a default savings account
            account = Account.objects.create(
                customer=profile,
                account_number=generate_account_number(),
                account_type='savings'
            )
            
            messages.success(request, 'Registration successful! Your account has been created.')
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        profile_form = CustomerProfileForm()
    
    return render(request, 'banking/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def dashboard(request):
    try:
        customer = Customer.objects.get(user=request.user)
        accounts = Account.objects.filter(customer=customer, is_active=True)
        recent_transactions = Transaction.objects.filter(account__in=accounts).order_by('-timestamp')[:5]
        
        # Calculate total balance
        total_balance = sum(account.balance for account in accounts)
        
    except Customer.DoesNotExist:
        # If no customer profile exists, create one
        customer = Customer.objects.create(
            user=request.user,
            phone_number='Not provided',
            address='Not provided',
            date_of_birth='2000-01-01'
        )
        accounts = []
        recent_transactions = []
        total_balance = 0
        messages.info(request, 'Please update your profile information.')
    
    return render(request, 'banking/dashboard.html', {
        'customer': customer,
        'accounts': accounts,
        'recent_transactions': recent_transactions,
        'total_balance': total_balance
    })

@login_required
def account_detail(request, account_id):
    try:
        customer = Customer.objects.get(user=request.user)
        account = get_object_or_404(Account, id=account_id, customer=customer)
        transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
    except Customer.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('dashboard')
    
    return render(request, 'banking/account_detail.html', {
        'account': account,
        'transactions': transactions
    })

@login_required
def create_account(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        # If no customer profile exists, create one with default values
        customer = Customer.objects.create(
            user=request.user,
            phone_number='Not provided',
            address='Not provided',
            date_of_birth='2000-01-01'  # Default date
        )
        messages.info(request, 'A customer profile was created for you with default values. Please update your profile information.')
    
    if request.method == 'POST':
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.customer = customer
            account.account_number = generate_account_number()
            account.save()
            messages.success(request, 'New account created successfully!')
            return redirect('dashboard')
    else:
        form = AccountCreationForm()
    
    return render(request, 'banking/create_account.html', {'form': form})

@login_required
def make_transaction(request, account_id):
    account = get_object_or_404(Account, id=account_id, customer__user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction_data = form.save(commit=False)
            transaction_data.account = account
            
            try:
                with transaction.atomic():
                    if transaction_data.transaction_type == 'withdrawal':
                        if account.balance >= transaction_data.amount:
                            account.balance -= transaction_data.amount
                            account.save()
                            transaction_data.save()
                            messages.success(request, 'Withdrawal successful!')
                        else:
                            messages.error(request, 'Insufficient funds!')
                            return render(request, 'banking/make_transaction.html', {'form': form, 'account': account})
                    
                    elif transaction_data.transaction_type == 'deposit':
                        account.balance += transaction_data.amount
                        account.save()
                        transaction_data.save()
                        messages.success(request, 'Deposit successful!')
                    
                    elif transaction_data.transaction_type == 'transfer':
                        recipient_account_number = request.POST.get('recipient_account')
                        try:
                            recipient_account = Account.objects.get(account_number=recipient_account_number, is_active=True)
                            if account.balance >= transaction_data.amount:
                                account.balance -= transaction_data.amount
                                recipient_account.balance += transaction_data.amount
                                account.save()
                                recipient_account.save()
                                transaction_data.recipient_account = recipient_account
                                transaction_data.save()
                                messages.success(request, 'Transfer successful!')
                            else:
                                messages.error(request, 'Insufficient funds for transfer!')
                                return render(request, 'banking/make_transaction.html', {'form': form, 'account': account})
                        except Account.DoesNotExist:
                            messages.error(request, 'Recipient account not found!')
                            return render(request, 'banking/make_transaction.html', {'form': form, 'account': account})
                
                return redirect('account_detail', account_id=account.id)
            
            except Exception as e:
                messages.error(request, f'Transaction failed: {str(e)}')
    
    else:
        form = TransactionForm()
    
    return render(request, 'banking/make_transaction.html', {'form': form, 'account': account})

@login_required
def apply_loan(request):
    customer = get_object_or_404(Customer, user=request.user)
    
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.customer = customer
            loan.interest_rate = 8.5  # Default interest rate
            loan.save()
            messages.success(request, 'Loan application submitted successfully!')
            return redirect('dashboard')
    else:
        form = LoanApplicationForm()
    
    return render(request, 'banking/apply_loan.html', {'form': form})

@login_required
def loan_list(request):
    customer = get_object_or_404(Customer, user=request.user)
    loans = Loan.objects.filter(customer=customer).order_by('-id')
    return render(request, 'banking/loan_list.html', {'loans': loans})
