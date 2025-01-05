function displayPassword() {
    var password = document.getElementById("password");
    var displayPass = document.getElementById("display-pass");
    var hidenPass = document.getElementById("hiden-pass");

    if (password.type === "password") {
        password.type = "text";
        displayPass.style.display = "block";
        hidenPass.style.display = "none";
    } else {
        password.type = "password";
        displayPass.style.display = "none";
        hidenPass.style.display = "block";
    }
}

function displayPasswordConfirm() {
    var passConfirm = document.getElementById("confirm");
    var displayPassConfirm = document.getElementById("display-confirm");
    var hidenPassConfirm = document.getElementById("hiden-confirm");

    if (passConfirm.type === "password") {
        console.log("click if");
        passConfirm.type = "text";
        displayPassConfirm.style.display = "block";
        hidenPassConfirm.style.display = "none";
    } else {
        console.log("click else");
        passConfirm.type = "password";
        displayPassConfirm.style.display = "none";
        hidenPassConfirm.style.display = "block";
    }
}

var cartOrder = [];

// Hàm thêm sản phẩm vào giỏ hàng
function addToOrder(productID, productName, productAuthor, productCate, productImage, productPrice, cart) {
    if (cartOrder.length === 0) {
        if (Object.keys(cart).length > 0) {
            for (var c in cart) {
                cartOrder.push({ id: cart[c]["id"], name: cart[c]["name"], author: cart[c]["author"], category: cart[c]["category"], price: cart[c]["price"], image: cart[c]["image"], quantity: cart[c]["quantity"] });
            }
        }
    }
    // Kiểm tra nếu sản phẩm đã có trong giỏ hàng bằng cách so sánh tên sản phẩm và hình ảnh
    const existingProduct = cartOrder.find(item => item.name === productName && item.image === productImage);
    if (existingProduct) {
        // Nếu sản phẩm đã có, tăng số lượng lên 1
        existingProduct.quantity++;
    } else {
        // Nếu sản phẩm chưa có, thêm mới vào giỏ hàng
        cartOrder.push({
            id: productID, name: productName,
            author: productAuthor, category: productCate, price: productPrice, image: productImage, quantity: 1
        });
    }
    // Cập nhật lại giao diện giỏ hàng
    updateOrderDisplay();
}
// Hàm rút gọn tên sách nếu dài hơn 16 ký tự
function truncateName(name) {
    if (name.length > 16) {
        return name.slice(0, 16) + '...';
    }
    return name;
}
// Hàm cập nhật giỏ hàng
function updateOrderDisplay() {
    const cartItemsContainer = document.getElementById('cartItems');
    const emptyCartMessage = document.getElementById('emptyCartMessage');
    const cartItemsContainerWrapper = document.getElementById('cartItemsContainer');
    // Xóa hết sản phẩm cũ trong giỏ hàng
    cartItemsContainer.innerHTML = "";
    if (cartOrder.length === 0) {
        // Nếu giỏ hàng trống, hiển thị thông báo
        emptyCartMessage.classList.remove('d-none');
        cartItemsContainerWrapper.classList.add('d-none');
    } else {
        // Nếu giỏ hàng có sản phẩm, ẩn thông báo và hiển thị các sản phẩm trong giỏ hàng
        emptyCartMessage.classList.add('d-none');
        cartItemsContainerWrapper.classList.remove('d-none');
        // Lặp qua từng sản phẩm trong giỏ hàng
        cartOrder.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                        <td class="product-name">${truncateName(item.name)}</td>
                        <td>
                            <input type="number" class="form-control quantity-input" value="${item.quantity}" min="1" onchange="updateQuantityOrder('${item.name}', '${item.image}', this)">
                        </td>
                    `;
            cartItemsContainer.appendChild(row);
            // Tính tổng số tiền
        });
    }
}
// Cập nhật số lượng sản phẩm trong giỏ hàng
function updateQuantityOrder(productName, productImage, obj, cart) {
    console.log(cartOrder);
    if (cartOrder.length === 0) {
        if (Object.keys(cart).length > 0) {
            for (var c in cart) {
                cartOrder.push({ id: cart[c]["id"], name: cart[c]["name"], author: cart[c]["author"], category: cart[c]["category"], price: cart[c]["price"], image: cart[c]["image"], quantity: cart[c]["quantity"] });
            }
        }
    }
    const product = cartOrder.find(item => item.name === productName && item.image === productImage);
    if (product) {
        product.quantity = parseInt(obj.value, 10);
        updateOrderDisplay();
    }
}

// Hàm thanh toán
function proceedToPayment() {
    alert("Proceeding to payment...");
}
// Hàm xóa giỏ hàng
function clearOrder() {
    cartOrder = [];
    updateOrderDisplay();
}



// Mảng để lưu trữ dữ liệu sách
let books = [];
function showDialog(action, bookIndex = null) {
    const modalTitle = document.getElementById('modalTitle');
    const bookForm = document.getElementById('bookForm');
    if (action === 'add') {
        modalTitle.textContent = 'Thêm sách mới';
        bookForm.reset(); // Đặt lại các trường trong biểu mẫu
        bookForm.dataset.index = ""; // Xóa chỉ số
    } else if (action === 'edit') {
        modalTitle.textContent = 'Chỉnh sửa sách';
        const book = books[bookIndex];
        bookForm.dataset.index = bookIndex; // Lưu chỉ số để chỉnh sửa
        // Điền thông tin hiện tại vào các trường biểu mẫu
        document.getElementById('bookName').value = book.name;
        document.getElementById('bookPrice').value = book.price;
        document.getElementById('bookAuthor').value = book.author;
        document.getElementById('bookStock').value = book.stock;
        document.getElementById('bookDate').value = book.date;
        document.getElementById('bookCategory').value = book.category;
    }
    const modal = new bootstrap.Modal(document.getElementById('bookModal'));
    modal.show();
}

function saveBook() {
    const bookName = document.getElementById('bookName').value;
    const bookPrice = document.getElementById('bookPrice').value;
    const bookAuthor = document.getElementById('bookAuthor').value;
    const bookStock = document.getElementById('bookStock').value;
    const bookDate = document.getElementById('bookDate').value;
    const bookImage = document.getElementById('bookImage').files[0];
    const bookCategory = document.getElementById('bookCategory').value;
    if (!bookName || !bookPrice || !bookAuthor || !bookCategory) {
        alert('Vui lòng điền đầy đủ các trường bắt buộc.');
        return;
    }
    // Chuẩn bị dữ liệu sách
    const bookData = {
        name: bookName,
        price: bookPrice,
        author: bookAuthor,
        stock: bookStock,
        date: bookDate,
        category: bookCategory,
        image: bookImage ? bookImage.name : "Không có hình ảnh",
    };
    // Kiểm tra đang chỉnh sửa hay thêm mới
    const bookForm = document.getElementById('bookForm');
    const bookIndex = bookForm.dataset.index;
    if (bookIndex === "") {
        // Thêm sách mới
        books.push(bookData);
    } else {
        // Chỉnh sửa sách hiện tại
        books[bookIndex] = bookData;
    }
    updateBookTable();
    alert('Lưu sách thành công!');
    const modal = bootstrap.Modal.getInstance(document.getElementById('bookModal'));
    modal.hide();
}

function updateBookTable() {
    const tableBody = document.getElementById('bookTableBody');
    tableBody.innerHTML = ""; // Xóa các dòng hiện tại
    books.forEach((book, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${book.name}</td>
            <td><img src="${book.image}" alt="Hình ảnh sách" width="50"></td>
            <td>${book.category}</td>
            <td>$${book.price}</td>
            <td>${book.author}</td>
            <td>${book.stock}</td>
            <td>${book.date}</td>
            <td>
                <button class="btn-icon edit" onclick="showDialog('edit', ${index})" title="Chỉnh sửa">
                    <i class="fas fa-pencil-alt"></i>
                </button>
                <button class="btn-icon delete" onclick="deleteBook(${index})" title="Xóa">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function deleteBook(index) {
    if (confirm("Bạn có chắc chắn muốn xóa sách này?")) {
        books.splice(index, 1);
        updateBookTable();
    }
}

document.getElementById('cancelOrderBtn').addEventListener('click', function(event) {
        let confirmCancel = confirm("Bạn chắc chắn muốn hủy đơn hàng?");

        if (confirmCancel) {
            document.getElementById('cancelOrderForm').submit();
        }
    });

document.addEventListener('DOMContentLoaded', function () {
    const paymentMethodRadios = document.querySelectorAll('input[name="paymentMethod"]');
    const addressInput = document.getElementById('address');
    const addressLabel = document.querySelector('label[for="address"]');
    const checkoutButton = document.querySelector('.payment-checkout-radio-btn button');
    // Hiện hoặc ẩn ô địa chỉ và label khi thay đổi phương thức thanh toán
    paymentMethodRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (radio.value === 'vnpay') {
                addressInput.style.display = 'block';
                addressLabel.style.display = 'block';
            } else {
                addressInput.style.display = 'none';
                addressLabel.style.display = 'none';
            }
        });
    });
    // Đặt mặc định ẩn ô địa chỉ và label nếu chọn VNPAY
    if (document.getElementById('debit').checked) {
        addressInput.style.display = 'none';
        addressLabel.style.display = 'none';
    }
});

// Hàm hiển thị toast
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');

    // Tạo HTML cho toast
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    // Nội dung của toast
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    // Thêm toast vào container
    toastContainer.appendChild(toast);

    // Kích hoạt bootstrap toast
    const bootstrapToast = new bootstrap.Toast(toast);
    bootstrapToast.show();

    // Xóa khỏi DOM sau khi ẩn
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

