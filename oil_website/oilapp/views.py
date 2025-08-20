from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.views.decorators.http import require_POST

def product_list(request):
    products = Product.objects.all()
    return render(request, "oilapp/product_list.html", {"products": products})

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get("cart", {})
    pid = str(product.id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session["cart"] = cart
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def view_cart(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total = Decimal('0.00')

    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str)
            product = Product.objects.get(pk=pid)
            subtotal = product.price * qty
            total += subtotal
            cart_items.append({
                "product": product,
                "quantity": qty,
                "subtotal": subtotal
            })
        except Product.DoesNotExist:
            continue

    return render(request, "oilapp/cart.html", {"cart_items": cart_items, "total": total})

@require_POST
def update_cart(request, product_id):
    qty = int(request.POST.get("quantity", 0))
    cart = request.session.get("cart", {})
    pid = str(product_id)
    if qty > 0:
        cart[pid] = qty
    else:
        cart.pop(pid, None)
    request.session["cart"] = cart
    return redirect("view_cart")

@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    pid = str(product_id)

    if pid in cart:
        if cart[pid] > 1:
            cart[pid] -= 1   # decrease by 1
        else:
            cart.pop(pid, None)  # remove if only 1 left

    request.session["cart"] = cart
    return redirect("view_cart")
