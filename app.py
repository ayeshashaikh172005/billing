import os
import json
from datetime import datetime
from io import BytesIO
from functools import wraps

from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from werkzeug.security import check_password_hash, generate_password_hash
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
try:
    from flask_cors import CORS
except ModuleNotFoundError:
    CORS = None

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///invoice_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["FIXED_ADMIN_EMAIL"] = os.getenv("FIXED_ADMIN_EMAIL", "admin@techcraftery.com").strip().lower()
app.config["FIXED_ADMIN_PASSWORD"] = os.getenv("FIXED_ADMIN_PASSWORD", "admin@123")
app.config["FIXED_ADMIN_NAME"] = os.getenv("FIXED_ADMIN_NAME", "admin")
app.config["FIXED_ADMIN_USERID"] = os.getenv("FIXED_ADMIN_USERID", "admin").strip().lower()
db = SQLAlchemy(app)
if CORS:
    CORS(app, supports_credentials=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    gstin = db.Column(db.String(20))
    company_name = db.Column(db.String(150))
    address = db.Column(db.Text)
    party_type = db.Column(db.String(20), default="customer")


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prod_type = db.Column(db.String(20), default="Product")
    price = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(10))


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    due_date = db.Column(db.String(20))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    total_amount = db.Column(db.Float, default=0.0)
    items = db.relationship("InvoiceItem", backref="invoice", lazy=True, cascade="all, delete-orphan")


class InvoiceMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoice.id"), unique=True, nullable=False)
    data_json = db.Column(db.Text, default="{}")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_type = db.Column(db.String(40), nullable=False, index=True)
    doc_number = db.Column(db.String(80), nullable=False, index=True)
    date = db.Column(db.String(20))
    due_date = db.Column(db.String(20))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    total_amount = db.Column(db.Float, default=0.0)
    meta_json = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship("DocRecordItem", backref="doc", lazy=True, cascade="all, delete-orphan")


class DocRecordItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey("doc_record.id"))
    product_name = db.Column(db.String(120))
    quantity = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)


class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoice.id"))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)


class Quotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quotation_number = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    valid_until = db.Column(db.String(20))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    total_amount = db.Column(db.Float, default=0.0)
    items = db.relationship("QuotationItem", backref="quotation", lazy=True, cascade="all, delete-orphan")


class QuotationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey("quotation.id"))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)


class ProFormaInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pfi_number = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    total_amount = db.Column(db.Float, default=0.0)
    items = db.relationship("ProFormaItem", backref="pro_forma", lazy=True, cascade="all, delete-orphan")


class ProFormaItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pfi_id = db.Column(db.Integer, db.ForeignKey("pro_forma_invoice.id"))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)


class Challan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challan_number = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    total_amount = db.Column(db.Float, default=0.0)
    items = db.relationship("ChallanItem", backref="challan", lazy=True, cascade="all, delete-orphan")


class ChallanItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challan_id = db.Column(db.Integer, db.ForeignKey("challan.id"))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)


class CreditNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_number = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    total_amount = db.Column(db.Float, default=0.0)
    items = db.relationship("CreditNoteItem", backref="credit_note", lazy=True, cascade="all, delete-orphan")


class CreditNoteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credit_note_id = db.Column(db.Integer, db.ForeignKey("credit_note.id"))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_number = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    vendor_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    total_amount = db.Column(db.Float, default=0.0)
    items = db.relationship("PurchaseItem", backref="purchase", lazy=True, cascade="all, delete-orphan")


class PurchaseItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchase.id"))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)


class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    vendor_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    total_amount = db.Column(db.Float, default=0.0)
    items = db.relationship("POItem", backref="purchase_order", lazy=True, cascade="all, delete-orphan")


class POItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey("purchase_order.id"))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.String(20))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    is_paid = db.Column(db.Boolean, default=True)


class IndirectIncome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    income_date = db.Column(db.String(20))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    is_received = db.Column(db.Boolean, default=True)


def payload():
    return request.get_json(silent=True) or {}


def required(data, fields):
    missing = [f for f in fields if not data.get(f)]
    return (jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400) if missing else None


def line_total(items):
    return round(sum(float(i.get("quantity", 0)) * float(i.get("unit_price", 0)) for i in items), 2)


def current_session_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)


def admin_api_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        u = current_session_user()
        if not u:
            return jsonify({"error": "Unauthorized"}), 401
        if (u.role or "user").lower() != "admin":
            return jsonify({"error": "Forbidden"}), 403
        if not bool(u.is_active):
            session.clear()
            return jsonify({"error": "Account is blocked"}), 403
        return fn(*args, **kwargs)

    return wrapper


def require_admin_for_bill_mutation():
    u = current_session_user()
    if not u:
        return jsonify({"error": "Unauthorized"}), 401
    if not bool(u.is_active):
        session.clear()
        return jsonify({"error": "Account is blocked"}), 403
    return None


def item_dict(item):
    return {
        "id": item.id,
        "product_name": item.product_name,
        "quantity": item.quantity,
        "unit_price": item.unit_price,
        "line_total": round((item.quantity or 0) * (item.unit_price or 0), 2),
    }


def get_invoice_meta(invoice_id):
    row = InvoiceMeta.query.filter_by(invoice_id=invoice_id).first()
    if not row or not row.data_json:
        return {}
    try:
        data = json.loads(row.data_json)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def set_invoice_meta(invoice_id, meta):
    if not isinstance(meta, dict):
        return
    row = InvoiceMeta.query.filter_by(invoice_id=invoice_id).first()
    if not row:
        row = InvoiceMeta(invoice_id=invoice_id)
        db.session.add(row)
    row.data_json = json.dumps(meta, ensure_ascii=True)


