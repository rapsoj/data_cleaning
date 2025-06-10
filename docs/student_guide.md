---

# 🧼 Beginner’s Guide: How to Add a Data Cleaner

Welcome! 👋
This guide will help you write a **data cleaner** that fits into our machine learning project. Don’t worry if you’re new — we’ll walk through it step by step.

---

## 🤔 What’s a Data Cleaner?

A **data cleaner** is just some Python code that:

1. **Downloads** some raw data
2. **Cleans it up** (like fixing missing values or typos)
3. **Returns a clean DataFrame** (a nice, organized table)

Our system takes care of saving the results and running your code — you just need to follow a few rules.

---

## 🧪 How It Works

* You write a Python file called `data_cleaner.py`
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

   You’ll also start to spot what needs fixing:  
   Maybe there are typos, or missing values, or strange formats (like `"N/A"` instead of real nulls). Write these things down — they’ll guide your cleaning code.
   
---

## 🚀 How to Start

### ✅ Option 1: Add Your Code to *This* Project

1. **Open a terminal** (or command line).

2. **Make a folder** for your cleaner:

   ```bash
   mkdir cleaners/my_cleaner
   ```

3. **Create this Python file** in that folder (called `data_cleaner.py`):

   ```python
   from core.base_cleaner import DataCleaner
   import pandas as pd
   from typing import Dict, Any

   class Cleaner(DataCleaner):
       """This cleaner downloads and cleans my cool dataset."""

       def download_to_df(self) -> pd.DataFrame:
           # Download your data here
           return pd.read_csv("https://example.com/mydata.csv")

       def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
           # Clean the data
           df = df.dropna()
           return df

       def get_metadata(self) -> Dict[str, Any]:
           return {
               'source_name': 'My Source',
               'variables': ['col1', 'col2'],
               'temporal_resolution': 'daily',
               'spatial_resolution': 'city'
           }
   ```

4. **Test your cleaner**:

   ```bash
   python data_cleaning.py --cleaner my_cleaner --test
   ```

---

### ✅ Option 2: Use Your Own GitHub Repo

If you don’t want to add to this project, you can make your own mini-project.

1. Make a folder (or repo) that looks like this:

   ```
   my_repo/
   ├── data_cleaner.py      ✅ Must be named exactly this
   └── requirements.txt     🧪 Optional (extra packages like pandas, requests)
   ```

2. Write a `Cleaner` class in `data_cleaner.py` (same as above)

3. Share the link to your repo with us. We’ll run:

   ```bash
   git clone https://github.com/you/my_repo.git external_cleaners/my_cleaner
   python data_cleaning.py --cleaner my_cleaner
   ```

---

## 🧱 What You Have to Write

Your `Cleaner` class needs to have 3 functions:

---

### 1. `download_to_df()`

Machine learning pipelines often require dynamic data to be periodically downloaded from the source. If your dataset is dynamic (check your project's project-tracking file under `Update Frequency`), then you need to write code to download the data from the source. This might require just using a link to directly download the CSV, working with an API, or even webscraping.  

The `download_to_df()` function will be used to download your raw data from the source. It must return a **pandas DataFrame**.

If your dataset is static (check your project's project-tracking file under `Update Frequency`), then you simply need to load the data from its repo path.

Example:

```python
def download_to_df(self):
    return pd.read_csv("https://example.com/data.csv")
```

---

### 2. `clean_from_df(df)`

This function takes in that raw DataFrame and cleans it.

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
        'variables': ['population', 'gdp'],
        'temporal_resolution': 'yearly',
        'spatial_resolution': 'country'
    }
```

---

## 💾 Where Your Files Go

* Raw downloads go in: `data/raw/`
* Temporary stuff goes in: `data/temp/`
* Cleaned data is **automatically saved** in:
  `data/cleaned/my_cleaner_cleaned.csv`

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

To test it yourself:

```bash
python data_cleaning.py --cleaner my_cleaner --test
```

---

## ✅ Quick Checklist

✅ You made a folder in `cleaners/`
✅ You created a `data_cleaner.py`
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
