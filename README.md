# Automata Command Center (DFA & NFA)

Project Tugas Akhir Teori Bahasa Automata (TBA).
Aplikasi ini merupakan simulasi interaktif berbasis web untuk berbagai operasi Automata, dirancang menggunakan **Python** dan **Streamlit**. Tampilannya dibuat *clean* dengan kombinasi warna Wine Red dan Hitam.

## Fitur Utama (5 Modul)
1. **DFA Simulator** - Mendefinisikan status dan transisi DFA, lalu melakukan pengetesan terhadap input string.
2. **Regex to NFA** - Konversi Regular Expression (termasuk *Kleene Star*, *Union*, *Concatenation*) menjadi NFA menggunakan metode Thompson Construction.
3. **NFA Simulator** - Mendefinisikan NFA secara manual, dilengkapi dukungan *epsilon transitions* (`ε`), untuk melakukan pengetesan string input (menggunakan Epsilon-Closure).
4. **DFA Minimizer** - Mengecilkan jumlah state (minimasi) pada sebuah DFA menggunakan metode *Table-Filling Algorithm (Myhill-Nerode)*.
5. **DFA Equivalence** - Memeriksa apakah dua DFA yang berbeda menghasilkan output dan bahasa (language) yang ekuivalen menggunakan *Product Construction*.

---

## Cara Menjalankan Program

### 1. Persiapan Lingkungan (Requirements)
Pastikan komputer kamu sudah terinstal **Python 3.8** atau versi yang lebih baru.

Buka Terminal / Command Prompt lalu jalankan perintah berikut untuk menginstal dependensi yang dibutuhkan:
```bash
pip install streamlit
```
*(Catatan: project ini murni menggunakan modul bawaan Python untuk logic-nya, sehingga Streamlit adalah satu-satunya library eksternal yang diwajibkan untuk menjalankan User Interface).*

### 2. Menjalankan Aplikasi
Arahkan Terminal kamu ke dalam folder proyek ini (dimana file `app.py` berada), lalu eksekusi perintah:
```bash
streamlit run app.py
```

### 3. Mengakses Aplikasi
Setelah perintah dijalankan, server lokal akan aktif. Buka browser kamu dan akses alamat yang tertera di terminal, biasanya berada di:
```text
http://localhost:8501
```

---

## Struktur Proyek
- `app.py` : File utama antarmuka pengguna (UI) berbasis Streamlit.
- `models/` : Berisi struktur kelas data untuk representasi objek `DFA` dan `NFA`.
- `moduls/` : Inti logika algoritma automata (simulator, minimizer, equivalensi, dan konversi regex).