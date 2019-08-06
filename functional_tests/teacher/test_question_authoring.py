def test_question_creation():
    pass
    #
    # # Teacher can create a question
    # self.browser.find_element_by_id("question-section").click()
    # self.browser.find_element_by_link_text("Create new").click()
    #
    # try:
    #     WebDriverWait(self.browser, timeout).until(
    #         presence_of_element_located(
    #             (By.XPATH, "//h2[contains(text(), 'Step 1')]")
    #         )
    #     )
    # except TimeoutException:
    #     assert False
    #
    # assert "Step 1" in self.browser.find_element_by_tag_name("h2").text
    #
    # inputbox = self.browser.find_element_by_id("id_title")
    # inputbox.send_keys("Test title")
    #
    # tinymce_embed = self.browser.find_element_by_tag_name("iframe")
    # self.browser.switch_to.frame(tinymce_embed)
    # ifrinputbox = self.browser.find_element_by_id("tinymce")
    # ifrinputbox.send_keys("Test text")
    # self.browser.switch_to.default_content()
    #
    # Select(
    #     self.browser.find_element_by_id("id_discipline")
    # ).select_by_value("1")
    #
    # category = self.browser.find_element_by_id("autofill_categories")
    # category.send_keys("Kinematics")
    # time.sleep(2)
    # category.send_keys(Keys.ENTER)
    #
    # self.browser.find_element_by_id("question-create-form").submit()
    #
    # try:
    #     WebDriverWait(self.browser, timeout).until(
    #         presence_of_element_located(
    #             (By.XPATH, "//h2[contains(text(), 'Step 2')]")
    #         )
    #     )
    # except TimeoutException:
    #     assert False
    #
    # tinymce_embed = self.browser.find_element_by_id(
    #     "id_answerchoice_set-0-text_ifr"
    # )
    # self.browser.switch_to.frame(tinymce_embed)
    # ifrinputbox = self.browser.find_element_by_id("tinymce")
    # ifrinputbox.send_keys("Answer 1")
    # self.browser.switch_to.default_content()
    #
    # tinymce_embed = self.browser.find_element_by_id(
    #     "id_answerchoice_set-1-text_ifr"
    # )
    # self.browser.switch_to.frame(tinymce_embed)
    # ifrinputbox = self.browser.find_element_by_id("tinymce")
    # ifrinputbox.send_keys("Answer 2")
    # self.browser.switch_to.default_content()
    #
    # self.browser.find_element_by_id(
    #     "id_answerchoice_set-0-correct"
    # ).click()
    #
    # inputbox = self.browser.find_element_by_id("answer-choice-form")
    #
    # inputbox.submit()
    #
    # try:
    #     WebDriverWait(self.browser, timeout).until(
    #         presence_of_element_located(
    #             (By.XPATH, "//h2[contains(text(), 'Step 3')]")
    #         )
    #     )
    # except TimeoutException:
    #     assert False
    #
    # self.browser.find_element_by_id("add_question_to_assignment").submit()
    #
    # try:
    #     WebDriverWait(self.browser, timeout).until(
    #         presence_of_element_located(
    #             (By.XPATH, "//h1[text()='My Account']")
    #         )
    #     )
    # except TimeoutException:
    #     assert False
    # assert "Test title" in self.browser.page_source
    #
    # # Teacher can edit their questions
    # try:
    #     WebDriverWait(self.browser, timeout).until(
    #         element_to_be_clickable((By.ID, "question-section"))
    #     ).click()
    # except TimeoutException:
    #     assert False
    # question = Question.objects.get(title="Test title")
    #
    # try:
    #     WebDriverWait(self.browser, timeout).until(
    #         element_to_be_clickable(
    #             (By.ID, "edit-question-{}".format(question.id))
    #         )
    #     ).click()
    # except TimeoutException:
    #     assert False
    #
    # try:
    #     WebDriverWait(self.browser, timeout).until(
    #         presence_of_element_located(
    #             (By.XPATH, "//h2[contains(text(), 'Step 1')]")
    #         )
    #     )
    # except TimeoutException:
    #     assert False
    #
    # assert "Step 1" in self.browser.find_element_by_tag_name("h2").text
    #
    # tinymce_embed = self.browser.find_element_by_tag_name("iframe")
    # self.browser.switch_to.frame(tinymce_embed)
    # ifrinputbox = self.browser.find_element_by_id("tinymce")
    # ifrinputbox.send_keys("Edited: ")
    # self.browser.switch_to.default_content()
    #
    # inputbox = self.browser.find_element_by_id("id_title")
    # inputbox.submit()
    #
    # try:
    #     WebDriverWait(self.browser, timeout).until(
    #         presence_of_element_located(
    #             (By.XPATH, "//h2[contains(text(), 'Step 2')]")
    #         )
    #     )
    # except TimeoutException:
    #     assert False
    #
    # question.refresh_from_db()
    #
    # assert "Edited: Test text" in question.text
    #
    # # Teacher cannot edit another teacher's questions
    # self.browser.get(
    #     self.live_server_url
    #     + reverse("question-update", kwargs={"pk": 43})
    # )
    # assert "Forbidden" in self.browser.page_source
    #
    # # Teacher can create an assignment
    # self.browser.get(
    #     self.live_server_url + reverse("teacher", kwargs={"pk": 1})
    # )
    # self.browser.find_element_by_id("assignment-section").click()
    # self.browser.find_element_by_link_text("Manage assignments").click()
    #
    # try:
    #     WebDriverWait(self.browser, timeout).until(
    #         presence_of_element_located(
    #             (
    #                 By.XPATH,
    #                 "//h2[contains(text(), 'Create a new assignment')]",
    #             )
    #         )
    #     )
    # except TimeoutException:
    #     assert False
    #
    # inputbox = self.browser.find_element_by_id("id_identifier")
    # inputbox.send_keys("new-unique-assignment-identifier")
    #
    # inputbox = self.browser.find_element_by_id("id_title")
    # inputbox.send_keys("New assignment title")
    #
    # inputbox.submit()
    #
    # try:
    #     WebDriverWait(self.browser, timeout).until(
    #         presence_of_element_located(
    #             (
    #                 By.XPATH,
    #                 "//*[contains(text(), "
    #                 "'new-unique-assignment-identifier')]",
    #             )
    #         )
    #     )
    # except TimeoutException:
    #     assert False
    #
    # assert (
    #     Assignment.objects.filter(
    #         identifier="new-unique-assignment-identifier"
    #     ).count()
    #     == 1
    # )
    #
    # # Teacher can edit an assignment
    #
    # # Teacher can create a blink assignment
    #
    # # Teacher can delete a blink assignment
    #
    # # Teacher can edit a blink assignment
    #
    # # Access account from link in top right corner
    #
    # # Teacher cannot access other teacher accounts
    # self.browser.get(
    #     self.live_server_url + reverse("teacher", kwargs={"pk": 2})
    # )
    # assert "Forbidden" in self.browser.page_source
    #
    # # Teacher declines TOS
    #
    # # Checkout what answer choice form looks like if student answers
    #
    # # Teacher cannot delete any questions
    #
    # # Need a test to assert reset question never appears in LTI
    #
    # # Teacher clones: check new and old question states including
    # # answer_choices
