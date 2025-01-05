import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import math
import cloudinary.uploader
from models import User, UserRole, RolePermission, Book, Form, ImportRule
from flask import render_template, redirect, request, session, jsonify, url_for
from flask_login import login_user, logout_user, current_user
from app import login, dao, app, utils, vnpay, VNP_HASH_SECRET, db
import hmac
import hashlib
import cloudinary
import urllib.parse
import uuid
from apscheduler.schedulers.background import BackgroundScheduler


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/api/profile", methods=['put'])
def update_profile():
    name = request.json.get('name')
    email = request.json.get('email')
    address = request.json.get('address')
    phone = request.json.get('phone')

    dao.update_profile(name=name, email=email, address=address, phone=phone)
    return jsonify({"status": "success", "url": "http://" + request.host + "/"})


@app.route("/")
def index():
    kw = request.args.get("kw")
    cate = request.args.get("category")
    page = request.args.get('page', 1)
    total = dao.count_books()
    books = dao.load_books(kw=kw, page=int(page), cate=cate)
    message = session.pop('message', None)  # Lấy và xóa sau khi sử dụng
    order_id = session.pop('order_id', None)
    if message == "success":
        alert = f"Thanh toán thành công! Mã giao dịch: {order_id}"
        alert_type = "success"
    elif message == "failure":
        alert = "Xác thực giao dịch thất bại!"
        alert_type = "danger"
    else:
        alert = None
        alert_type = None
    return render_template("index.html", books=books, alert=alert, alert_type=alert_type,
                           pages=math.ceil(total / app.config["PAGE_SIZE"]))


@app.route("/manage/")
def manage():
    page = request.args.get('page', 1)
    kw = request.args.get('kw')
    books = dao.load_books(page=int(page), kw=kw)
    cates = dao.load_cates()
    total = dao.count_books()
    return render_template("manage.html", books=books, pages=math.ceil(total / app.config["PAGE_SIZE"]), cates=cates)


@app.route("/bill")
def recent_bill():
    phone = request.args.get("phone")
    return render_template("bill.html", phone=phone)


@app.route("/bill/<orderID>")
def bill(orderID):
    bill = dao.load_bill(orderID)
    billInfo = dao.load_bill_info(orderID)
    return render_template("bill.html", bill=bill, billInfo=billInfo)


@app.route("/api/orders", methods=['post'])
def add_order():
    orderID = str(uuid.uuid4())
    phone = request.json.get('phone')
    dao.add_order(orderID=orderID, customerID=None, phone=phone, isPay=True, cart=session.get('cart'))
    dao.update_inventory_quantity(session.get('cart'))
    session['cart'] = {}
    return jsonify({"orderID": orderID, "url": "http://" + request.host + "/bill/" + orderID})


@app.route("/cart")
def cart():
    books = dao.load_books()
    return render_template("cart.html", books=books)


@app.route('/api/carts', methods=['post'])
def add_to_cart():
    id = str(request.json.get('id'))
    name = request.json.get('name')
    author = request.json.get('author')
    category = request.json.get('category')
    image = request.json.get('image')
    price = request.json.get('price')

    if dao.check_inventory_quantity(bookID=id, quantity=1):
        cart = session.get('cart')

        if not cart:
            cart = {}

        dao.buy_book(bookID=id, quantity=1)

        if id in cart:
            cart[id]["quantity"] += 1
        else:
            cart[id] = {
                "id": id,
                "name": name,
                "author": author,
                "category": category,
                "image": image,
                "price": price,
                "quantity": 1
            }

        session['cart'] = cart

        return jsonify({"stats": utils.stats_cart(cart), "status": "success"})
    
    return jsonify({"status": "fail", "message": "Số lượng sách không đủ"})


@app.route("/api/cartOrders", methods=['post'])
def add_cartOrders():
    cartOrder = request.json.get('cartOrder')
    cart = session.get('cart')

    if not cart:
        cart = {}

    if cartOrder:
        for c in cartOrder:
            if dao.check_inventory_quantity(bookID=c['id'], quantity=c['quantity']):
                cart[c['id']] = c
                cart[c['id']]['total_price'] = int(c['price']) * int(c['quantity'])
            else:
                return jsonify({"status": "fail", "message": "Số lượng sách không đủ"})
    session['cart'] = cart

    return jsonify({"url": "http://" + request.host + "/cart"})


@app.route('/api/cartOrders', methods=['delete'])
def remove_cart():
    session['cart'] = {}
    return jsonify({"cart": session.get('cart')})


@app.route('/api/cartOrders/<book_id>', methods=['put'])
def update_quantity_cartOrders(book_id):
    cart = session.get('cart')

    if cart and book_id in cart:
        quantity = int(request.json.get('quantity', 0))
        cart[book_id]['quantity'] = quantity

    session['cart'] = cart

    return jsonify(utils.stats_cart(cart))


@app.route('/api/carts/<book_id>', methods=['delete'])
def remove_from_cartID(book_id):
    cart = session.get('cart')

    if cart and book_id in cart:
        dao.refund_book(bookID=book_id, quantity=cart[book_id]['quantity'])
        del cart[book_id]

    session['cart'] = cart

    return jsonify(utils.stats_cart(cart))


