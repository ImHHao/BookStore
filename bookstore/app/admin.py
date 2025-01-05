from flask_admin.contrib.sqla import ModelView
from app import db, app, dao
from models import Staff, Book, Category, Author, UserRole, User, Form, ImportRule, Customer, RolePermission
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_login import current_user, logout_user
from flask import redirect, request
from datetime import datetime
from flask_admin.form import rules


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render('admin/index.html', cates=dao.stats_products())


admin = Admin(app=app, name="Bookstore Admin", template_mode='bootstrap4', index_view=MyAdminIndexView())


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class RuleView(AdminView):
    column_list = ['min_quantity', 'max_quantity', 'expire_time']


class UserView(AdminView):
    column_list = ['username', 'user_role']

    # Hàm xử lý trước khi lưu vào database
    def on_model_change(self, form, model, is_created):
        # Debug thông tin
        print(f"is_created: {is_created}, user_role: {model.user_role}, type: {type(model.user_role)}")

        # Nếu mật khẩu được nhập, băm mật khẩu
        if form.password.data:
            model.set_password(form.password.data)

        # Gọi phương thức cha
        super().on_model_change(form, model, is_created)

        # Xử lý khi user_role là STAFF
        if is_created and model.user_role == UserRole.STAFF.name:
            existing_staff = Staff.query.filter_by(id=model.id).first()
            if not existing_staff:
                staff = Staff(
                    id=model.id,
                    phone="0123456789",  # Giá trị mặc định
                    role_permission=RolePermission.SELLER
                )
                db.session.add(staff)
                db.session.commit()


class StaffView(AdminView):
    column_list = ['id', 'username', 'role_permission']
    can_create = False


class LogoutView(MyView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')


class StatsView(MyView):
    @expose('/')
    def index(self):
        # Lấy giá trị tháng và năm từ sự kiện click của button
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)

        # Gọi hàm DAO để lấy dữ liệu thống kê
        month_revenue_stats = dao.month_revenue_stats(month, year)
        book_frequency_stats = dao.book_frequency_stats(month, year)

        total_revenue = sum([s[2] for s in month_revenue_stats])

        # Trả về dữ liệu thống kê
        return self.render('admin/stats.html', month_revenue_stats=month_revenue_stats,
                           book_frequency_stats=book_frequency_stats, total_revenue=total_revenue)


admin.add_view(RuleView(ImportRule, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(StaffView(Staff, db.session))
admin.add_view(StatsView(name='Thống kê - Báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))
