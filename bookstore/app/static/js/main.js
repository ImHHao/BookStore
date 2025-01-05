function addToCart(id, name, author, category, image, price, is_authenticated) {
    if (is_authenticated === 'True') {
        fetch("/api/carts", {
            method: "POST",
            body: JSON.stringify({
                "id": id,
                "name": name,
                "author": author,
                "category": category,
                "image": image,
                "price": price,
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            if (data.status === "fail") {
                alert(data.message);
                location.reload();
            } else {
                let items = document.getElementsByClassName("cart-counter");
                for (let item of items)
                    item.innerText = data.stats.total_quantity;
            }

        });
    } else {
        const authModal = new bootstrap.Modal(document.getElementById('authModal'));
        authModal.show();
    }
}

function addCartFromOrder() {
    if (cartOrder != []) {
        fetch("/api/cartOrders", {
            method: "POST",
            body: JSON.stringify({
                "cartOrder": cartOrder
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            if (data.status === "fail") {
                alert(data.message);
                window.location.reload();
            } else
                window.location.href = data.url;
        });
    };
}

function removeCartFromOrder() {
    clearOrder()
    fetch("/api/cartOrders", {
        method: "DELETE"
    }).then(res => res.json()).then(data => {
        location.reload();
        console.log(data);
    })
}

function removeFromCart(id) {
    if (confirm("Bạn muốn xóa sản phẩm?") === true) {
        fetch(`/api/carts/${id}`, {
            method: "delete"
        }).then(res => res.json()).then(data => {
            // Ẩn sản phẩm đã bị xóa khỏi giỏ
            document.getElementById(`cart${id}`).style.display = "none";

            // Cập nhật lại số lượng tổng sản phẩm trong giỏ hàng
            let items = document.getElementsByClassName("cart-counter");
            for (let item of items) {
                item.innerText = data.total_quantity;
            }

            // Kiểm tra nếu giỏ hàng trống, ẩn nút thanh toán
            if (data.total_quantity === 0) {
                // Ẩn nút thanh toán nếu không còn sản phẩm trong giỏ
                const checkoutButton = document.querySelector('a[href="/checkout"]');
                if (checkoutButton) {
                    checkoutButton.style.display = 'none';
                }

                // Hoặc nếu bạn sử dụng button thay vì link:
                const payButton = document.querySelector('button.btn-danger');
                if (payButton) {
                    payButton.style.display = 'none';
                }
            }
        });
    }
}


function updateQuantity(id, btn) {
    const quantityInput = document.getElementById(`quantity-input-${id}`);
    let currentQuantity = parseInt(quantityInput.value);

    if (btn === 'giam' && currentQuantity <= 1) {
        if (confirm("Số lượng đã bằng 0. Bạn có muốn xóa sản phẩm khỏi giỏ hàng?")) {
            removeFromCart(id); // Gọi hàm xóa sản phẩm nếu người dùng xác nhận
        }
        return; // Ngăn việc gửi yêu cầu giảm số lượng về server
    }

    fetch(`/api/carts/${id}`, {
        method: "PUT",
        body: JSON.stringify({
            "btn": btn
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        if (data.status === "fail") {
            alert(data.message);
        } else {
            // Cập nhật giao diện số lượng
            quantityInput.value = data.quantity;

            // Cập nhật số lượng tổng trong giỏ hàng
            let items = document.getElementsByClassName("cart-counter");
            for (let item of items) {
                item.innerText = data.stats.total_quantity;
            }
        }
    });
}

function updateQuantityCartOrder(id, obj) {
    fetch(`/api/cartOrders/${id}`, {
        method: "put",
        body: JSON.stringify({
            quantity: obj.value
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        console.log(data);
    })
}

function payOrder(phone) {
    fetch("/api/orders", {
        method: "POST",
        body: JSON.stringify({
            "phone": phone
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        window.location.href = data.url;
    });
}

function payment(amount) {
    if (amount != 0) {
        let paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;

        if (paymentMethod === 'vnpay') {
            fetch('/api/create_payment', {
                method: "POST",
                body: JSON.stringify({
                    'amount': amount
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(res => res.json()).then(data => {
                console.log("Payment Data:", data);
                if (data.payment_url) {
                    window.location.href = data.payment_url;
                } else {
                    alert('Lỗi khi tạo thanh toán VNPay!');
                };
            })
        } else {
            fetch('/api/payment-direct', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(res => res.json()).then(data => {
                window.location.href = "http://127.0.0.1:5000/";
            });
        }
    }
}

function addComment(book_id) {
    fetch(`/api/books/${book_id}/comments`, {
        method: "post",
        body: JSON.stringify({
            'content': document.getElementById("comment").value
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(c => {
        // location.reload();
        let html = `
            <div class="book-detail-review">
                <img src="${c.user.avatar}" alt="User Avatar" class="book-detail-avatar">
                <div class="book-detail-review-content">
                    <p class="book-detail-review-name">${c.user.name}</p>
                    <p>${c.content}</p>
                    <p class="book-detail-review-time">${moment(c.created_date).locale("vi").fromNow()}</p>
                </div>
            </div>
        `;

        let h = document.getElementById("comments");
        h.innerHTML = html + h.innerHTML;
    })
}

function deleteBook(book_id) {
    if (confirm("Bạn muốn xóa sách?") === true) {
        fetch(`/api/books/${book_id}`, {
            method: "delete"
        }).then(res => res.json()).then(data => {
            if (data.status === "success") {
                showToast(data.message, data.status);
                document.getElementById(`book${book_id}`).style.display = "none";
            } else {
                showToast(data.message, data.status);
            }
        });
    }
}

function addBook(name, author, category, price, image, inventoryQuantity) {
    if (name === "" || author === "" || category === "" || price === "" || inventoryQuantity === "") {
        showToast("Vui lòng điền đầy đủ thông tin", "error");
        return;
    }
    const formData = new FormData();
    formData.append("name", name);
    formData.append("author", author);
    formData.append("category", category);
    formData.append("price", price);
    formData.append("inventoryQuantity", inventoryQuantity);
    formData.append("image", image);
    fetch("/api/books", {
        method: "POST",
        body: formData
    }).then(res => res.json()).then(book => {
        if (book.status === "success") {
            const modal = bootstrap.Modal.getInstance(document.getElementById('bookModal'));
            modal.hide();
            window.location.reload();
        } else {
            showToast(book.message, book.status);
        }
    });
}

function updateBook(book_id, inventoryQuantity) {
    if (inventoryQuantity == "" || parseInt(inventoryQuantity) < 0 || book_id == "") {
        showToast("Vui lòng điền đủ thông tin", "error");
        return;
    }
    fetch(`/api/books`, {
        method: "PUT",
        body: JSON.stringify({
            "inventoryQuantity": inventoryQuantity,
            "book_id": book_id
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        if (data.status === "success") {
            location.reload();
        } else {
            showToast(data.message, data.status);
        }
    });
}

function addForm() {
    fetch("/api/forms", {
        method: "POST"
    }).then(res => res.json()).then(data => {
        window.location.href = data.url;
    });
}

function saveChanges() {
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const address = document.getElementById('address').value.trim();

    if (name === '' || email === '' || phone === '' || address === '') {
        alert("Vui lòng điền đầy đủ thông tin!");
        return;
    }

    // Gọi API để lưu thông tin
    fetch('/api/profile', {
        method: 'PUT',
        body: JSON.stringify({
            "name": name,
            "email": email,
            "phone": phone,
            "address": address
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        if (data.status === 'success') {
            // Hiển thị thông báo thành công
            alert("Cập nhật thông tin thành công!");
            window.location.href = data.url;
        } else {
            alert("Cập nhật thông tin thất bại. Vui lòng thử lại!");
        }
    }).catch(error => {
        console.error("Error:", error);
        alert("Đã xảy ra lỗi. Vui lòng thử lại sau!");
    });
}