@app.route('/api/carts/<book_id>', methods=['PUT'])
def update_quantity(book_id):
    cart = session.get('cart')
    current_quantity = cart[book_id]['quantity']

    btn = request.json.get('btn')

    if btn == "tang":
        # Chỉ kiểm tra thêm 1 cuốn so với hiện tại
        if dao.check_inventory_quantity(bookID=book_id, quantity=1):
            dao.buy_book(bookID=book_id, quantity=1)
            cart[book_id]['quantity'] = current_quantity + 1
        else:
            return jsonify({"status": "fail", "message": "Số lượng sách không đủ"})
    else:
        dao.refund_book(bookID=book_id, quantity=1)
        cart[book_id]['quantity'] = current_quantity - 1

    session['cart'] = cart
    stats = utils.stats_cart(cart)

    return jsonify({
        "stats": stats,
        'quantity': cart[book_id]['quantity'],
        'id': cart[book_id]['id']
    })


@app.route('/api/books/<book_id>', methods=['delete'])
def delete_book(book_id):
    result = dao.delete_book(book_id)

    if result == 0:
        return jsonify({"message": f"Sách với mã {book_id} không tìm thấy", "status": "fail"})
    
    return jsonify({"message": f"Sách với mã {book_id} đã được xóa", "status": "success"})


@app.route('/api/books', methods=['put'])
def update_book():
    form = session.get('form')

    if not form:
        form = {}

    inventoryQuantity = int(request.json.get('inventoryQuantity'))
    book_id = request.json.get('book_id')
    result = dao.update_book(bookID=book_id, inventoryQuantity=inventoryQuantity)

    book = Book.query.get(book_id)

    if book_id in form:
        form[book_id]["inventoryQuantity"] = int(form[book_id]["inventoryQuantity"]) + inventoryQuantity
    else:
        form[book_id] = {
            "bookID": book_id,
            "inventoryQuantity": int(inventoryQuantity),
            "name": book.name,
            "author": book.author.name,
            "category": book.category.name,
        }

    session['form'] = form

    return jsonify(result)


@app.route('/api/books', methods=['post'])
def add_book():
    form = session.get('form')

    if not form:
        form = {}

    name = request.form.get('name')
    author = request.form.get('author')
    price = request.form.get('price')
    category = request.form.get('category')
    image = request.files.get('image')
    inventoryQuantity = int(request.form.get('inventoryQuantity'))

    if image:
        res = cloudinary.uploader.upload(image)
        image = res["secure_url"]
    else:
        image = "https://cdn-icons-png.flaticon.com/512/2716/2716054.png"

    r = ImportRule.query.first()

    if inventoryQuantity >= r.min_quantity:
        book = dao.add_book(name=name, author=author, price=price, inventoryQuantity=inventoryQuantity, category=category, image=image)
        form[str(book.id)] = {
            "bookID": book.id,
            "inventoryQuantity": book.inventoryQuantity,
            "name": book.name,
            "author": book.author.name,
            "category": book.category.name
        }
        session['form'] = form
        return jsonify({"status": "success", "id": book.id, "name": book.name, "author": book.author.name, "price": book.price, "category_id": book.category_id, "image": book.image, "inventoryQuantity": book.inventoryQuantity})
    else:
        return jsonify({"status": "fail", "message": f"Số lượng sách phải tối thiểu {r.min_quantity}"})


@app.route("/api/forms", methods=['post'])
def add_form():
    f = session.get("form")
    formID = dao.add_form(form=f)
    session["formID"] = formID
    return jsonify({"url": "http://" + request.host + "/bookEntrys"})


@app.route("/list-order")
def orderOnline():
    kw = request.args.get("kw")
    orders = dao.load_orders(kw=kw)
    books = dao.load_books()
    return render_template("list_order.html", books=books, orders=orders)


@app.route("/list-order/<int:cusID>")
def cus_detail_order(cusID):
    orders = dao.load_orders(cusID=cusID)
    return render_template("list_order.html", orders=orders)


@app.route("/books/<int:bookID>")
def book_detail(bookID):
    book = dao.load_book_by_id(bookID=bookID)
    return render_template("book-detail.html", book=book)


@app.route("/list-order/<string:orderID>")
def detail_order(orderID):
    # Lấy thông tin đơn hàng (bao gồm trạng thái isCancel)
    orders = dao.load_orders(kw=orderID)
    if orders:
        order = orders[0]  # Lấy order đầu tiên từ kết quả

    # Lấy chi tiết các items trong đơn hàng
    detailOrder = dao.load_detail_order(orderID=orderID)
    total = utils.total_price(detailOrder=detailOrder)

    return render_template("detail-order.html",
                           order=order,  # order chứa trạng thái isCancel
                           detailOrder=detailOrder,
                           total=total,
                           orderID=orderID)


@app.route("/order/")
def unplacedOrder():
    kw = request.args.get('kw')
    page = request.args.get('page', 1)
    total = dao.count_books()
    books = dao.load_books(kw=kw, page=int(page))
    return render_template("unplaced_order.html", books=books, pages=math.ceil(total / app.config["PAGE_SIZE"]))


