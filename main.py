from flask import Flask, render_template, url_for, request
from data import db_session
from data.books import Book
from data.users import User
from data.words import Word
from flask_login import LoginManager, logout_user, current_user
from html_from_epub import convert
from bs4 import BeautifulSoup
import os
import shutil
from distutils.command.upload import upload
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
login_manager = LoginManager()
login_manager.init_app(app)


def to_normal_words(html_str, delimitel):
    try:
        ind = html_str.index(delimitel) + len(delimitel) + 1
        final_str = html_str[ind : -len(delimitel) - 3]
        return final_str
    except Exception as error:
        return None


def translate_tat_to_rus(text):
    url = "https://translate.tatar/translate_hack/"
    params = {"lang": 1, "text": text}
    translated_text = requests.get(url, params=params).text.split("\n")
    final_json = {}
    if translated_text[0] != text:
        final_json["word"] = text
        try:
            final_json["speech_part"] = to_normal_words(translated_text[1], "POS")
        except Exception as error:
            final_json["speech_part"] = None
        try:
            final_json["main_translation"] = to_normal_words(
                translated_text[-1][:-6], "mt"
            )
        except Exception as error:
            final_json["main_translation"] = None
        try:
            final_json["translations"] = [
                to_normal_words(i, "translation") for i in translated_text[2:-3]
            ]
        except Exception as error:
            final_json["translations"] = [None]
        try:
            final_json["examples"] = [
                i.split(" – ")
                for i in to_normal_words(translated_text[-3], "examples").split(".  ")
            ]
        except Exception as error:
            final_json["examples"] = [[None, None]]
        return final_json
    else:
        return final_json


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def get_book(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    return book


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template(
        "homepage/home.html",
        link_css=url_for("static", filename="css/style.css"),
        link_logo=url_for("static", filename="img/logo.png"),
        link_js=url_for("static", filename="js/script.js"),
    )


def result_word(word):
    word = (
        word.replace(".", "").replace("?", "").replace("!", "").replace(",", "").lower()
    )
    if word != "null":
        dictionary = translate_tat_to_rus(word)
        if (
            "main_translation" in dictionary
            and dictionary["main_translation"] is not None
        ):
            translate_word = (
                dictionary["main_translation"]
                .replace(".", "")
                .replace("?", "")
                .replace("!", "")
                .replace(",", "")
                .lower()
            )
        else:
            translate_word = "Перевод отсутствует"
    else:
        translate_word = "Слово не выбрано"
    return translate_word


@app.route("/read_book/<int:book_id>/<int:page>/<word>", methods=["GET", "POST"])
def book_view(book_id, page, word):
    if request.method == "POST":
        tat_word = word
        rus_word = result_word(tat_word)

        db_sess = db_session.create_session()
        word = Word(word=tat_word, word_ru=rus_word)
        db_sess.add(word)
        db_sess.commit()
        max_id = db_sess.query(Word).order_by(Word.id).all()[-1]
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.words = user.words + str(max_id)
        db_sess.commit()

    book = get_book(book_id)
    if book:
        pages = book.pages
        if book and 1 <= page <= pages:
            # print(f'books/{book_id}/{book_id}.epub')
            # convert(f'books/{book_id}/{book_id}.epub')
            # shutil.move(f"{book_id}/", f"books/{book_id}/")
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
            "books/read_book.html",
            text=text,
            page=page,
            pages=pages,
            click_word=word,
            translate_word=translate_word,
            link_css=url_for("static", filename="css/style.css"),
            link_logo=url_for("static", filename="img/logo.png"),
            link_js=url_for("static", filename="js/script.js"),
        )
    return render_template("errors/404.html")


def main():
    db_session.global_init("db/database.db")
    app.run(port=8080, host="127.0.0.1")


if __name__ == "__main__":
    main()
