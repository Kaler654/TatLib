import datetime
import os
import shutil
from distutils.command.upload import upload
from random import choice, shuffle

import requests
import sqlalchemy
from bs4 import BeautifulSoup
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
    mixins,
)
from html_from_epub import convert

from data import (
    books_api,
    db_session,
    levels_api,
    users_api,
    word_levels_api,
    words_api,
)
from data.books import Book
from data.levels import Level
from data.questions import Question
from data.users import User
from data.word_levels import Word_level
from data.words import Word
from forms.add_text import TextForm
from forms.login import LoginForm
from forms.quiz import QuizForm
from forms.register import RegisterForm


app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
login_manager = LoginManager()
login_manager.init_app(app)
user_progress = {}
max_question_id = 1
quiz_analyze_session = None
table_stage2time = {0: 0, 1: 1, 2: 3, 3: 5, 4: 6, 5: 13, 6: 28, 7: 58, 8: 118}


# для переводчика
IAM_TOKEN = 't1.9euelZrIk5HKi8iTy5qVlpWOnZPPy-3rnpWakIuJjMaPmpGVl5mNkpXKnZbl8_cSdC9s-e8SaV5t_t3z91IiLWz57xJpXm3' \
            '-.lnBmzsqrTNq1m26p7EXkf9Q1lj2i4q4SxnqB0E10qGoFuWLBuYWVR0rcZb9T5DfOlSdMbXVh9Bps46Xk5bP1CQ '
folder_id = 'b1g83nu3ghg9j3hciugr'
target_language_ru = 'ru'
target_language_tt = 'tt'
sourceLanguage_tat = 'tt'
sourceLanguage_rus = 'ru'
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {0}".format(IAM_TOKEN)
}
# для переводчика


def training_dict():
    try:
        now_time = datetime.datetime.now()
        final_dict = []
        wordlist = list(quiz_analyze_session.query(Word).all())
        userwordlist = list(
            quiz_analyze_session.query(Word)
            .filter(Word.id.in_([int(i) for i in current_user.words.split(",")]))
            .all()
        )
        shuffle(wordlist)
        shuffle(userwordlist)
        for word in range(len(userwordlist)):
            word_level = (
                quiz_analyze_session.query(Word_level)
                .filter(
                    Word_level.word_id == userwordlist[word].id,
                    Word_level.user_id == current_user.id,
                )
                .first()
            )
            date = word_level.date
            stage = word_level.word_level
            if stage == 8:
                quiz_analyze_session.delete(userwordlist[word], word_level)
                quiz_analyze_session.commit()
            final_dict.append([userwordlist[word].word])
            final_dict[word].append(userwordlist[word].word_ru)
            final_dict[word].append([userwordlist[word].word_ru])
            while len(final_dict[word][2]) < 4:
                ch = choice(wordlist)
                try_list = [i[0] for i in final_dict[word][2]]
                if ch.word not in try_list:
                    final_dict[word][2].append(ch.word_ru)
            shuffle(final_dict[word][2])
            for i in range(len(final_dict[word][2])):
                ind = 1 if final_dict[word][2][i] == final_dict[word][1] else 0
                final_dict[word][2][i] = (final_dict[word][2][i], ind)
        return final_dict
    except Exception:
        return []


def training3_dict():
    try:
        now_time = datetime.datetime.now()
        final_dict = []
        wordlist = list(quiz_analyze_session.query(Word).all())
        userwordlist = list(
            quiz_analyze_session.query(Word)
            .filter(Word.id.in_([int(i) for i in current_user.words.split(",")]))
            .all()
        )
        shuffle(wordlist)
        shuffle(userwordlist)
        for word in range(len(userwordlist)):
            word_level = (
                quiz_analyze_session.query(Word_level)
                .filter(
                    Word_level.word_id == userwordlist[word].id,
                    Word_level.user_id == current_user.id,
                )
                .first()
            )
            date = word_level.date
            stage = word_level.word_level
            if stage == 8:
                quiz_analyze_session.delete(userwordlist[word], word_level)
                quiz_analyze_session.commit()
            shuffled_word = list(userwordlist[word].word)
            shuffle(shuffled_word)
            final_dict.append([userwordlist[word].word, "".join(shuffled_word)])
        return final_dict
    except Exception:
        return []


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ["epub"]


