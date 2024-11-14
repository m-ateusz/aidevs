from aidevs import send_task

def main():
    # Answer dictionary with categorized files
    answer = {
        "people": [
            "2024-11-12_report-00-sektor_C4.txt",
            "2024-11-12_report-07-sektor_C4.txt", 
            "2024-11-12_report-10-sektor-C1.mp3"
        ],
        "hardware": [
            "2024-11-12_report-13.png",
            "2024-11-12_report-15.png",
            "2024-11-12_report-17.png"
        ]
    }

    # Send the answer to the task endpoint
    send_task("kategorie", answer)

if __name__ == "__main__":
    main() 