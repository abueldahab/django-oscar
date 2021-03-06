from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from oscar.apps.address.forms import UserAddressForm
from oscar.view.generic import ModelView
from oscar.core.loading import import_module
import_module('address.models', ['UserAddress'], locals())
import_module('order.models', ['Order', 'Line'], locals())
import_module('basket.models', ['Basket'], locals())
import_module('basket.factory', ['BasketFactory'], locals())

@login_required
def profile(request):
    u"""Return a customers's profile"""
    # Load last 5 orders as preview
    orders = Order._default_manager.filter(user=request.user)[0:5]
    return render(request, 'oscar/customer/profile.html', locals())
    
        
class OrderHistoryView(ListView):
    u"""Customer order history"""
    context_object_name = "orders"
    template_name = 'oscar/customer/order-history.html'
    paginate_by = 20

    def get_queryset(self):
        u"""Return a customer's orders"""
        return Order._default_manager.filter(user=self.request.user)


class OrderDetailView(ModelView):
    u"""Customer order details"""
    template_file = "oscar/customer/order.html"
    
    def get_model(self):
        u"""Return an order object or 404"""
        return get_object_or_404(Order, user=self.request.user, number=self.kwargs['order_number'])
    
    def handle_GET(self, order):
        self.response = render(self.request, self.template_file, locals())
        
        
class OrderLineView(ModelView):
    u"""Customer order line"""
    
    def get_model(self):
        u"""Return an order object or 404"""
        order = get_object_or_404(Order, user=self.request.user, number=self.kwargs['order_number'])
        return order.lines.get(id=self.kwargs['line_id'])
    
    def handle_GET(self, line):
        return HttpResponseRedirect(reverse('oscar-customer-order-view', kwargs={'order_number': line.order.number}))
    
    def handle_POST(self, line):
        self.response = HttpResponseRedirect(reverse('oscar-customer-order-view', kwargs={'order_number': line.order.number}))
        super(OrderLineView, self).handle_POST(line)
    
    def do_reorder(self, line):
        # Get basket
        basket = BasketFactory().get_or_create_open_basket(self.request, self.response)
        if not line.product:
            return
        
        # Convert line attributes into basket options
        options = []
        for attribute in line.attributes.all():
            if attribute.option:
                options.append({'option': attribute.option, 'value': attribute.value})
        basket.add_product(line.product, 1, options)
        messages.info(self.request, "Line reordered")
        self.response = HttpResponseRedirect(reverse('oscar-basket'))
        

class AddressBookView(ListView):
    u"""Customer address book"""
    context_object_name = "addresses"
    template_name = 'oscar/customer/address-book.html'
    paginate_by = 40
        
    def get_queryset(self):
        u"""Return a customer's addresses"""
        return UserAddress._default_manager.filter(user=self.request.user)
    
    
class AddressView(ModelView):
    u"""Customer address view"""
    template_file = "oscar/customer/address-form.html"
    
    def get_model(self):
        u"""Return an address object or a 404"""
        return get_object_or_404(UserAddress, user=self.request.user, pk=self.kwargs['address_id'])
    
    def handle_GET(self, address):
        form = UserAddressForm(instance=address)
        self.response = render(self.request, self.template_file, locals())
        
    def do_save(self, address):
        u"""Save an address"""
        form = UserAddressForm(self.request.POST, instance=address)
        if form.is_valid():
            a = form.save()
            self.response = HttpResponseRedirect(reverse('oscar-customer-address-book'))
        else:
            self.response = render(self.request, self.template_file, locals())
            
    def do_delete(self, address):
        u"""Delete an address"""
        address.delete()
        self.response = HttpResponseRedirect(reverse('oscar-customer-address-book'))
            