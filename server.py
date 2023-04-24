from flask import Flask, render_template, redirect, request, abort, jsonify, url_for
from data import db_session
from data.users import User
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.login import LoginForm
from data.rating import Rating
import datetime
from stockfish import Stockfish
import chess
import chess.svg
from forms.input_move_form import MoveForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
games_dict = {}


def is_correct_move(move, board):
    try:
        test_move = chess.Move.from_uci(str(move))
        if board.is_legal(test_move):
            return True
        for x in list(board.legal_moves):
            if move == str(x):
                return True
        return False
    except Exception:
        return False


def get_rating():
    try:
        id = current_user.id
        db_sess = db_session.create_session()
        rating = db_sess.query(Rating).filter(Rating.user_id == id).first()
        user = db_sess.query(User).filter(User.id == id).first()
        data_reg = user.modified_date
        today = datetime.datetime.today()
        d = (today - data_reg)
        if d.days:
            hours = d.days * 24 + int((str(d).split(', ')[1]).split(':')[0])
        else:
            hours = int((str(d).split(':')[0]))
    except AttributeError:
        rating = None
        hours = None
    return rating, hours


@app.route('/start_game/<int:level>', methods=['GET', 'POST'])
def display_field(level):
    global games_dict
    id = current_user.id
    my_stockfish = games_dict[id][1]
    board = games_dict[id][0]
    end_game = games_dict[id][2]
    if level == 1:
        my_stockfish.set_skill_level(2)
    elif level == 2:
        my_stockfish.set_skill_level(5)
    elif level == 3:
        my_stockfish.set_skill_level(8)
    else:
        my_stockfish.set_skill_level(1)
    if not current_user.is_authenticated:
        return redirect("/")
    try:
        if games_dict[id][3] != level:
            if board != chess.Board():
                board = chess.Board()
                board_svg = chess.svg.board(board=board)
                field_file = open(f'static/img/photo_board{id}.svg', "w")
                field_file.write(board_svg)
                games_dict[id] = [board, my_stockfish, end_game]
            else:
                games_dict[id][3] = level
    except Exception:
        games_dict[id].append(level)
    photo = url_for('static', filename=f'img/photo_board{id}.svg')
    if not end_game:
        form = MoveForm()
        board_svg = chess.svg.board(board=board)
        field_file = open(f'static/img/photo_board{id}.svg', "w")
        field_file.write(board_svg)
        rating, hours = get_rating()
        while not board.is_checkmate() or not board.is_variant_draw():
            if form.validate_on_submit():
                if form.move.data == 'reset':
                    board = chess.Board()
                    board_svg = chess.svg.board(board=board)
                    field_file = open(f'static/img/photo_board{id}.svg', "w")
                    field_file.write(board_svg)
                    games_dict[id] = [board, my_stockfish, end_game]
                    return render_template('display_field.html', title='Игра', form=form,
                                           rating=rating, hours=hours,
                                           photo=photo)
                else:
                    fl = is_correct_move(form.move.data, board)
                    if fl:
                        get_move = chess.Move.from_uci(form.move.data)
                        board.push(get_move)
                        board_svg = chess.svg.board(board=board)
                        field_file = open(f'static/img/photo_board{id}.svg', "w")
                        field_file.write(board_svg)
                        if board.is_checkmate():
                            end_game = True
                            id = current_user.id
                            db_sess = db_session.create_session()
                            rating = db_sess.query(Rating).filter(Rating.user_id == id).first()
                            rating.wins += 1
                            if rating.points <= 1000:
                                if level == 1:
                                    rating.points += 10
                                elif level == 2:
                                    rating.points += 40
                                elif level == 3:
                                    rating.points += 70
                            elif 1000 < rating.points <= 1500:
                                if level == 2:
                                    rating.points += 20
                                elif level == 3:
                                    rating.points += 40
                            elif 1500 < rating.points:
                                if level == 2:
                                    rating.points += 5
                                elif level == 3:
                                    rating.points += 20
                            db_sess.commit()
                            return render_template('display_field.html', title='Игра', form=form,
                                                   rating=rating,
                                                   hours=hours, win=True, lose=False, draw=False,
                                                   photo=photo)
                        elif board.is_variant_draw():
                            end_game = True
                            return render_template('display_field.html', title='Игра', form=form,
                                                   rating=rating,
                                                   hours=hours, draw=True, win=False, lose=False,
                                                   photo=photo)
                        my_stockfish.set_fen_position(board.fen())
                        best_move = chess.Move.from_uci(my_stockfish.get_best_move())
                        board.push(best_move)
                        board_svg = chess.svg.board(board=board)
                        field_file = open(f'static/img/photo_board{id}.svg', "w")
                        field_file.write(board_svg)
                        if board.is_checkmate():
                            end_game = True
                            id = current_user.id
                            db_sess = db_session.create_session()
                            rating = db_sess.query(Rating).filter(Rating.user_id == id).first()
                            rating.losses += 1
                            if rating.points <= 1000:
                                if level == 1:
                                    rating.points -= 5
                            elif 1000 < rating.points < 1500:
                                if level == 1:
                                    rating.points -= 15
                                elif level == 2:
                                    rating.points -= 5
                            elif 1500 < rating.points:
                                if level == 1:
                                    rating.points -= 40
                                elif level == 2:
                                    rating.points -= 20
                                elif level == 3:
                                    rating.points -= 5
                            rating.points = max(0, rating.points)
                            db_sess.commit()
                            return render_template('display_field.html', title='Игра', form=form,
                                                   rating=rating,
                                                   hours=hours, lose=True, win=False, draw=False,
                                                   photo=photo)
                        elif board.is_variant_draw():
                            end_game = True
                            return render_template('display_field.html', title='Игра', form=form,
                                                   rating=rating,
                                                   hours=hours, draw=True, lose=False, win=False,
                                                   photo=photo)
                        elif board.is_check():
                            return render_template('display_field.html', title='Игра', form=form,
                                                   rating=rating,
                                                   hours=hours, check=True,
                                                   photo=photo)
            return render_template('display_field.html', title='Игра', form=form, rating=rating,
                                   hours=hours, photo=photo)
    form = MoveForm()
    rating, hours = get_rating()
    return render_template('display_field.html', title='Игра', form=form, rating=rating,
                           hours=hours, photo=photo)


