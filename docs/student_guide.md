---

# 🧼 Beginner’s Guide: How to Add a Data Cleaner

Welcome! 👋
This guide will help you write a **data cleaner** that fits into our machine learning project. Don’t worry if you’re new — we’ll walk through it step by step. For this process, the `Data Sources` tab of the `project-tracking` file for your project will be very useful. Please consult this document while cleaning your data to understand necessary specifications for the cleanded data and to track cleaning progress.

---

## 🤔 What’s a Data Cleaner?

A **data cleaner** is just some Python code that:

1. **Downloads** some raw data
2. **Cleans it up** (like fixing missing values, typos, incorrect data types, and selecting columns of interest)
3. **Returns fully cleaned data** (fully cleaned data of the format specified in the `project-tracking` file)

Our system takes care of saving the results and running your code — you just need to follow a few rules.

---

## 🧪 How It Works

* You write a Python file called `data_cleaner.py` (replace `data_cleaner` with the `Cleaner File` name specified in the `project-tracking` file)
* Inside it, you create a class called `Cleaner`
* You fill in a few functions with your download + cleaning steps
* We run your code with a simple command — no extra setup needed!

---

## 🏁 Before You Start

Before you write any code, take a bit of time to **understand your dataset**. This step is crucial — better models come from better data, and better data starts with you!

Here’s what to do:

1. **Check which dataset you're working on**  
   Your team lead will assign you a dataset. You can also look in the `project-tracking` file to see what project and data you're responsible for.

