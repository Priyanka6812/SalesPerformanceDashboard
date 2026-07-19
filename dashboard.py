from flask import Blueprint, render_template, session, redirect, url_for
from models import Sales

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/")
def home():
    return redirect(url_for("dashboard.dashboard"))


@dashboard.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    total_sales = 0
    total_profit = 0
    total_orders = 0
    total_customers = 0

    sales = Sales.query.all()

    total_orders = len(sales)

    customers = set()

    for row in sales:

        total_sales += row.sales or 0

        total_profit += row.profit or 0

        if row.customer:
            customers.add(row.customer)

    total_customers = len(customers)

    recent_sales = Sales.query.order_by(Sales.id.desc()).limit(10).all()

    return render_template(
        "dashboard.html",
        total_sales=round(total_sales, 2),
        total_profit=round(total_profit, 2),
        total_orders=total_orders,
        total_customers=total_customers,
        recent_sales=recent_sales
    )