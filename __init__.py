from mycroft import MycroftSkill, intent_file_handler


class HospitalTriage(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.med_record = {}

    @intent_file_handler('triage.hospital.intent')
    def handle_triage_hospital(self, message):
        #reply = self.get_response(dialog='Quali sono i sintomi?',
        #                          data=None, validator=None, on_fail=None, num_retries=-1)
        self.speak('Qual e il sintomo principale?', expect_response=True)

    @intent_file_handler('symptoms.fall.intent')
    def handle_fall(self, message):
        self.med_record["main_symptom"] = "fall"
        self.speak_dialog('symptoms.headache')
        self.request_other_symptoms()

    @intent_file_handler('symptoms.headache.intent')
    def handle_headache(self, message):
        self.med_record["main_symptom"] = "headache"
        self.speak_dialog('symptoms.headache')
        self.request_other_symptoms()

    def request_other_symptoms(self):
        other_symptoms = self.get_response(dialog='Hai altri sintomi?',
                                  data=None, validator=None, on_fail=None, num_retries=-1)
        if not self.voc_match(other_symptoms, 'no'):
            self.med_record["other_symptoms"] = other_symptoms
        else:
            self.med_record["other_symptoms"] = "no"
        self.log.info(self.med_record)

def create_skill():
    return HospitalTriage()
