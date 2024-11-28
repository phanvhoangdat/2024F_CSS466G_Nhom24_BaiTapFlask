from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import mysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Cấu hình flask-login
login_manager = LoginManager()
login_manager.init_app(app)

# Tải người dùng từ cơ sở dữ liệu
@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user['id'], user['username'], user['email'], user['role'])
    return None

# Lớp User để tương tác với flask-login
class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

# Trang đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        role = 'user'  # Mặc định quyền 'user'

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)', 
                       (username, email, hashed_password, role))
        mysql.connection.commit()
        flash('Đăng ký thành công', 'success')
        return redirect(url_for('login'))

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
            user_obj = User(user['id'], user['username'], user['email'], user['role'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'danger')

    return render_template('login.html')

# Trang chính
@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username, role=current_user.role)

# Trang quản trị
@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Bạn không có quyền truy cập vào trang này', 'danger')
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html')

# Đăng xuất
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