def parse_json_text(txt):
    if not txt:
        return {}
    try:
        data = json.loads(txt)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def draw_pdf_logo(pdf_canvas, page_height):
    logo_path = os.path.join(app.root_path, "static", "logo2.jpg")
    if not os.path.isfile(logo_path):
        return None
    try:
        img = ImageReader(logo_path)
        x = 40
        y = page_height - 95
        w = 130
        h = 48
        pdf_canvas.drawImage(img, x, y, width=w, height=h, preserveAspectRatio=True, mask="auto")
        return {"x": x, "y": y, "w": w, "h": h}
    except Exception:
        return None


def safe_txt(value):
    return str(value or "-")


def render_modern_pdf(
    pdf_canvas,
    page_size,
    title,
    number,
    date_value,
    due_value,
    party,
    items,
    meta,
    subtotal,
    total,
    footer_text,
):
    width, height = page_size
    margin = 30
    box_x = margin
    box_y = 28
    box_w = width - (margin * 2)
    box_h = height - 56

    table_cols = {
        "item": box_x + 14,
        "qty": box_x + box_w * 0.54,
        "rate": box_x + box_w * 0.69,
        "amount": box_x + box_w * 0.86,
    }

    def draw_page_header():
        pdf_canvas.setFillColor(colors.white)
        pdf_canvas.setStrokeColor(colors.HexColor("#2754C4"))
        pdf_canvas.setLineWidth(1.2)
        pdf_canvas.roundRect(box_x, box_y, box_w, box_h, 18, stroke=1, fill=1)

        logo_box = draw_pdf_logo(pdf_canvas, height - 8)

        pdf_canvas.setFillColor(colors.HexColor("#111827"))
        pdf_canvas.setFont("Helvetica-Bold", 21)
        pdf_canvas.drawCentredString(width / 2, height - 65, safe_txt(title))

        pdf_canvas.setFont("Helvetica", 11)
        pdf_canvas.setFillColor(colors.HexColor("#1F2937"))
        pdf_canvas.drawRightString(box_x + box_w - 16, height - 62, f"No: {safe_txt(number)}")
        pdf_canvas.drawRightString(box_x + box_w - 16, height - 83, f"Date: {safe_txt(date_value)}")
        pdf_canvas.drawRightString(box_x + box_w - 16, height - 102, f"Due: {safe_txt(due_value)}")

        if logo_box:
            y_line = min(height - 112, logo_box["y"] - 8)
        else:
            y_line = height - 112
        pdf_canvas.setStrokeColor(colors.HexColor("#D1D5DB"))
        pdf_canvas.setLineWidth(0.8)
        pdf_canvas.line(box_x + 12, y_line, box_x + box_w - 12, y_line)
        return y_line - 18

    def draw_table_header(y_pos):
        pdf_canvas.setFillColor(colors.HexColor("#1F2A44"))
        pdf_canvas.rect(box_x + 12, y_pos - 16, box_w - 24, 20, fill=1, stroke=0)
        pdf_canvas.setFont("Helvetica-Bold", 10.5)
        pdf_canvas.setFillColor(colors.white)
        pdf_canvas.drawString(table_cols["item"], y_pos - 11, "Item")
        pdf_canvas.drawString(table_cols["qty"], y_pos - 11, "Qty")
        pdf_canvas.drawString(table_cols["rate"], y_pos - 11, "Rate")
        pdf_canvas.drawString(table_cols["amount"], y_pos - 11, "Amount")
        return y_pos - 24

    y = draw_page_header()

    party_lines = [safe_txt(party.name if party else "Customer")]
    if party and party.company_name:
        party_lines.append(f"Company: {safe_txt(party.company_name)}")
    if party and party.phone:
        party_lines.append(f"Phone: {safe_txt(party.phone)}")
    if party and party.email:
        party_lines.append(f"Email: {safe_txt(party.email)}")
    if party and party.gstin:
        party_lines.append(f"GSTIN: {safe_txt(party.gstin)}")
    if meta.get("dispatch"):
        party_lines.append(f"Dispatch: {safe_txt(meta.get('dispatch'))}")
    if meta.get("bank_name"):
        party_lines.append(f"Bank: {safe_txt(meta.get('bank_name'))}")
    bdet = meta.get("bank_details") or {}
    if isinstance(bdet, dict):
        if bdet.get("ifsc"):
            party_lines.append(f"IFSC: {safe_txt(bdet.get('ifsc'))}")
        if bdet.get("account_no"):
            party_lines.append(f"Account: {safe_txt(bdet.get('account_no'))}")
        if bdet.get("upi"):
            party_lines.append(f"UPI: {safe_txt(bdet.get('upi'))}")
        if bdet.get("branch"):
            party_lines.append(f"Branch: {safe_txt(bdet.get('branch'))}")
    if meta.get("signature_name"):
        party_lines.append(f"Signature: {safe_txt(meta.get('signature_name'))}")

    party_box_h = max(88, 22 + (len(party_lines) * 14))
    pdf_canvas.setFillColor(colors.HexColor("#F8FAFC"))
    pdf_canvas.setStrokeColor(colors.HexColor("#E5E7EB"))
    pdf_canvas.roundRect(box_x + 12, y - party_box_h, box_w - 24, party_box_h, 8, stroke=1, fill=1)
    pdf_canvas.setFillColor(colors.HexColor("#111827"))
    pdf_canvas.setFont("Helvetica-Bold", 13)
    pdf_canvas.drawString(box_x + 20, y - 22, "Bill To")
    pdf_canvas.setFont("Helvetica", 11.5)
    line_y = y - 40
    for line in party_lines:
        pdf_canvas.drawString(box_x + 20, line_y, safe_txt(line)[:104])
        line_y -= 14

    y = y - party_box_h - 20
    y = draw_table_header(y)

    pdf_canvas.setStrokeColor(colors.HexColor("#E5E7EB"))
    pdf_canvas.setFillColor(colors.HexColor("#111827"))
    pdf_canvas.setFont("Helvetica", 10.5)

    rows = items or []
    if not rows:
        pdf_canvas.drawString(table_cols["item"], y - 4, "No items added")
        y -= 18
    else:
        for idx, item in enumerate(rows):
            if y < 115:
                pdf_canvas.setFont("Helvetica", 9)
                pdf_canvas.setFillColor(colors.HexColor("#6B7280"))
                pdf_canvas.drawString(box_x + 14, box_y + 10, "System generated document")
                pdf_canvas.showPage()
                y = draw_page_header()
                y = draw_table_header(y)
                pdf_canvas.setStrokeColor(colors.HexColor("#E5E7EB"))
                pdf_canvas.setFillColor(colors.HexColor("#111827"))
                pdf_canvas.setFont("Helvetica", 10.5)

            if idx % 2 == 0:
                pdf_canvas.setFillColor(colors.HexColor("#FBFDFF"))
                pdf_canvas.rect(box_x + 12, y - 14, box_w - 24, 16, fill=1, stroke=0)
                pdf_canvas.setFillColor(colors.HexColor("#111827"))

            qty = float(getattr(item, "quantity", 0) or 0)
            rate = float(getattr(item, "unit_price", 0) or 0)
            amount = round(qty * rate, 2)
            name = safe_txt(getattr(item, "product_name", "Item"))[:52]

            pdf_canvas.drawString(table_cols["item"], y - 3, name)
            pdf_canvas.drawString(table_cols["qty"], y - 3, f"{qty:g}")
            pdf_canvas.drawString(table_cols["rate"], y - 3, f"{rate:,.2f}")
            pdf_canvas.drawString(table_cols["amount"], y - 3, f"{amount:,.2f}")
            pdf_canvas.setStrokeColor(colors.HexColor("#ECEFF4"))
            pdf_canvas.line(box_x + 12, y - 16, box_x + box_w - 12, y - 16)
            y -= 17

    y -= 10
    totals_w = 230
    totals_x = box_x + box_w - totals_w - 12
    pdf_canvas.setFillColor(colors.HexColor("#F8FAFC"))
    pdf_canvas.setStrokeColor(colors.HexColor("#E5E7EB"))
    pdf_canvas.roundRect(totals_x, y - 52, totals_w, 52, 8, stroke=1, fill=1)
    pdf_canvas.setFillColor(colors.HexColor("#111827"))
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawRightString(totals_x + totals_w - 10, y - 18, f"Subtotal: INR {subtotal:,.2f}")
    pdf_canvas.setFont("Helvetica-Bold", 13)
    pdf_canvas.drawRightString(totals_x + totals_w - 10, y - 38, f"Total: INR {total:,.2f}")

    y -= 68
    extras = [
        ("Reference", meta.get("reference")),
        ("Payment Terms", meta.get("payment_terms")),
        ("Notes", meta.get("notes")),
        ("Terms", meta.get("terms")),
    ]
    for label, value in extras:
        if not value:
            continue
        txt = f"{label}: {safe_txt(value)}"
        pdf_canvas.setFont("Helvetica", 10.5 if label != "Terms" else 10)
        pdf_canvas.setFillColor(colors.HexColor("#374151"))
        while txt:
            if y < 90:
                pdf_canvas.setFont("Helvetica", 9)
                pdf_canvas.setFillColor(colors.HexColor("#6B7280"))
                pdf_canvas.drawString(box_x + 14, box_y + 10, footer_text)
                pdf_canvas.showPage()
                y = draw_page_header()
                pdf_canvas.setFont("Helvetica", 10.5 if label != "Terms" else 10)
                pdf_canvas.setFillColor(colors.HexColor("#374151"))
            pdf_canvas.drawString(box_x + 14, y, txt[:120])
            txt = txt[120:]
            y -= 13
        y -= 2

    pdf_canvas.setFont("Helvetica", 9)
    pdf_canvas.setFillColor(colors.HexColor("#6B7280"))
    pdf_canvas.drawString(box_x + 14, box_y + 10, footer_text)


