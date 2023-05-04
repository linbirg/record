from lib.yeab.web import get 


@get('/')
def index():
    return "<p>hello yeab!</p>"