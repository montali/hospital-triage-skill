"""Mycroft skill that does a pre-triage on hospital patients.

The skill tries to ask the patient its symptoms, its personal data, 
and more. Then, it assigns a color code, stating a priority for
medical interventions.
"""

from mycroft import MycroftSkill, intent_file_handler
import json
from fastai.text import *


""" TODO:
 1. Create GUI. I'll add some GUI comments to describe the desired behaviour.
 2. Translate strings to english
"""


class HospitalTriage(MycroftSkill):
    """Main skill class for the triage.

    This is the main skill class (extending MycroftSkill),
    which contains all the operations we need to perform the
    triage.

    Attributes:
        med_record: a dict containing all the patient data.
    """

    def __init__(self):
        MycroftSkill.__init__(self)
        # Registers the fallback handler
        self.register_fallback(self.handle_fallback, 10)
        self.med_record = {}
        # Load the classifier model
        self.learner = load_learner('models', 'exported_model')

        # Load the classifier classes from JSON
        with open('classes.json') as classes:
            self.classes = json.load(classes)

    def symptom_handler(handler):
        """Decorates a symptom with the needed operations.

        This function is used as a decorator for symptoms, adding
        operations like personal data asking, age, other symptoms...

        Returns:
            The decorator function
        """
        def ask_about_symptoms(*args, **kwargs):
            returned = handler(*args, **kwargs)
            args[0].med_record["symptom_declaration"] = args[1].data["utterance"]
            # I'm using args[0] here instead of self, but it works the same
            args[0].request_age()
            args[0].request_other_symptoms()
            args[0].evaluate_pain()
            args[0].request_name()
            args[0].export_med_record()
            return returned
        return ask_about_symptoms

    def covid_symptom(handler):
        """Decorates a COVID-compatible symptom.

        This function is used as a decorator in the COVID-compatible
        symptoms. It proceeds to ask the COVID-related questions
        to the patient.

        Returns:
            The decorator function
        """
        def check_if_covid(*args, **kwargs):
            returned = handler(*args, **kwargs)
            args[0].ask_covid_questions()
            return returned
        return check_if_covid

    # ------------------------------------
    # TRIAGE START HANDLER
    # ------------------------------------
    @intent_file_handler('triage.hospital.intent')
    def handle_triage_hospital(self, message):
        """This function handles the conversation start intent.

        It first checks if the patient is responsive (green code), then 
        proceeds to ask the symptoms.

        Args:
            message: the message object returned from Mycroft

        GUI: "Is it you?" --> "Main symptom?"
        """
        # STEP 1A: check if the patient walked in. If so, it is likely that he's not urgent.
        self.med_record["can_talk"] = self.ask_yesno('can_talk')

        # STEP 1B: Ask for the main symptom and check if we recognize it.
        print(self.speak_dialog('main_symptom', expect_response=True))
        # Gotta get that from the vocabulary
        self.gui.show_text("Sintomo principale?")

    # ------------------------------------
    # MAIN SYMPTOMS HANDLERS
    #   Ordered by priority.
    # ------------------------------------

    # FAINT
    @intent_file_handler('symptoms.faint.intent')
    @symptom_handler
    @covid_symptom
    def handle_faint(self, message):
        """This function handles a "faint" symptom.

        Faint is recognized as a red code, and is a 
        COVID-compatible symptom.

        Args:
            message: the message object returned from Mycroft

        GUI: show faint emoji
        """
        self.gui.show_text("😴")
        self.med_record["main_symptom"] = "faints"
        self.med_record["code"] = 'red'
        self.speak_dialog('symptoms.faint')
    # HEMORRHAGE
    @intent_file_handler('symptoms.bleeding.intent')
    @symptom_handler
    def handle_bleeding(self, message):
        """This function handles a "hemorrhage" symptom.

        Hemorrhage is recognized as a red code.

        Args:
            message: the message object returned from Mycroft

        GUI: show blood emoji
        """
        self.gui.show_text("🩸")
        self.med_record["main_symptom"] = "bleeding"
        self.med_record["code"] = 'red'
        self.speak_dialog('symptoms.bleeding')

    # SHOCK
    @intent_file_handler('symptoms.shock.intent')
    @symptom_handler
    def handle_shock(self, message):
        """This function handles a "shock" symptom.

        Shock is recognized as a red code.

        Args:
            message: the message object returned from Mycroft

        GUI: show shocked emoji
        """
        self.gui.show_text("😖")
        self.med_record["main_symptom"] = "shock"
        self.med_record["code"] = "red"
        self.speak_dialog('symptoms.shock')

    # BREATH
    @intent_file_handler('symptoms.breath.intent')
    @symptom_handler
    @covid_symptom
    def handle_breathing(self, message):
        """This function handles a "breathing fatigue" symptom.

        Breathing fatigue is recognized as a red code, and is a
        COVID-compatible symptom.

        Args:
            message: the message object returned from Mycroft

        GUI: show open mouth emoji
        """
        self.gui.show_text("😮")
        self.med_record["main_symptom"] = "breathing"
        self.med_record["code"] = "red"
        self.speak_dialog('symptoms.breath')

    # FRACTURE
    @intent_file_handler('symptoms.fracture.intent')
    @symptom_handler
    def handle_fracture(self, message):
        """This function handles a "fracture" symptom.

        Since fracture intents contain an entity stating the limb,
        it checks if it got that right. Then, it assigns a yellow code.

        Args:
            message: the message object returned from Mycroft

        GUI: show fracture emoji
        """
        self.gui.show_text("🤦‍♂️")
        self.med_record["main_symptom"] = "fracture"
        self.med_record["limb"] = message.data.get('limb')
        did_i_get_that = self.ask_yesno(
            'symptoms.fracture', {"article": message.data.get('article'), "limb": message.data.get('limb')})
        self.med_record["code"] = "yellow"
        if did_i_get_that == 'no':
            self.speak_dialog('main_symptom', expect_response=True)

    # FEVER
    @intent_file_handler('symptoms.fever.intent')
    @symptom_handler
    @covid_symptom
    def handle_fever(self, message):
        """This function handles a "fever" symptom.

        Fever is recognized as a yellow code, but it is a
        COVID-compatible symptom so it requires further investigation.

        Args:
            message: the message object returned from Mycroft

        GUI: show fever emoji
        """
        self.gui.show_text("🤒")
        self.med_record["main_symptom"] = "fever"
        self.med_record["code"] = "yellow"
        self.speak_dialog('symptoms.fever')
        self.check_fever()

    # BURN
    @intent_file_handler('symptoms.burn.intent')
    @symptom_handler
    def handle_burn(self, message):
        """This function handles a "burn" symptom.

        Burn is recognized as a yellow code.

        Args:
            message: the message object returned from Mycroft

        GUI: show burn emoji
        """
        self.gui.show_text("🔥")
        self.med_record["main_symptom"] = "burn"
        self.med_record["code"] = "yellow"
        self.speak_dialog('symptoms.burn')

    # ABDOMINAL PAIN
    @intent_file_handler('symptoms.ab_pain.intent')
    @symptom_handler
    def handle_abpain(self, message):
        """This function handles an "abdominal pain" symptom.

        Abdmonial pain can be related with heart issues,
        but for now the code is yellow.

        Args:
            message: the message object returned from Mycroft

        GUI: show abdominal pain emoji
        """
        self.gui.show_text("🥴")
        self.med_record["main_symptom"] = "ab_pain"
        self.med_record["code"] = "yellow"
        self.speak_dialog('symptoms.ab_pain')

    # ------------------------------------
    # FALLBACK SKILL
    #   If the symptom wasn't recognized, let AI do its thang.
    # ------------------------------------
    @symptom_handler
    def handle_fallback(self, message):
        utterance = message.data.get("utterance")
        symptom = self.classes[int(self.learner.predict(utterance)[0])]
        self.gui.show_text(symptom["emoji"])
        did_i_get_that = self.ask_yesno(
            'symptoms.fallback', {"symptom": symptom["name"]})
        if not did_i_get_that:
            self.speak_dialog('sorry')
        else:
            if symptom["covid"]:
                self.ask_covid_questions()
            self.med_record["main_symptom"] = symptom["name"]
            self.med_record["code"] = symptom["code"]

    # ------------------------------------
    # ------------------------------------
    # HELPERS
    #   These are being used in the decorators.
    # ------------------------------------

    def request_age(self):
        """Gets the patient age.

        This function requests the patient's age and
        saved it in the medical record.

        GUI: show textual question
        """
        self.gui.show_text("📅")
        self.med_record["age"] = int(self.get_response(dialog='get_age',
                                                       data=None, validator=age_validator, on_fail=None, num_retries=-1))

    def request_name(self):
        """Gets the patient name.

        It first asks for the full name, and if not correct, 
        it proceeds to ask the spelling.

        GUI: show textual question
        """
        self.gui.show_text("Nome?")
        full_name = self.get_response(dialog='get_fullname',
                                      data=None, validator=None, on_fail=None, num_retries=-1)
        if self.ask_yesno('check_fullname', {"full_name": full_name}) == "no":
            self.speak_dialog('lets_retry')
            full_name = self.get_response(dialog='get_fullname',
                                          data=None, validator=None, on_fail=None, num_retries=-1)
            if self.ask_yesno('check_fullname', {"full_name": full_name}) == "no":
                self.request_name()
            else:
                self.med_record["full_name"] = full_name
        else:
            self.med_record["full_name"] = full_name

    def check_fever(self):
        """Gets the patient fever.

        This function asks the patient if he measured 
        his temperature, and if so, it asks it.

        Returns:
            True if we got the temperature, False if not.

        GUI: show thermometer + textual question?
        """
        # Let's first check if the patient knows his temperature
        has_checked_fever = self.ask_yesno('has_checked_fever')
        self.log.info(has_checked_fever)
        # If he/she has a fever, it may be a COVID infect
        if has_checked_fever == "yes":
            self.gui.show_text("🌡Temperatura?")
            temperature_string = self.get_response(dialog='get_temperature',
                                                   data=None, validator=fever_validator, on_fail=None, num_retries=-1)
            self.med_record["fever"] = extract_temperature(temperature_string)
            return True
        else:
            return False

    def request_other_symptoms(self):
        """Gets the patient's other symptoms.

        Asks the patient if he got other symptoms to warn us about.

        GUI: textual question
        """
        self.gui.show_text("Altri sintomi?")
        other_symptoms = self.get_response(dialog='other_symptoms',
                                           data=None, validator=None, on_fail=None, num_retries=-1)
        if not self.voc_match(other_symptoms, 'no'):
            self.med_record["other_symptoms"] = other_symptoms
        else:
            self.med_record["other_symptoms"] = None
        self.log.info(self.med_record)

    def evaluate_pain(self):
        """Gets the patient's pain evaluation.

        Asks the patient his/her pain from 1 to 10.
        This is used by many hospitals to evaluate the conditions.

        GUI: show fire extinguisher emoji
        """
        self.gui.show_text("🧯")
        reply = self.get_response(dialog='pain_evaluation',
                                  data=None, validator=number_validator, on_fail=None, num_retries=3)
        # This check is needed because of the overlapping between 6 and the "essere" verb
        if reply == 'sei':
            reply = 6
        self.med_record["pain_index"] = reply

    def ask_covid_questions(self):
        """Checks for COVID symptoms.

        When triggered by a COVID-compatible symptom, 
        this function evaluates the patient symptoms to 
        try to guess if he/she has COVID19.

        GUI: show face mask emoji
        """
        self.gui.show_text("😷")
        self.speak_dialog('gotta_check_covid')
        covid_score = 1
        # Let's check if the patient knows the temperature. Skip if he already declared it.
        if not "fever" in self.med_record:
            self.check_fever()
        if "fever" in self.med_record:
            if self.med_record["fever"] > 37.5:
                covid_score = covid_score * 2
        # Let's define an array of tuples, each containing the yes/no question string and its COVID index multiplier
        yesno_questions = [("has_sore_throat", 1.3), ("has_cold", 1.3), ("has_breathing_difficulties",
                                                                         1.6), ("has_cough", 1.6), ("has_had_contacts", 2), ("misses_taste", 1.7)]
        self.speak_dialog('will_ask_yesno')
        # Check if he/she has COVID-compatible symptoms
        for question in yesno_questions:
            self.med_record[question[0]] = self.ask_yesno(question[0])
            if self.med_record[question[0]] == 'yes':
                covid_score = covid_score * question[1]
            self.log.info(covid_score)

        self.med_record["covid_score"] = covid_score
        if covid_score > 15:
            self.speak_dialog('probably_has_covid')
        else:
            self.speak_dialog('doesnt_have_covid')
        self.log.info(self.med_record)

    def export_med_record(self):
        """Exports the data to JSON.

        This function is called at the end of the interaction
        to export the fetched data from the patient. It then
        assigns a desk to the patient based on his/her severeness.

        GUI: show hands emoji
        """
        with open("med_record.json", "w") as med_record_file:
            med_record_file.write(json.dumps(self.med_record))
        self.speak_dialog('thanks_and_bye', {"desk": self.med_record["code"]})
        self.med_record = {}