def doc_record_to_dict(row):
    return {
        "id": row.id,
        "doc_type": row.doc_type,
        "number": row.doc_number,
        "date": row.date,
        "due_date": row.due_date,
        "customer_id": row.customer_id,
        "total_amount": row.total_amount,
        "meta": parse_json_text(row.meta_json),
        "items": [
            {
                "id": i.id,
                "product_name": i.product_name,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
                "line_total": round((i.quantity or 0) * (i.unit_price or 0), 2),
            }
            for i in row.items
        ],
    }


def doc_to_dict(doc, num_field, party_field, item_rel):
    party_id = getattr(doc, party_field, None)
    party = Customer.query.get(party_id) if party_id else None
    out = {
        "id": doc.id,
        "number": getattr(doc, num_field),
        "date": getattr(doc, "date", None),
        "due_date": getattr(doc, "due_date", None),
        "valid_until": getattr(doc, "valid_until", None),
        "total_amount": doc.total_amount,
        "party_id": party_id,
        "party_name": party.name if party else None,
        "items": [item_dict(i) for i in getattr(doc, item_rel)],
    }
    if isinstance(doc, Invoice):
        out["meta"] = get_invoice_meta(doc.id)
    return out


def create_doc(model, item_model, num_field, party_field, prefix):
    data = payload()
    miss = required(data, [party_field])
    if miss:
        return miss
    items = data.get("items", [])
    if not isinstance(items, list):
        return jsonify({"error": "items must be a list"}), 400
    number = data.get(num_field) or f"{prefix}-{model.query.count() + 1}"
    exists = model.query.filter_by(**{num_field: number}).first()
    if exists:
        return jsonify({"id": exists.id, "number": number, "message": "Already exists"}), 200
    total = float(data.get("total_amount", line_total(items)) or 0)
    row = model(**{num_field: number, "date": data.get("date"), party_field: data.get(party_field), "total_amount": total})
    if "due_date" in model.__table__.columns:
        row.due_date = data.get("due_date")
    if "valid_until" in model.__table__.columns:
        row.valid_until = data.get("valid_until")
    db.session.add(row)
    db.session.flush()
    fk = list(item_model.__table__.columns.keys())[1]
    for i in items:
        db.session.add(
            item_model(
                **{
                    fk: row.id,
                    "product_name": i.get("product_name") or i.get("name"),
                    "quantity": float(i.get("quantity", 0) or 0),
                    "unit_price": float(i.get("unit_price", i.get("price", 0)) or 0),
                }
            )
        )
    db.session.commit()
    return jsonify({"id": row.id, "number": number, "message": "Saved"}), 201


