from prometheus_client import Counter, Histogram


orders_created_total = Counter(
    "my_eats_orders_created_total",
    "Total number of successfully created orders",
)

orders_revenue_total = Counter(
    "my_eats_orders_revenue_total",
    "Total value of successfully created orders",
)

order_creation_errors_total = Counter(
    "my_eats_order_creation_errors_total",
    "Total number of failed order creation attempts",
    labelnames=("reason",),
)

order_status_changes_total = Counter(
    "my_eats_order_status_changes_total",
    "Total number of order status changes",
    labelnames=("from_status", "to_status"),
)

order_creation_duration_seconds = Histogram(
    "my_eats_order_creation_duration_seconds",
    "Time spent creating an order",
)
