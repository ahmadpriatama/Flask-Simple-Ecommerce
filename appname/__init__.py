#! ../env/bin/python

from flask import Flask
from webassets.loaders import PythonLoader as PythonAssetsLoader

from appname import assets
from appname.models import db
from appname.controllers.main import main
from appname.controllers.categories import categories
from appname.controllers.products import products
from appname.controllers.catalogs import catalogs
from flask_bootstrap import Bootstrap
from flask import send_from_directory
import os

from appname.extensions import (
    cache,
    assets_env,
    debug_toolbar,
    login_manager
)


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. appname.settings.ProdConfig
    """

    app = Flask(__name__)

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory('/home/ahmad/workspace/python/Flask-CRUD/uploads/', filename)

    Bootstrap(app)

    app.config.from_object(object_name)

    # initialize the cache
    cache.init_app(app)

    # initialize the debug tool bar
    debug_toolbar.init_app(app)

    # initialize SQLAlchemy
    db.init_app(app)
    db.app = app

    login_manager.init_app(app)

    # Import and register the different asset bundles
    assets_env.init_app(app)
    with app.app_context():
        assets_env.load_path = [
            os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), 'node_modules'),
            os.path.join(os.path.dirname(__file__), 'static'),
        ]
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().items():
        assets_env.register(name, bundle)

    # register our blueprints
    app.register_blueprint(main)
    app.register_blueprint(categories)
    app.register_blueprint(products)
    app.register_blueprint(catalogs)

    return app