def doc_detail(model, num_field, party_field, item_rel, rid):
    row = model.query.get_or_404(rid)
    if request.method == "GET":
        return jsonify(doc_to_dict(row, num_field, party_field, item_rel))
    deny = require_admin_for_bill_mutation()
    if deny:
        return deny
    if isinstance(row, Invoice):
        InvoiceMeta.query.filter_by(invoice_id=row.id).delete()
    db.session.delete(row)
    db.session.commit()
    return jsonify({"message": "Deleted"})


@app.route("/")
def home():
    return redirect(url_for("dashboard") if session.get("user_id") else url_for("login"))


@app.route("/login")
def login():
    return render_template("auth.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/admin")
def admin_panel():
    u = current_session_user()
    if not u:
        return redirect(url_for("login"))
    if (u.role or "user").lower() != "admin":
        return redirect(url_for("dashboard"))
    if not bool(u.is_active):
        session.clear()
        return redirect(url_for("login"))
    return redirect(url_for("admin_users_page"))


@app.route("/admin/users")
def admin_users_page():
    u = current_session_user()
    if not u:
        return redirect(url_for("login"))
    if (u.role or "user").lower() != "admin":
        return redirect(url_for("dashboard"))
    if not bool(u.is_active):
        session.clear()
        return redirect(url_for("login"))
    return render_template("admin.html", admin_view="users")


@app.route("/admin/docs")
def admin_docs_page():
    u = current_session_user()
    if not u:
        return redirect(url_for("login"))
    if (u.role or "user").lower() != "admin":
        return redirect(url_for("dashboard"))
    if not bool(u.is_active):
        session.clear()
        return redirect(url_for("login"))
    return render_template("admin.html", admin_view="docs")


@app.route("/<path:page>")
def page_router(page):
    if page.startswith("api/"):
        abort(404)
    choices = [page] if page.endswith(".html") else [page, f"{page}.html"]
    doc_pages = {
        "invoice.html": "invoice",
        "purchase.html": "purchase",
        "quotation.html": "quotation",
        "challan.html": "challan",
        "creditnote.html": "credit_note",
        "porder.html": "purchase_order",
        "proforma.html": "proforma",
        "expenses.html": "expenses",
        "indirectincome.html": "indirect_income",
    }
    for name in choices:
        if name == "admin.html":
            return redirect(url_for("admin_panel"))
        if name in doc_pages:
            return render_template("invoice.html", doc_kind=doc_pages[name])
        if os.path.isfile(os.path.join(app.template_folder or "templates", name)):
            return render_template(name)
    abort(404)


@app.route("/register", methods=["POST"])
def register():
    data = payload()
    miss = required(data, ["name", "email", "password"])
    if miss:
        return miss
    email = data["email"].strip().lower()
    role = (data.get("role") or "user").strip().lower()
    if role not in ("user", "admin"):
        role = "user"
    fixed_admin_email = app.config["FIXED_ADMIN_EMAIL"]
    if email == fixed_admin_email:
        return jsonify({"error": "This email is reserved for fixed admin login"}), 403
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409
    u = User(name=data["name"].strip(), email=email, password_hash=generate_password_hash(data["password"]), role=role)
    db.session.add(u)
    db.session.commit()
    session["user_id"] = u.id
    return jsonify(
        {
            "message": "Registration successful",
            "user_id": u.id,
            "user": {"id": u.id, "name": u.name, "email": u.email, "role": u.role or "user", "is_active": bool(u.is_active)},
        }
    ), 201


