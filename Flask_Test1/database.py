from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# Cấu hình kết nối cơ sở dữ liệu
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Thay đổi thành user của bạn
app.config['MYSQL_PASSWORD'] = 'your_password'  # Thay đổi mật khẩu MySQL của bạn
app.config['MYSQL_DB'] = 'user_management'

mysql = MySQL(app)
