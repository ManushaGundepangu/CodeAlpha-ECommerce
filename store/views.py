from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db.models import Q, Sum, Avg

from .models import (
    Product,
    CartItem,
    Order,
    OrderItem,
    Category,
    Wishlist,
    Review
)

def home(request):

    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()

    products = Product.objects.all()
    categories = Category.objects.all()

    selected_category = None

    # Search
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Category filter
    if category_id:
        if category_id.isdigit():
            selected_category = Category.objects.filter(
                id=int(category_id)
            ).first()

            if selected_category:
                products = products.filter(
                    category=selected_category
                )

    # Cart count
    cart_count = 0

    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(
            user=request.user
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0

    # Wishlist
    wishlist_products = []

    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list(
            'product_id',
            flat=True
        )

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'cart_count': cart_count,
        'search_query': search_query,
        'selected_category': selected_category,
        'wishlist_products': wishlist_products,
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    reviews = product.reviews.select_related(
        'user'
    ).all()

    average_rating = reviews.aggregate(
        average=Avg('rating')
    )['average']

    review_count = reviews.count()

    user_review = None

    if request.user.is_authenticated:
        user_review = reviews.filter(
            user=request.user
        ).first()

    return render(
        request,
        'product_detail.html',
        {
            'product': product,
            'reviews': reviews,
            'average_rating': average_rating,
            'review_count': review_count,
            'user_review': user_review,
        }
    )


@login_required(login_url='login')
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1

    cart_item.save()

    return redirect('cart')

@login_required(login_url='login')
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    total = sum(item.total_price() for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():

            return render(request, 'register.html', {
                'error': 'Username already exists.'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('home')

    return render(request, 'register.html')

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('home')

        return render(request, 'login.html', {
            'error': 'Invalid username or password.'
        })

    return render(request, 'login.html')


def user_logout(request):

    from django.contrib.auth import logout

    logout(request)

    return redirect('home')

@login_required(login_url='login')
def remove_from_cart(request, id):
    cart_item = get_object_or_404(
        CartItem,
        id=id,
        user=request.user
    )

    cart_item.delete()

    return redirect('cart')



@login_required(login_url='login')
def update_cart(request, id):
    cart_item = get_object_or_404(
        CartItem,
        id=id,
        user=request.user
    )

    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')

@login_required(login_url='login')
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart')

    total = sum(item.total_price() for item in cart_items)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        phone = request.POST.get('phone')

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            address=address,
            city=city,
            phone=phone,
            total_amount=total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()

        return redirect('order_success', order_id=order.id)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required(login_url='login')
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, 'order_success.html', {
        'order': order
    })
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'my_orders.html', {
        'orders': orders
    })


@login_required(login_url='login')
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required(login_url='login')
def remove_from_wishlist(request, id):
    wishlist_item = get_object_or_404(
        Wishlist,
        id=id,
        user=request.user
    )

    wishlist_item.delete()

    return redirect('wishlist')


@login_required(login_url='login')
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product')

    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items
    })


def category_products(request, id):
    category = get_object_or_404(Category, id=id)

    products = Product.objects.filter(
        category=category
    )

    return render(request, 'category_products.html', {
        'category': category,
        'products': products,
    })



@login_required(login_url='login')
def add_review(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            rating = 0

        if 1 <= rating <= 5 and comment:
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )

    return redirect('product_detail', id=id)


@login_required(login_url='login')
def delete_review(request, id):
    review = get_object_or_404(
        Review,
        id=id,
        user=request.user
    )

    product_id = review.product.id

    if request.method == 'POST':
        review.delete()

    return redirect(
        'product_detail',
        id=product_id
    )