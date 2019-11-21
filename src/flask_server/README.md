# Flask APP for PAE

This application acts as a frontend manager for the backend that will communicate with the SimCom modules from our nodes.

## Blueprints

The app uses frequently blueprints, which allow to divide the routes into different python modules and join them in a main file.

## Templates

The initial idea is to template each response that will be returned and to not have HTML in the python code, for customizing the templates, as it is widely used on Flask apps, Jinja2 will be in charge.
