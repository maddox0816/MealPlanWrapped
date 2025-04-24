import csv
import os
from collections import Counter
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import uuid
from wonderwords import RandomWord
#TODO
# ADD multiple themes for the summary image



# Ensure Flask serves static files from the 'static' folder
app = Flask(__name__, static_folder='static')

# Normalize column names to handle potential extra spaces or mismatches
def normalize_headers(headers):
    return [header.strip() for header in headers]

# Load data from CSV file
def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        reader.fieldnames = normalize_headers(reader.fieldnames)
        data = [row for row in reader]
    print(f"Loaded {len(data)} rows from the file.")
    return data

# Function to load data from uploaded CSV
def load_uploaded_data(file_path):
    return pd.read_csv(file_path)

# Analyze data to generate stats
def analyze_data(data):
    times = []
    days = []
    locations = []
    dollars_spent = 0
    swipes_used = 0
    meal_exchanges_used = 0
    grubhub_locations = []
    meal_exchange_days = set()
    late_night_meals = 0
    most_expensive_meal = 0
    chaotic_meal_times = Counter()
    dining_hall_counts = Counter()

    for row in data:
        print(f"Debug: Processing row: {row}")  # Debugging line
        # Parse date and time
        """
        try:
            post_date = datetime.strptime(row['Post Date'], '%m/%d/%Y %H:%M')
        except:
            post_date = datetime.strptime(row['ï»¿Post Date'], '%m/%d/%Y %H:%M')
            """
        post_date = datetime.strptime(row['Post Date'], '%m/%d/%Y %H:%M:%S')
        times.append(post_date)
        days.append(post_date.strftime('%A'))

        # Collect location
        locations.append(row['Location'])

        # Group dining halls
        if "FFC" in row['Location']:
            dining_hall_counts["Newcomb"] += 1
        elif "O-Hill" in row['Location']:
            dining_hall_counts["O-Hill"] += 1
        elif "Runk" in row['Location']:
            dining_hall_counts["Runk"] += 1

        # Track Grubhub locations for takeout stats
        if "Grubhub" in row['Location']:
            grubhub_locations.append(row['Location'])
            meal_exchange_days.add(post_date.date())
            #verify Type was Meal and add to meal exchanges used
            if row['Type'] == 'Meal':
                meal_exchanges_used += 1
                # Count swipes used for Grubhub meals


        # Calculate dollars spent and swipes used
        if row['Type'] == 'Debit' and "Laundry" not in row['Location'] and "Import" not in row['Location']:
            amount = abs(float(row['Amount'].replace('$', '').replace('(', '').replace(')', '')))
            dollars_spent += amount
            most_expensive_meal = max(most_expensive_meal, amount)
        elif row['Type'] == 'Meal':
            swipes_used += int(row['Amount'])

        # Count late-night meals (after 10 PM)
        if post_date.hour >= 22:
            late_night_meals += 1

        # Track chaotic meal times (e.g., meals eaten at odd hours)
        chaotic_meal_times[post_date.strftime('%H:%M')] += 1



    # Generate stats
    earliest_meal = min(times, key=lambda t: t.time()).strftime('%H:%M')  # Earliest time of day
    latest_meal = max(times, key=lambda t: t.time()).strftime('%H:%M')    # Latest time of day
    most_common_day = Counter(days).most_common(1)[0][0]
    most_common_location = dining_hall_counts.most_common(1)[0][0] if dining_hall_counts else "N/A"
    most_ordered_takeout = Counter(grubhub_locations).most_common(1)[0][0] if grubhub_locations else "N/A"
    total_meal_exchanges = meal_exchanges_used
    average_meal_exchanges_per_day = round(total_meal_exchanges / len(set([t.date() for t in times])), 2)

    # Filter times to exclude "Laundry," "Import," and duplicate meal entries
    filtered_times = [
        t for t, row in zip(times, data)
        if "Laundry" not in row['Location']
        and "Import" not in row['Location']
        and not (row['Type'] == 'Meal' and int(row['Amount']) < 0)  # Exclude negative meal entries
    ]

    # Remove exact duplicate timestamps
    filtered_times = sorted(set(filtered_times))

    # Sort filtered times to calculate time differences
    sorted_times = sorted(filtered_times)
    time_differences = [
        (sorted_times[i] - sorted_times[i - 1]).total_seconds() / 3600
        for i in range(1, len(sorted_times))
    ]
    longest_time_between_meals = max(time_differences) if time_differences else 0
    shortest_time_between_meals = min(time_differences) if time_differences else 0
    print("HHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    print(longest_time_between_meals)
    print(shortest_time_between_meals)
    print("--------------------------------------------------------------------------------------------------------------------------------")
    #make times more readable
    if shortest_time_between_meals < 0.01:
        shortest_time_between_meals = f"{round(shortest_time_between_meals * 60 * 60, 2)} Seconds"  # Convert to seconds
    elif shortest_time_between_meals < 1:
        shortest_time_between_meals = f"{round(shortest_time_between_meals * 60, 2)} Minutes"  # Convert to minutes
    else:
        shortest_time_between_meals = f"{round(shortest_time_between_meals, 2)} Hours"

    if longest_time_between_meals < 0.01:
        longest_time_between_meals = f"{round(longest_time_between_meals * 60 * 60, 2)} Seconds"  # Convert to seconds
    elif longest_time_between_meals < 1:
        longest_time_between_meals = f"{round(longest_time_between_meals * 60, 2)} Minutes"  # Convert to minutes
    else:
        longest_time_between_meals = f"{round(longest_time_between_meals, 2)} Hours"

    # Count meals used per day
    meals_per_day = Counter([t.date() for t in times])
    most_meals_in_a_day = max(meals_per_day.values()) if meals_per_day else 0

    meal_exchange_location_counts = Counter([loc.replace(" - Grubhub", "").replace("-Grubhub", "").replace(" - Kiosk","").replace("?","").replace("Kiosk","") for loc in grubhub_locations if loc])
    #sort by count of swipes used
    meal_exchange_location_counts = dict(sorted(meal_exchange_location_counts.items(), key=lambda item: item[1], reverse=True))  # Sort by values

    #sort dining hall counts by count of swipes used
    dining_hall_counts = dict(sorted(dining_hall_counts.items(), key=lambda item: item[1], reverse=True))  # Sort by values

    # Calculate average meal swipes by day of the week

    avg_meal_swipes_by_day = {}
    # Find sum of swipes for each xday starting with all Mondays, then all Tuesdays, etc. (Only include when type is 'Meal')
    # Initialize a dictionary to store total swipes for each day of the week
    swipes_by_day = {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
    
    # Group swipes by day of the week
    for row in data:
        if row['Type'] == 'Meal':
            try:
                post_date = datetime.strptime(row['ï»¿Post Date'], '%m/%d/%Y %H:%M:%S')
            except:
                post_date = datetime.strptime(row['Post Date'], '%m/%d/%Y %H:%M:%S')
            day_of_week = post_date.strftime('%A')
            swipes_by_day[day_of_week] += int(row['Amount'])
    
    # Calculate average swipes for each day of the week
    avg_meal_swipes_by_day = {day: round(swipes / len(set([t.date() for t in times if t.strftime('%A') == day])), 2)
                              for day, swipes in swipes_by_day.items() if swipes > 0}
    

    #Make the early and late meal times prettier
    # Convert to 12-hour format with AM/PM
    earliest_meal = datetime.strptime(earliest_meal, '%H:%M').strftime('%I:%M %p')
    latest_meal = datetime.strptime(latest_meal, '%H:%M').strftime('%I:%M %p')



    return {
        'earliest_meal': earliest_meal,
        'latest_meal': latest_meal,
        'most_common_day': most_common_day,
        'most_common_location': most_common_location,
        'most_ordered_takeout': most_ordered_takeout.replace(" - Grubhub", ""),
        'total_dollars_spent': round(dollars_spent, 2),
        'total_swipes_used': swipes_used,
        'total_meal_exchanges': total_meal_exchanges,
        'average_meal_exchanges_per_day': average_meal_exchanges_per_day,
        'late_night_meals': late_night_meals,
        'most_expensive_meal': round(most_expensive_meal, 2),
        'longest_time_between_meals': longest_time_between_meals,
        'shortest_time_between_meals': shortest_time_between_meals,
        'most_meals_in_a_day': most_meals_in_a_day,
        'dining_hall_counts': dining_hall_counts,
        'meal_exchange_location_counts': meal_exchange_location_counts,
        'avg_meals_by_day': avg_meal_swipes_by_day,
    }

# Function to calculate additional stats for the web app
def calculate_web_stats(data):
    # Example: Average swipes by day of the week
    data['Post Date'] = pd.to_datetime(data['Post Date'])
    data['Day of Week'] = data['Post Date'].dt.day_name()
    avg_swipes_by_day = data.groupby('Day of Week')['Amount'].mean().sort_index()
    return avg_swipes_by_day

# Display the wrapped summary
def display_summary(stats):
    print("Your Meal Plan Wrapped")
    print("-----------------------")
    print(f"Earliest Meal: {stats['earliest_meal']}")
    print(f"Latest Meal: {stats['latest_meal']}")
    print(f"Most Common Day: {stats['most_common_day']}")
    print(f"Most Common Dining Hall: {stats['most_common_location']}")
    print(f"Most Ordered Takeout Place: {stats['most_ordered_takeout']}")
    print(f"Total Dollars Spent: ${stats['total_dollars_spent']}")
    print(f"Total Swipes Used: {stats['total_swipes_used']}")
    print(f"Total Meal Exchanges: {stats['total_meal_exchanges']}")
    print(f"Average Meal Exchanges Per Day: {stats['average_meal_exchanges_per_day']}")
    print(f"Number of Late-Night Meals (after 10 PM): {stats['late_night_meals']}")
    print(f"Most Expensive Single Meal: ${stats['most_expensive_meal']}")
    print(f"Longest Time Between Meals: {stats['longest_time_between_meals']}")
    print(f"Shortest Time Between Meals: {stats['shortest_time_between_meals']}")
    print(f"Most Meals Used in a Single Day: {stats['most_meals_in_a_day']}")
    print("Dining Hall Visits:")
    for hall, count in stats['dining_hall_counts'].items():
        print(f"  {hall}: {count} visits")
    print("Takeout Locations:")
    for location, count in stats['meal_exchange_location_counts'].items():
        print(f"  {location}: {count} times")
    print("Average Meals by Day:")
    for day, avg in stats['avg_meals_by_day'].items():
        print(f"  {day}: {avg} swipes")

def save_file(file, filename):
    #This function takes the file and removes unwanted lines before saving it like everything below
    # Anything where Account is Cavalier Advantage or Wahoo Spins
    # Anything where the amount is a negative number be that negative meal swipes or $
    # Anything where the location is Import Loaction

    #example of the types of things to exclude
    """
    Post Date,Location,Account,Type,Amount
    08/21/2024 17:20:46,Import Loaction,All Access/$300,Meal,-50
    08/21/2024 17:20:46,Import Loaction,PCC-Dining Admin,Meal,-1
    08/21/2024 18:09:31,Import Loaction,Guest Meals,Meal,-10
    08/23/2024 11:08:30,Import Loaction,Flex $,Debit,$100.00"""

    # Read the file into a pandas DataFrame
    data = pd.read_csv(file)

    # Filter out unwanted rows
    data = data[~data['Account'].isin(['Cavalier Advantage', 'Wahoo Spins'])]  # Exclude specific accounts
    data = data[~data['Location'].str.contains('Import Loaction', na=False)]  # Exclude specific locations
    data = data[~data['Amount'].astype(str).str.startswith('-')]  # Exclude rows with negative meal swipe amounts
    data = data[~data['Amount'].astype(str).str.startswith('$-')]  # Exclude rows with negative dollar amounts


    # Save the cleaned data back to the file
    data.to_csv(filename, index=False)

    print(f"Debug: Saved cleaned data to '{filename}'.")
    return filename

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            try:
                rand = RandomWord()
                #file.filename = uuid.uuid4().hex + ".csv"  # Generate a unique filename
                file.filename = rand.word(word_min_length=3, word_max_length=6) +  rand.word(word_min_length=3, word_max_length=6) +  rand.word(word_min_length=3, word_max_length=6) + ".csv"  # Generate a unique filename
                print(f"Debug: Generated filename '{file.filename}'.")
                file_path = os.path.join('uploads', file.filename)
                print(f"Debug: Saving uploaded file to '{file_path}'.")
                # Save the uploaded file
                save_file(file, file_path)

                return redirect(url_for('view_file', uuid=file.filename.replace(".csv", "")))  # Redirect to view the file
            except Exception as e:
                print(f"Error: {e}")
                return render_template('error.html',  error = "Please make sure you copied everything and followed the instructions exactly. Then try again.")

    return render_template('upload.html')

@app.route('/favicon.ico')
def favicon():
    #return static/favicon.ico
    return app.send_static_file('favicon.ico')

@app.route('/view/<uuid>', methods=['GET'])
def view_file(uuid):
    file_path = os.path.join('uploads', uuid + ".csv")
    print(f"Debug: Viewing file at '{file_path}'.")
    if os.path.exists(file_path):
        try:
            data = load_data(file_path)
            
            #print out table
            #print(data.head())
            stats = analyze_data(data)
            display_summary(stats)
            return render_template('summary.html', stats=stats)
        except:
            return render_template('error.html', error="Error processing the data. Double check you followed the instructions and try again.")
    else:
        return redirect(url_for('upload_file'))

def generate_summary_image(stats, output_path="summary_image.png"):
    # Create an image with white background
    width, height = 1000, 800
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Load fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", size=40)
        font_subtitle = ImageFont.truetype("arial.ttf", size=30)
        font_body = ImageFont.truetype("arial.ttf", size=20)
        font_emoji = ImageFont.truetype("NotoColorEmoji-Regular.ttf", size=30)
    except IOError:
        font_title = font_subtitle = font_body = ImageFont.load_default()
        font_emoji = ImageFont.load_default()

    # Title
    title = "Your Meal Plan Wrapped"
    draw.text((width // 2 - draw.textlength(title, font=font_title) // 2, 30), title, fill="black", font=font_title)

    # Highlights with separate emoji area
    highlights = [
        ("Earliest Meal", stats['earliest_meal'], "🕒"),
        ("Latest Meal", stats['latest_meal'], "🌙"),
        ("Most Common Day", stats['most_common_day'], "📅"),
        ("Most Common Dining Hall", stats['most_common_location'], "🏛️"),
        ("Total Dollars Spent", f"${stats['total_dollars_spent']}", "💵"),
        ("Total Swipes Used", stats['total_swipes_used'], "🍽️"),
        ("Most Expensive Meal", f"${stats['most_expensive_meal']}", "💰"),
        ("Late-Night Meals", stats['late_night_meals'], "🌌"),
    ]

    # Draw blocks for highlights
    block_width, block_height = 400, 100
    x_start = (width - 2 * block_width - 20) // 2
    y_start = 100
    padding = 10

    for i, (label, value, icon) in enumerate(highlights):
        x = x_start + (i % 2) * (block_width + 20)
        y = y_start + (i // 2) * (block_height + 20)

        # Draw block background
        draw.rectangle([x, y, x + block_width, y + block_height], fill="#f0f0f0", outline="black", width=2)

        # Draw emoji in its own area
        draw.text((x + padding, y + padding), icon, fill="black", font=font_emoji)

        # Draw label and value
        draw.text((x + 60, y + padding), label, fill="black", font=font_body)
        draw.text((x + 60, y + padding + 30), str(value), fill="black", font=font_body)

    # Footer with link
    footer_text = "Try it yourself at mealplanwrapped.tech"
    draw.text((width // 2 - draw.textlength(footer_text, font=font_body) // 2, height - 50), footer_text, fill="blue", font=font_body)

    # Save the image
    image.save(output_path)
    print(f"Summary image saved to {output_path}")


# Main function
def main():
    file_path = 'MaddoxMeals.csv'
    print("Debug: Starting main function.")
    print(f"Debug: File path is '{file_path}'.")
    """
    data = load_data(file_path)
    
    if data:
        stats = analyze_data(data)
        generate_summary_image(stats, "summary_image.png")
        display_summary(stats)"""
    print("Debug: Main function completed.")

if __name__ == '__main__':
    main()
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(port=8080, debug=True, host="0.0.0.0")