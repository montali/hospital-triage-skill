from mycroft import MycroftSkill, intent_file_handler


class HospitalTriage(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('triage.hospital.intent')
    def handle_triage_hospital(self, message):
        self.speak_dialog('triage.hospital')


def create_skill():
    return HospitalTriage()

