from flask import Flask, render_template, redirect, request, abort, jsonify
from data import db_session
from data.users import User
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.login import LoginForm
from flask import make_response
from flask_restful import Api
from stockfish import Stockfish
import chess
import chess.svg
from forms.input_move_form import MoveForm

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
board = chess.Board()
my_stockfish = Stockfish('stockfish_15.1_win_x64_popcnt'
                         '/stockfish-windows-2022-x86-64-modern.exe')


def is_correct_move(move, board):
    for x in list(board.legal_moves):
        if move == str(x):
            return True
    return False


@app.route('/start_game', methods=['GET', 'POST'])
def display_field():
    form = MoveForm()
    board_svg = chess.svg.board(board=board)
    field_file = open('static/img/photo_board.svg', "w")
    field_file.write(board_svg)
    while not board.is_checkmate() or not board.is_variant_draw():
        if form.validate_on_submit():
            fl = is_correct_move(form.move.data, board)
            if fl:
                get_move = chess.Move.from_uci(form.move.data)
                board.push(get_move)
                board_svg = chess.svg.board(board=board)
                field_file = open('static/img/photo_board.svg', "w")
                field_file.write(board_svg)
                my_stockfish.set_fen_position(board.fen())
                best_move = chess.Move.from_uci(my_stockfish.get_best_move())
                board.push(best_move)
                board_svg = chess.svg.board(board=board)
                field_file = open('static/img/photo_board.svg', "w")
                field_file.write(board_svg)
        return render_template('display_field.html', title='Игра', form=form)


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
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
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
                                   message="Такой пользователь уже есть")
        user = User()
        user.surname = form.surname.data
        user.name = form.name.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.add(user)
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
