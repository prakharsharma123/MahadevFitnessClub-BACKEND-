from flask import Flask, render_template, request, redirect, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import os
import io

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Use /tmp for writable storage on Render (ephemeral but avoids crashes)
# For persistent data, use a proper DB — see deployment guide
INSTANCE_DIR = os.environ.get('INSTANCE_PATH', os.path.join(BASE_DIR, 'instance'))
os.makedirs(INSTANCE_DIR, exist_ok=True)

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gym_secret_key_mahadev_2025')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///' + os.path.join(INSTANCE_DIR, 'database.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

import calendar

# ---------------- HELPER FOR CALENDAR MONTHS ----------------
def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

# ---------------- PLAN CONFIG ----------------
PLAN_MONTHS = {
    "1_month": 1,
    "3_month": 3,
    "6_month": 6,
    "1_year": 12
}

# ---------------- DATABASE ----------------
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    fees = db.Column(db.Integer)
    joining_date = db.Column(db.String(20))
    last_fee_date = db.Column(db.String(20))
    plan = db.Column(db.String(20))
    payment_done = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

# ---------------- SMS MESSAGE GENERATOR ----------------
def generate_sms_message(name, fees, plan, expiry_date):
    payment_page = f"https://prakharsharma123.github.io/Gym_Payment/?amount={fees}"
    message = f"""MAHADEV FITNESS CLUB
Hello {name},

Your gym fees of Rs.{fees} are due.
Plan: {plan}
Expiry: {expiry_date}

Pay Online: {payment_page}

UPI: ashishrajsngh@ybl
- Team Mahadev"""
    return message

# ---------------- REVENUE CALCULATION ----------------
def calculate_revenue_stats():
    today = datetime.now().date()
    all_members = Member.query.all()
    stats = {
        'total_members': len(all_members),
        'paid_count': 0,
        'unpaid_count': 0,
        'paid_revenue': 0,
        'unpaid_revenue': 0,
        'total_revenue': 0,
        'active_members': 0,
        'expired_members': 0,
        'paid_today_count': 0,
        'paid_today_revenue': 0
    }
    today_str = today.strftime("%Y-%m-%d")
    for m in all_members:
        try:
            last_fee = datetime.strptime(m.last_fee_date, "%Y-%m-%d").date()
            months_to_add = PLAN_MONTHS.get(m.plan, 1)
            expiry = add_months(last_fee, months_to_add)
            days_left = (expiry - today).days
            if m.payment_done and m.last_fee_date == today_str:
                stats['paid_count'] += 1
                stats['paid_revenue'] += m.fees
                stats['paid_today_count'] += 1
                stats['paid_today_revenue'] += m.fees
            elif days_left <= 0:
                stats['unpaid_count'] += 1
                stats['unpaid_revenue'] += m.fees
                stats['expired_members'] += 1
            else:
                stats['active_members'] += 1
            stats['total_revenue'] += m.fees
        except Exception as e:
            print(f"Error calculating stats for {m.name}: {e}")
            continue
    return stats

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = os.environ.get('ADMIN_USERNAME', 'Ashish Singh')
        password = os.environ.get('ADMIN_PASSWORD', 'Ashish@123')
        if request.form["username"] == username and request.form["password"] == password:
            session["user"] = "admin"
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials!")
    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    stats = calculate_revenue_stats()
    return render_template("dashboard.html", stats=stats)

# ---------------- API ENDPOINT FOR REVENUE DATA ----------------
@app.route("/api/revenue")
def api_revenue():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    stats = calculate_revenue_stats()
    return jsonify(stats)

# ---------------- ADD MEMBER ----------------
@app.route("/add", methods=["GET", "POST"])
def add_member():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        member = Member(
            name=request.form["name"],
            phone=request.form["phone"],
            fees=request.form["fees"],
            joining_date=request.form["joining_date"],
            last_fee_date=request.form["last_fee_date"],
            plan=request.form["plan"]
        )
        db.session.add(member)
        db.session.commit()
        return redirect("/members")
    return render_template("add_member.html")

# ---------------- QUICK MARK PAID ----------------
@app.route("/mark_paid/<int:id>")
def mark_paid(id):
    if "user" not in session:
        return redirect("/")
    member = Member.query.get_or_404(id)
    today = datetime.now().strftime("%Y-%m-%d")
    member.payment_done = True
    member.last_fee_date = today
    db.session.commit()
    return redirect("/members")

# ---------------- VIEW MEMBERS ----------------
@app.route("/members")
def members():
    if "user" not in session:
        return redirect("/")
    today = datetime.now().date()
    today_str = today.strftime("%Y-%m-%d")
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')
    query = Member.query
    if search_query:
        query = query.filter(
            (Member.name.ilike(f'%{search_query}%')) |
            (Member.phone.ilike(f'%{search_query}%'))
        )
    all_members = query.all()
    filtered_members = []
    for m in all_members:
        if m.payment_done and m.last_fee_date != today_str:
            m.payment_done = False
            db.session.commit()
        try:
            last_fee = datetime.strptime(m.last_fee_date, "%Y-%m-%d").date()
            months_to_add = PLAN_MONTHS.get(m.plan, 1)
            expiry = add_months(last_fee, months_to_add)
            m.days_left = max((expiry - today).days, 0)
            m.expiry_date = expiry.strftime("%d %b %Y")
            m.sms_message = generate_sms_message(m.name, m.fees, m.plan, m.expiry_date)
        except:
            m.days_left = 0
            m.expiry_date = "N/A"
        include_member = True
        if status_filter == 'paid':
            include_member = (m.payment_done and m.last_fee_date == today_str)
        elif status_filter == 'pending':
            include_member = (m.days_left == 0 and not m.payment_done)
        elif status_filter == 'active':
            include_member = (m.days_left > 0 and not m.payment_done)
        elif status_filter == 'expired':
            include_member = (m.days_left == 0 and not m.payment_done)
        if include_member:
            filtered_members.append(m)
    return render_template("members.html",
                           members=filtered_members,
                           today=today_str,
                           search_query=search_query,
                           status_filter=status_filter)

# ---------------- EDIT MEMBER ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_member(id):
    if "user" not in session:
        return redirect("/")
    m = Member.query.get_or_404(id)
    if request.method == "POST":
        m.name = request.form["name"]
        m.phone = request.form["phone"]
        m.fees = request.form["fees"]
        m.plan = request.form["plan"]
        m.joining_date = request.form["joining_date"]
        m.last_fee_date = request.form["last_fee_date"]
        db.session.commit()
        return redirect("/members")
    return render_template("edit_member.html", m=m)

# ---------------- EXPORT MEMBERS TO EXCEL ----------------
@app.route("/export_members")
def export_members():
    if "user" not in session:
        return redirect("/")
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    today = datetime.now().date()
    all_members = Member.query.all()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Members"
    headers = ["#", "Name", "Phone", "Plan", "Fees (Rs)",
               "Joining Date", "Last Fee Submit Date", "Expiry Date",
               "Days Left", "Status", "Payment Done"]
    ws.append(headers)
    for idx, m in enumerate(all_members, start=1):
        try:
            last_fee = datetime.strptime(m.last_fee_date, "%Y-%m-%d").date()
            months_to_add = PLAN_MONTHS.get(m.plan, 1)
            expiry = add_months(last_fee, months_to_add)
            days_left = (expiry - today).days
            expiry_str = expiry.strftime("%d %b %Y")
        except Exception:
            days_left = 0
            expiry_str = "N/A"
        today_str = today.strftime("%Y-%m-%d")
        if m.payment_done and m.last_fee_date == today_str:
            status = "Paid Today"
        elif days_left > 0:
            status = "Active"
        else:
            status = "Expired"
        row_data = [
            idx, m.name, m.phone, m.plan.replace("_", " ").title(),
            m.fees, m.joining_date, m.last_fee_date, expiry_str,
            max(days_left, 0), status, "Yes" if m.payment_done else "No"
        ]
        ws.append(row_data)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name="members_export.xlsx")

