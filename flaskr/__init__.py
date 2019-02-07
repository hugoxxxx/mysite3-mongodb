from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # bootstrap  sample
    @app.route('/home')
    def home():
        return render_template('home.html', title_name='welcome')

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app