2. **Explore the dataset in a notebook**  
   Open a Jupyter notebook and load the data (you can use `pandas.read_csv()` or whatever format it's in). Then:

   - Look at a few rows with `.head()`  
   - Check the column names and data types with `.info()`  
   - Use `.describe()` to get a feel for the numbers  
   - Plot the key variables using `matplotlib` or `seaborn`  
   - Check for **missing data** with `.isna().sum()`  
   - Look for **weird values** or **outliers** that don’t make sense

   This step is *extremely* important! Don’t treat the data like a black box — the more you understand it, the better your cleaner will be.

   You will become your project's resident expert on this dataset, so make sure you understand what all the columns mean and how they relate to each other and the target variable.

   You’ll also start to spot what needs fixing:  
   Maybe there are typos, or missing values, or strange formats (like `"N/A"` instead of real nulls). Write these things down — they’ll guide your cleaning code.

4. **Test cleaning functions**
   You can use this notebook (or your preferred IDE) to test functions you will eventually need to write for the cleaner. Figure out how to download (or load) the data, perform thre necessary cleaning steps, and return the cleaned data in the format specified in the project-tracking file.
   
---

Here's your updated **README** section with **clear Git instructions** for both the **terminal** and **GitHub Desktop** workflows. It's written in markdown format, easy to copy:

---

## 🚀 How to Start

Follow these steps to add your cleaner to the project.

### 🧰 Step 1: Clone the GitHub Repo

You can do this using **Terminal** (for more control) or **GitHub Desktop** (easier UI).

---

#### ➡️ Option A: Using GitHub Desktop (Beginner-Friendly)

1. Install GitHub Desktop: [https://desktop.github.com](https://desktop.github.com)

2. Open GitHub Desktop and **clone the repository**:

   * Click `File` → `Clone Repository`
   * Find the repo under the `URL` or `GitHub.com` tab
   * Choose a local folder (e.g., `Documents/cleaning-pipeline`)

3. Once it’s cloned, click `Open in VS Code` or navigate to the folder manually.

---

#### ➡️ Option B: Using the Terminal (More Advanced)

1. Open your terminal or command prompt
2. Run the following to clone the repo:

   ```bash
   git clone [https://github.com/your-org/data-cleaning-pipeline.git](https://github.com/your-org/data-cleaning-pipeline.git)
   cd data-cleaning-pipeline
   ```

---

### 🏗 Step 2: Add Your Cleaner

1. Inside the project folder, go to the `cleaners/` directory

2. Inside that folder, create the cleaning file. It should be saved as:

   ```bash
   cleaners/data_cleaner.py
   ```

   Replacing `data_cleaner.py` with the `Cleaner File` name from the `project-tracking` document.

3. Paste the following example inside your new file and update it with your own data logic (see "What You Have to Write" section for details):

   ``` python
   from core.base_cleaner import DataCleaner
   import pandas as pd
   from typing import Dict, Any

   class Cleaner(DataCleaner):
   """This cleaner downloads and cleans my dataset."""

   def download_to_df(self) -> pd.DataFrame:  
       return pd.read_csv("https://example.com/mydata.csv")  

   def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:  
       df = df.dropna()  
       return df  

   def get_metadata(self) -> Dict[str, Any]:  
       return {  
           'source_name': 'My Source',  
           'variables': {
           'col1': 'Description',
           'col2': 'Description
           },  
           'temporal_resolution': 'Daily',  
           'spatial_resolution': 'City'  
       }
   ```

---

Here’s an improved version of **Step 3** with clearer folder navigation instructions:

---

### 🧪 Step 3: Test Your Cleaner

1. **Open a terminal window**.

2. **Navigate to the root folder** of the project — the one that contains `data_cleaning.py`.
   If you used GitHub Desktop, right-click the folder and choose “Open in Terminal” or “Open in Command Prompt”.
   If you're using the terminal, use the `cd` (change directory) command to go there. For example:

   ```bash
   cd ~/Documents/data-cleaning-pipeline
   ```

   Adjust the path depending on where you cloned the repo.

3. Once you're in the root folder, run the cleaner test command:

   ```bash
   python data-cleaning/data_cleaning.py --cleaner my_cleaner --test
   ```

   Replacing `data_cleaner.py` with the `Cleaner File` name from the `project-tracking` document.

If everything is working, you'll see logs confirming that your data was **downloaded, cleaned**, and saved.

---

### ✅ Step 4: Commit and Push Your Changes

#### ➡️ Option A: Using GitHub Desktop

1. GitHub Desktop will automatically show your changes
2. Write a summary in the `Commit message` box (e.g., “Add my_cleaner for XYZ data”)
3. Click `Commit to main` (or your current branch)
4. Click `Push origin` in the top bar to upload your changes

#### ➡️ Option B: Using Terminal

1. Stage your changes:
   
   ```bash
   git add cleaners/my_cleaner/
   ```

2. Commit with a message:

   ```bash
   git commit -m "Add my\_cleaner for XYZ data"
   ```

3. Push to GitHub:
   
   ```bash
   git push origin main
   ```
   *(or replace `main` with your current branch if you're not on main)*

---

You're done! 🎉
Once your cleaner is added and pushed, it will be automatically picked up by the pipeline and tested.

Let us know if you need help — we're here to support you!

---

## 🧱 What You Have to Write

Your `Cleaner` class needs to have 3 functions:

---

### 1. `download_to_df()`

Machine learning pipelines often require dynamic data to be periodically downloaded from the source. If your dataset is dynamic (check your project's `project-tracking` file under `Update Frequency`), then you need to write code to download the data from the source. This might require just using a link to directly download the CSV, working with an API, or even webscraping.  

The `download_to_df()` function will be used to download your raw data from the source. It must return a **pandas DataFrame**.

If your dataset is static (check your project's `project-tracking` file under `Update Frequency`), then you simply need to load the data from its repo path.

Example:

```python
def download_to_df(self):
    return pd.read_csv("https://example.com/data.csv")
```

---

### 2. `clean_from_df(df)`

This function takes in that raw DataFrame and cleans it. Think carefully about what cleaning needs to be done and which variables need to be selected. Ensure that the specified `Join Key` columns from the `project-tracking` file are present. This ensures your data can be linked with the other data in the pipeline.

Example:

```python
def clean_from_df(self, df):
    df = df.dropna()  # Remove empty rows
    df.columns = [col.lower() for col in df.columns]  # Make column names lowercase
    return df
```

---

### 3. `get_metadata()`

This just returns some info about your data.

Example:

```python
def get_metadata(self):
    return {
        'source_name': 'World Bank',
        'variables': {
        'population': 'Number of people in the country',
        'gdp': 'Gross Domestic Product, in 2005 dollars',
        'year': 'Year',
        'country': 'Country'
        },
        'temporal_resolution': 'yearly',
        'spatial_resolution': 'country'
    }
```

---

## 💾 Where Your Files Go

* Raw downloads go in: `data/raw/`
* Temporary stuff goes in: `data/temp/`
* Cleaned data is **automatically saved** in:
  `data/cleaned/my_data_cleaned.csv`

⚠️ You don’t need to save files yourself — just return the DataFrame!

---

## 📦 Using Extra Packages?

If you use libraries like `requests`, `geopandas`, or `beautifulsoup`, create a file like this:

**`requirements.txt`**

```
requests>=2.28.0
pandas>=1.5.0
```

We’ll install them automatically when we run your cleaner.

---

## 🧪 How Testing Works

When we run your cleaner, the system checks:

* Is your data empty?
* Are all the columns missing?
* Are the data types consistent?
* Is memory usage too high?

---

## ✅ Quick Checklist

✅ You made a folder in `cleaners/`

✅ You created a `data_cleaner.py` (replace the file name with the `Cleaner File` name from the `project-tracking` document)

✅ You made a `Cleaner` class

✅ You filled in `download_to_df()`, `clean_from_df()`, and `get_metadata()`

✅ You tested it with the command

✅ You’re done 🎉

---

## 💬 Still Confused?

Here’s what you can do:

* Look at other folders in `cleaners/` to see examples
* Read `core/base_cleaner.py` to understand how it works
* Ask for help on the discussion board or chat

---

That’s it! You’ve got this. Just follow the steps, and your cleaner will work in the pipeline automatically. 🚀✨
