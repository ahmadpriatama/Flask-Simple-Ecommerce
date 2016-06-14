import os
from appname import create_app

port = int(os.environ.get("PORT", 5001))
env = os.environ.get('APPNAME_ENV', 'dev')
app = create_app('appname.settings.%sConfig' % env.capitalize())
app.config['DEBUG'] = True
# app.run(debug=True, port=port)
