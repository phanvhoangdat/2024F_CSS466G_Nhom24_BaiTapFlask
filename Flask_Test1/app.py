from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL  # Đảm bảo đã import đúng MySQL
import pymysql
pymysql.install_as_MySQLdb()


from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import mysql

# Khởi tạo Flask và cấu hình ứng dụng
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Thay đổi key cho bảo mật

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'  # Đảm bảo người dùng chưa đăng nhập sẽ được chuyển đến trang đăng nhập
login_manager.init_app(app)

# Lớp User để tương tác với Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

# Hàm tải người dùng từ cơ sở dữ liệu
@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user['id'], user['username'], user['email'], user['role'])
    return None

# Trang đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Băm mật khẩu để bảo mật
        hashed_password = generate_password_hash(password, method='sha256')
        role = 'user'  # Mặc định quyền 'user'

        # Thực hiện lưu thông tin người dùng vào cơ sở dữ liệu
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)', 
                       (username, email, hashed_password, role))
        mysql.connection.commit()

        flash('Đăng ký thành công', 'success')
        return redirect(url_for('login'))  # Chuyển hướng đến trang đăng nhập sau khi đăng ký

    return render_template('register.html')

# Trang đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            # Tạo đối tượng User cho Flask-Login
            user_obj = User(user['id'], user['username'], user['email'], user['role'])
            login_user(user_obj)
            flash('Đăng nhập thành công', 'success')
            return redirect(url_for('index'))  # Chuyển hướng về trang chính

        flash('Tên đăng nhập hoặc mật khẩu không đúng', 'danger')

    return render_template('login.html')

# Trang chính
@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username, role=current_user.role)

# Trang quản trị (dành cho admin)
@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Bạn không có quyền truy cập vào trang này', 'danger')
        return redirect(url_for('index'))  # Nếu không phải admin, chuyển về trang chính
    return render_template('admin_dashboard.html')

# Trang chỉnh sửa thông tin người dùng
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Nếu người dùng gửi thông tin qua form
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256') if password else None

        cursor = mysql.connection.cursor()

        # Cập nhật thông tin người dùng
        if hashed_password:
            cursor.execute('UPDATE users SET username = %s, email = %s, password = %s WHERE id = %s', 
                           (username, email, hashed_password, current_user.id))
        else:
            cursor.execute('UPDATE users SET username = %s, email = %s WHERE id = %s', 
                           (username, email, current_user.id))

        mysql.connection.commit()
        flash('Thông tin đã được cập nhật!', 'success')
        return redirect(url_for('index'))

    # Nếu là phương thức GET, tải thông tin người dùng
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (current_user.id,))
    user = cursor.fetchone()

    return render_template('edit_profile.html', user=user)

# Trang đăng xuất
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đăng xuất thành công', 'success')
    return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập

# Cấu hình MySQL
app.config['MYSQL_HOST'] = 'localhost'  # Địa chỉ máy chủ MySQL (localhost hoặc địa chỉ IP)
app.config['MYSQL_USER'] = 'root'  # Tên người dùng MySQL, thường là 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'  # Mật khẩu người dùng MySQL
app.config['MYSQL_DB'] = 'your_database'  # Tên cơ sở dữ liệu mà bạn muốn kết nối

# Khởi tạo MySQL
mysql = MySQL(app)

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'  # Đảm bảo người dùng chưa đăng nhập sẽ được chuyển đến trang đăng nhập
login_manager.init_app(app)

# Lớp User để tương tác với Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

# Hàm tải người dùng từ cơ sở dữ liệu
@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user['id'], user['username'], user['email'], user['role'])
    return None

if __name__ == '__main__':
    app.run(debug=True)
