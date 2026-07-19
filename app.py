from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import pandas as pd
import os


app = Flask(__name__)
app.secret_key = "sales-performance-dashboard-secret-key"  # needed for flash messages


UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


DATA_FILE = "sales_data.csv"
ALLOWED_EXTENSIONS = {"csv"}


# Every dashboard column we need, mapped to the different names
# real-world CSV exports commonly use for the same thing.
# Matching is case-insensitive and ignores spaces/underscores/dashes.
COLUMN_ALIASES = {
    "Date": ["date", "orderdate", "order_date", "saledate", "sale_date", "transactiondate", "invoicedate"],
    "Customer": ["customer", "customername", "customer_name", "client", "clientname", "buyer", "buyername"],
    "Region": ["region", "area", "zone", "territory", "state"],
    "Category": ["category", "productcategory", "product_category", "segment", "type"],
    "Product": ["product", "productname", "product_name", "item", "itemname", "item_name"],
    "Sales": ["sales", "salesamount", "sales_amount", "amount", "revenue", "totalsales", "total_sales", "saleamount", "sale_amount", "grandtotal"],
    "Profit": ["profit", "netprofit", "net_profit", "margin"],
    "Quantity": ["quantity", "qty", "units", "unitsold", "units_sold"],
}


def _normalize(name):
    return str(name).strip().lower().replace(" ", "").replace("_", "").replace("-", "")


def normalize_columns(data):
    """Rename whatever columns the uploaded CSV has to the standard
    column names the dashboard expects, using COLUMN_ALIASES.
    Any column that can't be matched is left untouched."""

    rename_map = {}
    normalized_existing = {_normalize(c): c for c in data.columns}

    for standard_name, aliases in COLUMN_ALIASES.items():
        if standard_name in data.columns:
            continue
        for alias in aliases:
            if alias in normalized_existing:
                rename_map[normalized_existing[alias]] = standard_name
                break

    return data.rename(columns=rename_map)


def ensure_required_columns(data):
    """Guarantee every column the dashboard reads on actually exists,
    filling in sensible defaults for anything missing so the app
    never crashes on a differently-shaped CSV. Returns the fixed
    dataframe plus a list of columns that had to be auto-filled."""

    filled = []

    text_defaults = {
        "Customer": "Unknown",
        "Region": "Unknown",
        "Category": "Unknown",
        "Product": "Unknown",
    }
    numeric_defaults = ["Sales", "Profit", "Quantity"]

    for col, default in text_defaults.items():
        if col not in data.columns:
            data[col] = default
            filled.append(col)
        else:
            data[col] = data[col].fillna(default)

    for col in numeric_defaults:
        if col not in data.columns:
            data[col] = 0
            filled.append(col)
        else:
            data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    if "Date" not in data.columns:
        data["Date"] = pd.NaT
        filled.append("Date")
    else:
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    return data, filled


def load_csv_file(filepath):
    """Read any CSV, map its columns onto the dashboard's expected
    schema, and fill in anything missing. Raises ValueError with a
    friendly message if the file isn't usable at all."""

    try:
        raw = pd.read_csv(filepath)
    except Exception as exc:
        raise ValueError(f"Couldn't read this as a CSV file ({exc}).")

    if raw.empty or len(raw.columns) == 0:
        raise ValueError("The uploaded CSV appears to be empty.")

    mapped = normalize_columns(raw)
    fixed, filled = ensure_required_columns(mapped)

    return fixed, filled


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            data, _ = load_csv_file(DATA_FILE)
            return data
        except ValueError:
            return pd.DataFrame()
    return pd.DataFrame()


df = load_data()


# ---------------- Dashboard ----------------

@app.route("/")
def home():

    global df

    if df.empty:
        data = {
            "total_sales": 0,
            "total_profit": 0,
            "total_orders": 0,
            "total_customers": 0,
            "top_product": "No Data"
        }

        return render_template("dashboard.html", **data)


    total_sales = round(df["Sales"].sum(),2)
    total_profit = round(df["Profit"].sum(),2)
    total_orders = len(df)
    total_customers = df["Customer"].nunique()


    top_product = (
        df.groupby("Product")["Sales"]
        .sum()
        .idxmax()
    )


    # Region Sales

    region_sales = (
        df.groupby("Region")["Sales"]
        .sum()
        .to_dict()
    )


    # Product Sales

    product_sales = (
        df.groupby("Product")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .to_dict()
    )


    # Monthly Sales
    # (Date is already parsed to datetime by load_csv_file; rows where the
    # date couldn't be parsed are simply excluded from this breakdown.)

    valid_dates = df.dropna(subset=["Date"])

    monthly_sales = (
        valid_dates.groupby(valid_dates["Date"].dt.strftime("%B"))["Sales"]
        .sum()
        .to_dict()
    )


    return render_template(
        "dashboard.html",
        total_sales=total_sales,
        total_profit=total_profit,
        total_orders=total_orders,
        total_customers=total_customers,
        top_product=top_product,
        region_sales=region_sales,
        product_sales=product_sales,
        monthly_sales=monthly_sales
    )



# ---------------- Analytics ----------------


@app.route("/analytics")
def analytics():

    global df

    if df.empty:
        return render_template(
            "analytics.html",
            products={},
            regions={}
        )


    products = (
        df.groupby("Product")["Sales"]
        .sum()
        .to_dict()
    )


    regions = (
        df.groupby("Region")["Sales"]
        .sum()
        .to_dict()
    )


    return render_template(
        "analytics.html",
        products=products,
        regions=regions
    )



# ---------------- Reports ----------------


@app.route("/reports")
def reports():

    global df


    summary = {}

    if not df.empty:

        summary = {
            "Sales": df["Sales"].sum(),
            "Profit": df["Profit"].sum(),
            "Orders": len(df),
            "Customers": df["Customer"].nunique()
        }


    return render_template(
        "reports.html",
        summary=summary
    )



# ---------------- Upload ----------------


@app.route("/upload", methods=["GET","POST"])
def upload():

    global df


    if request.method=="POST":

        if "file" not in request.files:
            flash("No file was selected.")
            return redirect(request.url)


        file=request.files["file"]


        if file.filename=="":
            flash("No file was selected.")
            return redirect(request.url)


        if not allowed_file(file.filename):
            flash("Please upload a .csv file.")
            return redirect(request.url)


        filepath=os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )


        file.save(filepath)


        try:
            new_df, filled_columns = load_csv_file(filepath)
        except ValueError as exc:
            flash(f"Couldn't process this file: {exc}")
            return redirect(request.url)


        df = new_df

        if filled_columns:
            flash(
                "File uploaded. Note: these columns weren't found in your "
                f"CSV so default values were used: {', '.join(filled_columns)}."
            )
        else:
            flash("File uploaded successfully.")


        return redirect(url_for("home"))


    return render_template("upload.html")



# ---------------- API For Charts ----------------


@app.route("/chart-data")
def chart_data():

    global df


    if df.empty:
        return jsonify({})


    data={

        "region":
        df.groupby("Region")["Sales"].sum().to_dict(),


        "product":
        df.groupby("Product")["Sales"].sum().to_dict(),


        "category":
        df.groupby("Category")["Sales"].sum().to_dict()

    }


    return jsonify(data)



if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)