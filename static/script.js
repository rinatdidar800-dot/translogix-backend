// =====================
// ИНИЦИАЛИЗАЦИЯ ПОСЛЕ ЗАГРУЗКИ DOM
// =====================
document.addEventListener("DOMContentLoaded", function () {

    // ---------- Плавная прокрутка ----------
    window.scrollToContact = function () {
        const contact = document.getElementById("contact");
        if (contact) {
            contact.scrollIntoView({ behavior: "smooth" });
        }
    };

    // ---------- Переключение языка ----------
    const langToggle = document.getElementById("langToggle");
    let currentLang = "ru";

    const translations = {
        ru: {
            nameError: "Имя должно содержать минимум 2 символа.",
            phoneError: "Введите корректный телефон.",
            messageError: "Опишите груз подробнее.",
            directionError: "Выберите направление перевозки.",
            success: "Заявка успешно отправлена!"
        },
        kz: {
            nameError: "Аты кемінде 2 таңбадан тұруы керек.",
            phoneError: "Дұрыс телефон нөмірін енгізіңіз.",
            messageError: "Жүктің сипаттамасын жазыңыз.",
            directionError: "Тасымалдау бағытын таңдаңыз.",
            success: "Өтініш сәтті жіберілді!"
        }
    };

    if (langToggle) {
        langToggle.addEventListener("click", () => {
            currentLang = currentLang === "ru" ? "kz" : "ru";

            // Перевод текста
            document.querySelectorAll("[data-lang-ru]").forEach(el => {
                const value = el.getAttribute(`data-lang-${currentLang}`);
                if (value) el.textContent = value;
            });

            // Перевод placeholder
            document.querySelectorAll("[data-placeholder-ru]").forEach(el => {
                const value = el.getAttribute(`data-placeholder-${currentLang}`);
                if (value) el.placeholder = value;
            });

            // Текст кнопки
            langToggle.textContent = currentLang === "ru" ? "Қаз / Рус" : "Рус / Қаз";
        });
    }

    // ---------- Форма ----------
    const form = document.getElementById("contactForm");
    const formMessage = document.getElementById("formMessage");

    if (!form || !formMessage) return;

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const name = document.getElementById("name").value.trim();
        const phone = document.getElementById("phone").value.trim();
        const message = document.getElementById("message").value.trim();
        const direction = document.querySelector('input[name="direction"]:checked');

        if (!direction) {
            showError(translations[currentLang].directionError);
            return;
        }

        if (name.length < 2) {
            showError(translations[currentLang].nameError);
            return;
        }
        const phoneRegex = /^[\d\s()+-]{6,}$/;
        if (!phoneRegex.test(phone)) {
            showError(translations[currentLang].phoneError);
            return;
        }

        if (message.length < 5) {
            showError(translations[currentLang].messageError);
            return;
        }

        // Успех
        formMessage.textContent = translations[currentLang].success;
        formMessage.style.color = "green";

        // Отправка формы
        form.submit();
    });

    function showError(text) {
        formMessage.textContent = text;
        formMessage.style.color = "red";
    }

});