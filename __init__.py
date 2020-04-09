from mycroft import MycroftSkill, intent_file_handler


# TODO:
# 1. define some decorators:
#       covid symptom -> takes you to covid questions
#       symptom -> asks you about pain and other symptoms
#       When using them, put the general symptom before of the covid one, so that covid questions get asked first.
# 2. create personal informations request method. add spelling too.


class HospitalTriage(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.med_record = {}

    def symptom_handler(handler):
        def ask_about_symptoms(*args, **kwargs):
            returned = handler(*args, **kwargs)
            args[0].med_record["symptom_declaration"] = args[1].data["utterance"]
            # I'm using args[0] here instead of self, but it works the same
            args[0].request_other_symptoms()
            args[0].evaluate_pain()
            return returned
        return ask_about_symptoms

    def covid_symptom(handler):
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
        # STEP 1A: check if the patient walked in. If so, it is likely that he's not urgent.
        self.med_record["can_talk"] = self.ask_yesno('can_talk')

        # STEP 1B: Ask for the main symptom and check if we recognize it.
        self.speak_dialog('main_symptom', expect_response=True)

    # ------------------------------------
    # MAIN SYMPTOMS HANDLERS
    #   Ordered by priority.
    # ------------------------------------

    # FAINT
    @intent_file_handler('symptoms.faint.intent')
    @symptom_handler
    @covid_symptom
    def handle_faint(self, message):
        self.med_record["main_symptom"] = "faints"
        self.med_record["code"] = 'red'
        self.speak_dialog('symptoms.faint')
    # HEMORRHAGE
    @intent_file_handler('symptoms.bleeding.intent')
    @symptom_handler
    def handle_bleeding(self, message):
        self.med_record["main_symptom"] = "bleeding"
        self.med_record["code"] = 'red'
        self.speak_dialog('symptoms.bleeding')

    # SHOCK
    @intent_file_handler('symptoms.shock.intent')
    @symptom_handler
    def handle_shock(self, message):
        self.med_record["main_symptom"] = "shock"
        self.med_record["code"] = "red"
        self.speak_dialog('symptoms.shock')

    # BREATH
    @intent_file_handler('symptoms.breath.intent')
    @symptom_handler
    @covid_symptom
    def handle_breathing(self, message):
        self.med_record["main_symptom"] = "breathing"
        self.med_record["code"] = "red"
        self.speak_dialog('symptoms.breath')

    @intent_file_handler('symptoms.fracture.intent')
    @symptom_handler
    def handle_fracture(self, message):
        self.med_record["main_symptom"] = "fracture"
        self.log.info(message.data)
        self.med_record["limb"] = message.data.get('limb')
        did_i_get_that = self.ask_yesno(
            'symptoms.fracture', {"article": message.data.get('article'), "limb": message.data.get('limb')})
        self.med_record["code"] = "yellow"
        if did_i_get_that == 'no':
            self.speak_dialog('main_symptom', expect_response=True)
    # ------------------------------------
    # HELPERS
    #   These are being used in the decorators.
    # ------------------------------------

    def request_other_symptoms(self):
        other_symptoms = self.get_response(dialog='other_symptoms',
                                           data=None, validator=None, on_fail=None, num_retries=-1)
        if not self.voc_match(other_symptoms, 'no'):
            self.med_record["other_symptoms"] = other_symptoms
        else:
            self.med_record["other_symptoms"] = None
        self.log.info(self.med_record)

    def evaluate_pain(self):
        reply = self.get_response(dialog='pain_evaluation',
                                  data=None, validator=number_validator, on_fail=None, num_retries=3)
        # This check is needed because of the overlapping between 6 and the "essere" verb
        if reply == 'sei':
            reply = 6
        self.med_record["pain_index"] = reply

    def ask_covid_questions(self):
        self.speak_dialog('gotta_check_covid')
        covid_score = 1
        # Let's first check if the patient knows his temperature
        has_checked_fever = self.ask_yesno('has_checked_fever')
        self.log.info(has_checked_fever)
        # If he/she has a fever, it may be a COVID infect
        if has_checked_fever == "yes":
            temperature_string = self.get_response(dialog='get_temperature',
                                                   data=None, validator=None, on_fail=None, num_retries=-1)
            self.med_record["fever"] = extract_temperature(temperature_string)
            if self.med_record["fever"] > 37.5:
                covid_score = 10

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
        if covid_score > 40:
            self.speak_dialog('probably_has_covid')
        else:
            self.speak_dialog('doesnt_have_covid')
        self.log.info(self.med_record)


# number_validator: checks if the utterance is a number.
def number_validator(utterance):
    # This check is needed because of the overlapping between 6 and the "essere" verb
    if utterance == 'sei':
        utterance = 6
    try:
        return (0 < int(utterance) <= 10)
    except ValueError:
        return False


def fever_validator(utterance):
    if len(utterance) != 3:
        return False
    temperature = extract_temperature(utterance)
    # I guess you're pretty dead if your temperature is 32 or 45, but you never know
    return 32 <= temperature <= 45


def extract_temperature(utterance):
    # Beware: the ' e ' has to be before the simple space!
    possible_separators = ['/', '.', ',', ' e ', ' ']
    for separator in possible_separators:
        if separator in utterance:
            temperature_strings = utterance.split(separator)
            temperature = int(
                temperature_strings[0])+float(temperature_strings[1])*0.1
            return temperature
    return None


def create_skill():
    return HospitalTriage()
