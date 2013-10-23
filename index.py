import sys
yourappname = "/home/elevate/webapps/gitepack/htdocs"
if not yourappname in sys.path:
    sys.path.insert(0, yourappname)


from app import app as application
