from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
from vnpay import VNPay
from flask_mail import Mail
from urllib.parse import quote


app = Flask(__name__)
app.secret_key = 'HGHJAHA^&^&*AJAVAHJ*^&^&*%&*^GAFGFAG'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/saledb?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8
app.config["PAGE_MANAGE"] = 4
# Cấu hình email server
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'testapp2712@gmail.com'
app.config['MAIL_PASSWORD'] = 'lhfx smef jmsz ffui'
app.config['MAIL_DEFAULT_SENDER'] = 'testapp2712@gmail.com'



db = SQLAlchemy(app)
login = LoginManager(app=app)
mail = Mail(app)

cloudinary.config(
    cloud_name='dmtquupzx',
    api_key='832127566516445',
    api_secret='OVydA9RDWGDNkD-TtK8qcP7n_FM')

cloudinary.config(
    cloud_name="dgoxhps7w",
    api_key="621492548287866",
    api_secret="XpjoXDFFUIOiCiKU-RiyLfpgG8k",  # Click 'View API Keys' above to copy your API secret
    secure=True
)


VNP_TMN_CODE = "2GQGSK2S"
VNP_HASH_SECRET = "DZKBJI506YCYWDVRBLSS5QQ3TL7COWSF"
VNP_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"

vnpay = VNPay(VNP_TMN_CODE, VNP_HASH_SECRET, VNP_URL)
