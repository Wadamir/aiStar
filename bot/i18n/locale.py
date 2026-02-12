from bot.i18n.languages import is_supported

DEFAULT_LOCALE = "en"


def detect_locale(event) -> str:
    if not event or not event.from_user:
        return DEFAULT_LOCALE

    tg_locale = event.from_user.language_code
    if not tg_locale:
        return DEFAULT_LOCALE

    short = tg_locale.split("-")[0]

    if not is_supported(short):
        return DEFAULT_LOCALE

    return short