@app.route('/cancel-order/<string:order_id>', methods=['POST'])
def cancel_order(order_id):
    success = dao.cancel_order(order_id=order_id)
    if success:
        return redirect(url_for('cus_detail_order', cusID=current_user.id))


@app.route('/api/books/<book_id>/comments', methods=['post'])
def add_comment(book_id):
    c = dao.add_comment(content=request.json.get('content'), book_id=book_id)
    return {
        'content': c.content,
        'created_date': c.createdDate.isoformat(),
        'user': {
            'avatar': c.customer.user.avatar,
            'name': c.customer.user.name
        }
    }


@app.route('/login', methods=['GET', 'POST'])
def login_process():
    err_msg = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = dao.auth_user(username=username, password=password)

        if user:
            login_user(user)
            if user.user_role == UserRole.CUSTOMER:
                next = request.args.get('next')
                return redirect(next if next else '/')
            elif user.user_role == UserRole.ADMIN:
                return redirect('/admin')
            else:
                return redirect('/order')
        else:
            err_msg = "Invalid username or password"
    return render_template("login.html", err_msg=err_msg)


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    u = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
    if u:
        login_user(u)

    return redirect('/admin')


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register_process():
    err_msg = ""
    if request.method == "POST":
        phone = request.form.get("phone")
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = request.form.get("email")
        address = request.form.get("address")
        if not User.query.filter(User.username.__eq__(username)).first():
            if password.strip() != confirm.strip():
                err_msg = "Mật khẩu không trùng khớp"
            else:
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar = res["secure_url"]
                if dao.add_user(phone=phone, name=name, username=username, password=password, email=email,
                                address=address, avatar=avatar):
                    return redirect('/login')
                else:
                    err_msg = "Có lỗi xảy ra !!!"
        else:
            err_msg = "Tên người dùng đã tồn tại"
    return render_template('register.html', err_msg=err_msg)


@app.route('/api/payment-direct', methods=['POST'])
def payment_direct():
    orderID = str(uuid.uuid4())
    session['message'] = 'success'
    session['order_id'] = orderID
    dao.add_order(orderID, current_user.customer.id, current_user.customer.phone, False, session.get('cart'))
    dao.send_email(orderID, current_user.name, current_user.customer.address, current_user.email)
    session['cart'] = {}
    return jsonify({})


@app.route('/api/create_payment', methods=['POST'])
def create_payment():
    """Tạo URL thanh toán."""
    orderID = str(uuid.uuid4())
    amount = int(request.json.get('amount'))
    ip_address = request.remote_addr

    payment_url = vnpay.create_payment_url(orderID, amount, "http://" + request.host + "/payment_success", ip_address)
    return jsonify({"payment_url": payment_url})


@app.route('/payment_success', methods=['GET'])
def payment_success():
    """Xử lý sau khi thanh toán."""
    vnp_params = request.args.to_dict()
    vnp_secure_hash = vnp_params.pop("vnp_SecureHash", None)

    transaction_status = vnp_params.get('vnp_TransactionStatus')  # Lấy trạng thái giao dịch

    if transaction_status != '00':  # '00' là mã trạng thái giao dịch thành công
        session['message'] = 'failure'
        return redirect(url_for('index'))  # Giao dịch không thành công, trả về trang chính

    # Sắp xếp tham số
    sorted_params = sorted(vnp_params.items())
    query_string = "&".join(f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in sorted_params)

    # Tạo hash
    generated_hash = hmac.new(
        VNP_HASH_SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha512
    ).hexdigest()

    if generated_hash.upper() == vnp_secure_hash.upper():  # So sánh không phân biệt hoa thường
        session['message'] = 'success'
        session['order_id'] = vnp_params.get('vnp_TxnRef')
        dao.add_order(vnp_params.get('vnp_TxnRef'), current_user.customer.id, current_user.customer.phone, True, session.get('cart'))
        dao.send_email(vnp_params.get('vnp_TxnRef'), current_user.name, current_user.customer.address, current_user.email)
        session['cart'] = {}
        return redirect(url_for('index'))
    else:
        session['message'] = 'failure'
        return redirect(url_for('index'))
    

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")


@app.route("/bookEntrys")
def book_entry_form():
    fo = session.pop('form', None)
    formID = session.pop('formID', None)
    f = Form.query.get(formID)
    return render_template("book-entry-form.html", fo=fo, createdDate=f.createdDate)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.context_processor
def common_response():
    return {
        "cates" : dao.load_cates(),
        'cart_stats': utils.stats_cart(session.get('cart')),
        "cart": session.get('cart'),
        "form": session.get('form'),
        "UserRole": UserRole,
        "RolePer": RolePermission
    }


@app.template_filter('currency')
def currency_filter(value):
    return f"{value:,.0f} VND"


if __name__ == "__main__":
    with app.app_context():
        time = ImportRule.query.first().expire_time
    from app import admin
    scheduler = BackgroundScheduler()
    scheduler.add_job(dao.cancel_expired_orders, 'interval', minutes=time)
    scheduler.start()
    app.run(debug=True)
