import os

import connexion

from .config import CONFIG


options = {
    'swagger_ui': CONFIG['ENVIRONMENT'] == 'DEV'
}

app = connexion.App(__name__, specification_dir=os.getcwd(), options=options)

# Read the configuration file to configure the endpoints
app.add_api('apiconfiguration.yaml')


def start():
    app.run(port=CONFIG['PORT'], debug=CONFIG['VERBOSE'])