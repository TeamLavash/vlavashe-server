from flask import Flask, url_for, request, json
import user
import shawarma

app = Flask(__name__)

@app.route('/')
def api_root():
    return 'Welcome'

@app.route('/articles')
def api_articles():
    return 'List of ' + url_for('api_articles')

@app.route('/articles/<articleid>')
def api_article(articleid):
    return 'You are reading ' + articleid

@app.route('/sign_up', methods = ['POST'])
def api_sign_up():
	resp = user.sign_up(request.json)
	return json.dumps(resp)


@app.route('/sign_in', methods = ['POST'])
def api_sign_in():
	resp = user.sign_in(request.json)
	return json.dumps(resp)


@app.route('/favourite', methods = ['POST'])
def api_favourite():
	resp = user.get_favourite(request.json)
	return json.dumps(resp)


@app.route('/favourite_add', methods = ['POST'])
def api_favourite_add():
	resp = user.add_favourite(request.json)
	return json.dumps(resp)


@app.route('/favourite_remove', methods = ['POST'])
def api_favourite_remove():
	resp = user.remove_favourite(request.json)
	return json.dumps(resp)


@app.route('/shawa_add', methods = ['POST'])
def api_shawa_add():
	resp = shawarma.add_shawarma(request.json)
	return json.dumps(resp)


@app.route('/comments', methods = ['POST'])
def api_comments():
	resp = shawarma.get_comments(request.json)
	return json.dumps(resp)


@app.route('/comment_add', methods = ['POST'])
def api_comment_add():
	resp = shawarma.add_comment(request.json)
	return json.dumps(resp)


@app.route('/more', methods = ['POST'])
def api_more():
	resp = shawarma.more(request.json)
	return json.dumps(resp)


@app.route('/search', methods = ['POST'])
def api_search():
	resp = shawarma.search(request.json)
	return json.dumps(resp)


@app.route('/messages', methods = ['POST'])
def api_message():

    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        return "JSON Message: " + json.dumps(request.json)

    else:
        return "415 Unsupported Media Type ;)"

if __name__ == '__main__':
    app.run()