def translate_tat_to_rus(word_tat):
    symbols = '.,?!@#$%^&*()_+-=":;[]{}<>~`№'
    for i in symbols:
        word_tat = word_tat.replace(i, '')
    body = {
        "targetLanguageCode": target_language_ru,
        "texts": word_tat,
        "folderId": folder_id,
        "sourceLanguageCode": sourceLanguage_tat
    }
    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                             json=body,
                             headers=headers
                             )
    return response.json()['translations'][0]['text']


def translate_rus_to_tat(word_rus):
    symbols = '.,?!@#$%^&*()_+-=":;[]{}<>~`№'
    for i in symbols:
        word_rus = word_rus.replace(i, '')
    body = {
        "targetLanguageCode": target_language_tt,
        "texts": word_rus,
        "folderId": folder_id,
        "sourceLanguageCode": sourceLanguage_rus
    }
    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                             json=body,
                             headers=headers
                             )
    return response.json()['translations'][0]['text']


def get_book(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    return book


def result_word(word):
    word = (
        word.replace(".", "").replace("?", "").replace("!", "").replace(",", "").lower()
    )
    if word != "null":
        translate_word = translate_tat_to_rus(word)
    else:
        translate_word = "Слово не выбрано"
    return translate_word


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template(
        "index.html",
    )


@app.errorhandler(401)
def not_found(error):
    return redirect("/register")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template(
            "login.html", message="Неправильный логин или пароль", form=form
        )
    return render_template("login.html", title="Авторизация", form=form)


@app.route("/register", methods=["GET", "POST"])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Пароли не совпадают",
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Такой пользователь уже есть",
            )
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/profile")
@login_required
def profile():
    created_time = datetime.datetime.strptime(str(current_user.created_date)[:-10], "%Y-%m-%d %H:%M")
    using_time = str(datetime.datetime.now() - created_time)[:-10].replace('days,', 'дн')
    using_time = using_time[:-3] + "ч " + using_time[-2:] + "мин"
    try:
        word_count = len(current_user.words.split(","))
    except:
        word_count = 0
    items_list = [
        ["Имя", current_user.name], ["Почта", current_user.email],
        ["Телеграм", current_user.telegram_id if current_user.telegram_id is not None else "Не указан"],
        ["Дата создания", str(created_time)],
        ["Время использования", using_time],
        ["Кол-во слов", word_count]
        ]
    return render_template("profile.html", items_list=items_list)


@app.route("/books_and_texts/<int:val>", methods=["GET", "POST"])
@login_required
def books_and_texts(val):
    db_sess = db_session.create_session()
    if request.method == "POST":
        books = db_sess.query(Book).filter(
            (Book.title.like(f"%{request.form.get('field')}%"))
            | (Book.author.like(f"%{request.form.get('field')}%"))
        )
        return render_template(
            "books_and_texts.html", title="книги и тексты", books=books
        )
    if val == 0:
        books = db_sess.query(Book).all()
    else:
        books = db_sess.query(Book).filter(Book.level_id == val).all()
    return render_template("books_and_texts.html", title="книги и тексты", books=books)


@app.route("/words", methods=["GET", "POST"])
@login_required
def words():
    try:
        db_sess = db_session.create_session()
        user_words_id = (
            db_sess.query(User.words)
            .filter(User.id == current_user.id)
            .first()[0]
            .split(",")
        )
        if request.method == "POST":
            if "search2" in request.form:
                words = db_sess.query(Word).filter(
                    (Word.word.like(f"%{request.form.get('field')}%")),
                    Word.id.in_(list(map(int, user_words_id))),
                )
                return render_template("words.html", title="мои слова", words=words)
            words = db_sess.query(Word).filter((Word.word_ru.like(f"%{request.form.get('field')}%")),
                Word.id.in_(list(map(int, user_words_id))),
            )
            return render_template("words.html", title="мои слова", words=words)
        user_words_id = (
            db_sess.query(User.words)
            .filter(User.id == current_user.id, Word.id.in_(list(map(int, user_words_id))))
            .first()[0]
        )
        user_words_id = user_words_id.split(",")
        words = db_sess.query(Word).filter(Word.id.in_(list(map(int, user_words_id)))).all()
        return render_template("words.html", title="мои слова", words=words)
    except:
        return render_template("words.html", title="мои слова", words=[])


