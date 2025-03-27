# **LinkLab Publication Project**

A web-based application to manage and display academic publications dynamically. This project includes a periodic scheduler, a BibTeX generator, a Node.js Express server for serving the frontend, and configurations for managing authors and publications.

---

## **Table of Contents**

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Usage](#usage)
   - [Run the Express Server](#run-the-express-server)
   - [Run the BibTeX Generator](#run-the-bibtex-generator)
   - [Run the Scheduler](#run-the-scheduler)
5. [Configuration](#configuration)
6. [Output Files](#output-files)
7. [Contributing](#contributing)
8. [License](#license)

---

## **Features**

- Generate BibTeX files from ORCID API using `generate_bibtex.py`.
- Periodic automation of the BibTeX generation with `scheduler.py`.
- Serve a web interface using a Node.js Express server.
- Manage authors dynamically via `authors.json`.
- Output publication files in BibTeX (`Publications.bib`), JSON, and logs.

---

## **Project Structure**

```plaintext
LINKLABPUBLICATION/
├── src/
│   ├── config/
│   │   └── authors.json        # Config file for authors
│   ├── scripts/
│   │   ├── generate_bibtex.py  # Script to generate BibTeX
│   │   └── scheduler.py        # Scheduler for periodic BibTeX generation
│   ├── static/
│   │   ├── bib/
│   │   │   └── Publications.bib         # BibTeX source file
│   │   ├── css/
│   │   │   └── styles.css      # Frontend CSS
│   │   ├── js/
│   │   │   └── index.js        # Frontend JavaScript
│   ├── templates/
│   │   └── index.html          # Main HTML template
├── server.js                   # Node.js Express server
├── requirements.txt            # Python dependencies
├── package.json                # Node.js dependencies
├── .gitignore                  # Ignored files for version control
└── README.md                   # Project documentation
```

---

## **Installation**

### **1. Clone the Repository**
Clone this repository to your local machine:
```bash
git clone https://github.com/uva-linklab/linklabpublication.git
cd linklabpublication
```

### **2. Install Python Dependencies**
Ensure you have Python 3.9+ installed. Then, install the required Python libraries:
```bash
pip install -r requirements.txt
```

### **3. Install Node.js Dependencies**
Ensure Node.js 14+ is installed. Then, install the required Node.js libraries:
```bash
npm install
```

---

## **Usage**

### **1. Run the Express Server**
Start the Node.js server to serve the web application:
```bash
node server.js
```
The application will be available at:
```
http://localhost:3000
```

### **2. Run the BibTeX Generator**
Manually generate BibTeX files and publication data:
```bash
python3 src/scripts/generate_bibtex.py
```

### **3. Run the Scheduler**
Automate BibTeX generation every two weeks:
```bash
python3 src/scripts/scheduler.py
```
This script ensures the BibTeX generation script runs periodically.

---

## **Configuration**

### **1. Authors Configuration**
The `src/config/authors.json` file contains a mapping of authors and their ORCID IDs:
```json
{
  "John Doe": "0000-0002-1825-0097",
  "Jane Smith": "0000-0003-4825-6789"
}
```

Modify this file to add or update authors.

---

## **Output Files**

1. **`Publications.bib`**:
   - The generated BibTeX file containing all publications.
   - Location: `src/static/bib/Publications.bib`

2. **`PublicationStatistics.json`**:
   - Statistics on publications per author, year, and type.
   - Location: `src/logs/PublicationStatistics.json`

3. **`SkippedPublications.log`**:
   - Log of publications skipped due to invalid data or unsupported types.
   - Location: `src/logs/SkippedPublications.log`

---

## **Contributing**

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with detailed explanations of your changes.

---

## **License**

