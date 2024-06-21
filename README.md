# CatBot

## Project Overview 

This project involves the creation of a Telegram bot  for analyzing Japanese media, which assists users by providing information based on a pre-trained model and additional contextual data stored in JSON files. The bot interacts with users, processes their requests, and provides responses based on the specified year. The project includes data cleaning and preparation of JSON files, integration with Yandex GPT and Yandex Translate API, fine-tuning Yandex GPT, developing algorithms for higher quality translation, and managing interactions through the Telegram bot.

### Project Structure

```
.
├── config.json
├── app.py
├── requirements.txt
├── data
│   ├── cleaning_data.py
│   └── train2019.json
```

### Data Preparation

We received data in the form of WARC files. These were raw HTML news texts, not cleaned of advertisements, frequently recurring links, announcements, and other texts surrounding the actual news content. The dataset contained duplicates of the same news on different sites, possibly in slightly altered form.

We cleaned the dataset using the following methods:

### Main Data Processing Steps:

1. **HTML Content Cleaning and Link Extraction:**
   - We extracted files using the **warcio** library. Then we used the **BeautifulSoup** library for parsing and cleaning HTML content. We removed scripts, styles, comments, ad blocks, and other unnecessary elements to extract only useful textual information.
   - We also extracted all links found in the HTML content. This allowed us to preserve the context and sources of information.

2. **Text Normalization:**
   - We used the **unicodedata** library for text normalization. Using the `unicodedata.normalize` function, we unified the dataset to simplify further processing.

3. **Removing Repeating Links and Extra Spaces:**
   - We removed repeating links and extra spaces to make the text more readable and compact. This also helped to avoid information duplication during further analysis. We also used the **re** library for working with regular expressions.

4. **Removing Image Links:**
   - We removed links to images, as they do not provide useful textual information for our analysis.

You can view the dataset processing code in
```sh
data/cleaning_data.py
```
Part of the dataset used for training Yandex GPT is available in
```sh
data/train2019.json
```

The complete cleaned dataset in .JSON format can be found on Yandex Disk at https://disk.yandex.ru/d/JIXB7DPbTNygqg

### Technical Implementation

1. **Telegram Bot Initialization:**
   - We used the `python-telegram-bot` library for creating, configuring, and connecting the bot.

2. **User Request Processing:**
   - We added the ability for users to select the year of the data through buttons provided by the bot:
     ```sh
     up to 2019
     up to the end of 2019
     up to the end of 2022
     up to the end of 2023
     ```
   - Then, user requests are translated into Japanese using the Yandex Translate API.
   - The translated request and context from the corresponding JSON files are sent to the fine-tuned Yandex GPT for a response.

3. **Searching for Answers in JSON Files:**
   - JSON files are stored in folders corresponding to the years of the data.
   - Depending on the year selected by the user, answers are searched in the corresponding folders.

4. **Translating and Formatting Answers:**
   - The obtained answers are translated back into Russian using Yandex Translate. Special algorithms ensure that Japanese proper names are preserved in their original form.
   - We also added response formatting with links to additional materials.

5. **Sending the Response to the User:**
   - The formatted response is sent to the user through the Telegram bot.

### Installation and Running the Project

1. Clone the project repository:

   ```sh
   git clone https://github.com/Enc0der/CAIts.git
   cd project
   ```

2. Create and activate a virtual environment:

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Configure the `config.json` file with your API keys and other necessary parameters.

5. Start the bot:

   ```sh
   python app.py
   ```
### Installation with Docker

Run:

   ```sh
git clone https://github.com/Enc0der/CAIts.git
cd CAIts

docker build -t catbot .
docker run -d --name catbot catbot
  ```
Now your Telegram bot is ready for use. You can interact with it through Telegram by sending requests and receiving information based on data from JSON files.

   ```sh
Enjoy using the bot!
   ```