@app.route("/login-direct", methods=["POST"])
def login_direct():
    data = payload()
    miss = required(data, ["email", "password"])
    if miss:
        return miss
    raw_identifier = (data.get("email") or data.get("identifier") or "").strip()
    identifier = raw_identifier.lower()
    fixed_admin_userid = app.config.get("FIXED_ADMIN_USERID", "admin").strip().lower()
    fixed_admin_email = app.config["FIXED_ADMIN_EMAIL"]
    lookup_email = fixed_admin_email if identifier == fixed_admin_userid else identifier
    u = User.query.filter_by(email=lookup_email).first()
    if not u or not check_password_hash(u.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    if not bool(u.is_active):
        return jsonify({"error": "Account is blocked. Contact admin."}), 403
    session["user_id"] = u.id
    return jsonify(
        {
            "message": "Login successful",
            "user": {"id": u.id, "name": u.name, "email": u.email, "role": u.role or "user", "is_active": bool(u.is_active)},
        }
    )


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login")) if request.method == "GET" else jsonify({"message": "Logged out"})


@app.route("/me", methods=["GET"])
def me():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"authenticated": False}), 401
    u = User.query.get(uid)
    if not u:
        session.clear()
        return jsonify({"authenticated": False}), 401
    if not bool(u.is_active):
        session.clear()
        return jsonify({"authenticated": False}), 401
    return jsonify(
        {
            "authenticated": True,
            "user": {"id": u.id, "name": u.name, "email": u.email, "role": u.role or "user", "is_active": bool(u.is_active)},
        }
    )


@app.route("/api/admin/users", methods=["GET"])
@admin_api_required
def admin_users():
    rows = User.query.order_by(User.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": (u.role or "user").lower(),
                "is_active": bool(u.is_active),
                "created_at": (u.created_at.isoformat() if u.created_at else None),
            }
            for u in rows
        ]
    )


@app.route("/api/admin/users/<int:uid>/role", methods=["PUT"])
@admin_api_required
def admin_user_role(uid):
    data = payload()
    role = (data.get("role") or "").strip().lower()
    if role not in ("user", "admin"):
        return jsonify({"error": "role must be user or admin"}), 400
    row = User.query.get_or_404(uid)
    fixed_admin_email = app.config["FIXED_ADMIN_EMAIL"]
    if row.email == fixed_admin_email and role != "admin":
        return jsonify({"error": "Fixed admin role cannot be changed"}), 400
    if role == "admin" and row.email != fixed_admin_email:
        return jsonify({"error": "Only fixed admin account can have admin role"}), 400
    row.role = role
    db.session.commit()
    return jsonify({"message": "Role updated"})


@app.route("/api/admin/users/<int:uid>/status", methods=["PUT"])
@admin_api_required
def admin_user_status(uid):
    data = payload()
    if "is_active" not in data:
        return jsonify({"error": "is_active is required"}), 400
    active = bool(data.get("is_active"))
    row = User.query.get_or_404(uid)
    if row.id == session.get("user_id") and not active:
        return jsonify({"error": "You cannot block your own account"}), 400
    row.is_active = active
    db.session.commit()
    return jsonify({"message": "Status updated"})


@app.route("/api/dashboard/summary", methods=["GET"])
def summary():
    sales = db.session.query(func.sum(Invoice.total_amount)).scalar() or 0
    returns = db.session.query(func.sum(CreditNote.total_amount)).scalar() or 0
    purchases = db.session.query(func.sum(Purchase.total_amount)).scalar() or 0
    expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    inc = db.session.query(func.sum(IndirectIncome.amount)).scalar() or 0
    net_sales = sales - returns
    profit = (net_sales + inc) - (purchases + expenses)
    return jsonify(
        {
            "total_sales": sales,
            "total_returns": returns,
            "net_sales": net_sales,
            "total_purchases": purchases,
            "total_expenses": expenses,
            "indirect_income": inc,
            "net_profit": profit,
            "stats": {
                "customers": Customer.query.filter_by(party_type="customer").count(),
                "vendors": Customer.query.filter_by(party_type="vendor").count(),
                "products": Product.query.count(),
            },
        }
    )


@app.route("/api/customers", methods=["GET", "POST"])
def customers():
    if request.method == "GET":
        ptype = request.args.get("type")
        q = Customer.query.filter_by(party_type=ptype) if ptype in ("customer", "vendor") else Customer.query
        return jsonify(
            [
                {
                    "id": c.id,
                    "name": c.name,
                    "phone": c.phone,
                    "email": c.email,
                    "gstin": c.gstin,
                    "company_name": c.company_name,
                    "address": c.address,
                    "party_type": c.party_type,
                }
                for c in q.order_by(Customer.id.desc()).all()
            ]
        )
    data = payload()
    miss = required(data, ["name"])
    if miss:
        return miss
    c = Customer(
        name=data["name"],
        phone=data.get("phone"),
        email=data.get("email"),
        gstin=data.get("gstin"),
        company_name=data.get("company_name"),
        address=data.get("address"),
        party_type=(data.get("party_type") or "customer").lower(),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({"message": "Party added", "id": c.id}), 201


@app.route("/api/customers/<int:cid>", methods=["GET", "PUT", "DELETE"])
def customer_detail(cid):
    c = Customer.query.get_or_404(cid)
    if request.method == "GET":
        return jsonify(
            {
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "email": c.email,
                "gstin": c.gstin,
                "company_name": c.company_name,
                "address": c.address,
                "party_type": c.party_type,
            }
        )
    if request.method == "PUT":
        data = payload()
        for f in ["name", "phone", "email", "gstin", "company_name", "address", "party_type"]:
            if f in data:
                setattr(c, f, data[f])
        db.session.commit()
        return jsonify({"message": "Party updated"})
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Party deleted"})


@app.route("/api/products", methods=["GET", "POST"])
def products():
    if request.method == "GET":
        return jsonify(
            [
                {
                    "id": p.id,
                    "name": p.name,
                    "prod_type": p.prod_type,
                    "price": p.price,
                    "tax_rate": p.tax_rate,
                    "unit": p.unit,
                }
                for p in Product.query.order_by(Product.id.desc()).all()
            ]
        )
    data = payload()
    miss = required(data, ["name"])
    if miss:
        return miss
    p = Product(
        name=data["name"],
        prod_type=data.get("prod_type", "Product"),
        price=float(data.get("price", 0) or 0),
        tax_rate=float(data.get("tax_rate", 0) or 0),
        unit=data.get("unit"),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"message": "Product saved", "id": p.id}), 201


