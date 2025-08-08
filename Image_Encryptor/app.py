from flask import Flask, render_template, request, send_file, redirect, url_for
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


KEY = b'ThisIsASecretKey1234567890123456'  # 32 bytes ✅


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        with open(path, 'rb') as f:
            data = f.read()

        cipher = AES.new(KEY, AES.MODE_CBC)
        ciphertext = cipher.encrypt(pad(data, AES.block_size))
        encrypted_path = path + '.enc'

        with open(encrypted_path, 'wb') as f:
            f.write(cipher.iv + ciphertext)

        return send_file(encrypted_path, as_attachment=True)

    return redirect(url_for('index'))

@app.route('/decrypt', methods=['POST'])
def decrypt():
    file = request.files['file']
    if file and file.filename.endswith('.enc'):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        with open(path, 'rb') as f:
            iv = f.read(16)
            ciphertext = f.read()

        cipher = AES.new(KEY, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

        original_name = filename.replace('.enc', '_decrypted.jpg')  # assumes jpg
        decrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], original_name)

        with open(decrypted_path, 'wb') as f:
            f.write(plaintext)

        return send_file(decrypted_path, as_attachment=True)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
