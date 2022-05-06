// Меню бургер
const iconMenu = document.querySelector('.menu__icon');
const menuBody = document.querySelector('.menu__body');
const headerContacts = document.querySelector('.header__items');
if (iconMenu) {

    iconMenu.addEventListener("click", function(e) {
        document.body.classList.toggle('_lock');
        iconMenu.classList.toggle('_active');
        menuBody.classList.toggle('_active');
        headerContacts.classList.toggle('_active');
    });
}

// Курсор

// const cursor = document.querySelector('.tatar__cursor');

// document.addEventListener('mousemove', e => {
//     cursor.setAttribute("style", "top: " + (e.pageY) + "px; left: " + (e.pageX) + "px;")
// })


let scrollpos = window.scrollY

const header = document.getElementById('book__left__header');
const text_scroll = document.getElementById('text_scroll');
const book__right_ = document.getElementById('book__right__scroll');
console.log(header);
const scrollChange = 350;

const add_class_on_scroll = () => {
    header.classList.add("book__left_");
    text_scroll.classList.add("text_scroll");
    book__right_.classList.add("book__right_")
};
const remove_class_on_scroll = () => {
    header.classList.remove("book__left_");
    text_scroll.classList.remove("text_scroll");
    book__right_.classList.remove("book__right_")
};

window.addEventListener('scroll', function() {
    scrollpos = window.scrollY;

    if (scrollpos >= scrollChange) { add_class_on_scroll() } else { remove_class_on_scroll() }

})