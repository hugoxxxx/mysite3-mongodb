from flask import Flask
from flask_bootstrap import Bootstrap
# 导入 Bootstrap

bootstrap = Bootstrap()
# 初始化bootstrap


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    bootstrap.init_app(app)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app

