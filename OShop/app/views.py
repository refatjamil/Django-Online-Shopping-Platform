from django.shortcuts import render, redirect
from django.views import View
from .models import Product, Cart, OrderPlaced
from .forms import CoustomerRegistrationFrom, ShippingAddressForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
# def home(request):
#  return render(request, 'app/home.html')

class ProductView(View):
    def get(self, request):
        topwears = Product.objects.filter(category='TM')
        bottomewears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        laptops = Product.objects.filter(category='L')
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))

        context = {'topwears':topwears, 'bottomewears':bottomewears, 'mobiles':mobiles, 'laptops':laptops, 'totalitem':totalitem}

        return render(request, 'app/home.html', context)

class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()

        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))

        context = {'product':product, 'item_already_in_cart':item_already_in_cart, 'totalitem':totalitem}

        return render(request, 'app/productdetail.html', context)

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)


    if Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists():
        return redirect(f'/product-detail/{product_id}')

    cart = Cart(user=user, product=product)
    print(cart)

    cart.save()

    return redirect(f'/product-detail/{product_id}')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        carts = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0  
        cart_product = [p for p in Cart.objects.all() if p.user == user]


        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))

        if cart_product:
            for p in cart_product:
                temp_amount = (p.quantity * p.product.discounted_price)
                amount += temp_amount
        if amount == 0:
            total_amount = 0.0
        else:    
            total_amount = shipping_amount + amount

    context={'carts': carts, 'amount':amount, 'total_amount':total_amount, 'totalitem':totalitem}
    return render(request, 'app/addtocart.html', context)

@login_required
def plus_cart(request):
    if request.method =="GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0  
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                temp_amount = (p.quantity * p.product.discounted_price)
                amount += temp_amount
        if amount == 0:
            total_amount = 0.0
        else:    
            total_amount = shipping_amount + amount

        data = {
            'quantity': c.quantity,
            'amount':amount,
            'total_amount':total_amount
            }
        return JsonResponse(data)


@login_required
def minus_cart(request):
    if request.method =="GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        if c.quantity != 1:
            c.quantity-=1
            c.save()
        amount = 0.0
        shipping_amount = 70.0  
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                temp_amount = (p.quantity * p.product.discounted_price)
                amount += temp_amount
        if amount == 0:
            total_amount = 0.0
        else:    
            total_amount = shipping_amount + amount

        data = {
            'quantity': c.quantity,
            'amount':amount,
            'total_amount':total_amount
            }
        return JsonResponse(data)
    
@login_required
def remove_from_cart(request, id):
    p = Cart.objects.get(id=id)
    print(p)
    p.delete()
    return redirect('/cart')



@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')




 
@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user= request.user)
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))  
    context={'op':op, 'totalitem':totalitem}
    return render(request, 'app/orders.html', context)



def mobile(request, data=None):
    if data == None:
        mobile = Product.objects.filter(category='M')
    elif data == 'below':
        mobile = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
    elif data == 'above':
        mobile = Product.objects.filter(category='M').filter(discounted_price__gt=10000)    
    else:
        mobile = Product.objects.filter(category='M').filter(brand=data)

    allmobile = Product.objects.filter(category='M').values('brand').distinct()

    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user)) 
    context = {
        'mobile':mobile,
        'allmobile':allmobile,
        'totalitem':totalitem
        } 
      
    return render(request, 'app/mobile.html', context)

def laptop(request, data=None):
    if data == None:
        laptop = Product.objects.filter(category='L')
    elif data == 'below':
        laptop = Product.objects.filter(category='L').filter(discounted_price__lt=35000)
    elif data == 'above':
        laptop = Product.objects.filter(category='L').filter(discounted_price__gt=35000)    
    else:
        laptop = Product.objects.filter(category='L').filter(brand=data)


    alllaptop = Product.objects.filter(category='L').values('brand').distinct()

    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user)) 

    context = {
        'laptop':laptop,
        'alllaptop':alllaptop,
        'totalitem':totalitem
        } 
      
    return render(request, 'app/laptop.html', context)

def topwear(request, data=None):
    if data == None:
        topwear = Product.objects.filter(category='TM')
    elif data == 'below':
        topwear = Product.objects.filter(category='TM').filter(discounted_price__lt=35000)
    elif data == 'above':
        topwear = Product.objects.filter(category='TM').filter(discounted_price__gt=35000)    
    else:
        topwear = Product.objects.filter(category='TM').filter(brand=data)


    alltopwear = Product.objects.filter(category='TM').values('brand').distinct()


    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user)) 

    context = {
        'topwear':topwear,
        'alltopwear':alltopwear,
        'totalitem':totalitem
        } 
      
    return render(request, 'app/topwear.html', context)

def bottomwear(request, data=None):
    if data == None:
        bottomwear = Product.objects.filter(category='BW')
    elif data == 'below':
        bottomwear = Product.objects.filter(category='BW').filter(discounted_price__lt=35000)
    elif data == 'above':
        bottomwear = Product.objects.filter(category='BW').filter(discounted_price__gt=35000)    
    else:
        bottomwear = Product.objects.filter(category='BW').filter(brand=data)


    allbottomwear = Product.objects.filter(category='BW').values('brand').distinct()


    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user)) 
    context = {
        'bottomwear':bottomwear,
        'allbottomwear':allbottomwear,
        'totalitem':totalitem
        } 
      
    return render(request, 'app/bottomwear.html', context)

# def login(request):
#  return render(request, 'app/login.html')

# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')

class CustomerRegistrationView(View):
    def get(self, request):
      form = CoustomerRegistrationFrom()
      context = {'form': form}
      return render(request, 'app/customerregistration.html', context)
    
    def post(self, request):
        form = CoustomerRegistrationFrom(request.POST)
        if form.is_valid():
           messages.success(request, 'Congratulation !! Account Registered Successfully.')
           form.save()
        context = {'form': form}
        return render(request, 'app/customerregistration.html', context)
    
@login_required
def checkout(request):
    if request.method == 'POST':
        user = request.user
        SAForm = ShippingAddressForm(request.POST)
        if SAForm.is_valid():
            location = SAForm.cleaned_data['location']
            name = SAForm.cleaned_data['name']
            phone_number = SAForm.cleaned_data['phone_number']
            state = SAForm.cleaned_data['state']
            payment_method = SAForm.cleaned_data['payment_method']
        else:
            messages.error(request,'Unvalid')
            return redirect("checkout")
    

        cart = Cart.objects.filter(user=user)
        for c in cart:
            OrderPlaced(user=user, location=location, name=name, phone_number=phone_number, state=state, payment_method=payment_method, product=c.product, quantity=c.quantity).save()
            c.delete()

        return redirect("orders")    

    else:
        SAForm = ShippingAddressForm()
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user)) 


        amount = 0.0
        shipping_amount = 70.0  
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
                for p in cart_product:
                    temp_amount = (p.quantity * p.product.discounted_price)
                    amount += temp_amount
                if amount == 0:
                    total_amount = 0.0
                else:    
                    total_amount = shipping_amount + amount
        else:
            messages.error(request,'Please add product before order placed')
            return redirect("show-cart")
                
        context={'SAForm':SAForm, 'cart_items':cart_items, 'total_amount':total_amount, 'totalitem':totalitem}
        return render(request, 'app/checkout.html', context)


