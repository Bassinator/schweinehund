from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
from importlib import resources
import calendar
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os
from pathlib import Path

# Dynamically find the absolute path of this file's directory
BASE_DIR = Path(str(resources.files("schweinehund")))
APPLICATION_SUBPATH = os.getenv("APPLICATION_SUBPATH", "")

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
    static_url_path=f"{APPLICATION_SUBPATH}/static" if APPLICATION_SUBPATH else "/static"
)

# Initialize Blueprint dynamically based on execution environment
bp = Blueprint('schweinehund', __name__, url_prefix=APPLICATION_SUBPATH if APPLICATION_SUBPATH else None)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ein-sehr-geheimes-passwort-hier-einsetzen'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
# Redirect unauthenticated users to the namespaced login screen
login_manager.login_view = 'schweinehund.login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade="all, delete-orphan")
    logs = db.relationship('DailyLog', backref='user', lazy=True, cascade="all, delete-orphan")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    stage1_text = db.Column(db.String(100), nullable=False)
    stage1_points = db.Column(db.Integer, nullable=False)
    stage2_text = db.Column(db.String(100), nullable=False)
    stage2_points = db.Column(db.Integer, nullable=False)
    logs = db.relationship('DailyLog', backref='task', lazy=True, cascade="all, delete-orphan")

class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    completed_stage1 = db.Column(db.Boolean, default=False)
    completed_stage2 = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_xp_for_date(target_date):
    logs = DailyLog.query.filter_by(date=target_date, user_id=current_user.id).all()
    points = 0
    for log in logs:
        if log.completed_stage1: points += log.task.stage1_points
        if log.completed_stage2: points += log.task.stage2_points
    return points

def build_graph(x_data, y_data, title, xlabel):
    plt.clf()
    plt.figure(figsize=(7, 3.5))
    
    x_list = list(x_data) if x_data else []
    y_list = list(y_data) if y_data else []
    
    # FIX: If we only have 1 data period (e.g., 1 month or 1 year), 
    # a line plot is invisible. We force a bar chart instead.
    if len(x_list) <= 1:
        plt.bar(x_list if x_list else ["No Data"], y_list if y_list else [0], color='#2196F3', width=0.4)
    else:
        # If the X-axis contains text/strings, map them to numeric positions
        if x_list and isinstance(x_list[0], str):
            x_indices = range(len(x_list))
            plt.plot(x_indices, y_list, marker='o', color='#2196F3', linewidth=2)
            plt.xticks(x_indices, x_list, rotation=30 if len(x_list) > 6 else 0)
        else:
            plt.plot(x_list, y_list, marker='o', color='#2196F3', linewidth=2)
            
    plt.title(title, fontsize=12, fontweight='bold')
    plt.xlabel(xlabel)
    plt.ylabel('XP')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

# --- ROUTEN (Attached to bp instead of app) ---

@bp.route('/')
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for('schweinehund.dashboard'))
    return render_template('promo.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        action = request.form.get('action')
        
        if action == 'register':
            from sqlalchemy import func
            existing_user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
            if existing_user:
                flash('Dieser Benutzername ist bereits vergeben!')
                return redirect(url_for('schweinehund.login'))
            new_user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('schweinehund.dashboard'))
            
        elif action == 'login':
            user = User.query.filter_by(username=username).first()
            if user and user.username == username and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('schweinehund.dashboard'))
            flash('Ungültiger Benutzername oder Passwort!')
            
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('schweinehund.welcome'))

@bp.route('/dashboard')
@login_required
def dashboard():
    date_str = request.args.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        selected_date = date.today()

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    today_logs = DailyLog.query.filter_by(date=selected_date, user_id=current_user.id).all()
    total_points = get_xp_for_date(selected_date)
    
    status_map = {}
    for log in today_logs:
        status_map[log.task_id] = {'s1': log.completed_stage1, 's2': log.completed_stage2}

    year, month = selected_date.year, selected_date.month
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    
    calendar_weeks = []
    for week in month_days:
        week_days = []
        for day in week:
            if day == 0:
                week_days.append(None)
            else:
                d = date(year, month, day)
                week_days.append({'day': day, 'date_str': d.strftime('%Y-%m-%d'), 'xp': get_xp_for_date(d)})
        calendar_weeks.append(week_days)

    month_name = calendar.month_name[month]
    prev_month_date = (selected_date.replace(day=1) - timedelta(days=1))
    next_month_date = (selected_date.replace(day=28) + timedelta(days=5)).replace(day=1)

    return render_template('index.html', tasks=tasks, status_map=status_map, 
                           total_points=total_points, selected_date=selected_date, today=date.today(),
                           calendar_weeks=calendar_weeks, month_name=month_name, year=year,
                           prev_month=prev_month_date.strftime('%Y-%m-%d'), next_month=next_month_date.strftime('%Y-%m-%d'))