@app.route("/books", methods=["GET", "POST"])
@login_required
def books():
    db_sess = db_session.create_session()
    if request.method == "POST":
        books = (
            db_sess.query(Book)
            .filter(
                Book.user_author_id == current_user.id,
                Book.title.like(f"%{request.form.get('field')}%"),
            )
            .all()
        )
        return render_template("books.html", title="мои слова", books=books)
    books = db_sess.query(Book).filter(Book.user_author_id == current_user.id).all()
    return render_template("books.html", title="мои слова", books=books)


@app.route("/add_text", methods=["GET", "POST"])
@login_required
def add_text():
    form = TextForm()
    if form.validate_on_submit():
        if (
            form.author.data
            and form.title.data
            and form.file.data
            and form.difficult.data
        ):
            db_sess = db_session.create_session()
            max_id = db_sess.query(Book).order_by(Book.id).all()
            if not max_id:
                max_id = 1
            else:
                max_id = max_id[-1].id + 1
            book = Book()
            book.author = form.author.data
            book.title = form.title.data
            book.level_id = form.difficult.data
            if allowed_file(form.file.data.filename):
                f = request.files["file"]
                path = f"books\{max_id}.epub"
                f.save(path)
                os.mkdir(f"books\{max_id}")
                shutil.move(f"books\{max_id}.epub", f"books\{max_id}\{max_id}.epub")
            convert(f"books/{max_id}/{max_id}.epub")
            shutil.move(f"{max_id}/", f"books/{max_id}/")
            book.pages = 0
            for i in os.listdir(f"books/{max_id}/{max_id}"):
                if i.startswith("content") and i.endswith(".html"):
                    try:
                        test_ = int(i[7:-5])
                        book.pages += 1
                    except:
                        pass
            book.user_author_id = current_user.id
            db_sess.merge(current_user)
            db_sess.add(book)
            db_sess.commit()
            return redirect("/books_and_texts/0")
        return render_template(
            "add_text.html", message="не все поля заполнены", form=form
        )
    return render_template("add_text.html", title="добавление текста", form=form)


@app.route("/trainings")
def trainings():
    return render_template("trainings.html")


@app.route("/training/1", methods=["GET", "POST"])
def training1_form():
    if request.method == "GET" and not isinstance(
        current_user, mixins.AnonymousUserMixin
    ):
        try:
            print(user_progress)
            if (
                user_progress[current_user.id]["tr1"]["question_training_number"]
                == user_progress[current_user.id]["tr1"]["train_len"]
            ):
                try:
                    user_progress[current_user.id]["tr1"] = {
                        "id": current_user.id,
                        "question_training_number": 0,
                        "count_training": 0,
                        "showed": False,
                        "training_program": training_dict(),
                    }
                    user_progress[current_user.id]["tr1"]["train_len"] = len(
                        user_progress[current_user.id]["tr1"]["training_program"]
                    )
                except KeyError:
                    user_progress[current_user.id] = {}
                    user_progress[current_user.id]["tr1"] = {
                        "id": current_user.id,
                        "question_training_number": 0,
                        "count_training": 0,
                        "showed": False,
                        "training_program": training_dict(),
                    }
                    user_progress[current_user.id]["tr1"]["train_len"] = len(
                        user_progress[current_user.id]["tr1"]["training_program"]
                    )
        except:
            try:
                user_progress[current_user.id]["tr1"] = {
                    "id": current_user.id,
                    "question_training_number": 0,
                    "count_training": 0,
                    "showed": False,
                    "training_program": training_dict(),
                }
                user_progress[current_user.id]["tr1"]["train_len"] = len(
                    user_progress[current_user.id]["tr1"]["training_program"]
                )
            except KeyError:
                user_progress[current_user.id] = {}
                user_progress[current_user.id]["tr1"] = {
                    "id": current_user.id,
                    "question_training_number": 0,
                    "count_training": 0,
                    "showed": False,
                    "training_program": training_dict(),
                }
                user_progress[current_user.id]["tr1"]["train_len"] = len(
                    user_progress[current_user.id]["tr1"]["training_program"]
                )
        train = user_progress[current_user.id]["tr1"]["training_program"]
        if not train:
            return render_template("no_words.html")
        num = user_progress[current_user.id]["tr1"]["question_training_number"]
        params = {
            "question": train[num][0],
            "answers": train[num][2],
            "current_answer": train[num][1],
            "title": "Training",
        }
        return render_template("training1.html", **params)
    elif request.method == "POST" and type(current_user) != "AnonymousUserMixin":
        num = user_progress[current_user.id]["tr1"]["question_training_number"]
        train = user_progress[current_user.id]["tr1"]["training_program"]
        if request.form is not None:
            if len(request.form) > 1:
                user_progress[current_user.id]["tr1"]["question_training_number"] += 1
                user_progress[current_user.id]["tr1"]["count_training"] += int(
                    request.form["radio"]
                )
                last_word = (
                    quiz_analyze_session.query(Word)
                    .filter(Word.word == train[num][0])
                    .first()
                )
                if (
                    int(request.form["radio"]) == 1
                ):  # int(request.form["radio"]) [0 or 1] правильность слова
                    # last_word.level += 1
                    pass
                elif int(request.form["radio"]) == 0:
                    last_word.level = 0
                quiz_analyze_session.commit()
        if (
            user_progress[current_user.id]["tr1"]["question_training_number"]
            == user_progress[current_user.id]["tr1"]["train_len"]
        ):
            return redirect("/training/1_result")
        return redirect("/training/1")
    else:
        return redirect("/register")


