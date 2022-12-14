import logging, requests
from behave import when, then
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions


@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.BASE_URL)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    error_msg = "I should not see '%s' in '%s'" % (text_string, element.text)
    ensure(text_string in element.text, False, error_msg)

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    try:
        element.clear()
    except:
        pass
    element.send_keys(text_string)

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower().replace(" ", "-") + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)

@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    expect(found).to_be(True)

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)