def number_validator(utterance):
    """Checks if the utterance is a number.

    This validator is used when asking for pain from 1 to 10.

    Returns:
        True if the utterance contains a valid number, False if not.
    """
    # This check is needed because of the overlapping between 6 and the "essere" verb
    if utterance == 'sei':
        utterance = 6
    try:
        return (0 < int(utterance) <= 10)
    except ValueError:
        return False


def fever_validator(utterance):
    """Checks if the utterance is a fever-compatible value.

    This validator is used when asking for the patient temperature.

    Returns:
        True if plausible, False if not.
    """
    try:
        temperature = extract_temperature(utterance)
        # I guess you're pretty dead if your temperature is 32 or 45, but you never know
        return 32 <= temperature <= 45
    except TypeError:
        return False


def age_validator(utterance):
    """Checks if the utterance is an age.

    This validator is used when we're getting the patient age.

    Returns:
        True if plausible, False if not.
    """
    try:
        return 0 <= int(utterance) <= 120
    except TypeError:
        return False

# extract_temperature: extracts the float fever value, transforming it from the various ways of mycroft interpreting it


def extract_temperature(utterance):
    """Extracts the patient temperature from the utterance.

    This is needed because of the various ways of Mycroft interpreting
    floating point numbers. Some examples:
    - 38 e 1
    - 38/1
    - 38.1
    - 38,1
    - 38 1

    Returns:
        The floating point value of the temperature, or
        None if it is impossible to extract.
    """
    # Beware: the ' e ' has to be before the simple space!
    possible_separators = ['/', '.', ',', ' e ', ' ']
    try:
        for separator in possible_separators:
            if separator in utterance:
                temperature_strings = utterance.split(separator)
                if temperature_strings[1] == "mezzo":
                    temperature_strings[1] = "5"
                temperature = int(
                    temperature_strings[0])+float(temperature_strings[1])*0.1
                return temperature
        return None
    except TypeError:
        return None


def create_skill():
    """Creates the skill for the Mycroft bot using the 
    skill class.
    """
    return HospitalTriage()
