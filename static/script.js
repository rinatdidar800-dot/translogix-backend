document.addEventListener("DOMContentLoaded", function () {
    window.scrollToContact = function () {
        const contact = document.getElementById("contact");
        if (contact) {
            contact.scrollIntoView({ behavior: "smooth" });
        }
    };

    const langToggle = document.getElementById("langToggle");
    const form = document.getElementById("contactForm");
    const formMessage = document.getElementById("formMessage");

    let currentLang = "ru";

    const translations = {
        ru: {
            nameError: "Имя должно содержать минимум 2 символа.",
            phoneError: "Введите корректный телефон.",
            messageError: "Опишите груз подробнее.",
            directionError: "Выберите направление перевозки."
        },
        kz: {
            nameError: "Аты кемінде 2 таңбадан тұруы керек.",
            phoneError: "Дұрыс телефон нөмірін енгізіңіз.",
            messageError: "Жүктің сипаттамасын толығырақ жазыңыз.",
            directionError: "Тасымалдау бағытын таңдаңыз."
        }
    };

    function updateLanguage(lang) {
        document.querySelectorAll("[data-lang-ru]").forEach(el => {
            const value = el.getAttribute(`data-lang-${lang}`);
            if (value) {
                el.textContent = value;
            }
        });

        document.querySelectorAll("[data-placeholder-ru]").forEach(el => {
            const value = el.getAttribute(`data-placeholder-${lang}`);
            if (value) {
                el.placeholder = value;
            }
        });

        if (langToggle) {
            langToggle.textContent = lang === "ru" ? "Қаз / Рус" : "Рус / Қаз";
        }
    }

    if (langToggle) {
        langToggle.addEventListener("click", () => {
            currentLang = currentLang === "ru" ? "kz" : "ru";
            updateLanguage(currentLang);
        });
    }

    if (!form || !formMessage) {
        return;
    }

    form.addEventListener("submit", function (e) {
        const name = document.getElementById("name").value.trim();
        const phone = document.getElementById("phone").value.trim();
        const message = document.getElementById("message").value.trim();
        const direction = document.querySelector('input[name="direction"]:checked');

        const phoneRegex = /^[\d\s()+-]{6,}$/;

        clearMessage();

        if (!direction) {
            e.preventDefault();
            showError(translations[currentLang].directionError);
            return;
        }

        if (name.length < 2) {
            e.preventDefault();
            showError(translations[currentLang].nameError);
            return;
        }

        if (!phoneRegex.test(phone)) {
            e.preventDefault();
            showError(translations[currentLang].phoneError);
            return;
        }

        if (message.length < 5) {
            e.preventDefault();
            showError(translations[currentLang].messageError);
            return;
        }
    });

    function showError(text) {
        formMessage.textContent = text;
        formMessage.style.color = "#a12626";
    }

    function clearMessage() {
        formMessage.textContent = "";
    }
});