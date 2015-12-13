from app import app

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.


@app.template_filter()
def format_datetime(value):
    try:
        return value.strftime("%d.%m.%Y %H:%M:%S")
    except AttributeError as e:
        return value, str(e.message)