@app.route("/training/1_result")
def training1_result():
    try:
        count = user_progress[current_user.id]["tr1"]["count_training"]
        level = user_progress[current_user.id]["tr1"]["question_training_number"]
    except:
        return redirect("/training/1")
    params = {"count": count, "level": level, "title": "Training Result"}
    if user_progress[current_user.id]["tr1"]["showed"]:
        return render_template("training1_rezult.html", **params)
    level_name = count / level
    if level_name < 0.3334:
        level_name = "Новичок"
    elif level_name < 0.6667:
        level_name = "Средний"
    else:
        level_name = "Профи"
    params["level_name"] = level_name
    user = quiz_analyze_session.query(User).filter(User.id == current_user.id).first()
    id_ = (
        quiz_analyze_session.query(Level)
        .filter(Level.name == level_name)
        .first()
        .level_id
    )
    user.level_id = id_
    quiz_analyze_session.commit()
    user_progress[current_user.id]["tr1"]["showed"] = True
    return render_template("training1_rezult.html", **params)


@app.route("/training/3", methods=["GET", "POST"])
def training3_form():
    if request.method == "GET" and not isinstance(
        current_user, mixins.AnonymousUserMixin
    ):
        try:
            if (
                user_progress[current_user.id]["tr3"]["question_training_number"]
                == user_progress[current_user.id]["tr3"]["train_len"]
            ):
                try:
                    user_progress[current_user.id]["tr3"] = {
                        "id": current_user.id,
                        "question_training_number": 0,
                        "count_training": 0,
                        "showed": False,
                        "training_program": training3_dict(),
                    }
                    user_progress[current_user.id]["tr3"]["train_len"] = len(
                        user_progress[current_user.id]["tr3"]["training_program"]
                    )
                except KeyError:
                    user_progress[current_user.id] = {}
                    user_progress[current_user.id]["tr3"] = {
                        "id": current_user.id,
                        "question_training_number": 0,
                        "count_training": 0,
                        "showed": False,
                        "training_program": training3_dict(),
                    }
                    user_progress[current_user.id]["tr3"]["train_len"] = len(
                        user_progress[current_user.id]["tr3"]["training_program"]
                    )
        except:
            try:
                user_progress[current_user.id]["tr3"] = {
                    "id": current_user.id,
                    "question_training_number": 0,
                    "count_training": 0,
                    "showed": False,
                    "training_program": training3_dict(),
                }
                user_progress[current_user.id]["tr3"]["train_len"] = len(
                    user_progress[current_user.id]["tr3"]["training_program"]
                )
            except KeyError:
                user_progress[current_user.id] = {}
                user_progress[current_user.id]["tr3"] = {
                    "id": current_user.id,
                    "question_training_number": 0,
                    "count_training": 0,
                    "showed": False,
                    "training_program": training3_dict(),
                }
                user_progress[current_user.id]["tr3"]["train_len"] = len(
                    user_progress[current_user.id]["tr3"]["training_program"]
                )
        train = user_progress[current_user.id]["tr3"]["training_program"]
        if not train:
            return render_template("no_words.html")
        num = user_progress[current_user.id]["tr3"]["question_training_number"]
        params = {"question": train[num][1]}
        return render_template("training3.html", **params)
    elif request.method == "POST" and type(current_user) != "AnonymousUserMixin":
        num = user_progress[current_user.id]["tr3"]["question_training_number"]
        train = user_progress[current_user.id]["tr3"]["training_program"]
        if request.form is not None:
            if len(request.form) > 1:
                user_progress[current_user.id]["tr3"]["question_training_number"] += 1
                last_word = (
                    quiz_analyze_session.query(Word)
                    .filter(Word.word == train[num][0])
                    .first()
                )
                if request.form["user_answer"] == train[num][0]:
                    user_progress[current_user.id]["tr3"]["count_training"] += 1
                    # last_word.level += 1
                    pass
                else:
                    last_word.level = 0
                quiz_analyze_session.commit()
        if (
            user_progress[current_user.id]["tr3"]["question_training_number"]
            == user_progress[current_user.id]["tr3"]["train_len"]
        ):
            return redirect("/training/3_result")
        return redirect("/training/3")
    else:
        return redirect("/register")