# ---------------- DELETE MEMBER ----------------
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect("/")
    member = Member.query.get(id)
    if member:
        db.session.delete(member)
        db.session.commit()
    return redirect("/members")

# ---------------- PENDING MEMBERS LIST (FOR MANUAL SMS) ----------------
@app.route("/pending_sms")
def pending_sms():
    if "user" not in session:
        return redirect("/")
    today = datetime.now().date()
    all_members = Member.query.filter_by(payment_done=False).all()
    pending_members = []
    for m in all_members:
        try:
            last_fee = datetime.strptime(m.last_fee_date, "%Y-%m-%d").date()
            months_to_add = PLAN_MONTHS.get(m.plan, 1)
            expiry = add_months(last_fee, months_to_add)
            days_left = (expiry - today).days
            if days_left <= 0:
                m.days_left = 0
                m.expiry_date = expiry.strftime("%d %b %Y")
                m.days_overdue = abs(days_left)
                m.sms_message = generate_sms_message(m.name, m.fees, m.plan, m.expiry_date)
                pending_members.append(m)
        except:
            continue
    return render_template("pending_sms.html",
                           pending_members=pending_members,
                           total_pending=len(pending_members))

# ---------------- SEND SMS ----------------
@app.route("/send_sms/<int:id>")
def send_sms(id):
    if "user" not in session:
        return redirect("/")
    member = Member.query.get_or_404(id)
    today = datetime.now().date()
    try:
        last_fee = datetime.strptime(member.last_fee_date, "%Y-%m-%d").date()
        months_to_add = PLAN_MONTHS.get(member.plan, 1)
        expiry = add_months(last_fee, months_to_add)
        expiry_date = expiry.strftime("%d %b %Y")
    except:
        expiry_date = "N/A"
    message = generate_sms_message(member.name, member.fees, member.plan, expiry_date)
    from urllib.parse import quote
    encoded_message = quote(message)
    sms_link = f"sms:{member.phone}?body={encoded_message}"
    return redirect(sms_link)

# ---------------- HEALTH CHECK (keeps Render awake) ----------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
