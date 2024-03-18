import os
import sys
import requests
from datetime import datetime, timedelta

def get_comic_url(date, format="gif"):
    year = date.strftime("%Y") if date.year >= 2000 else "19" + date.strftime("%y")
    month = date.strftime("%m")
    day = date.strftime("%d")

    if date.year >= 2000:
        formatted_date = f"{date.strftime("%y")}{month}{day}"
    else:
        formatted_date = f"{date.strftime("%y")}{month.lstrip('2')}{day.lstrip('4')}"
        if len(month) == 1:
            formatted_date = f"0{month}{day}"
        elif len(day) == 1:
            formatted_date = f"{month}0{day.lstrip('0')}"

    base_url = f"https://picayune.uclick.com/comics/ga/{year}/"
    return base_url + f"ga{formatted_date}.{format}"

def download_comic(url, save_path):
    response = requests.get(url, stream=True)

    if response.status_code == 404:
        raise requests.exceptions.HTTPError("File not found")

    with open(save_path, "wb") as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)

def main():
    start_date_input = input("Enter the start date (YYYY-MM-DD): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD): ")

    try:
        start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        sys.exit(1)

    if end_date < start_date:
        print("End date must be equal to or later than the start date.")
        sys.exit(1)

    output_folder = "garfield_comics"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    current_date = start_date

    while current_date <= end_date:
        file_name_base = get_comic_url(current_date, format='').split('/')[-1].split('.')[0]

        comic_url_gif = get_comic_url(current_date)
        comic_url_jpg = get_comic_url(current_date, "jpg")

        save_path_gif = os.path.join(output_folder, f"{file_name_base}.gif")
        save_path_jpg = os.path.join(output_folder, f"{file_name_base}.jpg")

        found_comic = False
        for comic_url, save_path in [(comic_url_gif, save_path_gif), (comic_url_jpg, save_path_jpg)]:
            print(f"Downloading {comic_url}")
            try:
                download_comic(comic_url, save_path)
                print(f"Successfully downloaded {os.path.basename(save_path)}")
                found_comic = True
                break
            except requests.exceptions.HTTPError as e:
                if "File not found" in str(e):
                    continue
                elif e.response.status_code == 404:
                    continue
                else:
                    print(f"Failed to download {os.path.basename(save_path)}: {e}")
                    break
        if not found_comic:
            print(f"No comic found for {current_date.strftime('%Y-%m-%d')}")

        current_date += timedelta(days=1)

if __name__ == "__main__":
    main()
