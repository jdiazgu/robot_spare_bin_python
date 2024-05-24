from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF

import os 
import time
import zipfile
import shutil
from pathlib import Path


@task

def order_robots_from_RobotSpareBin():

    
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    file_name = "orders.csv"
    file_path = os.path.join(os.getcwd(), file_name)
    receipts_folder = os.path.join(os.getcwd(),'output/pdf merger')
    output_zip = os.path.join(os.getcwd(),'output/Output')
    
    browser.configure(
        slowmo=100,
    )
    
    open_robot_order_website()
    orders = get_orders(file_path)
    
   
    for order in orders:
        
        close_annoying_modal()
        fill_the_form( order)
        preview_the_robot()
        wait_until_keyword_succeeds(submit_the_order,120,3)
        pdf = store_receipt_as_pdf(order["Order number"])
        screenhot = screenshot_robot(order["Order number"])
        embed_screenshot_to_pdf(screenhot,pdf,output_pdf_path =  os.path.join(os.getcwd(),'output/pdf merger/',order["Order number"] + '.pdf'))
        order_another_robot()
    create_zip_archive(receipts_folder,output_zip)

def open_robot_order_website():
    """Navigates to the given URL"""
    
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders(file_path):
    """Downloads csv file from the given URL"""
    
    library = Tables()
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    
    # Source dialect is known and given explicitly
    orders_table  =  library.read_table_from_csv(file_path, columns=["Order number","Head","Body","Legs","Address"])
    return orders_table

def close_annoying_modal():
    """wait for any modal to appear and click ok if it appears"""
    page = browser.page()
    xpath = '//*[@id="root"]/div/div[2]/div/div/div/div/div'
    page.wait_for_selector(xpath, state="visible", timeout=45000)
    page.click("text=OK")
    #browser = Selenium()
   

def fill_the_form(order):
    """Fills in the orders data and click the 'Submit' button"""
    page = browser.page()
    xpath = '//html/body/div/div/div[1]/div/div[1]/form/div[3]/input'
    page.select_option("#head", str(order["Head"]))
    page.click("input[type='radio'][value='"+str(order["Body"])+"']")
    page.fill(xpath, str(order["Legs"]))
    page.fill("#address", str(order["Address"]))
    

def preview_the_robot():
    page = browser.page()  
    page.click("text=Preview")

def preview_the_robot():
    page = browser.page()  
    page.click("text=Preview")


def submit_the_order():
    xpath_order = '//*[@id="order"]'
    xpath_receipt = '//*[@id="receipt"]'
    page = browser.page() 
    page.wait_for_selector(xpath_order)  
    page.click(xpath_order)   
    page.wait_for_selector(xpath_receipt, state="visible", timeout=6000)

def order_another_robot():
    xpath_order = '//*[@id="order-another"]'
    page = browser.page() 
    page.wait_for_selector(xpath_order)  
    page.click(xpath_order)   
 

def wait_until_keyword_succeeds(attempt_func, timeout, interval):
    start_time = time.time()
    while True:
        try:
            attempt_func()
            print("Keyword succeeded.")
            break
        except Exception as e:
            print("Keyword failed, retrying...")
            time.sleep(interval)
            if time.time() - start_time > timeout:
                raise TimeoutError("Keyword did not succeed within the timeout period.") from e

def store_receipt_as_pdf(order_number):
    """ Store the receipt as a PDF file"""
    xpath = '//*[@id="receipt"]'
    page = browser.page() 
    pdf = PDF()
    page.wait_for_selector(xpath, state="visible", timeout=45000)
    receipt_file_name = os.path.join(os.getcwd(),'output/PDF/',order_number + '.pdf')
    receipt_html = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(receipt_html,receipt_file_name)
    return receipt_file_name

def screenshot_robot(order_number):
    """Take a screenshot of the page"""
    page = browser.page()
    page.screenshot(path= os.path.join(os.getcwd(),'output/Screenshots/',order_number + '.png'))
    return os.path.join(os.getcwd(),'output/Screenshots/',order_number + '.png')


def embed_screenshot_to_pdf(image_path, source_pdf_path, output_pdf_path):
    pdf = PDF()
    # Add the screenshot image to the PDF
    pdf.add_watermark_image_to_pdf(
        image_path=image_path,
        source_path=source_pdf_path,
        output_path=output_pdf_path,
        coverage=0.2  # Adjust the coverage as needed to fit the screenshot appropriately
    )


def archive_receipts(source_dir, output_filename):

    """
    Creates a ZIP file of the receipts.

    :param receipts_folder: Path to the folder containing receipt files.
    :param output_zip: Path where the ZIP file should be saved.
    """

def create_zip_archive(directory_path,output_zip_path):
    # Define the directory to be zipped
    ##directory_path = Path("path/to/directory")
    
    # Define the output path for the zip file (without the .zip extension)
    #output_zip_path = Path("path/to/output_zip_file")
    
    # Create a zip archive of the directory
    shutil.make_archive(output_zip_path, 'zip', directory_path)
    
    

