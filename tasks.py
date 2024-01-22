import os
from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin() -> None:
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    orders = get_orders()

    open_robot_order_website()
    close_annoying_modal()

    for order in orders:
        fill_the_form(order)
        screenshot_robot()
        store_receipt_as_pdf(order["Order number"])
        order_another()
        close_annoying_modal()

    archive_receipts()


def open_robot_order_website() -> None:
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def close_annoying_modal() -> None:
    page = browser.page()
    page.click("button:text('OK')")


def get_orders() -> list:
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    library = Tables()
    orders = library.read_table_from_csv("orders.csv")

    return orders


def fill_the_form(order: dict = None) -> None:
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.click(f"#id-body-{order['Body']}")
    page.fill(
        '//input[@placeholder="Enter the part number for the legs"]', str(order["Legs"])
    )
    page.fill("#address", str(order["Address"]))

    page.click("button:text('Order')")
    while page.locator("//div[@class='alert alert-danger']").is_visible():
        page.click("button:text('Order')")


def store_receipt_as_pdf(order_number) -> None:
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    receipt_pdf_path = f"output/receipts/receipt-{order_number}.pdf"
    pdf.html_to_pdf(receipt, receipt_pdf_path)

    pdf.add_watermark_image_to_pdf(
        image_path="output/robot.png",
        source_path=receipt_pdf_path,
        output_path=receipt_pdf_path,
    )

    os.remove("output/robot.png")


def screenshot_robot() -> bytes:
    page = browser.page()
    locator = page.locator("#robot-preview-image")
    screenshot = browser.screenshot(locator)

    with open("output/robot.png", "wb") as image_file:
        image_file.write(screenshot)


def order_another() -> None:
    page = browser.page()
    page.click("button:text('Order another robot')")


def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_tar("output/receipts", "output/receipts.tar")