@app.route("/training/3_result")
def training3_result():
    try:
        count = user_progress[current_user.id]["tr3"]["count_training"]
        level = user_progress[current_user.id]["tr3"]["question_training_number"]
    except:
        return redirect("/training/3")
    params = {"count": count, "level": level}
    if user_progress[current_user.id]["tr3"]["showed"]:
        return render_template("training_rezult.html", **params)
    level_name = count / level
    if level_name < 0.3334:
        level_name = "Новичок"
    elif level_name < 0.6667:
        level_name = "Средний"
    else:
        level_name = "Профи"
    params["level_name"] = level_name
    user = quiz_analyze_session.query(User).filter(User.id == current_user.id).first()
    id_ = (
        quiz_analyze_session.query(Level)
        .filter(Level.name == level_name)
        .first()
        .level_id
    )
    user.level_id = id_
    quiz_analyze_session.commit()
    user_progress[current_user.id]["tr3"]["showed"] = True
    return render_template("training3_rezult.html", **params)


def set_max_question_id():
    global max_question_id, quiz_analyze_session
    quiz_analyze_session = db_session.create_session()
    try:
        max_question_id = (
            quiz_analyze_session.query(Question).order_by(Question.id.desc()).first().id
        )
    except:
        max_question_id = 0


@app.route("/read_book/<int:book_id>/<int:page>/<word>", methods=["GET", "POST"])
def book_view(book_id, page, word):
    if request.method == "POST":
        tat_word = word.lower().replace(',', '').replace('!', '').replace('.', '').replace('?', '').replace('"', '').replace("'", '')
        rus_word = result_word(tat_word)
        db_sess = db_session.create_session()
        word1 = Word(word=tat_word, word_ru=rus_word)
        db_sess.add(word1)
        db_sess.commit()
        max_id = db_sess.query(Word).order_by(Word.id).all()[-1].id
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user.words:
            user.words = user.words + ',' + str(max_id)
        else:
            user.words = str(max_id)
        wl = Word_level()
        wl.user_id = current_user.id
        wl.word_id = max_id
        wl.word_level = 0
        db_sess.add(wl)
        db_sess.commit()
    book = get_book(book_id)
    if book:
        pages = book.pages
        if book and 1 <= page <= pages:
            html = open(
                f"books/{book_id}/{book_id}/content{page - 1}.html",
                "r",
                encoding="utf-8",
            ).read()
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text().split("\n")
        text = [x.split() for x in text if x]
        translate_word = result_word(word)
        return render_template(
            "read_book.html",
            text=text,
            page=page,
            pages=pages,
            click_word=word,
            translate_word=translate_word,
        )
    return render_template("404.html")


def main():
    db_session.global_init("db/database.db")
    set_max_question_id()
    app.register_blueprint(books_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.register_blueprint(words_api.blueprint)
    app.register_blueprint(levels_api.blueprint)
    app.register_blueprint(word_levels_api.blueprint)
    app.run(port=8080, host="127.0.0.1")


if __name__ == "__main__":
    main()
