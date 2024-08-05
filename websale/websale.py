from flask import Flask, render_template, request, redirect, session
import hashlib
import datetime
import random
import string
import telebot

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Token bot Telegram Anda
telegram_bot_token = "6595110317:AAGn3OREUReg_BjItf5phDI5Q-bGR2nxxC0"

# Inisialisasi bot Telegram
bot = telebot.TeleBot(telegram_bot_token)

# ID obrolan Telegram Anda
telegram_chat_id = "144269744"

# Fungsi untuk mengirim pesan ke Telegram
def send_message_to_telegram(chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        print(f"Failed to send message to Telegram: {e}")
        return False

# Fungsi untuk menghasilkan kata sandi baru
def generate_new_password():
    global expiration_time

    characters = string.ascii_letters + string.digits
    new_password = ''.join(random.choice(characters) for _ in range(10))
    print("Password baru:", new_password)
    with open("password_log.txt", "a") as file:
        file.write(new_password + "\n")
    send_message_to_telegram(telegram_chat_id, f"New password: {new_password}")
    
    # Perbarui waktu ekspirasi setiap kali password baru dihasilkan
    expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=2)

    return new_password


# Memanggil fungsi untuk menghasilkan password baru
password = generate_new_password()
expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=2)

# Polling untuk menerima pesan dari Telegram
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Anda dapat menambahkan logika di sini untuk menangani pesan yang diterima
    print(f"Received message: {message.text}")


# Lanjutan kode Flask Anda...


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    # Ganti nomor telepon sesuai dengan nomor tujuan Anda
    whatsapp_number = '+6282211124715'
    return redirect(f'https://wa.me/{whatsapp_number}')

@app.route('/send_proof', methods=['POST'])
def send_proof():
    # Proses pengiriman bukti pembayaran via WhatsApp
    # Di sini Anda dapat menambahkan logika untuk mengirim bukti pembayaran
    return "Proof sent successfully!"

@app.route('/checkout/<int:price>', methods=['POST', 'GET'])
def checkout(price):
    if request.method == 'POST':
        # Proses pembayaran di sini
        return render_template('payment_processing.html')
    else:
        return render_template('index.html')  # Kembali ke halaman index jika bukan POST request
    
# Kata sandi yang diizinkan untuk mengakses halaman
allowed_password = "password123"
# Kata sandi yang digenerate untuk tautan download
download_password = generate_new_password()


@app.route('/download_link', methods=['POST', 'GET'])
def download_link():
    global download_password, expiration_time

    if datetime.datetime.now() > expiration_time:
        # Jika waktu kedaluwarsa sudah berlalu, kirimkan pesan Telegram
        message = "Password for download link has expired. Please generate a new password."
        if send_message_to_telegram(telegram_chat_id, message):
            # Perbarui kata sandi dan waktu kedaluwarsa jika pesan berhasil terkirim
            download_password = generate_new_password()
            expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=2)  # Kedaluwarsa setiap 2 menit

    if request.method == 'POST':
        user_password = request.form.get('password', '')

        if user_password == download_password:
            # Jika kata sandi cocok, beri akses ke tautan download
            return render_template('download_link.html', access=True)
        else:
            # Jika kata sandi tidak cocok, kembalikan ke halaman download dengan pesan error
            return render_template('download_link.html', access=False)
    else:
        return render_template('download_link.html', access=None)  # Menampilkan form jika bukan POST request
    
@app.route('/')
def home():
    if 'logged_in' in session:
        return render_template('index.html')
    else:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if hashlib.sha256(password.encode()).hexdigest() == hashlib.sha256(allowed_password.encode()).hexdigest():
            session['logged_in'] = True
            return redirect('/')
        else:
            return render_template('login.html', error=True)
    else:
        return render_template('login.html', error=False)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')    

if __name__ == '__main__':
    app.run(debug=True)