def main():
    db_session.global_init("db/game_of_chess.db")
    app.run()


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            global games_dict
            board = chess.Board()
            my_stockfish = Stockfish('stockfish_15.1_win_x64_popcnt'
                                     '/stockfish-windows-2022-x86-64-modern.exe')
            id = current_user.id
            end_game = False
            games_dict[id] = [board, my_stockfish, end_game]
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/make_field_by_moves')
def make_field_by_moves():
    rating, hours = get_rating()
    return render_template('upload_file.html', rating=rating, title='Составление поля', hours=hours)


@app.route('/success', methods=['POST'])
def success():
    rating, hours = get_rating()
    if request.method == 'POST':
        f = request.files['file']
        if f.filename[-3:] == 'txt':
            test_board = chess.Board()
            f.save(f.filename)
            with open(f.filename, 'r', encoding='utf-8') as file:
                data = file.readlines()
            os.remove(f.filename)
            for move in data:
                move = move.strip()
                try:
                    corr_move = chess.Move.from_uci(move)
                    if corr_move in list(test_board.legal_moves):
                        test_board.push(corr_move)
                    else:
                        return render_template("field_by_moves.html", error=2,
                                               rating=rating, title='Составление поля', hours=hours)
                except:
                    return render_template("field_by_moves.html", error=2,
                                           rating=rating, title='Составление поля', hours=hours)
            board_svg = chess.svg.board(board=test_board)
            field_file = open('static/img/board_by_moves.svg', "w")
            field_file.write(board_svg)
            return render_template("field_by_moves.html", error=0, rating=rating,
                                   title='Составление поля', hours=hours)
        else:
            return render_template("field_by_moves.html", error=1, rating=rating,
                                   title='Составление поля', hours=hours)


@app.route("/")
def index():
    rating, hours = get_rating()
    return render_template("index.html", rating=rating, title='Главная страница', hours=hours)


@app.route("/rating")
def ratings():
    db_sess = db_session.create_session()
    ratings_users = db_sess.query(Rating).order_by(Rating.points.desc()).all()
    n = len(list(ratings_users))
    a = 1
    arr_rating = []
    for i in range(n):
        arr_rating.append((a, ratings_users[i].user.username, ratings_users[i].points))
        if i + 1 < n:
            if ratings_users[i].points > ratings_users[i + 1].points:
                a += 1
    return render_template("rating.html", rating=arr_rating, title='Рейтинг пользователй')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Аккаунт с этой почтой уже существует")
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такое имя пользователя уже существует")
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        rating = Rating()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        rating.user_id = user.id
        db_sess.add(rating)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
