"""User Agent Interaction handlers"""
#TODO: Client credentials UI Handler
from http.server import BaseHTTPRequestHandler, HTTPServer

"""
HTTP Server
"""
class StoppableHttpServer(HTTPServer):
    """http server that reacts to self.stop flag"""
    def serve_forever(self):
        """Handle one request at a time until stopped."""
        self.stop = False
        self.response_url = None
        while not self.stop:
            self.handle_request()
        return self.response_url

class HttpResponseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        from copy import copy
        #Send a Nice response back to client
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self.path.encode('ascii'))
        self.server.response_url = copy(self.path)
        #Stop the server
        self.server.stop = True
    def log_request(code = '-', size = '-'):
        pass

def run_http_server(pipe, port):
        httpd = StoppableHttpServer(('127.0.0.1', port), HttpResponseHandler)
        x = httpd.serve_forever()
        pipe.send(x)
        pipe.close()

def _run_http_server(port_pipe, pipe, port_range):
    import socket
    port = port_range[0]
    while port <= port_range[1]:
        try:
            httpd = StoppableHttpServer(('127.0.0.1', port), HttpResponseHandler)
            break
        except socket.error as e:
            if e.errno == 98 or e.errno == 13: #Address already in use or permission denied
                httpd = None
        port += 1
    if httpd is None:
        #Could not find a port
        port_pipe.send(0)
        port_pipe.close()
        return
    port_pipe.send(port)
    port_pipe.close()
    x = httpd.serve_forever()
    pipe.send(x)
    pipe.close()


def run_http_server(redirect_uri = None, modify_port = True, port_range = (10000, 10010) ):
    """Returns (modified) redirect_uri"""
    from multiprocessing import Process, Pipe
    from urllib.parse import urlsplit, urlunsplit
    if redirect_uri is None:
        redirect_uri = "http://localhost"
    p = urlsplit(redirect_uri)
    #Ensure hostname is localhost or 127.0.0.1
    if p.hostname != "127.0.0.1" and p.hostname != "localhost":
        raise ValueError("url must have host of 127.0.0.1 or localhost! Got: {}".format(p.hostname))
    if not modify_port:
        if p.port is not None:
            port_range = (int(p.port), int(p.port))
        else:
            port_range = (int(80), int(80))
    parent_port_pipe, child_port_pipe = Pipe()
    parent_pipe, child_pipe = Pipe()
    httpd_p = Process(target = _run_http_server, args = (child_port_pipe, child_pipe, port_range))
    httpd_p.start()
    if parent_port_pipe.poll(3000):
        final_port = parent_port_pipe.recv()
    else:
        raise Exception("Timeout waiting for HTTP server process to start")
    if final_port == 0:
        #Could not find a port
        raise Exception("Could not find open port")
    netloc = "{0}:{1}".format(p.hostname, final_port)
    if p.path:
        path = p.path
    else:
        path = '/'
    p = p._replace(netloc = netloc, path = path)
    return (urlunsplit(p), parent_pipe, httpd_p)

#TODO: Manual handler (when over SSH connection or something)

def ua_win_pyside_check():
    import sys
    if "PySide" in sys.modules:
        from PySide import QtGui
        return bool(QtGui.QApplication.instance())
    else:
        return False

def ua_win_pyside(url, pipe = None):
    from PySide import QtGui, QtCore
    #Start QApplication if it does not exist
    if not QtGui.QApplication.instance():
        QtGui.QApplication([])
    instructions = "Visit the following URL to authorize the application:"
    win = QtGui.QDialog()
    win.resize(250, 150)
    win.setWindowTitle("Authorization Required")
    instructions = QtGui.QLabel(instructions, win)
    #Textbox containing URL
    urlbox = QtGui.QLineEdit(win)
    urlbox.setText(str(url))
    urlbox.setReadOnly(True)
    #Open in Web Browser button
    def open_browser():
        from subprocess import Popen
        p = Popen(["sensible-browser", url])
    browserbutton = QtGui.QPushButton("Open in Web Browser", win)
    browserbutton.clicked.connect(open_browser)
    cancelbutton = QtGui.QPushButton("Cancel")
    cancelbutton.clicked.connect(win.reject)
    buttonbar = QtGui.QHBoxLayout()
    buttonbar.addStretch(1)
    buttonbar.addWidget(cancelbutton)
    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(instructions)
    vbox.addWidget(urlbox)
    vbox.addWidget(browserbutton)
    vbox.addLayout(buttonbar)
    win.setLayout(vbox)
    #Add timer
    if pipe:
        def poll():
            if pipe.poll():
                timer.stop()
                win.accept()
        timer = QtCore.QTimer(win)
        timer.timeout.connect(poll)
        timer.start(100)
    x = win.exec_()
    if x == QtGui.QDialog.Accepted:
        return True
    else:
        return False