@app.route("/api/products/<int:pid>", methods=["GET", "PUT", "DELETE"])
def product_detail(pid):
    p = Product.query.get_or_404(pid)
    if request.method == "GET":
        return jsonify({"id": p.id, "name": p.name, "prod_type": p.prod_type, "price": p.price, "tax_rate": p.tax_rate, "unit": p.unit})
    if request.method == "PUT":
        data = payload()
        for f in ["name", "prod_type", "unit"]:
            if f in data:
                setattr(p, f, data[f])
        for f in ["price", "tax_rate"]:
            if f in data:
                setattr(p, f, float(data[f] or 0))
        db.session.commit()
        return jsonify({"message": "Product updated"})
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Product deleted"})


@app.route("/api/invoices", methods=["GET", "POST"])
def invoices():
    if request.method == "GET":
        return jsonify([doc_to_dict(i, "invoice_number", "customer_id", "items") for i in Invoice.query.order_by(Invoice.id.desc()).all()])
    data = payload()
    miss = required(data, ["customer_id"])
    if miss:
        return miss
    items = data.get("items", [])
    if not isinstance(items, list):
        return jsonify({"error": "items must be a list"}), 400

    number = data.get("invoice_number") or f"INV-{Invoice.query.count() + 1}"
    inv = Invoice.query.filter_by(invoice_number=number).first()
    created = False
    if not inv:
        inv = Invoice(invoice_number=number)
        db.session.add(inv)
        created = True
    else:
        deny = require_admin_for_bill_mutation()
        if deny:
            return deny

    inv.date = data.get("date")
    inv.due_date = data.get("due_date")
    inv.customer_id = data.get("customer_id")
    inv.total_amount = float(data.get("total_amount", line_total(items)) or 0)

    InvoiceItem.query.filter_by(invoice_id=inv.id).delete() if inv.id else None
    db.session.flush()
    for i in items:
        db.session.add(
            InvoiceItem(
                invoice_id=inv.id,
                product_name=i.get("product_name") or i.get("name"),
                quantity=float(i.get("quantity", 0) or 0),
                unit_price=float(i.get("unit_price", i.get("price", 0)) or 0),
            )
        )

    meta = data.get("meta")
    if isinstance(meta, dict):
        set_invoice_meta(inv.id, meta)

    db.session.commit()
    return jsonify({"id": inv.id, "number": number, "message": "Saved", "created": created}), (201 if created else 200)


@app.route("/api/invoices/<int:rid>", methods=["GET", "DELETE"])
def invoice_detail(rid):
    return doc_detail(Invoice, "invoice_number", "customer_id", "items", rid)


@app.route("/api/invoices/<int:rid>/pdf", methods=["GET"])
def invoice_pdf(rid):
    inv = Invoice.query.get_or_404(rid)
    party = Customer.query.get(inv.customer_id) if inv.customer_id else None
    items = inv.items or []
    meta = get_invoice_meta(inv.id)

    subtotal = round(sum((i.quantity or 0) * (i.unit_price or 0) for i in items), 2)
    total = round(inv.total_amount or subtotal, 2)

    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    render_modern_pdf(
        pdf_canvas=p,
        page_size=A4,
        title="INVOICE",
        number=(inv.invoice_number or f"INV-{inv.id}"),
        date_value=(inv.date or "-"),
        due_value=(inv.due_date or meta.get("due_date") or "-"),
        party=party,
        items=items,
        meta=meta,
        subtotal=subtotal,
        total=total,
        footer_text="Page 1/1 | This is a digitally generated document.",
    )

    p.save()
    buf.seek(0)

    file_name = f"{inv.invoice_number or f'INV-{inv.id}'}.pdf"
    return send_file(buf, as_attachment=True, download_name=file_name, mimetype="application/pdf")


DOC_PREFIX = {
    "invoice": "INV",
    "purchase": "PUR",
    "quotation": "QTN",
    "challan": "CHL",
    "credit_note": "CRN",
    "purchase_order": "PO",
    "proforma": "PFI",
    "expenses": "EXP",
    "indirect_income": "INC",
}

