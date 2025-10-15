# Videoflix Backend

![Logo](/media/logoheader.png)

**Videoflix** is a video streaming platform inspired by Netflix. Users can register, activate their account via email, reset forgotten passwords, and stream videos in multiple resolutions with custom playback speeds in the integrated player.

This repository contains the backend of the application, built with **Django**, **Django REST Framework**, **JWT Authentication**, and **ffmpeg** for video encoding.

👉 Frontend repository: [Videoflix Frontend](https://github.com/HPetersen2/Videoflix-Frontend.git)

---

## 🚀 Features

- User registration and login  
- Email-based account activation  
- Password reset via email with secure token  
- Video streaming with selectable playback speeds  
- Video transcoding to multiple resolutions  
- RESTful API for integration  
- Docker-based development setup  

---

## 🧰 Requirements

- **Python** 3.13.3 or newer  
- **Docker** and **Docker Compose**  
  → [Install Docker](https://docs.docker.com/get-docker/)  
- **ffmpeg** (required for video transcoding)

### 🔧 Installing `ffmpeg`

> `ffmpeg` is required inside the container, but may also be useful locally for testing.

#### macOS

```bash
brew install ffmpeg
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows

1. Download from: https://ffmpeg.org/download.html  
2. Extract and add the `bin/` directory to your system PATH

---

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/HPetersen2/Videoflix-Backend.git
cd Videoflix-Backend
```

### 2. (Optional) Set up a virtual environment

```bash
python -m venv env
```

#### Activate the environment:

- **macOS/Linux**:
  ```bash
  source env/bin/activate
  ```

- **Windows (CMD)**:
  ```cmd
  env\Scripts\activate
  ```

- **Windows (PowerShell)**:
  ```powershell
  .\env\Scripts\Activate.ps1
  ```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy the template `.env` file:

- **Linux/macOS**:
  ```bash
  cp env.template .env
  ```

- **Windows (CMD)**:
  ```cmd
  copy env.template .env
  ```

- **Windows (PowerShell)**:
  ```powershell
  Copy-Item env.template .env
  ```

Edit the `.env` file and set the necessary variables.

---

### 5. Start the application

Build and run the container (first time):

```bash
docker-compose up --build
```

To start the container next time:

```bash
docker-compose up
```

The backend will be available at:  
[http://127.0.0.1:8000/](http://127.0.0.1:8000/) or  
[http://localhost:8000/](http://localhost:8000/)

---

## 🔌 API Endpoints

### 🔐 Authentication

| Method | Endpoint                                         | Description                     |
|--------|--------------------------------------------------|---------------------------------|
| POST   | `/api/register/`                                 | User registration               |
| GET    | `/api/activate/<uidb64>/<token>/`                | Email account activation        |
| POST   | `/api/login/`                                    | Login                           |
| POST   | `/api/logout/`                                   | Logout                          |
| POST   | `/api/token/refresh/`                            | Refresh JWT token               |
| POST   | `/api/password_reset/`                           | Request password reset          |
| POST   | `/api/password_confirm/<uidb64>/<token>/`        | Reset password via email token  |

---

### 🎬 Video

| Method | Endpoint                                                                 | Description                         |
|--------|--------------------------------------------------------------------------|-------------------------------------|
| GET    | `/api/video/`                                                            | Get list of videos                  |
| GET    | `/api/video/<int:movie_id>/<str:resolution>/index.m3u8`                 | Get streaming playlist (HLS)       |
| GET    | `/api/video/<int:movie_id>/<str:resolution>/<str:segment>/`            | Fetch video segment                 |

---

## 🛠️ Built With

- **Python 3.13.3**  
- **Django**  
- **Django REST Framework**  
- **JWT (JSON Web Token)**  
- **Docker**  
- **PostgreSQL**  
- **ffmpeg** – for video encoding/transcoding  
- **django-rq** – background task management  
- **Redis** – job queue backend  
- **Whitenoise** – static file serving  
- **pytest** & **coverage.py** – testing and code coverage  

---

## 👨‍💻 Credits

- **Backend**: Developed by Henrik Petersen  
- **Frontend**: Provided by Developer Akademie

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.
