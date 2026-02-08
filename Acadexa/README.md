# Acadexa

Acadexa is a web application that helps users curate educational resources based on their grade level, subjects, and preferred resource types. It searches various online sources to find relevant books, videos, articles, and libraries/PDFs, then compiles them into a downloadable PDF.

## Features

- **Customizable Searches**: Select grade level, subjects, and resource types (books, videos, articles, libraries/PDFs).
- **Multiple Sources**: Integrates with Open Library (books), YouTube (videos), Wikipedia (articles), GitHub (libraries for STEM subjects), and Ocean of PDF (PDFs for other subjects).
- **PDF Generation**: Automatically generates a PDF with curated resources for easy reference.
- **Relevance Filtering**: Filters results to ensure they match the selected subjects.

## Technologies Used

- **Backend**: Flask (Python web framework)
- **PDF Generation**: FPDF
- **APIs**: Requests for HTTP calls, YouTube Search Python for videos
- **Frontend**: HTML/CSS (simple form interface)
- **Deployment**: Ready for Render or similar platforms

## Installation

1. **Clone the repository**:
   ```
   git clone <your-repo-url>
   cd acadexa
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Run the app locally**:
   ```
   python main.py
   ```
   Visit `http://127.0.0.1:5000` in your browser.

## Usage

1. Open the app in your browser.
2. Select your grade level from the dropdown.
3. Choose one or more subjects (e.g., Math, Science).
4. Select resource types (books, videos, articles, libraries/PDFs).
5. Click "Curate Resources" to generate and download the PDF.

## Deployment

The app is configured for deployment on Render:

1. Push the code to a GitHub repository.
2. Sign up for Render and create a new Web Service.
3. Connect your GitHub repo, set build command to `pip install -r requirements.txt`, and start command to `python main.py`.
4. Deploy and get your live URL.

## Project Structure

- `main.py`: Main Flask application with search functions and routes.
- `templates/index.html`: HTML template for the form.
- `requirements.txt`: Python dependencies.
- `Procfile`: For deployment on Render.
- `README.md`: This file.

## Contributing

Feel free to fork the repo and submit pull requests for improvements.

## License

This project is open-source. Use it as you wish.
