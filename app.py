from flask import Flask, render_template, request

app = Flask(__name__,
    template_folder='src/templates',    # src/templates 폴더 지정
    static_folder='src/static'          # src/static 폴더 지정
)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
