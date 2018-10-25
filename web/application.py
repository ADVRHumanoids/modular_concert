from flask import Flask, render_template, request, jsonify, send_from_directory

import URDF_writer

app = Flask(__name__, static_folder='static', static_url_path='')

#load view_urdf.html
@app.route('/')
def index():
    return render_template('view_urdf.html')

#call URDF_writer.py to modify the urdf
@app.route('/changeURDF/', methods=['POST'])
def changeURDF():
    filename = request.form.get('module_name', 0)
    print(filename)
    parent = request.form.get('parent', 0)
    print(parent)
    offset = float(request.form.get('angle_offset', 0))
    print(offset)
    data = URDF_writer.add_module(filename, offset)
    data = jsonify(data)
    return data 

@app.route('/writeURDF/', methods=['POST'])
def writeURDF():
    string = request.form.get('string', 0)
    print(string)
    data = URDF_writer.write_urdf(string)
    # data = jsonify(data)
    return data 

#call URDF_writer.py to add another master cube
@app.route('/addMasterCube/', methods=['POST'])
def addCube():
    filename = request.form.get('module_name', 0)
    print(filename)
    parent = request.form.get('parent', 0)
    print(parent)
    offset = float(request.form.get('angle_offset', 0))
    print(offset)
    data = URDF_writer.add_slave_cube(offset)
    data = jsonify(data)
    return data 

#call URDF_writer.py to remove the last module
@app.route('/removeModule/', methods=['POST'])
def remove():
    parent = request.form.get('parent', 0)
    data = URDF_writer.remove_module()
    data = jsonify(data)
    return data

#update "last module" (and so shown buttons) when clicking on it
@app.route('/updateLastModule/', methods=['POST'])
def accessModule():
    parent = request.form.get('parent', 0)
    data = URDF_writer.select_module(parent)
    data = jsonify(data)
    return data

#update "last module" (and so shown buttons) when clicking on it
@app.route('/openFile/', methods=['POST'])
def openFile():
    file_str = request.form.get('file', 0)
    print(file_str)
    data = URDF_writer.read_file(file_str)
    data = jsonify(data)
    return data

#upload on the server the /static folder
@app.route('/<path:path>')
def send_file(path):
    return send_from_directory(app.static_folder, path)


if __name__ == '__main__':
    app.run(debug=True, threaded=True) 
    # from gevent.pywsgi import WSGIServer
    # http_server = WSGIServer(('', 5000), app)
    # http_server.serve_forever()
