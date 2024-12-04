from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Настройки для подключения к базе данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель для хранения статистики пользователей
class UserStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)  # Идентификатор пользователя
    action = db.Column(db.String(100), nullable=False)  # Тип действия (например, посещение страницы)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Время действия

# Модель для хранения статистики команд
class CommandStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    command_name = db.Column(db.String(100), nullable=False)  # Название команды
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Время выполнения команды

# Создание таблиц базы данных
with app.app_context():
    db.create_all()

# Логирование действий пользователя
def log_user_action(user_id, action):
    stat = UserStat(user_id=user_id, action=action)
    db.session.add(stat)
    db.session.commit()

# Логирование использования команды
def log_command_usage(command_name):
    stat = CommandStat(command_name=command_name)
    db.session.add(stat)
    db.session.commit()

# Главная страница
@app.route('/')
def index():
    user_id = request.remote_addr  # Используем IP-адрес как идентификатор пользователя
    log_user_action(user_id, 'visit_home')  # Логируем посещение главной страницы
    return render_template('index.html')

# Выполнение команды (логирование использования команд)
@app.route('/command/<command_name>')
def run_command(command_name):
    log_command_usage(command_name)
    return f"Команда '{command_name}' выполнена и записана в статистику."

# Получение статистики по пользователям
@app.route('/stats/users')
def get_user_stats():
    stats = UserStat.query.all()

    # Группировка действий по дням
    grouped_by_day = db.session.query(
        db.func.date(UserStat.timestamp), db.func.count(UserStat.id)
    ).group_by(db.func.date(UserStat.timestamp)).all()

    # Группировка действий по месяцам
    grouped_by_month = db.session.query(
        db.func.strftime('%Y-%m', UserStat.timestamp), db.func.count(UserStat.id)
    ).group_by(db.func.strftime('%Y-%m', UserStat.timestamp)).all()

    return jsonify({
        'total_actions': len(stats),
        'actions_by_day': {str(day): count for day, count in grouped_by_day},
        'actions_by_month': {month: count for month, count in grouped_by_month}
    })

# Получение статистики по использованию команд
@app.route('/stats/commands')
def get_command_stats():
    stats = CommandStat.query.all()

    # Группировка команд по дням
    grouped_by_day = db.session.query(
        db.func.date(CommandStat.timestamp), db.func.count(CommandStat.id)
    ).group_by(db.func.date(CommandStat.timestamp)).all()

    # Группировка команд по месяцам
    grouped_by_month = db.session.query(
        db.func.strftime('%Y-%m', CommandStat.timestamp), db.func.count(CommandStat.id)
    ).group_by(db.func.strftime('%Y-%m', CommandStat.timestamp)).all()

    return jsonify({
        'total_commands': len(stats),
        'commands_by_day': {str(day): count for day, count in grouped_by_day},
        'commands_by_month': {month: count for month, count in grouped_by_month}
    })

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)