def ua_win_tk_check():
    import sys
    if "tkinter" in sys.modules:
        from tkinter import Tk
        try:
            root = Tk()
            root.destroy()
            return True
        except:
            return False
    elif "IPython.zmq.iostream" in sys.modules:
        from IPython.zmq.iostream import OutStream
        return isinstance(sys.stdout, OutStream)
    else:
        return False

def ua_win_tk(url, pipe = None):
    from tkinter import Tk, Frame, Label, Entry, StringVar, BOTH, Button, RIGHT
    import sys
    sys.stdout.flush()
    instructions = "Visit the following URL to authorize the application:"
    response = {"x": False}
    root = Tk()
    root.title("oAuth2 Authorization Required")
    webbox = Frame(root)
    instructions = Label(webbox, text = instructions)
    instructions.pack(padx = 5, pady = 5)
    urlstr = StringVar(value = url)
    urlbox = Entry(webbox, textvariable = urlstr, state = "readonly")
    urlbox.pack(padx = 5, pady = 5)
    def open_browser():
        from subprocess import Popen
        p = Popen(["sensible-browser", url])
    browserbutton = Button(webbox, text = "Open in web browser", command = open_browser)
    browserbutton.pack(padx = 5, pady = 5)
    webbox.pack(fill = BOTH, expand = 1)
    if pipe:
        def poll():
            if pipe.poll():
                root.destroy()
                #Mutability ftw... wat
                response["x"] = True
            else:
                root.after(300, poll)
        root.after(300, poll)
    cancelbutton = Button(root, text = "Cancel", command = root.destroy)
    cancelbutton.pack(side = RIGHT, padx = 5, pady = 5)
    root.mainloop()
    return response["x"]

def ua_win_tty(url, pipe = None):
    from subprocess import Popen
    tty_out = open("/dev/tty", "w")
    tty_in = open("/dev/tty", "r")
    tty_out.write("pyoauth2client: Authorization Required. " \
            "Visit the following URL to authorize the application: \n" \
            "{0}\n\n".format(url))
    if pipe:
        tty_out.write("Press [Enter] to open your default web browser\n")
        x = tty_in.readline()
        #Open Web Browser
        p = Popen(["sensible-browser", url])
        #Wait for web browser to close
        p.wait()
        #Wait for pipe
        while not pipe.poll(300):
            pass
        return True
    else:
        tty_out.write("After authorizing the application, enter the URL " \
                "which your web browser was redirected to after " \
                "authentication:\nRedirected URL: ")
        x = tty_in.readline().strip()
        return x
        
    

def ua_handle_http(gen_user_req, redirect_uri, modify_port = True):
    import requests
    redirect_uri, pipe, p = run_http_server(redirect_uri, modify_port = modify_port)
    #Step 3: If all fails, fall back to tty
    #Step 4: If that fails, Fail noisily
    url, context = gen_user_req(redirect_uri)
    gui_handlers = [(ua_win_pyside, ua_win_pyside_check),
            (ua_win_tk, ua_win_tk_check)]
    #Step 1: Load handler based on what modules are already loaded
    result = None
    for x, y in gui_handlers:
        if y():
            result = x(url, pipe)
            break
    if result is None:
        result = ua_win_tty(url, pipe)
    if result:
        url = pipe.recv()
        p.join()
        pipe.close()
        return (url, context)
    else:
        #Send a request to redirect_uri to terminate application gracefully
        requests.get(redirect_uri)
        p.join()
        pipe.close()
        raise Exception("User cancelled")

def ua_handler(gen_user_req, redirect_uri, modify_port = True):
    return ua_handle_http(gen_user_req, redirect_uri, modify_port)
