from mycroft import MycroftSkill, intent_file_handler


class HospitalTriage(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('triage.hospital.intent')
    def handle_triage_hospital(self, message):
        reply = self.get_response(dialog='Quali sono i sintomi?', data=None, validator=None,
                                  on_fail=None, num_retries=-1)
        # self.speak_dialog('triage.hospital')
        self.speak_dialog(reply)


def create_skill():
    return HospitalTriage()
