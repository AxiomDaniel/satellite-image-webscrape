Author: Daniel Chan
Email: dgcha3@student.monash.edu
Last Updated: 19/07/2018

Steps to using this web scrubbing program:
1. Ensure that machine has Python 3.6, pip installed.

2. Ensure that python-virtualenv is installed. If not, run:
    pip install virtualenv

3. Open terminal, navigate to the folder where this README is saved (use cd command). 

4. If it is your first time running the code, type the line below into the terminal: 
    virtualenv -p python3.6 venv
This command installs a virtual folder to hold the packages. 

5. Then type:
    source venv/bin/activate
This command activates the virtual environment. 

6. Go to https://chromedriver.storage.googleapis.com/index.html?path=2.40/
Download the relevant version for your OS, unzip and paste into /venv/bin/

7. Enter login details for Nearmaps into loginDetails.py (Please write them within the quotation marks)
Login details can be obtained for Monash staff and students from https://resources.lib.monash.edu/eresources/nearmap-registration.html

8. In the file "findGardenProportion.py", replace "addresses.csv" to the CSV filename containing the addresses you wish to scrub (line 213).
Note: Ensure that the addresses are in the first column of the CSV (or directly edit "addresses.csv" with new addresses, whichever is more convenient).

9. If this is your first time running the code, install the packages by typing the line below into the terminal:
    pip install -r requirements.txt
This commands installs the required packages. 

10. Run the code by typing the line below into the terminal:
    python3 findGardenProportion.py
Note: The computer will navigate through the site on its own, try not to interrupt it.

11. The program will finish running once "Scrubbing completed" appears on your terminal.

12. Once you're finished, type the below line into the terminal:
    deactivate
