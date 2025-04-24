# <img src="static/favicon.ico" alt="MealPlanWrapped icon" width="30" height="30"> UVA 2025 MealPlanWrapped

A Flask web application to analyze your university meal plan usage from a CSV export and generate a "wrapped" style summary.

## Features

*   Upload your meal plan transaction history CSV file.
*   View detailed statistics about your eating habits, including:
    *   Earliest and latest meal times.
    *   Most common day and dining hall location.
    *   Total spending and swipes used.
    *   Meal exchange usage patterns.
    *   Late-night meal counts.
    *   Time between meals.
    *   ...and more!
*   Generates a shareable summary image (like Spotify Wrapped).

## How to Use

1.  **Clone or download the repository.**
2.  **Install dependencies:**
    *   This project uses Flask, Pandas, Pillow, and Wonderwords. You might need to install them:
        ```bash
        pip install Flask pandas Pillow wonderwords
        ```
3.  **Run the application:**
    ```bash
    python MealPlanWrapped.py
    ```
4.  **Access the web interface:**
    *   Open your web browser and go to `http://localhost:8080` (or the address provided in the terminal).
5.  **Upload your CSV:**
    *   Follow the instructions on the web page to upload your meal plan transaction history CSV file.
    *   *(Note: Ensure your CSV file has the expected columns like 'Post Date', 'Location', 'Type', 'Amount', etc.)*
6.  **View your summary:**
    *   The application will process the data and display your personalized MealPlanWrapped summary.

## File Structure

*   `MealPlanWrapped.py`: The main Flask application script.
*   `templates/`: Contains HTML templates for the web pages (upload form, summary display).
*   `static/`: Holds static assets like CSS, JavaScript, and images (including the favicon).
*   `uploads/`: Default directory where uploaded CSV files are temporarily stored.
*   `*.csv`: Example or user-specific data files.
