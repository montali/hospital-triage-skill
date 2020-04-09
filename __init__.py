from mycroft import MycroftSkill, intent_file_handler


# TODO: define some decorators:
#   covid symptom -> takes you to covid questions
#   symptom -> asks you about pain and other symptoms
#   When using them, put the general symptom before of the covid one, so that covid questions get asked first.


class HospitalTriage(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.med_record = {}

    def symptom_handler(handler):
        def ask_about_symptoms(*args, **kwargs):
            handler(*args, **kwargs)
            # I'm using args[0] here instead of self, but it works the same
            args[0].request_other_symptoms()
            args[0].evaluate_pain()
        return ask_about_symptoms

    def covid_symptom(handler):
        def check_if_covid(*args, **kwargs):
            handler(*args, **kwargs)
            args[0].ask_covid_questions()
        return check_if_covid

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

    # ------------------------------------
    # HELPERS
    #   This are being used in the decorators.
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
        self.log.info(reply)

    def ask_covid_questions(self):
        self.med_record["covid_index"] = self.ask_yesno('Hai il covid?')
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


def create_skill():
    return HospitalTriage()
