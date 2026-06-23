from apps.products.models import Item
from apps.orders.models import Order
from apps.payments.models import Payment
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone

User = get_user_model()

def dashboard_callback(request, context):
    # Total stats
    total_products = Item.objects.count()
    total_users = User.objects.count()
    
    # Ordered orders
    ordered_orders = Order.objects.filter(ordered=True)
    total_orders = ordered_orders.count()
    
    # Calculate total revenue
    total_revenue = 0
    for order in ordered_orders:
        try:
            total_revenue += order.get_total()
        except Exception:
            pass
            
    # Refund status
    pending_refunds = Order.objects.filter(refund_requested=True, refund_granted=False).count()
    
    # Recent orders
    recent_orders = Order.objects.order_by('-id')[:5]

    # Calculate monthly revenue for last 6 months
    now = timezone.now()
    monthly_revenue = []
    month_names = []
    
    for i in range(5, -1, -1):
        y = now.year
        m = now.month - i
        while m <= 0:
            m += 12
            y -= 1
            
        start_of_month = timezone.make_aware(datetime.datetime(y, m, 1))
        if m == 12:
            end_of_month = timezone.make_aware(datetime.datetime(y + 1, 1, 1))
        else:
            end_of_month = timezone.make_aware(datetime.datetime(y, m + 1, 1))
            
        # Sum payments in this month range
        payments = Payment.objects.filter(timestamp__gte=start_of_month, timestamp__lt=end_of_month)
        month_sum = sum(p.amount for p in payments)
        
        monthly_revenue.append(round(month_sum, 2))
        month_names.append(start_of_month.strftime('%b'))
    
    context.update({
        "total_products": total_products,
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "pending_refunds": pending_refunds,
        "recent_orders": recent_orders,
        "monthly_revenue": monthly_revenue,
        "month_names": month_names,
    })
    return context
