from flask import render_template, flash, redirect
from app import app
from .forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
	user = {'nickname' : 'Nikunj Shukla'}
	posts = [
		{
			'author' : {'nickname' : 'Nikunj Shukla'},
			'body' : 'Today I am sick and getting better'
		},
		{
			'author' : {'nickname' : 'Joey'},
			'body' : 'They are not breaking up'
		}
	]
	return render_template('index.html',
							title='Home',
							user=user,
							posts=posts)


@app.route('/status')
def status():
	return "hello, this is the status page!"


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('login requested for OpenID="%s", remember_me=%s' %
		(form.openid.data, str(form.remember_me.data)))
		return redirect('/index')
	return render_template('login.html',
						   title='Sign In',
						   form=form,
                    	   providers=app.config['OPENID_PROVIDERS'])