DOC_LABEL = {
    "invoice": "INVOICE",
    "purchase": "PURCHASE",
    "quotation": "QUOTATION",
    "challan": "CHALLAN",
    "credit_note": "CREDIT NOTE",
    "purchase_order": "PURCHASE ORDER",
    "proforma": "PRO FORMA",
    "expenses": "EXPENSES",
    "indirect_income": "INDIRECT INCOME",
}


@app.route("/api/docs/<doc_type>", methods=["GET", "POST"])
def docs_by_type(doc_type):
    if doc_type not in DOC_PREFIX:
        return jsonify({"error": "Invalid doc type"}), 400
    if request.method == "GET":
        rows = DocRecord.query.filter_by(doc_type=doc_type).order_by(DocRecord.id.desc()).all()
        return jsonify([doc_record_to_dict(r) for r in rows])

    data = payload()
    number = data.get("number") or data.get("doc_number")
    if not number:
        number = f"{DOC_PREFIX[doc_type]}-{DocRecord.query.filter_by(doc_type=doc_type).count() + 1}"

    row = DocRecord.query.filter_by(doc_type=doc_type, doc_number=number).first()
    created = False
    if not row:
        row = DocRecord(doc_type=doc_type, doc_number=number)
        db.session.add(row)
        created = True
    else:
        deny = require_admin_for_bill_mutation()
        if deny:
            return deny

    items = data.get("items", [])
    if not isinstance(items, list):
        items = []
    row.date = data.get("date")
    row.due_date = data.get("due_date")
    row.customer_id = data.get("customer_id")
    row.total_amount = float(data.get("total_amount", line_total(items)) or 0)
    row.meta_json = json.dumps(data.get("meta", {}), ensure_ascii=True)

    db.session.flush()
    DocRecordItem.query.filter_by(doc_id=row.id).delete()
    for i in items:
        db.session.add(
            DocRecordItem(
                doc_id=row.id,
                product_name=i.get("product_name") or i.get("name"),
                quantity=float(i.get("quantity", 0) or 0),
                unit_price=float(i.get("unit_price", i.get("price", 0)) or 0),
            )
        )
    db.session.commit()
    return jsonify({"id": row.id, "number": row.doc_number, "message": "Saved", "created": created}), (201 if created else 200)


@app.route("/api/docs/<doc_type>/<int:rid>", methods=["GET", "DELETE"])
def doc_detail_by_type(doc_type, rid):
    row = DocRecord.query.filter_by(doc_type=doc_type, id=rid).first_or_404()
    if request.method == "GET":
        return jsonify(doc_record_to_dict(row))
    deny = require_admin_for_bill_mutation()
    if deny:
        return deny
    db.session.delete(row)
    db.session.commit()
    return jsonify({"message": "Deleted"})


@app.route("/api/docs/<doc_type>/<int:rid>/pdf", methods=["GET"])
def doc_pdf(doc_type, rid):
    row = DocRecord.query.filter_by(doc_type=doc_type, id=rid).first_or_404()
    party = Customer.query.get(row.customer_id) if row.customer_id else None
    items = row.items or []
    meta = parse_json_text(row.meta_json)

    subtotal = round(sum((i.quantity or 0) * (i.unit_price or 0) for i in items), 2)
    total = round(row.total_amount or subtotal, 2)

    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    render_modern_pdf(
        pdf_canvas=p,
        page_size=A4,
        title=DOC_LABEL.get(doc_type, "DOCUMENT"),
        number=(row.doc_number or "-"),
        date_value=(row.date or "-"),
        due_value=(row.due_date or meta.get("due_date") or "-"),
        party=party,
        items=items,
        meta=meta,
        subtotal=subtotal,
        total=total,
        footer_text="Page 1/1 | This is a digitally generated document.",
    )
    p.save()
    buf.seek(0)

    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{row.doc_number}.pdf",
        mimetype="application/pdf",
    )


@app.route("/api/quotations", methods=["GET", "POST"])
def quotations():
    if request.method == "GET":
        return jsonify([doc_to_dict(i, "quotation_number", "customer_id", "items") for i in Quotation.query.order_by(Quotation.id.desc()).all()])
    return create_doc(Quotation, QuotationItem, "quotation_number", "customer_id", "QT")


@app.route("/api/quotations/<int:rid>", methods=["GET", "DELETE"])
def quotation_detail(rid):
    return doc_detail(Quotation, "quotation_number", "customer_id", "items", rid)


@app.route("/api/proforma-invoices", methods=["GET", "POST"])
def proforma():
    if request.method == "GET":
        return jsonify([doc_to_dict(i, "pfi_number", "customer_id", "items") for i in ProFormaInvoice.query.order_by(ProFormaInvoice.id.desc()).all()])
    return create_doc(ProFormaInvoice, ProFormaItem, "pfi_number", "customer_id", "PFI")


@app.route("/api/proforma-invoices/<int:rid>", methods=["GET", "DELETE"])
def proforma_detail(rid):
    return doc_detail(ProFormaInvoice, "pfi_number", "customer_id", "items", rid)


@app.route("/api/challans", methods=["GET", "POST"])
def challans():
    if request.method == "GET":
        return jsonify([doc_to_dict(i, "challan_number", "customer_id", "items") for i in Challan.query.order_by(Challan.id.desc()).all()])
    return create_doc(Challan, ChallanItem, "challan_number", "customer_id", "DC")


@app.route("/api/challans/<int:rid>", methods=["GET", "DELETE"])
def challan_detail(rid):
    return doc_detail(Challan, "challan_number", "customer_id", "items", rid)