@bp.route('/check/<int:task_id>/<int:stage_num>', methods=['POST'])
@login_required
def check_box(task_id, stage_num):
    date_str = request.form.get('date')
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    log = DailyLog.query.filter_by(task_id=task.id, date=selected_date, user_id=current_user.id).first()
    if not log:
        log = DailyLog(task_id=task.id, date=selected_date, user_id=current_user.id)
        db.session.add(log)
    
    if stage_num == 1:
        log.completed_stage1 = not log.completed_stage1
        if log.completed_stage1: log.completed_stage2 = False
    elif stage_num == 2:
        log.completed_stage2 = not log.completed_stage2
        if log.completed_stage2: log.completed_stage1 = False
            
    db.session.commit()
    return redirect(url_for('schweinehund.dashboard', date=date_str))

@bp.route('/stats')
@login_required
def stats():
    today = date.today()
    
    week_dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    week_x = [d.strftime('%a') for d in week_dates]
    week_y = [get_xp_for_date(d) for d in week_dates]
    week_graph = build_graph(week_x, week_y, 'XP-Verlauf (Letzte 7 Tage)', 'Wochentag')
    
    # Complete the truncated route response cleanly
    return render_template('stats.html', week_graph=week_graph)

@app.route('/stats')
@login_required
def stats():
    today = date.today()
    
    week_dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    week_x = [d.strftime('%a') for d in week_dates]
    week_y = [get_xp_for_date(d) for d in week_dates]
    week_graph = build_graph(week_x, week_y, 'XP-Verlauf (Letzte 7 Tage)', 'Wochentag')

    month_dates = [today - timedelta(days=i) for i in range(29, -1, -1)]
    month_x = [d.strftime('%d.%m') for d in month_dates]
    month_y = [get_xp_for_date(d) for d in month_dates]
    month_graph = build_graph(month_x, month_y, 'XP-Verlauf (Letzte 30 Tage)', 'Datum')

    year_y = []
    year_x = []
    current_first_of_month = today.replace(day=1)
    for i in range(11, -1, -1):
        m_date = current_first_of_month - timedelta(days=i*30)
        m_date = m_date.replace(day=1)
        _, num_days = calendar.monthrange(m_date.year, m_date.month)
        mon_xp = 0
        for day in range(1, num_days + 1):
            mon_xp += get_xp_for_date(date(m_date.year, m_date.month, day))
        year_x.append(m_date.strftime('%b %y'))
        year_y.append(mon_xp)
    year_graph = build_graph(year_x, year_y, 'XP-Verlauf (Letzte 12 Monate)', 'Monat')

    return render_template('stats.html', week_graph=week_graph, month_graph=month_graph, year_graph=year_graph)

@bp.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    if request.method == 'POST':
        new_task = Task(
            user_id=current_user.id,
            title=request.form['title'],
            stage1_text=request.form['stage1_text'],
            stage1_points=int(request.form['stage1_points']),
            stage2_text=request.form['stage2_text'],
            stage2_points=int(request.form['stage2_points'])
        )
        db.session.add(new_task)
        db.session.commit()
        # FIX: Point redirect to the namespaced blueprint endpoint
        return redirect(url_for('schweinehund.manage'))
        
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('manage.html', tasks=tasks)

@bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    # FIX: Point redirect to the namespaced blueprint endpoint
    return redirect(url_for('schweinehund.manage'))


# Register the blueprint with the application instance
app.register_blueprint(bp)

def start_dev_server():
    """ Runs exclusive local development servers with automatic hot reloading """
    print("Starting local Schweinehund development server with hot-reload...")
    app.run(host="127.0.0.1", port=5000, debug=True)

if __name__ == "__main__":
    start_dev_server()