@app.route("/api/credit-notes", methods=["GET", "POST"])
def credit_notes():
    if request.method == "GET":
        return jsonify([doc_to_dict(i, "note_number", "customer_id", "items") for i in CreditNote.query.order_by(CreditNote.id.desc()).all()])
    return create_doc(CreditNote, CreditNoteItem, "note_number", "customer_id", "CN")


@app.route("/api/credit-notes/<int:rid>", methods=["GET", "DELETE"])
def credit_note_detail(rid):
    return doc_detail(CreditNote, "note_number", "customer_id", "items", rid)


@app.route("/api/purchases", methods=["GET", "POST"])
def purchases():
    if request.method == "GET":
        return jsonify([doc_to_dict(i, "purchase_number", "vendor_id", "items") for i in Purchase.query.order_by(Purchase.id.desc()).all()])
    return create_doc(Purchase, PurchaseItem, "purchase_number", "vendor_id", "PUR")


@app.route("/api/purchases/<int:rid>", methods=["GET", "DELETE"])
def purchase_detail(rid):
    return doc_detail(Purchase, "purchase_number", "vendor_id", "items", rid)


@app.route("/api/purchase-orders", methods=["GET", "POST"])
def purchase_orders():
    if request.method == "GET":
        return jsonify([doc_to_dict(i, "po_number", "vendor_id", "items") for i in PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).all()])
    return create_doc(PurchaseOrder, POItem, "po_number", "vendor_id", "PO")


@app.route("/api/purchase-orders/<int:rid>", methods=["GET", "DELETE"])
def purchase_order_detail(rid):
    return doc_detail(PurchaseOrder, "po_number", "vendor_id", "items", rid)


@app.route("/api/expenses", methods=["GET", "POST"])
def expenses():
    if request.method == "GET":
        return jsonify(
            [
                {
                    "id": e.id,
                    "amount": e.amount,
                    "expense_date": e.expense_date,
                    "category": e.category,
                    "description": e.description,
                    "is_paid": e.is_paid,
                }
                for e in Expense.query.order_by(Expense.id.desc()).all()
            ]
        )
    data = payload()
    miss = required(data, ["amount", "expense_date", "category"])
    if miss:
        return miss
    e = Expense(
        amount=float(data["amount"]),
        expense_date=data["expense_date"],
        category=data["category"],
        description=data.get("description"),
        is_paid=bool(data.get("is_paid", True)),
    )
    db.session.add(e)
    db.session.commit()
    return jsonify({"message": "Expense saved", "id": e.id}), 201


@app.route("/api/expenses/<int:eid>", methods=["GET", "DELETE"])
def expense_detail(eid):
    e = Expense.query.get_or_404(eid)
    if request.method == "GET":
        return jsonify({"id": e.id, "amount": e.amount, "expense_date": e.expense_date, "category": e.category, "description": e.description, "is_paid": e.is_paid})
    db.session.delete(e)
    db.session.commit()
    return jsonify({"message": "Expense deleted"})


@app.route("/api/indirect-income", methods=["GET", "POST"])
def indirect_income():
    if request.method == "GET":
        return jsonify(
            [
                {
                    "id": i.id,
                    "amount": i.amount,
                    "income_date": i.income_date,
                    "category": i.category,
                    "description": i.description,
                    "is_received": i.is_received,
                }
                for i in IndirectIncome.query.order_by(IndirectIncome.id.desc()).all()
            ]
        )
    data = payload()
    miss = required(data, ["amount", "income_date", "category"])
    if miss:
        return miss
    i = IndirectIncome(
        amount=float(data["amount"]),
        income_date=data["income_date"],
        category=data["category"],
        description=data.get("description"),
        is_received=bool(data.get("is_received", True)),
    )
    db.session.add(i)
    db.session.commit()
    return jsonify({"message": "Income saved", "id": i.id}), 201


@app.route("/api/indirect-income/<int:iid>", methods=["GET", "DELETE"])
def indirect_income_detail(iid):
    i = IndirectIncome.query.get_or_404(iid)
    if request.method == "GET":
        return jsonify({"id": i.id, "amount": i.amount, "income_date": i.income_date, "category": i.category, "description": i.description, "is_received": i.is_received})
    db.session.delete(i)
    db.session.commit()
    return jsonify({"message": "Income deleted"})


@app.errorhandler(404)
def not_found(_):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("auth.html"), 404


with app.app_context():
    db.create_all()
    cols = {row[1] for row in db.session.execute(text("PRAGMA table_info(user)")).fetchall()}
    if "role" not in cols:
        db.session.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
        db.session.commit()
    if "is_active" not in cols:
        db.session.execute(text("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1"))
        db.session.commit()
    fixed_admin_email = app.config["FIXED_ADMIN_EMAIL"]
    fixed_admin_password = app.config["FIXED_ADMIN_PASSWORD"]
    fixed_admin_name = app.config["FIXED_ADMIN_NAME"]
    fixed_admin = User.query.filter_by(email=fixed_admin_email).first()
    if not fixed_admin:
        fixed_admin = User(
            name=fixed_admin_name,
            email=fixed_admin_email,
            password_hash=generate_password_hash(fixed_admin_password),
            role="admin",
            is_active=True,
        )
        db.session.add(fixed_admin)
    else:
        fixed_admin.name = fixed_admin_name
        fixed_admin.password_hash = generate_password_hash(fixed_admin_password)
        fixed_admin.role = "admin"
        fixed_admin.is_active = True
    db.session.commit()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
